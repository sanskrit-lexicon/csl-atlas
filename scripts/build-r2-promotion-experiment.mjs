// Run the R2 parser-promotion experiment authorized by the reviewed checkpoint.
//
// Reads the human decisions in src/data/review/r2-checkpoint-review.json and,
// for the rows with parserDisposition "promote-parser-candidate", applies the
// accepted window rules to the current source-backed anchor rows. Rows outside
// the promoted window are retained as side evidence, never discarded. Rows
// with "retain-side-evidence" stay untouched; "control-only" rows are
// recomputed as regression controls.
//
// Archive parity remains a comparison signal, not the optimization target:
// this script reports how the promoted windows move the source/archive ratio
// but never tunes a rule to a count.
//
// Usage: npm run build-r2-promotion-experiment

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import {
  R2_ANCHOR_LEMMAS,
  R2_DICTS,
  buildNormalRows,
  buildReverseRows,
  splitRecord,
  indigenousAuthorityHints
} from "./build-r2-source-anchors.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const REVIEW_PATH = path.resolve(process.cwd(), "src", "data", "review", "r2-checkpoint-review.json");
const SUMMARY_PATH = path.join(OUT_DIR, "r2_source_anchor_summary.json");
const JSON_OUT = path.join(OUT_DIR, "r2_promotion_experiment.json");
const DOC_OUT = path.resolve(process.cwd(), "docs", "R2_PROMOTION_EXPERIMENT.md");

// Reviewed record roles for the div-source-scope packet. These are the
// record-level assignments recorded by the human reviewer in the checkpoint
// notes (reviewIds r2-drift:gam:pwg and r2-drift:dharma:pwg); the experiment
// applies them, it does not infer them.
export const DIV_SOURCE_RECORD_ROLES = Object.freeze({
  "r2-drift:gam:pwg": Object.freeze({
    21814: "target-primary-series",
    72578: "same-headword-supplement",
    119742: "same-headword-supplement",
    21815: "separate-homonym"
  }),
  "r2-drift:dharma:pwg": Object.freeze({
    36241: "target-primary-series",
    76490: "same-headword-supplement"
  })
});

function normalizeAnchor(token) {
  return normalizeLemma(token).normalized.replace(/^[-.]+|[-.]+$/g, "");
}

function dictConfig(code) {
  return R2_DICTS.find(dict => dict.code === code);
}

function anchorTarget(lemma) {
  return R2_ANCHOR_LEMMAS.find(row => row.lemma === lemma);
}

function ratio(rows, archive) {
  if (!archive) return null;
  return Number((rows / archive).toFixed(3));
}

/**
 * Classify one full-text iti-unit from SKD/VCP into the promoted
 * indigenous-iti-authority labels. Heuristic and intentionally transparent:
 * authority markers win, then long prose counts as commentarial discussion,
 * the remainder are definition units (the sense-like window).
 */
export function classifyItiUnit(text, dictCode) {
  const hints = indigenousAuthorityHints(text, dictCode);
  const hasQuotation = /\byaTA\b/.test(text) || /[“”]/.test(text);
  if (hints.length || hasQuotation) {
    return hints.length ? "authority-quotation-unit" : "authority-siglum-unit";
  }
  if (text.replace(/\s+/g, " ").length > 350) return "commentarial-discussion-unit";
  return "definition-iti-unit";
}

// PWG prints its own sense enumeration in the entry text ("— 1)", "— 2)" at
// <div n="1">, letters at n="2", Greek at n="3"); the <div n> attribute is a
// DEPTH marker, not a sense number. The promoted window therefore follows the
// print's enumeration: numbered top-level divisions of the target-primary
// record, before the first <div n="p"> preverb block.
const PWG_NUMBERED_SENSE = /^[—–-]?\s*\d+\)/;

/** Window for the PWG div-source-scope packet: the target-primary record's
 *  own numbered top-level senses. Subdivisions, preverb/derived blocks,
 *  supplements and homonyms are labeled, not dropped. Rows must be in
 *  record/source order (as emitted by buildNormalRows). */
export function divSourceWindow(rows, recordRoles, acceptedLabels) {
  const excludePreverbs = acceptedLabels.includes("prefixed-or-derived-series");
  const afterPreverbByRecord = new Map();
  return rows.map(row => {
    const recordId = Number(row.blockIds?.[0]);
    const role = recordRoles[recordId] ?? "unassigned";
    if (role !== "target-primary-series") {
      return { row, inWindow: false, windowLabel: role };
    }
    if (excludePreverbs && row.markerLabel === "p") {
      afterPreverbByRecord.set(recordId, true);
      return { row, inWindow: false, windowLabel: "prefixed-or-derived-series" };
    }
    if (excludePreverbs && afterPreverbByRecord.get(recordId)) {
      return { row, inWindow: false, windowLabel: "prefixed-or-derived-series" };
    }
    if (row.splitConfidence !== "explicit") {
      return { row, inWindow: false, windowLabel: "preface-or-proxy" };
    }
    if (row.markerLabel === "1" && PWG_NUMBERED_SENSE.test(row.text ?? "")) {
      return { row, inWindow: true, windowLabel: "target-primary-series" };
    }
    return { row, inWindow: false, windowLabel: "candidate-sense-marker" };
  });
}

// Benfey introduces a preverb (upasarga) section with "-- With <preverb>".
const BEN_PREVERB_CUE = /--\s*With\s+/;

/** Pure: given a record's split parts in order, return the first marker-run
 *  index that begins Benfey's preverb zone. The "-- With <preverb>" cue sits
 *  in the tail segment of the run preceding the first preverb section, so the
 *  zone begins at that run index + 1. Infinity when no preverb zone exists. */
export function benBoundaryFromParts(parts) {
  for (const part of parts) {
    if (BEN_PREVERB_CUE.test(part.text || "")) return (part.markerRunIndex ?? 0) + 1;
  }
  return Infinity;
}

/** Find the first preverb-zone marker-run for a Benfey lemma from source.
 *  Benfey nests, in one record: the bare finite root (run 0), its primary
 *  derivatives — participles and causative (runs 1..k) — and preverb-combined
 *  lexemes (runs k+1..). Reads untruncated source text. */
export function benPreverbBoundary(lemma, dictCode) {
  const target = anchorTarget(lemma);
  const dict = dictConfig(dictCode);
  const lookupKeySet = new Set(target.lookupKeys.map(normalizeAnchor));
  let boundary = Infinity;
  for (const rec of iterateDict(dictCode)) {
    if (!lookupKeySet.has(normalizeAnchor(rec.k1 || ""))) continue;
    boundary = Math.min(boundary, benBoundaryFromParts(splitRecord(rec.body || "", dict)));
  }
  return boundary;
}

/** Window for the BEN marker-run-scope packet. The lemma window is the bare
 *  finite root (marker run 0); primary derivatives and preverb-combined
 *  lexemes are separate lexical items, retained as labeled side evidence.
 *  `firstPreverbRun` separates derivative runs from preverb runs. */
export function markerRunWindow(rows, acceptedLabels, exactHeadword = null, firstPreverbRun = Infinity) {
  if (acceptedLabels.includes("source-record-exact-target") && exactHeadword !== null) {
    return rows.map(row =>
      row.rawHeadword === exactHeadword
        ? { row, inWindow: true, windowLabel: "target-run" }
        : { row, inWindow: false, windowLabel: "lookup-bundle-split" }
    );
  }
  if (acceptedLabels.includes("archive-prefix-runs")) {
    return rows.map(row => {
      if (row.splitConfidence !== "explicit") {
        return { row, inWindow: false, windowLabel: "preface-or-proxy" };
      }
      const runIndex = row.markerRunIndex ?? 0;
      if (runIndex === 0) return { row, inWindow: true, windowLabel: "bare-root-run" };
      if (runIndex >= firstPreverbRun) return { row, inWindow: false, windowLabel: "preverb-lexeme-run" };
      return { row, inWindow: false, windowLabel: "primary-derivative-run" };
    });
  }
  return rows.map(row => ({ row, inWindow: true, windowLabel: "target-run" }));
}

/** Window for the AE reverse-band packet (nominal lemmas only). */
export function aeReverseWindow(rows) {
  return rows.map(row => {
    const rank = row.reverseMatch?.rank ?? "no-match";
    const direct = row.reverseMatch?.firstGroupIndex === 0;
    if (rank === "high") {
      return { row, inWindow: true, windowLabel: direct ? "direct-equivalent-candidate" : "reverse-high-candidate" };
    }
    const label = rank === "medium"
      ? "reverse-medium-review"
      : rank === "low"
        ? "reverse-low-context"
        : "reverse-tail-overmatch";
    return { row, inWindow: false, windowLabel: label };
  });
}

function labelCounts(labeled) {
  const counts = {};
  for (const { windowLabel } of labeled) counts[windowLabel] = (counts[windowLabel] || 0) + 1;
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function loadReviewDecisions() {
  const report = JSON.parse(fs.readFileSync(REVIEW_PATH, "utf8"));
  const decisions = new Map();
  for (const item of report.items ?? []) {
    decisions.set(item.reviewId, {
      reviewId: item.reviewId,
      lemma: item.subject?.lemma,
      dict: (item.subject?.dictionaries?.[0] ?? "").toLowerCase(),
      packetId: item.machineValue?.packetId,
      reviewStatus: item.reviewStatus,
      disposition: item.reviewedValue?.parserDisposition ?? null,
      acceptedParserLabels: item.reviewedValue?.acceptedParserLabels ?? [],
      reviewer: item.reviewer,
      reviewedAt: item.reviewedAt
    });
  }
  return decisions;
}

function loadArchiveCounts() {
  const summary = JSON.parse(fs.readFileSync(SUMMARY_PATH, "utf8"));
  const counts = new Map();
  for (const lemma of summary.lemmas ?? []) {
    for (const byDict of lemma.byDict ?? []) {
      counts.set(`${lemma.lemma}:${byDict.dict}`, byDict.archivedSenseRows ?? 0);
    }
  }
  return counts;
}

function buildRowsFor(lemma, dictCode) {
  const target = anchorTarget(lemma);
  const dict = dictConfig(dictCode);
  if (!target || !dict) throw new Error(`Unknown lemma/dict pair: ${lemma}:${dictCode}`);
  return dict.split === "reverse-equivalent" ? buildReverseRows(target, dict) : buildNormalRows(target, dict);
}

/** Full-text iti-unit classification for one lemma/dict (SKD or VCP). */
export function classifyIndigenousUnits(lemma, dictCode) {
  const target = anchorTarget(lemma);
  const dict = dictConfig(dictCode);
  const lookupKeySet = new Set(target.lookupKeys.map(normalizeAnchor));
  const units = [];
  for (const rec of iterateDict(dictCode)) {
    if (!lookupKeySet.has(normalizeAnchor(rec.k1 || ""))) continue;
    for (const part of splitRecord(rec.body || "", dict)) {
      units.push({
        blockId: rec.L,
        rawHeadword: rec.k1,
        localId: part.localId,
        windowLabel: classifyItiUnit(part.text, dictCode),
        inWindow: classifyItiUnit(part.text, dictCode) === "definition-iti-unit"
      });
    }
  }
  return units;
}

function experimentRow(decision, archiveCounts, body) {
  const archived = archiveCounts.get(`${decision.lemma}:${decision.dict}`) ?? 0;
  return {
    reviewId: decision.reviewId,
    lemma: decision.lemma,
    dict: decision.dict,
    packetId: decision.packetId,
    parserDisposition: decision.disposition,
    acceptedParserLabels: decision.acceptedParserLabels,
    archivedSenseRows: archived,
    ...body,
    ratioBefore: ratio(body.sourceSenseRows, archived),
    ratioAfter: body.windowRows == null ? null : ratio(body.windowRows, archived)
  };
}

function runExperiment() {
  const decisions = loadReviewDecisions();
  const archiveCounts = loadArchiveCounts();
  const results = [];
  const warnings = [];

  for (const decision of decisions.values()) {
    if (decision.reviewStatus !== "reviewed-ok") {
      warnings.push(`${decision.reviewId} is not reviewed-ok; skipped.`);
      continue;
    }

    const { rows } = buildRowsFor(decision.lemma, decision.dict);

    if (decision.disposition === "retain-side-evidence") {
      results.push(experimentRow(decision, archiveCounts, {
        sourceSenseRows: rows.length,
        windowRows: null,
        sideEvidenceRows: rows.length,
        windowLabelCounts: null,
        outcome: "side-evidence-retained"
      }));
      continue;
    }

    if (decision.disposition === "control-only") {
      const archived = archiveCounts.get(`${decision.lemma}:${decision.dict}`) ?? 0;
      results.push(experimentRow(decision, archiveCounts, {
        sourceSenseRows: rows.length,
        windowRows: rows.length,
        sideEvidenceRows: 0,
        windowLabelCounts: null,
        outcome: rows.length === archived ? "parity-confirmed" : "parity-broken"
      }));
      if (rows.length !== archived) {
        warnings.push(`${decision.reviewId}: parity control broke (${rows.length} vs ${archived}).`);
      }
      continue;
    }

    if (decision.disposition !== "promote-parser-candidate") {
      warnings.push(`${decision.reviewId}: unhandled disposition ${decision.disposition}; skipped.`);
      continue;
    }

    let labeled;
    if (decision.packetId === "div-source-scope") {
      labeled = divSourceWindow(rows, DIV_SOURCE_RECORD_ROLES[decision.reviewId] ?? {}, decision.acceptedParserLabels);
    } else if (decision.packetId === "marker-run-scope") {
      const exact = decision.acceptedParserLabels.includes("source-record-exact-target") ? decision.lemma : null;
      const firstPreverbRun = decision.acceptedParserLabels.includes("archive-prefix-runs")
        ? benPreverbBoundary(decision.lemma, decision.dict)
        : Infinity;
      labeled = markerRunWindow(rows, decision.acceptedParserLabels, exact, firstPreverbRun);
    } else if (decision.packetId === "ae-reverse-bands") {
      labeled = aeReverseWindow(rows);
    } else if (decision.packetId === "indigenous-iti-authority") {
      labeled = classifyIndigenousUnits(decision.lemma, decision.dict).map(unit => ({
        row: unit,
        inWindow: unit.inWindow,
        windowLabel: unit.windowLabel
      }));
    } else {
      warnings.push(`${decision.reviewId}: no window rule for packet ${decision.packetId}; skipped.`);
      continue;
    }

    const windowRows = labeled.filter(item => item.inWindow).length;
    results.push(experimentRow(decision, archiveCounts, {
      sourceSenseRows: labeled.length,
      windowRows,
      sideEvidenceRows: labeled.length - windowRows,
      windowLabelCounts: labelCounts(labeled),
      outcome: "window-applied"
    }));
  }

  results.sort((a, b) => a.reviewId.localeCompare(b.reviewId));
  return { results, warnings };
}

function buildPayload(results, warnings) {
  return {
    schemaVersion: "1.0.0",
    status: "promotion-experiment",
    claim: "Reviewed checkpoint window rules applied to source-backed R2 anchor rows; non-window rows retained as labeled side evidence.",
    generatedAt: new Date().toISOString(),
    generatedBy: "npm run build-r2-promotion-experiment",
    sourcePath: "src/data/review/r2-checkpoint-review.json",
    inputs: [
      "src/data/review/r2-checkpoint-review.json",
      "data/lexico/r2_source_anchor_summary.json",
      "../csl-orig/v02 (anchor-lemma records)"
    ],
    archiveParityPolicy: "Archive parity is a comparison signal and regression-control cue; ratios are reported, never optimized.",
    assumptions: [
      "Only rows with reviewStatus reviewed-ok are processed; dispositions gate every rule.",
      "div-source-scope record roles come verbatim from the reviewed checkpoint notes (DIV_SOURCE_RECORD_ROLES).",
      "The PWG window follows the print's own sense enumeration: numbered top-level divisions (\"— N)\" at div n=\"1\") of the target-primary record before the first div n=\"p\" preverb block; <div n> depth values are never counted as senses.",
      "The Benfey (gam:ben) window is the bare finite root (marker run 0); primary derivatives (participles, causative — runs 1..k) and preverb-combined lexemes (introduced by \"-- With <preverb>\", runs k+1..) are separate lexical items, retained as labeled side evidence. The archived count (root + first participle) is itself an artifact, not the optimization target.",
      "Indigenous iti-unit classification is heuristic (authority hints/quotation markers, then >350-char prose as discussion) and is a labeling experiment, not a scholar-reviewed sense decision.",
      "AE windows apply to the reviewed nominal lemma only; verbal reverse rows remain side evidence per r2-drift:gam:ae.",
      "No existing R2 output (senses, H1, H2H3, explorer) is modified; this artifact is additive."
    ],
    warnings,
    counts: {
      checkpointRows: results.length,
      promoted: results.filter(row => row.parserDisposition === "promote-parser-candidate").length,
      sideEvidence: results.filter(row => row.parserDisposition === "retain-side-evidence").length,
      controls: results.filter(row => row.parserDisposition === "control-only").length
    },
    results
  };
}

function fmtRatio(value) {
  return value == null ? "—" : value.toFixed(3);
}

function buildDoc(payload) {
  const lines = [];
  lines.push("# R2 Parser-Promotion Experiment");
  lines.push("");
  lines.push(`Date: ${payload.generatedAt.slice(0, 10)}`);
  lines.push("");
  lines.push("Status: generated experiment report. This applies the reviewed checkpoint");
  lines.push("window rules to the source-backed anchor rows. It is not a splitter change,");
  lines.push("not a public R2 page update, and not a scholar-reviewed sense decision layer.");
  lines.push("");
  lines.push("## Trust Block");
  lines.push("");
  lines.push("- Claim: " + payload.claim);
  lines.push("- Evidence label: `derived` (window assignments from `reviewed` checkpoint decisions).");
  lines.push("- Generated by: `npm run build-r2-promotion-experiment`.");
  lines.push("- Source files: `src/data/review/r2-checkpoint-review.json`, `data/lexico/r2_source_anchor_summary.json`, local `../csl-orig/v02`.");
  lines.push("- Output: `data/lexico/r2_promotion_experiment.json`.");
  lines.push("- Archive parity policy: comparison/control signal only, never the optimization target.");
  lines.push("- Boundary note: dictionary source rows, existing R2 source anchors, and reviewed checkpoint decisions only.");
  lines.push("");
  lines.push("## Results");
  lines.push("");
  lines.push("| Row | Disposition | Source rows | Window rows | Archive | Ratio before | Ratio after | Outcome |");
  lines.push("|---|---|---:|---:|---:|---:|---:|---|");
  for (const row of payload.results) {
    lines.push(
      `| \`${row.reviewId}\` | ${row.parserDisposition} | ${row.sourceSenseRows} | ` +
      `${row.windowRows ?? "—"} | ${row.archivedSenseRows} | ${fmtRatio(row.ratioBefore)} | ` +
      `${fmtRatio(row.ratioAfter)} | ${row.outcome} |`
    );
  }
  lines.push("");
  lines.push("## Window label breakdowns");
  lines.push("");
  for (const row of payload.results) {
    if (!row.windowLabelCounts) continue;
    lines.push(`### \`${row.reviewId}\``);
    lines.push("");
    for (const [label, count] of Object.entries(row.windowLabelCounts)) {
      lines.push(`- \`${label}\`: ${count}`);
    }
    lines.push("");
  }
  lines.push("## Limitations");
  lines.push("");
  for (const assumption of payload.assumptions) lines.push(`- ${assumption}`);
  if (payload.warnings.length) {
    lines.push("");
    lines.push("## Warnings");
    lines.push("");
    for (const warning of payload.warnings) lines.push(`- ${warning}`);
  }
  lines.push("");
  return lines.join("\n");
}

function main() {
  const { results, warnings } = runExperiment();
  const payload = buildPayload(results, warnings);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  fs.writeFileSync(DOC_OUT, buildDoc(payload));
  console.log(`Wrote ${path.relative(process.cwd(), JSON_OUT)} (${results.length} checkpoint rows)`);
  console.log(`Wrote ${path.relative(process.cwd(), DOC_OUT)}`);
  for (const warning of warnings) console.warn(`warning: ${warning}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
