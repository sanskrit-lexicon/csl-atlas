// Build MW Quantitative Depth outputs.
//
// Deterministic pipeline: parse mw.txt, enrich each record, and write compact
// JSON summaries for the Observable pages under src/data/mw/.
//
// Usage: npm run build-mw-depth
// No LLM inference at any stage.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseMwFile, MW_SOURCE } from "./lib/mw-parser.mjs";
import { classifyTypes, ARTICLE_TYPES } from "./lib/mw-classifiers.mjs";
import {
  recordSourceLayers,
  LAYER_ORDER,
  SOURCE_LAYER_ASSUMPTIONS
} from "./lib/mw-source-layers.mjs";
import {
  buildFamilies,
  compoundSegmentCount,
  FAMILY_ASSUMPTIONS
} from "./lib/mw-depth-graph.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "mw");
const EXPECTED_RECORD_COUNT = 286561;
const TOP_FAMILIES = 100;
const EXAMPLES_PER_TYPE = 3;

function sourceDate() {
  try {
    return fs.statSync(MW_SOURCE).mtime.toISOString().slice(0, 10);
  } catch {
    return null;
  }
}

function envelope(extra, { assumptions = [], warnings = [], recordCount }) {
  return {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourcePath: "../csl-orig/v02/mw/mw.txt",
    sourceDate: sourceDate(),
    recordCount,
    assumptions,
    warnings,
    ...extra
  };
}

function writeJson(name, payload) {
  const out = path.join(OUT_DIR, name);
  fs.writeFileSync(out, `${JSON.stringify(payload, null, 2)}\n`);
  return path.relative(process.cwd(), out);
}

function main() {
  const records = parseMwFile();
  const recordCount = records.length;

  // ---- Enrich each record once. ----
  const typeCounts = Object.fromEntries(ARTICLE_TYPES.map(t => [t, 0]));
  const typeExamples = Object.fromEntries(ARTICLE_TYPES.map(t => [t, []]));
  const overlap = new Map(); // "a|b" -> count
  const typeCountHistogram = new Map(); // number of types per record -> count
  const compoundDepthHistogram = new Map();
  const citationBuckets = { "0": 0, "1": 0, "2-3": 0, "4-7": 0, "8-15": 0, "16+": 0 };

  const layerMembership = Object.fromEntries(LAYER_ORDER.map(l => [l, 0]));
  const citationsByLayer = Object.fromEntries(LAYER_ORDER.map(l => [l, 0]));
  const earliestLayerCounts = Object.fromEntries([...LAYER_ORDER, "none"].map(l => [l, 0]));
  const unknownSourceFreq = new Map();
  let totalCitations = 0;

  for (const r of records) {
    const types = classifyTypes(r);
    const layerInfo = recordSourceLayers(r);
    const segCount = compoundSegmentCount(r);

    r.types = types;
    r.citationCount = layerInfo.citationCount;
    r.sourceLayers = layerInfo.sourceLayers;
    r.earliestLayer = layerInfo.earliestLayer;
    r.latestLayer = layerInfo.latestLayer;
    r.compoundSegmentCount = segCount;

    // type counts + examples
    for (const t of types) {
      typeCounts[t] += 1;
      if (typeExamples[t].length < EXAMPLES_PER_TYPE) {
        typeExamples[t].push({ k1: r.k1, L: r.L, pc: r.pc, line: r.startLine, href: r.href });
      }
    }
    // type overlaps (unordered pairs)
    const sortedTypes = [...types].sort();
    for (let i = 0; i < sortedTypes.length; i++) {
      for (let j = i + 1; j < sortedTypes.length; j++) {
        const key = `${sortedTypes[i]}|${sortedTypes[j]}`;
        overlap.set(key, (overlap.get(key) || 0) + 1);
      }
    }
    // histograms
    typeCountHistogram.set(types.length, (typeCountHistogram.get(types.length) || 0) + 1);
    compoundDepthHistogram.set(segCount, (compoundDepthHistogram.get(segCount) || 0) + 1);

    // citations
    const c = layerInfo.citationCount;
    totalCitations += c;
    const bucket = c === 0 ? "0" : c === 1 ? "1" : c <= 3 ? "2-3" : c <= 7 ? "4-7" : c <= 15 ? "8-15" : "16+";
    citationBuckets[bucket] += 1;

    // layers
    for (const l of layerInfo.sourceLayers) {
      if (l in layerMembership) layerMembership[l] += 1;
    }
    earliestLayerCounts[layerInfo.earliestLayer ?? "none"] += 1;
    for (const src of layerInfo.unknownSources) {
      unknownSourceFreq.set(src, (unknownSourceFreq.get(src) || 0) + 1);
    }
  }

  // attribute citations to layers (one pass over records' sources)
  for (const r of records) {
    for (const l of r.sourceLayers) {
      if (l in citationsByLayer) citationsByLayer[l] += 1;
    }
  }

  fs.mkdirSync(OUT_DIR, { recursive: true });
  const written = [];

  // ---- 1. Quantitative summary. ----
  const meanCitations = Number((totalCitations / Math.max(recordCount, 1)).toFixed(3));
  written.push(
    writeJson(
      "mw-quantitative-summary.json",
      envelope(
        {
          totalCitations,
          meanCitationsPerRecord: meanCitations,
          types: ARTICLE_TYPES.map(t => ({
            type: t,
            count: typeCounts[t],
            pct: Number(((100 * typeCounts[t]) / Math.max(recordCount, 1)).toFixed(2)),
            examples: typeExamples[t]
          }))
        },
        {
          recordCount,
          assumptions: [
            "Article types overlap; counts are membership counts, not an exclusive partition.",
            "Grammar types (noun-m/f/n, adjective-mfn, indeclinable) attach only to primary entries and are mutually exclusive by priority m>f>n>mfn>ind."
          ]
        }
      )
    )
  );

  // ---- 2. Type overlaps. ----
  const overlaps = [...overlap.entries()]
    .map(([key, count]) => {
      const [a, b] = key.split("|");
      return { a, b, count };
    })
    .sort((x, y) => y.count - x.count);
  written.push(
    writeJson(
      "mw-type-overlaps.json",
      envelope(
        { typeTotals: typeCounts, overlaps },
        { recordCount, assumptions: ["Overlap counts records sharing both types."] }
      )
    )
  );

  // ---- 3. Depth distribution. ----
  const toSortedPairs = m =>
    [...m.entries()].sort((a, b) => a[0] - b[0]).map(([value, count]) => ({ value, count }));
  written.push(
    writeJson(
      "mw-depth-distribution.json",
      envelope(
        {
          typesPerRecord: toSortedPairs(typeCountHistogram),
          compoundSegmentDistribution: toSortedPairs(compoundDepthHistogram),
          citationCountBuckets: citationBuckets
        },
        {
          recordCount,
          assumptions: [
            "compoundSegmentDistribution counts <k2> segments; segment count 1 means no compound marker."
          ]
        }
      )
    )
  );

  // ---- 4. Deepest families. ----
  const { families, familyCount } = buildFamilies(records, LAYER_ORDER);
  written.push(
    writeJson(
      "mw-deepest-families.json",
      envelope(
        {
          familyCount,
          shown: Math.min(TOP_FAMILIES, families.length),
          families: families.slice(0, TOP_FAMILIES)
        },
        {
          recordCount,
          assumptions: FAMILY_ASSUMPTIONS,
          warnings: ["Family grouping is inferred (evidence level: inferred); verify against source records via the example links."]
        }
      )
    )
  );

  // ---- 5. Source-layer summary. ----
  const topUnknown = [...unknownSourceFreq.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 100)
    .map(([source, count]) => ({ source, count }));
  written.push(
    writeJson(
      "mw-source-layer-summary.json",
      envelope(
        {
          layerOrder: LAYER_ORDER,
          recordsByLayerMembership: layerMembership,
          citationsByLayer,
          distinctUnknownSources: unknownSourceFreq.size,
          topUnknownSources: topUnknown
        },
        {
          recordCount,
          assumptions: SOURCE_LAYER_ASSUMPTIONS,
          warnings: [
            `${unknownSourceFreq.size} distinct source abbreviations are unmapped and resolve to "unknown" (source-layer review queue, UC-DIA-07).`
          ]
        }
      )
    )
  );

  // ---- 6. Diachronic profile. ----
  written.push(
    writeJson(
      "mw-diachronic-profile.json",
      envelope(
        {
          layerOrder: LAYER_ORDER,
          recordsByEarliestLayer: earliestLayerCounts,
          recordsByLayerMembership: layerMembership
        },
        {
          recordCount,
          assumptions: [
            "Layers are coarse buckets for comparison, NOT exact dates.",
            'earliestLayer ignores "unknown" unless it is a record\'s only layer; records with no textual citation are counted as "none".'
          ],
          warnings: ["Diachronic layers are derived/inferred; do not cite as dating evidence."]
        }
      )
    )
  );

  // ---- 7. Validation report (also written by validate script). ----
  const expected = loadExpectedCounts();
  const validation = compareCounts(typeCounts, expected, recordCount);
  written.push(
    writeJson(
      "mw-validation-report.json",
      envelope(
        { ...validation },
        {
          recordCount,
          assumptions: ["Expected counts come from src/data/article-type-counts.json, generated from an earlier mw.txt revision."],
          warnings: validation.warnings
        }
      )
    )
  );

  console.log(`Parsed ${recordCount} MW records. Wrote:`);
  for (const w of written) console.log(`- ${w}`);
  if (validation.warnings.length) {
    console.log(`\n${validation.warnings.length} validation warning(s):`);
    for (const w of validation.warnings) console.log(`  ! ${w}`);
  }
}

export function loadExpectedCounts() {
  const file = path.resolve(process.cwd(), "src", "data", "article-type-counts.json");
  if (!fs.existsSync(file)) return null;
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  return { total: data.total, types: new Map(data.types.map(t => [t.type, t.count])) };
}

export function compareCounts(typeCounts, expected, recordCount) {
  const warnings = [];
  const typeDiffs = [];
  if (expected) {
    for (const t of ARTICLE_TYPES) {
      const mine = typeCounts[t] || 0;
      const exp = expected.types.get(t) ?? 0;
      const diff = mine - exp;
      typeDiffs.push({ type: t, generated: mine, expected: exp, diff });
      if (Math.abs(diff) > Math.max(50, exp * 0.02)) {
        warnings.push(`Type "${t}" diverges: generated ${mine}, expected ${exp} (diff ${diff}).`);
      }
    }
    const recDiff = recordCount - expected.total;
    if (Math.abs(recDiff) > 100) {
      warnings.push(`Record count ${recordCount} is far from expected ${expected.total} (diff ${recDiff}).`);
    }
  } else {
    warnings.push("No expected counts file found; type-count validation skipped.");
  }
  return { expectedSource: "src/data/article-type-counts.json", recordCount, typeDiffs, warnings };
}

// Run only when executed directly (`node scripts/...`), not when imported by tests.
if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
