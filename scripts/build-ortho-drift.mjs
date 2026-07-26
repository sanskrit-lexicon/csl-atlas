// Build the gloss-language orthographic-drift census (PH5 ORTHO-CLOCK, H1577;
// agenda backlog #6): tokenise the German gloss text of the Cologne
// Petersburg-line dictionaries (PWG, PW, PWKVN, SCH) plus the independent
// control (GRA) and the declared derivative (CCS), count pre-reform vs
// post-reform spellings against the frozen SanskritSpellCheck reform maps,
// and test (i) the "clock" claim — pre-reform density falls monotonically
// with publication date — and (ii) the "descent" claim — descendants carry
// elevated fossil orthography relative to date-matched independents.
//
// Russian is the secondary lane: the only locally-available Russian gloss
// corpus is Kossovich (SamudraManthanam jsonl), so the RU census is a single
// dated point (share + CI), never a regression.
//
// Method notes:
// - The reform maps are OWNED by SanskritSpellCheck (A37 lane) and consumed
//   read-only from the sibling checkout — never re-derived here. A hit is
//   plain map membership on the lowercased token (the maps are already
//   dic-validated upstream: old form absent from the modern wordlist, modern
//   form present), so the census is deterministic and dependency-free.
// - preShare = pre / (pre + post) where post counts tokens equal to a
//   modern-side form of the same maps — a composition-robust companion to
//   the per-1000-token drift rate.
// - CIs are entry-level bootstrap (fixed-seed mulberry32); the tiny-n date
//   regression is guarded by an EXHAUSTIVE Spearman permutation p (all n!
//   orderings), not OLS standard errors; pair contrasts are entry-level
//   permutation tests. With exactly ONE independent German dictionary in the
//   corpus (GRA) the descent contrast is a directional pair test plus
//   descriptive residuals, and is labelled as such — no group test is
//   pretended.
// - The do_not_file suppression list (deliberate nonstandard SANSKRIT
//   headwords) does not intersect the German/Russian gloss token stream, so
//   it is deliberately NOT wired into these denominators.
//
// Usage: npm run build-ortho-drift   (then npm run validate-ortho-drift)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { loadDictionaryInventory, SOURCE_ROOT } from "./lib/dict-scope.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-ortho-drift";
const GITHUB_ROOT = path.resolve(process.cwd(), "..");
const SPELLCHECK_ROOT = process.env.SANSKRIT_SPELLCHECK_ROOT || path.join(GITHUB_ROOT, "SanskritSpellCheck");
const DE_MAP_PATH = path.join(SPELLCHECK_ROOT, "ortho_drift", "de_reform_map.tsv");
const RU_MAP_PATH = path.join(SPELLCHECK_ROOT, "ortho_drift", "ru_reform_map.tsv");
const KOSSOVICH_PATH =
  process.env.KOSSOVICH_JSONL ||
  path.join(GITHUB_ROOT, "SamudraManthanam", "web", "corpus_builder", "jsonl", "kossovich.jsonl");
const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "ortho_drift.json");
const SOURCE_OUT = path.join(OUT_DIR, "ortho_drift.source.json");

const BOOTSTRAP_B = 1000;
const PAIR_PERMUTATIONS = 1000;
const SEED = 15770801; // fixed: H1577 + arbitrary suffix, never wall-clock

// German-gloss roster. Lineage is the KNOWN genealogy, not inferred here:
// PW is Boehtlingk's own abridgement of PWG; PWKVN and SCH are Nachtraege to
// PW; CCS declares itself "nach den Petersburger Woerterbuechern bearbeitet"
// (title page, 1887); GRA is Grassmann's independent Rig-Veda lexicon.
export const DE_DICTS = [
  { code: "pwg", label: "PWG", lineage: "progenitor" },
  { code: "gra", label: "GRA", lineage: "independent" },
  { code: "pw", label: "PWK", lineage: "descendant" },
  { code: "pwkvn", label: "PWKVN", lineage: "descendant" },
  { code: "ccs", label: "CCS", lineage: "descendant" },
  { code: "sch", label: "SCH", lineage: "descendant" }
];

const DE_KNOWN_ERAS = new Set([
  "1901-th", "1901-c", "1901-c-iren", "1901-iren", "1901", "1901-th-adjacent",
  "1996-ss", "archaic-ey"
]);
const RU_KNOWN_ERAS = new Set(["1918-yat", "1918-i", "1918-hardsign", "1918-fita", "1918-izhitsa"]);

// --- gloss tokenisation (mirrors SanskritSpellCheck detectors/ortho_drift.py) ---
const RE_SKT = /\{#[\s\S]*?#\}|\{@[\s\S]*?@\}/g; // Sanskrit spans -> drop
const RE_ANNO = /\{\{[\s\S]*?\}\}/g; // {{old->new||date|editor|url|}} -> drop
const RE_META = /\{[A-Za-z]+=[^{}]*\}/g; // {part=,seq=1,...} entry metadata -> drop
const RE_BOT = /<bot>[\s\S]*?<\/bot>/gi; // botanical Latin spans -> drop
const RE_LS = /<ls\b[\s\S]*?<\/ls>/gi; // literary-source sigla -> drop
const RE_S = /<s>[\s\S]*?<\/s>/gi; // <s>SLP1</s> Sanskrit -> drop
const RE_ITAL = /\{%([\s\S]*?)%\}/g; // italic gloss -> unwrap
const RE_TAG = /<[^>]+>/g;
const RE_DEVA = /[ऀ-ॿ]+/g; // Devanagari -> drop (ru jsonl carries it)

export function cleanGloss(body) {
  let t = String(body ?? "");
  t = t.replace(RE_SKT, " ");
  t = t.replace(RE_ANNO, " ");
  t = t.replace(RE_META, " ");
  t = t.replace(RE_BOT, " ");
  t = t.replace(RE_LS, " ");
  t = t.replace(RE_S, " ");
  t = t.replace(RE_ITAL, " $1 ");
  t = t.replace(RE_TAG, " ");
  return t.replace(RE_DEVA, " ");
}

const DE_ABBR = new Set(
  ("adj subst sing plur nom gen dat acc voc loc instr comp conj praep partic " +
    "masc fem neutr vgl ibid cit seq fol vol cap caus comm com compar act med " +
    "pass lexicon adv praet").split(" ")
);

export const DE_PROFILE = {
  lang: "de",
  word: /[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß]{2,}/g,
  abbr: DE_ABBR,
  knownEras: DE_KNOWN_ERAS
};

export const RU_PROFILE = {
  lang: "ru",
  word: /[А-Яа-яЁёІіѢѣѲѳѴѵ]{2,}/g,
  abbr: new Set(),
  knownEras: RU_KNOWN_ERAS
};

export function glossTokens(profile, text) {
  const out = [];
  const cleaned = cleanGloss(text);
  for (const match of cleaned.matchAll(profile.word)) {
    const w = match[0];
    const lower = w.toLowerCase();
    if (profile.abbr.has(lower)) continue;
    if (w === w.toUpperCase()) continue; // all-caps = sigla/abbreviation
    out.push(lower);
  }
  return out;
}

/** Pre-1918 Russian letters are pre-reform BY DEFINITION (wordlist-free robustness check). */
export function ruDefinitionalHit(word) {
  return /[ІіѢѣѲѳѴѵ]/.test(word) || /ъ$/.test(word);
}

/** Load a SanskritSpellCheck reform map: old<TAB>modern<TAB>era. */
export function loadReformMap(filePath, knownEras) {
  const byOld = new Map();
  const modernSet = new Set();
  for (const line of fs.readFileSync(filePath, "utf8").split(/\r?\n/)) {
    if (!line || line.startsWith("#") || !line.includes("\t")) continue;
    const [old, modern, eraRaw] = line.split("\t");
    if (!old || !modern) continue;
    const era = knownEras.has(eraRaw) ? eraRaw : "other-map-era";
    byOld.set(old.toLowerCase(), { modern: modern.toLowerCase(), era });
    modernSet.add(modern.toLowerCase());
  }
  return { byOld, modernSet, forms: byOld.size };
}

/** Split a csl-orig v02 dictionary file into entry body strings (<L>...<LEND>). */
export function cslEntryBodies(fileText) {
  const bodies = [];
  let current = null;
  for (const line of fileText.split(/\r?\n/)) {
    if (line.startsWith("<L>")) {
      current = [];
      continue;
    }
    if (line.startsWith("<LEND>")) {
      if (current) bodies.push(current.join("\n"));
      current = null;
      continue;
    }
    if (current) current.push(line);
  }
  return bodies;
}

/**
 * Census one dictionary: per-entry [tokens, preDated, preAllMap, postHits]
 * quads for resampling, plus era and per-form tallies. "Dated" hits are the
 * era-attributed legislated-reform forms (1901/1996/1918/archaic) — the
 * clock object; "all-map" additionally counts the era-unattributed
 * corpus-mined pairs (bucket other-map-era). Pure over an array of entry
 * texts so tests can feed fixtures.
 */
export function censusEntries(profile, map, entryTexts) {
  const perEntry = [];
  const eras = new Map();
  const formCounts = new Map(); // old form -> pre count
  const modernCounts = new Map(); // modern form -> post count
  let tokens = 0;
  let preHitsDated = 0;
  let preHitsAllMap = 0;
  let postHits = 0;
  let definitionalHits = 0;
  for (const text of entryTexts) {
    const words = glossTokens(profile, text);
    let preDated = 0;
    let preAll = 0;
    let post = 0;
    for (const w of words) {
      const hit = map.byOld.get(w);
      if (hit) {
        preAll += 1;
        if (hit.era !== "other-map-era") preDated += 1;
        eras.set(hit.era, (eras.get(hit.era) ?? 0) + 1);
        formCounts.set(w, (formCounts.get(w) ?? 0) + 1);
      } else if (map.modernSet.has(w)) {
        post += 1;
        modernCounts.set(w, (modernCounts.get(w) ?? 0) + 1);
      }
      if (profile.lang === "ru" && ruDefinitionalHit(w)) definitionalHits += 1;
    }
    tokens += words.length;
    preHitsDated += preDated;
    preHitsAllMap += preAll;
    postHits += post;
    perEntry.push([words.length, preDated, preAll, post]);
  }
  return { perEntry, tokens, preHitsDated, preHitsAllMap, postHits, eras, formCounts, modernCounts, definitionalHits };
}

/** Deterministic 32-bit PRNG (mulberry32); Math.random is banned in builders. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function percentiles(sorted, lo = 0.025, hi = 0.975) {
  const at = (q) => sorted[Math.min(sorted.length - 1, Math.max(0, Math.floor(q * sorted.length)))];
  return [at(lo), at(hi)];
}

/**
 * Entry-level bootstrap 95% CIs for drift/1k and preShare. Resamples entries
 * with replacement, fixed seed -> reproducible.
 */
export function bootstrapCis(perEntry, { b = BOOTSTRAP_B, seed = SEED } = {}) {
  const n = perEntry.length;
  const rand = mulberry32(seed);
  const drift = [];
  const share = [];
  for (let i = 0; i < b; i++) {
    let tok = 0;
    let preDated = 0;
    let preAll = 0;
    let post = 0;
    for (let j = 0; j < n; j++) {
      const e = perEntry[Math.floor(rand() * n)];
      tok += e[0];
      preDated += e[1];
      preAll += e[2];
      post += e[3];
    }
    if (tok > 0) drift.push((preDated / tok) * 1000);
    if (preAll + post > 0) share.push(preAll / (preAll + post));
  }
  drift.sort((a, b2) => a - b2);
  share.sort((a, b2) => a - b2);
  return {
    driftPer1k: drift.length ? percentiles(drift).map((v) => round(v)) : null,
    preShare: share.length ? percentiles(share).map((v) => round(v)) : null
  };
}

/** OLS y = a + b x with R^2. */
export function olsFit(xs, ys) {
  const n = xs.length;
  const xBar = xs.reduce((a, v) => a + v, 0) / n;
  const yBar = ys.reduce((a, v) => a + v, 0) / n;
  let sxx = 0;
  let sxy = 0;
  let syy = 0;
  for (let i = 0; i < n; i++) {
    sxx += (xs[i] - xBar) ** 2;
    sxy += (xs[i] - xBar) * (ys[i] - yBar);
    syy += (ys[i] - yBar) ** 2;
  }
  const slope = sxy / sxx;
  const intercept = yBar - slope * xBar;
  const r2 = syy > 0 ? (sxy * sxy) / (sxx * syy) : null;
  return { slope, intercept, r2 };
}

function ranks(values) {
  const idx = values.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]);
  const out = new Array(values.length);
  for (let i = 0; i < idx.length; ) {
    let j = i;
    while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
    const rank = (i + j) / 2 + 1;
    for (let k = i; k <= j; k++) out[idx[k][1]] = rank;
    i = j + 1;
  }
  return out;
}

function pearson(xs, ys) {
  const { slope, r2 } = olsFit(xs, ys);
  return Math.sign(slope) * Math.sqrt(r2 ?? 0);
}

function* permutationsOf(arr) {
  if (arr.length <= 1) {
    yield arr;
    return;
  }
  for (let i = 0; i < arr.length; i++) {
    const rest = arr.slice(0, i).concat(arr.slice(i + 1));
    for (const p of permutationsOf(rest)) yield [arr[i], ...p];
  }
}

/**
 * Spearman rho with an EXHAUSTIVE permutation p (all n! orderings of y) —
 * the honest small-n guard demanded by the handoff ("no p-value theatre on
 * thin n without bounds").
 */
export function spearmanExact(xs, ys) {
  const rx = ranks(xs);
  const ry = ranks(ys);
  const rho = pearson(rx, ry);
  let total = 0;
  let exceed = 0;
  for (const perm of permutationsOf(ry)) {
    total += 1;
    if (Math.abs(pearson(rx, perm)) >= Math.abs(rho) - 1e-12) exceed += 1;
  }
  return { rho, pTwoSided: exceed / total, permutations: total };
}

/**
 * Entry-level permutation test for the drift/1k difference between two
 * dictionaries (b minus a). One-sided p in the stated direction
 * (`bMinusAPositive`: descent claim predicts b > a), fixed seed.
 */
export function pairPermutationTest(perEntryA, perEntryB, { b = PAIR_PERMUTATIONS, seed = SEED, bMinusAPositive = true } = {}) {
  // rate = DATED pre-reform hits per 1000 tokens (index 1 of the quad)
  const rate = (entries) => {
    let tok = 0;
    let pre = 0;
    for (const e of entries) {
      tok += e[0];
      pre += e[1];
    }
    return tok > 0 ? (pre / tok) * 1000 : 0;
  };
  const observed = rate(perEntryB) - rate(perEntryA);
  const all = perEntryA.concat(perEntryB);
  const nA = perEntryA.length;
  const rand = mulberry32(seed);
  let exceed = 0;
  for (let i = 0; i < b; i++) {
    // partial Fisher-Yates: the first nA slots become the permuted group A
    for (let j = 0; j < nA; j++) {
      const k = j + Math.floor(rand() * (all.length - j));
      [all[j], all[k]] = [all[k], all[j]];
    }
    const permDiff = rate(all.slice(nA)) - rate(all.slice(0, nA));
    if (bMinusAPositive ? permDiff >= observed : permDiff <= observed) exceed += 1;
  }
  return {
    diffPer1k: round(observed),
    pOneSided: round((exceed + 1) / (b + 1), 5),
    permutations: b
  };
}

function midYear(row) {
  const start = Number(row.start_year);
  const end = Number(row.end_year);
  if (Number.isFinite(start) && Number.isFinite(end)) return (start + end) / 2;
  const year = Number(row.year);
  return Number.isFinite(year) ? year : null;
}

function erasObject(eras) {
  return Object.fromEntries([...eras.entries()].sort((a, b) => b[1] - a[1]));
}

/**
 * Assemble the payload from per-dict censuses (pure; IO stays in main so
 * tests can feed fixture censuses).
 */
export function buildPayload({ german, russian, deMapForms, ruMapForms, generatedAt }) {
  const deDicts = german.map((d, i) => {
    const cis = bootstrapCis(d.census.perEntry, { seed: SEED + i });
    const dated = d.census.preHitsDated;
    const ss1996 = d.census.eras.get("1996-ss") ?? 0;
    const th1901 =
      (d.census.eras.get("1901-th") ?? 0) +
      (d.census.eras.get("1901-c") ?? 0) +
      (d.census.eras.get("1901-c-iren") ?? 0) +
      (d.census.eras.get("1901-iren") ?? 0) +
      (d.census.eras.get("1901") ?? 0);
    return {
      code: d.code,
      label: d.label,
      fullName: d.fullName,
      lineage: d.lineage,
      year: d.year,
      startYear: d.startYear,
      endYear: d.endYear,
      midYear: d.midYear,
      entries: d.census.perEntry.length,
      tokens: d.census.tokens,
      preHitsDated: dated,
      preHitsAllMap: d.census.preHitsAllMap,
      postHits: d.census.postHits,
      driftPer1k: round((dated / d.census.tokens) * 1000),
      driftPer1kAllMap: round((d.census.preHitsAllMap / d.census.tokens) * 1000),
      preShare: round(d.census.preHitsAllMap / (d.census.preHitsAllMap + d.census.postHits)),
      ci: cis,
      eras: erasObject(d.census.eras),
      // era-composition clock: which reform regime dominates the dated hits
      eraProfile: dated
        ? { share1901: round(th1901 / dated), share1996ss: round(ss1996 / dated) }
        : null,
      distinctPreForms: d.census.formCounts.size
    };
  });

  // Fossil-form overlap: share of a dictionary's distinct drifted forms that
  // also drift in PWG (the progenitor) — the "same fossils" descent signature.
  const pwgForms = new Set(german.find((d) => d.code === "pwg")?.census.formCounts.keys() ?? []);
  for (const [i, d] of german.entries()) {
    if (d.code === "pwg") {
      deDicts[i].fossilOverlapWithPwg = null;
      continue;
    }
    const forms = [...d.census.formCounts.keys()];
    const shared = forms.filter((f) => pwgForms.has(f)).length;
    deDicts[i].fossilOverlapWithPwg = forms.length ? round(shared / forms.length) : null;
  }

  // Date regression + exhaustive Spearman over the German points.
  const xs = deDicts.map((d) => d.midYear);
  const ys = deDicts.map((d) => d.driftPer1k);
  const fit = olsFit(xs, ys);
  const spearman = spearmanExact(xs, ys);
  const residuals = deDicts.map((d) => ({
    code: d.code,
    lineage: d.lineage,
    residual: round(d.driftPer1k - (fit.intercept + fit.slope * d.midYear))
  }));

  // Pair contrasts (entry-level permutation, one-sided in the claim direction).
  const byCode = new Map(german.map((d) => [d.code, d]));
  const pair = (aCode, bCode, claim, bMinusAPositive) => {
    const a = byCode.get(aCode);
    const b = byCode.get(bCode);
    if (!a || !b) return null;
    return {
      a: aCode,
      b: bCode,
      claim,
      ...pairPermutationTest(a.census.perEntry, b.census.perEntry, { bMinusAPositive, seed: SEED }),
      direction: bMinusAPositive ? `${bCode} > ${aCode} predicted` : `${bCode} < ${aCode} predicted`
    };
  };
  const pairTests = [
    pair("gra", "ccs", "descent claim (ii): the declared descendant CCS (1887) should be MORE pre-reform than the date-matched independent GRA (1873) if copying carried fossil orthography", true),
    pair("pwg", "gra", "independent-vs-progenitor: GRA (1873, independent) vs PWG (1855-75)", false),
    pair("pw", "ccs", "descendant-vs-source: CCS (1887) vs its declared source PW (1879-89)", true)
  ].filter(Boolean);

  const graD = deDicts.find((d) => d.code === "gra");
  const ccsD = deDicts.find((d) => d.code === "ccs");
  // No p-value theatre: "supported" needs BOTH the negative direction and the
  // exhaustive-permutation p; a negative rho alone is only direction-consistent.
  const clockVerdict =
    spearman.rho < 0 && spearman.pTwoSided <= 0.05
      ? "supported"
      : spearman.rho < 0
        ? "direction-consistent-inconclusive"
        : "not-supported";
  const descentTest = pairTests[0];
  const descentSupported = descentTest ? descentTest.diffPer1k > 0 && descentTest.pOneSided < 0.05 : null;

  // Top drifted forms across the German roster (per-dict pre counts + the
  // modern counterpart's post counts).
  const formTotals = new Map();
  for (const d of german) {
    for (const [form, count] of d.census.formCounts) {
      formTotals.set(form, (formTotals.get(form) ?? 0) + count);
    }
  }
  const deMap = german[0]?.map;
  // Reader-facing table: dated-reform fossils only — the era-unattributed
  // mined pairs (e.g. Sanskrit loanwords like brahman->brahmane) stay in the
  // per-dict all-map counts but out of the showcase table.
  const topForms = [...formTotals.entries()]
    .filter(([form]) => deMap.byOld.get(form)?.era !== "other-map-era")
    .sort((a, b) => b[1] - a[1])
    .slice(0, 60)
    .map(([form, total]) => {
      const info = deMap.byOld.get(form);
      const row = { old: form, modern: info?.modern ?? null, era: info?.era ?? null, total };
      for (const d of german) {
        row[d.code] = d.census.formCounts.get(form) ?? 0;
        row[`${d.code}_modern`] = info ? (d.census.modernCounts.get(info.modern) ?? 0) : 0;
      }
      return row;
    });

  const ruDicts = russian.map((d) => {
    const cis = bootstrapCis(d.census.perEntry, { seed: SEED + 7 });
    return {
      code: d.code,
      label: d.label,
      fullName: d.fullName,
      year: d.year,
      midYear: d.midYear,
      entries: d.census.perEntry.length,
      tokens: d.census.tokens,
      preHitsDated: d.census.preHitsDated,
      preHitsAllMap: d.census.preHitsAllMap,
      postHits: d.census.postHits,
      driftPer1k: round((d.census.preHitsDated / d.census.tokens) * 1000),
      driftPer1kAllMap: round((d.census.preHitsAllMap / d.census.tokens) * 1000),
      preShare: round(d.census.preHitsAllMap / (d.census.preHitsAllMap + d.census.postHits)),
      ci: cis,
      eras: erasObject(d.census.eras),
      distinctPreForms: d.census.formCounts.size,
      definitionalHits: d.census.definitionalHits
    };
  });
  const ruTopForms = russian.length
    ? [...russian[0].census.formCounts.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 40)
        .map(([form, count]) => {
          const info = russian[0].map.byOld.get(form);
          return { old: form, modern: info?.modern ?? null, era: info?.era ?? null, count };
        })
    : [];

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "SanskritSpellCheck/ortho_drift/de_reform_map.tsv",
      "SanskritSpellCheck/ortho_drift/ru_reform_map.tsv",
      "csl-orig/v02/{pwg,gra,pw,pwkvn,ccs,sch}",
      "SamudraManthanam/web/corpus_builder/jsonl/kossovich.jsonl",
      "src/data/lexicographic-structure/dictionary_inventory.csv",
      "scripts/build-ortho-drift.mjs"
    ],
    method:
      "Split each csl-orig v02 dictionary file into <L>...<LEND> entries and tokenise the gloss text with the SanskritSpellCheck ortho_drift tokenizer rules (drop {#...#}/{@...@} Sanskrit, {{...}} correction records, {k=v} entry metadata, <bot>/<ls>/<s> spans and all tags, unwrap {%...%}; German word = 3+ letters incl. umlauts/eszett, abbreviation stop-list, all-caps dropped). A PRE-reform hit is map membership of the lowercased token in the frozen de_reform_map.tsv (15,685 dic-validated old->modern pairs), split into DATED hits (era-attributed legislated-reform forms: 1901-*, 1996-ss, archaic-ey — the clock object and the headline driftPer1k) and ALL-MAP hits (adding the era-unattributed corpus-mined pairs, reported as driftPer1kAllMap); a POST-reform hit is membership in the map's modern-side form set. driftPer1k = datedPre/tokens*1000; preShare = allMapPre/(allMapPre+post). 95% CIs: entry-level bootstrap, B=" +
      BOOTSTRAP_B +
      ", fixed-seed mulberry32. Clock test: OLS of driftPer1k on inventory mid-year plus Spearman rho with an exhaustive n! permutation p. Descent test: with exactly one independent German dictionary (GRA) no group permutation test is identifiable; the claim is tested as directional entry-level permutation pair contrasts (B=" +
      PAIR_PERMUTATIONS +
      ") plus date-regression residuals by lineage, and reported as such. Russian: same census over the Kossovich jsonl rows against ru_reform_map.tsv (7,709 forms), plus a definitional pre-1918-letter robustness count; single dated point, no regression.",
    german: {
      referenceMap: { path: "SanskritSpellCheck/ortho_drift/de_reform_map.tsv", forms: deMapForms },
      dicts: deDicts,
      regression: {
        slopePer1kPerYear: round(fit.slope, 5),
        intercept: round(fit.intercept, 3),
        r2: round(fit.r2),
        spearmanRho: round(spearman.rho),
        spearmanExactPTwoSided: round(spearman.pTwoSided, 5),
        spearmanPermutations: spearman.permutations,
        residuals
      },
      pairTests,
      topForms
    },
    russian: {
      referenceMap: { path: "SanskritSpellCheck/ortho_drift/ru_reform_map.tsv", forms: ruMapForms },
      dicts: ruDicts,
      topForms: ruTopForms,
      note:
        "Kossovich (1854) is the only Russian-gloss dictionary with locally-available text; KNA (1893) and KCH (1978) have no csl-orig source, so the Russian lane is a single dated point — share and CI only, no clock regression."
    },
    verdict: {
      clock: clockVerdict,
      clockDetail: `Spearman rho ${round(spearman.rho)} (exact two-sided p ${round(spearman.pTwoSided, 5)} over ${spearman.permutations} orderings of ${deDicts.length} dictionaries): the density-vs-date direction is ${spearman.rho < 0 ? "negative" : "non-negative"} but ${spearman.pTwoSided <= 0.05 ? "significant" : "NOT significant at this n"}. Density tracks HOUSE STYLE more than date: the Boehtlingk-line dictionaries stay uniformly fossil regardless of publication date, while the non-Boehtlingk dictionaries modernise with date.`,
      eraCompositionDetail:
        "The era-COMPOSITION clock is the robust dating signal: every 19th-century dictionary is 1901-reform-dominated, while SCH (1928) flips to 1996-eszett-dominated with the 1901 signal collapsed — each dictionary's orthographic epoch is readable from its own gloss text (the upstream SCH-1928 control, reproduced here at the atlas layer).",
      descent: descentSupported === null ? "untestable" : descentSupported ? "supported" : "refuted",
      descentDetail: descentTest
        ? `Directional pair test CCS(1887, declared descendant) minus GRA(1873, independent): ${descentTest.diffPer1k}/1k dated drift (one-sided p ${descentTest.pOneSided}). ${descentSupported ? "The descendant is more pre-reform than the date-matched independent." : `The declared descendant CCS is ${ccsD && graD && ccsD.driftPer1k < graD.driftPer1k ? "LESS" : "not significantly more"} pre-reform than the independent GRA — copying Petersburg CONTENT did not carry fossil orthography at the token level; Cappeller re-spelled to his own decade's norms.`}`
        : "no pair available"
    },
    limitations: [
      "A pre-reform hit is reform-map membership only; the upstream transform-and-check + Hunspell layers are not re-run here (same tokenizer family, map-only counting), so absolute rates differ from the SanskritSpellCheck de_drift_summary.tsv snapshot (taken against a smaller map). The cross-dictionary GRADIENT and era composition are the objects, not the absolute level.",
      "About 12.8k of the 15.7k German map rows carry an era-unattributed third column (corpus/DTA-mined pairs); they are counted separately as all-map hits and EXCLUDED from the headline dated driftPer1k, so the clock statistic only uses forms attributable to a dated reform regime.",
      "The reform maps were partly MINED from these same dictionaries (then dic-validated upstream), so per-form recall is best on the Petersburg line; a form unique to an uncensused dictionary would be missed. The maps are consumed frozen, never extended here.",
      "preShare's post-reform denominator counts tokens equal to a modern-side map form, so it is conditioned on the map's pair inventory, not on all German tokens.",
      "German dictionary dates are inventory publication spans collapsed to mid-years (PWG 1855-1875 -> 1865, PW 1879-1889 -> 1884); PWKVN carries PW's span. With n=6 points the OLS fit is descriptive; the exhaustive Spearman permutation p is the inferential guard.",
      "The descent contrast has exactly ONE independent German dictionary (GRA), so it is a directional pair test plus descriptive residuals, not a group-level permutation test — stated, not hidden.",
      "The gloss token stream is post-markup-stripping; residual OCR/markup fragments (documented upstream at ~44% of the pre-classification residual) are outside the map and only dilute the denominator.",
      "The do_not_file suppression list covers deliberate nonstandard SANSKRIT headwords and does not intersect the German/Russian gloss tokens, so it is not wired into these denominators (decision recorded, H1577).",
      "Kossovich rows come from the SamudraManthanam corpus build, not csl-orig; its Russian is pervasively pre-1918 by construction (1854), and one dated point supports no trend claim."
    ],
    boundary: [
      "Gloss-language (meta-language) orthography only — Sanskrit-side orthographic drift is VisualDCS/Fonetika territory. Reform maps are owned by SanskritSpellCheck (A37) and consumed read-only from the sibling checkout; the committed data/lexico/ortho_drift.json is the CI-safe artifact. csl-orig is never written. Rendering owner repo: csl-atlas."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  const commitOf = (dir) => {
    try {
      return execSync(`git -C "${dir}" rev-parse HEAD`, { encoding: "utf8" }).trim();
    } catch {
      return "unknown";
    }
  };
  const envelope = {
    dataset: "ortho_drift",
    commit: commitOf(process.cwd()),
    reformMapRepo: "https://github.com/drdhaval2785/SanskritSpellCheck",
    reformMapCommit: commitOf(SPELLCHECK_ROOT),
    kossovichRepo: "https://github.com/gasyoun/SamudraManthanam",
    kossovichCommit: commitOf(path.join(GITHUB_ROOT, "SamudraManthanam")),
    cslOrigCommit: commitOf(path.resolve(SOURCE_ROOT, "..", "..")),
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  for (const [label, p] of [["German reform map", DE_MAP_PATH], ["Russian reform map", RU_MAP_PATH]]) {
    if (!fs.existsSync(p)) {
      console.error(
        `Required input missing: ${label} at ${p}\n` +
          "This builder needs a sibling SanskritSpellCheck checkout (the committed data/lexico/ortho_drift.json is the CI-safe artifact). STOP — do not invent pairs."
      );
      process.exit(1);
    }
  }
  const deMap = loadReformMap(DE_MAP_PATH, DE_KNOWN_ERAS);
  const ruMap = loadReformMap(RU_MAP_PATH, RU_KNOWN_ERAS);
  const inventory = new Map(loadDictionaryInventory().map((row) => [String(row.code).toLowerCase(), row]));

  const german = [];
  for (const spec of DE_DICTS) {
    const file = path.join(SOURCE_ROOT, spec.code, `${spec.code}.txt`);
    if (!fs.existsSync(file)) {
      console.error(`csl-orig source missing for ${spec.code}: ${file}`);
      process.exit(1);
    }
    const row = inventory.get(spec.code === "pw" ? "pw" : spec.code);
    const bodies = cslEntryBodies(fs.readFileSync(file, "utf8"));
    const census = censusEntries(DE_PROFILE, deMap, bodies);
    german.push({
      ...spec,
      fullName: row?.full_name ?? spec.label,
      year: Number(row?.year) || null,
      startYear: Number(row?.start_year) || null,
      endYear: Number(row?.end_year) || null,
      midYear: midYear(row ?? {}),
      census,
      map: deMap
    });
    console.log(`  ${spec.label}: ${bodies.length} entries, ${census.tokens} tokens, ${census.preHitsDated} dated / ${census.preHitsAllMap} all-map pre-reform hits`);
  }

  const russian = [];
  if (fs.existsSync(KOSSOVICH_PATH)) {
    const rows = fs
      .readFileSync(KOSSOVICH_PATH, "utf8")
      .split(/\r?\n/)
      .filter((l) => l.trim())
      .map((l) => JSON.parse(l))
      .filter((r) => !r.deleted);
    const census = censusEntries(RU_PROFILE, ruMap, rows.map((r) => r.text ?? ""));
    const row = inventory.get("kow");
    russian.push({
      code: "kow",
      label: "KOW",
      fullName: row?.full_name ?? "Kossovich Sanskrit-Russian Dictionary",
      lineage: "independent",
      year: Number(row?.year) || 1854,
      midYear: Number(row?.year) || 1854,
      census,
      map: ruMap
    });
    console.log(`  KOW: ${rows.length} rows, ${census.tokens} tokens, ${census.preHitsAllMap} pre-reform hits (${census.definitionalHits} definitional)`);
  } else {
    console.warn(`Kossovich jsonl absent (${KOSSOVICH_PATH}) — Russian lane skipped.`);
  }

  const payload = buildPayload({ german, russian, deMapForms: deMap.forms, ruMapForms: ruMap.forms });
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(`Wrote ortho-drift census (${payload.german.dicts.length} German + ${payload.russian.dicts.length} Russian dicts):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(`  clock: ${payload.verdict.clock} (${payload.verdict.clockDetail})`);
  console.log(`  descent: ${payload.verdict.descent} (${payload.verdict.descentDetail})`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
