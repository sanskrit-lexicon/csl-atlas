// Build ordered, human-facing review worksheets for the rows the auto-triage
// left for a person — the H4 semantic-field packet and the Xref source-check
// packet. Pure: reads the two committed review packets (which already carry the
// source pointers, evidence, and decision vocabularies) and writes two markdown
// worksheets. No csl-orig, no model. Auto-resolved rows are excluded; what's
// left is ordered evidence-first so the clearest decisions come first.
//
// Usage: npm run build-review-worksheets

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = process.cwd();
const H4_PACKET = path.join(ROOT, "data", "lexico", "h4_semantic_field_review_packet.json");
const XREF_PACKET = path.join(ROOT, "data", "lexico", "xref_source_check_packet.json");
const H4_OUT = path.join(ROOT, "docs", "H4_REVIEW_WORKSHEET.md");
const XREF_OUT = path.join(ROOT, "docs", "XREF_REVIEW_WORKSHEET.md");

const readJson = file => JSON.parse(fs.readFileSync(file, "utf8"));
const pct = v => (v == null ? "—" : `${(v * 100).toFixed(1)}%`);
const compact = (s, n = 160) => {
  const t = (s ?? "").replace(/\s+/g, " ").trim();
  return t.length > n ? `${t.slice(0, n)}…` : t;
};

const H4_TYPE_ORDER = [
  "skd-false-low", "ap-ap90-delta", "vcp-high-coverage",
  "specialized-baseline", "index-reverse-control"
];

export function buildH4Worksheet(packet) {
  const rows = packet.sampleRows.filter(row => !row.autoTriage?.resolved);
  const hasLink = row => row.sourcePointers.some(pointer => pointer.href);
  // Evidence signal: a missing SKD entry is a stronger false-low the LOWER the
  // field coverage; an ap-ap90 delta is more salient the bigger the gap; a
  // covered row is more salient the higher the coverage.
  const signal = row => {
    const cov = row.coverage?.coveragePct ?? 0;
    if (row.sampleType === "ap-ap90-delta") return Math.abs(row.coverageDeltaPct ?? 0);
    if (row.sampleType === "skd-false-low") return -cov;
    return cov;
  };
  rows.sort((a, b) =>
    H4_TYPE_ORDER.indexOf(a.sampleType) - H4_TYPE_ORDER.indexOf(b.sampleType)
    || (hasLink(b) - hasLink(a))
    || (signal(b) - signal(a))
    || a.rank - b.rank);

  const lines = [];
  lines.push("# H4 Semantic-Field Review Worksheet");
  lines.push("");
  lines.push(`Date: ${packet.generatedAt.slice(0, 10)} · Source: \`data/lexico/h4_semantic_field_review_packet.json\``);
  lines.push("");
  lines.push(`**${rows.length} rows need human review** (${packet.counts.autoResolved} were auto-resolved and are excluded — see their \`autoTriage\` blocks in the packet). Grouped by sample type; within each, rows with a direct source link first, then by signal strength. Pick one decision per row from its options.`);
  lines.push("");
  let lastType = null, n = 0;
  for (const row of rows) {
    if (row.sampleType !== lastType) {
      lastType = row.sampleType;
      const groupSize = rows.filter(other => other.sampleType === row.sampleType).length;
      lines.push(`## ${row.sampleLabel} — ${groupSize} rows`);
      lines.push("");
    }
    n += 1;
    const link = row.sourcePointers.find(pointer => pointer.href);
    const cov = row.coverage?.coveragePct != null
      ? `field coverage ${pct(row.coverage.coveragePct)} (${row.coverage.coveredLemmas}/${row.coverage.amarLemmas})`
      : "—";
    const delta = row.coverageDeltaPct != null ? `, Δ ${(row.coverageDeltaPct * 100).toFixed(1)}%` : "";
    lines.push(`**${n}. \`${row.lemma}\`** — ${row.field.label} · ${row.dictionary.label} (${row.dictionary.familyLabel})`);
    lines.push(`- Decide: ${row.expectedDecisionLabels.map(label => `\`${label}\``).join(" · ")}`);
    lines.push(`- Q: ${row.reviewQuestion}`);
    lines.push(`- Evidence: ${cov}${delta}${link ? ` · source: [${link.dictionary} L${link.L}](${link.href})` : " · (absence row — no direct headword link)"}`);
    lines.push("");
  }
  return `${lines.join("\n")}\n`;
}

const XREF_SHARED_CORE_LABELS = ["lexical-shared-core", "prefix-convention", "normalization-risk", "too-sparse"];

export function buildXrefWorksheet(packet) {
  const rows = packet.sharedCoreRows.filter(row => !row.autoTriage?.resolved);
  // Rows with the exact shared edge in BOTH dictionaries are decidable from the
  // links; the rows missing an exact edge need a manual source read, so last.
  rows.sort((a, b) =>
    (a.missingExactEdgeDictionaries.length - b.missingExactEdgeDictionaries.length)
    || a.sampleId.localeCompare(b.sampleId));

  const lines = [];
  lines.push("# Xref Source-Check Review Worksheet");
  lines.push("");
  lines.push(`Date: ${packet.generatedAt.slice(0, 10)} · Source: \`data/lexico/xref_source_check_packet.json\``);
  lines.push("");
  lines.push(`**${rows.length} MW/PWG shared-core edges need a source-check** (${packet.counts.autoResolved} prefix-convention rows auto-resolved, excluded). Ordered: rows with the exact shared edge in both dictionaries first; the ${packet.counts.sharedCoreRowsWithMissingExactEdge} rows missing an exact edge are flagged at the end. Pick one label per row.`);
  lines.push("");
  let n = 0;
  for (const row of rows) {
    n += 1;
    lines.push(`**${n}. \`${row.sourceLemma}\` → \`${row.target}\`**`);
    lines.push(`- Decide: ${XREF_SHARED_CORE_LABELS.map(label => `\`${label}\``).join(" · ")}`);
    lines.push(`- Q: ${row.reviewQuestion}`);
    if (row.missingExactEdgeDictionaries.length) {
      lines.push(`- ⚠ Exact edge missing in: ${row.missingExactEdgeDictionaries.join(", ")} — needs a manual source read.`);
    }
    for (const pointer of row.sourcePointers.filter(pointer => pointer.href)) {
      lines.push(`- ${pointer.dictionary} [L${pointer.L}](${pointer.href})${pointer.kind ? ` (${pointer.kind})` : ""}: ${compact(pointer.bodyExcerpt)}`);
    }
    lines.push("");
  }
  return `${lines.join("\n")}\n`;
}

function main() {
  const h4 = readJson(H4_PACKET);
  const xref = readJson(XREF_PACKET);
  fs.writeFileSync(H4_OUT, buildH4Worksheet(h4));
  fs.writeFileSync(XREF_OUT, buildXrefWorksheet(xref));
  console.log(`Wrote ${path.relative(ROOT, H4_OUT)} (${h4.counts.needsHumanReview} rows) and ${path.relative(ROOT, XREF_OUT)} (${xref.counts.needsHumanReview} rows).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
