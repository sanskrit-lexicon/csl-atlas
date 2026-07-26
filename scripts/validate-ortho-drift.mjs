// Validate the committed ortho-drift census (H1577, PH5 ORTHO-CLOCK).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// sibling inputs (SanskritSpellCheck maps, csl-orig text, Kossovich jsonl)
// are not on CI runners, so no rebuild is attempted there — spot-recount
// notes are emitted only when the siblings are present.
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - any dictionary's driftPer1k or preShare disagrees with its own
//   pre/post/token counts, or a CI does not bracket its point estimate;
// - German dicts are not distinct codes with numeric mid-years, or the
//   regression residuals disagree with the fitted line;
// - the verdict block disagrees with the recorded statistics (clock verdict
//   vs Spearman sign; descent verdict vs the CCS-GRA pair test);
// - pair-test / Spearman p-values fall outside (0,1];
// - topForms per-dict counts exceed the owning dictionary's preHits.
//
// Usage: npm run validate-ortho-drift   (run after build-ortho-drift)

import fs from "node:fs";
import path from "node:path";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "ortho_drift.json");
const SOURCE_OUT = path.join(OUT_DIR, "ortho_drift.source.json");
const SYNCED_COPY = path.resolve(process.cwd(), "src", "data", "lexico", "ortho_drift.json");
const DE_MAP = path.resolve(process.cwd(), "..", "SanskritSpellCheck", "ortho_drift", "de_reform_map.tsv");

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

function checkDict(d, lane) {
  const drift = (d.preHitsDated / d.tokens) * 1000;
  if (Math.abs(drift - d.driftPer1k) > 0.001) errors.push(`${lane} ${d.code}: driftPer1k ${d.driftPer1k} != ${drift.toFixed(4)} from dated counts`);
  const driftAll = (d.preHitsAllMap / d.tokens) * 1000;
  if (Math.abs(driftAll - d.driftPer1kAllMap) > 0.001) errors.push(`${lane} ${d.code}: driftPer1kAllMap ${d.driftPer1kAllMap} != ${driftAll.toFixed(4)} from counts`);
  const share = d.preHitsAllMap / (d.preHitsAllMap + d.postHits);
  if (Math.abs(share - d.preShare) > 0.001) errors.push(`${lane} ${d.code}: preShare ${d.preShare} != ${share.toFixed(4)} from counts`);
  const eraSum = Object.values(d.eras ?? {}).reduce((a, v) => a + v, 0);
  if (eraSum !== d.preHitsAllMap) errors.push(`${lane} ${d.code}: era counts sum ${eraSum} != preHitsAllMap ${d.preHitsAllMap}`);
  const datedSum = eraSum - (d.eras?.["other-map-era"] ?? 0);
  if (datedSum !== d.preHitsDated) errors.push(`${lane} ${d.code}: dated era sum ${datedSum} != preHitsDated ${d.preHitsDated}`);
  for (const [name, ci] of Object.entries(d.ci ?? {})) {
    if (!ci) continue;
    const point = name === "driftPer1k" ? d.driftPer1k : d.preShare;
    if (!(ci[0] <= point && point <= ci[1])) errors.push(`${lane} ${d.code}: ${name} CI [${ci}] does not bracket ${point}`);
    if (!(ci[0] <= ci[1])) errors.push(`${lane} ${d.code}: ${name} CI inverted`);
  }
  if (d.preHitsDated > d.preHitsAllMap) errors.push(`${lane} ${d.code}: preHitsDated ${d.preHitsDated} > preHitsAllMap ${d.preHitsAllMap}`);
  if (d.preHitsAllMap > d.tokens) errors.push(`${lane} ${d.code}: preHitsAllMap ${d.preHitsAllMap} > tokens ${d.tokens}`);
}

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);

if (packet) {
  const de = packet.german?.dicts ?? [];
  const ru = packet.russian?.dicts ?? [];
  if (de.length < 5) errors.push(`German roster has ${de.length} dicts — expected at least the Petersburg line + controls`);
  const codes = new Set(de.map((d) => d.code));
  if (codes.size !== de.length) errors.push("duplicate German dictionary codes");
  for (const d of de) {
    checkDict(d, "german");
    if (!Number.isFinite(d.midYear)) errors.push(`german ${d.code}: non-numeric midYear`);
    if (!["progenitor", "descendant", "independent"].includes(d.lineage)) errors.push(`german ${d.code}: unknown lineage ${d.lineage}`);
  }
  for (const d of ru) checkDict(d, "russian");

  const reg = packet.german?.regression ?? {};
  for (const r of reg.residuals ?? []) {
    const d = de.find((x) => x.code === r.code);
    if (!d) {
      errors.push(`regression residual for unknown dict ${r.code}`);
      continue;
    }
    const expected = d.driftPer1k - (reg.intercept + reg.slopePer1kPerYear * d.midYear);
    if (Math.abs(expected - r.residual) > 0.01) errors.push(`residual ${r.code}: ${r.residual} != ${expected.toFixed(4)} from the fitted line`);
  }
  if (!(reg.spearmanExactPTwoSided > 0 && reg.spearmanExactPTwoSided <= 1)) errors.push(`spearman p ${reg.spearmanExactPTwoSided} outside (0,1]`);
  if (reg.spearmanPermutations && de.length && reg.spearmanPermutations !== factorial(de.length)) {
    errors.push(`spearman permutations ${reg.spearmanPermutations} != ${de.length}! — not exhaustive`);
  }

  for (const t of packet.german?.pairTests ?? []) {
    if (!(t.pOneSided > 0 && t.pOneSided <= 1)) errors.push(`pair ${t.a}->${t.b}: p ${t.pOneSided} outside (0,1]`);
    const a = de.find((x) => x.code === t.a);
    const b = de.find((x) => x.code === t.b);
    if (a && b && Math.abs(b.driftPer1k - a.driftPer1k - t.diffPer1k) > 0.01) {
      errors.push(`pair ${t.a}->${t.b}: diffPer1k ${t.diffPer1k} != ${b.driftPer1k} - ${a.driftPer1k}`);
    }
  }

  const verdict = packet.verdict ?? {};
  const rho = reg.spearmanRho;
  const p = reg.spearmanExactPTwoSided;
  const expectedClock = rho < 0 && p <= 0.05 ? "supported" : rho < 0 ? "direction-consistent-inconclusive" : "not-supported";
  if (verdict.clock !== expectedClock) errors.push(`clock verdict "${verdict.clock}" disagrees with rho ${rho}, p ${p} (expected "${expectedClock}")`);
  const descentPair = (packet.german?.pairTests ?? []).find((t) => t.a === "gra" && t.b === "ccs");
  if (descentPair && verdict.descent === "supported" && !(descentPair.diffPer1k > 0 && descentPair.pOneSided < 0.05)) {
    errors.push("descent verdict 'supported' disagrees with the CCS-GRA pair test");
  }
  if (descentPair && verdict.descent === "refuted" && descentPair.diffPer1k > 0 && descentPair.pOneSided < 0.05) {
    errors.push("descent verdict 'refuted' disagrees with the CCS-GRA pair test");
  }

  for (const f of packet.german?.topForms ?? []) {
    for (const d of de) {
      if ((f[d.code] ?? 0) > d.preHitsAllMap) errors.push(`topForm ${f.old}: count ${f[d.code]} for ${d.code} exceeds its preHitsAllMap`);
    }
    if (f.total !== de.reduce((a, d) => a + (f[d.code] ?? 0), 0)) {
      // total is across the censused roster only when every dict column is present
      const sum = de.reduce((a, d) => a + (f[d.code] ?? 0), 0);
      errors.push(`topForm ${f.old}: total ${f.total} != per-dict sum ${sum}`);
    }
  }
}

function factorial(n) {
  let out = 1;
  for (let i = 2; i <= n; i++) out *= i;
  return out;
}

if (envelope && packet && envelope.generatedAt !== packet.generatedAt) {
  errors.push(`source envelope generatedAt ${envelope.generatedAt} != packet generatedAt ${packet.generatedAt}`);
}

if (packet && fs.existsSync(SYNCED_COPY)) {
  const synced = readJson(SYNCED_COPY);
  if (synced && JSON.stringify(synced) !== JSON.stringify(packet)) {
    errors.push("src/data/lexico/ortho_drift.json (site copy) differs from data/lexico/ortho_drift.json — run npm run sync-site-data");
  }
}

if (fs.existsSync(DE_MAP)) {
  const mapForms = fs
    .readFileSync(DE_MAP, "utf8")
    .split(/\r?\n/)
    .filter((l) => l && !l.startsWith("#") && l.includes("\t")).length;
  if (packet && packet.german?.referenceMap?.forms !== mapForms) {
    errors.push(`referenceMap.forms ${packet.german?.referenceMap?.forms} != live de_reform_map.tsv row count ${mapForms} — rerun npm run build-ortho-drift`);
  }
  notes.push("sibling SanskritSpellCheck present: live map row-count cross-check ran");
} else {
  notes.push("sibling SanskritSpellCheck checkout absent: internal-consistency checks only (expected on CI)");
}

for (const note of notes) console.log(`note: ${note}`);
if (errors.length > 0) {
  console.error(`validate-ortho-drift: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-ortho-drift: OK");
