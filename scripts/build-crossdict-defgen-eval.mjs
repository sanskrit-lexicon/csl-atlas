// H7104 — cross-dictionary sense-consistency evaluation of the frozen
// kosha defgen arms.
//
// Consumes the frozen 500-headword MW sample, five generation arms and five
// LLM-judge arms from kosha/data/eval/defgen (vendored under
// data/eval/crossdict-defgen), joins PWG/PWK/AP/MW sense units from the local
// csl-orig v02 sources through the committed H7098 sense adapters, and asks
// whether each generated gloss preserves the sense distinction the other
// dictionaries make.
//
// The generation is NOT re-run here. The script never accepts a generated
// definition as dictionary content; it only scores it.
//
// Usage:
//   npm run build-crossdict-defgen-eval
//   npm run build-crossdict-defgen-eval -- --reset-calibration
//
// Requires ../csl-orig/v02 next to the repository root (or CSL_ATLAS_CSL_ORIG).

import fs from "node:fs";
import path from "node:path";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { senseUnitsForDict } from "./lib/dict-feature-adapters.mjs";
import { licenseFields } from "./lib/dataset-meta.mjs";
import {
  readJson, readJsonl, sha256, hashKey, round, mean, csvEscape, parseCsv, parseTsv,
  glossSegments, quadraticWeightedKappa, pearson, spearman, decideVerdict
} from "./lib/crossdict-defgen-eval.mjs";

const SCHEMA_VERSION = "1.0.0";
const DIR = path.resolve("data", "eval", "crossdict-defgen");
const OUT_SENSE = path.join(DIR, "sense_units.jsonl");
const OUT_ITEMS = path.join(DIR, "crossdict_scores_per_item.csv");
const OUT_SCORES = path.join(DIR, "crossdict_scores.json");
const OUT_CAL_SAMPLE = path.join(DIR, "judge_calibration_sample.csv");
const WORKER_FILE = path.join(DIR, "judge_calibration_worker.tsv");
const OUT_CAL = path.join(DIR, "judge_calibration.json");
const SEED = "H7104";
const CORE_SENSE_DICTS = ["mw", "ap", "pwg", "pw"];
const OTHER_DICTS = ["ap", "pwg", "pw"];
const ARMS = ["A0_random_floor", "A1_chat_ctx", "A2_chat_noctx", "A3_reasoner_ctx", "F1_fable_ctx"];
const CAL_PER_ARM = 20;

function buildSenseIndex() {
  const sampleRows = parseTsv(fs.readFileSync(path.join(DIR, "frozen_sample.tsv"), "utf8"));
  const wanted = new Set(sampleRows.map(r => r.slp1));
  const index = new Map();
  const availability = {};
  for (const dict of CORE_SENSE_DICTS) {
    availability[dict] = { source: `../csl-orig/v02/${dict}/${dict}.txt`, records: 0, matched: 0 };
    if (!dictExists(dict)) continue;
    for (const rec of iterateDict(dict)) {
      availability[dict].records++;
      if (!rec.k1) continue;
      const key = normalizeLemma(rec.k1).normalized;
      if (!wanted.has(key)) continue;
      availability[dict].matched++;
      const units = senseUnitsForDict(dict, rec.body || "") ?? 1;
      if (!index.has(key)) index.set(key, {});
      const current = index.get(key)[dict];
      if (!current || units > current.units ||
          (units === current.units && rec.startLine < current.line)) {
        index.get(key)[dict] = {
          units,
          method: dict === "mw" ? "mw-sense-section-div" : `${dict}-sense-marker`,
          line: rec.startLine,
          href: rec.href
        };
      }
    }
  }
  return { index, availability, sampleRows };
}

function calibrationRows(itemsByKey) {
  const picked = [];
  for (const arm of ARMS) {
    const pool = itemsByKey.get(arm) || [];
    const sorted = [...pool].sort((a, b) =>
      hashKey(SEED, `${arm}:${a.slp1}`).localeCompare(hashKey(SEED, `${arm}:${b.slp1}`)) ||
      a.slp1.localeCompare(b.slp1));
    picked.push(...sorted.slice(0, CAL_PER_ARM));
  }
  return picked;
}

function main() {
  const resetCalibration = process.argv.includes("--reset-calibration");
  const { index, availability, sampleRows } = buildSenseIndex();
  const sampleByKey = new Map(sampleRows.map(r => [r.slp1, r]));

  const generations = new Map();
  const judges = new Map();
  for (const arm of ARMS) {
    const gens = new Map(readJsonl(path.join(DIR, "generations", `gen_${arm}.jsonl`)).map(r => [r.slp1, r]));
    const js = new Map(readJsonl(path.join(DIR, "judge", `judge_${arm}.jsonl`)).map(r => [r.slp1, r.adequacy]));
    generations.set(arm, gens);
    judges.set(arm, js);
  }

  const senseRows = [];
  for (const row of sampleRows) {
    const units = index.get(row.slp1) || {};
    senseRows.push({
      slp1: row.slp1,
      iast: row.iast,
      freq_band: row.freq_band,
      poly_band: row.poly_band,
      units: Object.fromEntries(CORE_SENSE_DICTS.map(d => [d, units[d]?.units ?? null])),
      entries: Object.fromEntries(CORE_SENSE_DICTS.map(d => [d, units[d]?.line ? { line: units[d].line, href: units[d].href } : null])),
      other_max: Math.max(...OTHER_DICTS.map(d => units[d]?.units ?? 0)),
      mw_units: units.mw?.units ?? null
    });
  }
  fs.writeFileSync(OUT_SENSE, senseRows.map(r => JSON.stringify(r)).join("\n") + "\n");

  const items = [];
  const calibrationPool = new Map(ARMS.map(arm => [arm, []]));
  for (const arm of ARMS) {
    const gens = generations.get(arm);
    const js = judges.get(arm);
    for (const row of sampleRows) {
      const sense = senseRows.find(r => r.slp1 === row.slp1);
      const gen = gens.get(row.slp1);
      if (!sense || !gen) continue;
      const genSegs = glossSegments(gen.gloss);
      const goldSegs = glossSegments(row.gold_gloss);
      const otherMax = sense.other_max;
      const availableOther = OTHER_DICTS.filter(d => sense.units[d] != null);
      const distinction = availableOther.length ? otherMax >= 2 : null;
      const preserved = distinction == null ? null : genSegs.length >= 2;
      const coverage = availableOther.length && otherMax >= 1
        ? Math.min(genSegs.length, otherMax) / otherMax
        : null;
      const mwMonoOtherPoly = sense.mw_units != null && sense.mw_units <= 1 && otherMax >= 2;
      const countF1 = availableOther.length && otherMax >= 1
        ? (() => {
            const g = genSegs.length;
            const o = otherMax;
            const m = Math.min(g, o);
            const precision = g ? m / g : 0;
            const recall = o ? m / o : 0;
            return precision + recall ? (2 * precision * recall) / (precision + recall) : 0;
          })()
        : null;
      const item = {
        arm,
        slp1: row.slp1,
        iast: row.iast,
        freq_band: row.freq_band,
        poly_band: row.poly_band,
        cell: `${row.freq_band}/${row.poly_band}`,
        mw_units: sense.mw_units,
        ap_units: sense.units.ap,
        pwg_units: sense.units.pwg,
        pw_units: sense.units.pw,
        other_max: otherMax,
        other_dicts_available: availableOther.join("+"),
        gen_segments: genSegs.length,
        gold_segments: goldSegs.length,
        crossdict_distinction: distinction,
        distinction_preserved: preserved,
        coverage_ratio: round(coverage, 4),
        count_f1: round(countF1, 4),
        mw_mono_other_poly: mwMonoOtherPoly,
        judge_adequacy: js.get(row.slp1) ?? null,
        gloss: gen.gloss || "",
        gold_gloss: row.gold_gloss || ""
      };
      items.push(item);
      if (availableOther.length && row.gold_gloss) calibrationPool.get(arm).push(item);
    }
  }

  const perItemHeader = [
    "arm", "slp1", "iast", "freq_band", "poly_band", "cell",
    "mw_units", "ap_units", "pwg_units", "pw_units", "other_max",
    "other_dicts_available", "gen_segments", "gold_segments",
    "crossdict_distinction", "distinction_preserved", "coverage_ratio",
    "count_f1", "mw_mono_other_poly", "judge_adequacy"
  ];
  fs.writeFileSync(OUT_ITEMS, [
    perItemHeader.join(","),
    ...items.map(row => perItemHeader.map(k => csvEscape(row[k])).join(","))
  ].join("\n") + "\n");

  const summarize = rows => {
    const other = rows.filter(r => r.other_dicts_available);
    const distinction = other.filter(r => r.crossdict_distinction);
    const monoGap = other.filter(r => r.mw_mono_other_poly);
    const adequate = r => r.judge_adequacy != null && r.judge_adequacy >= 3;
    const adequateDistinction = distinction.filter(adequate);
    return {
      n: rows.length,
      n_with_other_dict: other.length,
      crossdict_distinction_n: distinction.length,
      crossdict_distinction_rate: other.length ? round(distinction.length / other.length) : null,
      distinction_preserved_n: distinction.filter(r => r.distinction_preserved).length,
      distinction_preserved_rate: distinction.length
        ? round(distinction.filter(r => r.distinction_preserved).length / distinction.length)
        : null,
      mw_mono_other_poly_n: monoGap.length,
      mw_mono_other_poly_preserved_n: monoGap.filter(r => r.distinction_preserved).length,
      mw_mono_other_poly_preserved_rate: monoGap.length
        ? round(monoGap.filter(r => r.distinction_preserved).length / monoGap.length)
        : null,
      distinction_preserved_adequate_n: adequateDistinction.filter(r => r.distinction_preserved).length,
      distinction_preserved_adequate_rate: distinction.length
        ? round(adequateDistinction.filter(r => r.distinction_preserved).length / distinction.length)
        : null,
      mean_count_f1: round(mean(other.map(r => r.count_f1))),
      mean_coverage_ratio: round(mean(other.map(r => r.coverage_ratio))),
      mean_gen_segments: round(mean(rows.map(r => r.gen_segments))),
      mean_gold_segments: round(mean(rows.map(r => r.gold_segments))),
      mean_judge_adequacy: round(mean(rows.map(r => r.judge_adequacy)))
    };
  };

  const byArm = {};
  for (const arm of ARMS) byArm[arm] = summarize(items.filter(r => r.arm === arm));
  const byCell = {};
  for (const cell of [...new Set(items.map(r => r.cell))].sort()) {
    byCell[cell] = {};
    for (const arm of ARMS) byCell[cell][arm] = summarize(items.filter(r => r.arm === arm && r.cell === cell));
  }

  const frozenScores = parseTsv(fs.readFileSync(path.join(DIR, "scores_per_item.tsv"), "utf8"));
  const baseline = {};
  for (const arm of ARMS) {
    const rows = frozenScores.filter(r => r.arm === arm);
    baseline[arm] = {
      n: rows.length,
      mean_sent_chrf: round(mean(rows.map(r => Number(r.chrf)))),
      mean_sent_bleu: round(mean(rows.map(r => Number(r.bleu)))),
      mean_token_f1: round(mean(rows.map(r => Number(r.token_f1)))),
      source: "data/eval/crossdict-defgen/scores_per_item.tsv (frozen kosha H730/H2408 scorer)"
    };
  }

  const inputFiles = [
    "frozen_sample.tsv", "frozen_sample.meta.json", "scores_per_item.tsv", "scores_summary.json",
    ...ARMS.map(a => `generations/gen_${a}.jsonl`),
    ...ARMS.map(a => `judge/judge_${a}.jsonl`)
  ];
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    dataset: "h7104_crossdict_defgen_eval",
    goal: "H7104",
    purpose: "Cross-dictionary sense-consistency test of frozen MW definition-generation arms without re-running generation.",
    generatedAt: process.env.CSL_ATLAS_GENERATED_AT || new Date().toISOString(),
    seed: SEED,
    sourceProvenance: {
      koshaDefgen: {
        path: "gasyoun/kosha data/eval/defgen",
        status: "frozen-kosha-H730/H2408; consumed read-only, not regenerated",
        inputs: Object.fromEntries(inputFiles.map(f => [f, sha256(path.join(DIR, f))]))
      },
      senseAudit: {
        handoff: "H7098",
        method: "H7098 committed sense adapters (mw-sense-section-div, ap-bullet-sense-marker, pwg-div-sense-marker, pwk-div-sense-marker)",
        source: "../csl-orig/v02",
        availability
      }
    },
    design: {
      sample: "frozen 500-headword MW defgen sample (seed 730)",
      arms: ARMS,
      crossdict_reference: OTHER_DICTS,
      distinction_definition: "other_max >= 2, where other_max is the richest sense-unit count among AP/PWG/PWK",
      preserved_definition: "generated gloss has >= 2 segments after splitting on | or ;",
      coverage_definition: "min(gen_segments, other_max) / other_max",
      count_f1_definition: "harmonic mean of count precision min(gen,other)/gen and recall min(gen,other)/other; penalises both lost distinctions and synonym dumps",
      adequacy_gate: "judge adequacy >= 3; the adequacy-gated preservation rate is the primary endpoint because a random synonym dump can satisfy a raw count threshold",
      mw_mono_other_poly_definition: "MW <= 1 sense unit while AP/PWG/PWK reaches >= 2",
      contamination_caveat: "Generation and the LLM judge saw MW context/gold; MW-gold BLEU/chrF and judge adequacy are contaminated by construction. The cross-dictionary test is the primary endpoint, but PWG/PWK/AP share historical material and citation stock with MW, so independence is partial, not absolute."
    },
    summary: { overall: summarize(items), byArm, byCell },
    baseline,
    senseCoverage: {
      lemmas_with_any_core_sense_unit: senseRows.filter(r => CORE_SENSE_DICTS.some(d => r.units[d] != null)).length,
      lemmas_with_other_dict: senseRows.filter(r => OTHER_DICTS.some(d => r.units[d] != null)).length,
      lemmas_crossdict_distinction: senseRows.filter(r => r.other_max >= 2).length,
      lemmas_mw_mono_other_poly: senseRows.filter(r => r.mw_units != null && r.mw_units <= 1 && r.other_max >= 2).length
    },
    limitations: [
      "Sense units are structural marker counts, not curated sense inventories.",
      "The defgen sample is MW-derived and MW-stratified; cross-dictionary reference coverage is uneven.",
      "No generation was re-run; the five frozen arms are evaluated as delivered.",
      "Judges are LLM judges; the 100-row single-key manual calibration was scored by the executing worker, not an independent human."
    ]
  };

  if (resetCalibration || !fs.existsSync(OUT_CAL_SAMPLE)) {
    const picked = calibrationRows(calibrationPool);
    const calHeader = ["sample_id", "arm", "slp1", "iast", "cell", "judge_adequacy", "worker_adequacy", "gold_gloss", "gloss"];
    fs.writeFileSync(OUT_CAL_SAMPLE, [
      calHeader.join(","),
      ...picked.map((r, i) => {
        const sampleId = `H7104-CAL-${String(i + 1).padStart(3, "0")}`;
        const values = { ...r, sample_id: sampleId, worker_adequacy: "" };
        return calHeader.map(k => csvEscape(values[k])).join(",");
      })
    ].join("\n") + "\n");
  }

  const calibration = { status: "sample-built", n: 0, worker_file: path.relative(process.cwd(), WORKER_FILE) };
  if (fs.existsSync(WORKER_FILE)) {
    const worker = new Map(parseTsv(fs.readFileSync(WORKER_FILE, "utf8"))
      .filter(r => /^[0-5]$/.test((r.worker_adequacy || "").trim()))
      .map(r => [r.sample_id, Number(r.worker_adequacy)]));
    const sample = parseCsv(fs.readFileSync(OUT_CAL_SAMPLE, "utf8"));
    const pairs = [];
    const byArmPairs = {};
    for (const row of sample) {
      const h = worker.get(row.sample_id);
      const j = Number(row.judge_adequacy);
      if (h == null || !Number.isFinite(j)) continue;
      pairs.push([j, h]);
      (byArmPairs[row.arm] ||= []).push([j, h]);
    }
    const qwk = quadraticWeightedKappa(pairs);
    Object.assign(calibration, {
      status: pairs.length === sample.length ? "single-key-worker-scored" : "partially-single-key-worker-scored",
      n: pairs.length,
      n_sample: sample.length,
      exact_agreement: pairs.length ? round(pairs.filter(([a, b]) => a === b).length / pairs.length) : null,
      within_one_agreement: pairs.length ? round(pairs.filter(([a, b]) => Math.abs(a - b) <= 1).length / pairs.length) : null,
      mean_worker: round(mean(pairs.map(p => p[1]))),
      mean_judge: round(mean(pairs.map(p => p[0]))),
      quadratic_weighted_kappa: qwk.kappa,
      pearson: pearson(pairs),
      spearman: spearman(pairs),
      byArm: Object.fromEntries(Object.entries(byArmPairs).map(([arm, ps]) => [arm, {
        n: ps.length,
        exact_agreement: round(ps.filter(([a, b]) => a === b).length / ps.length),
        within_one_agreement: round(ps.filter(([a, b]) => Math.abs(a - b) <= 1).length / ps.length),
        quadratic_weighted_kappa: quadraticWeightedKappa(ps).kappa
      }])),
      humanGoldStatus: "blocked",
      calibrationBasis: "one blind manual key scored by the executing worker, not an independent human; provisional until two human keys plus adjudication",
      rubric: {
        scale: "1-5 adequacy against the MW gold gloss and the joined AP/PWG/PWK sense units",
        "5": "all main senses preserved; no invented sense",
        "4": "main senses preserved; one minor sense or nuance missing",
        "3": "core sense present; at least one cross-dictionary distinction lost",
        "2": "only a partial/related sense; main sense missing",
        "1": "wrong sense",
        "0": "empty or unusable",
        blinding: "Human scorer sees slp1, gold gloss and generated gloss only; judge score is hidden during scoring."
      }
    });
  }
  payload.judgeCalibration = calibration;

  payload.verdict = decideVerdict(byArm, calibration);
  fs.writeFileSync(OUT_SCORES, JSON.stringify(payload, null, 2) + "\n");
  fs.writeFileSync(OUT_CAL, JSON.stringify({ schemaVersion: SCHEMA_VERSION, ...licenseFields(), goal: "H7104", ...calibration }, null, 2) + "\n");
  console.log(`wrote ${OUT_SCORES}`);
  console.log(JSON.stringify(payload.verdict, null, 2));
}

main();
