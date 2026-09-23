// Validate the usage/register label census (H5333).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - a category in the payload is outside the closed mapping vocabulary;
// - a counted label is not in the mapping, or its category disagrees with it;
// - a label that the mapping marks as an EXCLUDED look-alike was counted anyway
//   (the <ab>lit. / <ab>ep. / <ab>L. false positives this census exists to avoid);
// - per-dictionary instances do not reconcile between instances, byLabel and byCategory;
// - a rate does not recompute from counts / entries;
// - the global category table or the scope totals do not reconcile with the dictionaries.
//
// Usage: npm run validate-usage-register-census   (run after build-usage-register-census)

import fs from "node:fs";
import path from "node:path";
import { loadMapping, vocabularySet, assertMappingConsistent } from "./build-usage-register-census.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "usage_register_census.json");
const SOURCE_OUT = path.join(OUT_DIR, "usage_register_census.source.json");
const MAPPING_PATH = path.resolve(process.cwd(), "data", "lexico", "usage_register_mapping.json");

const errors = [];
const notes = [];
const RATE_TOL = 0.001;

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON ${path.relative(process.cwd(), file)}: ${e.message}`);
    return null;
  }
}

function near(a, b, tol = RATE_TOL) {
  return Math.abs(a - b) <= tol;
}

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);

if (packet) {
  let mapping = null;
  try {
    mapping = loadMapping(MAPPING_PATH);
    assertMappingConsistent(mapping);
  } catch (e) {
    errors.push(`mapping invalid: ${e.message}`);
  }
  const vocab = mapping ? vocabularySet(mapping) : new Set();
  const index = new Map((mapping?.labels ?? []).map((r) => [`${r.tag}\t${r.token}`, r]));
  const excluded = new Set((mapping?.excluded?.tokens ?? []).map((t) => `${t.tag}\t${t.token}`));

  // Scope + totals reconcile with the per-dictionary rows.
  const dictSumInstances = packet.perDictionary.reduce((a, d) => a + d.instances, 0);
  const dictSumEntries = packet.perDictionary.reduce((a, d) => a + d.entries, 0);
  const dictSumWithLabel = packet.perDictionary.reduce((a, d) => a + d.entriesWithLabel, 0);
  if (dictSumInstances !== packet.scope.totalInstances) {
    errors.push(`scope.totalInstances ${packet.scope.totalInstances} != per-dictionary sum ${dictSumInstances}`);
  }
  if (dictSumEntries !== packet.scope.totalEntries) {
    errors.push(`scope.totalEntries ${packet.scope.totalEntries} != per-dictionary sum ${dictSumEntries}`);
  }
  if (dictSumWithLabel !== packet.scope.entriesWithLabel) {
    errors.push(`scope.entriesWithLabel ${packet.scope.entriesWithLabel} != per-dictionary sum ${dictSumWithLabel}`);
  }
  if (packet.scope.dictionariesScanned !== packet.perDictionary.length) {
    errors.push(`scope.dictionariesScanned ${packet.scope.dictionariesScanned} != perDictionary ${packet.perDictionary.length}`);
  }
  const withLabels = packet.perDictionary.filter((d) => d.instances > 0).length;
  if (withLabels !== packet.scope.dictionariesWithLabels) {
    errors.push(`scope.dictionariesWithLabels ${packet.scope.dictionariesWithLabels} != counted ${withLabels}`);
  }
  if (packet.diagnostics.length !== packet.perDictionary.length - withLabels) {
    errors.push(`diagnostics ${packet.diagnostics.length} != zero-label dictionaries ${packet.perDictionary.length - withLabels}`);
  }

  // Per-dictionary reconciliation + closed-vocabulary + false-positive guard.
  for (const d of packet.perDictionary) {
    const sumLabels = d.byLabel.reduce((a, l) => a + l.instances, 0);
    const sumCats = d.byCategory.reduce((a, c) => a + c.instances, 0);
    if (sumLabels !== d.instances) errors.push(`${d.code}: byLabel instances ${sumLabels} != instances ${d.instances}`);
    if (sumCats !== d.instances) errors.push(`${d.code}: byCategory instances ${sumCats} != instances ${d.instances}`);
    if (d.entriesWithLabel > d.entries) errors.push(`${d.code}: entriesWithLabel ${d.entriesWithLabel} > entries ${d.entries}`);
    if (d.entries > 0 && !near(d.instancesPer1000Entries, (d.instances / d.entries) * 1000)) {
      errors.push(`${d.code}: instancesPer1000Entries ${d.instancesPer1000Entries} does not recompute from ${d.instances}/${d.entries}`);
    }
    if (d.entries > 0 && !near(d.pctEntriesWithLabel, (d.entriesWithLabel / d.entries) * 100, RATE_TOL)) {
      errors.push(`${d.code}: pctEntriesWithLabel ${d.pctEntriesWithLabel} does not recompute from ${d.entriesWithLabel}/${d.entries}`);
    }
    for (const l of d.byLabel) {
      const key = `${l.tag}\t${l.token}`;
      if (excluded.has(key)) errors.push(`${d.code}: counted an excluded look-alike label ${JSON.stringify(key)}`);
      if (!vocab.has(l.category)) errors.push(`${d.code}: category "${l.category}" outside the vocabulary (${key})`);
      const row = index.get(key);
      if (!row) errors.push(`${d.code}: label ${JSON.stringify(key)} is not in the mapping`);
      else if (row.category !== l.category) errors.push(`${d.code}: ${key} category "${l.category}" != mapping "${row.category}"`);
    }
    for (const c of d.byCategory) {
      if (!vocab.has(c.category)) errors.push(`${d.code}: byCategory "${c.category}" outside the vocabulary`);
      if (c.entries > d.entries) errors.push(`${d.code}: category ${c.category} entries ${c.entries} > dictionary entries ${d.entries}`);
      if (d.instances > 0 && !near(c.shareOfInstances, c.instances / d.instances, RATE_TOL)) {
        errors.push(`${d.code}: category ${c.category} share ${c.shareOfInstances} != ${c.instances}/${d.instances}`);
      }
    }
  }

  // Global category table reconciles with the per-dictionary category rows.
  const global = new Map();
  for (const d of packet.perDictionary) {
    for (const c of d.byCategory) {
      const g = global.get(c.category) || { instances: 0, entries: 0, class: c.class };
      g.instances += c.instances;
      g.entries += c.entries;
      global.set(c.category, g);
    }
  }
  for (const c of packet.categories) {
    const g = global.get(c.category);
    if (!g) errors.push(`categories[] "${c.category}" not present in any dictionary row`);
    else {
      if (g.instances !== c.instances) errors.push(`categories[] ${c.category} instances ${c.instances} != summed ${g.instances}`);
      if (g.entries !== c.entries) errors.push(`categories[] ${c.category} entries ${c.entries} != summed ${g.entries}`);
      if (g.class !== c.class) errors.push(`categories[] ${c.category} class "${c.class}" != summed "${g.class}"`);
    }
    if (!vocab.has(c.category)) errors.push(`categories[] "${c.category}" outside the vocabulary`);
    if (packet.scope.totalInstances > 0 && !near(c.shareOfInstances, c.instances / packet.scope.totalInstances, RATE_TOL)) {
      errors.push(`categories[] ${c.category} share ${c.shareOfInstances} != ${c.instances}/${packet.scope.totalInstances}`);
    }
  }

  notes.push(
    `${packet.scope.dictionariesScanned} dicts, ${packet.scope.totalInstances.toLocaleString()} instances over ` +
      `${packet.scope.totalEntries.toLocaleString()} entries (${packet.scope.instancesPer1000Entries}/1000), ` +
      `${packet.categories.length} categories in use, ${packet.scope.dictionariesWithLabels} dictionaries with labels`
  );
}

if (envelope && packet && envelope.generatedAt !== packet.generatedAt) {
  errors.push("source envelope generatedAt does not match packet generatedAt");
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length) {
  console.error(`validate-usage-register-census: ${errors.length} error(s):`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log("validate-usage-register-census: OK");