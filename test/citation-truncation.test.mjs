import test from "node:test";
import assert from "node:assert/strict";
import {
  locatorOf,
  locatorDepth,
  classifyCitation,
  collectDict,
  buildPayload,
  SCOPE_DICTS,
  MIN_CITATIONS_PER_SIDE,
  TIE_BAND
} from "../scripts/build-citation-truncation.mjs";

const FIXED_AT = "2026-07-29T00:00:00.000Z";

function record(k1, citations, body = "") {
  return { k1, body: body + citations.map(c => `<ls>${c}</ls>`).join(" ") };
}

function makeIntern() {
  const ids = new Map();
  return lemma => {
    let id = ids.get(lemma);
    if (id === undefined) { id = ids.size; ids.set(lemma, id); }
    return id;
  };
}

function collect(code, records, intern) {
  const dict = SCOPE_DICTS.find(d => d.code === code);
  return collectDict(dict, records, intern);
}

test("locatorDepth counts numeric and i/v/x roman components after the siglum", () => {
  assert.equal(locatorDepth(locatorOf("RV")), 0);
  assert.equal(locatorDepth(locatorOf("RV. i, 1")), 2);
  assert.equal(locatorDepth(locatorOf("Rv. 1.22.16")), 3);
  assert.equal(locatorDepth(locatorOf("P. 5,1,123")), 3);
});

test("locatorDepth ignores l/c/d/m, which are abbreviation letters here, not numerals", () => {
  // "MED. l. 57" is a column marker plus a line, not roman 50 plus 57.
  assert.equal(locatorDepth(locatorOf("MED. l. 57")), 1);
  assert.equal(locatorDepth(locatorOf("AIT. BR. 4,1")), 2);
});

test("classifyCitation separates sources, elliptical continuations, and non-text markers", () => {
  assert.equal(classifyCitation("MBh. iii, 5").kind, "source");
  // The Petersburg lane's bare-numeral references continue the previous
  // citation's siglum and so have no source of their own.
  assert.equal(classifyCitation("112,24").kind, "continuation");
  assert.equal(classifyCitation("162").kind, "continuation");
  // MW reuses <ls> for the lexicographer hedge and editorial cross-references.
  assert.equal(classifyCitation("L").kind, "nontext");
  assert.equal(classifyCitation("Cat").kind, "nontext");
  assert.equal(classifyCitation("").kind, "empty");
});

test("classifyCitation folds a source to one canonical identity across dictionaries", () => {
  const deep = classifyCitation("MBH. 14,1040");
  const bare = classifyCitation("MBh");
  assert.equal(deep.sourceId, bare.sourceId);
  assert.equal(deep.depth, 2);
  assert.equal(bare.depth, 0);
});

test("collectDict counts usable citations and excludes continuations from the source index", () => {
  const intern = makeIntern();
  const state = collect("pwg", [
    record("agni", ["MBh. 1,2", "112,24", "RV. i, 1"]),
    record("agni1", ["MBh. 3"])
  ], intern);
  assert.equal(state.entries, 2);
  assert.equal(state.citationsRaw, 4);
  assert.equal(state.citationsUsable, 3);
  assert.equal(state.citationsContinuation, 1);
  // agni1 normalises onto agni (homonym digit dropped), so one distinct lemma.
  assert.equal(state.headwords.size, 1);
  const mbh = state.bySource.get(classifyCitation("MBh").sourceId);
  assert.equal(mbh.count, 2);
  assert.equal(mbh.depthSum, 3); // "1,2" → 2, "3" → 1
});

test("buildPayload measures truncation one-directionally on shared sources", () => {
  const intern = makeIntern();
  const deep = Array.from({ length: MIN_CITATIONS_PER_SIDE }, (_, i) => `MBh. ${i + 1},${i + 1}`);
  const bare = Array.from({ length: MIN_CITATIONS_PER_SIDE }, () => "MBh");
  const states = [
    collect("pwg", [record("agni", deep)], intern),
    collect("mw", [record("agni", bare)], intern)
  ];
  const payload = buildPayload(states, { generatedAt: FIXED_AT });
  const pair = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");

  assert.equal(pair.citationTestable, true);
  assert.equal(pair.citation.sharedSources, 1);
  // Every PWG citation (depth 2) beats MW's mean depth of 0; none of MW's does.
  assert.equal(pair.citation.truncationEvidenceAB, MIN_CITATIONS_PER_SIDE);
  assert.equal(pair.citation.truncationEvidenceBA, 0);
  assert.equal(pair.citation.truncationRateAB, 1);
  assert.equal(pair.citation.truncationRateBA, 0);
  assert.equal(pair.citation.asymmetry, 1);
  assert.equal(pair.citation.moreSpecific, "pwg");
});

test("buildPayload calls a symmetric pair tied and keeps the tie band honest", () => {
  const intern = makeIntern();
  const same = Array.from({ length: MIN_CITATIONS_PER_SIDE }, () => "MBh. 1,2");
  const payload = buildPayload([
    collect("pwg", [record("agni", same)], intern),
    collect("mw", [record("agni", same)], intern)
  ], { generatedAt: FIXED_AT });
  const pair = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");
  assert.equal(pair.citation.asymmetry, 0);
  assert.equal(pair.citation.moreSpecific, "tied");
  assert.ok(TIE_BAND > 0);
});

test("buildPayload drops shared sources below the per-side citation floor", () => {
  const intern = makeIntern();
  const payload = buildPayload([
    collect("pwg", [record("agni", ["Ragh. 1,2"])], intern),
    collect("mw", [record("agni", ["Ragh"])], intern)
  ], { generatedAt: FIXED_AT });
  const pair = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");
  assert.equal(pair.citation, null);
  assert.equal(pair.citationTestable, false);
});

test("a citation-less dictionary is excluded from the citation half with a stated reason", () => {
  const intern = makeIntern();
  const deep = Array.from({ length: MIN_CITATIONS_PER_SIDE }, (_, i) => `MBh. ${i + 1},1`);
  const payload = buildPayload([
    collect("pwg", [record("agni", deep)], intern),
    collect("mw72", [record("agni", []), record("soma", [])], intern)
  ], { generatedAt: FIXED_AT });

  const excluded = payload.scope.excludedDictionaries.map(d => d.code);
  assert.deepEqual(excluded, ["mw72"]);
  assert.match(payload.scope.excludedDictionaries[0].reason, /no <ls> source citations/);
  assert.deepEqual(payload.scope.citationDictionaries, ["pwg"]);

  const pair = payload.pairs.find(p => p.a === "pwg" && p.b === "mw72");
  assert.equal(pair.citationTestable, false);
  assert.equal(pair.citation, null);
  // The hapax half still runs for it.
  assert.equal(pair.hapax.all.intersection, 1);
  assert.equal(pair.hapax.citedShared, null);
});

test("shared hapax counts only lemmas exclusive to the pair", () => {
  const intern = makeIntern();
  const payload = buildPayload([
    // shared-by-all: agni; pwg+mw only: kutumbaka; pwg only: pwgOnly
    collect("pwg", [record("agni", []), record("kuwumbaka", []), record("pwgonly", [])], intern),
    collect("mw", [record("agni", []), record("kuwumbaka", [])], intern),
    collect("pw", [record("agni", [])], intern)
  ], { generatedAt: FIXED_AT });

  const pwgMw = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");
  assert.equal(pwgMw.hapax.all.intersection, 2);
  assert.equal(pwgMw.hapax.all.sharedHapax, 1); // kuwumbaka only
  assert.equal(pwgMw.hapax.all.sharedHapaxShareOfIntersection, 0.5);

  const pwgPw = payload.pairs.find(p => p.a === "pwg" && p.b === "pw");
  assert.equal(pwgPw.hapax.all.intersection, 1);
  assert.equal(pwgPw.hapax.all.sharedHapax, 0); // agni is in three dictionaries
});

test("the cited-shared hapax scope is restricted to headwords citing a shared source", () => {
  const intern = makeIntern();
  const deep = Array.from({ length: MIN_CITATIONS_PER_SIDE }, (_, i) => `MBh. ${i + 1},1`);
  const bare = Array.from({ length: MIN_CITATIONS_PER_SIDE }, () => "MBh");
  const payload = buildPayload([
    collect("pwg", [record("agni", deep), record("soma", [])], intern),
    collect("mw", [record("agni", bare), record("soma", [])], intern)
  ], { generatedAt: FIXED_AT });
  const pair = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");

  assert.equal(pair.hapax.all.intersection, 2);      // agni + soma
  assert.equal(pair.hapax.citedShared.intersection, 1); // only agni cites MBh
  assert.equal(pair.hapax.citedShared.jaccard, 1);
});

test("every unordered pair of in-scope dictionaries appears exactly once, with a lane relation", () => {
  const intern = makeIntern();
  const states = SCOPE_DICTS.map(d => collect(d.code, [record("agni", [])], intern));
  const payload = buildPayload(states, { generatedAt: FIXED_AT });
  const n = SCOPE_DICTS.length;
  assert.equal(payload.pairs.length, (n * (n - 1)) / 2);
  assert.equal(new Set(payload.pairs.map(p => [p.a, p.b].sort().join("|"))).size, payload.pairs.length);
  const pwgMw = payload.pairs.find(p => p.a === "pwg" && p.b === "mw");
  const pwgPw = payload.pairs.find(p => p.a === "pwg" && p.b === "pw");
  assert.equal(pwgMw.relation, "cross-lane");
  assert.equal(pwgPw.relation, "within-petersburg");
});

test("buildPayload is deterministic for a fixed generatedAt", () => {
  const build = () => {
    const intern = makeIntern();
    const deep = Array.from({ length: MIN_CITATIONS_PER_SIDE }, (_, i) => `MBh. ${i + 1},1`);
    return buildPayload([
      collect("pwg", [record("agni", deep)], intern),
      collect("mw", [record("agni", ["MBh", "MBh", "MBh", "MBh", "MBh"])], intern)
    ], { generatedAt: FIXED_AT });
  };
  assert.equal(JSON.stringify(build()), JSON.stringify(build()));
});
