import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  loadMapping,
  assertMappingConsistent,
  indexMapping,
  vocabularySet,
  censusDictionary,
  buildCensus
} from "../scripts/build-usage-register-census.mjs";

const FIXED_AT = "2026-09-23T00:00:00.000Z";

// Records are the <L>..<LEND> shell. Entry 1 carries two labels, entry 2 carries
// only excluded look-alikes, entry 3 carries the MW-only hedge.
const MW_FIXTURE = [
  "<L>1<k1>a</k1><e>1</e>",
  "gloss <lang>Ved.</lang> and <ab>fig.</ab>",
  "<LEND>",
  "<L>2<k1>b</k1><e>2</e>",
  "<ab>lit.</ab> and <ab>ep.</ab> and <ab>L.</ab> and <lang>L.</lang>",
  "<LEND>",
  "<L>3<k1>c</k1><e>3</e>",
  "<ls>L.</ls>",
  "<LEND>"
].join("\n");

test("the published mapping is consistent with its own vocabulary and negative map", () => {
  const mapping = loadMapping();
  assert.equal(assertMappingConsistent(mapping), true);
  const vocab = vocabularySet(mapping);
  assert.ok(vocab.has("lexicographer-only"));
  assert.ok(vocab.has("vedic"));
  assert.ok(vocab.has("prakrit"));
  assert.ok(mapping.excluded.tokens.some((t) => t.tag === "ab" && t.token === "lit."));
});

test("indexMapping rejects a duplicated (tag, token) label", () => {
  const mapping = loadMapping();
  mapping.labels.push({ ...mapping.labels.find((r) => r.category === "vedic") });
  assert.throws(() => indexMapping(mapping), /duplicate label/);
});

test("assertMappingConsistent rejects a category outside the closed vocabulary", () => {
  const mapping = loadMapping();
  mapping.labels = [{ tag: "ab", token: "x.", class: "register", category: "made-up" }];
  assert.throws(() => assertMappingConsistent(mapping), /outside the closed vocabulary/);
});

test("assertMappingConsistent rejects a pair listed as both label and excluded look-alike", () => {
  const mapping = loadMapping();
  mapping.excluded.tokens.push({ tag: "lang", token: "Ved.", reason: "contradiction" });
  assert.throws(() => assertMappingConsistent(mapping), /both as a label and as an excluded look-alike/);
});

test("censusDictionary counts marked labels and ignores the excluded look-alikes", () => {
  const index = indexMapping(loadMapping());
  const c = censusDictionary("mw", MW_FIXTURE, index);
  assert.equal(c.entries, 3);
  // Only Ved. (lang), fig. (ab) and L. (ls) are real labels; lit./ep./L. in <ab>
  // and L. in <lang> are excluded look-alikes and must contribute nothing.
  assert.equal(c.instances, 3);
  assert.equal(c.entriesWithLabel, 2); // entries 1 and 3; entry 2 is all look-alikes
  assert.deepEqual(
    c.byCategory.map((x) => x.category).sort(),
    ["figurative", "lexicographer-only", "vedic"]
  );
  assert.equal(c.byCategory.find((x) => x.category === "lexicographer-only").instances, 1);
});

test("censusDictionary honours the per-dictionary allow-list on a label", () => {
  const index = indexMapping(loadMapping());
  // <ls>L. is MW-only and <lang>Ved. is MW/BHS-only, but <ab>fig. is an AP label
  // too — so AP keeps only the figurative instance.
  const ap = censusDictionary("ap", MW_FIXTURE, index);
  assert.equal(ap.instances, 1);
  assert.deepEqual(ap.byCategory.map((x) => x.category), ["figurative"]);
  assert.equal(ap.entries, 3);
});

test("buildCensus derives per-dictionary rates and diagnostics", () => {
  const mapping = loadMapping();
  const sources = [
    { code: "mw", text: MW_FIXTURE },
    { code: "wil", text: "<L>1<k1>a</k1><e>1</e>\nplain gloss\n<LEND>" }
  ];
  const p = buildCensus(sources, mapping, FIXED_AT);
  assert.equal(p.generatedAt, FIXED_AT);
  assert.equal(p.scope.dictionariesScanned, 2);
  assert.equal(p.scope.dictionariesWithLabels, 1);
  assert.equal(p.scope.totalEntries, 4);
  assert.equal(p.scope.totalInstances, 3);
  assert.equal(p.scope.entriesWithLabel, 2);

  const mw = p.perDictionary.find((d) => d.code === "mw");
  assert.equal(mw.instances, 3);
  assert.equal(mw.instancesPer1000Entries, Number(((3 / 3) * 1000).toFixed(4)));

  const wil = p.perDictionary.find((d) => d.code === "wil");
  assert.equal(wil.instances, 0);
  assert.deepEqual(p.diagnostics, [{ code: "wil", reason: "no mapped usage/register label in markup" }]);

  // Global category rows reconcile with the per-dictionary rows.
  const vedic = p.categories.find((c) => c.category === "vedic");
  assert.equal(vedic.instances, 1);
  assert.equal(vedic.class, "register");
});

test("committed census is internally consistent and keeps MW's lexicographer hedge unique", () => {
  const file = path.resolve(process.cwd(), "src", "data", "lexico", "usage_register_census.json");
  assert.ok(fs.existsSync(file), "committed usage_register_census.json missing");
  const p = JSON.parse(fs.readFileSync(file, "utf8"));
  const mapping = loadMapping();
  const vocab = vocabularySet(mapping);

  assert.equal(p.schemaVersion, "1.0.0");
  assert.equal(p.evidenceLabel, "observed");
  assert.ok(p.scope.dictionariesScanned >= 40, "expected the full csl-orig dictionary sweep");
  assert.equal(p.perDictionary.length, p.scope.dictionariesScanned);

  for (const d of p.perDictionary) {
    assert.ok(d.entries > 0, `${d.code} has no entries`);
    assert.equal(d.byLabel.reduce((a, l) => a + l.instances, 0), d.instances, `${d.code} label sum`);
    assert.equal(d.byCategory.reduce((a, c) => a + c.instances, 0), d.instances, `${d.code} category sum`);
    for (const c of d.byCategory) assert.ok(vocab.has(c.category), `${d.code} bad category ${c.category}`);
  }

  // The own-data canary: the lexicographers-only hedge is the MW <ls>L. label and
  // nothing else. If a look-alike ever leaks in, this fails.
  const withLex = p.perDictionary.filter((d) => d.byCategory.some((c) => c.category === "lexicographer-only"));
  assert.deepEqual(withLex.map((d) => d.code), ["mw"]);
  const mw = p.perDictionary.find((d) => d.code === "mw");
  assert.ok(
    mw.byCategory.find((c) => c.category === "lexicographer-only").instances > 30000,
    "MW lexicographer-only baseline collapsed"
  );
  // MW's Vedic/epic labels come from <lang>, not <ab>.
  const mwLabels = new Map(mw.byLabel.map((l) => [`${l.tag}\t${l.token}`, l.instances]));
  assert.ok(mwLabels.get("lang\tVed.") > 500, "MW <lang>Ved. baseline collapsed");
  assert.ok(!mwLabels.has("ab\tVed."), "MW has no <ab>Ved. label");
  assert.ok(!mwLabels.has("ab\tlit."), "MW <ab>lit. is 'literally', never counted");
  assert.ok(!mwLabels.has("ab\tep."), "MW <ab>ep. would be epithet, never counted");
});