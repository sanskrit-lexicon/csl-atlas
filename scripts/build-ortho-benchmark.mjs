// Build the de/ru historical-normalization benchmark (H7103).
//
// Freezes a 200-token gold sample from the csl-orig v02 gloss text of the
// German Petersburg-line dictionaries (PWG, PWK, CCS, SCH) and the Russian
// Kossovich dictionary (the only Russian-gloss text available locally),
// with source file + line + context and the modern target supplied by the
// frozen SanskritSpellCheck reform maps.
//
// The sample is SOURCE-TEXT-GROUNDED, not scan-image verified: every token is
// an actual token occurrence in the digitised dictionary transcription (the
// committed csl-orig line is named), but this builder does not re-open page
// images. That limitation is stated in the dataset card and the JSON caveats.
//
// Sampling is deterministic: distinct old forms per dictionary are shuffled
// with a fixed-seed mulberry32 stream, 25 forms are taken per German
// dictionary (100 total) and 100 from Kossovich; each dictionary's 25 rows are
// split 15 train / 5 dev / 5 test (Kossovich 60/20/20).
//
// The reform maps are owned by SanskritSpellCheck and consumed read-only.
// They are NOT redistributed: the committed gold TSV carries only the sampled
// token -> modern target pairs (short factual word pairs) plus attribution.
//
// Usage:
//   DE_MAP=/path/de_reform_map.tsv RU_MAP=/path/ru_reform_map.tsv \
//   CSL_ORIG_ROOT=/path/csl-orig/v02 KOSSOVICH_JSONL=/path/kossovich.jsonl \
//   npm run build-ortho-benchmark

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { cleanGloss, glossTokens, DE_PROFILE, RU_PROFILE, mulberry32, round } from "./build-ortho-drift.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { normalizeRule, computeMetrics, bootstrapMetricCis } from "./score-ortho-benchmark.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-ortho-benchmark";
const GITHUB_ROOT = path.resolve(process.cwd(), "..");
const SOURCE_ROOT = process.env.CSL_ORIG_ROOT || path.resolve(process.cwd(), "..", "csl-orig", "v02");
const DE_MAP_PATH = process.env.DE_MAP || path.resolve(GITHUB_ROOT, "SanskritSpellCheck", "ortho_drift", "de_reform_map.tsv");
const RU_MAP_PATH = process.env.RU_MAP || path.resolve(GITHUB_ROOT, "SanskritSpellCheck", "ortho_drift", "ru_reform_map.tsv");
const KOSSOVICH_PATH =
  process.env.KOSSOVICH_JSONL || path.resolve(GITHUB_ROOT, "SamudraManthanam", "web", "corpus_builder", "jsonl", "kossovich.jsonl");
const OUT_DIR = path.resolve(process.cwd(), "data", "ortho");
const JSON_OUT = path.join(OUT_DIR, "normalization_benchmark.json");
const GOLD_OUT = path.join(OUT_DIR, "gold.tsv");
const CANDIDATES_OUT = path.join(OUT_DIR, "candidates.tsv");
const CARD_OUT = path.join(OUT_DIR, "normalization_benchmark.card.md");
const DOCS_CARD_OUT = path.resolve(process.cwd(), "docs", "ORTHO_BENCHMARK.md");

const SEED = 71031910;
const PER_GERMAN_DICT = 25;
const RU_ROWS = 100;

export const GERMAN_ROSTER = [
  { code: "pwg", label: "PWG" },
  { code: "pw", label: "PWK" },
  { code: "ccs", label: "CCS" },
  { code: "sch", label: "SCH" }
];

const DE_KNOWN_ERAS = new Set([
  "1901-th", "1901-c", "1901-c-iren", "1901-iren", "1901", "1901-th-adjacent",
  "1996-ss", "archaic-ey"
]);
const RU_KNOWN_ERAS = new Set(["1918-yat", "1918-i", "1918-hardsign", "1918-fita", "1918-izhitsa"]);

export function loadMap(filePath, knownEras) {
  const byOld = new Map();
  for (const line of fs.readFileSync(filePath, "utf8").split(/\r?\n/)) {
    if (!line || line.startsWith("#") || !line.includes("\t")) continue;
    const [old, modern, eraRaw] = line.split("\t");
    if (!old || !modern) continue;
    byOld.set(old.toLowerCase(), {
      modern: modern.toLowerCase(),
      era: knownEras.has(eraRaw) ? eraRaw : "other-map-era"
    });
  }
  return byOld;
}

function contextAround(line, token, width = 180) {
  const collapsed = String(line ?? "").replace(/\s+/g, " ").trim();
  if (!collapsed) return "";
  const at = collapsed.toLowerCase().indexOf(token);
  if (at < 0) return collapsed.slice(0, width);
  const start = Math.max(0, at - Math.floor(width / 3));
  const end = Math.min(collapsed.length, start + width);
  return `${start > 0 ? "…" : ""}${collapsed.slice(start, end)}${end < collapsed.length ? "…" : ""}`;
}

function shuffleInPlace(items, rand) {
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

/** Collect the first occurrence of every dated old form in a line iterator. */
export function collectOccurrences(profile, map, lines, { datedOnly = true } = {}) {
  const occurrences = new Map();
  let lineNo = 0;
  for (const line of lines) {
    lineNo += 1;
    for (const token of glossTokens(profile, line)) {
      if (occurrences.has(token)) continue;
      const hit = map.get(token);
      if (!hit) continue;
      if (hit.modern === token) continue; // identity pair: not a normalization case
      if (datedOnly && hit.era === "other-map-era") continue;
      occurrences.set(token, {
        line: lineNo,
        context: contextAround(line, token),
        modern: hit.modern,
        era: hit.era
      });
    }
  }
  return occurrences;
}

export function sampleRows({ lang, dict, label, sourceFile, occurrences, count, seed }) {
  const forms = [...occurrences.keys()].sort();
  if (forms.length < count) {
    throw new Error(`${label}: only ${forms.length} distinct dated old forms found, need ${count}`);
  }
  const rand = mulberry32(seed);
  shuffleInPlace(forms, rand);
  const chosen = forms.slice(0, count);
  return chosen.map((token, index) => {
    const occ = occurrences.get(token);
    return {
      id: `${lang}-${dict}-${String(index + 1).padStart(3, "0")}`,
      split: null,
      lang,
      dict,
      source_file: sourceFile,
      line: occ.line,
      token,
      target: occ.modern,
      era: occ.era,
      context: occ.context,
      scan_url: "",
      scan_verified: "false"
    };
  });
}

/**
 * Stratified 100/50/50 split. German quotas per dictionary sum to 50/25/25;
 * Kossovich contributes 50/25/25 on its own. Rows keep their deterministic
 * within-dictionary order, so the split is reproducible.
 */
export const GERMAN_SPLIT_QUOTAS = {
  pwg: { train: 13, dev: 6, test: 6 },
  pw: { train: 13, dev: 6, test: 6 },
  ccs: { train: 12, dev: 6, test: 7 },
  sch: { train: 12, dev: 7, test: 6 }
};

export function assignSplits(rows) {
  const byDict = new Map();
  for (const row of rows) {
    if (!byDict.has(row.dict)) byDict.set(row.dict, []);
    byDict.get(row.dict).push(row);
  }
  for (const [dict, dictRows] of byDict) {
    const quota = dict === "kow" ? { train: 50, dev: 25, test: 25 } : GERMAN_SPLIT_QUOTAS[dict];
    if (!quota) throw new Error(`no split quota for ${dict}`);
    const total = quota.train + quota.dev + quota.test;
    if (dictRows.length !== total) throw new Error(`${dict}: ${dictRows.length} rows but quota sums to ${total}`);
    dictRows.forEach((row, index) => {
      row.split = index < quota.train ? "train" : index < quota.train + quota.dev ? "dev" : "test";
    });
  }
  return rows;
}

export function buildGold({ deMap, ruMap, germanFiles, kossovichPath }) {
  const rows = [];
  for (const [index, spec] of GERMAN_ROSTER.entries()) {
    const filePath = germanFiles[spec.code];
    if (!filePath || !fs.existsSync(filePath)) throw new Error(`missing German source for ${spec.code}: ${filePath}`);
    const occurrences = collectOccurrences(DE_PROFILE, deMap, fs.readFileSync(filePath, "utf8").split(/\r?\n/));
    rows.push(
      ...sampleRows({
        lang: "de",
        dict: spec.code,
        label: spec.label,
        sourceFile: `v02/${spec.code}/${spec.code}.txt`,
        occurrences,
        count: PER_GERMAN_DICT,
        seed: SEED + index * 101
      })
    );
  }

  const kossovich = fs
    .readFileSync(kossovichPath, "utf8")
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line))
    .filter((row) => !row.deleted);
  const ruLines = kossovich.map((row) => row.text ?? "");
  const occurrences = collectOccurrences(RU_PROFILE, ruMap, ruLines);
  rows.push(
    ...sampleRows({
      lang: "ru",
      dict: "kow",
      label: "KOW",
      sourceFile: "SamudraManthanam/web/corpus_builder/jsonl/kossovich.jsonl",
      occurrences,
      count: RU_ROWS,
      seed: SEED + 999
    })
  );

  // Kossovich line numbers are 1-based JSONL record indexes.
  return assignSplits(rows);
}

export function toTsv(rows) {
  const header = [
    "id", "split", "lang", "dict", "source_file", "line", "scan_url", "scan_verified",
    "token", "target", "era", "context"
  ];
  const esc = (value) => String(value ?? "").replace(/\t/g, " ").replace(/\r?\n/g, " ");
  return [header.join("\t"), ...rows.map((row) => header.map((key) => esc(row[key])).join("\t"))].join("\n") + "\n";
}

export function parseTsv(text) {
  const lines = text.split(/\r?\n/).filter((line) => line.trim());
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    return Object.fromEntries(header.map((key, index) => [key, cells[index] ?? ""]));
  });
}

export function summarize(rows, predictions, name) {
  const pairs = rows.map((row) => ({ lang: row.lang, dict: row.dict, split: row.split, target: row.target, pred: predictions(row) }));
  const metrics = computeMetrics(pairs);
  const byDict = {};
  for (const [dict, values] of Object.entries(metrics.byDict)) {
    byDict[dict] = {
      ...values,
      ci: bootstrapMetricCis(pairs.filter((pair) => pair.dict === dict), { b: 1000, seed: SEED + dict.length })
    };
  }
  return {
    name,
    ...metrics,
    byDict,
    ci: bootstrapMetricCis(pairs, { b: 1000, seed: SEED })
  };
}

export function candidatesTsv(rows) {
  const header = ["id", "lang", "dict", "source_file", "line", "token", "target", "reason"];
  const reason = "no scan-image verification: source-text-grounded only; page image not opened, scan_verified=false";
  return [header.join("\t"), ...rows.map((row) => [row.id, row.lang, row.dict, row.source_file, row.line, row.token, row.target, reason].join("\t"))].join("\n") + "\n";
}

export function splitManifest(rows) {
  const body = rows.map((row) => `${row.id}\t${row.split}`).join("\n") + "\n";
  return {
    seed: SEED,
    rule: "stratified by dictionary; German quotas pwg/pw 13-6-6, ccs 12-6-7, sch 12-7-6; Kossovich 50-25-25",
    sha256: crypto.createHash("sha256").update(body).digest("hex"),
    body
  };
}

export function buildPayload({ rows, generatedAt }) {
  const goldTsv = toTsv(rows);
  const sha256 = crypto.createHash("sha256").update(goldTsv).digest("hex");
  const counts = { total: rows.length, german: rows.filter((r) => r.lang === "de").length, russian: rows.filter((r) => r.lang === "ru").length };
  const splitCounts = {};
  for (const row of rows) splitCounts[row.split] = (splitCounts[row.split] ?? 0) + 1;
  const ruleMap = summarize(rows, (row) => normalizeRule(row.lang, row.token), "rule-map rewrite baseline");
  const identity = summarize(rows, (row) => row.token, "identity (no-op) baseline");
  const mapOracle = summarize(rows, (row) => row.target, "frozen reform-map lookup (ceiling)");

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    title: "German and Russian historical orthographic normalization benchmark (200 gold tokens)",
    description:
      "A frozen 200-token gold sample for historical orthographic normalization: 100 pre-reform German gloss tokens from PWG, PWK, CCS and SCH, and 100 pre-1918 Russian gloss tokens from Kossovich. Each row names the csl-orig/SamudraManthanam source record, line number, a short context, the historical token and its modern target.",
    citation:
      "Bollmann, M. (2019). A Large-Scale Comparison of Historical Text Normalization Systems. Proceedings of NAACL 2019 (N19-1389). Metrics follow that evaluation: token accuracy and character error rate (CER) on a fixed gold set.",
    method:
      "Distinct old forms were collected from the csl-orig v02 gloss text (cleanGloss/glossTokens from build-ortho-drift.mjs) by membership in the frozen SanskritSpellCheck reform maps; only era-attributed dated reforms (1901-*/1996-ss/archaic-ey for German, 1918-* for Russian) are admitted. Forms were deterministically shuffled with fixed-seed mulberry32 and 25 were taken per German dictionary (100) and 100 from Kossovich. Each token instance is the first source occurrence of the selected form; line = 1-based physical line (Kossovich: JSONL record index). Targets are the map's modern-side form. Splits are stratified by dictionary into 100 train / 50 dev / 50 test; the split seed and manifest hash are recorded. No page image was opened, so every row carries scan_verified=false and appears in candidates.tsv with that reason.",
    sampling: {
      seed: SEED,
      germanPerDict: PER_GERMAN_DICT,
      russianRows: RU_ROWS,
      unit: "distinct old form, one source occurrence each",
      splitRule: "stratified by dictionary; global 100 train / 50 dev / 50 test"
    },
    sources: [
      { id: "csl-orig", url: "https://github.com/sanskrit-lexicon/csl-orig", license: "CC-BY-SA-4.0", note: "v02/pwg/pwg.txt, v02/pw/pw.txt, v02/ccs/ccs.txt, v02/sch/sch.txt" },
      { id: "samudra-manthanam", url: "https://github.com/gasyoun/SamudraManthanam", license: "see upstream", note: "web/corpus_builder/jsonl/kossovich.jsonl" },
      { id: "sanskrit-spellcheck", url: "https://github.com/drdhaval2785/SanskritSpellCheck", license: "upstream declares no license (recorded honestly; map not redistributed)", note: "ortho_drift/de_reform_map.tsv, ortho_drift/ru_reform_map.tsv" }
    ],
    rightsNote:
      "Gold contexts are short excerpts of csl-orig text (CC-BY-SA-4.0), so this benchmark is CC-BY-SA-4.0. SanskritSpellCheck declares no software license; its reform maps are consumed read-only to derive modern targets and are NOT redistributed here (no map TSV is committed). Only 200 short token/target pairs and brief contexts are published. Kossovich excerpts come from the SamudraManthanam corpus build; consult that repository for its rights statement.",
    counts: { ...counts, bySplit: splitCounts, scanVerified: 0, scanUnverified: rows.length },
    scope:
      "Reform-map benchmark under the handoff's fail-path clause: scan-image grounding was not established, so no scan claim is made. Every row is source-text-grounded in a named csl-orig/SamudraManthanam line; scan_verified=false and candidates.tsv carries the full honest residual.",
    splitManifest: splitManifest(rows),
    dicts: GERMAN_ROSTER.map((d) => ({ code: d.code, label: d.label, lang: "de", rows: PER_GERMAN_DICT })).concat([
      { code: "kow", label: "KOW", lang: "ru", rows: RU_ROWS }
    ]),
    metrics: { ruleMap, identity, mapOracle },
    goldTsv: { path: "data/ortho/gold.tsv", rows: rows.length, sha256 },
    candidatesTsv: { path: "data/ortho/candidates.tsv", rows: rows.length, reason: "no scan-image verification (source-text-grounded only)" },
    datasetCard: "data/ortho/normalization_benchmark.card.md",
    docsCard: "docs/ORTHO_BENCHMARK.md",
    caveats: [
      "SOURCE-TEXT-GROUNDED, NOT SCAN-IMAGE VERIFIED: each row is grounded in a named csl-orig/SamudraManthanam source line, but no page image was re-opened. This is not a scan-level diplomatic edition, and no scan claim is made (handoff fail-path scope).",
      "All 200 rows carry scan_verified=false and are listed in candidates.tsv with the reason; the gold set is the reform-map benchmark, not a scan-verified subset.",
      "Targets are the frozen SanskritSpellCheck reform-map modern forms. The rule-map baseline is therefore an agreement-with-the-map lower bound, not an independent historical judgement; the map's provenance and limits are upstream.",
      "The reform maps are not redistributed: no map TSV is committed. Only the 200 sampled token/target pairs are published, with upstream attribution; SanskritSpellCheck declares no license.",
      "The German roster is the Petersburg line plus CCS and SCH as specified by the handoff (PWG, PWK, CCS, SCH). GRA and PWKVN are outside this benchmark.",
      "Russian is KOW (Kossovich, 1854) only: csl-orig v02 exposes no second Russian-gloss dictionary locally, so the Russian half is single-dictionary and single-date.",
      "The 'map oracle' row is a ceiling by construction (it copies the gold target) and exists only to bound the metric; the substantive baseline is the rule-map rewriter.",
      "CER uses lowercased Unicode code points and target-length normalization; WER is the token error rate (1 - accuracy) on single-token rows. This is a token-level adaptation, not Bollmann's sentence-level corpus CER.",
      "The Kossovich source is a corpus JSONL, not a csl-orig v02 file; its 'line' is the 1-based JSONL record index."
    ],
    boundary: [
      "Gloss-language (meta-language) orthography only. Sanskrit-side orthography is out of scope. csl-orig is read, never written. Reform maps stay upstream in SanskritSpellCheck; only sampled gold pairs are committed."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return { payload, goldTsv };
}

function cardMarkdown(payload) {
  const m = payload.metrics;
  const row = (name, metric) => `| ${name} | ${(metric.accuracy * 100).toFixed(1)}% | ${(metric.wer * 100).toFixed(1)}% | ${metric.cer.toFixed(4)} | ${metric.ci?.accuracy ? `[${metric.ci.accuracy.map((v) => (v * 100).toFixed(1)).join(", ")}]` : "—"} | ${metric.n} |`;
  return `# Dataset card — de/ru historical normalization benchmark (H7103)

_Created: 19-10-2026 · Schema ${payload.schemaVersion}_

## What this is

A frozen **200-token** gold set for historical orthographic normalization of the
dictionary meta-language: **100 German** pre-reform gloss tokens (PWG, PWK, CCS,
SCH) and **100 Russian** pre-1918 gloss tokens (Kossovich). Each gold row gives a
source file, line, short context, historical token and modern target.

Files:

- \`data/ortho/gold.tsv\` — the gold rows
  (sha256 \`${payload.goldTsv.sha256}\`, ${payload.goldTsv.rows} rows),
  including \`scan_url\` and \`scan_verified\` columns.
- \`data/ortho/candidates.tsv\` — the honest residual: all rows whose
  \`scan_verified\` is false, with the reason (here: all ${payload.candidatesTsv.rows}).
- \`data/ortho/normalization_benchmark.json\` — this card's machine-readable
  envelope: counts, splits, baselines, caveats, rights.
- \`data/ortho/normalization_benchmark.card.md\` — this file.
- \`scripts/build-ortho-benchmark.mjs\` — reproducible builder (needs the
  sibling csl-orig/SanskritSpellCheck/SamudraManthanam inputs; the committed
  files are the CI-safe artifact).
- \`docs/ORTHO_BENCHMARK.md\` — the same card at its handoff-specified path.
- \`scripts/score-ortho-benchmark.mjs\` — scorer (accuracy + WER + CER,
  bootstrap CIs, overall and by language/dictionary/split;
  \`--predictions id<TAB>prediction\`).

## Provenance and grounding

- German: \`csl-orig/v02/{pwg,pw,ccs,sch}\`, CC-BY-SA-4.0.
- Russian: \`SamudraManthanam/web/corpus_builder/jsonl/kossovich.jsonl\`.
- Targets: frozen \`SanskritSpellCheck/ortho_drift/{de,ru}_reform_map.tsv\`,
  consumed read-only; the maps are not redistributed.
- Grounding: **source-text-grounded, not scan-image verified.** Every token is
  an actual occurrence in the digitised transcription at the named line; no page
  image was re-opened. Every row has \`scan_verified=false\` and is listed in
  \`candidates.tsv\`. This is the handoff's **fail-path scope**: publish the
  reform-map benchmark with an explicit caveat and no scan claim.

## Splits

| split | rows |
|---|---:|
${Object.entries(payload.counts.bySplit).map(([k, v]) => `| ${k} | ${v} |`).join("\n")}

Stratified by dictionary: PWG/PW 13-6-6, CCS 12-6-7, SCH 12-7-6,
Kossovich 50-25-25. Split seed and manifest sha256 are in the JSON.

## Baselines

| baseline | accuracy | WER | CER | 95% accuracy CI | n |
|---|---:|---:|---:|---:|---:|
${row(m.ruleMap.name, m.ruleMap)}
${row(m.identity.name, m.identity)}
${row(m.mapOracle.name, m.mapOracle)}

The **rule-map** baseline applies generic reform rules (\`th→t\`, final
\`iren→ieren\`, \`ß→ss\`; Russian \`ѣ→е\`, \`і→и\`, \`ѳ→ф\`, \`ѵ→и\`, final \`ъ\` dropped).
The **identity** baseline is the no-op floor. The **map-oracle** row copies the
gold target and is a ceiling by construction, not a model.

## Metrics

Token accuracy = exact match after lowercasing/NFC. WER = 1 - accuracy on these
single-token rows. CER = character Levenshtein distance on lowercased Unicode
code points, summed over the set and divided by the summed target length. 95%
CIs are fixed-seed row-level bootstrap (B=1,000). Framing follows Bollmann
(2019), NAACL, N19-1389; this is a token-level adaptation, not the paper's
sentence-level corpus CER. Per-dictionary CIs are in the JSON.

## Rights

The benchmark is **CC-BY-SA-4.0** (csl-orig source excerpts are CC-BY-SA-4.0).
SanskritSpellCheck **declares no license**; the reform maps are used read-only to
derive modern targets and are not redistributed. Only 200 short token/target
pairs plus brief contexts are published. Kossovich excerpts are from the
SamudraManthanam corpus build; check that repository for its rights statement.

## Known limitations

${payload.caveats.map((c) => `- ${c}`).join("\n")}

## Regeneration

\`\`\`
DE_MAP=…/de_reform_map.tsv RU_MAP=…/ru_reform_map.tsv \\
CSL_ORIG_ROOT=…/csl-orig/v02 KOSSOVICH_JSONL=…/kossovich.jsonl \\
npm run build-ortho-benchmark
npm run score-ortho-benchmark
npm test
\`\`\`
`;
}

function main() {
  for (const [label, file] of [
    ["German reform map", DE_MAP_PATH],
    ["Russian reform map", RU_MAP_PATH],
    ["Kossovich jsonl", KOSSOVICH_PATH]
  ]) {
    if (!fs.existsSync(file)) {
      console.error(`Required input missing: ${label} at ${file}. The committed benchmark is the CI-safe artifact; STOP — do not invent gold.`);
      process.exit(1);
    }
  }
  const deMap = loadMap(DE_MAP_PATH, DE_KNOWN_ERAS);
  const ruMap = loadMap(RU_MAP_PATH, RU_KNOWN_ERAS);
  const germanFiles = Object.fromEntries(GERMAN_ROSTER.map((d) => [d.code, path.join(SOURCE_ROOT, d.code, `${d.code}.txt`)]));
  const rows = buildGold({ deMap, ruMap, germanFiles, kossovichPath: KOSSOVICH_PATH });
  const { payload, goldTsv } = buildPayload({ rows });
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(GOLD_OUT, goldTsv);
  fs.writeFileSync(CANDIDATES_OUT, candidatesTsv(rows));
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  const card = cardMarkdown(payload);
  fs.writeFileSync(CARD_OUT, card);
  fs.mkdirSync(path.dirname(DOCS_CARD_OUT), { recursive: true });
  fs.writeFileSync(DOCS_CARD_OUT, card);
  console.log(`Wrote ${rows.length} gold rows (${payload.counts.german} de + ${payload.counts.russian} ru), splits ${JSON.stringify(payload.counts.bySplit)}`);
  console.log(`- ${path.relative(process.cwd(), GOLD_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), CANDIDATES_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), CARD_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), DOCS_CARD_OUT)}`);
  console.log(`  rule-map accuracy ${(payload.metrics.ruleMap.accuracy * 100).toFixed(1)}%, WER ${(payload.metrics.ruleMap.wer * 100).toFixed(1)}%, CER ${payload.metrics.ruleMap.cer.toFixed(4)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
