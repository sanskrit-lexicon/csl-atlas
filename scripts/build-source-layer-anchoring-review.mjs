// Build the source-layer anchoring review queue (review layer).
//
// Calibrates the atlas's coarse MW source LAYERS (vedic, epic, classical,
// puranic, technical, lexicographic) against the Dharmamitra Sanskrit Dating
// chronology snapshot (src/data/external/dharmamitra-chronology.json). For each
// layer it proposes an EMPIRICAL date band derived from the dated works in the
// mapped Dharmamitra era(s) — turning "coarse bucket" into "coarse bucket that
// empirically spans these years per Dharmamitra", for a human to ratify before
// the atlas ever cites a date.
//
// Deliberately NOT a per-siglum join: MW <ls> sigla are abbreviations and the
// chronology is keyed by work title, so siglum-level matching would be fuzzy
// and low-yield. The layer<->era crosswalk below is small, explicit, and
// reviewable; ambiguous mappings are flagged crosswalkConfidence="judgment".
//
// The chronology is a probabilistic model output: this queue is review
// EVIDENCE, never a silent input to the deterministic build, and it never
// rewrites src/data/mw-source-layers.json. See docs/DHARMAMITRA_INTEGRATION.md.
//
// Usage: npm run build-source-layer-anchoring-review. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const CHRONOLOGY = path.resolve(process.cwd(), "src", "data", "external", "dharmamitra-chronology.json");
const LAYERS = path.resolve(process.cwd(), "src", "data", "mw-source-layers.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "source-layer-anchoring-review.json");

// Explicit, reviewable crosswalk: atlas source layer -> Dharmamitra era key(s).
// "high" = the layer and era denote the same canon; "judgment" = a defensible
// but arguable span the reviewer should confirm.
const CROSSWALK = {
  vedic: { eras: ["vedic"], confidence: "high" },
  epic: { eras: ["epic-sutra"], confidence: "high" },
  classical: { eras: ["classical"], confidence: "high" },
  puranic: { eras: ["early-medieval"], confidence: "judgment" },
  technical: { eras: ["epic-sutra", "classical"], confidence: "judgment" },
  lexicographic: { eras: ["late-medieval"], confidence: "high" }
  // "unknown" has no chronological anchor by definition -> no proposal.
};

const SOURCE_POINTER = {
  dictionary: "Dharmamitra Sanskrit Dating",
  line: null,
  href: "https://dharmamitra.github.io/sanskrit-dating/sanskrit_chronology_interactive.html"
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function quantile(sortedAsc, q) {
  if (sortedAsc.length === 0) return null;
  const pos = (sortedAsc.length - 1) * q;
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  if (lo === hi) return sortedAsc[lo];
  return Math.round(sortedAsc[lo] + (sortedAsc[hi] - sortedAsc[lo]) * (pos - lo));
}

function main() {
  const chronology = readJson(CHRONOLOGY);
  const layersDoc = readJson(LAYERS);
  const warnings = [];

  // Index chronology works by era key, anchors only (reliable dates).
  const anchorsByEra = new Map();
  for (const w of chronology.works) {
    if (w.source !== "anchor" || !Number.isFinite(w.postMedian)) continue;
    if (!anchorsByEra.has(w.eraKey)) anchorsByEra.set(w.eraKey, []);
    anchorsByEra.get(w.eraKey).push(w);
  }

  const preserved = loadPreserved(OUTPUT);
  const items = [];
  let preservedCount = 0;

  for (const layer of layersDoc.layerOrder) {
    const cw = CROSSWALK[layer];
    if (!cw) continue; // unknown / unmapped layers get no chronological proposal

    const works = cw.eras.flatMap(era => anchorsByEra.get(era) ?? []);
    const dates = works.map(w => w.postMedian).sort((a, b) => a - b);

    let dateBand = null;
    let exemplars = [];
    if (dates.length) {
      dateBand = {
        lo: dates[0],
        p10: quantile(dates, 0.10),
        median: quantile(dates, 0.50),
        p90: quantile(dates, 0.90),
        hi: dates[dates.length - 1]
      };
      // Three works nearest the median, for a human sanity check.
      const median = dateBand.median;
      exemplars = [...works]
        .sort((a, b) => Math.abs(a.postMedian - median) - Math.abs(b.postMedian - median))
        .slice(0, 3)
        .map(w => ({ title: w.title, postMedian: w.postMedian }));
    } else {
      warnings.push(`Layer "${layer}" mapped to era(s) ${cw.eras.join("/")} but no anchor works matched.`);
    }

    const reviewId = `source-layer-anchoring:${layer}`;
    if (preserved.has(reviewId)) preservedCount += 1;

    items.push({
      reviewId,
      queue: "source-layer-anchoring",
      subject: { kind: "source-layer", lemma: null, dictionaries: ["MW"] },
      sourcePointers: [SOURCE_POINTER],
      machineValue: {
        atlasLayer: layer,
        dharmamitraEras: cw.eras,
        crosswalkConfidence: cw.confidence,
        anchorWorkCount: works.length,
        dateBand,
        exemplars
      },
      evidenceLevel: "inferred", // dates are probabilistic model output
      ...reviewFields(preserved, reviewId)
    });
  }

  const payload = reviewPayload({
    queue: "source-layer-anchoring",
    sourcePath: "src/data/mw-source-layers.json + src/data/external/dharmamitra-chronology.json",
    items,
    extra: {
      chronology: { generatedAt: chronology.generatedAt, workCount: chronology.workCount },
      crosswalk: CROSSWALK
    },
    assumptions: [
      "Date bands are computed over Dharmamitra ANCHOR works only (externally-dated), not inferred ones.",
      "The atlas layer <-> Dharmamitra era crosswalk is explicit and small; crosswalkConfidence flags arguable mappings.",
      "Years are CE; negative = BCE. A band describes the spread of cited-work dates in a layer, not a single layer date.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "Dharmamitra dates are posterior model estimates, not established facts; ratify before the atlas cites any band.",
      "This queue never rewrites mw-source-layers.json; it proposes external date evidence for the existing coarse layers.",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} source-layer anchoring items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  for (const it of items) {
    const b = it.machineValue.dateBand;
    console.log(`  ${it.machineValue.atlasLayer.padEnd(14)} ${it.machineValue.anchorWorkCount.toString().padStart(4)} anchors  ${b ? `band ${b.lo}..${b.hi} (median ${b.median})` : "no match"}`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
