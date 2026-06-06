// Build machine-readable R2 label proposals and the human checkpoint slice.
//
// This is intentionally a Labels + Checkpoint artifact. It does not change R2
// splitting, source anchors, review rows, public pages, or runtime behavior.
//
// Usage: npm run build-r2-label-proposals

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const PACKETS_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_review_packets.json");
const OUT = path.resolve(process.cwd(), "data", "lexico", "r2_packet_label_proposals.json");

export const CHECKPOINT_DIAGNOSTIC_IDS = Object.freeze([
  "r2-drift:gam:pwg",
  "r2-drift:dharma:pwg",
  "r2-drift:gam:ben",
  "r2-drift:rama:ben",
  "r2-drift:gam:ae",
  "r2-drift:dharma:ae",
  "r2-drift:dharma:vcp",
  "r2-drift:dharma:skd",
  "r2-drift:iti:ap",
  "r2-drift:gam:ap"
]);

export const PACKET_LABEL_VOCABULARY = Object.freeze({
  "div-source-scope": {
    doc: "docs/R2_DIV_SOURCE_SCOPE_LABELS.md",
    labels: {
      "target-primary-series": {
        meaning: "Main source record for the requested lookup or homonym.",
        parserConsequence: "Candidate for R2 sense splitting after marker-depth rules are reviewed."
      },
      "same-headword-supplement": {
        meaning: "Later addendum or continuation keyed to the same headword or homonym.",
        parserConsequence: "Keep as evidence, but do not merge into the main count until a supplement-folding rule is approved."
      },
      "separate-homonym": {
        meaning: "Explicit homonym or distinct raw headword caught by the lookup bundle.",
        parserConsequence: "Track separately; do not count as the target series."
      },
      "prefixed-or-derived-series": {
        meaning: "Prefixed verbs, participles, compounds, or derivative subseries under a root or headword.",
        parserConsequence: "Keep nested or lower-confidence unless the target is explicitly that subseries."
      },
      "cross-reference-only": {
        meaning: "Comparison or see-also material without an independent sense series.",
        parserConsequence: "Preserve as source evidence; no default sense-count contribution."
      },
      "source-expansion-control": {
        meaning: "Source-backed PW/PWK row with no archived R2 baseline.",
        parserConsequence: "Useful for parser design, but not archive parity evidence."
      },
      "lookup-bundle-split": {
        meaning: "The anchor lookup deliberately includes multiple historical spellings or raw headwords.",
        parserConsequence: "Split by raw headword or homonym before comparing row counts."
      },
      "candidate-sense-marker": {
        meaning: "Explicit nested semantic numbering in a target-primary source record.",
        parserConsequence: "Count only after depth and parent/child rules are chosen."
      },
      "supplement-marker": {
        meaning: "An addendum continues or corrects earlier numbering.",
        parserConsequence: "Keep outside target count until supplement folding is reviewed."
      }
    }
  },
  "marker-run-scope": {
    doc: "docs/R2_MARKER_RUN_SCOPE_LABELS.md",
    labels: {
      "archive-prefix-runs": {
        meaning: "The archived count equals the first one or more explicit marker runs.",
        parserConsequence: "Candidate main parser window; later rows stay in retained side tables."
      },
      "reset-run-expansion": {
        meaning: "Later numeric marker sequences restart after a completed run.",
        parserConsequence: "Preserve as derived or later expansion until dictionary-specific rules are reviewed."
      },
      "preface-proxy-extra": {
        meaning: "A source-backed row carries headword, POS, or header text rather than an explicit sense marker.",
        parserConsequence: "Exclude from sense counts by default unless a reviewed dictionary rule keeps it."
      },
      "lookup-bundle-split": {
        meaning: "The anchor lookup aggregates raw headwords such as rama and rAma.",
        parserConsequence: "Split by raw headword or homonym before marker-run comparison."
      },
      "source-record-exact-target": {
        meaning: "One source record's row count equals the archive count.",
        parserConsequence: "Candidate target record, not proof that sibling records are irrelevant."
      },
      "single-run-parity-control": {
        meaning: "One explicit marker run matches the archive after dropping the preface row.",
        parserConsequence: "Positive parser control, not a blocking decision."
      },
      "preface-retained-control": {
        meaning: "The exact archive/source count includes a preface or header proxy.",
        parserConsequence: "Low-priority cue; decide whether the header carries content."
      },
      "lumped-parity-control": {
        meaning: "Source and archive both have one unsplit row.",
        parserConsequence: "Useful coverage control, not evidence for marker-run logic."
      },
      "no-anchor-control": {
        meaning: "Neither source-backed nor archived row exists.",
        parserConsequence: "Keep as a control; no parser decision now."
      }
    }
  },
  "ae-reverse-bands": {
    doc: "docs/R2_AE_REVERSE_BAND_LABELS.md",
    labels: {
      "reverse-high-candidate": {
        meaning: "The first matching Sanskrit equivalent is in AE equivalent group 0-2.",
        parserConsequence: "Keep in the first AE review band; do not count as final alignment without source-role review."
      },
      "reverse-medium-review": {
        meaning: "The first matching Sanskrit equivalent is in group 3-4.",
        parserConsequence: "Keep as a secondary review band; useful for distinctive lemmas, risky for common roots."
      },
      "reverse-low-context": {
        meaning: "The first matching Sanskrit equivalent is in group 5-9.",
        parserConsequence: "Retain as context, but exclude from default cross-dictionary alignment counts."
      },
      "reverse-tail-overmatch": {
        meaning: "The first matching Sanskrit equivalent is in group 10 or later.",
        parserConsequence: "Retain only as overmatch evidence unless a reviewer promotes the row."
      },
      "direct-equivalent-candidate": {
        meaning: "The queried Sanskrit form is a direct equivalent for the English headword.",
        parserConsequence: "Eligible for AE alignment review within its rank band."
      },
      "phrase-or-collocation-match": {
        meaning: "The queried form appears inside a phrase, compound, quoted example, or idiom.",
        parserConsequence: "Preserve as dictionary evidence, but do not treat as headword-level equivalence by default."
      },
      "broad-headword-overmatch": {
        meaning: "The English headword has many equivalent groups and the queried form appears deep in a broad list.",
        parserConsequence: "Use as a noise-control row; exclude from default alignment counts."
      },
      "reverse-no-anchor-control": {
        meaning: "AE has no source-backed reverse row for the anchor lemma.",
        parserConsequence: "Keep as a coverage control; no parser decision now."
      }
    }
  },
  "indigenous-iti-authority": {
    doc: "docs/R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md",
    labels: {
      "definition-iti-unit": {
        meaning: "An iti split carries a definition, synonym list, or semantic function list.",
        parserConsequence: "Candidate indigenous source unit; not automatically one dictionary sense."
      },
      "authority-quotation-unit": {
        meaning: "The unit carries a quotation or named authority phrase in SKD prose.",
        parserConsequence: "Preserve authority evidence separately from sense counting."
      },
      "authority-siglum-unit": {
        meaning: "The unit carries VCP-style abbreviated authority tokens.",
        parserConsequence: "Preserve as raw authority hints; do not normalize into citations without review."
      },
      "commentarial-discussion-unit": {
        meaning: "The unit is prose discussion of doctrine, lakshana, or commentary rather than a compact meaning.",
        parserConsequence: "Keep as explanatory evidence; group before sense-count comparison."
      },
      "morphology-grammar-unit": {
        meaning: "The unit carries derivation, root class, grammatical function, or form inventory.",
        parserConsequence: "Keep outside default semantic sense counts."
      },
      "headword-stub-unit": {
        meaning: "The split produces only the headword or a very small preface fragment.",
        parserConsequence: "Treat as parser artifact unless reviewed as content-bearing."
      },
      "same-headword-record-split": {
        meaning: "Multiple source records with the same headword contribute rows.",
        parserConsequence: "Split records before comparing with archived counts."
      },
      "raw-headword-split": {
        meaning: "Lookup gathers distinct raw headwords such as rama and rAma.",
        parserConsequence: "Keep raw headwords separate unless the reviewed target merges them."
      },
      "source-record-exact-control": {
        meaning: "One source record row count equals the archived count.",
        parserConsequence: "Useful parser control, not semantic proof."
      },
      "lumped-indigenous-proxy": {
        meaning: "A source record has no explicit iti split and is represented by one proxy row.",
        parserConsequence: "Preserve as source evidence; do not infer internal sense boundaries."
      },
      "no-anchor-control": {
        meaning: "No SKD/VCP source-backed row exists for the anchor in this prototype.",
        parserConsequence: "Keep as a coverage control; no parser decision now."
      }
    }
  },
  "source-gap-controls": {
    doc: "docs/R2_SOURCE_GAP_CONTROL_LABELS.md",
    labels: {
      "mild-drift-follow-up": {
        meaning: "Drift is visible but lower-risk than the high-priority parser families.",
        parserConsequence: "Queue after promoted parser rules; do not block the current R2 slice."
      },
      "under-split-marker-gap": {
        meaning: "Source rows are fewer than archived rows because marker coverage is coarser than the archived fixture.",
        parserConsequence: "Review nested marker coverage and lookup variants after high-risk packets."
      },
      "nested-marker-gap": {
        meaning: "Source text contains submarkers or subpoints not yet split as separate rows.",
        parserConsequence: "Preserve as a targeted parser follow-up, not a source absence claim."
      },
      "preface-proxy-extra": {
        meaning: "A source-backed row carries headword, POS, or header text rather than an explicit sense marker.",
        parserConsequence: "Exclude from default sense counts unless a reviewed rule keeps it."
      },
      "lookup-bundle-split": {
        meaning: "The lookup includes multiple raw headwords or homonyms.",
        parserConsequence: "Split raw headword or homonym records before count comparison."
      },
      "archive-parity-control": {
        meaning: "Source and archive counts match, or are close enough to be a positive parser control.",
        parserConsequence: "Use as a regression check while changing higher-risk parser rules."
      },
      "homonym-record-control": {
        meaning: "Parity depends on preserving separate homonym or source records.",
        parserConsequence: "Do not collapse homonyms just to satisfy row-count checks."
      },
      "continuation-proxy-row": {
        meaning: "A source row points at a continuation or body proxy rather than an independent sense.",
        parserConsequence: "Preserve as a parser artifact; inspect before counting."
      },
      "source-only-expansion": {
        meaning: "Source-backed row exists where the archived fixture has no baseline.",
        parserConsequence: "Keep as rebuild expansion evidence; no archive regression implied."
      },
      "no-anchor-control": {
        meaning: "No source-backed row and no archived row exist for the anchor pair.",
        parserConsequence: "Keep as a coverage control; revisit only when lookup coverage broadens."
      }
    }
  }
});

export const ROW_PROPOSAL_LABELS = Object.freeze({
  "r2-drift:gam:pwg": ["target-primary-series", "same-headword-supplement", "prefixed-or-derived-series", "separate-homonym", "candidate-sense-marker", "supplement-marker"],
  "r2-drift:rama:pwg": ["lookup-bundle-split", "target-primary-series", "separate-homonym", "candidate-sense-marker"],
  "r2-drift:dharma:pwg": ["target-primary-series", "same-headword-supplement", "candidate-sense-marker", "supplement-marker"],
  "r2-drift:iti:pwg": ["target-primary-series", "same-headword-supplement", "separate-homonym", "cross-reference-only", "candidate-sense-marker", "supplement-marker"],
  "r2-drift:gam:pw": ["target-primary-series", "source-expansion-control", "same-headword-supplement", "prefixed-or-derived-series", "candidate-sense-marker", "supplement-marker"],
  "r2-drift:rama:pw": ["lookup-bundle-split", "target-primary-series", "separate-homonym", "source-expansion-control", "candidate-sense-marker"],
  "r2-drift:dharma:pw": ["target-primary-series", "source-expansion-control", "same-headword-supplement", "candidate-sense-marker", "supplement-marker"],
  "r2-drift:iti:pw": ["target-primary-series", "source-expansion-control", "separate-homonym", "same-headword-supplement", "candidate-sense-marker", "supplement-marker"],
  "r2-drift:bodhisattva:pw": ["target-primary-series", "source-expansion-control"],
  "r2-drift:bodhisattva:pwg": ["target-primary-series", "cross-reference-only", "same-headword-supplement", "prefixed-or-derived-series"],

  "r2-drift:gam:ben": ["archive-prefix-runs", "reset-run-expansion"],
  "r2-drift:rama:ben": ["source-record-exact-target", "lookup-bundle-split"],
  "r2-drift:rama:wil": ["archive-prefix-runs", "lookup-bundle-split", "preface-proxy-extra"],
  "r2-drift:rama:ap90": ["lookup-bundle-split", "reset-run-expansion"],
  "r2-drift:dharma:bhs": ["lookup-bundle-split", "preface-proxy-extra"],
  "r2-drift:bodhisattva:ap": ["single-run-parity-control", "preface-proxy-extra"],
  "r2-drift:dharma:ap": ["single-run-parity-control", "preface-proxy-extra"],
  "r2-drift:dharma:ap90": ["single-run-parity-control", "preface-proxy-extra"],
  "r2-drift:dharma:ben": ["single-run-parity-control", "preface-proxy-extra"],
  "r2-drift:dharma:wil": ["archive-prefix-runs", "preface-proxy-extra"],
  "r2-drift:gam:ap90": ["archive-prefix-runs", "reset-run-expansion", "preface-proxy-extra"],
  "r2-drift:iti:ben": ["single-run-parity-control", "preface-proxy-extra"],
  "r2-drift:iti:wil": ["single-run-parity-control", "preface-proxy-extra"],
  "r2-drift:iti:ap90": ["preface-retained-control"],
  "r2-drift:rama:mw72": ["lookup-bundle-split", "lumped-parity-control"],
  "r2-drift:bodhisattva:bhs": ["lumped-parity-control"],
  "r2-drift:bodhisattva:cae": ["lumped-parity-control"],
  "r2-drift:bodhisattva:wil": ["lumped-parity-control"],
  "r2-drift:dharma:cae": ["lumped-parity-control"],
  "r2-drift:dharma:sch": ["lumped-parity-control"],
  "r2-drift:gam:cae": ["lumped-parity-control"],
  "r2-drift:gam:sch": ["lumped-parity-control"],
  "r2-drift:rama:bhs": ["lumped-parity-control"],
  "r2-drift:bodhisattva:ap90": ["no-anchor-control"],
  "r2-drift:bodhisattva:ben": ["no-anchor-control"],
  "r2-drift:gam:bhs": ["no-anchor-control"],
  "r2-drift:gam:wil": ["no-anchor-control"],
  "r2-drift:iti:bhs": ["no-anchor-control"],

  "r2-drift:gam:ae": ["reverse-high-candidate", "reverse-medium-review", "reverse-low-context", "reverse-tail-overmatch", "phrase-or-collocation-match", "broad-headword-overmatch"],
  "r2-drift:iti:ae": ["reverse-high-candidate", "direct-equivalent-candidate", "reverse-medium-review", "reverse-low-context", "phrase-or-collocation-match", "reverse-tail-overmatch", "broad-headword-overmatch"],
  "r2-drift:dharma:ae": ["reverse-high-candidate", "direct-equivalent-candidate", "reverse-medium-review", "reverse-low-context", "reverse-tail-overmatch", "phrase-or-collocation-match", "broad-headword-overmatch"],
  "r2-drift:rama:ae": ["reverse-high-candidate", "phrase-or-collocation-match", "reverse-low-context", "reverse-tail-overmatch", "broad-headword-overmatch"],
  "r2-drift:bodhisattva:ae": ["reverse-no-anchor-control"],

  "r2-drift:dharma:vcp": ["definition-iti-unit", "authority-siglum-unit", "commentarial-discussion-unit"],
  "r2-drift:dharma:skd": ["source-record-exact-control", "same-headword-record-split", "definition-iti-unit", "authority-quotation-unit"],
  "r2-drift:rama:skd": ["morphology-grammar-unit", "definition-iti-unit", "authority-quotation-unit"],
  "r2-drift:iti:skd": ["headword-stub-unit", "definition-iti-unit", "authority-quotation-unit", "morphology-grammar-unit"],
  "r2-drift:iti:vcp": ["headword-stub-unit", "definition-iti-unit", "authority-siglum-unit", "authority-quotation-unit", "morphology-grammar-unit"],
  "r2-drift:rama:vcp": ["lumped-indigenous-proxy", "same-headword-record-split", "raw-headword-split", "source-record-exact-control", "authority-siglum-unit"],
  "r2-drift:bodhisattva:skd": ["definition-iti-unit", "authority-quotation-unit"],
  "r2-drift:bodhisattva:vcp": ["lumped-indigenous-proxy", "source-record-exact-control", "authority-siglum-unit"],
  "r2-drift:gam:skd": ["no-anchor-control"],
  "r2-drift:gam:vcp": ["no-anchor-control"],

  "r2-drift:rama:mw": ["mild-drift-follow-up", "lookup-bundle-split", "homonym-record-control"],
  "r2-drift:iti:ap": ["under-split-marker-gap", "nested-marker-gap", "preface-proxy-extra"],
  "r2-drift:rama:ap": ["under-split-marker-gap", "lookup-bundle-split", "preface-proxy-extra"],
  "r2-drift:dharma:mw": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:rama:cae": ["source-only-expansion"],
  "r2-drift:bodhisattva:mw": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:dharma:mw72": ["archive-parity-control", "homonym-record-control", "continuation-proxy-row"],
  "r2-drift:gam:ap": ["archive-parity-control", "continuation-proxy-row", "nested-marker-gap"],
  "r2-drift:gam:mw": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:gam:mw72": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:iti:cae": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:iti:mw": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:iti:mw72": ["archive-parity-control", "homonym-record-control"],
  "r2-drift:bodhisattva:mw72": ["no-anchor-control"],
  "r2-drift:bodhisattva:sch": ["no-anchor-control"],
  "r2-drift:iti:sch": ["no-anchor-control"],
  "r2-drift:rama:sch": ["no-anchor-control"]
});

function rowsFromPackets(packetsPayload) {
  return (packetsPayload.packets ?? []).flatMap(packet =>
    packet.rows.map(row => ({ packetId: packet.packetId, packetTitle: packet.title, ...row }))
  );
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

export function labelsForPacket(packetId, vocabulary = PACKET_LABEL_VOCABULARY) {
  return new Set(Object.keys(vocabulary[packetId]?.labels ?? {}));
}

export function vocabularyLabels(vocabulary = PACKET_LABEL_VOCABULARY) {
  return new Set(Object.values(vocabulary).flatMap(packet => Object.keys(packet.labels)));
}

function compactSourceRecord(record) {
  return {
    kind: "source-record",
    blockId: record.blockId,
    rawHeadword: record.rawHeadword,
    sourceLine: record.sourceLine,
    href: record.href,
    rowCount: record.rowCount
  };
}

function sourcePointersForRow(row) {
  const pointers = [];
  for (const record of row.sourceRecordCounts ?? []) pointers.push(compactSourceRecord(record));
  for (const record of row.sourceRecordExactMatches ?? []) {
    const exists = pointers.some(pointer => pointer.kind === "source-record" && pointer.blockId === record.blockId && pointer.href === record.href);
    if (!exists) pointers.push({ ...compactSourceRecord(record), role: "source-record-exact-match" });
  }
  for (const example of row.exampleRows ?? []) {
    pointers.push({
      kind: "example-row",
      rowId: example.rowId,
      senseId: example.senseId,
      sourceLine: example.sourceLine,
      href: example.href,
      splitConfidence: example.splitConfidence,
      limitations: example.limitations ?? []
    });
  }
  return pointers;
}

function reviewQuestionFor(row) {
  if (row.packetId === "div-source-scope") {
    return `Which ${row.dict.toUpperCase()} source record(s) should define the target ${row.lemma} primary series, and which should remain retained side evidence?`;
  }
  if (row.packetId === "marker-run-scope") {
    return `Do the proposed marker-run or source-record labels identify the parser window for ${row.lemma} in ${row.dict.toUpperCase()} while retaining non-target rows?`;
  }
  if (row.packetId === "ae-reverse-bands") {
    return `Which AE reverse rank bands for ${row.lemma} should be reviewed as direct equivalents, and which should remain context or overmatch evidence?`;
  }
  if (row.packetId === "indigenous-iti-authority") {
    return `Which ${row.dict.toUpperCase()} iti units for ${row.lemma} are definition, authority, grammar, or discussion evidence rather than reviewed senses?`;
  }
  return `Should ${row.lemma} in ${row.dict.toUpperCase()} remain a parser control or follow-up row, and do the source pointers explain the archive comparison drift?`;
}

function rowProposalFor(row, labels) {
  return {
    diagnosticId: row.diagnosticId,
    packetId: row.packetId,
    packetTitle: row.packetTitle,
    lemma: row.lemma,
    dict: row.dict,
    parserFamily: row.parserFamily,
    split: row.split,
    driftClass: row.driftClass,
    priority: row.priority,
    archiveComparison: {
      sourceSenseRows: row.sourceSenseRows,
      archivedSenseRows: row.archivedSenseRows,
      sourceToArchiveRatio: row.sourceToArchiveRatio,
      sourceRecordCount: row.sourceRecordCount
    },
    evidenceClues: row.scopeClues ?? [],
    proposedParserLabels: labels,
    sourcePointers: sourcePointersForRow(row),
    reviewQuestion: reviewQuestionFor(row),
    nextAction: row.nextAction
  };
}

function checkpointRowFor(proposal) {
  return {
    checkpointId: `checkpoint:${proposal.diagnosticId}`,
    diagnosticId: proposal.diagnosticId,
    packetId: proposal.packetId,
    lemma: proposal.lemma,
    dict: proposal.dict,
    driftClass: proposal.driftClass,
    priority: proposal.priority,
    archiveComparison: proposal.archiveComparison,
    sourcePointers: proposal.sourcePointers,
    proposedParserLabels: proposal.proposedParserLabels,
    reviewQuestion: proposal.reviewQuestion,
    reviewedValue: null,
    reviewer: "",
    reviewedAt: "",
    note: ""
  };
}

function validateRows(rows) {
  const errors = [];
  const seen = new Set();
  for (const row of rows) {
    if (seen.has(row.diagnosticId)) errors.push(`duplicate diagnosticId ${row.diagnosticId}`);
    seen.add(row.diagnosticId);
    if (!ROW_PROPOSAL_LABELS[row.diagnosticId]) errors.push(`${row.diagnosticId}: missing proposal entry`);
  }
  for (const diagnosticId of Object.keys(ROW_PROPOSAL_LABELS)) {
    if (!seen.has(diagnosticId)) errors.push(`${diagnosticId}: proposal entry has no source diagnostic row`);
  }
  return errors;
}

function validatePayload(payload, rows) {
  const errors = validateRows(rows);
  const proposalIds = Object.keys(payload.rowProposals);
  if (proposalIds.length !== rows.length) errors.push(`rowProposals has ${proposalIds.length} rows, expected ${rows.length}`);
  for (const row of rows) {
    const proposal = payload.rowProposals[row.diagnosticId];
    if (!proposal) continue;
    const allowed = labelsForPacket(proposal.packetId);
    if (!proposal.proposedParserLabels.length) errors.push(`${proposal.diagnosticId}: no proposedParserLabels`);
    for (const label of proposal.proposedParserLabels) {
      if (!allowed.has(label)) errors.push(`${proposal.diagnosticId}: label "${label}" is not in vocabulary for ${proposal.packetId}`);
    }
  }
  const checkpointIds = payload.checkpointRows.map(row => row.diagnosticId);
  if (checkpointIds.join("|") !== CHECKPOINT_DIAGNOSTIC_IDS.join("|")) {
    errors.push(`checkpointRows are not the stable checkpoint list: ${checkpointIds.join(", ")}`);
  }
  for (const row of payload.checkpointRows) {
    if (!row.sourcePointers.length) errors.push(`${row.diagnosticId}: checkpoint row lacks source pointers`);
    if (row.reviewedValue !== null) errors.push(`${row.diagnosticId}: reviewedValue must stay null`);
    if (row.reviewer !== "") errors.push(`${row.diagnosticId}: reviewer must stay empty`);
    if (row.reviewedAt !== "") errors.push(`${row.diagnosticId}: reviewedAt must stay empty`);
    if (row.note !== "") errors.push(`${row.diagnosticId}: note must stay empty`);
  }
  if (errors.length) {
    const error = new Error(`R2 label proposals failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

export function buildPayload(packetsPayload) {
  const rows = rowsFromPackets(packetsPayload);
  const rowProposals = {};
  for (const row of rows) {
    const labels = ROW_PROPOSAL_LABELS[row.diagnosticId];
    if (labels) rowProposals[row.diagnosticId] = rowProposalFor(row, labels);
  }

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "r2-label-proposals",
    claim: "R2 review packet diagnostics have machine-readable parser-label proposals plus a 10-row human checkpoint.",
    evidenceLabel: "derived",
    reviewStatus: "machine-proposed",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-r2-label-proposals",
    sourceGeneratedBy: packetsPayload.generatedBy,
    sourceFiles: [
      "data/lexico/r2_review_packets.json",
      "docs/R2_DIV_SOURCE_SCOPE_LABELS.md",
      "docs/R2_MARKER_RUN_SCOPE_LABELS.md",
      "docs/R2_AE_REVERSE_BAND_LABELS.md",
      "docs/R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md",
      "docs/R2_SOURCE_GAP_CONTROL_LABELS.md"
    ],
    packetLabelVocabulary: PACKET_LABEL_VOCABULARY,
    counts: {
      packetCount: new Set(rows.map(row => row.packetId)).size,
      diagnosticRows: rows.length,
      checkpointRows: CHECKPOINT_DIAGNOSTIC_IDS.length,
      byPacket: countBy(rows, row => row.packetId),
      byDriftClass: countBy(rows, row => row.driftClass),
      byPriority: countBy(rows, row => row.priority)
    },
    rowProposals,
    checkpointRows: CHECKPOINT_DIAGNOSTIC_IDS.map(id => checkpointRowFor(rowProposals[id])),
    archiveParityPolicy: "Archive parity is retained as a comparison signal and regression-control cue, not as the optimization target for parser labels.",
    limitations: [
      "Labels are machine proposals derived from existing R2 review packets and source-inspected proposal docs; they are not scholar-reviewed sense decisions.",
      "Checkpoint rows intentionally keep reviewedValue, reviewer, reviewedAt, and note empty for human review.",
      "The artifact does not promote parser behavior, alter source-anchor generation, change H5 review rows, or update public R2 pages.",
      "Archive parity is a comparison signal for future rebuild review, not a target to optimize by collapsing or discarding source evidence."
    ],
    boundaryNote: "Dictionary source rows, existing source anchors, recovered R2 archive fixtures, and source-inspected proposal docs only.",
    boundary: [
      "No R2 splitter behavior is changed.",
      "No source-anchor generation is changed.",
      "No H5 review rows or reviewedValue fields are changed.",
      "No public R2 pages, backend, database, runtime LLM, DCS, corpus, standards, or cross-repo content joins are used."
    ]
  };
  validatePayload(payload, rows);
  return payload;
}

function main() {
  try {
    const packetsPayload = JSON.parse(fs.readFileSync(PACKETS_PATH, "utf8"));
    const payload = buildPayload(packetsPayload);
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
    console.log(`Wrote ${path.relative(process.cwd(), OUT)} (${payload.counts.diagnosticRows} diagnostics, ${payload.counts.checkpointRows} checkpoint rows).`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
