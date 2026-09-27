// Measure how far each learner-card layer actually reaches — the coverage table in
// docs/LEARNER_LAYER_V1_SPEC.md §8. Read-only; not part of any build.
//
// Two inputs live in sibling repos and are consumed, never re-derived:
//   VisualDCS     learner-contracts-v1 payloads (paradigms)  — VDCS_REPO
//   WhitneyRoots  crosswalk/roots.csv + root_class.csv       — WHITNEY_REPO
// Defaults assume the standard ~/Documents/GitHub/ layout; override with env vars.
// Re-measure after any input refresh rather than trusting the numbers in the spec.
//
// Usage: node scripts/measure-learner-layer-coverage.mjs
import fs from "node:fs";
import { slp1ToIast } from "../src/lib/lookup-normalize.js";

const VDCS = process.env.VDCS_REPO ?? "../VisualDCS";
const WR = process.env.WHITNEY_REPO ?? "../WhitneyRoots";
for (const [label, dir] of [["VisualDCS", VDCS], ["WhitneyRoots", WR]]) {
  if (!fs.existsSync(dir)) {
    console.error(`${label} not found at ${dir} — set ${label === "VisualDCS" ? "VDCS_REPO" : "WHITNEY_REPO"}.`);
    process.exit(2);
  }
}
const rd = p => JSON.parse(fs.readFileSync(p, "utf8"));

const idx = rd("src/data/learner/learner-index.json");
const lemmas = idx.entries.map(e => e.l);
const iastOf = new Map(lemmas.map(l => [l, slp1ToIast(l)]));
console.log("learner-index lemmas:", lemmas.length);
console.log("  counts:", JSON.stringify(idx.counts));

// --- VisualDCS nominal paradigm join (IAST keys) ---
const nom = rd(`${VDCS}/visual/contracts/v1/nominal-trainer.json`);
const nomByIast = new Map();
for (const l of nom.lemmas) {
  if (!nomByIast.has(l.lemma)) nomByIast.set(l.lemma, []);
  nomByIast.get(l.lemma).push(l.lemmaId);
}
let nomHit = 0, nomAmbig = 0;
for (const l of lemmas) {
  const ids = nomByIast.get(iastOf.get(l));
  if (ids) { nomHit++; if (ids.length > 1) nomAmbig++; }
}
console.log(`nominal-trainer: ${nom.lemmaCount} lemmas; distinct IAST ${nomByIast.size}; ` +
  `atlas hit ${nomHit} (${(100 * nomHit / lemmas.length).toFixed(1)}%), of which multi-lemmaId ${nomAmbig}`);

// --- VisualDCS verb paradigm join (root IAST) ---
const vb = rd(`${VDCS}/visual/contracts/v1/verb-trainer.json`);
const vbRoots = new Set(vb.roots.map(r => r.rootId));
let vbHit = 0;
for (const l of lemmas) if (vbRoots.has(iastOf.get(l))) vbHit++;
console.log(`verb-trainer: ${vb.rootCount} roots; atlas lemma hit ${vbHit}`);

// --- Whitney roots + gana ---
const csv = s => s.trim().split(/\r?\n/).map(r => {
  const out = []; let cur = "", q = false;
  for (const ch of r) {
    if (ch === '"') q = !q; else if (ch === "," && !q) { out.push(cur); cur = ""; } else cur += ch;
  }
  out.push(cur); return out;
});
const rootsRows = csv(fs.readFileSync(`${WR}/crosswalk/roots.csv`, "utf8"));
const rh = rootsRows[0];
const col = n => rh.indexOf(n);
const roots = rootsRows.slice(1).map(r => ({
  no: r[col("whitney_no")], slp1: r[col("root_slp1")], iast: r[col("root_iast")],
  hom: r[col("homonym")], cls: r[col("class")], clsUnc: r[col("class_uncertain")]
}));
const classRows = csv(fs.readFileSync(`${WR}/crosswalk/root_class.csv`, "utf8"));
const ch = classRows[0];
const ganaByNo = new Map(classRows.slice(1).map(r => [r[ch.indexOf("whitney_no")],
  { gana: r[ch.indexOf("gana")], certainty: r[ch.indexOf("certainty")] }]));
const rootsBySlp1 = new Map();
for (const r of roots) {
  if (!rootsBySlp1.has(r.slp1)) rootsBySlp1.set(r.slp1, []);
  rootsBySlp1.get(r.slp1).push(r);
}
let wrHit = 0, wrHom = 0, wrGana = 0;
for (const l of lemmas) {
  const rs = rootsBySlp1.get(l);
  if (!rs) continue;
  wrHit++;
  if (rs.length > 1) wrHom++;
  if (rs.some(r => ganaByNo.has(r.no) || r.cls)) wrGana++;
}
const inClass = roots.filter(r => ganaByNo.has(r.no) || r.cls).length;
console.log(`Whitney roots.csv: ${roots.length} roots; distinct SLP1 ${rootsBySlp1.size}; ` +
  `with gana ${inClass}; root_class.csv rows ${ganaByNo.size}`);
console.log(`  atlas lemma == Whitney root (SLP1 exact): ${wrHit}; homonym-ambiguous ${wrHom}; with gana ${wrGana}`);

// --- P2 survival panel ---
const h2 = rd("data/lexico/r2_h2h3.json");
const senses = rd("data/lexico/r2_h2_senses.json");
const panel = new Set(h2.panel);
const panelInAtlas = [...panel].filter(p => iastOf.has(p));
const panelLemmasWithRows = new Set(senses.rows.map(r => r.lemma));
console.log(`P2 survival: panel ${panel.size} lemmas; per-sense rows ${senses.rows.length}; ` +
  `lemmas with rows ${panelLemmasWithRows.size}; panel lemmas present in learner index ${panelInAtlas.length}`);
console.log(`  survival coverage of learner index: ${(100 * panelInAtlas.length / lemmas.length).toFixed(4)}%`);

// --- homonym split ---
const hs = rd("src/data/dicts/homonym-split.json");
console.log(`homonym-split: candidateCount ${hs.candidateCount}, shipped rows ${hs.shown}`);
const hsLemmas = new Set(hs.candidates.map(c => c.lemma));
let hsHit = 0;
for (const l of lemmas) if (hsLemmas.has(l)) hsHit++;
console.log(`  shipped homonym rows matching a learner lemma: ${hsHit}`);

// --- all four together ---
let all4 = 0, three = 0;
for (const l of lemmas) {
  const i = iastOf.get(l);
  const n = nomByIast.has(i) || vbRoots.has(i);
  const w = rootsBySlp1.has(l);
  const s = panel.has(l);
  const f = true;
  const k = [n, w, s, f].filter(Boolean).length;
  if (k === 4) all4++; else if (k === 3) three++;
}
console.log(`cards with all four layers: ${all4}; with three: ${three}`);

// --- card completeness tiers ---
const tier = { A: 0, B: 0, C: 0, D: 0 };
let freqOnly = 0;
for (const e of idx.entries) {
  const i = iastOf.get(e.l);
  const para = nomByIast.has(i) || vbRoots.has(i);
  const root = rootsBySlp1.has(e.l);
  const surv = panel.has(e.l);
  if (surv) tier.A++;
  else if (para && root) tier.B++;
  else if (para || root) tier.C++;
  else { tier.D++; if (e.fb > 0) freqOnly++; }
}
console.log("card tiers:", JSON.stringify(tier), "(tier D with a freq band:", freqOnly, ")");
const panelPara = [...panel].filter(p => nomByIast.has(slp1ToIast(p)) || vbRoots.has(slp1ToIast(p))).length;
const panelRoot = [...panel].filter(p => rootsBySlp1.has(p)).length;
console.log(`P2 panel: with paradigm ${panelPara}/28; that are Whitney roots ${panelRoot}/28`);
