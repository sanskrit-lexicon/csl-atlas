// MW source-layer classifier.
//
// Maps a record's <ls> citations to coarse diachronic layers using the
// reviewable seed map in src/data/mw-source-layers.json. Conservative by
// design: unmapped sources become "unknown" and are reported for review.

import fs from "node:fs";
import path from "node:path";
import { extractCitations, normalizeSource } from "./mw-classifiers.mjs";

const MAP_FILE = path.resolve(process.cwd(), "src", "data", "mw-source-layers.json");

const data = JSON.parse(fs.readFileSync(MAP_FILE, "utf8"));
const SOURCE_MAP = new Map(Object.entries(data.map));
const EDITORIAL = new Set(data.editorialReferences ?? []);

export const LAYER_ORDER = data.layerOrder;
export const SOURCE_LAYER_ASSUMPTIONS = data.assumptions ?? [];

/**
 * Reduce a citation to its base sigla by dropping a trailing book/section
 * reference or editorial tail, e.g. "MBh. i" -> "MBh", "ŚBr. xiv" -> "ŚBr",
 * "Yājñ., Sch" -> "Yājñ". Returns the original string when there is no tail.
 */
export function baseForm(normalized) {
  const base = normalized.split(/[.,]/)[0].trim();
  return base.length ? base : normalized;
}

/** Layer for one normalized source abbreviation. */
export function layerForSource(normalized) {
  if (SOURCE_MAP.has(normalized)) return SOURCE_MAP.get(normalized);
  const base = baseForm(normalized);
  if (base !== normalized && SOURCE_MAP.has(base)) return SOURCE_MAP.get(base);
  return "unknown";
}

export function isEditorialReference(normalized) {
  return EDITORIAL.has(normalized) || EDITORIAL.has(baseForm(normalized));
}

function layerRank(layer) {
  const i = LAYER_ORDER.indexOf(layer);
  return i === -1 ? LAYER_ORDER.length : i;
}

/**
 * Compute source-layer metrics for one parsed record.
 * Returns layers present, span (excluding "unknown" unless it is the only
 * layer), and the list of unmapped sources for review.
 */
export function recordSourceLayers(record) {
  const citations = extractCitations(record.body || "");
  const normalized = citations.map(normalizeSource);

  const layers = new Set();
  const unknownSources = new Set();
  for (const src of normalized) {
    if (isEditorialReference(src)) continue; // not a textual witness
    const layer = layerForSource(src);
    layers.add(layer);
    if (layer === "unknown") unknownSources.add(src);
  }

  // Chronological span ignores "unknown" unless it is the only layer.
  const chronological = [...layers].filter(l => l !== "unknown");
  const spanLayers = chronological.length ? chronological : [...layers];
  const sorted = [...spanLayers].sort((a, b) => layerRank(a) - layerRank(b));
  const earliestLayer = sorted[0] ?? null;
  const latestLayer = sorted[sorted.length - 1] ?? null;
  const sourceLayerSpan = chronological.length
    ? layerRank(latestLayer) - layerRank(earliestLayer)
    : 0;

  return {
    citationCount: citations.length,
    sourceLayers: [...layers],
    sourceLayerCount: layers.size,
    earliestLayer,
    latestLayer,
    sourceLayerSpan,
    unknownSources: [...unknownSources]
  };
}
