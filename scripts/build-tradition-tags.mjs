// Build the tradition-community packet for A50 §4 (agenda backlog #9).
//
// H305 (PH1 CANON-CORE) found the dict×text citation matrix significantly
// MODULAR, not nested — the dictionaries carry partly disjoint tradition
// communities. A50 §4 asserts "separate citation communities" but had no
// human-reviewed map NAMING them. This builder joins the small curated
// text→tradition overlay (data/citations/tradition_tags.tsv, ~120 texts) onto
// the committed <ls> citation edges and derives, per dictionary, how its cited
// volume splits across traditions — the evidence that turns the machine verdict
// into a named-community reading.
//
// The map is INFERRED until a human votes (evidenceLabel: inferred). The page
// and A50 flag every tradition claim by the tags' review state; unreviewed tags
// are never shown as fact. When reviewers flip `reviewed` to yes in the TSV and
// this is rebuilt, reviewStatus rises to human-reviewed automatically.
//
// Pure derivation from one committed TSV + the committed citation edges; no
// source/corpus read. Deterministic (generatedAtForPayload idiom).
//
// Usage: npm run build-tradition-tags   (then npm run validate-tradition-tags)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-tradition-tags";
const EDGES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_edges.tsv");
const NODES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_nodes.tsv");
const TAGS_PATH = path.resolve(process.cwd(), "data", "citations", "tradition_tags.tsv");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "citations");
const JSON_OUT = path.join(OUT_DIR, "tradition_tags.json");
const SOURCE_OUT = path.join(OUT_DIR, "tradition_tags.source.json");

// Closed tradition vocabulary (proposal set). The reviewer may reclassify a text
// to any of these; jain/tantra are legitimate options even if no seed row uses
// them yet. Kept in sync with data/citations/tradition_tags.tsv + the review
// sheet generator (scripts/build-tradition-review-sheet.mjs).
export const TRADITION_VOCAB = [
  "vedic",
  "epic",
  "purana",
  "classical-kavya",
  "poetics-sastra",
  "grammar-sastra",
  "dharma-sastra",
  "lexical-kosa",
  "medical",
  "jyotisa",
  "darsana",
  "buddhist",
  "jain",
  "tantra",
  "other"
];

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

export function parseTsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

// Join the tag map onto the citation edges → per-dict tradition splits.
export function buildPayload(edgeRows, nodeRows, tagRows, generatedAt) {
  const nodeByText = new Map();
  for (const r of nodeRows) {
    nodeByText.set(r.canonical_text, {
      total: Number(r.total_cites) || 0,
      nDicts: Number(r.n_dicts) || 0,
      variants: r.variant_forms || ""
    });
  }

  // Validate + index the tag map.
  const tagByText = new Map();
  const badTradition = [];
  for (const r of tagRows) {
    const text = r.canonical_text;
    const tradition = (r.tradition || "").trim();
    if (!TRADITION_VOCAB.includes(tradition)) badTradition.push({ text, tradition });
    tagByText.set(text, {
      tradition,
      confidence: (r.confidence || "").trim() || "low",
      reviewed: /^(yes|y|true|1)$/i.test((r.reviewed || "").trim()),
      note: (r.note || "").trim()
    });
  }
  if (badTradition.length) {
    throw new Error(
      `tradition_tags.tsv has ${badTradition.length} row(s) with a tradition outside the closed vocabulary: ` +
        badTradition.map((b) => `${b.text}→"${b.tradition}"`).join(", ")
    );
  }

  // Per-(dict, text) weights from the edges; per-dict total in-graph volume.
  const dictSet = new Set();
  const weight = new Map(); // `${dict}\t${text}` -> count
  const dictTotalAll = new Map(); // dict -> total in-graph cites (all texts)
  for (const e of edgeRows) {
    const dict = e.dict;
    const text = e.canonical_text;
    const count = Number(e.count) || 0;
    if (!dict || !text) continue;
    dictSet.add(dict);
    weight.set(`${dict}\t${text}`, (weight.get(`${dict}\t${text}`) || 0) + count);
    dictTotalAll.set(dict, (dictTotalAll.get(dict) || 0) + count);
  }
  const dicts = [...dictSet].sort();

  // Tagged-texts view (sorted by total cites desc).
  const taggedTexts = [...tagByText.entries()]
    .map(([text, tag]) => {
      const node = nodeByText.get(text);
      return {
        text,
        tradition: tag.tradition,
        confidence: tag.confidence,
        reviewed: tag.reviewed,
        note: tag.note,
        totalCites: node ? node.total : 0,
        nDicts: node ? node.nDicts : 0
      };
    })
    .sort((a, b) => b.totalCites - a.totalCites || (a.text < b.text ? -1 : 1));

  // Per-dict tradition split over the tagged texts it cites.
  const perDict = dicts.map((dict) => {
    const byTradition = new Map(); // tradition -> {cites, texts:Set}
    let taggedCites = 0;
    for (const [text, tag] of tagByText.entries()) {
      const c = weight.get(`${dict}\t${text}`) || 0;
      if (c === 0) continue;
      taggedCites += c;
      const rec = byTradition.get(tag.tradition) || { cites: 0, texts: 0 };
      rec.cites += c;
      rec.texts += 1;
      byTradition.set(tag.tradition, rec);
    }
    const splits = [...byTradition.entries()]
      .map(([tradition, rec]) => ({
        tradition,
        cites: rec.cites,
        texts: rec.texts,
        share: taggedCites > 0 ? round(rec.cites / taggedCites, 4) : 0
      }))
      .sort((a, b) => b.cites - a.cites || (a.tradition < b.tradition ? -1 : 1));
    const totalAll = dictTotalAll.get(dict) || 0;
    return {
      dict,
      taggedCites,
      totalInGraphCites: totalAll,
      taggedCoverage: totalAll > 0 ? round(taggedCites / totalAll, 4) : 0,
      dominantTradition: splits.length ? splits[0].tradition : null,
      byTradition: splits
    };
  });

  // Overall tradition totals across all dicts (over tagged texts).
  const traditionTotals = new Map();
  for (const d of perDict) {
    for (const s of d.byTradition) {
      const rec = traditionTotals.get(s.tradition) || { cites: 0, textSet: new Set() };
      rec.cites += s.cites;
      traditionTotals.set(s.tradition, rec);
    }
  }
  for (const t of taggedTexts) {
    const rec = traditionTotals.get(t.tradition) || { cites: 0, textSet: new Set() };
    rec.textSet.add(t.text);
    traditionTotals.set(t.tradition, rec);
  }
  const allTaggedCites = perDict.reduce((a, d) => a + d.taggedCites, 0);
  const traditions = TRADITION_VOCAB.filter((tr) => traditionTotals.has(tr)).map((tr) => {
    const rec = traditionTotals.get(tr);
    return {
      tradition: tr,
      texts: taggedTexts.filter((t) => t.tradition === tr).length,
      cites: rec.cites,
      share: allTaggedCites > 0 ? round(rec.cites / allTaggedCites, 4) : 0
    };
  }).sort((a, b) => b.cites - a.cites);

  // Review-state summary.
  const reviewedCount = taggedTexts.filter((t) => t.reviewed).length;
  const byConfidence = { high: 0, medium: 0, low: 0 };
  for (const t of taggedTexts) byConfidence[t.confidence] = (byConfidence[t.confidence] || 0) + 1;
  const allReviewed = reviewedCount === taggedTexts.length && taggedTexts.length > 0;

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    status: "tradition-community-map",
    claim:
      "Each Cologne Sanskrit dictionary's <ls> citation volume splits across a small set of textual traditions (Vedic, epic, classical-kāvya, Buddhist, dharma-śāstra, lexical-kośa, …); the per-dictionary split names the modular citation communities PH1 CANON-CORE detected quantitatively.",
    evidenceLabel: "inferred",
    reviewStatus: allReviewed ? "human-reviewed" : "inferred-pending-review",
    reviewNote:
      "The text→tradition map is a scholarly proposal routed to human review (agenda backlog #9). Every tradition claim on the page is flagged by review state; unreviewed tags are shown as inferred, never asserted as fact.",
    ownerRepo: "csl-atlas",
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "data/citations/tradition_tags.tsv",
      "data/citations/ls_citation_edges.tsv",
      "data/citations/ls_citation_nodes.tsv",
      "scripts/build-tradition-tags.mjs"
    ],
    method:
      "Join the curated text→tradition overlay onto the committed <ls> citation edges; per dictionary, sum citation volume by tradition over the tagged texts it cites and report the share, the dominant tradition, and what fraction of the dictionary's in-graph citation volume the tagged texts cover.",
    vocabulary: TRADITION_VOCAB,
    reviewState: {
      taggedTexts: taggedTexts.length,
      reviewed: reviewedCount,
      pctReviewed: round(taggedTexts.length ? reviewedCount / taggedTexts.length : 0, 4),
      byConfidence,
      allReviewed
    },
    coverage: {
      nDicts: dicts.length,
      taggedTexts: taggedTexts.length,
      taggedCites: allTaggedCites,
      note:
        "Shares are over the ~120 tagged texts (the modular signal: shared head + each dict's heaviest sources), not the full 912-text graph; per-dict taggedCoverage reports the covered fraction. Prose/iti citations (VCP, SKD, WIL) and MW's filtered grammatical markers are out of the <ls> graph entirely (see A50 §5)."
    },
    traditions,
    perDict,
    taggedTexts
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  let commit = "unknown";
  try {
    commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {
    commit = "unknown";
  }
  const envelope = {
    dataset: "tradition_tags",
    commit,
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  const edgeRows = parseTsv(fs.readFileSync(EDGES_PATH, "utf8"));
  const nodeRows = parseTsv(fs.readFileSync(NODES_PATH, "utf8"));
  const tagRows = parseTsv(fs.readFileSync(TAGS_PATH, "utf8"));
  const payload = buildPayload(edgeRows, nodeRows, tagRows);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(
    `Wrote tradition-community packet (${payload.reviewState.taggedTexts} tagged texts across ${payload.coverage.nDicts} dicts, ${payload.traditions.length} traditions in use):`
  );
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(`  review status: ${payload.reviewStatus} (${payload.reviewState.reviewed}/${payload.reviewState.taggedTexts} reviewed)`);
  for (const t of payload.traditions.slice(0, 6)) {
    console.log(`  ${t.tradition.padEnd(16)} ${t.texts} texts, ${t.cites.toLocaleString()} cites (${(t.share * 100).toFixed(1)}%)`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
