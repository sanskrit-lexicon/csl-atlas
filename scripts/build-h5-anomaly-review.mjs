// Build the H5 ghost/anomaly review queue.
//
// H5 remains proof-first: these rows are not error claims. They are compact
// review samples drawn from existing forensic outputs, with source links and
// preserved review fields.
//
// Usage: npm run build-h5-anomaly-review

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const F0 = path.resolve(process.cwd(), "data", "forensic", "shared_headword_anomalies.csv");
const F2_RAW = path.resolve(process.cwd(), "data", "forensic", "raw_headword_pool.csv");
const CORRECTIONS = path.resolve(process.cwd(), "data", "forensic", "shared_corrections.csv");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "h5-anomaly-review.json");

const TARGETS = {
  mwPwgDoublets: 30,
  mwPwDoublets: 30,
  rawMwPwgExclusive: 30,
  nullControls: 20,
  knownCorrections: 20
};

const DICT_CODE = {
  MW: "mw",
  PWG: "pwg",
  PW: "pw",
  BOP: "bop",
  SKD: "skd"
};

export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
      continue;
    }
    if (ch === '"') quoted = true;
    else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (ch !== "\r") {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  if (!rows.length) return [];
  const header = rows[0];
  return rows.slice(1)
    .filter(values => values.some(value => value !== ""))
    .map(values => Object.fromEntries(header.map((key, index) => [key, values[index] ?? ""])));
}

function readCsv(file) {
  return parseCsv(fs.readFileSync(file, "utf8"));
}

function dictSet(row) {
  return new Set((row.dicts || "").split(/\s+/).filter(Boolean));
}

function hasPair(row, a, b) {
  const set = dictSet(row);
  return set.has(a) && set.has(b);
}

function norm(value) {
  return normalizeLemma(value).normalized;
}

function sanitize(value) {
  return String(value).replace(/[^A-Za-z0-9_.:-]+/g, "_");
}

function reviewId(...parts) {
  return `h5:${parts.map(sanitize).join(":")}`;
}

function collectNeededForms(selected) {
  const needed = new Map(); // dict -> Set<form>
  function add(dict, form) {
    const code = DICT_CODE[dict] || dict.toLowerCase();
    if (!needed.has(code)) needed.set(code, new Set());
    needed.get(code).add(norm(form));
  }
  for (const row of selected) {
    for (const dict of row.pointerDicts || []) add(dict, row.pointerForm);
  }
  return needed;
}

function buildSourceIndex(needed) {
  const index = new Map(); // code:normalized -> pointer
  const warnings = [];
  for (const [code, forms] of needed) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; H5 pointers from that dictionary were skipped.`);
      continue;
    }
    for (const rec of iterateDict(code)) {
      const key = norm(rec.k1 || "");
      if (!forms.has(key)) continue;
      const id = `${code}:${key}`;
      if (!index.has(id)) {
        index.set(id, {
          dictionary: code.toUpperCase(),
          L: rec.L ?? null,
          line: rec.startLine,
          href: rec.href
        });
      }
    }
  }
  return { index, warnings };
}

function sourcePointers(index, row) {
  const pointers = [];
  for (const dict of row.pointerDicts || []) {
    const code = DICT_CODE[dict] || dict.toLowerCase();
    const pointer = index.get(`${code}:${norm(row.pointerForm)}`);
    if (pointer) pointers.push(pointer);
  }
  return pointers;
}

function selectF0(rows, pair, count, sampleClass) {
  const [a, b] = pair;
  return rows
    .filter(row => hasPair(row, a, b))
    .filter(row => sampleClass === "null-control" || Number(row.n_dicts_with_both || 0) >= 2)
    .slice(0, count * 6)
    .map(row => ({
      sampleClass,
      pointerDicts: [a, b],
      pointerForm: row.typo_form,
      subjectLemma: row.typo_form,
      dictionaries: [a, b],
      machineValue: {
        sampleClass,
        pair: `${a}/${b}`,
        typoForm: row.typo_form,
        nearestReal: row.nearest_real,
        nRealNeighbours: Number(row.n_real_neighbours || 0),
        dfTypo: Number(row.df_typo || 0),
        nDicts: Number(row.n_dicts || 0),
        dicts: row.dicts,
        nDictsWithBoth: Number(row.n_dicts_with_both || 0),
        interpretation: sampleClass === "null-control"
          ? "Control sample for false-positive morphology rate."
          : "Candidate shared rare near-core doublet; lineage signal before error claim."
      }
    }));
}

function selectRaw(rows, count) {
  return rows
    .filter(row => row.shared_with === "PWG")
    .slice(0, count * 4)
    .map(row => ({
      sampleClass: "raw-headword-exclusive",
      pointerDicts: ["MW", row.shared_with],
      pointerForm: row.raw_k1,
      subjectLemma: row.raw_k1,
      dictionaries: ["MW", row.shared_with],
      machineValue: {
        sampleClass: "raw-headword-exclusive",
        rawHeadword: row.raw_k1,
        sharedWith: row.shared_with,
        interpretation: "Raw <k1> appears only in MW plus one Petersburg dictionary among parsed sources."
      }
    }));
}

function selectCorrections(rows, count) {
  return rows
    .filter(row => ["pw", "pwg"].includes((row.pet_dict || "").toLowerCase()))
    .slice(0, count * 6)
    .map(row => {
      const pet = row.pet_dict.toUpperCase();
      return {
        sampleClass: "known-correction",
        pointerDicts: ["MW", pet],
        pointerForm: row.headword,
        subjectLemma: row.headword,
        dictionaries: ["MW", pet],
        machineValue: {
          sampleClass: "known-correction",
          headword: row.headword,
          petDict: row.pet_dict,
          inPwgIssues: row.in_pwgissues === "True",
          petOld: row.pet_old,
          petNew: row.pet_new,
          mwOld: row.mw_old,
          mwNew: row.mw_new,
          interpretation: "Already observed correction pair for reviewer calibration."
        }
      };
    });
}

function finalizeCandidates(candidates, sourceIndex, countByClass) {
  const out = [];
  const seen = new Set();
  const classCounts = {};
  for (const candidate of candidates) {
    const limit = countByClass[candidate.sampleClass] ?? Infinity;
    if ((classCounts[candidate.sampleClass] || 0) >= limit) continue;
    const pointers = sourcePointers(sourceIndex, candidate);
    if (!pointers.length) continue;
    const id = reviewId(candidate.sampleClass, candidate.dictionaries.join("-"), candidate.subjectLemma, candidate.machineValue.nearestReal || "");
    if (seen.has(id)) continue;
    seen.add(id);
    classCounts[candidate.sampleClass] = (classCounts[candidate.sampleClass] || 0) + 1;
    out.push({ ...candidate, reviewId: id, sourcePointers: pointers });
  }
  return { items: out, classCounts };
}

function toReviewItems(candidates, preserved) {
  let preservedCount = 0;
  const items = candidates.map(candidate => {
    if (preserved.has(candidate.reviewId)) preservedCount += 1;
    return {
      reviewId: candidate.reviewId,
      queue: "encoding-ocr",
      subject: {
        kind: "entry",
        lemma: candidate.subjectLemma,
        dictionaries: candidate.dictionaries
      },
      sourcePointers: candidate.sourcePointers,
      machineValue: candidate.machineValue,
      evidenceLevel: candidate.sampleClass === "known-correction" ? "observed" : "inferred",
      ...reviewFields(preserved, candidate.reviewId)
    };
  });
  return { items, preservedCount };
}

function main() {
  const f0Rows = readCsv(F0);
  const rawRows = readCsv(F2_RAW);
  const correctionRows = readCsv(CORRECTIONS);

  const wanted = [
    ...selectF0(f0Rows, ["MW", "PWG"], TARGETS.mwPwgDoublets, "mw-pwg-shared-doublet"),
    ...selectF0(f0Rows, ["MW", "PW"], TARGETS.mwPwDoublets, "mw-pw-shared-doublet"),
    ...selectRaw(rawRows, TARGETS.rawMwPwgExclusive),
    ...selectF0(f0Rows, ["BOP", "MW"], Math.ceil(TARGETS.nullControls / 2), "null-control"),
    ...selectF0(f0Rows, ["SKD", "BOP"], Math.floor(TARGETS.nullControls / 2), "null-control"),
    ...selectCorrections(correctionRows, TARGETS.knownCorrections)
  ];

  const needed = collectNeededForms(wanted);
  const { index, warnings } = buildSourceIndex(needed);
  const { items: candidates, classCounts } = finalizeCandidates(wanted, index, {
    "mw-pwg-shared-doublet": TARGETS.mwPwgDoublets,
    "mw-pw-shared-doublet": TARGETS.mwPwDoublets,
    "raw-headword-exclusive": TARGETS.rawMwPwgExclusive,
    "null-control": TARGETS.nullControls,
    "known-correction": TARGETS.knownCorrections
  });

  const preserved = loadPreserved(OUTPUT);
  const { items, preservedCount } = toReviewItems(candidates, preserved);
  items.sort((a, b) =>
    String(a.machineValue.sampleClass).localeCompare(String(b.machineValue.sampleClass)) ||
    String(a.subject.lemma).localeCompare(String(b.subject.lemma)) ||
    a.reviewId.localeCompare(b.reviewId)
  );

  const targetTotal = Object.values(TARGETS).reduce((sum, value) => sum + value, 0);
  const payload = reviewPayload({
    queue: "encoding-ocr",
    sourcePath: "data/forensic/{shared_headword_anomalies.csv,raw_headword_pool.csv,shared_corrections.csv}",
    items,
    extra: {
      reviewFamily: "h5-ghost-anomaly",
      targetTotal,
      classCounts
    },
    assumptions: [
      "H5 rows are review candidates, not error claims.",
      "F0 rows are rare near-core forms one edit from common lemmas; most may be legitimate Sanskrit or morphology.",
      "F2 raw-headword rows preserve raw <k1> forms shared by MW and one Petersburg dictionary.",
      "Known-correction rows calibrate reviewer labels against already observed edits.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "Queue type is encoding-ocr to keep the canonical review-report schema unchanged; reviewFamily identifies this as H5.",
      "Rows without at least one source href are omitted, so class counts may be below target.",
      "Null controls must remain in the queue; they estimate false-positive morphology rate.",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} H5 anomaly review items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`Class counts: ${JSON.stringify(classCounts)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
