// MW lexical-family depth graph (conservative heuristic).
//
// Groups records into families by the leading base of <k2>, then computes
// depth metrics. This is an INFERRED layer: there is no explicit derivation
// link in MW markup, so families are approximated by shared base. All
// assumptions are surfaced in the output and metric components are stored
// separately from the sort score.

const COMPOUND_MARKER = /[—\-+]/;

export const FAMILY_ASSUMPTIONS = [
  "Families are grouped by the leading base segment of <k2>; this is an inferred grouping, not an explicit MW derivation link.",
  "compoundSegmentCount counts <k2> segments split on compound markers (em dash, hyphen, plus).",
  "maxFamilyDepth uses compound segment count as a depth proxy; it is not a Paninian derivation depth.",
  "rootCandidate prefers a member tagged genuineroot, else the shortest base member.",
  "depthScore is for ranking only; always read the stored components instead."
];

/** Strip the udatta accent marker and return the leading base of k2. */
export function familyBase(record) {
  const k2 = record.k2 || record.k1 || "";
  const noAccent = k2.replace(/\//g, "");
  const first = noAccent.split(COMPOUND_MARKER)[0];
  return first.trim();
}

export function compoundSegmentCount(record) {
  const k2 = (record.k2 || "").replace(/\//g, "");
  if (!COMPOUND_MARKER.test(k2)) return 1;
  return k2.split(COMPOUND_MARKER).filter(Boolean).length;
}

function layerRank(order, layer) {
  const i = order.indexOf(layer);
  return i === -1 ? order.length : i;
}

/**
 * Build family summaries from enriched records (records must already carry
 * the per-record metrics added by the build script: types, citationCount,
 * sourceLayers, earliestLayer, latestLayer, compoundSegmentCount).
 *
 * @param {object[]} records enriched MW records
 * @param {string[]} layerOrder diachronic layer order for span computation
 * @returns {{families: object[], familyCount: number}}
 */
export function buildFamilies(records, layerOrder) {
  const groups = new Map();
  for (const r of records) {
    const key = familyBase(r);
    if (!key) continue;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(r);
  }

  const families = [];
  for (const [familyKey, members] of groups) {
    if (members.length < 2) continue; // a family needs >1 member

    const rootMember =
      members.find(m => (m.types || []).includes("root")) ||
      [...members].sort((a, b) => (a.k1 || "").length - (b.k1 || "").length)[0];

    const layersPresent = new Set();
    let citationCount = 0;
    let maxCompoundDepth = 0;
    let descendantCount = 0;
    for (const m of members) {
      citationCount += m.citationCount || 0;
      maxCompoundDepth = Math.max(maxCompoundDepth, m.compoundSegmentCount || 1);
      if (m !== rootMember) descendantCount += 1;
      for (const l of m.sourceLayers || []) layersPresent.add(l);
    }

    const chronological = [...layersPresent].filter(l => l !== "unknown");
    const sorted = chronological.sort(
      (a, b) => layerRank(layerOrder, a) - layerRank(layerOrder, b)
    );
    const earliestLayer = sorted[0] ?? null;
    const latestLayer = sorted[sorted.length - 1] ?? null;
    const sourceLayerSpan = sorted.length
      ? layerRank(layerOrder, latestLayer) - layerRank(layerOrder, earliestLayer)
      : 0;

    const maxFamilyDepth = maxCompoundDepth; // depth proxy
    const depthScore =
      maxFamilyDepth * 3 +
      maxCompoundDepth * 2 +
      sourceLayerSpan * 2 +
      Math.log1p(citationCount) +
      Math.log1p(descendantCount);

    const topExamples = [...members]
      .sort(
        (a, b) =>
          (b.compoundSegmentCount || 1) - (a.compoundSegmentCount || 1) ||
          (b.citationCount || 0) - (a.citationCount || 0)
      )
      .slice(0, 5)
      .map(m => ({
        k1: m.k1,
        L: m.L,
        pc: m.pc,
        line: m.startLine,
        href: m.href,
        compoundSegmentCount: m.compoundSegmentCount || 1,
        citationCount: m.citationCount || 0,
        types: m.types || []
      }));

    families.push({
      familyKey,
      rootCandidate: rootMember?.k1 ?? familyKey,
      memberCount: members.length,
      descendantCount,
      maxFamilyDepth,
      maxCompoundDepth,
      sourceLayerSpan,
      earliestLayer,
      latestLayer,
      citationCount,
      depthScore: Number(depthScore.toFixed(4)),
      topExamples
    });
  }

  families.sort((a, b) => b.depthScore - a.depthScore);
  return { families, familyCount: families.length };
}
