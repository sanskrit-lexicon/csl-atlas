// Build the citation-apparatus comparison (Phase 2, UC-CD-07 / UC-LX-06).
//
// Compares how the dictionaries cite sources: citation density per entry,
// distinct source abbreviations, the shared source vocabulary (a source x
// dictionary matrix), and pairwise source-set overlap. Source-level comparison
// covers the <ls>-tagged dictionaries (MW, AP, PWG, PWK); WIL is essentially
// untagged and VCP/SKD cite in prose via `iti`, so for those only a density
// proxy is reported.
//
// Usage: npm run build-citation-apparatus. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { DICTS, DICT_LABELS } from "./lib/dict-manifest.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { extractCitations, normalizeSource } from "./lib/mw-classifiers.mjs";
import { baseForm } from "./lib/mw-source-layers.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const TOP_SOURCES = 60;

const TAGGED = DICTS.filter(d => d.citationTagged).map(d => d.code);

function analyse(code, tagged) {
  let recordCount = 0;
  let recordsWithCitations = 0;
  let totalCitations = 0;
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
        // Reduce to the base sigla so loci don't fragment a source:
        // "MBh. iii,5" -> "MBh", "P. 1,1,14" -> "P".
        const s = baseForm(normalizeSource(c));
        if (s) sources.set(s, (sources.get(s) || 0) + 1);
      }
    } else {
      // prose citation proxy: count `iti` formulae
      const n = (body.match(/\biti\b/g) || []).length;
      if (n) recordsWithCitations += 1;
      totalCitations += n;
    }
  }

  return { recordCount, recordsWithCitations, totalCitations, sources };
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

  // Per-dictionary apparatus: density, breadth, and each dictionary's own
  // top sources. Cross-dictionary source alignment is deliberately NOT done
  // here — see the deferred note below.
  const perDict = DICTS.filter(d => perDictRaw[d.code]).map(d => {
    const r = perDictRaw[d.code];
    const topSources = d.citationTagged
      ? [...r.sources.entries()].sort((a, b) => b[1] - a[1]).slice(0, TOP_SOURCES)
          .map(([source, count]) => ({ source, count }))
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

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    citationTaggedDicts: TAGGED.map(c => DICT_LABELS[c]),
    perDict,
    assumptions: [
      "Source-level comparison covers the <ls>-tagged dictionaries (MW, AP, PWG, PWK).",
      "citationsPerRecord uses <ls> count for tagged dicts and `iti` count for prose dicts (VCP, SKD); the two methods are not directly comparable.",
      "WIL is essentially untagged for citations (<ls> almost absent), so its density is near zero by encoding, not by content.",
      "Source strings are reduced to base sigla (locus/book detail stripped): 'MBh. iii,5' -> 'MBh', 'P. 1,1,14' -> 'P'.",
      "Each dictionary's topSources are its OWN sigla; counts are not aligned across dictionaries (see deferred note).",
      "Editorial and cross-reference markers (ib., W., etc.) are counted; they are part of the apparatus."
    ],
    deferred: [
      "Cross-dictionary source alignment (a shared source x dictionary matrix and source-set overlap) is NOT computed: dictionaries use different siglum conventions (MW 'MBh' vs PWG 'MBH', 'RV' vs 'ṚV'), so naive matching is wrong. It needs a reviewed cross-dictionary siglum-mapping table — a scholarly task tracked for a later slice."
    ],
    warnings
  };

  fs.writeFileSync(path.join(OUT_DIR, "citation-apparatus.json"), `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`\nWrote citation apparatus for ${perDict.length} dictionaries to:`);
  console.log(`- ${path.relative(process.cwd(), path.join(OUT_DIR, "citation-apparatus.json"))}`);
}

main();
