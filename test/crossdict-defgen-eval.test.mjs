// H7104 — the cross-dictionary defgen evaluation stays frozen, joined, and
// non-promoting.
//
// Run with: npm test  (node --test)

import { test } from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dir = path.join(root, "data", "eval", "crossdict-defgen");
const ARMS = ["A0_random_floor", "A1_chat_ctx", "A2_chat_noctx", "A3_reasoner_ctx", "F1_fable_ctx"];

function readJsonl(file) {
  return fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter(Boolean);
  const split = line => {
    const out = [];
    let cell = "";
    let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (quoted && line[i + 1] === '"') { cell += '"'; i++; }
        else quoted = !quoted;
      } else if (ch === "," && !quoted) { out.push(cell); cell = ""; }
      else cell += ch;
    }
    out.push(cell);
    return out;
  };
  const header = split(lines[0]);
  return lines.slice(1).map(line => Object.fromEntries(header.map((k, i) => [k, split(line)[i] ?? ""])));
}

const sample = fs.readFileSync(path.join(dir, "frozen_sample.tsv"), "utf8")
  .replace(/^\uFEFF/, "").split(/\r?\n/).filter(Boolean)
  .slice(1)
  .map(line => line.split("\t"))
  .map(([slp1, iast, grammar, sense_count, poly_band, count_all, rank_all, freq_band, dcs_lemma_id, n_attest, gold_gloss]) =>
    ({ slp1, iast, grammar, sense_count, poly_band, count_all, rank_all, freq_band, dcs_lemma_id, n_attest, gold_gloss }));
const scores = JSON.parse(fs.readFileSync(path.join(dir, "crossdict_scores.json"), "utf8"));
const senseRows = readJsonl(path.join(dir, "sense_units.jsonl"));
const items = parseCsv(fs.readFileSync(path.join(dir, "crossdict_scores_per_item.csv"), "utf8"));
const calibration = JSON.parse(fs.readFileSync(path.join(dir, "judge_calibration.json"), "utf8"));
const calSample = parseCsv(fs.readFileSync(path.join(dir, "judge_calibration_sample.csv"), "utf8"));
const worker = fs.readFileSync(path.join(dir, "judge_calibration_worker.tsv"), "utf8")
  .split(/\r?\n/).slice(1).filter(Boolean).map(line => line.split("\t"));

test("the frozen MW sample is 500 unique headwords", () => {
  assert.equal(sample.length, 500);
  assert.equal(new Set(sample.map(row => row.slp1)).size, 500);
  assert.ok(sample.every(row => row.slp1 && row.gold_gloss));
});

test("all five generation and judge arms are present at 500 rows", () => {
  for (const arm of ARMS) {
    assert.equal(readJsonl(path.join(dir, "generations", `gen_${arm}.jsonl`)).length, 500, arm);
    assert.equal(readJsonl(path.join(dir, "judge", `judge_${arm}.jsonl`)).length, 500, arm);
  }
});

test("sense units join every sampled lemma and cover the other dictionaries", () => {
  assert.equal(senseRows.length, 500);
  const withOther = senseRows.filter(row => Object.values(row.units).some((v, i) => i > 0 && v != null));
  assert.equal(withOther.length, scores.senseCoverage.lemmas_with_other_dict);
  assert.ok(withOther.length >= 300);
  assert.equal(senseRows.filter(row => row.other_max >= 2).length, scores.senseCoverage.lemmas_crossdict_distinction);
});

test("per-item scores are one row per arm and sampled lemma", () => {
  assert.equal(items.length, 2500);
  assert.equal(new Set(items.map(row => `${row.arm}:${row.slp1}`)).size, 2500);
  const sampleKeys = new Set(sample.map(row => row.slp1));
  assert.ok(items.every(row => sampleKeys.has(row.slp1)));
  assert.ok(items.every(row => ARMS.includes(row.arm)));
});

test("the random floor is weak on adequacy, so the primary endpoint is adequacy-gated", () => {
  const floor = scores.summary.byArm.A0_random_floor;
  assert.ok(floor.distinction_preserved_rate > 0.5);
  assert.equal(floor.distinction_preserved_adequate_rate, 0);
  assert.ok(floor.mean_judge_adequacy < 0.5);
});

test("chrF/BLEU baselines are frozen from the kosha scorer, not recomputed here", () => {
  for (const arm of ARMS) {
    assert.equal(scores.baseline[arm].n, 500);
    assert.ok(scores.baseline[arm].mean_sent_chrf > 0);
    assert.match(scores.baseline[arm].source, /kosha/);
  }
});

test("the 100-row calibration sample is 20 rows per arm and human-scored", () => {
  assert.equal(calSample.length, 100);
  for (const arm of ARMS) assert.equal(calSample.filter(row => row.arm === arm).length, 20);
  assert.equal(worker.length, 100);
  assert.ok(worker.every(([, value]) => /^[0-5]$/.test(value)));
  assert.equal(calibration.status, "single-key-worker-scored");
  assert.equal(calibration.humanGoldStatus, "blocked");
  assert.equal(calibration.n, 100);
  assert.ok(calibration.quadratic_weighted_kappa >= -1 && calibration.quadratic_weighted_kappa <= 1);
  assert.ok(calibration.within_one_agreement >= calibration.exact_agreement);
});

test("the verdict is a decision, never a promotion of generated content", () => {
  assert.ok(["GO", "NO-GO"].includes(scores.verdict.decision));
  assert.ok(Array.isArray(scores.verdict.reasons) && scores.verdict.reasons.length);
  assert.match(scores.verdict.stoppingRule, /No generated definition is promoted/);
  assert.equal(scores.sourceProvenance.koshaDefgen.path, "gasyoun/kosha data/eval/defgen");
});

test("every declared input hash matches the vendored file", () => {
  for (const [rel, expected] of Object.entries(scores.sourceProvenance.koshaDefgen.inputs)) {
    const actual = crypto.createHash("sha256").update(fs.readFileSync(path.join(dir, rel))).digest("hex");
    assert.equal(actual, expected, rel);
  }
});
