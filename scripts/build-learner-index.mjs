// Build the learner's reading-layer index.
//
// Joins the reader lemma-lookup (dictionary coverage + gender) with the DCS
// corpus frequency band, producing a compact per-lemma index a student can use
// to answer "is this word worth learning yet (frequency), and which dictionary
// should I trust for it (coverage)". Frequency is the organising principle:
// band 5 = learn first, band 1 = hapax.
//
// Honest scope: DCS bands are coarse (log10) and absent for ~unattested lemmas;
// Whitney roots / gaṇa and per-sense survival are NOT joined here (not present
// in csl-atlas) — see docs and the page Trust Block.
//
// Usage: npm run build-learner-index

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { loadDcsSummary } from "./lib/dcs-summary.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const ROOT = process.cwd();
const LOOKUP_PATH = path.resolve(ROOT, "src", "data", "dicts", "lemma-lookup.json");
const OUT_DIR = path.resolve(ROOT, "src", "data", "learner");
const OUT_PATH = path.join(OUT_DIR, "learner-index.json");

// Frequency band → learner-facing study priority (self-documenting in the data).
const BAND_LEGEND = [
  { band: 5, range: "1000+", en: "very common", ru: "очень частотное", priorityEn: "learn first", priorityRu: "учить в первую очередь" },
  { band: 4, range: "100–999", en: "common", ru: "частотное", priorityEn: "learn early", priorityRu: "учить рано" },
  { band: 3, range: "10–99", en: "uncommon", ru: "нечастотное", priorityEn: "learn later", priorityRu: "учить позже" },
  { band: 2, range: "2–9", en: "rare", ru: "редкое", priorityEn: "reference", priorityRu: "справочно" },
  { band: 1, range: "1", en: "hapax", ru: "гапакс", priorityEn: "reference", priorityRu: "справочно" },
  { band: 0, range: "—", en: "not in corpus", ru: "нет в корпусе", priorityEn: "uncorroborated", priorityRu: "без корпуса" }
];

function grammarReliableTuples(dicts, dictMeta) {
  return [...dicts].filter(t => dictMeta[t[0]]?.grammarReliable).sort((a, b) => a[0] - b[0]);
}

function representativeGender(dicts, dictMeta) {
  // gender from the highest-priority grammar-reliable dictionary that reports one
  for (const t of grammarReliableTuples(dicts, dictMeta)) {
    if (t[3]) return t[3];
  }
  return "";
}

function primarySource(dicts, dictMeta) {
  // [dictCode, firstLine] of the highest-priority grammar-reliable dict present,
  // else the first dict present — a "open this word in the source" pointer.
  const t = grammarReliableTuples(dicts, dictMeta)[0]
    ?? [...dicts].sort((a, b) => a[0] - b[0])[0];
  return t ? [dictMeta[t[0]].code, t[2]] : null;
}

function main() {
  const lookup = JSON.parse(fs.readFileSync(LOOKUP_PATH, "utf-8"));
  const dcs = loadDcsSummary();
  const dictMeta = Object.fromEntries(lookup.dictionaries.map((d, i) => [i, d]));

  const warnings = [];
  if (!Object.keys(dcs).length) {
    warnings.push("DCS summary absent (data/dcs/dcs_lemma_summary.json); all freqBand = 0.");
  }

  const byBand = Object.fromEntries(BAND_LEGEND.map(b => [b.band, 0]));
  let withFreq = 0;
  const entries = [];
  for (const [lemma, dicts] of lookup.entries) {
    const { normalized } = normalizeLemma(lemma);
    const rec = dcs[normalized] ?? null;
    const fb = rec?.freqBand ?? 0;
    if (fb > 0) withFreq += 1;
    byBand[fb] += 1;
    const codes = dicts.map(t => dictMeta[t[0]].code);
    const gr = dicts.filter(t => dictMeta[t[0]].grammarReliable).length;
    entries.push({
      l: lemma,
      fb,
      at: Boolean(rec?.attested),
      c: dicts.length,
      gr,
      d: codes,
      g: representativeGender(dicts, dictMeta),
      src: primarySource(dicts, dictMeta)
    });
  }

  // sanity
  for (const e of entries) {
    if (e.fb < 0 || e.fb > 5) throw new Error(`bad freqBand ${e.fb} for ${e.l}`);
  }

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: new Date().toISOString(),
    sourcePath: "src/data/dicts/lemma-lookup.json + data/dcs/dcs_lemma_summary.json",
    generatedBy: "npm run build-learner-index",
    claim: "Frequency-graded reader index: each lemma carries its DCS corpus frequency band and cross-dictionary coverage, for study-priority and trust.",
    evidenceLevel: "derived",
    dictionaries: lookup.dictionaries,
    grammarReliableCodes: lookup.dictionaries.filter(d => d.grammarReliable).map(d => d.code),
    inputSchemes: ["SLP1", "IAST"],
    minDicts: lookup.minDicts,
    hrefBase: lookup.hrefBase,
    bandLegend: BAND_LEGEND,
    tupleFields: { l: "lemma (SLP1)", fb: "DCS frequency band 0–5", at: "attested in DCS", c: "dictionary count", gr: "grammar-reliable dict count", d: "dictionary codes present", g: "representative gender (grammar-reliable dict)", src: "[dictCode, firstLine] primary source pointer" },
    assumptions: [
      "Frequency bands are coarse log10 buckets from the DCS corpus (band 5 = 1000+ occurrences ... band 1 = hapax); band 0 = lemma not attested in the DCS corpus, which does NOT mean the word is unused, only uncorroborated by this corpus.",
      "Gender is the value reported by the highest-priority grammar-reliable dictionary present (MW > AP > PWG > PWK > WIL); VCP/SKD prose genders are not used.",
      "Lemma set is the reader lookup (attested in at least minDicts dictionaries)."
    ],
    warnings,
    counts: { recordCount: entries.length, withFrequency: withFreq, byBand },
    entries
  };

  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUT_PATH, fs), payload);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  // Written compact (like lemma-lookup/lemma-dossier): one large data file.
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload)}\n`);
  console.log(`Wrote ${path.relative(ROOT, OUT_PATH)} (${entries.length} lemmas; ${withFreq} with a DCS frequency band).`);
  console.log(`  by band: ${BAND_LEGEND.map(b => `${b.band}:${byBand[b.band]}`).join("  ")}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();

export { representativeGender, BAND_LEGEND };
