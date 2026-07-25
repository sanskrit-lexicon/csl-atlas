import test from "node:test";
import assert from "node:assert/strict";
import {
  PERIODS,
  parsePeriodsField,
  gammaQ,
  kruskalWallis,
  koshaPeriodMap,
  buildPayload
} from "../scripts/build-period-signatures.mjs";

const INVENTORY = [
  { code: "pwg", year: 1855, family: "Sanskrit-German" },
  { code: "pw", year: 1879, family: "Sanskrit-German" },
  { code: "gra", year: 1873, family: "Sanskrit-German" },
  { code: "mw", year: 1899, family: "Sanskrit-English" },
  { code: "cae", year: 1891, family: "Sanskrit-English" },
  { code: "bur", year: 1866, family: "Sanskrit-French" }
];

function unionRow(slp1, dicts) {
  const list = dicts.split(" ");
  return { slp1, iast: slp1, n_dicts: String(list.length), dicts, gender: "", fem_fold: "" };
}

function freqRow(lemma, periods) {
  return { lemma_slp1: lemma, count_all: "10", grammar_all: "m", rank_all: "1", periods, periods_sum: "", coverage_pct: "", core_rank: "" };
}

test("parsePeriodsField handles the real kosha token shapes, including fused 3200/4700", () => {
  const counts = parsePeriodsField("9 Vedic=8283|1 -800=2897|2 -300=1588|3200=12492|4700=21167|5 1200=35932|6 1700=11318|7 1900=1158|11 Epic=25725|12 Classic=55544");
  assert.equal(counts.length, PERIODS.length);
  assert.equal(counts[0], 8283); // 9 Vedic
  assert.equal(counts[3], 12492); // 3200 = period 3 / 200 CE
  assert.equal(counts[9], 55544); // 12 Classic
  assert.deepEqual(parsePeriodsField(""), new Array(PERIODS.length).fill(0));
  assert.throws(() => parsePeriodsField("8 Unknown=5"), /unknown DCS period label/);
  assert.throws(() => parsePeriodsField("9 Vedic"), /without '='/);
});

test("gammaQ matches known chi-square upper-tail values", () => {
  // chi2 df=1 critical 3.841 -> p ~ 0.05; df=3 critical 7.815 -> p ~ 0.05
  assert.ok(Math.abs(gammaQ(0.5, 3.841 / 2) - 0.05) < 0.001);
  assert.ok(Math.abs(gammaQ(1.5, 7.815 / 2) - 0.05) < 0.001);
  assert.equal(gammaQ(2, 0), 1);
});

test("kruskalWallis matches the hand-computed two-group example", () => {
  const { h, df, p } = kruskalWallis([[1, 2, 3], [4, 5, 6]]);
  assert.ok(Math.abs(h - 3.857) < 0.01, `H ${h}`);
  assert.equal(df, 1);
  assert.ok(Math.abs(p - 0.0495) < 0.005, `p ${p}`);
});

test("koshaPeriodMap sums vectors for rows folding onto one normalized key", () => {
  const map = koshaPeriodMap([
    freqRow("deva", "9 Vedic=10|12 Classic=30"),
    freqRow("deva", "9 Vedic=5"),
    freqRow("agni", "1 -800=7")
  ]);
  assert.equal(map.get("deva")[0], 15);
  assert.equal(map.get("deva")[9], 30);
  assert.equal(map.get("agni")[1], 7);
  assert.equal(map.size, 2);
});

test("buildPayload: shares sum to 1, modal counts cohere, chron score correct, KW stays descriptive", () => {
  const unionRows = [
    unionRow("veda", "GRA PWG"),
    unionRow("kavya", "MW CAE"),
    unionRow("agni", "GRA MW PWG"),
    unionRow("ghost", "MW") // no kosha row -> unmatched
  ];
  const freqRows = [
    freqRow("veda", "9 Vedic=80|1 -800=20"), // chron = (80*-1000 + 20*-800)/100 = -960
    freqRow("kavya", "5 1200=50|12 Classic=50"), // dated only 1200
    freqRow("agni", "9 Vedic=100")
  ];
  const payload = buildPayload(unionRows, freqRows, INVENTORY, { generatedAt: "2026-07-25T00:00:00.000Z", bootstrapB: 50 });
  assert.equal(payload.totals.unionLemmas, 4);
  assert.equal(payload.totals.matchedLemmas, 3);

  const gra = payload.perDict.find((d) => d.code === "GRA");
  assert.equal(gra.matched, 2);
  const shareSum = gra.typeShare.reduce((a, v) => a + v, 0);
  assert.ok(Math.abs(shareSum - 1) < 0.001);
  assert.equal(gra.modalCounts.reduce((a, v) => a + v, 0), gra.matched);
  // GRA lemmas: veda (chron -960) and agni (chron -1000) -> mean -980
  assert.ok(Math.abs(gra.meanChron - -980) < 0.5, `GRA meanChron ${gra.meanChron}`);

  const mw = payload.perDict.find((d) => d.code === "MW");
  assert.equal(mw.matched, 2); // kavya + agni (ghost unmatched)
  assert.ok(Math.abs(mw.matchRate - 2 / 3) < 0.001);

  // baseline covers each matched lemma once
  assert.equal(payload.baseline.modalCounts.reduce((a, v) => a + v, 0), 3);

  // KW: only families with >=2 dicts (Sanskrit-German GRA+PWG, Sanskrit-English MW+CAE)
  assert.deepEqual(payload.kruskalWallis.families.map((f) => f.family).sort(), ["Sanskrit-English", "Sanskrit-German"]);
  assert.equal(payload.kruskalWallis.evidenceGrade, "descriptive");

  // deterministic
  const again = buildPayload(unionRows, freqRows, INVENTORY, { generatedAt: "2026-07-25T00:00:00.000Z", bootstrapB: 50 });
  assert.deepEqual(again, payload);
});
