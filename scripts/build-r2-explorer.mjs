// Restore the R2 sense-alignment explorer package from local csl-orig.
//
// Reproduces the archived /tools/r2-explorer payload (5 anchor lemmas) from
// source, plus full per-dict sense files. It REUSES the documented split
// heuristics exported by build-r2-source-anchors.mjs — it does NOT change any
// parser rule (the five R2 packet decisions remain deferred to checkpoint
// review). Archive parity is a regression signal; drift is documented, not
// optimized away (see R2_REBUILD_CONTRACT.md).
//
// Outputs (data/lexico/):
//   senses_<dict>.jsonl   one sense-unit record per anchor-lemma sense, per dict
//   r2_align_<lemma>.json  archived-shape {senses, alignments} per anchor lemma
//   r2_summary.json        coverage + archive-drift summary
//
// Usage: npm run build-r2-explorer

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { dictExists } from "./lib/dict-parser.mjs";
import {
  R2_ANCHOR_LEMMAS,
  R2_DICTS,
  buildNormalRows,
  buildReverseRows,
  jaccard
} from "./build-r2-source-anchors.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const ARCHIVE_EXPLORER = path.join(OUT_DIR, "r2_archive_explorer.json");
const SUMMARY_OUT = path.join(OUT_DIR, "r2_summary.json");
const TEXT_MAX = 150; // archived spans run ~150 chars

function localIdOf(row) {
  // prototype senseId === `${blockId}:${localId}`; archived `sense` is the localId
  const id = String(row.senseId ?? "");
  const idx = id.lastIndexOf(":");
  return idx >= 0 ? id.slice(idx + 1) : id;
}

function clip(text, max = TEXT_MAX) {
  if (!text) return "";
  return text.length > max ? `${text.slice(0, max - 1)}...` : text;
}

function alignmentAnchors(row) {
  return [
    ...(row.sanskritAnchors ?? []).map(v => `s:${v}`),
    ...(row.citationAnchors ?? [])
  ];
}

function strongShared(shared) {
  return shared.filter(v =>
    v.startsWith("ls:") || v.startsWith("sig:") || v.replace(/^s:/, "").length >= 4
  );
}

// Build {senses, alignments} for one lemma in the archived explorer shape.
export function buildLemmaPayload(lemmaRows) {
  const senses = {};
  for (const row of lemmaRows) {
    const dict = row.dict;
    (senses[dict] ??= []).push({
      sense: localIdOf(row),
      text: clip(row.text),
      cluster: row.parserFamily, // archived "cluster" == parser family/cluster
      n_anchor: (row.sanskritAnchors ?? []).length
    });
  }

  const alignments = [];
  for (let i = 0; i < lemmaRows.length; i++) {
    const left = lemmaRows[i];
    const la = alignmentAnchors(left);
    if (!la.length) continue;
    for (let j = i + 1; j < lemmaRows.length; j++) {
      const right = lemmaRows[j];
      if (left.dict === right.dict) continue;
      const ra = alignmentAnchors(right);
      if (!ra.length) continue;
      const shared = [...new Set(la.filter(v => ra.includes(v)))].sort();
      const strong = strongShared(shared);
      if (!strong.length) continue;
      const score = jaccard(la, ra);
      if (score < 0.02 && strong.length < 2) continue;
      alignments.push({
        a: `${left.dict}#${localIdOf(left)}`,
        b: `${right.dict}#${localIdOf(right)}`,
        j: Number(score.toFixed(3)),
        shared: shared.slice(0, 24),
        cross: left.parserFamily !== right.parserFamily
      });
    }
  }
  alignments.sort((a, b) =>
    b.j - a.j || Number(b.cross) - Number(a.cross) || a.a.localeCompare(b.a) || a.b.localeCompare(b.b)
  );
  return { senses, alignments };
}

function rowsForLemma(target) {
  const rows = [];
  for (const dict of R2_DICTS) {
    if (!dictExists(dict.code)) continue;
    const { rows: r } = dict.split === "reverse-equivalent"
      ? buildReverseRows(target, dict)
      : buildNormalRows(target, dict);
    rows.push(...r);
  }
  return rows;
}

function archiveCounts() {
  if (!fs.existsSync(ARCHIVE_EXPLORER)) return null;
  const a = JSON.parse(fs.readFileSync(ARCHIVE_EXPLORER, "utf8"));
  const out = { byLemma: {}, senseRows: 0, alignmentRows: 0 };
  for (const L of a.lemmas ?? []) {
    const senseCount = Object.values(L.senses ?? {}).reduce((s, r) => s + r.length, 0);
    out.byLemma[L.lemma] = { senses: senseCount, alignments: (L.alignments ?? []).length };
    out.senseRows += senseCount;
    out.alignmentRows += (L.alignments ?? []).length;
  }
  return out;
}

function writeJson(file, payload) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const archive = archiveCounts();
  const sensesByDict = new Map(); // dict -> jsonl rows
  const lemmaSummaries = [];
  let totalSenseRows = 0;
  let totalAlignmentRows = 0;

  for (const target of R2_ANCHOR_LEMMAS) {
    const rows = rowsForLemma(target);
    const payload = buildLemmaPayload(rows);

    // per-dict sense-unit jsonl rows (contract: senses_<dict>.jsonl)
    for (const row of rows) {
      if (!sensesByDict.has(row.dict)) sensesByDict.set(row.dict, []);
      sensesByDict.get(row.dict).push({
        dict: row.dict,
        lemma: target.lemma,
        rawHeadword: row.rawHeadword,
        blockIds: row.blockIds,
        senseId: row.senseId,
        parserFamily: row.parserFamily,
        splitConfidence: row.splitConfidence,
        text: clip(row.text),
        sanskritAnchors: row.sanskritAnchors,
        citationAnchors: row.citationAnchors,
        limitations: row.limitations
      });
    }

    const senseCount = Object.values(payload.senses).reduce((s, r) => s + r.length, 0);
    const alignCount = payload.alignments.length;
    totalSenseRows += senseCount;
    totalAlignmentRows += alignCount;

    writeJson(path.join(OUT_DIR, `r2_align_${target.lemma}.json`), {
      schemaVersion: "0.1.0",
      status: "source-backed-r2-explorer",
      claim: "R2 explorer payload regenerated from current csl-orig; archive parity is a comparison signal.",
      lemma: target.lemma,
      lookupKeys: target.lookupKeys,
      counts: {
        senseRows: senseCount,
        alignmentRows: alignCount,
        crossAlignmentRows: payload.alignments.filter(r => r.cross).length,
        archivedSenseRows: archive?.byLemma[target.lemma]?.senses ?? null,
        archivedAlignmentRows: archive?.byLemma[target.lemma]?.alignments ?? null
      },
      ...payload
    });

    lemmaSummaries.push({
      lemma: target.lemma,
      senseRows: senseCount,
      alignmentRows: alignCount,
      archivedSenseRows: archive?.byLemma[target.lemma]?.senses ?? null,
      archivedAlignmentRows: archive?.byLemma[target.lemma]?.alignments ?? null,
      dicts: Object.keys(payload.senses).sort()
    });
  }

  for (const [dict, rows] of [...sensesByDict].sort((a, b) => a[0].localeCompare(b[0]))) {
    fs.writeFileSync(
      path.join(OUT_DIR, `senses_${dict}.jsonl`),
      rows.map(r => JSON.stringify(r)).join("\n") + "\n"
    );
  }

  writeJson(SUMMARY_OUT, {
    schemaVersion: "0.1.0",
    status: "source-backed-r2-explorer",
    claim: "R2 explorer coverage rebuilt from current local csl-orig anchor rows.",
    sourceRoot: "../csl-orig/v02",
    generatedBy: "npm run build-r2-explorer",
    limitations: [
      "Restored explorer slice for the five anchor lemmas; h2h3 inheritance edges are a separate slice.",
      "Split heuristics are reused unchanged from build-r2-source-anchors.mjs; no parser rule is promoted.",
      "PWK (pw) is present in source but absent from the archived explorer; counts may drift accordingly.",
      "Archive parity is a regression signal, not an optimization target."
    ],
    counts: {
      lemmaCount: R2_ANCHOR_LEMMAS.length,
      senseRows: totalSenseRows,
      alignmentRows: totalAlignmentRows,
      archivedSenseRows: archive?.senseRows ?? null,
      archivedAlignmentRows: archive?.alignmentRows ?? null
    },
    lemmas: lemmaSummaries
  });

  console.log(`Wrote r2_align_<lemma>.json (${R2_ANCHOR_LEMMAS.length} lemmas)`);
  console.log(`Wrote senses_<dict>.jsonl (${sensesByDict.size} dicts)`);
  console.log(`Wrote ${path.relative(process.cwd(), SUMMARY_OUT)}`);
  console.log(`senseRows ${totalSenseRows} vs archived ${archive?.senseRows ?? "?"}; alignmentRows ${totalAlignmentRows} vs archived ${archive?.alignmentRows ?? "?"}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
