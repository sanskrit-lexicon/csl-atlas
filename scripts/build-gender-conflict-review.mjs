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

import path from "node:path";
import { DICTS, DICT_LABELS, dictHref } from "./lib/dict-manifest.mjs";
import { iterateDict, dictExists, genderForDict } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { genderConflict } from "./lib/dict-align.mjs";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

// The review overlay lives where Observable reads it (docs/REVIEW_REPORTS.md).
// Reviewers hand-edit this file; it is regenerated with human decisions
// preserved by reviewId.
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "gender-conflicts-review.json");

// All gender-bearing dictionaries: <lex> for the tagged set, prose markers for VCP/SKD.
const GENDER_DICTS = DICTS.map(d => d.code);

function buildGenderIndex(warnings) {
  const index = new Map(); // normalized -> { code -> { genders:Set, line } }
  for (const code of GENDER_DICTS) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; skipped.`);
      continue;
    }
    for (const rec of iterateDict(code)) {
      if (!rec.k1) continue;
      const g = genderForDict(code, rec.body);
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
  const preserved = loadPreserved(OUTPUT);
  console.log(`Indexing gender-bearing dictionaries (${GENDER_DICTS.map(c => DICT_LABELS[c]).join(", ")})...`);
  const index = buildGenderIndex(warnings);

  const items = [];
  let preservedCount = 0;
  for (const [lemma, entry] of index) {
    const gc = genderConflict(entry, GENDER_DICTS);
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

    if (preserved.has(reviewId)) preservedCount += 1;

    items.push({
      reviewId,
      queue: "pos-gender-conflict",
      subject: { kind: "alignment", lemma, dictionaries: codes.map(c => DICT_LABELS[c]) },
      sourcePointers,
      machineValue,
      evidenceLevel: "derived",
      ...reviewFields(preserved, reviewId)
    });
  }

  items.sort((a, b) => a.subject.lemma.localeCompare(b.subject.lemma));

  const payload = reviewPayload({
    queue: "pos-gender-conflict",
    sourcePath: "../csl-orig/v02/{mw,ap,pwg,pw,wil,vcp,skd}/*.txt",
    items,
    assumptions: [
      "Gender is from <lex> for the tagged dictionaries (MW, AP, PWG, PWK, WIL) and from prose markers for VCP and SKD.",
      "A conflict means two dictionaries assert disjoint specific genders ({m,f,n}); adjective/indeclinable tags never trigger one.",
      "Within-dictionary polysemy (one lemma listed under several genders) does not count as a conflict.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "VCP prose markers under-mark feminine/neuter at the anchor position, so some VCP f/n genders are absent (missed conflicts, never false ones).",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`\nWrote ${items.length} gender-conflict review items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
}

main();
