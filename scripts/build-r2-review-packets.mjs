// Build reviewer-facing packets from the R2 parser diagnostics.
//
// The diagnostics file is intentionally row-oriented. This artifact groups the
// same dictionary-only evidence into stable work packets so review can proceed
// by parser decision rather than by isolated lemma/dictionary rows.
//
// Usage: npm run build-r2-review-packets

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const DIAGNOSTICS_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_parser_diagnostics.json");
const OUT = path.resolve(process.cwd(), "data", "lexico", "r2_review_packets.json");

const PACKET_DEFINITIONS = {
  "div-source-scope": {
    title: "PWG/PWK division and source-record scope",
    proves: "The current div splitter is counting several same-headword source records and marker classes together before sense-level review.",
    doesNotProve: "It does not prove that non-prefix source records are invalid or should be discarded.",
    nextDecision: "Decide which source records and div label classes represent the target sense series for each anchor lemma.",
    paperTarget: "R2 sense-structure methods; MW/Petersburg macro/micro trade-off."
  },
  "marker-run-scope": {
    title: "Numbered-marker run scope",
    proves: "Some archived counts match a prefix of deterministic marker runs, so later runs may be derived, prefixed, or separately keyed material.",
    doesNotProve: "It does not prove that matching prefixes are philologically complete senses.",
    nextDecision: "Review prefix matches and exact source-record matches before promoting a run boundary into parser logic.",
    paperTarget: "R2 sense-structure methods; dictionary-specific parser notes."
  },
  "ae-reverse-bands": {
    title: "AE reverse-equivalent rank bands",
    proves: "AE overmatching is measurable by equivalent-position rank for common Sanskrit roots.",
    doesNotProve: "It does not prove that high-rank rows are automatically valid alignments or that tail rows are false.",
    nextDecision: "Choose review bands for high, medium, low, and tail rows before using AE as alignment evidence.",
    paperTarget: "Cross-language sense alignment caveats."
  },
  "indigenous-iti-authority": {
    title: "SKD/VCP iti-unit authority review",
    proves: "Indigenous prose rows can expose authority hints even where they are not encoded as `<ls>` citations.",
    doesNotProve: "It does not prove that the prose has been normalized into a citation apparatus or fully split into senses.",
    nextDecision: "Review iti-unit boundaries, authority quotations, and source-record scope for SKD/VCP rows.",
    paperTarget: "Indigenous lexicographic microstructure and citation-density caveats."
  },
  "source-gap-controls": {
    title: "Source gaps, mild drift, and parity controls",
    proves: "Lower-priority rows separate lookup/source gaps and positive parser controls from the highest-risk parser families.",
    doesNotProve: "It does not prove semantic equivalence for parity rows or missing content for source-gap rows.",
    nextDecision: "Use parity rows as controls and inspect source gaps after high-priority parser packets.",
    paperTarget: "R2 rebuild quality controls."
  }
};

export function packetIdForDiagnostic(row) {
  if (row.split === "div") return "div-source-scope";
  if (row.parserFamily === "reverse") return "ae-reverse-bands";
  if (row.parserFamily === "indigenous") return "indigenous-iti-authority";
  if (row.markerRunPrefixMatch || row.sourceRecordExactMatches?.length || row.split === "number-marker" || row.split === "dot-squared") {
    return "marker-run-scope";
  }
  return "source-gap-controls";
}

function compactRow(row) {
  return {
    diagnosticId: row.diagnosticId,
    lemma: row.lemma,
    dict: row.dict,
    parserFamily: row.parserFamily,
    split: row.split,
    driftClass: row.driftClass,
    priority: row.priority,
    sourceSenseRows: row.sourceSenseRows,
    archivedSenseRows: row.archivedSenseRows,
    sourceToArchiveRatio: row.sourceToArchiveRatio,
    sourceRecordCount: row.sourceRecordCount,
    ...(row.sourceRecordExactMatches?.length ? { sourceRecordExactMatches: row.sourceRecordExactMatches } : {}),
    ...(row.markerRunPrefixMatch ? { markerRunPrefixMatch: row.markerRunPrefixMatch } : {}),
    ...(row.markerLabelCounts ? { markerLabelCounts: row.markerLabelCounts } : {}),
    ...(row.markerRunCounts ? { markerRunCounts: row.markerRunCounts } : {}),
    ...(row.reverseRankCounts ? { reverseRankCounts: row.reverseRankCounts } : {}),
    ...(row.indigenousAuthorityHintCounts ? { indigenousAuthorityHintCounts: row.indigenousAuthorityHintCounts } : {}),
    nextAction: row.nextAction
  };
}

function byPriority(a, b) {
  const priorities = { high: 3, medium: 2, low: 1, info: 0 };
  return (priorities[b.priority] ?? 0) - (priorities[a.priority] ?? 0) ||
    Math.abs(b.sourceSenseRows - b.archivedSenseRows) - Math.abs(a.sourceSenseRows - a.archivedSenseRows) ||
    a.lemma.localeCompare(b.lemma) ||
    a.dict.localeCompare(b.dict);
}

function packetRows(diagnostics) {
  const buckets = new Map(Object.keys(PACKET_DEFINITIONS).map(id => [id, []]));
  for (const row of diagnostics) {
    const packetId = packetIdForDiagnostic(row);
    buckets.get(packetId).push(row);
  }
  return [...buckets.entries()].map(([packetId, rows]) => {
    const def = PACKET_DEFINITIONS[packetId];
    const sorted = rows.sort(byPriority);
    return {
      packetId,
      ownerRepo: "csl-atlas",
      title: def.title,
      proves: def.proves,
      doesNotProve: def.doesNotProve,
      nextDecision: def.nextDecision,
      paperDashboardTarget: def.paperTarget,
      counts: {
        diagnosticRows: sorted.length,
        highPriorityRows: sorted.filter(row => row.priority === "high").length,
        mediumPriorityRows: sorted.filter(row => row.priority === "medium").length,
        dictionaryCount: new Set(sorted.map(row => row.dict)).size,
        lemmaCount: new Set(sorted.map(row => row.lemma)).size
      },
      rows: sorted.map(compactRow)
    };
  });
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function validate(payload) {
  const errors = [];
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (!payload.packets.length) errors.push("no packets");
  for (const packet of payload.packets) {
    if (packet.ownerRepo !== "csl-atlas") errors.push(`${packet.packetId}: ownerRepo must be csl-atlas`);
    if (!packet.proves) errors.push(`${packet.packetId}: missing proves`);
    if (!packet.doesNotProve) errors.push(`${packet.packetId}: missing doesNotProve`);
    if (!packet.nextDecision) errors.push(`${packet.packetId}: missing nextDecision`);
  }
  if (errors.length) {
    console.error(`R2 review packets failed with ${errors.length} error(s):`);
    for (const error of errors) console.error(`  - ${error}`);
    process.exit(1);
  }
}

export function buildPayload(diagnosticsPayload) {
  const diagnostics = diagnosticsPayload.diagnostics ?? [];
  const packets = packetRows(diagnostics);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "r2-review-packets",
    claim: "R2 parser diagnostics are grouped into review packets by parser decision.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-r2-review-packets",
    sourceGeneratedBy: diagnosticsPayload.generatedBy,
    sourceFiles: [
      "data/lexico/r2_parser_diagnostics.json",
      "data/lexico/r2_source_anchor_summary.json",
      "data/lexico/r2_source_anchor_senses.jsonl"
    ],
    counts: {
      packetCount: packets.length,
      diagnosticRows: diagnostics.length,
      highPriorityRows: diagnostics.filter(row => row.priority === "high").length,
      mediumPriorityRows: diagnostics.filter(row => row.priority === "medium").length,
      byPacket: countBy(diagnostics, row => packetIdForDiagnostic(row))
    },
    packets,
    limitations: [
      "Packets are work planning aids, not scholar-reviewed sense decisions.",
      "Rows inherit the limitations of the source-backed R2 prototype and recovered archive fixtures.",
      "Exact count matches and prefix matches are scope clues, not automatic filters."
    ],
    boundary: [
      "This artifact uses dictionary source rows and recovered atlas R2 fixtures only.",
      "No DCS, corpus frequency, TEI/OntoLex, FrAC, GitHub, organization-process evidence, runtime LLM, database, or backend input is used."
    ]
  };
  validate(payload);
  return payload;
}

function main() {
  const diagnosticsPayload = JSON.parse(fs.readFileSync(DIAGNOSTICS_PATH, "utf8"));
  const payload = buildPayload(diagnosticsPayload);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT)} (${payload.counts.packetCount} packets).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
