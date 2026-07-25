// Validate the committed ghost-stock packet (H1575, PH4 + PH6).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// cross-check against the sibling SanskritLexicography union/crosswalk runs
// only when that checkout is present (it is not on CI runners).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - byMultiplicity strata don't sum to the union totals, a stratum rate
//   disagrees with its counts, or a Wilson bound doesn't bracket its rate;
// - perDict unique/uniqueAttested sums disagree with the n_dicts=1 stratum;
// - the 2x2x2 cube doesn't sum to mwLemmas, or the triple-filter queue length
//   disagrees with its cube cell / totals row;
// - the triple-filter grade is not `inferred` (the honesty gate);
// - the logistic block did not converge or carries non-finite terms;
// - (sibling present) rebuilding from the live inputs disagrees with the
//   committed totals.
//
// Usage: npm run validate-ghost-stock   (run after build-ghost-stock)

import fs from "node:fs";
import path from "node:path";
import { parseTsv } from "./build-heritage-witness.mjs";
import { buildPayload } from "./build-ghost-stock.mjs";
import { parseDcsSummaryFile } from "./lib/dcs-summary.mjs";
import { loadDictionaryInventory } from "./lib/dict-scope.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "ghost-stock");
const JSON_OUT = path.join(OUT_DIR, "ghost_stock.json");
const SOURCE_OUT = path.join(OUT_DIR, "ghost_stock.source.json");
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "SanskritLexicography");
const UNION_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "union", "union_headwords.tsv");
const CROSSWALK_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "mw_heritage_crosswalk.tsv");
const DCS_SUMMARY_PATH = path.resolve(process.cwd(), "data", "dcs", "dcs_lemma_summary.json");

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

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);

if (packet) {
  const t = packet.totals ?? {};

  let sumLemmas = 0;
  let sumAttested = 0;
  for (const row of packet.byMultiplicity ?? []) {
    sumLemmas += row.lemmas;
    sumAttested += row.attested;
    if (Math.abs(row.attested / row.lemmas - row.rate) > 0.0011) {
      errors.push(`byMultiplicity n_dicts=${row.nDicts}: rate ${row.rate} != attested/lemmas`);
    }
    if (!(row.ciLo >= 0 && row.ciLo <= row.rate + 0.0011 && row.rate <= row.ciHi + 0.0011 && row.ciHi <= 1)) {
      errors.push(`byMultiplicity n_dicts=${row.nDicts}: Wilson CI [${row.ciLo}, ${row.ciHi}] does not bracket rate ${row.rate}`);
    }
  }
  if (sumLemmas !== t.unionLemmas) errors.push(`byMultiplicity lemmas sum ${sumLemmas} != totals.unionLemmas ${t.unionLemmas}`);
  if (sumAttested !== t.unionAttested) errors.push(`byMultiplicity attested sum ${sumAttested} != totals.unionAttested ${t.unionAttested}`);
  if (Math.abs(t.unionAttested / t.unionLemmas - t.attestedPct) > 0.0011) {
    errors.push(`totals.attestedPct ${t.attestedPct} != unionAttested/unionLemmas`);
  }

  const stratum1 = (packet.byMultiplicity ?? []).find((r) => r.nDicts === 1);
  let sumUnique = 0;
  let sumUniqueAttested = 0;
  for (const d of packet.perDict ?? []) {
    sumUnique += d.unique;
    sumUniqueAttested += d.uniqueAttested;
    if (d.uniqueAttested > d.unique || d.unique > d.lemmas) {
      errors.push(`perDict ${d.code}: uniqueAttested ${d.uniqueAttested} / unique ${d.unique} / lemmas ${d.lemmas} out of order`);
    }
    if (!d.family) errors.push(`perDict ${d.code}: missing family`);
  }
  if (stratum1 && sumUnique !== stratum1.lemmas) {
    errors.push(`perDict unique sum ${sumUnique} != n_dicts=1 stratum lemmas ${stratum1.lemmas}`);
  }
  if (stratum1 && sumUniqueAttested !== stratum1.attested) {
    errors.push(`perDict uniqueAttested sum ${sumUniqueAttested} != n_dicts=1 stratum attested ${stratum1.attested}`);
  }

  const cube = packet.heritageCube ?? {};
  const cells = cube.cells ?? [];
  if (cells.length !== 8) errors.push(`heritageCube has ${cells.length} cells, expected 8`);
  const cubeSum = cells.reduce((a, c) => a + c.lemmas, 0);
  if (cubeSum !== t.mwLemmas) errors.push(`heritageCube cells sum ${cubeSum} != totals.mwLemmas ${t.mwLemmas}`);
  const coveredSum = cells.filter((c) => c.heritageCovered).reduce((a, c) => a + c.lemmas, 0);
  if (coveredSum !== t.mwHeritageCovered) {
    errors.push(`heritageCube covered sum ${coveredSum} != totals.mwHeritageCovered ${t.mwHeritageCovered}`);
  }
  const uniqueSum = cells.filter((c) => c.mwUnique).reduce((a, c) => a + c.lemmas, 0);
  if (uniqueSum !== t.mwUnique) errors.push(`heritageCube mwUnique sum ${uniqueSum} != totals.mwUnique ${t.mwUnique}`);
  const tripleCell = cells.find((c) => c.mwUnique && !c.heritageCovered && !c.dcsAttested);
  for (const or of cube.oddsRatios ?? []) {
    if (!(or.oddsRatio > 0) || !(or.ciLo <= or.oddsRatio && or.oddsRatio <= or.ciHi)) {
      errors.push(`heritageCube odds ratio "${or.contrast}": CI [${or.ciLo}, ${or.ciHi}] does not bracket ${or.oddsRatio}`);
    }
  }

  const tf = packet.tripleFilter ?? {};
  if (tf.evidenceGrade !== "inferred") errors.push(`tripleFilter.evidenceGrade ${tf.evidenceGrade} != inferred`);
  const queueLen = (tf.explicitUncovered?.length ?? 0) + (tf.crosswalkMissing?.length ?? 0);
  if (queueLen !== tf.total) errors.push(`tripleFilter queue length ${queueLen} != tripleFilter.total ${tf.total}`);
  if (tf.total !== t.tripleFilter) errors.push(`tripleFilter.total ${tf.total} != totals.tripleFilter ${t.tripleFilter}`);
  if (tripleCell && tripleCell.lemmas !== tf.total) {
    errors.push(`triple-filter cube cell ${tripleCell.lemmas} != tripleFilter.total ${tf.total}`);
  }

  const l = packet.logistic ?? {};
  if (l.converged !== true) errors.push("logistic fit did not converge");
  if (l.n !== t.unionLemmas) errors.push(`logistic.n ${l.n} != totals.unionLemmas ${t.unionLemmas}`);
  for (const term of l.terms ?? []) {
    if (!Number.isFinite(term.estimate) || !Number.isFinite(term.se)) {
      errors.push(`logistic term ${term.term}: non-finite estimate/se`);
    }
  }

  // Sibling cross-check, only when the live inputs are all present.
  if (fs.existsSync(UNION_PATH) && fs.existsSync(CROSSWALK_PATH) && fs.existsSync(DCS_SUMMARY_PATH)) {
    const rebuilt = buildPayload(
      parseTsv(fs.readFileSync(UNION_PATH, "utf8")),
      parseDcsSummaryFile(DCS_SUMMARY_PATH),
      parseTsv(fs.readFileSync(CROSSWALK_PATH, "utf8")),
      loadDictionaryInventory(),
      { generatedAt: packet.generatedAt }
    );
    for (const key of ["unionLemmas", "unionAttested", "mwLemmas", "mwUnique", "mwHeritageCovered", "tripleFilter"]) {
      if (rebuilt.totals[key] !== t[key]) {
        errors.push(`sibling rebuild: totals.${key} ${rebuilt.totals[key]} != committed ${t[key]} — rerun npm run build-ghost-stock`);
      }
    }
    notes.push("sibling cross-check ran (full rebuild from union + crosswalk + DCS summary)");
  } else {
    notes.push("sibling SanskritLexicography checkout absent — internal-consistency checks only (expected on CI)");
  }
}

if (envelope) {
  if (envelope.dataset !== "ghost_stock") errors.push(`envelope dataset ${envelope.dataset} != ghost_stock`);
  if (!envelope.siblingCommit) errors.push("envelope missing siblingCommit");
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length > 0) {
  console.error(`validate-ghost-stock FAILED (${errors.length}):`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-ghost-stock OK");
