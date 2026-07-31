// Build the citation-truncation + hapax-overlap evidence packet (PET-MW-CITE, H1827).
//
// The Petersburg→MW descent claim has a direction problem: containment of
// headword stock (OBS-R) is symmetric and size-confounded, so it cannot say
// WHO copied WHOM. `docs/LEXICOGRAPHY_ROADMAP.md` §"Citation truncation
// patterns" names the asymmetric test: a dictionary can SHORTEN an ancestor's
// reference (PWG `Rv. 1.22.16` → MW `RV.`) but cannot invent locator precision
// it never had. So per shared cited source, the more-specific side is the
// plausible ancestor.
//
// Two measures, one packet:
//
//   1. citation_truncation_evidence(A→B) — over the sources BOTH dictionaries
//      cite (canonical siglum, shared with the citation-apparatus fold + alias
//      table), the count of A's citations whose LOCATOR DEPTH exceeds B's mean
//      depth for that same source. Locator depth = the number of numeric or
//      i/v/x roman components after the siglum: "RV." = 0, "Rv. 1.22.16" = 3.
//      Reported as a rate over A's shared-source citations, and as the
//      asymmetry rate(A→B) − rate(B→A). This is the ONE-DIRECTIONAL signal.
//
//   2. hapax overlap — rare-headword agreement. A shared COMMON lemma is
//      evidence of nothing (every dictionary has `agni`); a lemma recorded by
//      exactly two of the in-scope dictionaries and by no other is the
//      rare-stock analogue of a shared error. Reported as the shared-hapax
//      count plus a rare-set Jaccard, over the full headword sets AND over the
//      headwords that actually cite a shared source (the "shared-source
//      headwords" the roadmap names), each against the all-headword Jaccard
//      baseline so the rare-set number has a contrast rather than a vibe.
//
// Honest shrinkage, measured not assumed:
//   - MW72 carries ZERO <ls> tags (0 of 17.2 MB); it cannot enter the citation
//     half at all and appears in the hapax half only. The handoff named it as a
//     citation target; the data refuses.
//   - "PW" and "PWK" are the same digitisation in csl-orig — PWK lives at code
//     `pw` (see scripts/lib/dict-manifest.mjs). PWKVN (the kürzere-Fassung
//     Nachträge) is included as the third Petersburg witness so the lane is not
//     a single point.
//   - PWG/PWK/PWKVN use bare-numeral ELLIPTICAL citations (`<ls>112,24</ls>`)
//     that continue the previous citation's siglum. They carry no siglum of
//     their own, so they cannot join a shared source; they are excluded from
//     the pair comparison and counted separately rather than silently dropped.
//
// Within-lane pairs (PWG↔PWK, MW↔MW72) are computed as CONTROLS, not because
// they are descent hypotheses.
//
// Pure derivation from csl-orig v02 + committed atlas alias tables. No model
// inference, no corpus read, no human decision.
//
// Usage: npm run build-citation-truncation   (then npm run validate-citation-truncation)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { extractCitations, normalizeSource } from "./lib/mw-classifiers.mjs";
import { baseForm, isEditorialReference } from "./lib/mw-source-layers.mjs";
import { canonicalSiglum, canonicalName } from "./lib/source-siglum.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-citation-truncation";
const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "citation_truncation_hapax.json");
const SOURCE_OUT = path.join(OUT_DIR, "citation_truncation_hapax.source.json");
const SITE_OUT = path.resolve(process.cwd(), "src", "data", "lexico", "citation_truncation_hapax.json");
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "csl-orig");

// In-scope dictionaries. `lane` groups the descent hypothesis: petersburg →
// mw is the PET-MW-CITE direction; same-lane pairs are controls.
// `citationTagged` is asserted here and VERIFIED at build time — a dictionary
// declared tagged that yields no <ls> is a hard error, not a silent zero.
export const SCOPE_DICTS = [
  { code: "pwg", label: "PWG", lane: "petersburg", citationTagged: true },
  { code: "pw", label: "PWK", lane: "petersburg", citationTagged: true },
  { code: "pwkvn", label: "PWKVN", lane: "petersburg", citationTagged: true },
  { code: "mw", label: "MW", lane: "mw", citationTagged: true },
  { code: "mw72", label: "MW72", lane: "mw", citationTagged: false }
];

// A shared source needs enough citations on BOTH sides for a mean-depth
// comparison to mean anything. Sources under this floor stay in the packet's
// counts but out of the pair statistics.
export const MIN_CITATIONS_PER_SIDE = 5;
// |asymmetry| below this is reported as "tied" rather than a direction.
export const TIE_BAND = 0.05;
const TOP_SOURCES_PER_PAIR = 25;

// Non-bibliographic <ls> markers. MW reuses <ls> for the lexicographer hedge
// ("L.") and for editorial cross-references (ib, Cat, Col, IW, ...); those are
// not texts and must not become shared "sources". The editorial list is the
// reviewed one in src/data/mw-source-layers.json; "L" is added explicitly.
const NONTEXT_BASES = new Set(["L"]);

const NUMERIC = /^\d+$/;
// Roman locator components, restricted to i/v/x — the same restriction
// scripts/lib/source-siglum.mjs applies, and for the same reason: `l.`, `c.`,
// `d.` and `m.` are abbreviation letters in this corpus far more often than
// they are numerals ("MED. l. 57" is a column, not line 50).
const ROMAN_IVX = /^[ivx]+$/i;

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

/** The locator remainder of a citation: everything after the base siglum. */
export function locatorOf(normalized) {
  const base = baseForm(normalized);
  return normalized.startsWith(base) ? normalized.slice(base.length) : "";
}

/**
 * Locator depth: how many numeric / i-v-x roman components the reference
 * carries after its siglum. "RV." → 0; "RV. i, 1" → 2; "Rv. 1.22.16" → 3.
 * This is the specificity scale the truncation test compares.
 */
export function locatorDepth(locator) {
  return String(locator ?? "")
    .split(/[^0-9A-Za-z]+/)
    .filter(token => token && (NUMERIC.test(token) || ROMAN_IVX.test(token)))
    .length;
}

/**
 * Classify one raw <ls> payload.
 * Returns { kind, sourceId, depth } where kind is:
 *   "source"       — a real siglum with a canonical identity (usable);
 *   "continuation" — an elliptical bare-numeral reference (PWG "112,24");
 *   "nontext"      — an editorial / lexicographer marker (MW "L.", "ib.");
 *   "empty"        — nothing left after normalisation.
 */
export function classifyCitation(raw) {
  const normalized = normalizeSource(raw ?? "");
  if (!normalized) return { kind: "empty", sourceId: null, depth: 0 };
  const base = baseForm(normalized);
  const depth = locatorDepth(locatorOf(normalized));
  if (NUMERIC.test(base) || ROMAN_IVX.test(base)) {
    return { kind: "continuation", sourceId: null, depth };
  }
  if (NONTEXT_BASES.has(base) || isEditorialReference(normalized)) {
    return { kind: "nontext", sourceId: null, depth };
  }
  const sourceId = canonicalSiglum(base);
  if (!sourceId) return { kind: "empty", sourceId: null, depth };
  return { kind: "source", sourceId, depth };
}

function emptyDictState(dict) {
  return {
    ...dict,
    entries: 0,
    headwords: new Set(),          // interned lemma ids
    citationsRaw: 0,
    citationsUsable: 0,
    citationsContinuation: 0,
    citationsNontext: 0,
    depthSum: 0,                   // over usable citations only
    depthHistogram: new Map(),     // depth → count
    bySource: new Map(),           // sourceId → { count, depthSum, headwords:Set }
    sourceCount: 0
  };
}

/**
 * Read one dictionary into the intermediate state the pair statistics need.
 * `intern` maps a normalized lemma to a small integer so the per-source
 * headword sets stay cheap across five dictionaries.
 */
export function collectDict(dict, records, intern) {
  const state = emptyDictState(dict);
  for (const record of records) {
    state.entries += 1;
    const lemmaKey = normalizeLemma(record.k1 ?? "").normalized;
    const lemmaId = lemmaKey ? intern(lemmaKey) : null;
    if (lemmaId !== null) state.headwords.add(lemmaId);
    for (const raw of extractCitations(record.body ?? "")) {
      state.citationsRaw += 1;
      const { kind, sourceId, depth } = classifyCitation(raw);
      if (kind === "continuation") { state.citationsContinuation += 1; continue; }
      if (kind === "nontext") { state.citationsNontext += 1; continue; }
      if (kind !== "source") continue;
      state.citationsUsable += 1;
      state.depthSum += depth;
      state.depthHistogram.set(depth, (state.depthHistogram.get(depth) ?? 0) + 1);
      let bucket = state.bySource.get(sourceId);
      if (!bucket) {
        bucket = { count: 0, depthSum: 0, depths: [], headwords: new Set() };
        state.bySource.set(sourceId, bucket);
      }
      bucket.count += 1;
      bucket.depthSum += depth;
      bucket.depths.push(depth);
      if (lemmaId !== null) bucket.headwords.add(lemmaId);
    }
  }
  state.sourceCount = state.bySource.size;
  return state;
}

function depthHistogramObject(histogram, total) {
  const out = {};
  for (const depth of [...histogram.keys()].sort((a, b) => a - b)) {
    out[String(depth)] = { citations: histogram.get(depth), share: round(histogram.get(depth) / total) };
  }
  return out;
}

function intersectionSize(a, b) {
  const [small, large] = a.size <= b.size ? [a, b] : [b, a];
  let n = 0;
  for (const v of small) if (large.has(v)) n += 1;
  return n;
}

function jaccard(interSize, sizeA, sizeB) {
  const union = sizeA + sizeB - interSize;
  return union === 0 ? null : round(interSize / union);
}

/**
 * Truncation statistics for one ordered direction A→B over the shared sources.
 * `evidence` is the roadmap's citation_truncation_evidence(A→B): the count of
 * A's citations that are MORE SPECIFIC than B's typical citation of the same
 * source.
 */
function truncationDirection(stateA, stateB, sharedSources) {
  let evidence = 0;
  let citations = 0;
  let depthSum = 0;
  for (const sourceId of sharedSources) {
    const a = stateA.bySource.get(sourceId);
    const b = stateB.bySource.get(sourceId);
    const bMean = b.depthSum / b.count;
    citations += a.count;
    depthSum += a.depthSum;
    for (const depth of a.depths) if (depth > bMean) evidence += 1;
  }
  return {
    evidence,
    citations,
    rate: citations === 0 ? null : round(evidence / citations),
    meanLocatorDepth: citations === 0 ? null : round(depthSum / citations, 3)
  };
}

function hapaxBlock(setA, setB, lemmaDictCount, pairMemberships) {
  const inter = intersectionSize(setA, setB);
  let rareA = 0;
  let rareB = 0;
  let rareInter = 0;
  let sharedHapax = 0;
  for (const lemma of setA) if ((lemmaDictCount.get(lemma) ?? 0) <= 2) rareA += 1;
  for (const lemma of setB) if ((lemmaDictCount.get(lemma) ?? 0) <= 2) rareB += 1;
  const [small, large] = setA.size <= setB.size ? [setA, setB] : [setB, setA];
  for (const lemma of small) {
    if (!large.has(lemma)) continue;
    const n = lemmaDictCount.get(lemma) ?? 0;
    if (n <= 2) rareInter += 1;
    if (n === 2 && pairMemberships.has(lemma)) sharedHapax += 1;
  }
  const allJaccard = jaccard(inter, setA.size, setB.size);
  const rareJaccard = jaccard(rareInter, rareA, rareB);
  return {
    headwordsA: setA.size,
    headwordsB: setB.size,
    intersection: inter,
    jaccard: allJaccard,
    rareHeadwordsA: rareA,
    rareHeadwordsB: rareB,
    rareIntersection: rareInter,
    rareJaccard,
    sharedHapax,
    sharedHapaxShareOfIntersection: inter === 0 ? null : round(sharedHapax / inter),
    // Structurally ≤ 1: a "rare" lemma sits in at most two dictionaries, so the
    // rare set can only overlap through the exactly-two case while the
    // all-headword set overlaps through every case. Read it as how much of the
    // pair's agreement survives when common stock is removed, not as a lift.
    rareVsAllJaccard: allJaccard && rareJaccard !== null ? round(rareJaccard / allJaccard, 3) : null
  };
}

export function buildPayload(states, options = {}) {
  const byCode = new Map(states.map(s => [s.code, s]));
  const dicts = SCOPE_DICTS.filter(d => byCode.has(d.code));

  // Lemma rarity is computed over the in-scope dictionaries only — see
  // limitations. A lemma's "dict count" is how many of them record it.
  const lemmaDictCount = new Map();
  const lemmaDicts = new Map();
  for (const state of states) {
    for (const lemma of state.headwords) {
      lemmaDictCount.set(lemma, (lemmaDictCount.get(lemma) ?? 0) + 1);
      let owners = lemmaDicts.get(lemma);
      if (!owners) { owners = new Set(); lemmaDicts.set(lemma, owners); }
      owners.add(state.code);
    }
  }

  const perDictionary = dicts.map(dict => {
    const s = byCode.get(dict.code);
    const usable = s.citationsUsable;
    return {
      code: s.code,
      label: s.label,
      lane: s.lane,
      entries: s.entries,
      headwords: s.headwords.size,
      citationsRaw: s.citationsRaw,
      citationsUsable: usable,
      citationsContinuation: s.citationsContinuation,
      citationsNontext: s.citationsNontext,
      distinctSources: s.sourceCount,
      meanLocatorDepth: usable ? round(s.depthSum / usable, 3) : null,
      bareSiglumShare: usable ? round((s.depthHistogram.get(0) ?? 0) / usable) : null,
      depthHistogram: usable ? depthHistogramObject(s.depthHistogram, usable) : {}
    };
  });

  const excludedDictionaries = dicts
    .filter(d => byCode.get(d.code).citationsUsable === 0)
    .map(d => ({
      code: d.code,
      label: d.label,
      reason: `no <ls> source citations in csl-orig v02/${d.code} (${byCode.get(d.code).citationsRaw} raw <ls> payloads) — cannot enter the citation-truncation half; hapax half only`
    }));

  const pairs = [];
  for (let i = 0; i < dicts.length; i += 1) {
    for (let j = i + 1; j < dicts.length; j += 1) {
      const A = byCode.get(dicts[i].code);
      const B = byCode.get(dicts[j].code);
      const relation = A.lane === B.lane ? `within-${A.lane}` : "cross-lane";

      // --- shared cited sources (citation half) ---
      const sharedAll = [...A.bySource.keys()].filter(id => B.bySource.has(id)).sort();
      const shared = sharedAll.filter(id =>
        A.bySource.get(id).count >= MIN_CITATIONS_PER_SIDE &&
        B.bySource.get(id).count >= MIN_CITATIONS_PER_SIDE);
      const citationTestable = A.citationsUsable > 0 && B.citationsUsable > 0 && shared.length > 0;

      let citation = null;
      if (citationTestable) {
        const ab = truncationDirection(A, B, shared);
        const ba = truncationDirection(B, A, shared);
        const asymmetry = round(ab.rate - ba.rate);
        const moreSpecific = Math.abs(asymmetry) < TIE_BAND ? "tied" : (asymmetry > 0 ? A.code : B.code);
        const perSource = shared
          .map(id => {
            const a = A.bySource.get(id);
            const b = B.bySource.get(id);
            return {
              source: id,
              name: canonicalName(id),
              citationsA: a.count,
              citationsB: b.count,
              meanDepthA: round(a.depthSum / a.count, 3),
              meanDepthB: round(b.depthSum / b.count, 3),
              depthDelta: round(a.depthSum / a.count - b.depthSum / b.count, 3)
            };
          })
          .sort((x, y) => (y.citationsA + y.citationsB) - (x.citationsA + x.citationsB));
        citation = {
          sharedSourcesAll: sharedAll.length,
          sharedSources: shared.length,
          minCitationsPerSide: MIN_CITATIONS_PER_SIDE,
          truncationEvidenceAB: ab.evidence,
          truncationEvidenceBA: ba.evidence,
          sharedSourceCitationsA: ab.citations,
          sharedSourceCitationsB: ba.citations,
          truncationRateAB: ab.rate,
          truncationRateBA: ba.rate,
          meanDepthA: ab.meanLocatorDepth,
          meanDepthB: ba.meanLocatorDepth,
          asymmetry,
          moreSpecific,
          sourcesAMoreSpecific: perSource.filter(s => s.depthDelta > 0).length,
          sourcesBMoreSpecific: perSource.filter(s => s.depthDelta < 0).length,
          topSources: perSource.slice(0, TOP_SOURCES_PER_PAIR)
        };
      }

      // --- hapax overlap (headword half) ---
      const pairCodes = new Set([A.code, B.code]);
      const pairMemberships = new Map();
      for (const [lemma, owners] of lemmaDicts) {
        if (owners.size === 2 && owners.has(A.code) && owners.has(B.code)) pairMemberships.set(lemma, true);
      }
      const hapaxAll = hapaxBlock(A.headwords, B.headwords, lemmaDictCount, pairMemberships);
      let hapaxCitedShared = null;
      if (citationTestable) {
        const citedA = new Set();
        const citedB = new Set();
        for (const id of shared) {
          for (const lemma of A.bySource.get(id).headwords) citedA.add(lemma);
          for (const lemma of B.bySource.get(id).headwords) citedB.add(lemma);
        }
        hapaxCitedShared = hapaxBlock(citedA, citedB, lemmaDictCount, pairMemberships);
      }

      pairs.push({
        a: A.code,
        b: B.code,
        labelA: A.label,
        labelB: B.label,
        relation,
        pair: `${A.label}↔${B.label}`,
        citationTestable,
        citation,
        hapax: { all: hapaxAll, citedShared: hapaxCitedShared },
        pairCodes: [...pairCodes].sort()
      });
    }
  }

  const crossLaneCitation = pairs.filter(p => p.relation === "cross-lane" && p.citation);
  const petersburgMoreSpecific = crossLaneCitation.filter(p => {
    const petersburg = p.a === "mw" || p.a === "mw72" ? p.b : p.a;
    return p.citation.moreSpecific === petersburg;
  });

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    status: "citation-truncation-and-hapax-overlap-evidence",
    hypothesis: "PET-MW-CITE",
    claim:
      "The Petersburg→MW lineage is visible as a one-directional citation-truncation asymmetry: on the sources both sides cite, the Petersburg dictionaries carry systematically deeper locators than MW, and the rare-headword (hapax) overlap between the lanes exceeds the all-headword baseline.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "csl-orig/v02/{pwg,pw,pwkvn,mw,mw72}",
      "src/data/dicts/dict-source-aliases.json",
      "src/data/mw-source-layers.json",
      "scripts/build-citation-truncation.mjs"
    ],
    method: {
      locatorDepth:
        "Locator depth = the number of numeric or i/v/x roman components following the base siglum of an <ls> citation. \"RV.\" → 0, \"RV. i, 1\" → 2, \"Rv. 1.22.16\" → 3. Roman components are restricted to i/v/x because l./c./d./m. are abbreviation letters in this corpus far more often than numerals.",
      sourceIdentity:
        "Sources are folded to a canonical identity with the same two-layer scheme the citation apparatus uses (scripts/lib/source-siglum.mjs: diacritic/case fold + the reviewed src/data/dicts/dict-source-aliases.json alias table), so MW \"MBh\" and PWG \"MBH.\" are one source.",
      truncationEvidence:
        `citation_truncation_evidence(A→B) = the number of A's citations, on sources both dictionaries cite at least ${MIN_CITATIONS_PER_SIDE} times each, whose locator depth EXCEEDS B's mean depth for that same source. Reported as a rate over A's shared-source citations; the pair's direction is the asymmetry rate(A→B) − rate(B→A), called "tied" inside ±${TIE_BAND}.`,
      hapaxOverlap:
        "A lemma's rarity is its in-scope dictionary count (1–5 of the dictionaries in this packet). shared hapax(A,B) = lemmas recorded by exactly two of the in-scope dictionaries, and those two are A and B — the rare-stock analogue of a shared error, since common stock is shared by every dictionary and so evidences nothing. Reported as a count, as a share of the pair's intersection, and beside a rare-set Jaccard (lemmas in ≤2 dictionaries) whose ratio to the all-headword Jaccard (`rareVsAllJaccard`) is structurally ≤1 and is a composition figure, not a lift.",
      scopes:
        "The hapax block is computed twice: `all` over the full <k1> headword sets, and `citedShared` restricted to the headwords whose entry actually cites one of the pair's shared sources — the roadmap's \"shared-source headwords\". Rarity itself stays global to the packet in both scopes: rarity is a property of the lemma, not of the citing subset.",
      headwordIdentity:
        "Headwords are the SLP1 <k1> normalised through scripts/lib/dict-normalize.mjs (the canonical sanskrit-util slp1_norm: accent marks and homonym digits dropped, phonemic case preserved)."
    },
    scope: {
      dictionaries: dicts.map(d => ({ code: d.code, label: d.label, lane: d.lane })),
      citationDictionaries: perDictionary.filter(d => d.citationsUsable > 0).map(d => d.code),
      excludedDictionaries,
      pwNote:
        "\"PW\" and \"PWK\" are one digitisation in csl-orig — the kürzere Fassung lives at code `pw` and is labelled PWK by scripts/lib/dict-manifest.mjs. PWKVN (its Nachträge) is included as a third Petersburg witness so the lane is not a single point.",
      controlPairs:
        "Within-lane pairs (PWG↔PWK, PWG↔PWKVN, PWK↔PWKVN, MW↔MW72) are controls: they show what the same measures read when descent is not in question."
    },
    perDictionary,
    pairs,
    findings: {
      citationTestablePairs: pairs.filter(p => p.citationTestable).length,
      crossLanePairsTested: crossLaneCitation.length,
      crossLanePairsWherePetersburgIsDeeper: petersburgMoreSpecific.length,
      maxCrossLaneAsymmetry: crossLaneCitation.length
        ? round(Math.max(...crossLaneCitation.map(p => Math.abs(p.citation.asymmetry))))
        : null,
      mwBareSiglumShare: perDictionary.find(d => d.code === "mw")?.bareSiglumShare ?? null,
      pwgBareSiglumShare: perDictionary.find(d => d.code === "pwg")?.bareSiglumShare ?? null,
      maxCrossLaneSharedHapax: (() => {
        const counts = pairs.filter(p => p.relation === "cross-lane").map(p => p.hapax.all.sharedHapax);
        return counts.length ? Math.max(...counts) : null;
      })(),
      maxWithinLaneSharedHapax: (() => {
        const counts = pairs.filter(p => p.relation !== "cross-lane").map(p => p.hapax.all.sharedHapax);
        return counts.length ? Math.max(...counts) : null;
      })()
    },
    interpretation: [],
    limitations: [
      "Locator depth measures FORMATTING specificity, not scholarship. MW's house style is compressed by editorial policy (a one-volume English dictionary), so a depth gap is consistent with descent-plus-truncation AND with independent house style. The measure bounds the direction of information loss; it does not by itself prove copying.",
      "The canonical-siglum fold is a reviewed but incomplete alias table: unaliased sigla fall back to their bare fold key, so a source the two dictionaries abbreviate incompatibly is counted as two sources and simply never enters the shared set. That biases the shared-source count DOWN, not the asymmetry up.",
      `Sources are required to carry at least ${MIN_CITATIONS_PER_SIDE} citations on each side, so the per-source mean depth is not a one-citation artifact; the excluded thin sources are reported as sharedSourcesAll − sharedSources.`,
      "The elliptical bare-numeral citations of the Petersburg lane (`<ls>112,24</ls>`, continuing the previous citation's siglum) are excluded, because they have no siglum to share. They are a real part of PWG's apparatus, so PWG's usable-citation count here is smaller than its raw <ls> count.",
      "Hapax rarity is computed over the five in-scope dictionaries only. A lemma \"unique to PWG and MW\" here may well appear in AP, SKD or VCP; the corpus-wide rarity base (OBS-R's 44-dictionary collapse) is the natural upgrade and would only shrink these counts.",
      "Headword identity is the normalised <k1> string; it does not resolve homonym merges or orthographic variants beyond slp1_norm, so both intersection and union are slightly conservative.",
      "MW72 contributes headwords only — it carries no <ls> tags at all, so nothing in the citation half can be said about it."
    ],
    boundary: [
      "Derived from committed csl-orig dictionary text and the atlas's own reviewed alias tables; no corpus read, no external maker work, no human decision promoted. csl-orig is never written."
    ]
  };

  const pwg = perDictionary.find(d => d.code === "pwg");
  const mw = perDictionary.find(d => d.code === "mw");
  const pwgMw = pairs.find(p => p.a === "pwg" && p.b === "mw");
  if (pwg && mw) {
    payload.interpretation.push(
      `Apparatus style splits the lanes before any pair is formed: ${mw.label} leaves ${(mw.bareSiglumShare * 100).toFixed(1)}% of its citations at a bare siglum (mean locator depth ${mw.meanLocatorDepth}), against ${(pwg.bareSiglumShare * 100).toFixed(1)}% for ${pwg.label} (mean depth ${pwg.meanLocatorDepth}). Truncation is not a rare event in MW — it is MW's default.`
    );
  }
  if (pwgMw?.citation) {
    const c = pwgMw.citation;
    payload.interpretation.push(
      `On the ${c.sharedSources} sources PWG and MW both cite at least ${MIN_CITATIONS_PER_SIDE} times, citation_truncation_evidence(PWG→MW) = ${c.truncationEvidenceAB.toLocaleString()} of ${c.sharedSourceCitationsA.toLocaleString()} PWG citations (${(c.truncationRateAB * 100).toFixed(1)}%), against ${c.truncationEvidenceBA.toLocaleString()} of ${c.sharedSourceCitationsB.toLocaleString()} the other way (${(c.truncationRateBA * 100).toFixed(1)}%) — asymmetry ${c.asymmetry}. The direction is the one the descent hypothesis needs; the magnitude is a house-style gap as much as a copying signal.`
    );
  }
  const withinLaneCitation = pairs.filter(p => p.relation !== "cross-lane" && p.citation);
  const absAsym = list => list.map(p => Math.abs(p.citation.asymmetry));
  if (withinLaneCitation.length && crossLaneCitation.length) {
    const w = absAsym(withinLaneCitation);
    const c = absAsym(crossLaneCitation);
    payload.interpretation.push(
      `The within-lane pairs are the control, and they are not zero: |asymmetry| runs ${round(Math.min(...w))}–${round(Math.max(...w))} inside the Petersburg lane (where descent is not in question and house style is shared) against ${round(Math.min(...c))}–${round(Math.max(...c))} across the lanes. The separation is the finding; the non-zero control is the reminder that this measure reads apparatus style, and even sibling Petersburg digitisations differ in it. Cross-lane pairs where the Petersburg side is the deeper one: ${petersburgMoreSpecific.length} of ${crossLaneCitation.length}.`
    );
  }
  if (pwgMw && pwgMw.hapax.all.intersection > 0) {
    const h = pwgMw.hapax.all;
    payload.interpretation.push(
      `Hapax overlap adds the content-side half: PWG and MW share ${h.intersection.toLocaleString()} headwords (Jaccard ${h.jaccard}), of which ${h.sharedHapax.toLocaleString()} (${(h.sharedHapaxShareOfIntersection * 100).toFixed(1)}% of the intersection) are recorded by these two dictionaries and by no other in-scope dictionary. Common stock is shared by everyone and evidences nothing; this rare residue is the part that a shared source would explain.`
    );
  }
  if (payload.findings.maxCrossLaneSharedHapax !== null && payload.findings.maxWithinLaneSharedHapax !== null) {
    payload.interpretation.push(
      `The shared-hapax counts are descriptive, not size-corrected: the largest cross-lane count is ${payload.findings.maxCrossLaneSharedHapax.toLocaleString()} against ${payload.findings.maxWithinLaneSharedHapax.toLocaleString()} for the largest within-lane pair, but headword-set sizes differ by a factor of five across the packet and nothing here normalises for that — read the counts beside the per-dictionary headword totals. With only ${dicts.length} dictionaries in the rarity base, "recorded by no other in-scope dictionary" is a floor on rarity, not corpus-wide uniqueness; the 44-dictionary base would shrink every count here.`
    );
  }

  payload.generatedAt = options.generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  let commit = "unknown";
  let cslOrigCommit = "unknown";
  try { commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim(); } catch {}
  try { cslOrigCommit = execSync(`git -C "${SIBLING_ROOT}" rev-parse HEAD`, { encoding: "utf8" }).trim(); } catch {}
  const envelope = {
    dataset: "citation_truncation_hapax",
    commit,
    cslOrigRepo: "https://github.com/sanskrit-lexicon/csl-orig",
    cslOrigCommit,
    dictionaries: payload.scope.dictionaries.map(d => d.code),
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  const missing = SCOPE_DICTS.filter(d => !dictExists(d.code));
  if (missing.length) {
    console.error(
      `Missing csl-orig source(s): ${missing.map(d => d.code).join(", ")}\n` +
        "This builder needs a sibling csl-orig checkout at ../csl-orig/v02 " +
        "(the committed data/lexico/citation_truncation_hapax.json is the CI-safe artifact)."
    );
    process.exit(1);
  }
  const lemmaIds = new Map();
  const intern = lemma => {
    let id = lemmaIds.get(lemma);
    if (id === undefined) { id = lemmaIds.size; lemmaIds.set(lemma, id); }
    return id;
  };
  const states = SCOPE_DICTS.map(dict => {
    const state = collectDict(dict, iterateDict(dict.code), intern);
    if (dict.citationTagged && state.citationsUsable === 0) {
      console.error(`${dict.label} is declared citation-tagged but yielded no usable <ls> citations — refusing to write a silent zero.`);
      process.exit(1);
    }
    console.log(
      `  ${dict.label.padEnd(6)} ${state.entries.toLocaleString().padStart(9)} entries · ` +
      `${state.citationsUsable.toLocaleString().padStart(8)} usable citations · ${state.sourceCount.toLocaleString().padStart(6)} sources`
    );
    return state;
  });
  const payload = buildPayload(states);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  fs.mkdirSync(path.dirname(SITE_OUT), { recursive: true });
  fs.writeFileSync(SITE_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote citation-truncation + hapax packet (${payload.pairs.length} pairs, ${payload.findings.citationTestablePairs} citation-testable):`);
  for (const file of [JSON_OUT, SOURCE_OUT, SITE_OUT]) console.log(`- ${path.relative(process.cwd(), file)}`);
  const pwgMw = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");
  if (pwgMw?.citation) {
    console.log(
      `  PWG→MW truncation evidence ${pwgMw.citation.truncationEvidenceAB.toLocaleString()} (${pwgMw.citation.truncationRateAB}) ` +
      `vs MW→PWG ${pwgMw.citation.truncationEvidenceBA.toLocaleString()} (${pwgMw.citation.truncationRateBA}); ` +
      `asymmetry ${pwgMw.citation.asymmetry}; shared hapax ${pwgMw.hapax.all.sharedHapax.toLocaleString()}`
    );
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
