// Copy generated top-level data artifacts into Observable's src root.
//
// Observable Framework only packages FileAttachment paths under `src/`. Some
// atlas generators intentionally keep canonical research artifacts under
// top-level `data/`; this script creates the site-facing copies before build.

import fs from "node:fs";
import path from "node:path";

import { BROAD_HEADWORD_SHARD_PREFIXES, shardIdForLemma, shardPrefixForId } from "./lib/dict-scope.mjs";

const COPIES = [
  {
    source: "data/dcs/dcs_lemma_summary.json",
    target: "src/data/dcs/dcs_lemma_summary.json",
    optionalFallback: JSON.stringify({ lemmas: {} }, null, 2) + "\n",
    dcsSummaryShardTarget: "src/data/dcs/lemma-summary"
  },
  {
    source: "data/lexico/sense_divergence.json",
    target: "src/data/lexico/sense_divergence.json"
  },
  {
    source: "data/lexico/h4_semantic_field_review_packet.json",
    target: "src/data/lexico/h4_semantic_field_review_packet.json"
  },
  {
    source: "data/lexico/heap_sat.json",
    target: "src/data/lexico/heap_sat.json"
  },
  {
    source: "data/lexico/period_signatures.json",
    target: "src/data/lexico/period_signatures.json"
  },
  {
    source: "data/lexico/ortho_drift.json",
    target: "src/data/lexico/ortho_drift.json"
  }
];

function readIfExists(file) {
  try {
    return fs.readFileSync(file);
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

function writeIfChanged(target, content) {
  const current = readIfExists(target);
  if (current && Buffer.compare(current, content) === 0) return false;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content);
  return true;
}

function writeJsonIfChanged(target, value) {
  return writeIfChanged(target, Buffer.from(`${JSON.stringify(value)}\n`));
}

function shardIds() {
  return [...BROAD_HEADWORD_SHARD_PREFIXES.map(prefix => prefix.charCodeAt(0).toString(16)), "other"];
}

function compareLemma(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

function syncDcsSummaryShards(content, targetDir) {
  const payload = JSON.parse(content.toString("utf8"));
  const lemmas = payload?.lemmas && typeof payload.lemmas === "object" ? payload.lemmas : {};
  const shardDir = path.join(targetDir, "shards");
  fs.mkdirSync(shardDir, { recursive: true });

  const shards = new Map(shardIds().map(id => [id, []]));
  for (const lemma of Object.keys(lemmas).sort(compareLemma)) {
    shards.get(shardIdForLemma(lemma)).push([lemma, lemmas[lemma]]);
  }

  let changed = 0;
  const shardSummary = [];
  for (const [id, entries] of shards.entries()) {
    const shardPayload = {
      schemaVersion: payload.schemaVersion ?? "1.0.0",
      scope: "dcsLemmaSummary",
      shard: id,
      prefix: shardPrefixForId(id),
      count: entries.length,
      tupleFields: ["lemma", "summary"],
      entries
    };
    if (writeJsonIfChanged(path.join(shardDir, `${id}.json`), shardPayload)) changed++;
    shardSummary.push({ id, prefix: shardPayload.prefix, path: `shards/${id}.json`, count: entries.length });
  }

  const manifest = {
    schemaVersion: payload.schemaVersion ?? "1.0.0",
    generatedBy: payload.generatedBy ?? "VisualDCS",
    scope: "dcsLemmaSummary",
    generatedAt: payload.generatedAt,
    corpusRelease: payload.corpusRelease,
    source: "data/dcs/dcs_lemma_summary.json",
    count: payload.lemmaCount ?? Object.keys(lemmas).length,
    tupleFields: ["lemma", "summary"],
    shards: shardSummary,
    warnings: ["DCS chips load only the shards needed for displayed dossier lemmas."]
  };
  if (writeJsonIfChanged(path.join(targetDir, "manifest.json"), manifest)) changed++;
  return changed;
}

let changed = 0;

for (const entry of COPIES) {
  const source = path.resolve(entry.source);
  const target = path.resolve(entry.target);
  const sourceContent = readIfExists(source);
  const content = sourceContent ?? (entry.optionalFallback !== undefined ? Buffer.from(entry.optionalFallback) : null);

  if (!content) {
    throw new Error(`Required site data missing: ${entry.source}`);
  }
  if (!sourceContent) console.warn(`Optional site data missing: ${entry.source}; wrote empty fallback.`);

  if (writeIfChanged(target, content)) changed++;
  if (entry.dcsSummaryShardTarget) changed += syncDcsSummaryShards(content, path.resolve(entry.dcsSummaryShardTarget));
}

console.log(`Synced site data (${changed} file${changed === 1 ? "" : "s"} changed).`);
