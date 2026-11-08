// Build the learner's reading-layer index (v1).
//
// v0 joined the reader lemma-lookup (dictionary coverage + gender) with the DCS
// corpus frequency band. v1 closes the v0 header's honest-scope sentence: it
// adds the three missing layers per docs/LEARNER_LAYER_V1_SPEC.md —
//   survival-ranked senses  (P2 panel, data/lexico/r2_h2{h3,_senses}.json)
//   root + gaṇa             (WhitneyRoots crosswalk, consumed never re-derived)
//   paradigm link           (VisualDCS learner-contracts-v1, pinned + verified)
// plus the card completeness tier and named absences (closed vocabulary).
//
// The join is one normalised SLP1 lemma key; VisualDCS is joined through
// slp1ToIast() from src/lib/lookup-normalize.js (SLP1 → IAST only — the
// reverse direction is lossy over accent/anusvāra variants). VisualDCS
// payloads are verified against the pinned release digests and the build
// FAILS CLOSED on a mismatch or an unknown contractVersion. When the sibling
// checkout is absent the build degrades to the v0 card set with a warning;
// when it is present and lying, it stops.
//
// Usage: npm run build-learner-index   (VDCS_REPO / WHITNEY_REPO override the
// sibling paths, default ../VisualDCS and ../WhitneyRoots)

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { loadDcsSummary } from "./lib/dcs-summary.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import {
  SCHEMA_VERSION, VDCS_PIN, SURVIVAL_THRESHOLD, ABSENCE_CODES,
  assignTier, buildParadigmIndexes, loadSurvival, loadWhitney,
  resolveParadigm, survivalCardField, verifyVisualDcsPins, whitneyCardField
} from "./lib/learner-join.mjs";
import { extractSenses, loadDictByStem } from "./build-r2-h2h3.mjs";
import { slp1ToIast } from "../src/lib/lookup-normalize.js";

const ROOT = process.cwd();
const LOOKUP_PATH = path.resolve(ROOT, "src", "data", "dicts", "lemma-lookup.json");
const OUT_DIR = path.resolve(ROOT, "src", "data", "learner");
const OUT_PATH = path.join(OUT_DIR, "learner-index.json");

// Frequency band → learner-facing study priority (self-documenting in the data).
const BAND_LEGEND = [
  { band: 5, range: "1000+", en: "very common", ru: "очень частотное", priorityEn: "learn first", priorityRu: "учить в первую очередь" },
  { band: 4, range: "100–999", en: "common", ru: "частотное", priorityEn: "learn early", priorityRu: "учить рано" },
  { band: 3, range: "10–99", en: "uncommon", ru: "нечастотное", priorityEn: "learn later", priorityRu: "учить позже" },
  { band: 2, range: "2–9", en: "rare", ru: "редкое", priorityEn: "reference", priorityRu: "справочно" },
  { band: 1, range: "1", en: "hapax", ru: "гапакс", priorityEn: "reference", priorityRu: "справочно" },
  { band: 0, range: "—", en: "not in corpus", ru: "нет в корпусе", priorityEn: "uncorroborated", priorityRu: "без корпуса" }
];

const TIER_LEGEND = [
  { tier: "A", en: "full evidence", ru: "полная картина", note: "survival senses present (the 28-lemma P2 panel)" },
  { tier: "B", en: "grammar-complete", ru: "грамматически полный", note: "paradigm and Whitney root" },
  { tier: "C", en: "partial", ru: "частичный", note: "paradigm or Whitney root" },
  { tier: "D", en: "frequency + dictionaries", ru: "частотность и словари", note: "neither paradigm nor root — the majority card; absences are named, not silent" }
];

// The survival caveat travels with the layer everywhere (spec §6): the P2
// effect is edge-concentrated and the clean within-edge test is not
// significant — the card may state per-sense survival, never a population claim.
export const SURVIVAL_CAVEAT =
  "Per-sense survival only: this sense is attested to survive into the later dictionary of the shown edge " +
  "(max gloss-word Jaccard ≥ " + SURVIVAL_THRESHOLD + "). The P2 effect is edge-concentrated (essentially all " +
  "cited senses sit on ap90→ap) and the clean within-edge test is NOT significant (z = 1.80, p = 0.072) — " +
  "no 'cited senses survive more often' population claim is made or implied.";

function grammarReliableTuples(dicts, dictMeta) {
  return [...dicts].filter(t => dictMeta[t[0]]?.grammarReliable).sort((a, b) => a[0] - b[0]);
}

function representativeGender(dicts, dictMeta) {
  // gender from the highest-priority grammar-reliable dictionary that reports one
  for (const t of grammarReliableTuples(dicts, dictMeta)) {
    if (t[3]) return t[3];
  }
  return "";
}

function primarySource(dicts, dictMeta) {
  // [dictCode, firstLine] of the highest-priority grammar-reliable dict present,
  // else the first dict present — a "open this word in the source" pointer.
  const t = grammarReliableTuples(dicts, dictMeta)[0]
    ?? [...dicts].sort((a, b) => a[0] - b[0])[0];
  return t ? [dictMeta[t[0]].code, t[2]] : null;
}

/** Harvest the ancestor sense texts for the P2 panel rows by re-running the
 *  same extraction the P2 build used (single implementation, exported from
 *  scripts/build-r2-h2h3.mjs). Only the panel's ancestor dictionaries are
 *  streamed. Returns { textByKey: Map<"lemma\u001fedge", text|null>, mismatches }.
 *  A missing article or a short sense list yields null — named in warnings,
 *  never fabricated. */
export function harvestSenseText(rowsByLemma, dictLoader = loadDictByStem) {
  const ancestors = new Set();
  for (const rows of rowsByLemma.values()) for (const r of rows) ancestors.add(r.edge.split("→")[0]);
  const bodiesByAnc = new Map();
  for (const anc of ancestors) bodiesByAnc.set(anc, dictLoader(anc));
  const textByKey = new Map();
  let mismatches = 0;
  for (const [lemma, rows] of rowsByLemma) {
    for (const r of rows) {
      const anc = r.edge.split("→")[0];
      const body = bodiesByAnc.get(anc)?.get(lemma) ?? bodiesByAnc.get(anc)?.get(lemma.replace(/[HM]$/, "")) ?? null;
      let text = null;
      if (body) {
        const senses = extractSenses(body, anc);
        if (senses.length > r.position) text = senses[r.position].text;
      }
      if (!text) mismatches += 1;
      textByKey.set(`${lemma}\u001f${r.edge}\u001f${r.position}`, text);
    }
  }
  return { textByKey, mismatches };
}

function main() {
  const lookup = JSON.parse(fs.readFileSync(LOOKUP_PATH, "utf-8"));
  const dcs = loadDcsSummary();
  const dictMeta = Object.fromEntries(lookup.dictionaries.map((d, i) => [i, d]));

  const warnings = [];
  if (!Object.keys(dcs).length) {
    warnings.push("DCS summary absent (data/dcs/dcs_lemma_summary.json); all freqBand = 0.");
  }

  // --- sibling inputs: VisualDCS (I4–I6) + WhitneyRoots (I7–I8), fail-closed ---
  const vdcsRoot = process.env.VDCS_REPO ?? "../VisualDCS";
  const wrRoot = process.env.WHITNEY_REPO ?? "../WhitneyRoots";
  let visualDcs = null;
  let paradigms = null;
  if (fs.existsSync(path.join(vdcsRoot, VDCS_PIN.envelope))) {
    const { manifest, nominal, verb } = verifyVisualDcsPins(vdcsRoot);
    paradigms = buildParadigmIndexes(nominal, verb);
    visualDcs = {
      releaseId: VDCS_PIN.releaseId,
      contractVersion: VDCS_PIN.contractVersion,
      commit: VDCS_PIN.commit,
      envelope: VDCS_PIN.envelope,
      digests: Object.fromEntries(Object.entries(VDCS_PIN.payloads).map(([p, d]) => [path.basename(p), d])),
      counts: { nominalLemmas: nominal.lemmaCount, verbRoots: verb.rootCount },
      manifestGeneratedAt: manifest.generatedAt
    };
  } else {
    warnings.push(`VisualDCS checkout not found at ${vdcsRoot} (set VDCS_REPO); paradigm layer absent for every card (${ABSENCE_CODES.paradigm}).`);
  }

  let whitney = null;
  if (fs.existsSync(path.join(wrRoot, "crosswalk", "roots.csv"))) {
    whitney = loadWhitney(wrRoot);
  } else {
    warnings.push(`WhitneyRoots checkout not found at ${wrRoot} (set WHITNEY_REPO); root/gaṇa layer absent for every card (${ABSENCE_CODES.root}).`);
  }

  // --- P2 survival (I9/I10) + sense-text harvest + homonyms (I11) ---
  const survival = loadSurvival(ROOT);
  const panelRows = new Map([...survival.byLemma].filter(([lemma]) => survival.panel.has(lemma)));
  const { textByKey, mismatches } = harvestSenseText(panelRows);
  if (mismatches) {
    warnings.push(`${mismatches} P2 sense row(s) could not be re-attached to ancestor sense text (article moved or sense count changed since the P2 build); their text is null — named absence, never fabricated.`);
  }
  const homonymSplit = JSON.parse(fs.readFileSync(path.resolve(ROOT, "src", "data", "dicts", "homonym-split.json"), "utf-8"));
  const homonymByLemma = new Map(homonymSplit.candidates.map(c => [c.lemma, c]));

  // --- per-lemma join ---
  const byBand = Object.fromEntries(BAND_LEGEND.map(b => [b.band, 0]));
  const tiers = { A: 0, B: 0, C: 0, D: 0 };
  const coverage = {
    frequency: 0, nominalParadigm: 0, verbParadigm: 0, paradigmTotal: 0,
    whitneyRoot: 0, withGana: 0, rootHomonyms: 0, survival: 0,
    homonymWarning: 0, paradigmAmbiguous: 0, allFour: 0
  };
  let withFreq = 0;
  const entries = [];
  for (const [lemma, dicts] of lookup.entries) {
    const { normalized } = normalizeLemma(lemma);
    const rec = dcs[normalized] ?? null;
    const fb = rec?.freqBand ?? 0;
    if (fb > 0) { withFreq += 1; coverage.frequency += 1; }
    byBand[fb] += 1;
    const codes = dicts.map(t => dictMeta[t[0]].code);
    const gr = dicts.filter(t => dictMeta[t[0]].grammarReliable).length;

    const entry = {
      l: lemma,
      fb,
      at: Boolean(rec?.attested),
      c: dicts.length,
      gr,
      d: codes,
      g: representativeGender(dicts, dictMeta),
      src: primarySource(dicts, dictMeta)
    };

    const iast = slp1ToIast(lemma);
    if (paradigms) {
      const p = resolveParadigm(paradigms.nomById, paradigms.verbRoots, iast);
      if (p) {
        entry.p = p;
        coverage.paradigmTotal += 1;
        // nominal/verb counted independently of precedence (the spec §8 table's
        // per-file basis); the card itself links the highest-tokens contract.
        if (paradigms.nomById.has(iast)) coverage.nominalParadigm += 1;
        if (paradigms.verbRoots.has(iast)) coverage.verbParadigm += 1;
        if (p.alt) coverage.paradigmAmbiguous += 1;
      }
    }
    if (whitney) {
      const roots = whitney.rootsBySlp1.get(lemma);
      if (roots) {
        entry.w = whitneyCardField(roots, whitney.ganaByNo);
        coverage.whitneyRoot += 1;
        if (roots.length > 1) coverage.rootHomonyms += 1;
        if (entry.w.some(r => r.gana != null)) coverage.withGana += 1;
      }
    }
    const rows = panelRows.get(lemma);
    if (rows) {
      entry.s = rows.map(r => ({ ...survivalCardField([r])[0], t: textByKey.get(`${lemma}\u001f${r.edge}\u001f${r.position}`) ?? null }));
      entry.s = entry.s.sort((a, b) => (Number(b.sv) - Number(a.sv)) || (b.ov - a.ov) || (a.pos - b.pos));
      coverage.survival += 1;
    }
    const hm = homonymByLemma.get(lemma);
    if (hm) {
      entry.hm = { mx: hm.maxHomonyms };
      coverage.homonymWarning += 1;
    }

    entry.tier = assignTier({
      hasSenses: Boolean(entry.s),
      hasParadigm: Boolean(entry.p),
      hasRoot: Boolean(entry.w)
    });
    tiers[entry.tier] += 1;
    // all four layers = paradigm + root + survival + frequency; the frequency
    // field is carried by every card by construction (band 0 included), same
    // denominator the spec's measure used — its headline is that this is 0.
    if (entry.p && entry.w && entry.s) coverage.allFour += 1;
    entries.push(entry);
  }

  // sanity
  for (const e of entries) {
    if (e.fb < 0 || e.fb > 5) throw new Error(`bad freqBand ${e.fb} for ${e.l}`);
    if (!["A", "B", "C", "D"].includes(e.tier)) throw new Error(`bad tier ${e.tier} for ${e.l}`);
    for (const s of e.s ?? []) {
      if (!s.e || !s.e.includes("→")) throw new Error(`survival rank without edge for ${e.l}`);
      if (typeof s.ov !== "number") throw new Error(`survival rank without overlap for ${e.l}`);
    }
  }

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: new Date().toISOString(),
    sourcePath: "src/data/dicts/lemma-lookup.json + data/dcs/dcs_lemma_summary.json + data/lexico/r2_h2h3.json + data/lexico/r2_h2_senses.json + src/data/dicts/homonym-split.json + VisualDCS learner-contracts-v1 + WhitneyRoots crosswalk",
    generatedBy: "npm run build-learner-index",
    claim: "Frequency-graded reader card: each lemma carries its DCS corpus frequency band, cross-dictionary coverage, survival-ranked best-attested senses (P2 panel), Whitney root(s) with gaṇa, and an attested-paradigm link, with a completeness tier and named absences for everything the evidence does not reach.",
    evidenceLevel: "derived",
    spec: "docs/LEARNER_LAYER_V1_SPEC.md",
    dictionaries: lookup.dictionaries,
    grammarReliableCodes: lookup.dictionaries.filter(d => d.grammarReliable).map(d => d.code),
    inputSchemes: ["SLP1", "IAST"],
    minDicts: lookup.minDicts,
    hrefBase: lookup.hrefBase,
    bandLegend: BAND_LEGEND,
    tierLegend: TIER_LEGEND,
    survivalThreshold: SURVIVAL_THRESHOLD,
    survivalCaveat: SURVIVAL_CAVEAT,
    absenceCodes: ABSENCE_CODES,
    visualDcs,
    tupleFields: {
      l: "lemma (SLP1)", fb: "DCS frequency band 0–5", at: "attested in DCS",
      c: "dictionary count", gr: "grammar-reliable dict count", d: "dictionary codes present",
      g: "representative gender (grammar-reliable dict)", src: "[dictCode, firstLine] primary source pointer",
      tier: "card completeness tier A–D (tierLegend)",
      p: "paradigm {k: nominal|verb, id: vdcs lemmaId/rootId, cells, tokens, alt?: other lemmaIds}",
      w: "Whitney roots (ALL matching rows): {no, iast, hom, gana?, certainty?, clsUnc?}",
      s: "survival-ranked senses: {t: sense text (null = not re-attachable), sv: survived, ov: max Jaccard, e: edge, pos, ci: cited}",
      hm: "dictionary homonym warning {mx: maxHomonyms} — advisory and incomplete by construction (400 of 9,839 candidates shipped)"
    },
    absenceNotes: {
      frequency: "band 0 = lemma not attested in the DCS corpus — uncorroborated by this corpus, NOT 'unused'",
      paradigm: "no attested-paradigm contract in VisualDCS learner-contracts-v1 for this lemma",
      root: "lemma is not a Whitney root form",
      senses: "outside the 28-lemma P2 survival panel (widening it is research, not build)",
      homonyms: "homonym candidates shipped are 400 of 9,839 — the warning is advisory and incomplete by construction"
    },
    assumptions: [
      "Frequency bands are coarse log10 buckets from the DCS corpus (band 5 = 1000+ occurrences ... band 1 = hapax); band 0 = lemma not attested in the DCS corpus, which does NOT mean the word is unused, only uncorroborated by this corpus.",
      "Gender is the value reported by the highest-priority grammar-reliable dictionary present (MW > AP > PWG > PWK > WIL); VCP/SKD prose genders are not used.",
      "Lemma set is the reader lookup (attested in at least minDicts dictionaries).",
      "Survival is defined, not intuited: max gloss-word Jaccard ≥ 0.15 against any descendant sense (threshold pinned in build-r2-h2h3.mjs, swept 0.10–0.25 in the paper's sensitivity grid); the card shows the threshold, not a derived confidence %.",
      "Per-sense survival claims only — the clean within-edge test is not significant; no population claim is made (survivalCaveat).",
      "Whitney root homonyms are shown together, never resolved to one; gaṇa comes only from root_class.csv via whitney_no with its certainty, or is absent — never inferred from the corpus.",
      "VisualDCS lemmaId collisions resolve to the highest-tokens lemmaId with alternatives disclosed; the stable ID recorded is the resolved one, so re-resolution is visible as an ID change.",
      "The paradigm link and its stable IDs are VisualDCS contract surface pinned at release " + VDCS_PIN.releaseId + " (commit " + VDCS_PIN.commit.slice(0, 8) + "); digests verified fail-closed at build."
    ],
    warnings,
    counts: {
      recordCount: entries.length,
      withFrequency: withFreq,
      byBand,
      tiers,
      coverage
    },
    entries
  };

  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUT_PATH, fs), payload);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  // Written compact (like lemma-lookup/lemma-dossier): one large data file.
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload)}\n`);
  console.log(`Wrote ${path.relative(ROOT, OUT_PATH)} (${entries.length} lemmas; ${withFreq} with a DCS frequency band).`);
  console.log(`  by band: ${BAND_LEGEND.map(b => `${b.band}:${byBand[b.band]}`).join("  ")}`);
  console.log(`  layers: paradigm ${coverage.paradigmTotal} (nom ${coverage.nominalParadigm} / verb ${coverage.verbParadigm}, ambiguous ${coverage.paradigmAmbiguous}), Whitney root ${coverage.whitneyRoot} (with gaṇa ${coverage.withGana}, homonyms ${coverage.rootHomonyms}), survival ${coverage.survival}, homonym warning ${coverage.homonymWarning}, all-four ${coverage.allFour}`);
  console.log(`  tiers: A ${tiers.A} / B ${tiers.B} / C ${tiers.C} / D ${tiers.D}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();

export { representativeGender, BAND_LEGEND, TIER_LEGEND };
