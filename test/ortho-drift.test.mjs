import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  cleanGloss,
  glossTokens,
  DE_PROFILE,
  RU_PROFILE,
  ruDefinitionalHit,
  loadReformMap,
  cslEntryBodies,
  censusEntries,
  mulberry32,
  bootstrapCis,
  olsFit,
  spearmanExact,
  pairPermutationTest,
  buildPayload
} from "../scripts/build-ortho-drift.mjs";

const DE_ERAS = new Set(["1901-th", "1996-ss"]);

function fixtureMap() {
  const file = path.join(os.tmpdir(), `ortho-fixture-${process.pid}.tsv`);
  fs.writeFileSync(
    file,
    "# comment line\nthier\ttier\t1901-th\ntheil\tteil\t1901-th\ndaß\tdass\t1996-ss\naachner\taachener\t75\n"
  );
  const map = loadReformMap(file, DE_ERAS);
  fs.unlinkSync(file);
  return map;
}

test("cleanGloss strips Sanskrit, annotations, metadata, sigla and tags", () => {
  const body =
    "{#agni#} das Thier <ls>MBH. 1,23</ls> {{alt->neu||2020|ed|url|}} " +
    "<bot>Curcuma longa</bot> {%kursiv%} <ab>vgl.</ab> {part=,seq=1,type=,n=1} अग्नि";
  const cleaned = cleanGloss(body);
  assert.ok(!cleaned.includes("agni"));
  assert.ok(!cleaned.includes("MBH"));
  assert.ok(!cleaned.includes("Curcuma"));
  assert.ok(!cleaned.includes("seq=1"));
  assert.ok(!cleaned.includes("अग्नि"));
  assert.ok(cleaned.includes("Thier"));
  assert.ok(cleaned.includes("kursiv")); // italics unwrapped, not dropped
});

test("glossTokens lowercases, drops abbreviations and all-caps sigla", () => {
  const tokens = glossTokens(DE_PROFILE, "Das Thier und der THIER-CODEX, vgl. Blüthe adj");
  assert.deepEqual(tokens, ["das", "thier", "und", "der", "blüthe"]);
});

test("loadReformMap indexes old forms, modern set, and buckets unknown eras", () => {
  const map = fixtureMap();
  assert.equal(map.forms, 4);
  assert.deepEqual(map.byOld.get("thier"), { modern: "tier", era: "1901-th" });
  assert.equal(map.byOld.get("aachner").era, "other-map-era");
  assert.ok(map.modernSet.has("dass"));
});

test("cslEntryBodies splits <L>...<LEND> records and ignores prologue", () => {
  const text = "<H>{#a#}\n\n<L>1<pc>1-1<k1>a<k2>a\nline one\nline two\n<LEND>\n<L>2<pc>1-1<k1>b<k2>b\nzweite\n<LEND>\n";
  assert.deepEqual(cslEntryBodies(text), ["line one\nline two", "zweite"]);
});

test("censusEntries splits dated vs all-map pre-reform hits and counts post-reform hits", () => {
  const map = fixtureMap();
  const { perEntry, tokens, preHitsDated, preHitsAllMap, postHits, eras, formCounts, modernCounts } = censusEntries(
    DE_PROFILE,
    map,
    ["das Thier läuft", "der Teil und Tier", "daß nichts", "der Aachner Dom"]
  );
  assert.equal(tokens, 12);
  assert.equal(preHitsDated, 2); // thier, daß (era-attributed)
  assert.equal(preHitsAllMap, 3); // + aachner (other-map-era)
  assert.equal(postHits, 2); // teil, tier
  assert.deepEqual(perEntry, [[3, 1, 1, 0], [4, 0, 0, 2], [2, 1, 1, 0], [3, 0, 1, 0]]);
  assert.equal(eras.get("1901-th"), 1);
  assert.equal(eras.get("1996-ss"), 1);
  assert.equal(eras.get("other-map-era"), 1);
  assert.equal(formCounts.get("thier"), 1);
  assert.equal(modernCounts.get("tier"), 1);
});

test("ruDefinitionalHit flags 1918-abolished letters and final hard sign", () => {
  assert.ok(ruDefinitionalHit("въ"));
  assert.ok(ruDefinitionalHit("растеніе"));
  assert.ok(ruDefinitionalHit("имѣющій"));
  assert.ok(!ruDefinitionalHit("дом"));
  assert.ok(!ruDefinitionalHit("объект")); // internal hard sign is modern
});

test("RU tokens keep pre-1918 letters; mulberry32 is deterministic", () => {
  const tokens = glossTokens(RU_PROFILE, "первая буква Санскритскаго алфавита въ");
  assert.ok(tokens.includes("санскритскаго"));
  assert.ok(tokens.includes("въ"));
  const a = mulberry32(7);
  const b = mulberry32(7);
  for (let i = 0; i < 50; i++) assert.equal(a(), b());
});

test("bootstrapCis brackets the point estimate and is reproducible", () => {
  const perEntry = Array.from({ length: 200 }, (_, i) => [10, i % 10 === 0 ? 2 : 0, i % 10 === 0 ? 2 : 0, 1]);
  const c1 = bootstrapCis(perEntry, { b: 300, seed: 42 });
  const c2 = bootstrapCis(perEntry, { b: 300, seed: 42 });
  assert.deepEqual(c1, c2);
  const drift = (perEntry.reduce((a, e) => a + e[1], 0) / perEntry.reduce((a, e) => a + e[0], 0)) * 1000;
  assert.ok(c1.driftPer1k[0] <= drift && drift <= c1.driftPer1k[1]);
});

test("olsFit recovers an exact line; spearmanExact is exhaustive and signs correctly", () => {
  const fit = olsFit([1, 2, 3, 4], [10, 8, 6, 4]);
  assert.ok(Math.abs(fit.slope + 2) < 1e-12);
  assert.ok(Math.abs(fit.r2 - 1) < 1e-12);
  const sp = spearmanExact([1865, 1873, 1884, 1887, 1928], [10, 8, 9, 5, 2]);
  assert.equal(sp.permutations, 120);
  assert.ok(sp.rho < 0);
  assert.ok(sp.pTwoSided > 0 && sp.pTwoSided <= 1);
});

test("pairPermutationTest detects a real rate difference and keeps p in (0,1]", () => {
  const low = Array.from({ length: 120 }, () => [10, 0, 0, 1]);
  const high = Array.from({ length: 120 }, () => [10, 1, 1, 1]);
  const t = pairPermutationTest(low, high, { b: 200, seed: 9, bMinusAPositive: true });
  assert.ok(t.diffPer1k > 90);
  assert.ok(t.pOneSided <= 0.01);
  const null1 = pairPermutationTest(low, low.slice(), { b: 200, seed: 9, bMinusAPositive: true });
  assert.ok(null1.pOneSided > 0.05);
});

test("buildPayload: coherent dicts, exhaustive spearman, verdicts consistent with stats", () => {
  const map = fixtureMap();
  const mk = (code, label, lineage, year, texts) => ({
    code,
    label,
    fullName: label,
    lineage,
    year,
    startYear: year,
    endYear: year,
    midYear: year,
    census: censusEntries(DE_PROFILE, map, texts),
    map
  });
  const old = "das Thier und der Theil weil daß";
  const modern = "das Tier und der Teil weil dass";
  const german = [
    mk("pwg", "PWG", "progenitor", 1865, [old, old, old, modern]),
    mk("gra", "GRA", "independent", 1873, [old, old, modern, modern]),
    mk("pw", "PWK", "descendant", 1884, [old, modern, modern, modern]),
    mk("ccs", "CCS", "descendant", 1887, [modern, modern, modern, old]),
    mk("sch", "SCH", "descendant", 1928, [modern, modern, modern, modern])
  ];
  const payload = buildPayload({
    german,
    russian: [],
    deMapForms: map.forms,
    ruMapForms: 0,
    generatedAt: "2026-07-26T00:00:00.000Z"
  });
  assert.equal(payload.german.dicts.length, 5);
  assert.equal(payload.german.regression.spearmanPermutations, 120);
  for (const d of payload.german.dicts) {
    assert.ok(Math.abs(d.driftPer1k - (d.preHitsDated / d.tokens) * 1000) < 0.001);
    assert.ok(d.preHitsDated <= d.preHitsAllMap);
    assert.ok(d.ci.driftPer1k[0] <= d.driftPer1k && d.driftPer1k <= d.ci.driftPer1k[1]);
  }
  const rho = payload.german.regression.spearmanRho;
  const p = payload.german.regression.spearmanExactPTwoSided;
  const expectedClock = rho < 0 && p <= 0.05 ? "supported" : rho < 0 ? "direction-consistent-inconclusive" : "not-supported";
  assert.equal(payload.verdict.clock, expectedClock);
  const descentPair = payload.german.pairTests.find((t) => t.a === "gra" && t.b === "ccs");
  assert.ok(descentPair);
  // determinism: same inputs -> identical payload
  const again = buildPayload({
    german,
    russian: [],
    deMapForms: map.forms,
    ruMapForms: 0,
    generatedAt: "2026-07-26T00:00:00.000Z"
  });
  assert.deepEqual(again, payload);
});
