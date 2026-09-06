// Build the atlas discipline-coverage packet: the join of the atlas's
// dictionary inventory through the estate's ratified meso->discipline
// crosswalk (H4178 flip 3; H3567 ruling F5, released by F5c).
//
// The crosswalk is OWNED by IndologyScholars (curation/meso_discipline_crosswalk.csv
// + curation/disciplines.csv) and consumed here read-only from the sibling
// checkout — the discipline taxonomy is never re-derived atlas-side, and
// keyword_filtering.py is never used. The atlas contributes only the
// dict -> meso_code assignment layer (src/data/disciplines/dict_meso_assignments.json).
//
// Emits (committed, page-sized):
//   - src/data/disciplines/discipline_coverage.json: per-dict disciplines
//     (confidence = assignment x crosswalk, capped at 1), per-discipline
//     coverage summary, the crosswalk's deliberate NOT-MAPPED sentinel rows.
//   - src/data/disciplines/discipline_coverage.source.json: provenance pin.
//
// Usage: npm run build-discipline-coverage   (then npm run validate-discipline-coverage)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-discipline-coverage";
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "IndologyScholars");
const CROSSWALK_PATH = path.join(SIBLING_ROOT, "curation", "meso_discipline_crosswalk.csv");
const DISCIPLINES_PATH = path.join(SIBLING_ROOT, "curation", "disciplines.csv");
const COVERAGE_PATH = path.resolve(process.cwd(), "src", "data", "dictionary-coverage.json");
const ASSIGNMENTS_PATH = path.resolve(process.cwd(), "src", "data", "disciplines", "dict_meso_assignments.json");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "disciplines");
const JSON_OUT = path.join(OUT_DIR, "discipline_coverage.json");
const SOURCE_OUT = path.join(OUT_DIR, "discipline_coverage.source.json");

// Minimal RFC-4180-ish CSV parser: handles quoted fields with commas/quotes.
export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === "," && !inQuotes) {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field);
      field = "";
      rows.push(row);
      row = [];
    } else if (ch === "\r") {
      // skip
    } else {
      field += ch;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  const header = rows.shift().map((h) => h.trim());
  return rows
    .filter((r) => r.some((cell) => cell.trim() !== ""))
    .map((r) => Object.fromEntries(header.map((h, i) => [h, (r[i] ?? "").trim()])));
}

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

async function main() {
  const crosswalkRows = parseCsv(fs.readFileSync(CROSSWALK_PATH, "utf8"));
  const disciplineRows = parseCsv(fs.readFileSync(DISCIPLINES_PATH, "utf8"));
  const coverage = JSON.parse(fs.readFileSync(COVERAGE_PATH, "utf8"));
  const assignmentsDoc = JSON.parse(fs.readFileSync(ASSIGNMENTS_PATH, "utf8"));

  // meso_code -> [{disciplineCode, confidence, note}] (a code may map to several).
  const crosswalk = new Map();
  const sentinelRows = [];
  for (const r of crosswalkRows) {
    const meso = r.meso_code;
    const disc = r.discipline_code;
    if (!meso) continue;
    if (!disc) {
      sentinelRows.push({ mesoCode: meso, confidence: Number(r.confidence) || 0, note: r.note });
      continue;
    }
    if (!crosswalk.has(meso)) crosswalk.set(meso, []);
    crosswalk.get(meso).push({
      disciplineCode: disc,
      confidence: Number(r.confidence) || 0,
      note: r.note || "",
    });
  }

  const disciplineLabels = new Map(
    disciplineRows.map((r) => [
      r.discipline_code,
      { labelEn: r.label_en, labelRu: r.label_ru, parentCode: r.parent_code || null, status: r.status },
    ])
  );

  const assignmentByDict = new Map(assignmentsDoc.assignments.map((a) => [a.dict, a]));

  const dicts = coverage.dicts.map((d) => {
    const a = assignmentByDict.get(d.code);
    if (!a) throw new Error(`no assignment row for coverage dict ${d.code}`);
    const base = {
      dict: d.code,
      title: d.title,
      mesoCode: a.mesoCode,
      assignmentConfidence: a.confidence,
      rationale: a.rationale,
    };
    if (!a.mesoCode) return { ...base, disciplines: [] };
    const mappings = crosswalk.get(a.mesoCode);
    if (!mappings) {
      throw new Error(`meso code ${a.mesoCode} (dict ${d.code}) not in sibling crosswalk`);
    }
    const disciplines = mappings.map((m) => {
      const label = disciplineLabels.get(m.disciplineCode);
      if (!label) throw new Error(`discipline ${m.disciplineCode} not in sibling disciplines.csv`);
      return {
        code: m.disciplineCode,
        labelEn: label.labelEn,
        labelRu: label.labelRu,
        parentCode: label.parentCode,
        confidence: round(Math.min(1, a.confidence * m.confidence)),
        crosswalkConfidence: m.confidence,
        crosswalkNote: m.note,
      };
    });
    disciplines.sort((x, y) => y.confidence - x.confidence);
    return { ...base, disciplines };
  });

  const assigned = dicts.filter((d) => d.disciplines.length > 0);
  const perDiscipline = new Map();
  for (const d of assigned) {
    for (const disc of d.disciplines) {
      if (!perDiscipline.has(disc.code)) {
        perDiscipline.set(disc.code, {
          code: disc.code,
          labelEn: disc.labelEn,
          labelRu: disc.labelRu,
          dicts: [],
        });
      }
      perDiscipline.get(disc.code).dicts.push(d.dict);
    }
  }

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    license: "CC BY-SA 4.0",
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "IndologyScholars/curation/meso_discipline_crosswalk.csv",
      "IndologyScholars/curation/disciplines.csv",
      "src/data/disciplines/dict_meso_assignments.json",
      "scripts/build-discipline-coverage.mjs",
    ],
    method:
      "Atlas dict -> meso_code assignments joined through the sibling IndologyScholars crosswalk to the ratified discipline taxonomy; taxonomy never re-derived (H3567 F5 / F5c).",
    totals: {
      dicts: dicts.length,
      assigned: assigned.length,
      unassigned: dicts.length - assigned.length,
      disciplines: perDiscipline.size,
    },
    perDiscipline: [...perDiscipline.values()].sort((a, b) => b.dicts.length - a.dicts.length),
    notMappedSentinels: sentinelRows,
    dicts,
  };

  let feedCommit = null;
  try {
    feedCommit = execSync("git rev-parse HEAD", { cwd: SIBLING_ROOT, encoding: "utf8" }).trim();
  } catch {
    // sibling checkout may be shallow/detached; the source envelope degrades honestly
  }

  const source = {
    dataset: "discipline_coverage",
    commit: execSync("git rev-parse HEAD", { encoding: "utf8" }).trim(),
    feedRepo: "https://github.com/gasyoun/IndologyScholars",
    feedCommit,
    generatedAt: new Date().toISOString(),
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION,
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, JSON.stringify(payload, null, 2) + "\n");
  fs.writeFileSync(SOURCE_OUT, JSON.stringify(source, null, 2) + "\n");

  console.log(
    `Wrote discipline-coverage packet (${dicts.length} dicts, ${assigned.length} assigned, ` +
      `${perDiscipline.size} disciplines):`
  );
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
