// Unit tests for the deterministic atlas libraries.
// Run with: npm test  (node --test, no external dependency)
//
// These cover the pure logic the generators depend on. They do not read the
// large source files; inputs are small synthetic records modeled on real CDSL
// markup seen during development.

import { test } from "node:test";
import assert from "node:assert/strict";
import os from "node:os";
import fs from "node:fs";
import path from "node:path";

import { injectMarker, generateExplorerScript, h1PanelPoints } from "../scripts/build-r2-pages.mjs";
import { parseHeader, iterateRecords } from "../scripts/lib/mw-parser.mjs";
import { classifyTypes, normalizeSource, isLexicographerOnly, extractCitations } from "../scripts/lib/mw-classifiers.mjs";
import { baseForm, layerForSource, isEditorialReference, recordSourceLayers } from "../scripts/lib/mw-source-layers.mjs";
import { compoundSegmentCount, familyBase } from "../scripts/lib/mw-depth-graph.mjs";
import { normalizeLemma } from "../scripts/lib/dict-normalize.mjs";
import { genderFromLex, genderFromProse, genderForDict } from "../scripts/lib/dict-parser.mjs";
import { iterateKoshaHeadwordsFromText, parseKoshaSynonymToken } from "../scripts/lib/dict-headwords.mjs";
import { lemmaConfidence, genderConflict, presentDicts } from "../scripts/lib/dict-align.mjs";
import { CORE_COMPARISON_DICTS, buildBroadHeadwordDictionaries, isBroadHeadwordEligible, shardIdForLemma } from "../scripts/lib/dict-scope.mjs";
import { foldSiglum, canonicalSiglum } from "../scripts/lib/source-siglum.mjs";
import { loadPreserved, reviewFields, reviewPayload } from "../scripts/lib/review-report.mjs";
import { iastToSlp1, normalizeLookupQuery, normalizeSlp1Lemma, slp1ToIast } from "../src/lib/lookup-normalize.js";
import { parseDcsSummaryFile } from "../scripts/lib/dcs-summary.mjs";

// ---- build-r2-pages ----
test("injectMarker is idempotent: inject twice gives identical result", () => {
  const scaffold = `before\n<!-- R2-GEN:START foo -->\nold\n<!-- R2-GEN:END foo -->\nafter`;
  const once = injectMarker(scaffold, "foo", "new content");
  const twice = injectMarker(once, "foo", "new content");
  assert.equal(once, twice);
});

test("generateExplorerScript defaults to dharma, lists all lemmas", () => {
  const mockAlign = {
    dharma: { senses: { mw: [{ sense: "1", text: "law", cluster: "western", n_anchor: 1 }] }, alignments: [] },
    gam:    { senses: { mw: [{ sense: "1", text: "go",  cluster: "western", n_anchor: 2 }] }, alignments: [] }
  };
  const lemmaList = ["dharma", "gam"];
  const script = generateExplorerScript(mockAlign, lemmaList);
  assert.ok(script.includes('render(sel.value="dharma")'), "default lemma must be dharma");
  assert.ok(script.includes('"dharma"'), "dharma must appear in DATA");
  assert.ok(script.includes('"gam"'),    "gam must appear in DATA");
  assert.ok(script.startsWith("<script>"), "must open <script>");
  assert.ok(script.endsWith("</script>"), "must close </script>");
});

// ---- mw-parser ----
test("parseHeader extracts flat header fields", () => {
  const h = parseHeader("<L>2<pc>1,1<k1>akAra<k2>a—kAra<h>1<e>3");
  assert.equal(h.L, "2");
  assert.equal(h.pc, "1,1");
  assert.equal(h.k1, "akAra");
  assert.equal(h.k2, "a—kAra");
  assert.equal(h.h, "1");
  assert.equal(h.ecode, "3");
});

test("iterateRecords yields records with line numbers and href", () => {
  const text = ["<L>1<pc>1,1<k1>a<k2>a<e>1", "<s>a</s> ¦ first letter", "<LEND>"].join("\n");
  const recs = [...iterateRecords(text)];
  assert.equal(recs.length, 1);
  assert.equal(recs[0].k1, "a");
  assert.equal(recs[0].startLine, 1);
  assert.match(recs[0].href, /#L1$/);
  assert.match(recs[0].body, /first letter/);
});

// ---- mw-classifiers ----
test("classifyTypes: structural types from ecode/k2", () => {
  assert.deepEqual(classifyTypes({ ecode: "2", k2: "x", body: "" }), ["derived"]);
  assert.deepEqual(classifyTypes({ ecode: "1A", k2: "x", body: "" }), ["continuation"]);
  assert.ok(classifyTypes({ ecode: "3", k2: "a—b", body: "" }).includes("compound"));
  assert.ok(classifyTypes({ ecode: "1", k2: "x", body: "x genuineroot x" }).includes("root"));
});

test("classifyTypes: grammar types attach only to primary entries", () => {
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "<lex>m.</lex>" }), ["noun-m"]);
  // a compound with a gender tag stays compound only (grammar excluded)
  assert.deepEqual(classifyTypes({ ecode: "3", k2: "a—b", body: "<lex>m.</lex>" }), ["compound"]);
});

test("classifyTypes: grammar genders are mutually exclusive by priority", () => {
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "<lex>m.</lex> ... <lex>f.</lex>" }), ["noun-m"]);
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "<lex>mfn.</lex>" }), ["adjective-mfn"]);
});

test("classifyTypes: lexicographer-only, vedic-accented, other", () => {
  assert.ok(classifyTypes({ ecode: "1", k2: "x", body: "<ls>L.</ls>" }).includes("lexicographer-only"));
  assert.ok(!classifyTypes({ ecode: "1", k2: "x", body: "<ls>RV.</ls>" }).includes("lexicographer-only"));
  assert.ok(classifyTypes({ ecode: "1", k2: "a/MSa", body: "" }).includes("vedic-accented"));
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "" }), ["other"]);
});

test("normalizeSource and isLexicographerOnly", () => {
  assert.equal(normalizeSource(" MBh. "), "MBh");
  assert.equal(normalizeSource("L."), "L");
  assert.equal(isLexicographerOnly(["L"]), true);
  assert.equal(isLexicographerOnly(["L", "RV"]), false);
  assert.equal(isLexicographerOnly([]), false);
});

test("extractCitations pulls <ls> values", () => {
  assert.deepEqual(extractCitations("x <ls>RV. x, 1</ls> y <ls>L.</ls>"), ["RV. x, 1", "L."]);
});

// ---- mw-source-layers ----
test("baseForm strips locus to base sigla", () => {
  assert.equal(baseForm("MBh. iii,5"), "MBh");
  assert.equal(baseForm("P. 1,1,14"), "P");
  assert.equal(baseForm("RV"), "RV");
  assert.equal(baseForm("Yājñ., Sch"), "Yājñ");
});

test("layerForSource maps known sources and falls back to base form", () => {
  assert.equal(layerForSource("RV"), "vedic");
  assert.equal(layerForSource("MBh"), "epic");
  assert.equal(layerForSource("MBh. i"), "epic"); // base-form fallback
  assert.equal(layerForSource("L"), "lexicographic");
  assert.equal(layerForSource("ZZZ-unmapped"), "unknown");
});

test("isEditorialReference recognizes editorial markers", () => {
  assert.equal(isEditorialReference("ib"), true);
  assert.equal(isEditorialReference("RV"), false);
});

test("recordSourceLayers computes span ignoring unknown", () => {
  const r = recordSourceLayers({ body: "<ls>RV.</ls> <ls>MBh.</ls>" });
  assert.equal(r.citationCount, 2);
  assert.equal(r.earliestLayer, "vedic");
  assert.equal(r.latestLayer, "epic");
  assert.ok(r.sourceLayerSpan >= 1);
});

// ---- mw-depth-graph ----
test("compoundSegmentCount and familyBase", () => {
  assert.equal(compoundSegmentCount({ k2: "a—tra—koSa" }), 3);
  assert.equal(compoundSegmentCount({ k2: "agni" }), 1);
  assert.equal(familyBase({ k2: "a/Msa—tra—koSa" }), "aMsa");
  assert.equal(familyBase({ k1: "agni", k2: "" }), "agni");
});

// ---- dict-normalize ----
test("normalizeLemma strips accents and trailing digits", () => {
  assert.deepEqual(normalizeLemma("a/MSa"), { normalized: "aMSa", changed: true });
  assert.deepEqual(normalizeLemma("agni"), { normalized: "agni", changed: false });
  assert.equal(normalizeLemma("agni2").normalized, "agni");
});

test("normalizeSlp1Lemma mirrors dictionary headword normalization", () => {
  assert.deepEqual(normalizeSlp1Lemma("a/MSa"), { normalized: "aMSa", changed: true });
  assert.equal(normalizeSlp1Lemma("o~").normalized, "o");
  assert.equal(normalizeSlp1Lemma("agni2").normalized, "agni");
});

// ---- dict-scope ----
test("core comparison dictionaries remain stable in order and labels", () => {
  assert.deepEqual(
    CORE_COMPARISON_DICTS.map(({ code, label }) => [code, label]),
    [["mw", "MW"], ["ap", "AP"], ["pwg", "PWG"], ["pw", "PWK"], ["wil", "WIL"], ["vcp", "VCP"], ["skd", "SKD"]]
  );
});

test("broad headword scope includes local Sanskrit/BHS and excludes reverse dictionaries", () => {
  const inventoryRows = [
    { code: "MW", full_name: "Monier-Williams", language_pair: "Skt-Eng", family: "Sanskrit-English", year: 1899, start_year: 1899, deprecated: false, in_github: true },
    { code: "BHS", full_name: "Buddhist Hybrid Sanskrit", language_pair: "BHS-Eng", family: "Buddhist Hybrid Sanskrit", year: 1953, start_year: 1953, deprecated: false, in_github: true },
    { code: "ABCH", full_name: "Abhidhana Chintamani", language_pair: "Skt-Skt", family: "Sanskrit-Sanskrit", year: 1200, start_year: 1200, deprecated: false, in_github: false },
    { code: "AE", full_name: "Apte English-Sanskrit", language_pair: "Eng-Skt", family: "English-Sanskrit", year: 1920, start_year: 1920, deprecated: false, in_github: true },
    { code: "BOR", full_name: "Borooah English-Sanskrit", language_pair: "Eng-Skt", family: "English-Sanskrit", year: 1877, start_year: 1877, deprecated: false, in_github: true }
  ];
  const localCodes = new Set(["mw", "bhs", "abch", "ae", "bor"]);
  const broad = buildBroadHeadwordDictionaries({ inventoryRows, localCodes });
  assert.deepEqual(broad.map(dict => dict.code), ["abch", "mw", "bhs"]);
  assert.equal(broad.find(dict => dict.code === "abch").sourceLinkMode, "local-only");
  assert.equal(broad.find(dict => dict.code === "mw").sourceLinkMode, "github");
  assert.equal(isBroadHeadwordEligible(inventoryRows[3], localCodes), false);
});

test("broad shard ids preserve SLP1 case distinctions", () => {
  assert.equal(shardIdForLemma("aMSa"), "61");
  assert.equal(shardIdForLemma("Agni"), "41");
  assert.notEqual(shardIdForLemma("aMSa"), shardIdForLemma("Agni"));
});

test("parseKoshaSynonymToken separates headword and gender suffix", () => {
  assert.deepEqual(parseKoshaSynonymToken("arhan-puM"), { k1: "arhan", genderSuffix: "puM", genders: ["m"] });
  assert.deepEqual(parseKoshaSynonymToken("rajobala-klI"), { k1: "rajobala", genderSuffix: "klI", genders: ["n"] });
  assert.deepEqual(parseKoshaSynonymToken("peyUza-puMklI"), { k1: "peyUza", genderSuffix: "puMklI", genders: ["m", "n"] });
  assert.deepEqual(parseKoshaSynonymToken("naktam-a"), { k1: "naktam", genderSuffix: "a", genders: ["adj"] });
});

test("iterateKoshaHeadwordsFromText extracts <syns> headwords and source lines", () => {
  const text = [
    ";METADATA",
    "<L>1<pc>5",
    "<info kvvv=\"<s>x</s>\"/>",
    "<eid>1<syns><s>arhan-puM,jina-puM,rajobala-klI</s>",
    "<s>verse text</s>",
    "<LEND>"
  ].join("\n");
  const rows = [...iterateKoshaHeadwordsFromText("abch", text, { sourceLinkMode: "local-only" })];
  assert.deepEqual(rows.map(row => row.k1), ["arhan", "jina", "rajobala"]);
  assert.deepEqual(rows.map(row => row.genderHint), ["m", "m", "n"]);
  assert.equal(rows[0].startLine, 2);
  assert.equal(rows[0].href, null);
  assert.equal(rows[0].adapter, "kosha-syns");
});

test("broad headword manifest and shards are internally consistent", () => {
  const base = path.resolve("src/data/dicts/broad-headword");
  const manifest = JSON.parse(fs.readFileSync(path.join(base, "manifest.json"), "utf8"));
  assert.equal(manifest.scope, "broadHeadword");
  assert.equal(manifest.dictionaryCount, 40);
  assert.ok(manifest.dictionaries.some(dict => dict.code === "bhs"), "BHS must be included as Sanskrit-family coverage");
  assert.ok(manifest.dictionaries.some(dict => dict.sourceLinkMode === "local-only"), "local-only dictionaries must be represented");
  for (const code of ["abch", "acph", "acsj"]) {
    assert.ok(manifest.lemmasByDict[code] > 0, `${code} must contribute kosha synonym headwords`);
  }
  assert.ok(manifest.excluded.some(dict => dict.code === "ae" && /reverse/.test(dict.reason)), "AE must be excluded as reverse lookup");
  assert.ok(manifest.excluded.some(dict => dict.code === "bor" && /reverse/.test(dict.reason)), "BOR must be excluded as reverse lookup");
  assert.ok(manifest.excluded.some(dict => dict.code === "mwe" && /reverse/.test(dict.reason)), "MWE must be excluded as reverse lookup");

  let shardTotal = 0;
  for (const shardInfo of manifest.shards) {
    const shard = JSON.parse(fs.readFileSync(path.join(base, shardInfo.path), "utf8"));
    assert.equal(shard.scope, "broadHeadword");
    assert.equal(shard.shard, shardInfo.id);
    assert.equal(shard.count, shard.entries.length);
    assert.equal(shardInfo.count, shard.entries.length);
    shardTotal += shard.entries.length;
    for (let i = 1; i < shard.entries.length; i++) {
      assert.ok(shard.entries[i - 1][0] <= shard.entries[i][0], `${shard.shard} shard must be sorted`);
    }
    for (const [, dictTuples] of shard.entries) {
      for (const [dictIndex, records, firstLine] of dictTuples) {
        assert.ok(dictIndex >= 0 && dictIndex < manifest.dictionaries.length, "dict index must resolve to manifest metadata");
        assert.ok(records >= 1, "record count must be positive");
        assert.ok(firstLine >= 1, "first source line must be positive");
      }
    }
  }
  assert.equal(shardTotal, manifest.count);
});

test("coverage artifacts expose broad default and stable core scope", () => {
  const coverage = JSON.parse(fs.readFileSync(path.resolve("src/data/dicts/coverage-matrix.json"), "utf8"));
  const overlap = JSON.parse(fs.readFileSync(path.resolve("src/data/dicts/pairwise-overlap.json"), "utf8"));
  const intersection = JSON.parse(fs.readFileSync(path.resolve("src/data/dicts/all-intersection.json"), "utf8"));

  assert.equal(coverage.defaultScope, "broadHeadword");
  assert.equal(coverage.scopes.broadHeadword.dictionaryCount, 40);
  assert.equal(coverage.scopes.coreComparison.dictionaryCount, 7);
  assert.deepEqual(
    coverage.scopes.coreComparison.dictionaries.map(({ code, label }) => [code, label]),
    [["mw", "MW"], ["ap", "AP"], ["pwg", "PWG"], ["pw", "PWK"], ["wil", "WIL"], ["vcp", "VCP"], ["skd", "SKD"]]
  );
  for (const [label, count] of Object.entries(coverage.scopes.broadHeadword.lemmasByDict)) {
    assert.ok(count > 0, `${label} must contribute broad headwords`);
  }
  assert.equal(overlap.scopes.broadHeadword.pairwise.length, 780);
  assert.equal(overlap.scopes.coreComparison.pairwise.length, 21);
  assert.ok(intersection.scopes.coreComparison.count > 0, "core all-dictionary intersection must remain non-empty");
  assert.equal(typeof intersection.scopes.broadHeadword.count, "number");
});

test("iastToSlp1 transliterates common IAST queries", () => {
  assert.equal(iastToSlp1("agni"), "agni");
  assert.equal(iastToSlp1("śiva"), "Siva");
  assert.equal(iastToSlp1("ṛta"), "fta");
  assert.equal(iastToSlp1("mahābhārata"), "mahABArata");
  assert.equal(iastToSlp1("saṃskṛta"), "saMskfta");
});

test("slp1ToIast renders public headwords in IAST", () => {
  assert.equal(slp1ToIast("aMSa"), "aṃśa");
  assert.equal(slp1ToIast("Siva"), "śiva");
  assert.equal(slp1ToIast("akza"), "akṣa");
  assert.equal(slp1ToIast("mahABArata"), "mahābhārata");
  assert.equal(slp1ToIast("dA"), "dā");
});

test("normalizeLookupQuery supports SLP1, IAST, and title-case reader input", () => {
  assert.deepEqual(normalizeLookupQuery("aMSa").candidates, ["aMSa"]);
  assert.deepEqual(normalizeLookupQuery("a/MSa").candidates, ["aMSa"]);
  assert.deepEqual(normalizeLookupQuery("śiva").candidates, ["Siva"]);
  assert.deepEqual(normalizeLookupQuery("dharma").candidates, ["dharma", "Darma"]);
  assert.deepEqual(normalizeLookupQuery("Agni").candidates, ["Agni", "agni"]);
  assert.deepEqual(normalizeLookupQuery("Dharma").candidates, ["Dharma", "dharma", "Darma"]);
});

// ---- dict-parser ----
test("genderFromLex maps <lex> to coarse tokens", () => {
  assert.equal(genderFromLex("<lex>m.</lex>"), "m");
  assert.equal(genderFromLex("<lex>mfn.</lex>"), "adj");
  assert.equal(genderFromLex("<lex>Adj.</lex>"), "adj");
  assert.equal(genderFromLex("<lex>ind.</lex>"), "ind");
  assert.equal(genderFromLex("no tag"), null);
});

test("genderFromProse: VCP markers (token + '0' after ¦)", () => {
  assert.equal(genderFromProse("a¦ pu0 avati rakzati", "vcp"), "m");
  assert.equal(genderFromProse("x¦ strI0 ...", "vcp"), "f");
  assert.equal(genderFromProse("x¦ tri0 ...", "vcp"), "adj");
  assert.equal(genderFromProse("x¦ avya0 ...", "vcp"), "ind");
  assert.equal(genderFromProse("x¦ cu0 ...", "vcp"), null); // verb-class marker, not gender
  assert.equal(genderFromProse("no separator", "vcp"), null);
});

test("genderFromProse: SKD markers (comma-delimited after ¦)", () => {
  assert.equal(genderFromProse("a¦, puM, (atati...", "skd"), "m");
  assert.equal(genderFromProse("x¦, klI, dinaM", "skd"), "n");
  assert.equal(genderFromProse("x¦, strI, ...", "skd"), "f");
  assert.equal(genderFromProse("x¦, [n], tri, (na...", "skd"), "adj"); // skips bracket note
});

test("genderForDict dispatches lex vs prose by code", () => {
  assert.equal(genderForDict("mw", "<lex>m.</lex>"), "m");
  assert.equal(genderForDict("vcp", "a¦ pu0 x"), "m");
  assert.equal(genderForDict("skd", "a¦, klI, x"), "n");
});

// ---- dict-align ----
test("lemmaConfidence: high when raws identical, medium otherwise", () => {
  const high = { mw: { raws: new Set(["agni"]) }, pwg: { raws: new Set(["agni"]) } };
  const med = { mw: { raws: new Set(["o"]) }, pwg: { raws: new Set(["o~"]) } };
  assert.equal(lemmaConfidence(high, ["mw", "pwg"]), "high");
  assert.equal(lemmaConfidence(med, ["mw", "pwg"]), "medium");
});

test("genderConflict: disjoint specific genders only", () => {
  const conflict = { mw: { genders: new Set(["m"]) }, pwg: { genders: new Set(["f"]) } };
  const overlap = { mw: { genders: new Set(["m"]) }, pwg: { genders: new Set(["m", "f"]) } };
  const adjOnly = { mw: { genders: new Set(["adj"]) }, pwg: { genders: new Set(["m"]) } };
  assert.equal(genderConflict(conflict, ["mw", "pwg"]).conflict, true);
  assert.equal(genderConflict(overlap, ["mw", "pwg"]).conflict, false);
  assert.equal(genderConflict(adjOnly, ["mw", "pwg"]).conflict, false);
});

test("presentDicts respects order", () => {
  assert.deepEqual(presentDicts({ pwg: {}, mw: {} }, ["mw", "ap", "pwg"]), ["mw", "pwg"]);
});

// ---- source-siglum ----
test("foldSiglum folds case and diacritics", () => {
  assert.equal(foldSiglum("MBh"), "mbh");
  assert.equal(foldSiglum("MBH"), "mbh");
  assert.equal(foldSiglum("ṚV"), "rv");
  assert.equal(foldSiglum("RV"), "rv");
});

test("canonicalSiglum applies the reviewed alias table", () => {
  assert.equal(canonicalSiglum("MBh"), "mbh");
  // bhag -> bhp via src/data/dict-source-aliases.json
  assert.equal(canonicalSiglum("Bhāg"), "bhp");
  assert.equal(canonicalSiglum("BhP"), "bhp");
});

// ---- review-report ----
test("reviewFields defaults to needs-review, preserves human decisions", () => {
  const empty = reviewFields(new Map(), "x");
  assert.equal(empty.reviewStatus, "needs-review");
  assert.equal(empty.reviewedValue, null);
  const preserved = new Map([["x", { reviewStatus: "reviewed-corrected", reviewedValue: { g: "n" }, reviewer: "ab", reviewedAt: "2026-01-01", note: "ok" }]]);
  assert.equal(reviewFields(preserved, "x").reviewStatus, "reviewed-corrected");
  assert.equal(reviewFields(preserved, "x").reviewer, "ab");
});

test("reviewPayload assembles envelope with recordCount = items.length", () => {
  const p = reviewPayload({ queue: "pos-gender-conflict", sourcePath: "x", items: [{}, {}], extra: { foo: 1 } });
  assert.equal(p.queue, "pos-gender-conflict");
  assert.equal(p.recordCount, 2);
  assert.equal(p.foo, 1);
  assert.ok(Array.isArray(p.items) && Array.isArray(p.assumptions) && Array.isArray(p.warnings));
});

test("loadPreserved returns empty map for a missing file", () => {
  const p = path.join(os.tmpdir(), `nope-${Date.now()}.json`);
  assert.equal(loadPreserved(p).size, 0);
});

test("loadPreserved carries only human-decided items", () => {
  const file = path.join(os.tmpdir(), `rev-${Date.now()}.json`);
  fs.writeFileSync(file, JSON.stringify({ items: [
    { reviewId: "a", reviewStatus: "needs-review" },
    { reviewId: "b", reviewStatus: "reviewed-ok" },
    { reviewId: "c", reviewStatus: "machine", reviewer: "x" }
  ] }));
  const m = loadPreserved(file);
  fs.unlinkSync(file);
  assert.equal(m.has("a"), false);
  assert.equal(m.has("b"), true);
  assert.equal(m.has("c"), true);
});

// ---- dcs-summary ----
test("parseDcsSummaryFile returns {} for a missing file", () => {
  const p = path.join(os.tmpdir(), `dcs-nope-${Date.now()}.json`);
  assert.deepEqual(parseDcsSummaryFile(p), {});
});

test("parseDcsSummaryFile resolves anchor lemmas from a present file", () => {
  const file = path.join(os.tmpdir(), `dcs-${Date.now()}.json`);
  fs.writeFileSync(file, JSON.stringify({
    schemaVersion: "1.0.0", generatedBy: "VisualDCS",
    lemmas: {
      gam:        { freqBand: 5, attested: true, formCount: 144 },
      Darma:      { freqBand: 5, attested: true },
      boDisattva: { freqBand: 2, attested: true, formCount: 7, firstAttestationEra: "late" }
    }
  }));
  const map = parseDcsSummaryFile(file);
  fs.unlinkSync(file);
  assert.equal(map.gam?.freqBand, 5);
  assert.equal(map.gam?.formCount, 144);
  assert.equal(map.Darma?.attested, true);
  assert.equal(map.boDisattva?.firstAttestationEra, "late");
  assert.equal(map.xyz, undefined);
});

test("parseDcsSummaryFile returns {} when lemmas key is absent", () => {
  const file = path.join(os.tmpdir(), `dcs-empty-${Date.now()}.json`);
  fs.writeFileSync(file, JSON.stringify({ schemaVersion: "1.0.0", generatedBy: "VisualDCS" }));
  const map = parseDcsSummaryFile(file);
  fs.unlinkSync(file);
  assert.deepEqual(map, {});
});

// ---- h1PanelPoints ----
test("h1PanelPoints returns a valid SVG string from panel JSON", () => {
  const mockPanel = {
    rows: [
      { dict: "mw",  year: 1899, family: "Monier-Williams", meanPanelUnits: 14.9, panelLemmasFound: 30, panelLemmasTotal: 30 },
      { dict: "wil", year: 1832, family: "Wilson",          meanPanelUnits: 8.0,  panelLemmasFound: 30, panelLemmasTotal: 30 },
      { dict: "skd", year: 1822, family: "indigenous",      meanPanelUnits: 1.767,panelLemmasFound: 30, panelLemmasTotal: 30 },
    ],
    stats: { pearsonYearVsUnits: 0.093, archivedPearsonAll: 0.01 }
  };
  const svg = h1PanelPoints(mockPanel);
  assert.ok(svg.startsWith("<svg"), "must start with <svg");
  assert.ok(svg.endsWith("</svg>"), "must end with </svg>");
  assert.ok(svg.includes("mw"), "must include dict label");
  assert.ok(svg.includes("Pearson r = 0.093"), "must include Pearson r");
  assert.ok(!svg.includes("NaN"), "must not contain NaN coordinates");
});

test("h1PanelPoints clips values above MAX_UNITS without NaN", () => {
  const mockPanel = {
    rows: [
      { dict: "mw72", year: 1872, family: "Monier-Williams", meanPanelUnits: 24.333, panelLemmasFound: 30, panelLemmasTotal: 30 },
    ],
    stats: { pearsonYearVsUnits: 0.05, archivedPearsonAll: 0.01 }
  };
  const svg = h1PanelPoints(mockPanel);
  assert.ok(!svg.includes("NaN"), "clipped outlier must not produce NaN");
  assert.ok(svg.includes("mw72"), "dict label must be present");
});
