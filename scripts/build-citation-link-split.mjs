// DTB link-splitting audit — combined <ls> references in MW (review layer).
//
// Month 2, second DTB sub-task (org taxonomy `link-splitting`): split a single
// citation that packs several references (e.g. "SOURCE N; M" or "SOURCE N-M")
// into individual per-locus links.
//
// FINDING (the point of this audit): in Monier-Williams it is a near-empty
// problem. Of ~311,933 <ls> citations only a handful carry a combined-reference
// signal — the Cologne digitizers already atomised citations into one <ls> per
// reference. So link-splitting needs no pipeline; this build quantifies that and
// queues the exceptions for human splitting. Atlas only proposes; csl-corrections
// owns any edit. No model, no network.
//
// Usage: npm run build-citation-link-split.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const MW_SOURCE = path.resolve(process.cwd(), "..", "csl-orig", "v02", "mw", "mw.txt");
const MW_HREF = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt";
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "citation-link-split-review.json");

const LS_RE = /<ls>([^<]*)<\/ls>/gi;
const SEMICOLON = /;/;
const RANGE = /(\d+)\s*[-–]\s*(\d+)/;          // "1-5"
const SEQUENCE = /\bsqq?\.|\bfoll\.|&c\b/i;     // open-ended "and following"
// Leading source siglum, e.g. "Bālar.", "PadmaP., Svargakh." — text before the
// first locus number, used to re-attach the source to inherited sub-references.
const SIGLUM = /^([^0-9]*?[A-Za-zŚṢṬĀĪŪṚṄÑḌḤṂ]\.)\s*/;

function classify(text) {
  if (SEQUENCE.test(text)) return "open-sequence";
  if (SEMICOLON.test(text)) return "semicolon";
  if (RANGE.test(text)) return "range";
  return null;
}

// Best-effort split into individual reference strings (for human review).
function splitRefs(text, kind) {
  const sig = (text.match(SIGLUM) || [, ""])[1].trim();
  if (kind === "semicolon") {
    return text.split(";").map((p, i) => {
      const t = p.trim().replace(/\.$/, "");
      return i === 0 || /[A-Za-z]\./.test(t) ? t : `${sig} ${t}`.trim();
    }).filter(Boolean);
  }
  if (kind === "range") {
    const m = text.match(RANGE);
    const lo = Number(m[1]), hi = Number(m[2]);
    const base = text.slice(0, m.index).trim();
    if (hi > lo && hi - lo <= 50) {
      return Array.from({ length: hi - lo + 1 }, (_, i) => `${base} ${lo + i}`.replace(/,\s*$/, "").trim());
    }
  }
  return [text.trim()]; // open-sequence or un-splittable -> one item, flagged for manual split
}

function main() {
  const lines = fs.readFileSync(MW_SOURCE, "utf8").split(/\r?\n/);
  let total = 0;
  const combined = [];
  const tally = { semicolon: 0, range: 0, "open-sequence": 0 };

  for (let i = 0; i < lines.length; i++) {
    let m;
    LS_RE.lastIndex = 0;
    while ((m = LS_RE.exec(lines[i])) !== null) {
      total += 1;
      const text = m[1].trim();
      const kind = classify(text);
      if (!kind) continue;
      tally[kind] += 1;
      combined.push({ text, kind, line: i + 1 });
    }
  }
  combined.sort((a, b) => a.text.localeCompare(b.text));

  const preserved = loadPreserved(OUTPUT);
  const items = [];
  let preservedCount = 0;
  for (const c of combined) {
    const parts = splitRefs(c.text, c.kind);
    const reviewId = `citation-link-target:split:${c.line}:${c.text}`;
    if (preserved.has(reviewId)) preservedCount += 1;
    items.push({
      reviewId,
      queue: "citation-link-target",
      subject: { kind: "citation", lemma: null, dictionaries: ["MW"] },
      sourcePointers: [{ dictionary: "MW", line: c.line, href: `${MW_HREF}#L${c.line}` }],
      machineValue: {
        citation: c.text,
        splitKind: c.kind,
        splitParts: parts,
        partCount: parts.length,
        verdict: parts.length > 1 ? "split-proposed" : "needs-manual-split"
      },
      evidenceLevel: "derived",
      ...reviewFields(preserved, reviewId)
    });
  }

  const payload = reviewPayload({
    queue: "citation-link-target",
    sourcePath: "../csl-orig/v02/mw/mw.txt (combined <ls> references)",
    items,
    extra: {
      subTask: "link-splitting",
      totalCitations: total,
      combinedCount: combined.length,
      combinedFraction: total ? Number((combined.length / total).toExponential(2)) : 0,
      breakdown: tally,
      finding: "MW <ls> citations are already atomised by the digitizers; link-splitting is a near-empty sub-task."
    },
    assumptions: [
      "Scope: Monier-Williams. A citation is 'combined' if it carries a semicolon, a digit range (N-M), or an open sequence (sq./foll./&c).",
      "splitParts is a best-effort split for human review; inherited sub-refs re-attach the leading source siglum; ranges expand to endpoints (capped at 50).",
      "This proposes splits; it never edits csl-orig. Reviews preserved by reviewId across rebuilds."
    ],
    warnings: [
      `Headline: only ${combined.length} of ${total} MW citations (${total ? (100 * combined.length / total).toExponential(1) : 0}%) are combined — the corpus is already atomised, so link-splitting needs no pipeline, only manual handling of these exceptions.`,
      "Best-effort splits must be verified (e.g. a range may be inclusive vs a span; an open sequence (sq.) has no explicit upper bound).",
      "PWG carries a few more semicolon-combined refs (~4) — extend this scan to PWG/PWK if their link-targets are tackled."
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} link-splitting items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`  combined: ${combined.length} / ${total} MW citations | breakdown: ${JSON.stringify(tally)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
