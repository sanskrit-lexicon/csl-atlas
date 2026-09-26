// Build the usage/register label census across the CDSL dictionaries (H5333).
//
// The lexicographers-only label (MW <ls>L.) was studied for MW alone. This
// builder generalises the measurement: it finds every USAGE and REGISTER label
// a dictionary writes into its markup — Vedic, epic, classical, poetic,
// figurative, vulgar, Buddhist, Prākrit, Pāli, the L. hedge and the rest —
// normalises each (tag, token) pair onto one closed vocabulary published in
// data/lexico/usage_register_mapping.json, and reports counts and entry rates
// per dictionary.
//
// The load-bearing discipline is the MATCHING, not the counting. The same
// token means different things in different tags: <ab>lit. is always English
// 'literally' while <lang>Lit. is Lithuanian; <ab>ep. is 'epithet' while
// <lang>ep. is 'epic'; <lang>L. in AP is Latin while <ls>L. in MW is the
// lexicographers hedge. So a label is counted only on an exact (tag, token)
// pair listed in the mapping — everything else in those tags (grammar,
// editorial, etymology languages) is ignored, and the ignored look-alikes are
// published under `excluded` in the mapping.
//
// Pure derivation from the csl-orig source (`../csl-orig/v02/<code>/<code>.txt`,
// never committed) plus the committed mapping. Deterministic
// (generatedAtForPayload idiom).
//
// Usage: npm run build-usage-register-census
//        (then npm run validate-usage-register-census)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-usage-register-census";
const CSLORIG_ROOT = path.resolve(process.cwd(), "..", "csl-orig", "v02");
const MAPPING_PATH = path.resolve(process.cwd(), "data", "lexico", "usage_register_mapping.json");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "usage_register_census.json");
const SOURCE_OUT = path.join(OUT_DIR, "usage_register_census.source.json");

// One markup label: <tag>token</tag> or <tag n="...">token</tag>. Tokens never span a line.
const LABEL_RE = /<(ab|lang|ls)\b[^>]*>([^<]*)<\/\1>/g;

export function loadMapping(file = MAPPING_PATH) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

/** Closed vocabulary as a flat Set of category names. */
export function vocabularySet(mapping) {
  const set = new Set();
  for (const categories of Object.values(mapping.vocabulary)) {
    for (const c of categories) set.add(c);
  }
  return set;
}

/**
 * Cross-check the mapping against its own closed vocabulary and its negative map.
 * Throws on: a label category outside the vocabulary, an (tag, token) pair listed
 * both as a label and as an excluded look-alike, or an empty labels array.
 */
export function assertMappingConsistent(mapping) {
  const vocab = vocabularySet(mapping);
  if (!Array.isArray(mapping.labels) || mapping.labels.length === 0) {
    throw new Error("usage_register_mapping.json: `labels` is empty");
  }
  const excluded = new Set((mapping.excluded?.tokens ?? []).map((t) => `${t.tag}\t${t.token}`));
  for (const row of mapping.labels) {
    if (!vocab.has(row.category)) {
      throw new Error(`usage_register_mapping.json: "${row.category}" (${row.tag} ${row.token}) is outside the closed vocabulary`);
    }
    const key = `${row.tag}\t${row.token}`;
    if (excluded.has(key)) {
      throw new Error(`usage_register_mapping.json: ${JSON.stringify(key)} is listed both as a label and as an excluded look-alike`);
    }
  }
  return true;
}

/**
 * Index the mapping rows into `${tag}\t${token}` -> {class, category, gloss, dictionaries}.
 * Throws on a duplicate key, so the map can never silently shadow a label.
 */
export function indexMapping(mapping) {
  const index = new Map();
  for (const row of mapping.labels) {
    const key = `${row.tag}\t${row.token}`;
    if (index.has(key)) throw new Error(`usage_register_mapping.json: duplicate label ${JSON.stringify(key)}`);
    index.set(key, row);
  }
  return index;
}

function isAllowed(row, code) {
  return !row.dictionaries || row.dictionaries.includes(code);
}

/** Find the dictionaries present as `<code>/<code>.txt` under the csl-orig v02 root. */
export function discoverDictionaries(root = CSLORIG_ROOT) {
  if (!fs.existsSync(root)) {
    throw new Error(
      `csl-orig v02 root not found at ${root}. The census reads the dictionary sources; ` +
        "clone sanskrit-lexicon/csl-orig next to csl-atlas (never commit it)."
    );
  }
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .filter((code) => fs.existsSync(path.join(root, code, `${code}.txt`)))
    .sort();
}

/**
 * Census one dictionary from its raw text.
 * Returns { code, entries, instances, entriesWithLabel, byCategory, byLabel }.
 *
 * A label instance is counted once per markup occurrence; an entry is credited
 * to a category when at least one of its records carries that category. Records
 * are the <L>..<LEND> shell used by every CDSL dictionary.
 */
export function censusDictionary(code, text, index) {
  const lines = text.split(/\r?\n/);
  let entries = 0;
  let inRecord = false;
  let instances = 0;
  let entriesWithLabel = 0;
  let currentRecordHasLabel = false;
  const entryCategories = new Set(); // categories seen in the current record
  const byCategory = new Map(); // category -> { class, instances, entries }
  const byLabel = new Map(); // `${tag}\t${token}` -> { tag, token, category, instances }
  const categoriesCredited = new Set();

  const creditRecord = () => {
    if (currentRecordHasLabel) entriesWithLabel += 1;
    for (const c of entryCategories) {
      if (!byCategory.has(c)) byCategory.set(c, { class: "", instances: 0, entries: 0 });
      byCategory.get(c).entries += 1;
    }
    entryCategories.clear();
    currentRecordHasLabel = false;
  };

  for (const line of lines) {
    if (line.startsWith("<L>")) {
      if (inRecord) creditRecord();
      inRecord = true;
      entries += 1;
    }
    // Collect labels on this line (the header line can carry them too).
    LABEL_RE.lastIndex = 0;
    let m;
    while ((m = LABEL_RE.exec(line)) !== null) {
      const tag = m[1];
      const token = m[2].trim();
      const row = index.get(`${tag}\t${token}`);
      if (!row) continue;
      if (!isAllowed(row, code)) continue;
      instances += 1;
      currentRecordHasLabel = true;
      const key = `${tag}\t${token}`;
      if (!byLabel.has(key)) byLabel.set(key, { tag, token, category: row.category, gloss: row.gloss, instances: 0 });
      byLabel.get(key).instances += 1;
      if (!byCategory.has(row.category)) byCategory.set(row.category, { class: row.class, instances: 0, entries: 0 });
      byCategory.get(row.category).instances += 1;
      entryCategories.add(row.category);
      categoriesCredited.add(row.category);
    }
    if (line.startsWith("<LEND>")) {
      creditRecord();
      inRecord = false;
    }
  }
  if (inRecord) creditRecord();

  const categories = [...byCategory.entries()]
    .map(([category, rec]) => ({
      category,
      class: rec.class,
      instances: rec.instances,
      entries: rec.entries,
      instancesPer1000Entries: entries > 0 ? Number(((rec.instances / entries) * 1000).toFixed(4)) : 0,
      shareOfInstances: instances > 0 ? Number((rec.instances / instances).toFixed(4)) : 0
    }))
    .sort((a, b) => b.instances - a.instances || (a.category < b.category ? -1 : 1));

  const labels = [...byLabel.values()].sort((a, b) => b.instances - a.instances || (a.token < b.token ? -1 : 1));

  return {
    code,
    entries,
    instances,
    entriesWithLabel,
    pctEntriesWithLabel: entries > 0 ? Number(((entriesWithLabel / entries) * 100).toFixed(4)) : 0,
    instancesPer1000Entries: entries > 0 ? Number(((instances / entries) * 1000).toFixed(4)) : 0,
    categoriesCredited: categoriesCredited.size,
    byCategory: categories,
    byLabel: labels
  };
}

/**
 * Build the full census payload from [{code, text}] sources.
 * Pure function: no fs, no clock beyond the injected generatedAt.
 */
export function buildCensus(sources, mapping, generatedAt) {
  assertMappingConsistent(mapping);
  const index = indexMapping(mapping);
  const vocab = vocabularySet(mapping);
  const perDictionary = [];

  let totalEntries = 0;
  let totalInstances = 0;
  let totalEntriesWithLabel = 0;
  const globalCategory = new Map(); // category -> {class, instances, entries}
  const dictionariesWithLabels = new Set();
  const diagnostics = [];

  for (const { code, text } of sources) {
    const c = censusDictionary(code, text, index);
    totalEntries += c.entries;
    totalInstances += c.instances;
    totalEntriesWithLabel += c.entriesWithLabel;
    if (c.instances > 0) dictionariesWithLabels.add(code);
    else diagnostics.push({ code, reason: "no mapped usage/register label in markup" });

    perDictionary.push(c);

    for (const cat of c.byCategory) {
      if (!vocab.has(cat.category)) throw new Error(`${code}: category "${cat.category}" outside the closed vocabulary`);
      if (!globalCategory.has(cat.category)) globalCategory.set(cat.category, { class: cat.class, instances: 0, entries: 0 });
      const g = globalCategory.get(cat.category);
      g.instances += cat.instances;
      g.entries += cat.entries;
    }
  }

  const dictionaries = [...globalCategory.entries()]
    .map(([category, rec]) => ({
      category,
      class: rec.class,
      instances: rec.instances,
      entries: rec.entries,
      instancesPer1000Entries: totalEntries > 0 ? Number(((rec.instances / totalEntries) * 1000).toFixed(4)) : 0,
      shareOfInstances: totalInstances > 0 ? Number((rec.instances / totalInstances).toFixed(4)) : 0
    }))
    .sort((a, b) => b.instances - a.instances || (a.category < b.category ? -1 : 1));

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    status: "usage-register-census",
    claim:
      "Every CDSL dictionary states a word's usage or register in a small, dictionary-specific set of markup labels; normalised onto one closed vocabulary the labels are comparable across dictionaries, and the per-dictionary rate shows how much of the lexicon each dictionary marks for register at all.",
    evidenceLabel: "observed",
    ownerRepo: "csl-atlas",
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "data/lexico/usage_register_mapping.json",
      "scripts/build-usage-register-census.mjs",
      "../csl-orig/v02/<code>/<code>.txt (source of truth, external)"
    ],
    method:
      "For each csl-orig dictionary, scan the <ab>, <lang> and <ls> markup tags; count an occurrence only when its exact (tag, token) pair is listed in data/lexico/usage_register_mapping.json; normalise it to the closed vocabulary; report instances, the number of <L>..<LEND> records carrying the label, and the instances-per-1000-entries rate per dictionary.",
    limit:
      "Zero is not absence. A dictionary with no mapped label marks register in prose, not markup (the indigenous SKD/VCP and the untagged reverse dictionaries), or simply does not mark register at all. Only marked labels are counted; the mission's 'the like' is bounded by the published mapping and its `excluded` section.",
    sourceCommit: readUpstreamCommit(),
    vocabulary: mapping.vocabulary,
    mappingSummary: {
      source: "data/lexico/usage_register_mapping.json",
      labels: mapping.labels.length,
      excludedLookAlikes: mapping.excluded?.tokens?.length ?? 0,
      byTag: countBy(mapping.labels, (r) => r.tag),
      byClass: countBy(mapping.labels, (r) => r.class)
    },
    scope: {
      dictionariesScanned: sources.length,
      dictionariesWithLabels: dictionariesWithLabels.size,
      totalEntries,
      totalInstances,
      entriesWithLabel: totalEntriesWithLabel,
      pctEntriesWithLabel: totalEntries > 0 ? Number(((totalEntriesWithLabel / totalEntries) * 100).toFixed(4)) : 0,
      instancesPer1000Entries: totalEntries > 0 ? Number(((totalInstances / totalEntries) * 1000).toFixed(4)) : 0
    },
    categories: dictionaries,
    perDictionary,
    diagnostics
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function countBy(rows, fn) {
  const out = {};
  for (const r of rows) {
    const k = fn(r);
    out[k] = (out[k] || 0) + 1;
  }
  return out;
}

function readUpstreamCommit() {
  try {
    return execSync("git rev-parse HEAD", { cwd: CSLORIG_ROOT, encoding: "utf8" }).trim();
  } catch {
    return "unknown";
  }
}

function readSources() {
  const codes = discoverDictionaries();
  return codes.map((code) => ({ code, text: fs.readFileSync(path.join(CSLORIG_ROOT, code, `${code}.txt`), "utf8") }));
}

function writeSourceEnvelope(payload) {
  const envelope = {
    dataset: "usage_register_census",
    commit: gitHead(),
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    upstreamCommit: payload.sourceCommit,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function gitHead() {
  try {
    return execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {
    return "unknown";
  }
}

function main() {
  const mapping = loadMapping();
  const sources = readSources();
  const payload = buildCensus(sources, mapping);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(
    `Wrote usage/register census (${payload.scope.dictionariesScanned} dicts, ` +
      `${payload.scope.totalInstances.toLocaleString()} label instances over ` +
      `${payload.scope.totalEntries.toLocaleString()} entries):`
  );
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  for (const cat of payload.categories.slice(0, 8)) {
    console.log(`  ${cat.category.padEnd(20)} ${String(cat.instances).padStart(7)} instances (${(cat.shareOfInstances * 100).toFixed(1)}%)`);
  }
  const withLabels = payload.perDictionary.filter((d) => d.instances > 0).length;
  console.log(`  dictionaries with at least one mapped label: ${withLabels}/${payload.scope.dictionariesScanned}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();