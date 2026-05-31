// Build the citation-apparatus comparison (Phase 2, UC-CD-07 / UC-LX-06).
//
// Compares how the dictionaries cite sources: citation density per entry,
// apparatus breadth, each dictionary's most-cited sources, and — using the
// cross-dictionary canonical siglum (fold + reviewed alias table) — a shared
// source x dictionary matrix and pairwise source overlap.
//
// Source-level comparison covers the <ls>-tagged dictionaries (MW, AP, PWG,
// PWK). WIL is essentially untagged and VCP/SKD cite in prose via `iti`, so
// for those only a density proxy is reported.
//
// Usage: npm run build-citation-apparatus. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { DICTS, DICT_LABELS } from "./lib/dict-manifest.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { extractCitations, normalizeSource } from "./lib/mw-classifiers.mjs";
import { baseForm } from "./lib/mw-source-layers.mjs";
import { canonicalSiglum, canonicalName } from "./lib/source-siglum.mjs";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const REVIEW_OUT = path.resolve(process.cwd(), "src", "data", "review", "source-siglum-review.json");
const TOP_SOURCES = 60;
// A single-dictionary source siglum cited at least this often is a candidate
// for the cross-dictionary alias table (it may equal another dict's siglum).
const ALIAS_REVIEW_MIN = 100;

const TAGGED = DICTS.filter(d => d.citationTagged).map(d => d.code);

function analyse(code, tagged) {
  let recordCount = 0;
  let recordsWithCitations = 0;
  let totalCitations = 0;
  // canonical id -> { count, forms: Map<rawBaseForm, count> }
  const sources = new Map();

  for (const rec of iterateDict(code)) {
    if (!rec.k1) continue;
    recordCount += 1;
    const body = rec.body || "";
    if (tagged) {
      const cites = extractCitations(body);
      if (cites.length) recordsWithCitations += 1;
      totalCitations += cites.length;
      for (const c of cites) {
        const form = baseForm(normalizeSource(c)); // strip locus: "MBh. iii,5" -> "MBh"
        if (!form) continue;
        const id = canonicalSiglum(form); // fold + alias: "MBh"/"MBH" -> "mbh"
        let s = sources.get(id);
        if (!s) {
          s = { count: 0, forms: new Map(), href: rec.href };
          sources.set(id, s);
        }
        s.count += 1;
        s.forms.set(form, (s.forms.get(form) || 0) + 1);
      }
    } else {
      const n = (body.match(/\biti\b/g) || []).length;
      if (n) recordsWithCitations += 1;
      totalCitations += n;
    }
  }
  return { recordCount, recordsWithCitations, totalCitations, sources };
}

// Most frequent raw form for a canonical id within one dictionary.
export function topForm(sourceEntry) {
  let best = null;
  let bestN = -1;
  for (const [form, n] of sourceEntry.forms) {
    if (n > bestN) {
      best = form;
      bestN = n;
    }
  }
  return best;
}

function displayLabel(id, perDictRaw) {
  const named = canonicalName(id);
  if (named) return named;
  // otherwise show the most frequent raw form seen in any tagged dictionary
  let best = null;
  let bestN = -1;
  for (const code of TAGGED) {
    const e = perDictRaw[code]?.sources.get(id);
    if (e && e.count > bestN) {
      best = topForm(e);
      bestN = e.count;
    }
  }
  return best ?? id;
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const warnings = [];
  const perDictRaw = {};

  for (const d of DICTS) {
    if (!dictExists(d.code)) {
      warnings.push(`Missing source for ${d.code}; skipped.`);
      continue;
    }
    perDictRaw[d.code] = analyse(d.code, d.citationTagged);
    console.log(`  ${d.code}: ${perDictRaw[d.code].totalCitations} citations (${d.citationTagged ? "ls" : "iti"})`);
  }

  // Per-dictionary apparatus.
  const perDict = DICTS.filter(d => perDictRaw[d.code]).map(d => {
    const r = perDictRaw[d.code];
    const topSources = d.citationTagged
      ? [...r.sources.entries()].sort((a, b) => b[1].count - a[1].count).slice(0, TOP_SOURCES)
          .map(([id, e]) => ({ source: canonicalName(id) ?? topForm(e), count: e.count }))
      : [];
    return {
      dict: d.label,
      method: d.citationTagged ? "ls" : "iti",
      recordCount: r.recordCount,
      recordsWithCitations: r.recordsWithCitations,
      totalCitations: r.totalCitations,
      citationsPerRecord: r.recordCount ? Number((r.totalCitations / r.recordCount).toFixed(3)) : 0,
      distinctSources: d.citationTagged ? r.sources.size : null,
      topSources
    };
  });

  // Cross-dictionary source x dictionary matrix (canonical sigla).
  const totals = new Map();
  for (const code of TAGGED) {
    if (!perDictRaw[code]) continue;
    for (const [id, e] of perDictRaw[code].sources) totals.set(id, (totals.get(id) || 0) + e.count);
  }
  const taggedPresent = TAGGED.filter(c => perDictRaw[c]);
  const sourceMatrix = [...totals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, TOP_SOURCES)
    .map(([id, total]) => ({
      source: displayLabel(id, perDictRaw),
      total,
      dictsCiting: taggedPresent.filter(c => perDictRaw[c].sources.has(id)).length,
      byDict: Object.fromEntries(taggedPresent.map(c => [DICT_LABELS[c], perDictRaw[c].sources.get(id)?.count || 0]))
    }));

  // Pairwise canonical source-set overlap (Jaccard).
  const sourceOverlap = [];
  for (let i = 0; i < taggedPresent.length; i++) {
    for (let j = i + 1; j < taggedPresent.length; j++) {
      const a = new Set(perDictRaw[taggedPresent[i]].sources.keys());
      const b = new Set(perDictRaw[taggedPresent[j]].sources.keys());
      let shared = 0;
      for (const s of a) if (b.has(s)) shared += 1;
      const union = a.size + b.size - shared;
      sourceOverlap.push({
        a: DICT_LABELS[taggedPresent[i]],
        b: DICT_LABELS[taggedPresent[j]],
        sharedSources: shared,
        jaccard: union ? Number((shared / union).toFixed(4)) : 0
      });
    }
  }
  sourceOverlap.sort((x, y) => y.sharedSources - x.sharedSources);

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    citationTaggedDicts: TAGGED.map(c => DICT_LABELS[c]),
    perDict,
    sourceMatrix,
    sourceOverlap,
    assumptions: [
      "Source-level comparison covers the <ls>-tagged dictionaries (MW, AP, PWG, PWK).",
      "citationsPerRecord uses <ls> count for tagged dicts and `iti` count for prose dicts (VCP, SKD); the two methods are not directly comparable.",
      "WIL is essentially untagged for citations (<ls> almost absent), so its density is near zero by encoding, not by content.",
      "Sigla are reduced to base form (loci stripped: 'MBh. iii,5' -> 'MBh') then canonicalized across dictionaries by diacritic/case fold plus the reviewed alias table src/data/dict-source-aliases.json.",
      "The fold aligns MBh/MBH and RV/ṚV automatically; abbreviation-scheme differences (BhP vs Bhāg) need an alias entry. Unaliased differences still under-count cross-dictionary overlap — see the source-siglum review queue."
    ],
    warnings
  };

  fs.writeFileSync(path.join(OUT_DIR, "citation-apparatus.json"), `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`\nWrote citation apparatus for ${perDict.length} dictionaries to:`);
  console.log(`- ${path.relative(process.cwd(), path.join(OUT_DIR, "citation-apparatus.json"))}`);

  writeSiglumReviewQueue(perDictRaw);
}

// Review queue (UC source-siglum-alias): high-frequency canonical sigla cited
// by exactly one tagged dictionary. A reviewer decides whether each is genuinely
// unique to that dictionary or equals another dictionary's siglum under a
// different abbreviation scheme (then adds an entry to dict-source-aliases.json).
function writeSiglumReviewQueue(perDictRaw) {
  const present = TAGGED.filter(c => perDictRaw[c]);
  // canonical id -> [{code, entry}]
  const byId = new Map();
  for (const code of present) {
    for (const [id, e] of perDictRaw[code].sources) {
      if (!byId.has(id)) byId.set(id, []);
      byId.get(id).push({ code, e });
    }
  }

  const preserved = loadPreserved(REVIEW_OUT);
  let preservedCount = 0;
  const items = [];
  for (const [id, hits] of byId) {
    if (hits.length !== 1) continue; // only single-dictionary sigla are alias candidates
    const { code, e } = hits[0];
    if (e.count < ALIAS_REVIEW_MIN) continue;
    const reviewId = `source-siglum-alias:${id}`;
    if (preserved.has(reviewId)) preservedCount += 1;
    items.push({
      reviewId,
      queue: "source-siglum-alias",
      subject: { kind: "source-abbreviation", source: topForm(e), canonicalId: id },
      sourcePointers: [{ dictionary: DICT_LABELS[code], href: e.href }],
      machineValue: { siglum: topForm(e), citedOnlyBy: DICT_LABELS[code], citations: e.count },
      evidenceLevel: "derived",
      ...reviewFields(preserved, reviewId)
    });
  }
  items.sort((a, b) => b.machineValue.citations - a.machineValue.citations);

  const payload = reviewPayload({
    queue: "source-siglum-alias",
    sourcePath: "../csl-orig/v02/{mw,ap,pwg,pw}/*.txt",
    items,
    extra: { minCitations: ALIAS_REVIEW_MIN },
    assumptions: [
      `A candidate is a canonical siglum cited only by one tagged dictionary and at least ${ALIAS_REVIEW_MIN} times.`,
      "It may be genuinely unique to that dictionary, or equal another dictionary's siglum under a different scheme.",
      "To merge it, add an alias entry to src/data/dict-source-aliases.json; it then aligns and leaves this queue.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: ["Sigla already aligned by the diacritic/case fold are not listed; only scheme-level differences remain."]
  });
  writeReport(REVIEW_OUT, payload);
  console.log(`Wrote ${items.length} source-siglum-alias review items (${preservedCount} preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), REVIEW_OUT)}`);
}

// Run only when executed directly, not when imported by tests.
if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
