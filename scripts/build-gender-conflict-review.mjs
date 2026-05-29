// Build the gender-conflict review queue (Phase 2 -> review layer).
//
// Emits review reports conforming to data/schema/review-report.schema.json for
// every cross-dictionary gender disagreement among the grammar-reliable tagged
// dictionaries (MW, AP, PWG, PWK, WIL). This is the first generator that feeds
// the review layer described in docs/REVIEW_REPORTS.md.
//
// CRITICAL: reviews are an overlay. A rebuild MUST NOT discard human decisions.
// Existing items whose reviewStatus is human-set (reviewed-ok, reviewed-corrected,
// blocked, deferred) or which carry a reviewer are preserved by stable reviewId;
// only the machine-derived fields are refreshed.
//
// Usage: npm run build-gender-review. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { DICTS, DICT_LABELS, dictHref } from "./lib/dict-manifest.mjs";
import { iterateDict, dictExists, genderFromLex } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { genderConflict } from "./lib/dict-align.mjs";

const SCHEMA_VERSION = "1.0.0";
// Single source of truth: the review overlay lives where Observable reads it
// (docs/REVIEW_REPORTS.md). Reviewers hand-edit this file; it is regenerated
// with human decisions preserved by reviewId.
const OUTPUTS = [
  path.resolve(process.cwd(), "src", "data", "review", "gender-conflicts-review.json")
];

const TAGGED = DICTS.filter(d => d.grammarReliable).map(d => d.code);
const HUMAN_STATUSES = new Set(["reviewed-ok", "reviewed-corrected", "blocked", "deferred"]);

function loadExistingReviews() {
  const preserved = new Map(); // reviewId -> { reviewStatus, reviewedValue, reviewer, reviewedAt, note }
  for (const out of OUTPUTS) {
    if (!fs.existsSync(out)) continue;
    try {
      const doc = JSON.parse(fs.readFileSync(out, "utf8"));
      for (const item of doc.items || []) {
        const humanReviewed = HUMAN_STATUSES.has(item.reviewStatus) || item.reviewer;
        if (humanReviewed && !preserved.has(item.reviewId)) {
          preserved.set(item.reviewId, {
            reviewStatus: item.reviewStatus,
            reviewedValue: item.reviewedValue ?? null,
            reviewer: item.reviewer ?? null,
            reviewedAt: item.reviewedAt ?? null,
            note: item.note ?? ""
          });
        }
      }
    } catch {
      // ignore malformed prior file; we regenerate machine fields anyway
    }
    break; // both outputs are identical; read the first that exists
  }
  return preserved;
}

function buildTaggedIndex(warnings) {
  const index = new Map(); // normalized -> { code -> { genders:Set, line } }
  for (const code of TAGGED) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; skipped.`);
      continue;
    }
    for (const rec of iterateDict(code)) {
      if (!rec.k1) continue;
      const g = genderFromLex(rec.body);
      if (!g) continue; // only entries that assert a gender/POS matter here
      const { normalized } = normalizeLemma(rec.k1);
      if (!normalized) continue;
      let entry = index.get(normalized);
      if (!entry) {
        entry = {};
        index.set(normalized, entry);
      }
      let slot = entry[code];
      if (!slot) {
        slot = { genders: new Set(), line: rec.startLine };
        entry[code] = slot;
      }
      slot.genders.add(g);
    }
    console.log(`  indexed ${code}`);
  }
  return index;
}

function main() {
  const warnings = [];
  const preserved = loadExistingReviews();
  console.log(`Indexing tagged dictionaries (${TAGGED.map(c => DICT_LABELS[c]).join(", ")})...`);
  const index = buildTaggedIndex(warnings);

  const items = [];
  let preservedCount = 0;
  for (const [lemma, entry] of index) {
    const gc = genderConflict(entry, TAGGED);
    if (!gc.conflict) continue;

    const reviewId = `gender-conflict:${lemma}`;
    const codes = Object.keys(gc.byDict);
    const machineValue = {
      byDict: Object.fromEntries(codes.map(c => [DICT_LABELS[c], gc.byDict[c]]))
    };
    const sourcePointers = codes.map(c => ({
      dictionary: DICT_LABELS[c],
      line: entry[c].line,
      href: dictHref(c, entry[c].line)
    }));

    const carried = preserved.get(reviewId);
    if (carried) preservedCount += 1;

    items.push({
      reviewId,
      queue: "pos-gender-conflict",
      subject: { kind: "alignment", lemma, dictionaries: codes.map(c => DICT_LABELS[c]) },
      sourcePointers,
      machineValue,
      evidenceLevel: "derived",
      reviewStatus: carried?.reviewStatus ?? "needs-review",
      reviewedValue: carried?.reviewedValue ?? null,
      reviewer: carried?.reviewer ?? null,
      reviewedAt: carried?.reviewedAt ?? null,
      note: carried?.note ?? ""
    });
  }

  items.sort((a, b) => a.subject.lemma.localeCompare(b.subject.lemma));

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourcePath: "../csl-orig/v02/{mw,ap,pwg,pw,wil}/*.txt",
    recordCount: items.length,
    queue: "pos-gender-conflict",
    assumptions: [
      "Conflicts are derived from <lex> gender tags in the grammar-reliable tagged dictionaries (MW, AP, PWG, PWK, WIL).",
      "A conflict means two dictionaries assert disjoint specific genders ({m,f,n}); adjective/indeclinable tags never trigger one.",
      "Within-dictionary polysemy (one lemma listed under several genders) does not count as a conflict.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "VCP and SKD encode gender in prose and are excluded.",
      ...warnings
    ],
    items
  };

  for (const out of OUTPUTS) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, `${JSON.stringify(payload, null, 2)}\n`);
  }

  console.log(`\nWrote ${items.length} gender-conflict review items (${preservedCount} human reviews preserved) to:`);
  for (const out of OUTPUTS) console.log(`- ${path.relative(process.cwd(), out)}`);
}

main();
