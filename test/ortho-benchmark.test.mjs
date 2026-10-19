import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  normalizeRule,
  levenshtein,
  cer,
  computeMetrics,
  readGoldTsv,
  scorePredictions
} from "../scripts/score-ortho-benchmark.mjs";

const ROOT = process.cwd();
const GOLD = path.join(ROOT, "data", "ortho", "gold.tsv");
const CANDIDATES = path.join(ROOT, "data", "ortho", "candidates.tsv");
const BENCH = path.join(ROOT, "data", "ortho", "normalization_benchmark.json");
const CARD = path.join(ROOT, "data", "ortho", "normalization_benchmark.card.md");
const DOCS_CARD = path.join(ROOT, "docs", "ORTHO_BENCHMARK.md");
const PAGE = path.join(ROOT, "src", "tools", "ortho-drift.md");

const bench = JSON.parse(fs.readFileSync(BENCH, "utf8"));
const rows = readGoldTsv(GOLD);

test("rule rewriter handles German and Russian reform patterns", () => {
  assert.equal(normalizeRule("de", "Thier"), "tier");
  assert.equal(normalizeRule("de", "daß"), "dass");
  assert.equal(normalizeRule("de", "studiren"), "studieren");
  assert.equal(normalizeRule("de", "passirt"), "passiert");
  assert.equal(normalizeRule("ru", "въ"), "в");
  assert.equal(normalizeRule("ru", "имѣющій"), "имеющий");
  assert.equal(normalizeRule("ru", "Ѳеодоръ"), "феодор");
  assert.equal(normalizeRule("ru", "объект"), "объект");
});

test("Levenshtein and CER are code-point based", () => {
  assert.equal(levenshtein("kitten", "sitting"), 3);
  assert.equal(levenshtein("", "abc"), 3);
  assert.equal(levenshtein("abc", ""), 3);
  assert.equal(cer("tier", "tier"), 0);
  assert.ok(Math.abs(cer("thier", "tier") - 0.25) < 1e-12);
  assert.equal(levenshtein("ѣ", "е"), 1);
});

test("computeMetrics returns overall and grouped accuracy/CER", () => {
  const metrics = computeMetrics([
    { lang: "de", dict: "pwg", split: "train", target: "tier", pred: "tier" },
    { lang: "de", dict: "pwg", split: "dev", target: "teil", pred: "theil" },
    { lang: "ru", dict: "kow", split: "test", target: "в", pred: "въ" }
  ]);
  assert.equal(metrics.n, 3);
  assert.equal(metrics.accuracy, Number((1 / 3).toFixed(6)));
  assert.equal(metrics.byLang.de.n, 2);
  assert.equal(metrics.byLang.ru.n, 1);
  assert.equal(metrics.bySplit.test.n, 1);
  assert.ok(metrics.cer > 0);
});

test("gold TSV is complete, unique, grounded and split 100/50/50", () => {
  assert.equal(rows.length, 200);
  assert.equal(rows.filter((r) => r.lang === "de").length, 100);
  assert.equal(rows.filter((r) => r.lang === "ru").length, 100);
  const dictCounts = {};
  for (const row of rows) dictCounts[row.dict] = (dictCounts[row.dict] ?? 0) + 1;
  assert.deepEqual(dictCounts, { ccs: 25, kow: 100, pw: 25, pwg: 25, sch: 25 });
  const splits = {};
  for (const row of rows) splits[row.split] = (splits[row.split] ?? 0) + 1;
  assert.deepEqual(splits, { train: 100, dev: 50, test: 50 });
  assert.equal(new Set(rows.map((r) => r.id)).size, rows.length);
  assert.equal(new Set(rows.map((r) => `${r.lang}:${r.dict}:${r.token}`)).size, rows.length);
  for (const row of rows) {
    assert.ok(row.token.length > 0 && row.target.length > 0, row.id);
    assert.notEqual(row.token, row.target, `${row.id} is not a pre-reform token`);
    assert.ok(Number.isInteger(Number(row.line)) && Number(row.line) > 0, `${row.id} line`);
    assert.ok(row.context.length > 0, `${row.id} context`);
    assert.ok(["de", "ru"].includes(row.lang));
    assert.ok(row.source_file.includes(row.dict) || row.dict === "kow");
    assert.ok(row.era && row.era !== "other-map-era");
    assert.equal(row.scan_verified, "false");
    assert.equal(row.scan_url, "");
  }
  const candidates = fs.readFileSync(CANDIDATES, "utf8").split(/\r?\n/).filter((line) => line.trim());
  assert.equal(candidates.length, rows.length + 1);
  assert.match(candidates[0], /reason/);
});

test("committed JSON counts, hash and baselines agree with the gold TSV", () => {
  assert.equal(bench.schemaVersion, "1.0.0");
  assert.equal(bench.license, "CC-BY-SA-4.0");
  assert.equal(bench.counts.total, 200);
  assert.equal(bench.counts.german, 100);
  assert.equal(bench.counts.russian, 100);
  assert.deepEqual(bench.counts.bySplit, { train: 100, dev: 50, test: 50 });
  assert.equal(bench.counts.scanVerified, 0);
  assert.equal(bench.counts.scanUnverified, 200);
  assert.match(bench.scope, /fail-path/i);
  assert.equal(bench.splitManifest.seed, 71031910);
  assert.match(bench.splitManifest.sha256, /^[0-9a-f]{64}$/);
  const sha = crypto.createHash("sha256").update(fs.readFileSync(GOLD, "utf8")).digest("hex");
  assert.equal(bench.goldTsv.sha256, sha);
  assert.equal(bench.goldTsv.rows, rows.length);

  const ruleMetrics = scorePredictions(rows, new Map(rows.map((r) => [r.id, normalizeRule(r.lang, r.token)])));
  assert.ok(Math.abs(ruleMetrics.accuracy - bench.metrics.ruleMap.accuracy) < 1e-9);
  assert.ok(Math.abs(ruleMetrics.cer - bench.metrics.ruleMap.cer) < 1e-9);
  assert.equal(ruleMetrics.wer, Number((1 - ruleMetrics.accuracy).toFixed(6)));
  const ci = bench.metrics.ruleMap.ci;
  assert.ok(ci.accuracy[0] <= bench.metrics.ruleMap.accuracy && bench.metrics.ruleMap.accuracy <= ci.accuracy[1]);
  assert.ok(ci.cer[0] <= bench.metrics.ruleMap.cer && bench.metrics.ruleMap.cer <= ci.cer[1]);
  for (const dictMetrics of Object.values(bench.metrics.ruleMap.byDict)) {
    assert.ok(dictMetrics.ci.accuracy[0] <= dictMetrics.accuracy && dictMetrics.accuracy <= dictMetrics.ci.accuracy[1]);
  }
  const identityMetrics = scorePredictions(rows, new Map(rows.map((r) => [r.id, r.token])));
  assert.ok(Math.abs(identityMetrics.accuracy - bench.metrics.identity.accuracy) < 1e-9);
  assert.equal(bench.metrics.mapOracle.accuracy, 1);
  assert.equal(bench.metrics.mapOracle.cer, 0);
  assert.ok(bench.metrics.ruleMap.accuracy > bench.metrics.identity.accuracy);
});

test("rights and grounding caveats are recorded in JSON, card and page", () => {
  assert.match(bench.rightsNote, /CC-BY-SA-4\.0/);
  assert.match(bench.rightsNote, /no .*license|declares no license/i);
  assert.ok(bench.caveats.some((c) => /NOT SCAN-IMAGE VERIFIED/i.test(c)));
  assert.ok(bench.caveats.some((c) => /not redistributed|NOT redistributed/i.test(c)));
  const card = fs.readFileSync(CARD, "utf8");
  const docsCard = fs.readFileSync(DOCS_CARD, "utf8");
  assert.equal(docsCard, card);
  assert.match(card, /source-text-grounded, not scan-image verified/i);
  assert.match(card, /SanskritSpellCheck \*\*declares no license\*\*/);
  assert.match(card, /CC-BY-SA-4\.0/);
  const page = fs.readFileSync(PAGE, "utf8");
  assert.match(page, /## Normalization benchmark/);
  assert.match(page, /normalization_benchmark\.json/);
  assert.match(page, /data\/ortho\/gold\.tsv/);
  assert.match(page, /csvDownloadButton/);
});
