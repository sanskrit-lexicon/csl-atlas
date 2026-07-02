// Corpus-scale SKD/VCP sense/citation-fusion counter (A02 revision, R1).
//
// New, read-only build over local csl-orig/v02: walks every SKD and every VCP
// record and classifies each iti-unit (the existing indigenous-prose split
// from build-r2-source-anchors.mjs) into one of three classes:
//
//   (a) authority-terminal — the synonym/definition run ends *in* the
//       authority formula: sense and citation share one iti-unit (the
//       *dharma*-in-SKD pattern, e.g. "...vfzaH 5 . ityamaraH . 1.4.24..").
//   (b) separable — the unit is (almost) nothing but the authority tag; its
//       definitional content sits in a different iti-unit (the
//       *dharma*-in-VCP pattern of citations woven through discursive prose).
//   (c) other/no-authority — no authority marker detected in the unit.
//
// Authority detection reuses indigenousAuthorityHints() from
// build-r2-source-anchors.mjs (the reviewed VCP `...0`-siglum / curated SKD
// authority-name signal already used by the promotion experiment's
// classifyItiUnit), generalised with one additional SKD pattern: the
// sandhi-fused "ity<word>" formula (`ityamaraH`, `ityetyAdi`, ...), which
// covers authority names outside the curated 16-entry exemplar list. This is
// a pattern-based classifier, not a philological reading of every citation —
// borderline units exist (see `limitations` in the payload).
//
// Fused-vs-separable is decided by how much definitional content precedes
// the authority match *within the same unit*: if there are at least
// FUSION_MIN_CONTENT_CHARS non-whitespace characters before the match, the
// unit reads as a definition run that closes in its own citation (fused);
// otherwise the unit is essentially just the citation tag, and the
// definition it belongs to lives in a sibling unit (separable).
//
// Usage: npm run build-r2-kosa-fusion

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { R2_DICTS, splitRecord, indigenousAuthorityHints, cleanText } from "./build-r2-source-anchors.mjs";
import { generatedAtForPayload, readJsonIfExists, licenseFields } from "./lib/dataset-meta.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "r2_kosa_fusion.json");
const SAMPLE_OUT = path.join(OUT_DIR, "r2_kosa_fusion_sample.json");

const DICT_CODES = ["skd", "vcp"];
const FUSION_MIN_CONTENT_CHARS = 20;

// Generalises indigenousAuthorityHints()'s curated SKD list with the
// sandhi-fused formula itself, so corpus-scale detection is not limited to
// the 16 names the exemplar pass hand-picked. VCP already generalises via
// the `...0` siglum convention inside indigenousAuthorityHints().
const SKD_FUSED_AUTHORITY = /\bity[a-zA-Z]{3,}\b/g;
const VCP_SIGLUM = /\b[A-Za-z]{2,}0\b/g;
const VCP_AUTHORITY_EXCLUDE = new Set(["avya", "klI", "na", "pu", "strI", "tri", "vya"]);

/** Earliest character offset in `text` at which an authority signal begins,
 *  or -1 if none is found. Mirrors indigenousAuthorityHints()'s boolean
 *  detection but also returns a position, which that function does not. */
function earliestAuthorityOffset(text, dictCode) {
  let earliest = -1;
  const consider = index => {
    if (index >= 0 && (earliest === -1 || index < earliest)) earliest = index;
  };
  if (dictCode === "skd") {
    SKD_FUSED_AUTHORITY.lastIndex = 0;
    const m = SKD_FUSED_AUTHORITY.exec(text);
    if (m) consider(m.index);
    // Curated exemplar names that are NOT sandhi-fused (e.g. "iti medinI")
    // still surface as a leading token of the tail unit once split on "iti";
    // indigenousAuthorityHints() catches these by name, so fall back to a
    // direct index search of the same hint labels.
    for (const hint of indigenousAuthorityHints(text, "skd")) {
      const name = hint.replace(/^auth:/, "");
      const idx = text.toLowerCase().indexOf(name.toLowerCase());
      if (idx >= 0) consider(idx);
    }
  } else if (dictCode === "vcp") {
    VCP_SIGLUM.lastIndex = 0;
    let m;
    while ((m = VCP_SIGLUM.exec(text))) {
      const token = m[1] ?? m[0].slice(0, -1);
      if (!VCP_AUTHORITY_EXCLUDE.has(token)) {
        consider(m.index);
        break;
      }
    }
  }
  return earliest;
}

function classifyUnit(unitText, dictCode) {
  const hints = indigenousAuthorityHints(unitText, dictCode);
  const offset = earliestAuthorityOffset(unitText, dictCode);
  if (!hints.length && offset === -1) return { authorityMarked: false, klass: "other-no-authority" };
  const before = offset >= 0 ? unitText.slice(0, offset) : "";
  const contentChars = before.replace(/<[^>]+>/g, " ").replace(/\s+/g, "").length;
  const klass = contentChars >= FUSION_MIN_CONTENT_CHARS ? "authority-terminal" : "separable";
  return { authorityMarked: true, klass };
}

function classifyRecord(dictCode, dict, rec) {
  const parts = splitRecord(rec.body || "", dict);
  const units = parts.map((part, index) => ({
    index,
    text: part.text,
    ...classifyUnit(part.text, dictCode)
  }));
  return units;
}

function pct(n, d) {
  return d ? Number(((100 * n) / d).toFixed(1)) : 0;
}

function buildSample(dictRows, sizePerClass = 34) {
  // Stratified ~100-row sample of SKD iti-units across the three classes,
  // for the human citational-vs-grammatical adjudication (A02 R1 caveat /
  // A08 C-M1, run once per REVISION_BRIEF_P2_OBS.md §Part 4).
  const byClass = { "authority-terminal": [], separable: [], "other-no-authority": [] };
  for (const row of dictRows) byClass[row.klass]?.push(row);
  const sample = [];
  for (const klass of Object.keys(byClass)) {
    const pool = byClass[klass];
    const step = Math.max(1, Math.floor(pool.length / sizePerClass));
    for (let i = 0; i < pool.length && sample.filter(r => r.klass === klass).length < sizePerClass; i += step) {
      sample.push(pool[i]);
    }
  }
  return sample;
}

function main() {
  const dictConfigs = DICT_CODES.map(code => R2_DICTS.find(d => d.code === code));
  const perDict = [];
  const sampleRows = [];

  for (const dict of dictConfigs) {
    if (!dictExists(dict.code)) {
      console.warn(`Missing source for ${dict.code}; skipped.`);
      continue;
    }
    let records = 0;
    let recordsWithAuthorityUnit = 0;
    let totalUnits = 0;
    const classCounts = { "authority-terminal": 0, separable: 0, "other-no-authority": 0 };
    const flatRows = [];

    for (const rec of iterateDict(dict.code)) {
      records += 1;
      const units = classifyRecord(dict.code, dict, rec);
      let recordHasAuthority = false;
      for (const unit of units) {
        totalUnits += 1;
        classCounts[unit.klass] += 1;
        if (unit.authorityMarked) recordHasAuthority = true;
        flatRows.push({
          L: rec.L,
          k1: rec.k1,
          unitIndex: unit.index,
          klass: unit.klass,
          text: cleanText(unit.text, 200)
        });
      }
      if (recordHasAuthority) recordsWithAuthorityUnit += 1;
    }

    const authorityMarkedUnits = classCounts["authority-terminal"] + classCounts.separable;
    perDict.push({
      dict: dict.code,
      label: dict.label,
      records,
      totalUnits,
      recordsWithAuthorityUnit,
      pctRecordsWithAuthorityUnit: pct(recordsWithAuthorityUnit, records),
      authorityMarkedUnits,
      classCounts,
      pctFusedAmongAuthorityMarked: pct(classCounts["authority-terminal"], authorityMarkedUnits),
      pctSeparableAmongAuthorityMarked: pct(classCounts.separable, authorityMarkedUnits)
    });

    if (dict.code === "skd") sampleRows.push(...buildSample(flatRows));
  }

  const payload = {
    schemaVersion: "1.0.0",
    status: "source-backed-r2-kosa-fusion",
    ...licenseFields(),
    claim: "Corpus-scale SKD/VCP iti-unit classification: does the sense/citation split cleanly (separable, the VCP pattern) or fuse into one unit (authority-terminal, the SKD pattern)?",
    generatedBy: "npm run build-r2-kosa-fusion",
    sourceRoot: "../csl-orig/v02",
    method: {
      unitSplit: "iti-unit (splitIndigenous(), build-r2-source-anchors.mjs)",
      authoritySignal: "indigenousAuthorityHints() (VCP `...0` siglum convention, curated SKD authority-name list) generalised with the SKD sandhi-fused `ity<word>` formula pattern.",
      fusionRule: `A unit with an authority signal is "authority-terminal" if >= ${FUSION_MIN_CONTENT_CHARS} non-whitespace characters of definitional content precede the earliest authority match within the SAME unit; otherwise "separable" (the unit is essentially the citation tag alone, and its definition sits in a sibling unit).`
    },
    limitations: [
      "Pattern-based classifier over a heterogeneous corpus of philological Sanskrit prose, not a scholar-reviewed sense/citation boundary; borderline units exist (short definitions that happen to fall under the fusion threshold, long discursive quotations misread as content).",
      `FUSION_MIN_CONTENT_CHARS = ${FUSION_MIN_CONTENT_CHARS} is a documented threshold, not a calibrated cut point; report at other thresholds may shift the fused/separable split modestly without changing which dictionary dominates.`,
      "VCP's discursive commentarial register (long Mimamsa-style argument interspersed with `...0` sigla) differs structurally from the simple synonym-run register the *dharma* exemplar illustrates; per-record classification may diverge from the record-level exemplar description even where the dictionary-level contrast holds.",
      "The ~100-row SKD sample below is a stratified draw for human citational-vs-grammatical adjudication (REVISION_BRIEF_P2_OBS.md Part 4 / A08 C-M1); it is not itself the adjudicated result."
    ],
    perDict
  };

  const samplePayload = {
    schemaVersion: "1.0.0",
    status: "adjudication-sample",
    ...licenseFields(),
    claim: "Stratified ~100-row sample of SKD iti-units (authority-terminal / separable / other-no-authority) for human citational-vs-grammatical adjudication.",
    generatedBy: "npm run build-r2-kosa-fusion",
    dict: "skd",
    rows: sampleRows
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  payload.generatedAt = generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  samplePayload.generatedAt = generatedAtForPayload(readJsonIfExists(SAMPLE_OUT, fs), samplePayload);
  fs.writeFileSync(SAMPLE_OUT, `${JSON.stringify(samplePayload, null, 2)}\n`);

  console.log(`Wrote ${path.relative(process.cwd(), JSON_OUT)}`);
  for (const row of perDict) {
    console.log(
      `  ${row.dict.toUpperCase()} records=${row.records} authorityUnits=${row.authorityMarkedUnits} ` +
      `(${row.pctRecordsWithAuthorityUnit}% of records) fused=${row.classCounts["authority-terminal"]} ` +
      `(${row.pctFusedAmongAuthorityMarked}%) separable=${row.classCounts.separable} (${row.pctSeparableAmongAuthorityMarked}%)`
    );
  }
  console.log(`Wrote ${path.relative(process.cwd(), SAMPLE_OUT)} (${sampleRows.length} rows)`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
