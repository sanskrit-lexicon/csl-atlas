// Build broad headword coverage for every eligible local Sanskrit/BHS dictionary.
//
// This is intentionally a headword-presence layer only. It does not expand the
// core 7-dictionary deep comparison model for gender, citations, homonyms,
// sense depth, or divergence.

import fs from "node:fs";
import path from "node:path";

import { generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { iterateHeadwords } from "./lib/dict-headwords.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import {
  BROAD_HEADWORD_SHARD_PREFIXES,
  buildBroadHeadwordDictionaries,
  excludedBroadHeadwordDictionaries,
  shardIdForLemma,
  shardPrefixForId
} from "./lib/dict-scope.mjs";
import { CSL_ORIG_GITHUB_BASE } from "./lib/source-links.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts", "broad-headword");
const SHARD_DIR = path.join(OUT_DIR, "shards");
const MANIFEST_PATH = path.join(OUT_DIR, "manifest.json");
const SAMPLE_LEMMAS = ["agni", "Siva", "aMSa", "akza", "dA"];

function ensureCleanOutput() {
  fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(SHARD_DIR, { recursive: true });
}

function writeJson(file, value, space = 0) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, space)}\n`);
}

function emptyCountObject(dictionaries) {
  return Object.fromEntries(dictionaries.map(dict => [dict.code, 0]));
}

function shardIds() {
  return [...BROAD_HEADWORD_SHARD_PREFIXES.map(prefix => prefix.charCodeAt(0).toString(16)), "other"];
}

function localOnlyWarning(dictionaries) {
  const localOnly = dictionaries.filter(dict => dict.sourceLinkMode !== "github").map(dict => dict.label);
  return localOnly.length
    ? [`${localOnly.length} dictionaries are local-only or not linkable from GitHub: ${localOnly.join(", ")}.`]
    : [];
}

function zeroRecordWarning(dictionaries, recordsByDict) {
  const zeroRecord = dictionaries.filter(dict => recordsByDict[dict.code] === 0).map(dict => dict.label);
  return zeroRecord.length
    ? [`${zeroRecord.length} eligible local dictionaries produced no parsed headword records with the current adapters: ${zeroRecord.join(", ")}.`]
    : [];
}

function serializeEntry([lemma, byDict]) {
  return [
    lemma,
    [...byDict.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([dictIndex, value]) => [dictIndex, value.records, value.firstLine])
  ];
}

function build() {
  const dictionaries = buildBroadHeadwordDictionaries();
  const excluded = excludedBroadHeadwordDictionaries();
  const recordsByDict = emptyCountObject(dictionaries);
  const lemmasByDict = emptyCountObject(dictionaries);
  const index = new Map();
  const previousManifest = readJsonIfExists(MANIFEST_PATH, fs);

  console.log(`Building broad headword coverage for ${dictionaries.length} dictionaries...`);
  for (const [dictIndex, dict] of dictionaries.entries()) {
    let records = 0;
    for (const record of iterateHeadwords(dict)) {
      if (!record.k1) continue;
      const lemma = normalizeLemma(record.k1).normalized;
      if (!lemma) continue;
      records++;
      let byDict = index.get(lemma);
      if (!byDict) {
        byDict = new Map();
        index.set(lemma, byDict);
      }
      const existing = byDict.get(dictIndex);
      if (existing) {
        existing.records += 1;
      } else {
        byDict.set(dictIndex, { records: 1, firstLine: record.startLine });
        lemmasByDict[dict.code] += 1;
      }
    }
    recordsByDict[dict.code] = records;
    console.log(`  ${dict.label}: ${lemmasByDict[dict.code].toLocaleString()} lemmas, ${records.toLocaleString()} records`);
  }

  ensureCleanOutput();

  const shards = new Map(shardIds().map(id => [id, []]));
  const sortedEntries = [...index.entries()]
    .sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0)
    .map(serializeEntry);

  for (const entry of sortedEntries) {
    const id = shardIdForLemma(entry[0]);
    shards.get(id).push(entry);
  }

  const sampleEntries = SAMPLE_LEMMAS
    .map(lemma => index.has(lemma) ? serializeEntry([lemma, index.get(lemma)]) : null)
    .filter(Boolean);
  if (!sampleEntries.length) sampleEntries.push(...sortedEntries.slice(0, 5));

  const shardSummary = [];
  for (const [id, entries] of shards.entries()) {
    const payload = {
      schemaVersion: "1.0.0",
      scope: "broadHeadword",
      shard: id,
      prefix: shardPrefixForId(id),
      count: entries.length,
      tupleFields: ["lemma", "dicts"],
      dictTupleFields: ["dictIndex", "records", "firstLine"],
      entries
    };
    writeJson(path.join(SHARD_DIR, `${id}.json`), payload);
    shardSummary.push({ id, prefix: payload.prefix, path: `shards/${id}.json`, count: entries.length });
  }

  const manifestBase = {
    schemaVersion: "1.0.0",
    generatedBy: "npm run build-broad-headword-lookup",
    scope: "broadHeadword",
    sourceRoot: "../csl-orig/v02",
    hrefBase: CSL_ORIG_GITHUB_BASE,
    minDicts: 1,
    inputSchemes: ["IAST"],
    count: index.size,
    dictionaryCount: dictionaries.length,
    dictionaries,
    recordsByDict,
    lemmasByDict,
    shards: shardSummary,
    sampleLemmas: sampleEntries.map(entry => entry[0]),
    sampleEntries,
    tupleFields: ["lemma", "dicts"],
    dictTupleFields: ["dictIndex", "records", "firstLine"],
    assumptions: [
      "Broad mode indexes local Sanskrit/BHS headword dictionaries only.",
      "Reverse English-Sanskrit dictionaries are excluded from Sanskrit-headword lookup.",
      "This layer records headword presence, record count, and first source line only."
    ],
    warnings: [
      "Deep comparison remains limited to the core 7 dictionaries.",
      ...localOnlyWarning(dictionaries),
      ...zeroRecordWarning(dictionaries, recordsByDict)
    ],
    excluded
  };
  const { schemaVersion, ...manifestRest } = manifestBase;
  const manifest = {
    schemaVersion,
    generatedAt: generatedAtForPayload(previousManifest, manifestBase),
    ...manifestRest
  };
  writeJson(MANIFEST_PATH, manifest, 2);

  const recordTotal = Object.values(recordsByDict).reduce((sum, n) => sum + n, 0);
  console.log(`Wrote ${index.size.toLocaleString()} broad lemmas from ${recordTotal.toLocaleString()} records to ${OUT_DIR}`);
}

build();
