// Validate the committed citation-truncation + hapax packet (PET-MW-CITE, H1827).
//
// CI-safe: every structural check runs from the committed JSON alone. The live
// cross-check against csl-orig runs only when that sibling checkout is present
// (it is not on CI runners), and re-derives ONE small dictionary (PWKVN, ~25k
// entries) rather than the whole 150 MB scope, so the validator stays usable
// interactively.
//
// Fails (exit 1) when:
// - the packet or its provenance envelope is missing / unparseable / mismatched;
// - a per-dictionary row's citation counts or depth histogram don't add up;
// - a dictionary declared citation-tagged in the packet has zero usable
//   citations, or an excluded dictionary has some (the MW72 shrinkage must stay
//   honest in both directions);
// - a pair is missing, duplicated, or names a dictionary outside the scope;
// - a pair's truncation evidence exceeds its citation count, its rate
//   disagrees with evidence/citations, or its asymmetry disagrees with the two
//   rates;
// - a pair's `moreSpecific` verdict disagrees with the sign of its asymmetry
//   and the tie band;
// - sharedSources exceeds sharedSourcesAll, or a top-source row falls below the
//   per-side citation floor;
// - a hapax block's intersection exceeds either headword set, its Jaccard
//   disagrees with the sets, or sharedHapax exceeds the intersection;
// - (sibling present) a live re-derivation of PWKVN disagrees with the
//   committed row.
//
// Usage: npm run validate-citation-truncation   (run after build-citation-truncation)

import fs from "node:fs";
import path from "node:path";
import { SCOPE_DICTS, MIN_CITATIONS_PER_SIDE, TIE_BAND, collectDict } from "./build-citation-truncation.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "citation_truncation_hapax.json");
const SOURCE_OUT = path.join(OUT_DIR, "citation_truncation_hapax.source.json");
const SITE_OUT = path.resolve(process.cwd(), "src", "data", "lexico", "citation_truncation_hapax.json");
const LIVE_CHECK_DICT = "pwkvn";

const errors = [];
const notes = [];

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON: ${path.relative(process.cwd(), file)} (${e.message})`);
    return null;
  }
}

function close(a, b, tolerance = 0.0002) {
  return Math.abs(a - b) <= tolerance;
}

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);
const siteCopy = readJson(SITE_OUT);

if (packet && siteCopy && JSON.stringify(packet) !== JSON.stringify(siteCopy)) {
  errors.push("src/data/lexico/citation_truncation_hapax.json differs from the canonical data/lexico copy — re-run the builder");
}

if (packet && envelope) {
  if (envelope.dataset !== "citation_truncation_hapax") errors.push(`envelope.dataset is "${envelope.dataset}"`);
  if (envelope.generatedAt !== packet.generatedAt) {
    errors.push(`envelope.generatedAt ${envelope.generatedAt} != packet.generatedAt ${packet.generatedAt}`);
  }
  if (envelope.schemaVersion !== packet.schemaVersion) {
    errors.push(`envelope.schemaVersion ${envelope.schemaVersion} != packet.schemaVersion ${packet.schemaVersion}`);
  }
}

if (packet) {
  const scopeCodes = new Set(SCOPE_DICTS.map(d => d.code));
  const byCode = new Map((packet.perDictionary ?? []).map(d => [d.code, d]));

  for (const code of scopeCodes) {
    if (!byCode.has(code)) errors.push(`perDictionary is missing scope dictionary "${code}"`);
  }

  for (const d of packet.perDictionary ?? []) {
    if (!scopeCodes.has(d.code)) errors.push(`perDictionary has out-of-scope dictionary "${d.code}"`);
    const accounted = d.citationsUsable + d.citationsContinuation + d.citationsNontext;
    if (accounted > d.citationsRaw) {
      errors.push(`${d.code}: usable+continuation+nontext ${accounted} exceeds raw <ls> count ${d.citationsRaw}`);
    }
    const histTotal = Object.values(d.depthHistogram ?? {}).reduce((sum, row) => sum + row.citations, 0);
    if (histTotal !== d.citationsUsable) {
      errors.push(`${d.code}: depthHistogram sums to ${histTotal}, citationsUsable is ${d.citationsUsable}`);
    }
    for (const [depth, row] of Object.entries(d.depthHistogram ?? {})) {
      if (!close(row.share, row.citations / d.citationsUsable)) {
        errors.push(`${d.code}: depthHistogram[${depth}].share ${row.share} != ${row.citations}/${d.citationsUsable}`);
      }
    }
    if (d.citationsUsable > 0) {
      const bare = d.depthHistogram?.["0"]?.citations ?? 0;
      if (!close(d.bareSiglumShare, bare / d.citationsUsable)) {
        errors.push(`${d.code}: bareSiglumShare ${d.bareSiglumShare} != ${bare}/${d.citationsUsable}`);
      }
      if (d.distinctSources <= 0) errors.push(`${d.code}: has usable citations but distinctSources ${d.distinctSources}`);
    }
    if (d.headwords > d.entries) errors.push(`${d.code}: ${d.headwords} distinct headwords exceeds ${d.entries} entries`);
  }

  // The honest-shrinkage contract, checked in both directions.
  const excluded = new Set((packet.scope?.excludedDictionaries ?? []).map(d => d.code));
  const declaredCitation = new Set(packet.scope?.citationDictionaries ?? []);
  for (const d of packet.perDictionary ?? []) {
    if (d.citationsUsable === 0 && !excluded.has(d.code)) {
      errors.push(`${d.code}: zero usable citations but not listed in scope.excludedDictionaries`);
    }
    if (d.citationsUsable > 0 && excluded.has(d.code)) {
      errors.push(`${d.code}: listed as excluded but has ${d.citationsUsable} usable citations`);
    }
    if ((d.citationsUsable > 0) !== declaredCitation.has(d.code)) {
      errors.push(`${d.code}: scope.citationDictionaries membership disagrees with citationsUsable ${d.citationsUsable}`);
    }
  }

  // Pair coverage: every unordered pair of scope dictionaries, exactly once.
  const seen = new Set();
  for (const p of packet.pairs ?? []) {
    const key = [p.a, p.b].sort().join("|");
    if (seen.has(key)) errors.push(`duplicate pair ${key}`);
    seen.add(key);
    if (!scopeCodes.has(p.a) || !scopeCodes.has(p.b)) errors.push(`pair ${key} names an out-of-scope dictionary`);
  }
  const expectedPairs = (scopeCodes.size * (scopeCodes.size - 1)) / 2;
  if (seen.size !== expectedPairs) errors.push(`expected ${expectedPairs} pairs, packet has ${seen.size}`);

  for (const p of packet.pairs ?? []) {
    const key = `${p.a}↔${p.b}`;
    const a = byCode.get(p.a);
    const b = byCode.get(p.b);
    const bothTagged = (a?.citationsUsable ?? 0) > 0 && (b?.citationsUsable ?? 0) > 0;
    if (p.citationTestable && !bothTagged) errors.push(`${key}: citationTestable but a side has no usable citations`);
    if (p.citationTestable !== Boolean(p.citation)) errors.push(`${key}: citationTestable ${p.citationTestable} but citation block ${p.citation ? "present" : "absent"}`);

    if (p.citation) {
      const c = p.citation;
      if (c.sharedSources > c.sharedSourcesAll) {
        errors.push(`${key}: sharedSources ${c.sharedSources} exceeds sharedSourcesAll ${c.sharedSourcesAll}`);
      }
      if (c.minCitationsPerSide !== MIN_CITATIONS_PER_SIDE) {
        errors.push(`${key}: minCitationsPerSide ${c.minCitationsPerSide} != builder constant ${MIN_CITATIONS_PER_SIDE}`);
      }
      if (c.truncationEvidenceAB > c.sharedSourceCitationsA) {
        errors.push(`${key}: truncationEvidenceAB ${c.truncationEvidenceAB} exceeds sharedSourceCitationsA ${c.sharedSourceCitationsA}`);
      }
      if (c.truncationEvidenceBA > c.sharedSourceCitationsB) {
        errors.push(`${key}: truncationEvidenceBA ${c.truncationEvidenceBA} exceeds sharedSourceCitationsB ${c.sharedSourceCitationsB}`);
      }
      if (!close(c.truncationRateAB, c.truncationEvidenceAB / c.sharedSourceCitationsA)) {
        errors.push(`${key}: truncationRateAB ${c.truncationRateAB} disagrees with ${c.truncationEvidenceAB}/${c.sharedSourceCitationsA}`);
      }
      if (!close(c.truncationRateBA, c.truncationEvidenceBA / c.sharedSourceCitationsB)) {
        errors.push(`${key}: truncationRateBA ${c.truncationRateBA} disagrees with ${c.truncationEvidenceBA}/${c.sharedSourceCitationsB}`);
      }
      if (!close(c.asymmetry, c.truncationRateAB - c.truncationRateBA)) {
        errors.push(`${key}: asymmetry ${c.asymmetry} != rateAB - rateBA`);
      }
      const expectedVerdict = Math.abs(c.asymmetry) < TIE_BAND ? "tied" : (c.asymmetry > 0 ? p.a : p.b);
      if (c.moreSpecific !== expectedVerdict) {
        errors.push(`${key}: moreSpecific "${c.moreSpecific}" disagrees with asymmetry ${c.asymmetry} (expected "${expectedVerdict}")`);
      }
      if (c.sourcesAMoreSpecific + c.sourcesBMoreSpecific > c.sharedSources) {
        errors.push(`${key}: sourcesAMoreSpecific + sourcesBMoreSpecific exceeds sharedSources ${c.sharedSources}`);
      }
      if (c.topSources.length > c.sharedSources) errors.push(`${key}: more topSources than sharedSources`);
      for (const s of c.topSources) {
        if (s.citationsA < MIN_CITATIONS_PER_SIDE || s.citationsB < MIN_CITATIONS_PER_SIDE) {
          errors.push(`${key}: top source "${s.source}" is below the ${MIN_CITATIONS_PER_SIDE}-citation floor (${s.citationsA}/${s.citationsB})`);
        }
        if (!close(s.depthDelta, s.meanDepthA - s.meanDepthB, 0.002)) {
          errors.push(`${key}: top source "${s.source}" depthDelta ${s.depthDelta} != meanDepthA - meanDepthB`);
        }
      }
      for (let i = 1; i < c.topSources.length; i += 1) {
        const prev = c.topSources[i - 1];
        const cur = c.topSources[i];
        if (prev.citationsA + prev.citationsB < cur.citationsA + cur.citationsB) {
          errors.push(`${key}: topSources are not sorted by combined citation count`);
          break;
        }
      }
    }

    for (const [scope, h] of Object.entries(p.hapax ?? {})) {
      if (!h) continue;
      const label = `${key} hapax.${scope}`;
      if (h.intersection > Math.min(h.headwordsA, h.headwordsB)) {
        errors.push(`${label}: intersection ${h.intersection} exceeds the smaller headword set`);
      }
      const union = h.headwordsA + h.headwordsB - h.intersection;
      if (union > 0 && !close(h.jaccard, h.intersection / union)) {
        errors.push(`${label}: jaccard ${h.jaccard} disagrees with ${h.intersection}/${union}`);
      }
      if (h.rareIntersection > h.intersection) errors.push(`${label}: rareIntersection exceeds intersection`);
      if (h.rareHeadwordsA > h.headwordsA || h.rareHeadwordsB > h.headwordsB) {
        errors.push(`${label}: rare headword count exceeds the headword set`);
      }
      if (h.sharedHapax > h.rareIntersection) {
        errors.push(`${label}: sharedHapax ${h.sharedHapax} exceeds rareIntersection ${h.rareIntersection}`);
      }
      if (h.intersection > 0 && !close(h.sharedHapaxShareOfIntersection, h.sharedHapax / h.intersection)) {
        errors.push(`${label}: sharedHapaxShareOfIntersection disagrees with sharedHapax/intersection`);
      }
    }
  }

  if (!packet.limitations?.length) errors.push("packet carries no limitations");
  if (!packet.interpretation?.length) errors.push("packet carries no interpretation");
  if (packet.hypothesis !== "PET-MW-CITE") errors.push(`hypothesis is "${packet.hypothesis}", expected PET-MW-CITE`);
}

// --- live cross-check (skipped without a sibling csl-orig checkout) ---
if (packet && dictExists(LIVE_CHECK_DICT)) {
  const dict = SCOPE_DICTS.find(d => d.code === LIVE_CHECK_DICT);
  const lemmaIds = new Map();
  const intern = lemma => {
    let id = lemmaIds.get(lemma);
    if (id === undefined) { id = lemmaIds.size; lemmaIds.set(lemma, id); }
    return id;
  };
  const live = collectDict(dict, iterateDict(LIVE_CHECK_DICT), intern);
  const committed = packet.perDictionary.find(d => d.code === LIVE_CHECK_DICT);
  const checks = [
    ["entries", live.entries, committed.entries],
    ["headwords", live.headwords.size, committed.headwords],
    ["citationsUsable", live.citationsUsable, committed.citationsUsable],
    ["citationsContinuation", live.citationsContinuation, committed.citationsContinuation],
    ["distinctSources", live.sourceCount, committed.distinctSources]
  ];
  for (const [field, liveValue, committedValue] of checks) {
    if (liveValue !== committedValue) {
      errors.push(`live ${LIVE_CHECK_DICT} re-derivation: ${field} ${liveValue} != committed ${committedValue}`);
    }
  }
  notes.push(`live cross-check re-derived ${LIVE_CHECK_DICT} from csl-orig: ${checks.length} fields agree`);
} else if (packet) {
  notes.push(`sibling csl-orig checkout absent — live re-derivation skipped (structural checks ran)`);
}

for (const note of notes) console.log(`note: ${note}`);
if (errors.length) {
  console.error(`\nvalidate-citation-truncation: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log(`validate-citation-truncation: OK (${packet.pairs.length} pairs, ${packet.findings.citationTestablePairs} citation-testable)`);
