// Unit tests for decision-bearing helpers in the build orchestrators.
//
// The orchestrators read large source files in main(); they are guarded to run
// only when executed directly, so importing them here is side-effect-free and
// we can test their pure helpers with synthetic inputs.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { compareCounts } from "../scripts/build-mw-quantitative-depth.mjs";
import { senseUnits } from "../scripts/build-sense-depth.mjs";
import { indigenousAuthorityHints, jaccard, lookupKeysForLemma, reverseMatchProfile, sourceRecordCounts, splitExplicitMarkers } from "../scripts/build-r2-source-anchors.mjs";
import { classifyDrift, markerRunPrefixMatch, priorityForClass, sourceRecordExactMatches } from "../scripts/build-r2-parser-diagnostics.mjs";
import { packetIdForDiagnostic, scopeCluesForDiagnostic } from "../scripts/build-r2-review-packets.mjs";
import { CHECKPOINT_DIAGNOSTIC_IDS, buildPayload as buildR2LabelProposalPayload, labelsForPacket } from "../scripts/build-r2-label-proposals.mjs";
import { buildMarkdown as buildR2CheckpointMarkdown, buildPayload as buildR2CheckpointPayload } from "../scripts/build-r2-checkpoint-packet.mjs";
import { PARSER_DISPOSITIONS, applyPreservedDecisions as applyR2CheckpointPreserved, buildPayload as buildR2CheckpointReviewPayload } from "../scripts/build-r2-checkpoint-review.mjs";
import { buildMarkdown as buildR2DriftExplanationMarkdown, buildPayload as buildR2DriftExplanationPayload } from "../scripts/build-r2-drift-explanation.mjs";
import { parseCsv } from "../scripts/build-h5-anomaly-review.mjs";
import { buildMarkdown as buildH5MakerQaMarkdown, buildPayload as buildH5MakerQaPayload, preservedSourceCheckMap } from "../scripts/build-h5-maker-qa-candidates.mjs";
import { buildMarkdown as buildH5MakerCorrectionMarkdown, buildPayload as buildH5MakerCorrectionPayload, preservedCorrectionTargetMap } from "../scripts/build-h5-maker-correction-proposal.mjs";
import { EXPECTED_EDGE_IDS as THREE_AXIS_EDGE_IDS, axisReadingForScores, buildMarkdown as buildThreeAxisMarkdown, buildPayload as buildThreeAxisPayload } from "../scripts/build-three-axis-comparison.mjs";
import { EXPECTED_PREFIX_CONTROL_IDS as XREF_PREFIX_CONTROL_IDS, EXPECTED_SHARED_CORE_SAMPLE_IDS as XREF_SHARED_CORE_IDS, XREF_LABEL_VOCABULARY, buildMarkdown as buildXrefSourceCheckMarkdown, buildPayload as buildXrefSourceCheckPayload, preservedSourcePointerMap as preservedXrefSourcePointerMap } from "../scripts/build-xref-source-check-packet.mjs";
import { loadPreserved } from "../scripts/lib/review-report.mjs";
import { mean as h4Mean, rankFamilyFields, roundPct } from "../scripts/build-h4-family-profiles.mjs";
import { EXPECTED_H4_SAMPLE_COUNTS, H4_MACHINE_LABEL_VOCABULARY, buildMarkdown as buildH4ReviewPacketMarkdown, buildPayload as buildH4ReviewPacketPayload, preservedSourcePointerMap as preservedH4SourcePointerMap } from "../scripts/build-h4-review-packet.mjs";
import { edgeReviewClass, structuralDistance } from "../scripts/build-h6-structural-review.mjs";
import { classifyHubTarget, parseCsv as parseXrefCsv } from "../scripts/build-xref-hub-review.mjs";
import { classify, fitBand, median, percent } from "../scripts/build-dictionary-coverage.mjs";
import { topForm } from "../scripts/build-citation-apparatus.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const r2ReviewPackets = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_review_packets.json"), "utf8"));
const r2LabelProposals = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_packet_label_proposals.json"), "utf8"));
const r2CheckpointPacket = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_checkpoint_review_packet.json"), "utf8"));
const r2CheckpointReviewMd = fs.readFileSync(path.join(repoRoot, "docs", "R2_CHECKPOINT_REVIEW.md"), "utf8");
const r2CheckpointReviewReport = JSON.parse(fs.readFileSync(path.join(repoRoot, "src", "data", "review", "r2-checkpoint-review.json"), "utf8"));
const r2DriftExplanation = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_drift_explanation.json"), "utf8"));
const r2DriftExplanationMd = fs.readFileSync(path.join(repoRoot, "docs", "R2_DRIFT_EXPLANATION.md"), "utf8");
const r2DriftExplanationMachineOnlyMd = fs.readFileSync(path.join(repoRoot, "test", "fixtures", "R2_DRIFT_EXPLANATION.machine-only.md"), "utf8");
const h5AnomalyReviewReportPath = path.join(repoRoot, "src", "data", "review", "h5-anomaly-review.json");
const h5AnomalyReviewReport = JSON.parse(fs.readFileSync(h5AnomalyReviewReportPath, "utf8"));
const h5MakerQaCandidates = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "h5_maker_qa_candidates.json"), "utf8"));
const h5MakerQaCandidatesMd = fs.readFileSync(path.join(repoRoot, "docs", "H5_MAKER_QA_CANDIDATES.md"), "utf8");
const h5MakerCorrectionProposal = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "h5_maker_correction_proposal.json"), "utf8"));
const h5MakerCorrectionProposalMd = fs.readFileSync(path.join(repoRoot, "docs", "H5_MAKER_CORRECTION_PROPOSAL.md"), "utf8");
const threeAxisComparison = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "three_axis_comparison.json"), "utf8"));
const threeAxisComparisonMd = fs.readFileSync(path.join(repoRoot, "docs", "THREE_AXIS_COMPARISON.md"), "utf8");
const xrefHubReview = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "xref_hub_review.json"), "utf8"));
const xrefEdgeRows = parseXrefCsv(fs.readFileSync(path.join(repoRoot, "data", "lexico", "xref_edges.csv"), "utf8"));
const xrefSourceCheckPacket = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "xref_source_check_packet.json"), "utf8"));
const xrefSourceCheckMd = fs.readFileSync(path.join(repoRoot, "docs", "MICROSTRUCTURE_XREF_SOURCE_CHECK.md"), "utf8");
const h4SemanticFields = JSON.parse(fs.readFileSync(path.join(repoRoot, "src", "data", "dicts", "semantic-fields.json"), "utf8"));
const h4FamilyProfiles = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "semantic_field_family_profiles.json"), "utf8"));
const h4SemanticRows = parseCsv(fs.readFileSync(path.join(repoRoot, "data", "lexico", "semantic_fields.csv"), "utf8"));
const h4ReviewPacket = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "h4_semantic_field_review_packet.json"), "utf8"));
const h4ReviewPacketMd = fs.readFileSync(path.join(repoRoot, "docs", "H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md"), "utf8");
const threeAxisSourceInputs = {
  bootstrapRows: parseCsv(fs.readFileSync(path.join(repoRoot, "src", "data", "lexicographic-structure", "L0", "bootstrap_support.csv"), "utf8")),
  jaccardRows: parseCsv(fs.readFileSync(path.join(repoRoot, "src", "data", "lexicographic-structure", "sanhw1_jaccard.csv"), "utf8")),
  conventionRows: parseCsv(fs.readFileSync(path.join(repoRoot, "src", "data", "lexicographic-structure", "L0", "content_convention_scatter.csv"), "utf8")),
  structural: JSON.parse(fs.readFileSync(path.join(repoRoot, "src", "data", "dicts", "structural-register.json"), "utf8")),
  microstructure: JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "microstructure_fingerprint.json"), "utf8"))
};

const H5_REVIEW_LABELS = new Set([
  "legitimate-form",
  "variant-convention",
  "possible-typo",
  "ghost-candidate",
  "lineage-only",
  "parser-artifact"
]);

const H5_EXPECTED_CLASS_COUNTS = {
  "known-correction": 20,
  "mw-pw-shared-doublet": 30,
  "mw-pwg-shared-doublet": 30,
  "null-control": 20,
  "raw-headword-exclusive": 30
};

const H5_EXPECTED_REVIEWED_VALUE_COUNTS = {
  "legitimate-form": 58,
  "lineage-only": 15,
  "parser-artifact": 12,
  "possible-typo": 22,
  "variant-convention": 23
};

const H5_MAKER_QA_REVIEW_IDS = Object.freeze([
  "h5:mw-pw-shared-doublet:MW-PW:ajamI_a:ajamIQa",
  "h5:mw-pw-shared-doublet:MW-PW:awawyA:awAwyA",
  "h5:mw-pwg-shared-doublet:MW-PWG:akalkala:akalkana",
  "h5:mw-pwg-shared-doublet:MW-PWG:cApaqa:cApala",
  "h5:mw-pwg-shared-doublet:MW-PWG:uzmopagama:uzRopagama",
  "h5:mw-pw-shared-doublet:MW-PW:aprapAda:apramAda",
  "h5:mw-pw-shared-doublet:MW-PW:apraRASa:aprakASa",
  "h5:mw-pwg-shared-doublet:MW-PWG:divaraTa:devaraTa",
  "h5:mw-pwg-shared-doublet:MW-PWG:jalaDitA:jalaDigA",
  "h5:mw-pwg-shared-doublet:MW-PWG:kftAlaka:mftAlaka"
]);

function preservedReviewMap(report) {
  return new Map(report.items.map(item => [
    item.reviewId,
    {
      reviewStatus: item.reviewStatus,
      reviewedValue: item.reviewedValue,
      reviewer: item.reviewer,
      reviewedAt: item.reviewedAt,
      note: item.note
    }
  ]));
}

function normalizeLineEndings(text) {
  return text.replace(/\r\n/g, "\n");
}

function countBy(rows, keyFn) {
  const out = {};
  for (const row of rows) {
    const key = keyFn(row);
    out[key] = (out[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b)));
}

// ---- MW depth: count-divergence validation ----
test("compareCounts: no warnings when counts match", () => {
  const expected = { total: 100, types: new Map([["root", 10], ["compound", 50]]) };
  const r = compareCounts({ root: 10, compound: 50 }, expected, 100);
  assert.equal(r.warnings.length, 0);
  assert.ok(r.typeDiffs.every(d => d.diff === 0));
});

test("compareCounts: warns on a large type divergence", () => {
  const expected = { total: 100, types: new Map([["root", 10]]) };
  const r = compareCounts({ root: 9000 }, expected, 100);
  assert.ok(r.warnings.some(w => /root/.test(w)));
});

test("compareCounts: tolerates small drift without warning", () => {
  const expected = { total: 286561, types: new Map([["compound", 126360]]) };
  const r = compareCounts({ compound: 126359 }, expected, 286560); // -1, within tolerance
  assert.equal(r.warnings.length, 0);
});

test("compareCounts: warns when record count is far from expected", () => {
  const expected = { total: 286561, types: new Map() };
  const r = compareCounts({}, expected, 200000);
  assert.ok(r.warnings.some(w => /Record count/.test(w)));
});

test("compareCounts: flags missing expected file", () => {
  const r = compareCounts({ root: 1 }, null, 100);
  assert.ok(r.warnings.some(w => /No expected counts/.test(w)));
});

// ---- Sense depth: sense-unit counting ----
test("senseUnits counts markers with a floor of 1", () => {
  assert.equal(senseUnits("<div n='1'> a <div n='2'> b", /<div\b/g), 2);
  assert.equal(senseUnits("single sense, no marker", /<div\b/g), 1);
  assert.equal(senseUnits("∙²1 a ∙²2 b ∙²3 c", /∙/g), 3);
  assert.equal(senseUnits("", /<div\b/g), 1);
});

test("senseUnits is repeatable (does not leak regex lastIndex)", () => {
  const re = /<div\b/g;
  assert.equal(senseUnits("<div><div>", re), 2);
  assert.equal(senseUnits("<div><div>", re), 2); // second call must match the first
});

// ---- R2 source anchors: lookup keys, marker splitting, alignment score ----
test("lookupKeysForLemma carries historical source spellings", () => {
  assert.deepEqual(lookupKeysForLemma("dharma"), ["Darma", "DarmaH", "Darmma", "DarmmaH", "dharma"]);
  assert.deepEqual(lookupKeysForLemma("bodhisattva"), ["boDisattva", "boDisattvaH", "boDisattvaM", "bodhisattva"]);
});

test("splitExplicitMarkers keeps preface and numbered parts stable", () => {
  const parts = splitExplicitMarkers("grammar {@1@} first {@--2@} second", /\{@\s*(?:--)?(\d+)\.?\s*@\}/g);
  assert.deepEqual(parts.map(part => part.localId), ["preface", "1", "2"]);
  assert.equal(parts[0].splitConfidence, "lumped-proxy");
  assert.equal(parts[1].splitConfidence, "explicit");
  assert.deepEqual(parts.map(part => part.markerLabel ?? null), [null, "1", "2"]);
  assert.deepEqual(parts.map(part => part.markerRunIndex ?? null), [null, 0, 0]);
});

test("splitExplicitMarkers records numeric marker-run resets", () => {
  const parts = splitExplicitMarkers("grammar {@1@} first {@2@} second {@1@} derived", /\{@\s*(?:--)?(\d+)\.?\s*@\}/g);
  assert.deepEqual(parts.map(part => part.localId), ["preface", "1", "2", "1"]);
  assert.deepEqual(parts.map(part => part.markerRunIndex ?? null), [null, 0, 0, 1]);
});

test("splitExplicitMarkers captures div n labels while keeping ordinal ids", () => {
  const marker = /<div\b(?:[^>]*?\bn=["']?([^"'>\s]+))?[^>]*>/g;
  const parts = splitExplicitMarkers("lead <div n=\"1\"> first <div type=\"x\" n=\"p\"> preverb <div n=\"2\"> second", marker, {
    useMarkerLabelAsLocalId: false
  });
  assert.deepEqual(parts.map(part => part.localId), ["preface", "1", "2", "3"]);
  assert.deepEqual(parts.map(part => part.markerLabel ?? null), [null, "1", "p", "2"]);
  assert.deepEqual(parts.map(part => part.markerRunIndex ?? null), [null, 0, null, 0]);
});

test("jaccard scores anchor overlap", () => {
  assert.equal(jaccard(["a", "b"], ["b", "c"]), 1 / 3);
  assert.equal(jaccard([], []), 0);
});

test("sourceRecordCounts keeps the largest source records first", () => {
  const rows = [
    { blockIds: ["2"], rawHeadword: "b", sourceLine: 20, href: "b" },
    { blockIds: ["1"], rawHeadword: "a", sourceLine: 10, href: "a" },
    { blockIds: ["2"], rawHeadword: "b", sourceLine: 20, href: "b" },
    { blockIds: ["3"], rawHeadword: "c", sourceLine: 30, href: "c" }
  ];
  assert.deepEqual(sourceRecordCounts(rows, 2), [
    { blockId: "2", rawHeadword: "b", sourceLine: 20, href: "b", rowCount: 2 },
    { blockId: "1", rawHeadword: "a", sourceLine: 10, href: "a", rowCount: 1 }
  ]);
});

test("indigenousAuthorityHints keeps SKD and VCP authority evidence separate from citations", () => {
  assert.deepEqual(indigenousAuthorityHints("medinI . hemacandraH .. hitodeSe .", "skd"), [
    "auth:hemacandra",
    "auth:hitopadesa",
    "auth:medini"
  ]);
  assert.deepEqual(indigenousAuthorityHints("hemaca0 na0 pu0 medi0", "vcp"), [
    "auth:hemaca",
    "auth:medi"
  ]);
  assert.deepEqual(indigenousAuthorityHints("medinI .", "mw"), []);
});

test("reverseMatchProfile ranks AE equivalents by first matching group", () => {
  const lookup = new Set(["gam"]);
  assert.deepEqual(
    reverseMatchProfile("{@Approach@} {#upa gam#} {#yA#}", lookup),
    { rank: "high", firstGroupIndex: 1, matchGroupCount: 1, equivalentGroupCount: 3, score: 0.5 }
  );
  assert.equal(
    reverseMatchProfile("{@A@} {#foo#} {#bar#} {#baz#} {#gam#}", lookup).rank,
    "medium"
  );
  assert.equal(
    reverseMatchProfile("{@A@} {#one#} {#two#} {#three#} {#four#} {#five#} {#six#} {#gam#}", lookup).rank,
    "low"
  );
  assert.equal(
    reverseMatchProfile("{@A@} {#one#} {#two#} {#three#} {#four#} {#five#} {#six#} {#seven#} {#eight#} {#nine#} {#ten#} {#gam#}", lookup).rank,
    "tail"
  );
  assert.equal(reverseMatchProfile("{@No match@} {#yA#}", lookup).rank, "no-match");
});

test("R2 parser diagnostics classify drift by rebuild work package", () => {
  assert.equal(
    classifyDrift({ parserFamily: "western", split: "ap-bullet", sourceSenseRows: 16, archivedSenseRows: 16 }),
    "archive-parity"
  );
  assert.equal(
    classifyDrift({ parserFamily: "western", split: "number-marker", sourceSenseRows: 172, archivedSenseRows: 23 }),
    "over-split-candidate"
  );
  assert.equal(
    classifyDrift({ parserFamily: "western", split: "div", sourceSenseRows: 367, archivedSenseRows: 0 }),
    "source-only-dictionary"
  );
  assert.equal(
    classifyDrift({ parserFamily: "reverse", split: "reverse-equivalent", sourceSenseRows: 243, archivedSenseRows: 30 }),
    "reverse-overmatch"
  );
  assert.equal(
    classifyDrift({ parserFamily: "indigenous", split: "iti-unit", sourceSenseRows: 27, archivedSenseRows: 9 }),
    "indigenous-coarse-review"
  );
});

test("R2 parser diagnostics keep parser priorities stable", () => {
  assert.equal(priorityForClass("over-split-candidate"), "high");
  assert.equal(priorityForClass("mild-drift"), "medium");
  assert.equal(priorityForClass("archive-parity"), "low");
  assert.equal(priorityForClass("no-anchor-evidence"), "info");
});

test("R2 parser diagnostics detects marker-run prefixes that match archive counts", () => {
  assert.deepEqual(
    markerRunPrefixMatch({ archivedSenseRows: 23, markerRunCounts: { 0: 9, 1: 14, 2: 4 } }),
    { maxRunIndex: 1, runCount: 2, countedRows: 23 }
  );
  assert.equal(markerRunPrefixMatch({ archivedSenseRows: 10, markerRunCounts: { 0: 9, 1: 14 } }), null);
});

test("R2 parser diagnostics detects source records that match archive counts", () => {
  assert.deepEqual(sourceRecordExactMatches({
    archivedSenseRows: 7,
    sourceRecordCounts: [
      { blockId: "1", rowCount: 8 },
      { blockId: "2", rowCount: 7 }
    ]
  }), [{ blockId: "2", rowCount: 7 }]);
  assert.deepEqual(sourceRecordExactMatches({ archivedSenseRows: 0, sourceRecordCounts: [{ blockId: "1", rowCount: 1 }] }), []);
});

test("R2 review packets route diagnostics by parser decision", () => {
  assert.equal(packetIdForDiagnostic({
    split: "div",
    driftClass: "over-split-candidate",
    parserFamily: "western"
  }), "div-source-scope");
  assert.equal(packetIdForDiagnostic({
    split: "reverse-equivalent",
    driftClass: "reverse-overmatch",
    parserFamily: "reverse"
  }), "ae-reverse-bands");
  assert.equal(packetIdForDiagnostic({
    split: "iti-unit",
    driftClass: "indigenous-coarse-review",
    parserFamily: "indigenous"
  }), "indigenous-iti-authority");
  assert.equal(packetIdForDiagnostic({
    split: "number-marker",
    driftClass: "over-split-candidate",
    parserFamily: "western"
  }), "marker-run-scope");
});

test("R2 review packets expose deterministic review clues", () => {
  assert.deepEqual(scopeCluesForDiagnostic({
    sourceRecordCounts: [{ blockId: "1" }, { blockId: "2" }],
    sourceRecordExactMatches: [{ blockId: "2" }],
    markerLabelCounts: { 1: 2 },
    markerRunPrefixMatch: { countedRows: 2 },
    reverseRankCounts: { high: 1 },
    indigenousAuthorityHintCounts: { "auth:medini": 1 }
  }), [
    "multiple-source-records",
    "source-record-exact-match",
    "marker-label-counts",
    "marker-run-prefix-match",
    "reverse-rank-counts",
    "indigenous-authority-hints"
  ]);
});

test("R2 label proposal artifact is generated from review packets", () => {
  assert.deepEqual(r2LabelProposals, buildR2LabelProposalPayload(r2ReviewPackets));
});

test("R2 label proposals cover every diagnostic id", () => {
  const diagnosticIds = r2ReviewPackets.packets.flatMap(packet => packet.rows.map(row => row.diagnosticId));
  assert.equal(Object.keys(r2LabelProposals.rowProposals).length, diagnosticIds.length);
  for (const diagnosticId of diagnosticIds) {
    assert.ok(r2LabelProposals.rowProposals[diagnosticId], `${diagnosticId} lacks a proposal`);
    assert.ok(r2LabelProposals.rowProposals[diagnosticId].proposedParserLabels.length, `${diagnosticId} lacks labels`);
  }
});

test("R2 label proposals use only packet vocabulary labels", () => {
  for (const proposal of Object.values(r2LabelProposals.rowProposals)) {
    const allowed = labelsForPacket(proposal.packetId, r2LabelProposals.packetLabelVocabulary);
    for (const label of proposal.proposedParserLabels) {
      assert.ok(allowed.has(label), `${proposal.diagnosticId} has out-of-vocabulary label ${label}`);
    }
  }
});

test("R2 label proposal checkpoint rows are stable with empty human fields", () => {
  assert.equal(r2LabelProposals.checkpointRows.length, 10);
  assert.deepEqual(r2LabelProposals.checkpointRows.map(row => row.diagnosticId), CHECKPOINT_DIAGNOSTIC_IDS);
  for (const row of r2LabelProposals.checkpointRows) {
    assert.ok(row.sourcePointers.length, `${row.diagnosticId} lacks source pointers`);
    assert.ok(row.proposedParserLabels.length, `${row.diagnosticId} lacks proposed parser labels`);
    assert.ok(row.reviewQuestion, `${row.diagnosticId} lacks a review question`);
    assert.equal(row.reviewedValue, null);
    assert.equal(row.reviewer, "");
    assert.equal(row.reviewedAt, "");
    assert.equal(row.note, "");
  }
});

test("R2 label proposal counts match the current review packet fixture", () => {
  assert.equal(r2LabelProposals.counts.diagnosticRows, 70);
  assert.equal(r2LabelProposals.counts.packetCount, 5);
  assert.deepEqual(r2LabelProposals.counts.byPacket, {
    "marker-run-scope": 28,
    "source-gap-controls": 17,
    "div-source-scope": 10,
    "indigenous-iti-authority": 10,
    "ae-reverse-bands": 5
  });
});

test("R2 checkpoint packet artifact is generated from label proposals", () => {
  assert.deepEqual(r2CheckpointPacket, buildR2CheckpointPayload(r2LabelProposals));
});

test("R2 checkpoint worksheet is generated from the checkpoint packet", () => {
  assert.equal(normalizeLineEndings(r2CheckpointReviewMd), buildR2CheckpointMarkdown(r2CheckpointPacket));
});

test("R2 checkpoint packet preserves the stable 10-row order", () => {
  assert.equal(r2CheckpointPacket.counts.checkpointRows, 10);
  assert.deepEqual(r2CheckpointPacket.checkpointRows.map(row => row.diagnosticId), CHECKPOINT_DIAGNOSTIC_IDS);
});

test("R2 checkpoint packet keeps human decision fields empty", () => {
  for (const row of r2CheckpointPacket.checkpointRows) {
    assert.equal(row.reviewedValue, null);
    assert.equal(row.reviewer, "");
    assert.equal(row.reviewedAt, "");
    assert.equal(row.note, "");
  }
});

test("R2 checkpoint packet rows are reviewer-ready", () => {
  for (const row of r2CheckpointPacket.checkpointRows) {
    assert.ok(row.sourcePointers.length, `${row.diagnosticId} lacks source pointers`);
    assert.ok(row.proposedParserLabels.length, `${row.diagnosticId} lacks proposed labels`);
    assert.ok(row.reviewQuestion, `${row.diagnosticId} lacks a review question`);
    assert.ok(row.packetTitle, `${row.diagnosticId} lacks packet context`);
  }
});

test("R2 checkpoint worksheet contains all checkpoint diagnostic ids", () => {
  for (const diagnosticId of CHECKPOINT_DIAGNOSTIC_IDS) {
    assert.ok(r2CheckpointReviewMd.includes(diagnosticId), `${diagnosticId} missing from worksheet`);
  }
});

test("R2 checkpoint review report machine fields match the checkpoint packet", () => {
  // The on-disk report carries human decisions (reviewed 2026-06-12); compare
  // machine fields only against a freshly generated machine-only payload.
  const machine = buildR2CheckpointReviewPayload(r2CheckpointPacket, new Map(), r2CheckpointReviewReport.generatedAt);
  const stripHuman = payload => ({
    ...payload,
    items: payload.items.map(item => ({
      ...item,
      reviewStatus: null,
      reviewedValue: null,
      reviewer: null,
      reviewedAt: null,
      note: null
    }))
  });
  assert.deepEqual(stripHuman(r2CheckpointReviewReport), stripHuman(machine));
});

test("R2 checkpoint review report carries complete human decisions", () => {
  assert.equal(r2CheckpointReviewReport.queue, "r2-checkpoint");
  assert.equal(r2CheckpointReviewReport.recordCount, 10);
  assert.deepEqual(r2CheckpointReviewReport.items.map(item => item.reviewId), CHECKPOINT_DIAGNOSTIC_IDS);
  for (const item of r2CheckpointReviewReport.items) {
    assert.equal(item.queue, "r2-checkpoint");
    assert.equal(item.subject.kind, "entry");
    assert.equal(item.reviewStatus, "reviewed-ok", `${item.reviewId} should be reviewed-ok`);
    assert.ok(item.reviewer, `${item.reviewId} lacks reviewer`);
    assert.ok(item.reviewedAt, `${item.reviewId} lacks reviewedAt`);
    assert.ok(item.note, `${item.reviewId} lacks a review note`);
    assert.ok(Array.isArray(item.reviewedValue?.acceptedParserLabels), `${item.reviewId} lacks acceptedParserLabels`);
    assert.ok(
      item.machineValue.allowedParserDispositions.includes(item.reviewedValue?.parserDisposition),
      `${item.reviewId} has an out-of-vocabulary parserDisposition`
    );
    for (const label of item.reviewedValue.acceptedParserLabels) {
      assert.ok(
        item.machineValue.proposedParserLabels.includes(label),
        `${item.reviewId} accepted label "${label}" is outside the proposed vocabulary`
      );
    }
  }
});

test("R2 checkpoint review report carries reviewer-ready machine values", () => {
  for (const item of r2CheckpointReviewReport.items) {
    assert.ok(item.sourcePointers.length, `${item.reviewId} lacks source pointers`);
    assert.ok(item.sourcePointers.every(pointer => pointer.href), `${item.reviewId} has a source pointer without href`);
    assert.ok(item.machineValue.proposedParserLabels.length, `${item.reviewId} lacks proposed labels`);
    assert.ok(item.machineValue.reviewQuestion, `${item.reviewId} lacks review question`);
    assert.deepEqual(item.machineValue.allowedParserDispositions, PARSER_DISPOSITIONS);
  }
});

test("R2 checkpoint review report ignores preserved human fields in machine-only mode", () => {
  const preserved = new Map([[
    "r2-drift:gam:pwg",
    {
      reviewStatus: "reviewed-corrected",
      reviewedValue: {
        acceptedParserLabels: ["target-primary-series"],
        parserDisposition: "promote-parser-candidate"
      },
      reviewer: "mg",
      reviewedAt: "2026-06-06",
      note: "Test decision."
    }
  ]]);
  const payload = buildR2CheckpointReviewPayload(r2CheckpointPacket, preserved, "2026-06-06T00:00:00.000Z");
  const item = payload.items.find(row => row.reviewId === "r2-drift:gam:pwg");
  assert.equal(item.reviewStatus, "needs-review");
  assert.equal(item.reviewedValue, null);
  assert.equal(item.reviewer, null);
  assert.equal(item.reviewedAt, null);
  assert.equal(item.note, "");
  assert.equal(item.machineValue.packetId, "div-source-scope");
});

test("applyPreservedDecisions re-applies the human overlay onto a machine-only payload", () => {
  // Regression guard for the CLI footgun: a plain rebuild must preserve human
  // decisions by reviewId, not blank them. main() overlays loadPreserved() via
  // this function; here we feed it the committed report's own decisions.
  const machine = buildR2CheckpointReviewPayload(r2CheckpointPacket, new Map(), r2CheckpointReviewReport.generatedAt);
  const preserved = preservedReviewMap(r2CheckpointReviewReport);
  const merged = applyR2CheckpointPreserved(machine, preserved);

  // The committed report is fully human-reviewed, so every row is carried forward.
  for (const item of merged.items) {
    const source = r2CheckpointReviewReport.items.find(row => row.reviewId === item.reviewId);
    assert.equal(item.reviewStatus, source.reviewStatus, `${item.reviewId} reviewStatus not preserved`);
    assert.deepEqual(item.reviewedValue, source.reviewedValue, `${item.reviewId} reviewedValue not preserved`);
    assert.equal(item.reviewer, source.reviewer, `${item.reviewId} reviewer not preserved`);
    assert.equal(item.reviewedAt, source.reviewedAt, `${item.reviewId} reviewedAt not preserved`);
    assert.equal(item.note, source.note, `${item.reviewId} note not preserved`);
    // Machine fields stay exactly as generated.
    assert.deepEqual(item.machineValue, machine.items.find(m => m.reviewId === item.reviewId).machineValue);
  }

  // Pure: the machine payload is not mutated, and an empty overlay is a no-op.
  assert.equal(machine.items[0].reviewStatus, "needs-review");
  assert.equal(applyR2CheckpointPreserved(machine, new Map()), machine);
});

test("R2 checkpoint review report rejects dirty checkpoint source rows", () => {
  const dirty = JSON.parse(JSON.stringify(r2CheckpointPacket));
  dirty.checkpointRows[0].reviewer = "mg";
  assert.throws(
    () => buildR2CheckpointReviewPayload(dirty, new Map(), "2026-06-06T00:00:00.000Z"),
    /checkpoint reviewer must be empty string/
  );
});

test("R2 checkpoint review report rejects source pointers without links", () => {
  const dirty = JSON.parse(JSON.stringify(r2CheckpointPacket));
  delete dirty.checkpointRows[0].sourcePointers[0].href;
  assert.throws(
    () => buildR2CheckpointReviewPayload(dirty, new Map(), "2026-06-06T00:00:00.000Z"),
    /source pointer is missing href/
  );
});

test("R2 drift explanation generator rejects incomplete or out-of-vocabulary checkpoint decisions", () => {
  const outOfVocab = JSON.parse(JSON.stringify(r2CheckpointReviewReport));
  outOfVocab.items[0].reviewedValue.acceptedParserLabels = ["not-a-proposed-label"];
  assert.throws(
    () => buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, outOfVocab),
    /accepted label "not-a-proposed-label" is outside the proposed labels/
  );

  const missingReviewer = JSON.parse(JSON.stringify(r2CheckpointReviewReport));
  missingReviewer.items[1].reviewer = null;
  assert.throws(
    () => buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, missingReviewer),
    /reviewer is empty/
  );

  const badDisposition = JSON.parse(JSON.stringify(r2CheckpointReviewReport));
  badDisposition.items[2].reviewedValue.parserDisposition = "not-a-disposition";
  assert.throws(
    () => buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, badDisposition),
    /parserDisposition "not-a-disposition" is not an allowed disposition/
  );
});

test("R2 drift explanation generator accepts decided and empty checkpoint overlays", () => {
  const decided = buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, r2CheckpointReviewReport);
  assert.equal(decided.counts.checkpointNeedsReview, 0);
  assert.equal(decided.counts.checkpointDecided, 10);
  assert.equal(decided.reviewStatus, "human-decided");
  const dispositionTotal = Object.values(decided.counts.checkpointByDisposition).reduce((sum, n) => sum + n, 0);
  assert.equal(dispositionTotal, 10);
  for (const disposition of Object.keys(decided.counts.checkpointByDisposition)) {
    assert.ok(PARSER_DISPOSITIONS.includes(disposition), `unexpected disposition ${disposition}`);
  }

  const emptied = {
    ...r2CheckpointReviewReport,
    items: r2CheckpointReviewReport.items.map(item => ({
      ...item,
      reviewStatus: "needs-review",
      reviewedValue: null,
      reviewer: null,
      reviewedAt: null,
      note: ""
    }))
  };
  const machineOnly = buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, emptied);
  assert.equal(machineOnly.counts.checkpointNeedsReview, 10);
  assert.equal(machineOnly.counts.checkpointDecided, 0);
  assert.equal(machineOnly.reviewStatus, "machine-explained");
});

test("R2 drift explanation generator reports a partially-human-decided mixed overlay", () => {
  const mixed = {
    ...r2CheckpointReviewReport,
    items: r2CheckpointReviewReport.items.map((item, index) => index === 0 ? {
      ...item,
      reviewStatus: "needs-review",
      reviewedValue: null,
      reviewer: null,
      reviewedAt: null,
      note: ""
    } : item)
  };
  const payload = buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, mixed);
  assert.equal(payload.counts.checkpointNeedsReview, 1);
  assert.equal(payload.counts.checkpointDecided, 9);
  assert.equal(payload.reviewStatus, "partially-human-decided");
});

test("R2 drift explanation doc is generated from the artifact", () => {
  assert.equal(normalizeLineEndings(r2DriftExplanationMd), buildR2DriftExplanationMarkdown(r2DriftExplanation));
});

// The committed doc is the post-decision form, so the machine-only markdown
// branch has no live doc to guard it. Snapshot it against a golden fixture
// generated from an emptied checkpoint overlay. Regenerate the fixture after an
// intentional change with:
//   node --input-type=module -e 'import fs from "node:fs";import {buildPayload,buildMarkdown} from "./scripts/build-r2-drift-explanation.mjs";const r=p=>JSON.parse(fs.readFileSync(p,"utf8"));const rev=r("src/data/review/r2-checkpoint-review.json");const e={...rev,items:rev.items.map(i=>({...i,reviewStatus:"needs-review",reviewedValue:null,reviewer:null,reviewedAt:null,note:""}))};fs.writeFileSync("test/fixtures/R2_DRIFT_EXPLANATION.machine-only.md",buildMarkdown(buildPayload(r("data/lexico/r2_packet_label_proposals.json"),r("data/lexico/r2_checkpoint_review_packet.json"),e)))'
test("R2 drift explanation machine-only doc matches its golden fixture", () => {
  const emptied = {
    ...r2CheckpointReviewReport,
    items: r2CheckpointReviewReport.items.map(item => ({
      ...item,
      reviewStatus: "needs-review",
      reviewedValue: null,
      reviewer: null,
      reviewedAt: null,
      note: ""
    }))
  };
  const payload = buildR2DriftExplanationPayload(r2LabelProposals, r2CheckpointPacket, emptied);
  const markdown = buildR2DriftExplanationMarkdown(payload);
  assert.equal(payload.reviewStatus, "machine-explained");
  assert.ok(!markdown.includes("## Counts By Disposition"), "machine-only doc must omit the disposition summary");
  assert.ok(markdown.includes("## Checkpoint Rows Still Needs-Review"), "machine-only doc must use the needs-review checkpoint header");
  assert.equal(normalizeLineEndings(r2DriftExplanationMachineOnlyMd), markdown);
});

test("R2 drift explanation rows cover every diagnostic id", () => {
  const proposalIds = Object.keys(r2LabelProposals.rowProposals);
  assert.equal(r2DriftExplanation.explanationRows.length, 70);
  assert.deepEqual(r2DriftExplanation.explanationRows.map(row => row.diagnosticId), proposalIds);
});

test("R2 drift explanation labels stay inside packet vocabularies", () => {
  for (const row of r2DriftExplanation.explanationRows) {
    const allowed = labelsForPacket(row.packetId, r2LabelProposals.packetLabelVocabulary);
    assert.ok(row.proposedParserLabels.length, `${row.diagnosticId} lacks proposed labels`);
    for (const label of row.proposedParserLabels) {
      assert.ok(allowed.has(label), `${row.diagnosticId} has out-of-vocabulary label ${label}`);
    }
    for (const explanation of row.proposedLabelExplanations) {
      assert.ok(explanation.meaning, `${row.diagnosticId} lacks meaning for ${explanation.label}`);
      assert.ok(explanation.parserConsequence, `${row.diagnosticId} lacks parser consequence for ${explanation.label}`);
    }
  }
});

test("R2 drift explanation keeps checkpoint rows stable and carries the recorded decisions", () => {
  assert.equal(r2DriftExplanation.counts.checkpointRows, 10);
  assert.equal(r2DriftExplanation.counts.checkpointNeedsReview, 0);
  assert.equal(r2DriftExplanation.counts.checkpointDecided, 10);
  assert.deepEqual(r2DriftExplanation.checkpointRows.map(row => row.diagnosticId), CHECKPOINT_DIAGNOSTIC_IDS);
  for (const row of r2DriftExplanation.checkpointRows) {
    assert.ok(
      ["reviewed-ok", "reviewed-corrected", "deferred", "blocked"].includes(row.reviewStatus),
      `${row.diagnosticId} has unexpected reviewStatus ${row.reviewStatus}`
    );
    assert.ok(row.sourcePointerCount > 0, `${row.diagnosticId} lacks source pointers`);
    assert.ok(row.proposedParserLabels.length, `${row.diagnosticId} lacks proposed labels`);
    assert.ok(row.reviewQuestion, `${row.diagnosticId} lacks review question`);
    assert.ok(row.reviewer, `${row.diagnosticId} lacks reviewer`);
    assert.ok(row.reviewedAt, `${row.diagnosticId} lacks reviewedAt`);
    assert.ok(row.note, `${row.diagnosticId} lacks a review note`);
    assert.ok(Array.isArray(row.reviewedValue?.acceptedParserLabels), `${row.diagnosticId} lacks acceptedParserLabels`);
    for (const label of row.reviewedValue.acceptedParserLabels) {
      assert.ok(row.proposedParserLabels.includes(label), `${row.diagnosticId} accepted out-of-vocabulary label ${label}`);
    }
    assert.ok(
      PARSER_DISPOSITIONS.includes(row.reviewedValue.parserDisposition),
      `${row.diagnosticId} has unexpected parserDisposition ${row.reviewedValue.parserDisposition}`
    );
  }
});

test("R2 drift explanation counts match current R2 artifacts", () => {
  assert.equal(r2DriftExplanation.counts.packetCount, 5);
  assert.equal(r2DriftExplanation.counts.diagnosticRows, 70);
  assert.deepEqual(r2DriftExplanation.counts.byPacket, r2LabelProposals.counts.byPacket);
  assert.deepEqual(r2DriftExplanation.counts.byDriftClass, r2LabelProposals.counts.byDriftClass);
  assert.deepEqual(r2DriftExplanation.counts.byPriority, r2LabelProposals.counts.byPriority);
  assert.equal(
    r2DriftExplanation.counts.proposedLabelAssignments,
    r2DriftExplanation.explanationRows.reduce((sum, row) => sum + row.proposedParserLabels.length, 0)
  );
});

test("R2 drift explanation doc names all checkpoint diagnostic ids", () => {
  for (const diagnosticId of CHECKPOINT_DIAGNOSTIC_IDS) {
    assert.ok(r2DriftExplanationMd.includes(diagnosticId), `${diagnosticId} missing from drift explanation doc`);
  }
  assert.ok(r2DriftExplanationMd.includes("Parser promotion is gated by each checkpoint row's recorded `parserDisposition`"));
});

// ---- H5 anomaly queue: quoted CSV parsing ----
test("parseCsv handles quoted commas and escaped quotes", () => {
  const rows = parseCsv('a,b,c\nx,"y, z","q ""quoted"""\n');
  assert.deepEqual(rows, [{ a: "x", b: "y, z", c: 'q "quoted"' }]);
});

test("H5 anomaly review has the classified 130-row sample", () => {
  assert.equal(h5AnomalyReviewReport.recordCount, 130);
  assert.equal(h5AnomalyReviewReport.items.length, 130);
  assert.equal(h5AnomalyReviewReport.reviewFamily, "h5-ghost-anomaly");
  assert.equal(h5AnomalyReviewReport.queue, "encoding-ocr");
  assert.deepEqual(
    countBy(h5AnomalyReviewReport.items, item => item.machineValue.sampleClass),
    H5_EXPECTED_CLASS_COUNTS
  );
});

test("H5 anomaly review values are stable and stay in the documented taxonomy", () => {
  assert.deepEqual(
    countBy(h5AnomalyReviewReport.items, item => item.reviewedValue),
    H5_EXPECTED_REVIEWED_VALUE_COUNTS
  );
  for (const item of h5AnomalyReviewReport.items) {
    assert.ok(H5_REVIEW_LABELS.has(item.reviewedValue), `${item.reviewId} has unexpected label ${item.reviewedValue}`);
    assert.equal(item.reviewStatus, "reviewed-ok", `${item.reviewId} should be reviewed-ok`);
    assert.equal(item.reviewer, "codex", `${item.reviewId} should retain reviewer`);
    assert.equal(item.reviewedAt, "2026-06-07", `${item.reviewId} should retain reviewedAt`);
    assert.ok(item.note, `${item.reviewId} should keep an audit note`);
  }
});

test("H5 anomaly review rows keep source pointers and generator-preserved human fields", () => {
  const preserved = loadPreserved(h5AnomalyReviewReportPath);
  assert.equal(preserved.size, 130);
  for (const item of h5AnomalyReviewReport.items) {
    assert.ok(item.sourcePointers.length >= 1, `${item.reviewId} missing source pointer`);
    const saved = preserved.get(item.reviewId);
    assert.ok(saved, `${item.reviewId} missing from generator preservation map`);
    assert.deepEqual(saved, {
      reviewStatus: item.reviewStatus,
      reviewedValue: item.reviewedValue,
      reviewer: item.reviewer,
      reviewedAt: item.reviewedAt,
      note: item.note
    });
  }
});

test("H5 maker QA packet is generated from the reviewed H5 report", () => {
  assert.deepEqual(
    h5MakerQaCandidates,
    buildH5MakerQaPayload(
      h5AnomalyReviewReport,
      h5MakerQaCandidates.generatedAt,
      preservedSourceCheckMap(h5MakerQaCandidates)
    )
  );
  assert.equal(normalizeLineEndings(h5MakerQaCandidatesMd), buildH5MakerQaMarkdown(h5MakerQaCandidates));
});

test("H5 maker QA packet keeps the stable 10-row source-check order", () => {
  assert.equal(h5MakerQaCandidates.status, "h5-maker-qa-candidate-packet");
  assert.equal(h5MakerQaCandidates.generatedBy, "npm run build-h5-maker-qa-candidates");
  assert.equal(h5MakerQaCandidates.counts.reviewRows, 130);
  assert.equal(h5MakerQaCandidates.counts.possibleTypoRows, 22);
  assert.equal(h5MakerQaCandidates.counts.inferredPossibleTypoRows, 16);
  assert.equal(h5MakerQaCandidates.counts.knownCorrectionCalibrationRows, 6);
  assert.equal(h5MakerQaCandidates.counts.qaCandidateRows, 10);
  assert.deepEqual(
    h5MakerQaCandidates.qaCandidateRows.map(row => row.reviewId),
    H5_MAKER_QA_REVIEW_IDS
  );
});

test("H5 maker QA packet rows keep source-check decisions without editing dictionary data", () => {
  assert.deepEqual(h5MakerQaCandidates.counts.byPair, { "MW/PWG": 6, "MW/PW": 4 });
  assert.deepEqual(h5MakerQaCandidates.counts.byNRealNeighbours, { "1": 5, "2": 5 });
  assert.equal(h5MakerQaCandidates.counts.sourceCheckedRows, 10);
  assert.equal(h5MakerQaCandidates.counts.acceptedCorrectionRows, 1);
  assert.deepEqual(h5MakerQaCandidates.counts.bySourceCheckStatus, {
    "source-supported-distinct": 5,
    "source-supported-variant": 4,
    "source-declared-correction-candidate": 1
  });
  for (const row of h5MakerQaCandidates.qaCandidateRows) {
    assert.equal(row.reviewDecision.reviewStatus, "reviewed-ok");
    assert.equal(row.reviewDecision.reviewedValue, "possible-typo");
    assert.notEqual(row.sampleClass, "known-correction");
    assert.ok(row.candidateSourcePointers.length >= 1, `${row.reviewId} missing candidate pointers`);
    assert.ok(row.contrastSourcePointers.length >= 1, `${row.reviewId} missing contrast pointers`);
    assert.notEqual(row.sourceCheckStatus, "needs-source-check");
    assert.equal(row.checkedBy, "codex");
    assert.equal(row.checkedAt, "2026-06-07");
    assert.ok(row.sourceCheckNote, `${row.reviewId} missing source-check note`);
    if (row.reviewId === "h5:mw-pwg-shared-doublet:MW-PWG:divaraTa:devaraTa") {
      assert.equal(row.sourceCheckStatus, "source-declared-correction-candidate");
      assert.equal(row.acceptedCorrection, "diviraTa");
    } else {
      assert.notEqual(row.sourceCheckStatus, "source-declared-correction-candidate");
      assert.equal(row.acceptedCorrection, null);
    }
  }
  for (const row of h5MakerQaCandidates.calibrationRows) {
    assert.equal(row.sampleClass, "known-correction");
    assert.equal(row.reviewDecision.reviewedValue, "possible-typo");
  }
});

test("H5 maker QA worksheet names every selected candidate", () => {
  for (const reviewId of H5_MAKER_QA_REVIEW_IDS) {
    assert.ok(h5MakerQaCandidatesMd.includes(reviewId), `${reviewId} missing from H5 maker QA worksheet`);
  }
  assert.ok(h5MakerQaCandidatesMd.includes("Current review status: `source-checked`"));
  assert.ok(h5MakerQaCandidatesMd.includes("source-declared-correction-candidate"));
  assert.ok(h5MakerQaCandidatesMd.includes("accepted correction: `diviraTa`"));
});

test("H5 maker correction proposal is generated from the source-checked QA packet", () => {
  assert.deepEqual(
    h5MakerCorrectionProposal,
    buildH5MakerCorrectionPayload(
      h5MakerQaCandidates,
      h5MakerCorrectionProposal.generatedAt,
      preservedCorrectionTargetMap(h5MakerCorrectionProposal)
    )
  );
  assert.equal(normalizeLineEndings(h5MakerCorrectionProposalMd), buildH5MakerCorrectionMarkdown(h5MakerCorrectionProposal));
});

test("H5 maker correction proposal keeps exactly the source-declared row", () => {
  assert.equal(h5MakerCorrectionProposal.status, "h5-maker-correction-proposal-packet");
  assert.equal(h5MakerCorrectionProposal.generatedBy, "npm run build-h5-maker-correction-proposal");
  assert.equal(h5MakerCorrectionProposal.counts.qaCandidateRows, 10);
  assert.equal(h5MakerCorrectionProposal.counts.proposalRows, 1);
  assert.equal(h5MakerCorrectionProposal.counts.excludedSourceSupportedRows, 9);
  assert.deepEqual(h5MakerCorrectionProposal.counts.excludedBySourceCheckStatus, {
    "source-supported-distinct": 5,
    "source-supported-variant": 4
  });
  assert.deepEqual(
    h5MakerCorrectionProposal.excludedRows.map(row => row.reviewId),
    H5_MAKER_QA_REVIEW_IDS.filter(reviewId => reviewId !== "h5:mw-pwg-shared-doublet:MW-PWG:divaraTa:devaraTa")
  );
});

test("H5 maker correction proposal cites candidate, target, and rejected-neighbor sources", () => {
  const [row] = h5MakerCorrectionProposal.proposalRows;
  assert.equal(row.reviewId, "h5:mw-pwg-shared-doublet:MW-PWG:divaraTa:devaraTa");
  assert.equal(row.lemma, "divaraTa");
  assert.equal(row.proposedCorrection, "diviraTa");
  assert.equal(row.rejectedNearestNeighbor, "devaraTa");
  assert.equal(row.sourceCheckStatus, "source-declared-correction-candidate");
  assert.deepEqual(row.dictionaries, ["MW", "PWG"]);
  assert.deepEqual(row.candidateSourcePointers.map(pointer => pointer.dictionary), ["MW", "PWG"]);
  assert.deepEqual(row.correctionTargetSourcePointers.map(pointer => pointer.dictionary), ["MW", "PWG"]);
  assert.deepEqual(row.correctionTargetSourcePointers.map(pointer => pointer.form), ["diviraTa", "diviraTa"]);
  assert.deepEqual(row.rejectedNearestNeighborSourcePointers.map(pointer => pointer.dictionary), ["MW", "PWG"]);
  for (const pointer of [
    ...row.candidateSourcePointers,
    ...row.correctionTargetSourcePointers,
    ...row.rejectedNearestNeighborSourcePointers
  ]) {
    assert.ok(pointer.href, `${pointer.dictionary} ${pointer.form} missing href`);
    assert.ok(pointer.L, `${pointer.dictionary} ${pointer.form} missing L`);
  }
});

test("H5 maker correction proposal keeps maker decision fields empty", () => {
  const [row] = h5MakerCorrectionProposal.proposalRows;
  assert.equal(row.makerDecision.submittedBy, null);
  assert.equal(row.makerDecision.submittedAt, null);
  assert.equal(row.makerDecision.externalIssueUrl, null);
  assert.equal(row.makerDecision.makerDisposition, null);
  assert.equal(row.makerDecision.note, "");
  assert.ok(h5MakerCorrectionProposalMd.includes("Proposed correction: `divaraTa` -> `diviraTa`"));
  assert.ok(h5MakerCorrectionProposalMd.includes("Rejected detector neighbor: `devaraTa`"));
  assert.ok(h5MakerCorrectionProposalMd.includes("submittedBy = null"));
});

// ---- THREE-AXES comparison packet: content, convention, microstructure ----
test("three-axis comparison packet is generated from existing atlas artifacts", () => {
  assert.deepEqual(
    threeAxisComparison,
    buildThreeAxisPayload(threeAxisSourceInputs, threeAxisComparison.generatedAt)
  );
  assert.equal(normalizeLineEndings(threeAxisComparisonMd), buildThreeAxisMarkdown(threeAxisComparison));
});

test("three-axis comparison keeps the stable L0 known-edge order", () => {
  assert.equal(threeAxisComparison.status, "three-axis-comparison-packet");
  assert.equal(threeAxisComparison.generatedBy, "npm run build-three-axis-comparison");
  assert.equal(threeAxisComparison.counts.comparisonRows, 13);
  assert.deepEqual(threeAxisComparison.comparisonRows.map(row => row.rowId), THREE_AXIS_EDGE_IDS);
  assert.deepEqual(threeAxisComparison.focusRows.map(row => row.rowId), [
    "three-axis:PWG:MW",
    "three-axis:CCS:CAE",
    "three-axis:WIL:SHS",
    "three-axis:PWG:SCH"
  ]);
});

test("three-axis comparison rows carry all three bounded axes", () => {
  for (const row of threeAxisComparison.comparisonRows) {
    assert.notEqual(row.contentAxis.parentInChild, null, `${row.rowId} missing content axis`);
    assert.notEqual(row.conventionAxis.conventionSimilarity, null, `${row.rowId} missing convention axis`);
    assert.notEqual(row.microstructureAxis.microstructureSimilarity01, null, `${row.rowId} missing microstructure axis`);
    for (const value of [
      row.contentAxis.parentInChild,
      row.contentAxis.jaccard,
      row.conventionAxis.conventionSimilarity,
      row.microstructureAxis.microstructureSimilarity01
    ]) {
      assert.ok(value >= 0 && value <= 1, `${row.rowId} axis value out of range: ${value}`);
    }
    assert.ok(row.contentAxis.band, `${row.rowId} missing content band`);
    assert.ok(row.conventionAxis.band, `${row.rowId} missing convention band`);
    assert.ok(row.microstructureAxis.band, `${row.rowId} missing microstructure band`);
    assert.ok(row.axisReading, `${row.rowId} missing axis reading`);
    assert.ok(row.interpretation, `${row.rowId} missing interpretation`);
  }
});

test("three-axis focus rows preserve the roadmap comparison signals", () => {
  const byId = new Map(threeAxisComparison.comparisonRows.map(row => [row.rowId, row]));
  const pwgMw = byId.get("three-axis:PWG:MW");
  assert.equal(pwgMw.contentAxis.band, "high-content-overlap");
  assert.equal(pwgMw.conventionAxis.band, "low-convention-overlap");
  assert.equal(pwgMw.axisReading, "content-carried-with-convention-and-register-recoding");
  const ccsCae = byId.get("three-axis:CCS:CAE");
  assert.equal(ccsCae.contentAxis.band, "high-content-overlap");
  assert.equal(ccsCae.conventionAxis.band, "high-convention-overlap");
  assert.equal(ccsCae.axisReading, "content-and-convention-aligned-register-shift");
  assert.equal(threeAxisComparison.counts.highContentLowConventionRows, 2);
  for (const rowId of THREE_AXIS_EDGE_IDS) {
    assert.ok(threeAxisComparisonMd.includes(rowId.replace("three-axis:", "").replace(":", " -> ")), `${rowId} missing from markdown table`);
  }
});

test("axisReadingForScores separates recoding and aligned-register cases", () => {
  assert.equal(
    axisReadingForScores({ parentInChild: 0.9, conventionSimilarity: 0.3, microstructureSimilarity: 0.4 }),
    "content-carried-with-convention-and-register-recoding"
  );
  assert.equal(
    axisReadingForScores({ parentInChild: 0.9, conventionSimilarity: 0.8, microstructureSimilarity: 0.9 }),
    "aligned-content-convention-register"
  );
  assert.equal(
    axisReadingForScores({ parentInChild: 0.2, conventionSimilarity: 0.8, microstructureSimilarity: 0.4 }),
    "shared-convention-with-narrow-content-overlap"
  );
});

// ---- H4 family profiles: stable ranking helpers ----
test("H4 mean and percentage rounding are stable", () => {
  assert.ok(Math.abs(h4Mean([0.1, 0.2, Number.NaN, 0.3]) - 0.2) < 1e-12);
  assert.equal(h4Mean([]), 0);
  assert.equal(roundPct(1 / 3), 0.3333);
});

test("rankFamilyFields chooses high and low fields deterministically", () => {
  const rows = [
    { fieldKey: "a", fieldOrder: 2, meanCoveragePct: 0.5, dictionariesWithCoverage: 1 },
    { fieldKey: "b", fieldOrder: 1, meanCoveragePct: 0.5, dictionariesWithCoverage: 3 },
    { fieldKey: "c", fieldOrder: 3, meanCoveragePct: 0.1, dictionariesWithCoverage: 1 }
  ];
  assert.deepEqual(rankFamilyFields(rows, "high", 2).map(row => row.fieldKey), ["b", "a"]);
  assert.deepEqual(rankFamilyFields(rows, "low", 2).map(row => row.fieldKey), ["c", "b"]);
});

// ---- H4 semantic-field review packet: stable machine-only samples ----
test("H4 review packet is generated from semantic field artifacts", () => {
  assert.deepEqual(
    h4ReviewPacket,
    buildH4ReviewPacketPayload(
      h4SemanticFields,
      h4FamilyProfiles,
      h4SemanticRows,
      h4ReviewPacket.generatedAt,
      preservedH4SourcePointerMap(h4ReviewPacket)
    )
  );
  assert.equal(normalizeLineEndings(h4ReviewPacketMd), buildH4ReviewPacketMarkdown(h4ReviewPacket));
});

test("H4 review packet keeps stable sample counts and order", () => {
  assert.equal(h4ReviewPacket.status, "h4-semantic-field-review-packet");
  assert.equal(h4ReviewPacket.generatedBy, "npm run build-h4-review-packet");
  assert.equal(h4ReviewPacket.counts.sampleRows, 105);
  assert.deepEqual(h4ReviewPacket.counts.bySampleType, EXPECTED_H4_SAMPLE_COUNTS);
  assert.deepEqual(countBy(h4ReviewPacket.sampleRows, row => row.sampleType), EXPECTED_H4_SAMPLE_COUNTS);
  assert.equal(h4ReviewPacket.sampleRows[0].reviewId, "h4-skd-false-low:skd:01:viSezyaniGnavargaH:sukftin");
  assert.equal(h4ReviewPacket.sampleRows[24].reviewId, "h4-skd-false-low:skd:25:SUdravargaH:SUdra");
  assert.equal(h4ReviewPacket.sampleRows[25].reviewId, "h4-vcp-high-coverage:vcp:01:narakavargaH:nAraka");
  assert.equal(h4ReviewPacket.sampleRows[45].reviewId, "h4-ap-ap90-delta:ap:01:vanOzaDivargaH:vipina");
  assert.equal(h4ReviewPacket.sampleRows[65].reviewId, "h4-specialized-baseline:armh:01:pAtAlaBogivargaH:aDoBuvana");
  assert.equal(h4ReviewPacket.sampleRows[85].reviewId, "h4-index-reverse-control:ae:01:avyayavargaH:cit");
});

test("H4 review rows keep human fields empty and labels valid", () => {
  const labels = new Set(H4_MACHINE_LABEL_VOCABULARY.map(row => row.label));
  const decisionLabels = new Set(Object.values(h4ReviewPacket.decisionVocabulary).flat());
  for (const row of h4ReviewPacket.sampleRows) {
    assert.equal(row.reviewStatus, "needs-review", `${row.reviewId} should remain needs-review`);
    assert.equal(row.reviewedValue, null, `${row.reviewId} reviewedValue should stay null`);
    assert.equal(row.reviewer, "", `${row.reviewId} reviewer should stay empty`);
    assert.equal(row.reviewedAt, "", `${row.reviewId} reviewedAt should stay empty`);
    assert.equal(row.note, "", `${row.reviewId} note should stay empty`);
    assert.ok(row.reviewQuestion, `${row.reviewId} lacks review question`);
    assert.ok(row.sourcePointers.length >= 2, `${row.reviewId} lacks source pointers`);
    assert.ok(row.sourcePointers.some(pointer => pointer.role === "amar-field-lemma"), `${row.reviewId} lacks AMAR pointer`);
    assert.ok(row.sourcePointers.some(pointer => pointer.role === "semantic-coverage-row"), `${row.reviewId} lacks coverage pointer`);
    assert.ok(labels.has(row.proposedLabel), `${row.reviewId} has unknown label`);
    assert.ok(row.expectedDecisionLabels.length, `${row.reviewId} lacks expected decision labels`);
    for (const label of row.expectedDecisionLabels) {
      assert.ok(decisionLabels.has(label), `${row.reviewId} has unknown decision label ${label}`);
    }
  }
});

test("H4 review packet counts match current semantic-field artifacts", () => {
  assert.equal(h4ReviewPacket.counts.familyProfiles, 5);
  assert.equal(h4ReviewPacket.counts.fieldContrasts, 12);
  assert.equal(h4ReviewPacket.counts.dictionaryCount, 43);
  assert.equal(h4ReviewPacket.counts.fieldCount, 24);
  assert.equal(h4ReviewPacket.counts.byDictionary.skd, 25);
  assert.equal(h4ReviewPacket.counts.byDictionary.vcp, 20);
  assert.equal(h4ReviewPacket.counts.byDictionary.ap, 20);
  assert.equal(h4ReviewPacket.counts.exactDictionaryPointers, 80);
});

test("H4 review worksheet names every review row", () => {
  for (const row of h4ReviewPacket.sampleRows) {
    assert.ok(h4ReviewPacketMd.includes(row.reviewId), `${row.reviewId} missing from markdown`);
  }
  assert.ok(h4ReviewPacketMd.includes("Archive/corpus parity is not an H4 optimization target"));
});

// ---- H6 structural-register review: stable distance labels ----
test("structuralDistance normalizes H6 chart coordinates", () => {
  assert.deepEqual(
    structuralDistance({ citationRegisterPct: 0, grammarPct: 0 }, { citationRegisterPct: 100, grammarPct: 100 }),
    { citationDeltaPct: 100, grammarDeltaPct: 100, structuralDistance01: 1 }
  );
  assert.equal(
    structuralDistance({ citationRegisterPct: 10, grammarPct: 20 }, { citationRegisterPct: 10, grammarPct: 20 }).structuralDistance01,
    0
  );
});

test("edgeReviewClass separates controls, tensions, and convergence", () => {
  assert.equal(
    edgeReviewClass({ consensus_support: 0.8 }, { structuralDistance01: 0.1 }, true, true),
    "positive-control"
  );
  assert.equal(
    edgeReviewClass({ consensus_support: 0.8 }, { structuralDistance01: 0.4 }, true, true),
    "genealogy-structure-tension"
  );
  assert.equal(
    edgeReviewClass({ consensus_support: 0.05 }, { structuralDistance01: 0.1 }, false, true),
    "structural-convergence"
  );
});

// ---- Xref hub review: target-class labels ----
test("classifyHubTarget separates prefix hubs, lexical targets, and normalization risks", () => {
  assert.equal(classifyHubTarget("a-"), "prefix-convention");
  assert.equal(classifyHubTarget("mahA\u02da"), "prefix-convention");
  assert.equal(classifyHubTarget("narasiMha"), "lexical-target");
  assert.equal(classifyHubTarget("paropadeSe pAMqityaM"), "normalization-risk");
});

// ---- Xref source-check packet: shared-core rows and prefix controls ----
test("xref source-check packet is generated from hub review and xref edges", () => {
  assert.deepEqual(
    xrefSourceCheckPacket,
    buildXrefSourceCheckPayload(
      xrefHubReview,
      xrefEdgeRows,
      xrefSourceCheckPacket.generatedAt,
      preservedXrefSourcePointerMap(xrefSourceCheckPacket)
    )
  );
  assert.equal(normalizeLineEndings(xrefSourceCheckMd), buildXrefSourceCheckMarkdown(xrefSourceCheckPacket));
});

test("xref source-check packet keeps stable shared-core and prefix-control order", () => {
  assert.equal(xrefSourceCheckPacket.status, "xref-source-check-packet");
  assert.equal(xrefSourceCheckPacket.generatedBy, "npm run build-xref-source-check-packet");
  assert.equal(xrefSourceCheckPacket.counts.sharedCoreRows, 40);
  assert.equal(xrefSourceCheckPacket.counts.prefixControlRows, 10);
  assert.deepEqual(xrefSourceCheckPacket.sharedCoreRows.map(row => row.sampleId), XREF_SHARED_CORE_IDS);
  assert.deepEqual(xrefSourceCheckPacket.prefixControlRows.map(row => row.controlId), XREF_PREFIX_CONTROL_IDS);
});

test("xref source-check rows keep human fields empty and reviewer-ready", () => {
  const vocabulary = new Set(XREF_LABEL_VOCABULARY.map(row => row.label));
  const rows = [...xrefSourceCheckPacket.sharedCoreRows, ...xrefSourceCheckPacket.prefixControlRows];
  assert.equal(rows.length, 50);
  for (const row of rows) {
    const id = row.sampleId ?? row.controlId;
    assert.equal(row.reviewStatus, "needs-source-check", `${id} should remain needs-source-check`);
    assert.equal(row.reviewedValue, null, `${id} reviewedValue should stay null`);
    assert.equal(row.reviewer, "", `${id} reviewer should stay empty`);
    assert.equal(row.reviewedAt, "", `${id} reviewedAt should stay empty`);
    assert.equal(row.note, "", `${id} note should stay empty`);
    assert.ok(row.reviewQuestion, `${id} lacks review question`);
    assert.ok(row.sourcePointers.length, `${id} lacks source pointers`);
    assert.ok(row.sourcePointers.every(pointer => pointer.href), `${id} has source pointer without href`);
    assert.ok(row.proposedLabels.length, `${id} lacks proposed labels`);
    for (const label of row.proposedLabels) {
      assert.ok(vocabulary.has(label), `${id} has out-of-vocabulary label ${label}`);
    }
  }
});

test("xref source-check counts match current generated artifacts", () => {
  assert.equal(xrefHubReview.counts.sharedCoreSample, 40);
  assert.equal(xrefSourceCheckPacket.counts.sourceCheckRows, 50);
  assert.equal(xrefSourceCheckPacket.counts.sourcePointerRows, 106);
  assert.equal(xrefSourceCheckPacket.counts.exactSharedCorePointers, 76);
  assert.equal(xrefSourceCheckPacket.counts.sharedCoreRowsWithMissingExactEdge, 4);
  assert.equal(xrefSourceCheckPacket.counts.prefixControlPointers, 30);
  assert.deepEqual(xrefSourceCheckPacket.counts.bySampleClass, {
    "shared-core": 40,
    "prefix-control": 10
  });
  assert.deepEqual(xrefSourceCheckPacket.counts.byProposedLabel, {
    "lexical-shared-core": 40,
    "prefix-convention": 10
  });
  assert.deepEqual(xrefSourceCheckPacket.counts.prefixControlsByDictionary, {
    "mw": 5,
    "pwg": 5
  });
});

test("xref source-check worksheet names all stable row ids", () => {
  for (const sampleId of XREF_SHARED_CORE_IDS) {
    assert.ok(xrefSourceCheckMd.includes(sampleId), `${sampleId} missing from source-check worksheet`);
  }
  for (const controlId of XREF_PREFIX_CONTROL_IDS) {
    assert.ok(xrefSourceCheckMd.includes(controlId), `${controlId} missing from source-check worksheet`);
  }
  assert.ok(xrefSourceCheckMd.includes("Prefix controls test convention pressure"));
});

// ---- All-dictionary coverage: classify + fit bands ----
test("coverage classify: priority root > compound > proper > gender", () => {
  assert.equal(classify("<L>1<k1>aMS<lex></lex> <info verb=\"genuineroot\"/>"), "rootVerb");
  assert.equal(classify("<L>1<k1>a-kAra body"), "compoundOrSubentry"); // hyphen in k1
  assert.equal(classify("<L>1<k1>deva <lex>m.</lex>"), "nounMasculine");
  assert.equal(classify("<L>1<k1>nadI <lex>f.</lex>"), "nounFeminine");
  assert.equal(classify("<L>1<k1>vana <lex>n.</lex>"), "nounNeuter");
  assert.equal(classify("<L>1<k1>x <lex>ind.</lex>"), "indeclinable");
  assert.equal(classify("<L>1<k1>x plain body"), "other");
});

test("coverage fitBand thresholds", () => {
  assert.equal(fitBand(0, 0, {}, 0), "empty");
  assert.equal(fitBand(50, 100, { head: 95, body: 95, gram: 25 }, 4), "full structured fit");
  assert.equal(fitBand(50, 100, { head: 85, body: 85, citeTagged: 0, citeInlineIti: 6 }, 1), "prose / iti fit");
  assert.equal(fitBand(50, 100, { head: 95, body: 95, gram: 6 }, 2), "partial structured fit");
  assert.equal(fitBand(10, 100, { head: 85, body: 85, citeTagged: 0, citeInlineIti: 0 }, 0), "entry-shell fit");
  assert.equal(fitBand(25, 100, { head: 10, body: 10 }, 0), "weak fit");
  assert.equal(fitBand(5, 100, { head: 10, body: 10 }, 0), "outside scheme");
});

test("coverage median and percent", () => {
  assert.equal(median([3, 1, 2]), 2);
  assert.equal(median([1, 2, 3, 4]), 2.5);
  assert.equal(median([]), 0);
  assert.equal(percent(1, 4), 25);
  assert.equal(percent(1, 0), 0);
});

// ---- Citation apparatus: most-frequent raw form ----
test("topForm picks the most frequent raw form for a canonical id", () => {
  assert.equal(topForm({ count: 7, forms: new Map([["MBh", 5], ["Mbh", 2]]) }), "MBh");
  assert.equal(topForm({ count: 1, forms: new Map([["RV", 1]]) }), "RV");
});

// ---- R2 explorer: buildLemmaPayload ----
import { buildLemmaPayload } from "../scripts/build-r2-explorer.mjs";
const FAKE_ROWS = [
  { dict: "ap", parserFamily: "western", senseId: "L1:1", splitConfidence: "explicit", sanskritAnchors: ["dharma", "pARini"], citationAnchors: ["ls:MBh"], text: "Duty" },
  { dict: "ap90", parserFamily: "western", senseId: "L2:1", splitConfidence: "explicit", sanskritAnchors: ["dharma", "pARini"], citationAnchors: ["ls:MBh"], text: "Duty (1890)" },
  { dict: "pwg", parserFamily: "western", senseId: "L3:1", splitConfidence: "explicit", sanskritAnchors: ["Darman"], citationAnchors: [], text: "Sitte" },
  { dict: "vcp", parserFamily: "indigenous", senseId: "L4:1", splitConfidence: "iti-unit", sanskritAnchors: ["dharma", "pARini"], citationAnchors: [], text: "Sanskrit text" }
];

test("buildLemmaPayload groups senses by dict and builds alignments", () => {
  const payload = buildLemmaPayload(FAKE_ROWS);
  assert.equal(Object.keys(payload.senses).length, 4);
  assert.ok(payload.senses.ap.length >= 1);
  assert.equal(payload.senses.ap[0].sense, "1");
  assert.ok(payload.alignments.length >= 1, "should produce at least one alignment");
  // alignment keys are "dict#localId" strings
  const apAp90 = payload.alignments.find(a => a.a.startsWith("ap#") && a.b.startsWith("ap90#"));
  assert.ok(apAp90, "ap~ap90 alignment expected");
  assert.equal(apAp90.j, 1, "ap~ap90 should be Jaccard 1 (identical anchors)");
  assert.equal(apAp90.cross, false);
});

test("buildLemmaPayload marks cross-tradition alignments", () => {
  const payload = buildLemmaPayload(FAKE_ROWS);
  const crossAlign = payload.alignments.find(a => a.cross);
  assert.ok(crossAlign, "cross-tradition alignment expected (western~indigenous)");
});

test("buildLemmaPayload caps alignments at 30 per lemma", () => {
  // Generate many rows for two dicts with different anchors to force many pairs
  const rows = [];
  for (let i = 0; i < 10; i++) {
    rows.push({ dict: "ap", parserFamily: "western", senseId: `L${i}:1`, splitConfidence: "explicit", sanskritAnchors: [`w${i}`, "shared"], citationAnchors: [], text: `sense ${i}` });
    rows.push({ dict: "pwg", parserFamily: "western", senseId: `L${100+i}:1`, splitConfidence: "explicit", sanskritAnchors: [`w${i}`, "shared"], citationAnchors: [], text: `sinn ${i}` });
    rows.push({ dict: "vcp", parserFamily: "indigenous", senseId: `L${200+i}:1`, splitConfidence: "iti-unit", sanskritAnchors: [`w${i}`, "shared"], citationAnchors: [], text: `sk ${i}` });
  }
  const payload = buildLemmaPayload(rows);
  assert.ok(payload.alignments.length <= 30, `cap should be 30, got ${payload.alignments.length}`);
});

// ---- R2 H1: h1SenseUnits (aliased to avoid collision with build-sense-depth senseUnits) ----
import { senseUnits as h1SenseUnits } from "../scripts/build-r2-h1.mjs";
const CAE_DICT = { code: "cae", split: "lumped-proxy" };
const BEN_DICT = { code: "ben", split: "number-marker" };
const AP_DICT  = { code: "ap",  split: "ap-bullet" };
const WIL_DICT = { code: "wil", split: "dot-squared" };
const PWG_DICT = { code: "pwg", split: "div" };
const SKD_DICT = { code: "skd", split: "iti-unit" };

test("h1SenseUnits returns 1 for empty body", () => {
  assert.equal(h1SenseUnits("", CAE_DICT), 1);
  assert.equal(h1SenseUnits("", BEN_DICT), 1);
});

test("h1SenseUnits counts number-marker senses for ben", () => {
  const body = "{@1.@} first sense; {@2.@} second sense; {@3.@} third sense.";
  assert.equal(h1SenseUnits(body, BEN_DICT), 3);
});

test("h1SenseUnits uses semicolons for lumped/div dicts (cae, pwg)", () => {
  const body = "meaning one; meaning two; meaning three";
  assert.equal(h1SenseUnits(body, CAE_DICT), 3);
  assert.equal(h1SenseUnits(body, PWG_DICT), 3);
});

test("h1SenseUnits counts ap-bullet markers", () => {
  const body = "∙²1 first; ∙²2 second.";
  assert.equal(h1SenseUnits(body, AP_DICT), 2);
});

test("h1SenseUnits counts dot-squared markers for wil", () => {
  const body = ".²1 first meaning .²2 second meaning";
  assert.equal(h1SenseUnits(body, WIL_DICT), 2);
});

test("h1SenseUnits falls back to 1 for single-sense entries", () => {
  assert.equal(h1SenseUnits("A simple definition with no markers.", BEN_DICT), 1);
  assert.equal(h1SenseUnits("Ein einfacher Satz.", PWG_DICT), 1);
});

test("h1SenseUnits strips ls citations before semicolon-splitting for lumped dicts", () => {
  const body = "some meaning <ls n='MBh'>iii,1;2;3</ls> more text";
  const units = h1SenseUnits(body, CAE_DICT);
  assert.equal(units, 1, "ls-internal semicolons should not inflate sense count");
});

// ---- R2 H2H3: splitInlineNumber / glossOverlap ----
import { splitInlineNumber, glossOverlap } from "../scripts/build-r2-h2h3.mjs";

test("splitInlineNumber returns single sense for body with no markers", () => {
  const parts = splitInlineNumber("A simple definition.");
  assert.equal(parts.length, 1);
  assert.ok(parts[0].includes("simple definition"));
});

test("splitInlineNumber splits SHS-style N. markers correctly", () => {
  const body = "{#yoga#}¦ m. ({#-gaH#}) 1. Junction, joining, union. 2. Combination, association. 3. Meditation.";
  const parts = splitInlineNumber(body);
  assert.equal(parts.length, 3);
  assert.ok(parts[0].includes("Junction"), `expected Junction in part[0], got "${parts[0]}"`);
  assert.ok(parts[1].includes("Combination"));
  assert.ok(parts[2].includes("Meditation"));
});

test("splitInlineNumber strips XML tags before splitting", () => {
  const body = "<entry>1. First sense. 2. Second sense.</entry>";
  const parts = splitInlineNumber(body);
  assert.equal(parts.length, 2);
});

test("splitInlineNumber strips curly-brace markup before splitting", () => {
  const body = "{#foo#}¦ m. 1. A thing. 2. Another thing.";
  const parts = splitInlineNumber(body);
  assert.equal(parts.length, 2);
  assert.ok(parts[0].includes("thing"));
});

test("glossOverlap returns 1 for identical texts", () => {
  const ov = glossOverlap("Junction joining union", "Junction joining union");
  assert.equal(ov, 1);
});

test("glossOverlap returns 0 for empty texts", () => {
  assert.equal(glossOverlap("", ""), 0);
  assert.equal(glossOverlap("abc", ""), 0);
});

test("glossOverlap is symmetric", () => {
  const a = "a share or portion of land";
  const b = "a portion of property";
  assert.equal(glossOverlap(a, b), glossOverlap(b, a));
});

test("glossOverlap gives high score for near-identical senses (WIL→SHS pattern)", () => {
  const wil = "Junction, joining, union.";
  const shs = "Junction, joining, union.";
  assert.ok(glossOverlap(wil, shs) >= 0.9, "near-verbatim copy should score >= 0.9");
});

test("glossOverlap gives low score for condensed YAT-style senses", () => {
  const wil = "Religious and abstract meditation, devotion, spiritual worship.";
  const yat = "Junction; meeting; devotion; fitness.";
  const ov = glossOverlap(wil, yat);
  assert.ok(ov < 0.4, `condensed sense should score below 0.4, got ${ov}`);
});

// ---- R2 H1 panel: stemKey ----
import { stemKey } from "../scripts/build-r2-h1-panel.mjs";

test("stemKey strips trailing H (masculine nominative)", () => {
  assert.equal(stemKey("yogaH"), "yoga");
  assert.equal(stemKey("DarmaH"), "Darma");
});

test("stemKey strips trailing M (neuter nominative)", () => {
  assert.equal(stemKey("karmaN"), "karmaN"); // N not stripped (only H/M)
  assert.equal(stemKey("manaM"), "mana");
});

test("stemKey is idempotent on stems without endings", () => {
  assert.equal(stemKey("yoga"), "yoga");
  assert.equal(stemKey("kAla"), "kAla");
  assert.equal(stemKey("hari"), "hari");
});

test("stemKey does not strip mid-word H or M", () => {
  assert.equal(stemKey("dharma"), "dharma");
  assert.equal(stemKey("brahman"), "brahman");
});

// ---- R2 page generation: build-r2-pages.mjs ----
import { yearToX, rateToY, patternColor, h1Points, h2Bars, h3rDumbbells } from "../scripts/build-r2-pages.mjs";

test("patternColor maps patterns to hex colors", () => {
  assert.equal(patternColor("copy"), "#2ca02c"); // green
  assert.equal(patternColor("verbatim copy"), "#2ca02c");
  assert.equal(patternColor("condensation"), "#d62728"); // red
  assert.equal(patternColor("revision"), "#ff7f0e"); // orange
  assert.equal(patternColor("unknown"), "#1f77b4"); // default
});

test("yearToX maps years to x coordinates per spec", () => {
  assert.equal(yearToX(1820), 60);
  assert.equal(yearToX(1960), 550);
  const y1832 = yearToX(1832);
  assert.ok(y1832 > 60 && y1832 < 150, `1832 should map between 60 and 150, got ${y1832}`);
});

test("rateToY maps rates to y coordinates", () => {
  assert.equal(rateToY(0), 250);
  assert.equal(rateToY(1), 40);
  const mid = rateToY(0.5);
  assert.ok(mid > 40 && mid < 250, `0.5 should map between 40 and 250, got ${mid}`);
});

test("h1Points generates SVG with 11 data points plus legend", () => {
  const h1Data = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_h1.json"), "utf-8"));
  const svg = h1Points(h1Data);
  assert.ok(svg.includes("<svg"), "output should contain SVG tag");
  assert.ok(svg.includes("skd"), "should contain dict label skd");
  assert.ok(svg.includes("ap"), "should contain dict label ap");
  assert.ok(svg.includes("Pearson"), "should contain Pearson-r annotation");
  assert.ok(svg.includes("indigenous"), "should contain legend");
});

test("h2Bars generates SVG with 4 bars and percentage labels", () => {
  const h2h3Data = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_h2h3.json"), "utf-8"));
  const svg = h2Bars(h2h3Data);
  assert.ok(svg.includes("<svg"), "output should contain SVG tag");
  assert.ok(svg.includes("76%"), "should contain cited rate as 76% (0.762)");
  assert.ok(svg.includes("59%"), "should contain uncited rate as 59% (0.591)");
  assert.ok(svg.includes("Cited"), "should have Cited group label");
  assert.ok(svg.includes("Uncited"), "should have Uncited group label");
});

test("h3rDumbbells generates SVG with 3 edges and pattern colors", () => {
  const h2h3Data = JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", "r2_h2h3.json"), "utf-8"));
  const svg = h3rDumbbells(h2h3Data);
  assert.ok(svg.includes("<svg"), "output should contain SVG tag");
  const lineCount = (svg.match(/<line/g) || []).length;
  assert.ok(lineCount >= 3, `should have ≥3 lines for dumbbells, got ${lineCount}`);
  // Check that the 3 edges are represented
  assert.ok(svg.includes("Wilson 1832"), "should contain Wilson 1832");
  assert.ok(svg.includes("Śabda-Sāgara"), "should contain Śabda-Sāgara");
  assert.ok(svg.includes("Apte"), "should contain Apte");
});
