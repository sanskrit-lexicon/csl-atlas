// Build the learner's reading-layer index — v1 (H5318, per docs/LEARNER_LAYER_V1_SPEC.md).
//
// v0 joined the reader lemma-lookup (dictionary coverage + gender) with the DCS
// corpus frequency band. v1 closes the gap its own header declared: it joins
// FOUR evidence layers around one question — "is this word worth learning yet,
// and what do I need to know to read it?":
//   frequency band (I3) · best-attested senses ranked by survival (I9/I10)
//   root + gaṇa (I7/I8) · paradigm link (I4/I5 at the pinned VisualDCS release)
// plus the v0 substrate (cross-dictionary coverage, representative gender,
// source pointer) and the homonym split warning (I11).
//
// Pin rule (§4): I4–I6 are consumed at the envelope's releaseId; the builder
// verifies the declared sha256 of every VisualDCS payload it reads and FAILS
// CLOSED on a mismatch or an unknown contractVersion — never best-effort.
//
// Join key (§5): the normalised SLP1 lemma; SLP1→IAST via the repo's single
// normaliser (src/lib/lookup-normalize.js), never the lossy reverse direction.
//
// Sibling repos (consumed, never re-derived): VisualDCS (VDCS_REPO) and
// WhitneyRoots (WHITNEY_REPO). Defaults assume the standard ~/Documents/GitHub
// layout; override with env vars. Missing sibling = clear error, not a partial card.
//
// Usage: npm run build-learner-index

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { loadDcsSummary } from "./lib/dcs-summary.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { slp1ToIast } from "../src/lib/lookup-normalize.js";

const SCHEMA_VERSION = "2.0.0";
const ROOT = process.cwd();
const VDCS = process.env.VDCS_REPO ?? path.resolve(ROOT, "..", "VisualDCS");
const WR = process.env.WHITNEY_REPO ?? path.resolve(ROOT, "..", "WhitneyRoots");
const LOOKUP_PATH = path.resolve(ROOT, "src", "data", "dicts", "lemma-lookup.json");
const OUT_DIR = path.resolve(ROOT, "src", "data", "learner");
const OUT_PATH = path.join(OUT_DIR, "learner-index.json");

// The pinned VisualDCS release (I6). A release bump is a deliberate, reviewed
// change: update PIN together with the envelope reference and re-verify.
const PIN = {
  envelope: "visual/contracts/envelopes/learner-contracts-v1-2026-08-09.envelope.json",
  envelopeSha256: null, // envelope file is the pin's own anchor; its payloads are hashed below
  releaseId: "vdcs-learner-v1-20260809",
  commit: "6d19eed11a75076c3639cfb2f9e6f5ff9c6648cf",
  manifest: "visual/contracts/v1/manifest.json",
  payloads: {
    "visual/contracts/v1/nominal-trainer.json": "13b5a16f5b45e886744f56f3464e8122730d60e1a677323f5b67024684de6663",
    "visual/contracts/v1/verb-trainer.json": "5276b7d04ee409c58c8fe7426b26efdabc2cbc1d3d4d05082f5ed1d593f2d4f6"
  }
};

const ABSENCE_CODES = {
  "not-in-dcs": "band 0 — the lemma is uncorroborated by the DCS corpus (not 'unused')",
  "no-paradigm-contract": "no attested paradigm at the pinned VisualDCS release (vdcs-learner-v1-20260809)",
  "not-a-root": "the headword is not a Whitney root, so no root/gaṇa layer exists for it",
  "outside-survival-panel": "the lemma is outside the 28-lemma P2 survival panel — no ranked senses exist yet",
  "homonym-payload-truncated": "the homonym warning is absent; the shipped homonym payload is truncated by construction (see payload warning — declared payload-level, not per-card, because unshipped candidates cannot be attributed to a card)"
};

// Frequency band → learner-facing study priority (self-documenting in the data).
const BAND_LEGEND = [
  { band: 5, range: "1000+", en: "very common", ru: "очень частотное", priorityEn: "learn first", priorityRu: "учить в первую очередь" },
  { band: 4, range: "100–999", en: "common", ru: "частотное", priorityEn: "learn early", priorityRu: "учить рано" },
  { band: 3, range: "10–99", en: "uncommon", ru: "нечастотное", priorityEn: "learn later", priorityRu: "учить позже" },
  { band: 2, range: "2–9", en: "rare", ru: "редкое", priorityEn: "reference", priorityRu: "справочно" },
  { band: 1, range: "1", en: "hapax", ru: "гапакс", priorityEn: "reference", priorityRu: "справочно" },
  { band: 0, range: "—", en: "not in corpus", ru: "нет в корпусе", priorityEn: "uncorroborated", priorityRu: "без корпуса" }
];

// --- pure helpers (unit-tested) ------------------------------------------------

// §8 completeness tiers: A full evidence (survival senses present);
// B grammar-complete (paradigm AND root); C partial (either); D neither.
function tierOf({ hasSenses, hasParadigm, hasRoot }) {
  if (hasSenses) return "A";
  if (hasParadigm && hasRoot) return "B";
  if (hasParadigm || hasRoot) return "C";
  return "D";
}

// §6 rank order: survived desc, overlap desc, position asc. Ties break on
// position — never on gloss length. Returns a new sorted array; input untouched.
function rankSenses(rows) {
  return [...rows].sort((a, b) =>
    (b.survived ? 1 : 0) - (a.survived ? 1 : 0)
    || b.overlap - a.overlap
    || a.position - b.position);
}

// §7.3: the paradigm link resolves to the highest-tokens lemmaId; the card
// discloses the alternatives. Nominal wins over a verb-root match (the verb
// link stays visible as an alternative). ids: [{id, tokens}]; verbId: string|null.
function resolveParadigm(ids, verbId) {
  const nominalIds = ids ?? [];
  if (!nominalIds.length && !verbId) return { px: null, pxA: [] };
  if (!nominalIds.length) return { px: `vdcs:v1:verb:${verbId}`, pxA: [] };
  const best = nominalIds.reduce((a, b) => (b.tokens > a.tokens ? b : a));
  const px = `vdcs:v1:nominal:${best.id}`;
  const pxA = [
    ...nominalIds.filter(r => r.id !== best.id).map(r => `vdcs:v1:nominal:${r.id}`),
    ...(verbId ? [`vdcs:v1:verb:${verbId}`] : [])
  ];
  return { px, pxA };
}

// §9.1 named absences from the closed vocabulary (per-card knowable subset —
// the homonym-payload-truncated code is declared payload-level, see its legend entry).
function absenceCodes({ fb, px, rootCount, senseCount }) {
  const codes = [];
  if (fb === 0) codes.push("not-in-dcs");
  if (!px) codes.push("no-paradigm-contract");
  if (!rootCount) codes.push("not-a-root");
  if (!senseCount) codes.push("outside-survival-panel");
  return codes;
}

// --- inputs ---------------------------------------------------------------------

function sha256File(p) {
  return crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
}

function requireFile(p, what) {
  if (!fs.existsSync(p)) throw new Error(`FAIL-CLOSED: ${what} not found at ${p} — set the env var or restore the input; refusing to build a partial card set (spec §9.2).`);
}

function loadVdcsPinned() {
  requireFile(VDCS, "VisualDCS repo (VDCS_REPO)");
  const manifestPath = path.join(VDCS, PIN.manifest);
  requireFile(manifestPath, `VisualDCS manifest ${PIN.manifest}`);
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  if (manifest.releaseId !== PIN.releaseId) {
    throw new Error(`FAIL-CLOSED: VisualDCS releaseId "${manifest.releaseId}" != pinned "${PIN.releaseId}" — a release bump is a deliberate, reviewed change (spec §9.3).`);
  }
  for (const [rel, expected] of Object.entries(PIN.payloads)) {
    const p = path.join(VDCS, rel);
    requireFile(p, `VisualDCS payload ${rel}`);
    const actual = sha256File(p);
    if (actual !== expected) {
      throw new Error(`FAIL-CLOSED: sha256 mismatch for ${rel}: got ${actual}, manifest declares ${expected} (spec §9.2).`);
    }
  }
  const nominal = JSON.parse(fs.readFileSync(path.join(VDCS, "visual/contracts/v1/nominal-trainer.json"), "utf8"));
  const verb = JSON.parse(fs.readFileSync(path.join(VDCS, "visual/contracts/v1/verb-trainer.json"), "utf8"));
  for (const [name, payload] of [["nominal-trainer", nominal], ["verb-trainer", verb]]) {
    if (payload.contractVersion !== "1.0.0") {
      throw new Error(`FAIL-CLOSED: unknown contractVersion "${payload.contractVersion}" in ${name} — keep the previous pin (spec §9.3).`);
    }
  }
  if (nominal.lemmaCount !== nominal.lemmas.length || verb.rootCount !== verb.roots.length) {
    throw new Error("FAIL-CLOSED: VisualDCS payload recordCount disagrees with the payload body.");
  }
  return { nominal, verb };
}

// Minimal RFC-4180 CSV reader (quoted fields, no multiline quoting needed here).
function csv(s) {
  return s.trim().split(/\r?\n/).map(r => {
    const out = []; let cur = "", q = false;
    for (const ch of r) {
      if (ch === '"') q = !q; else if (ch === "," && !q) { out.push(cur); cur = ""; } else cur += ch;
    }
    out.push(cur); return out;
  });
}

function loadWhitney() {
  requireFile(WR, "WhitneyRoots repo (WHITNEY_REPO)");
  const rootsPath = path.join(WR, "crosswalk/roots.csv");
  const classPath = path.join(WR, "crosswalk/root_class.csv");
  requireFile(rootsPath, "WhitneyRoots crosswalk/roots.csv");
  requireFile(classPath, "WhitneyRoots crosswalk/root_class.csv");
  const rootsRows = csv(fs.readFileSync(rootsPath, "utf8"));
  const rh = rootsRows[0];
  const col = n => rh.indexOf(n);
  const roots = rootsRows.slice(1).map(r => ({
    no: r[col("whitney_no")], slp1: r[col("root_slp1")], iast: r[col("root_iast")],
    hom: r[col("homonym")], cls: r[col("class")], clsUnc: r[col("class_uncertain")]
  }));
  const classRows = csv(fs.readFileSync(classPath, "utf8"));
  const ch = classRows[0];
  const ganaByNo = new Map(classRows.slice(1).map(r => [r[ch.indexOf("whitney_no")],
    { gana: r[ch.indexOf("gana")], certainty: r[ch.indexOf("certainty")] }]));
  return { roots, ganaByNo };
}

// --- main -----------------------------------------------------------------------

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

function main() {
  const lookup = JSON.parse(fs.readFileSync(LOOKUP_PATH, "utf-8"));
  const dcs = loadDcsSummary();
  const dictMeta = Object.fromEntries(lookup.dictionaries.map((d, i) => [i, d]));
  const { nominal, verb } = loadVdcsPinned();
  const { roots, ganaByNo } = loadWhitney();
  const h2 = JSON.parse(fs.readFileSync(path.resolve(ROOT, "data/lexico/r2_h2h3.json"), "utf8"));
  const senseRows = JSON.parse(fs.readFileSync(path.resolve(ROOT, "data/lexico/r2_h2_senses.json"), "utf8")).rows;
  const homSplit = JSON.parse(fs.readFileSync(path.resolve(ROOT, "src/data/dicts/homonym-split.json"), "utf8"));

  // --- join maps (§5: normalised SLP1 lemma is the key) ---
  const nomByIast = new Map(); // IAST → [{id, tokens}]
  for (const l of nominal.lemmas) {
    if (!nomByIast.has(l.lemma)) nomByIast.set(l.lemma, []);
    nomByIast.get(l.lemma).push({ id: l.lemmaId, tokens: l.tokens });
  }
  const verbByIast = new Map(verb.roots.map(r => [r.rootId, r.rootId]));
  const rootsBySlp1 = new Map();
  for (const r of roots) {
    if (!rootsBySlp1.has(r.slp1)) rootsBySlp1.set(r.slp1, []);
    rootsBySlp1.get(r.slp1).push(r);
  }
  const sensesByLemma = new Map();
  for (const row of senseRows) {
    if (!sensesByLemma.has(row.lemma)) sensesByLemma.set(row.lemma, []);
    sensesByLemma.get(row.lemma).push(row);
  }
  const homByLemma = new Map(homSplit.candidates.map(c => [c.lemma, c]));
  const panel = new Set(h2.panel);

  const warnings = [];
  if (!Object.keys(dcs).length) {
    warnings.push("DCS summary absent (data/dcs/dcs_lemma_summary.json); all freqBand = 0.");
  }
  warnings.push(
    `Homonym warnings are ADVISORY AND INCOMPLETE BY CONSTRUCTION: ${homSplit.candidateCount} candidate lemmas, ` +
    `${homSplit.shown} shipped, of which ${[...new Set([...homByLemma.keys()].filter(l => lookupLemmas.has(l)))].length} match a learner lemma ` +
    "(raising the shipped payload is a separate unit, spec §7.1)."
  );
  warnings.push(
    "The P2 cited→survived effect is edge-concentrated (essentially all cited senses sit on ap90→ap); " +
    "the clean within-edge test is not significant (z = 1.80, p = 0.072). A card may say 'this sense survives " +
    "into the later dictionary' — it may NOT say 'cited senses survive more often' (spec §6)."
  );

  const lookupLemmas = new Set(lookup.entries.map(([lemma]) => lemma));
  const byBand = Object.fromEntries(BAND_LEGEND.map(b => [b.band, 0]));
  let withFreq = 0;
  const tierCounts = { A: 0, B: 0, C: 0, D: 0 };
  let tierDWithFreq = 0;
  const layerReach = { freq: 0, paradigm: 0, root: 0, rootWithGana: 0, survival: 0, homonymWarning: 0, allFourLayers: 0 };

  const entries = [];
  for (const [lemma, dicts] of lookup.entries) {
    const { normalized } = normalizeLemma(lemma);
    const rec = dcs[normalized] ?? null;
    const fb = rec?.freqBand ?? 0;
    if (fb > 0) { withFreq += 1; layerReach.freq += 1; }
    byBand[fb] += 1;
    const codes = dicts.map(t => dictMeta[t[0]].code);
    const gr = dicts.filter(t => dictMeta[t[0]].grammarReliable).length;

    // paradigm link (I4/I5), SLP1 → IAST, never the reverse (§5)
    const iast = slp1ToIast(lemma);
    const { px, pxA } = resolveParadigm(nomByIast.get(iast), verbByIast.get(iast));
    if (px) layerReach.paradigm += 1;

    // Whitney roots + gaṇa (I7/I8) — show ALL matching roots, never pick one (§7.2)
    const rootRows = rootsBySlp1.get(lemma) ?? [];
    const rt = rootRows.map(r => {
      const g = ganaByNo.get(r.no);
      return {
        n: r.no, h: r.hom || undefined,
        g: g?.gana || r.cls || undefined,
        gc: g?.certainty || undefined,
        u: r.clsUnc === "1" || r.clsUnc === "true" ? true : undefined
      };
    });
    if (rt.length) {
      layerReach.root += 1;
      if (rt.some(r => r.g)) layerReach.rootWithGana += 1;
    }

    // survival-ranked senses (I9/I10) — the triple travels with edge + threshold (§6)
    let sv;
    if (panel.has(lemma)) {
      const rows = sensesByLemma.get(lemma) ?? [];
      sv = rankSenses(rows).map(r => ({
        t: r.text ?? "", s: Boolean(r.survived), o: r.overlap, e: r.edge, p: r.position, c: Boolean(r.cited)
      }));
      layerReach.survival += 1;
    }

    // homonym split warning (I11) — advisory, per-dictionary counts + source links (§7.1)
    let hw;
    const cand = homByLemma.get(lemma);
    if (cand && cand.maxHomonyms > 1) {
      hw = {
        m: cand.maxHomonyms,
        byDict: cand.byDict,
        src: (cand.examples ?? []).filter(x => x.href).slice(0, 6).map(x => [x.dict, x.href])
      };
      layerReach.homonymWarning += 1;
    }

    const tiers = tierOf({ hasSenses: Boolean(sv?.length), hasParadigm: Boolean(px), hasRoot: Boolean(rt.length) });
    tierCounts[tiers] += 1;
    if (tiers === "D" && fb > 0) tierDWithFreq += 1;
    if (fb > 0 && px && rt.length && sv?.length) layerReach.allFourLayers += 1;

    const abs = absenceCodes({ fb, px, rootCount: rt.length, senseCount: sv?.length ?? 0 });

    const e = {
      l: lemma,
      fb,
      at: Boolean(rec?.attested),
      c: dicts.length,
      gr,
      d: codes,
      g: representativeGender(dicts, dictMeta),
      src: primarySource(dicts, dictMeta),
      tier: tiers
    };
    if (px) { e.px = px; if (pxA.length) e.pxA = pxA; }
    if (rt.length) e.rt = rt;
    if (sv) e.sv = sv;
    if (hw) e.hw = hw;
    if (abs.length) e.abs = abs;
    entries.push(e);
  }

  // sanity
  for (const e of entries) {
    if (e.fb < 0 || e.fb > 5) throw new Error(`bad freqBand ${e.fb} for ${e.l}`);
    if (!["A", "B", "C", "D"].includes(e.tier)) throw new Error(`bad tier ${e.tier} for ${e.l}`);
    if (e.abs && e.abs.some(code => !(code in ABSENCE_CODES))) throw new Error(`unknown absence code in ${e.l}`);
  }

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: new Date().toISOString(),
    sourcePath: "src/data/dicts/lemma-lookup.json + data/dcs/dcs_lemma_summary.json + VisualDCS learner-contracts-v1 (pinned) + WhitneyRoots crosswalk + data/lexico/r2_h2{h3,senses}.json + src/data/dicts/homonym-split.json",
    generatedBy: "npm run build-learner-index",
    claim: "Sparse per-lemma reading card with named absences: DCS frequency band, survival-ranked best-attested senses (28-lemma panel only), Whitney root + gaṇa, paradigm link at the pinned VisualDCS release, cross-dictionary coverage and a source pointer. Zero lemmas carry all four layers today — the card is designed sparse, not full (spec §8).",
    evidenceLevel: "derived",
    spec: "docs/LEARNER_LAYER_V1_SPEC.md",
    dictionaries: lookup.dictionaries,
    grammarReliableCodes: lookup.dictionaries.filter(d => d.grammarReliable).map(d => d.code),
    inputSchemes: ["SLP1", "IAST"],
    minDicts: lookup.minDicts,
    hrefBase: lookup.hrefBase,
    bandLegend: BAND_LEGEND,
    vdcs: {
      releaseId: PIN.releaseId,
      commit: PIN.commit,
      envelope: `https://github.com/gasyoun/VisualDCS/blob/main/${PIN.envelope}`,
      sha256Verified: Object.fromEntries(Object.entries(PIN.payloads).map(([rel, sha]) => [path.basename(rel), sha])),
      ceilingNote: "DCS cannot distinguish class I from VI, or IV from the passive, at the root-class level (VisualDCS ceilingNote) — an absent gaṇa is rendered absent, never inferred."
    },
    survival: {
      threshold: h2.survivedThreshold,
      panelSize: h2.panelSize,
      source: "data/lexico/r2_h2_senses.json",
      caveat: "Survival = max gloss-word Jaccard ≥ 0.15 against any descendant sense (threshold swept 0.10–0.25). Per-sense fact only; NOT a population claim about cited senses (spec §6)."
    },
    homonyms: {
      candidateCount: homSplit.candidateCount,
      shipped: homSplit.shown,
      matched: layerReach.homonymWarning,
      advisory: true,
      note: "The split warning is advisory and incomplete by construction; raising the shipped payload is a separate unit (spec §7.1)."
    },
    absenceCodes: ABSENCE_CODES,
    tierLegend: {
      A: "full evidence — survival senses present",
      B: "grammar-complete — paradigm and Whitney root",
      C: "partial — paradigm or root",
      D: "frequency + dictionaries only"
    },
    tupleFields: {
      l: "lemma (SLP1)", fb: "DCS frequency band 0–5", at: "attested in DCS", c: "dictionary count",
      gr: "grammar-reliable dict count", d: "dictionary codes present", g: "representative gender (grammar-reliable dict)",
      src: "[dictCode, firstLine] primary source pointer", tier: "card completeness tier A–D (§8)",
      px: "resolved paradigm link vdcs:v1:{nominal:<lemmaId>|verb:<rootId>}", pxA: "disclosed alternative paradigm links",
      rt: "matching Whitney roots [{n: whitney_no, h: homonym index, g: gaṇa, gc: gaṇa certainty, u: class uncertain}]",
      sv: "survival-ranked senses [{t: text, s: survived, o: overlap, e: edge, p: position, c: cited}] — only with survival.threshold + per-sense e",
      hw: "homonym split warning {m: maxHomonyms, byDict: per-dict counts, src: [dict, href]} — advisory",
      abs: "named absence reason codes (§9.1 closed vocabulary)"
    },
    assumptions: [
      "Frequency bands are coarse log10 buckets from the DCS corpus (band 5 = 1000+ occurrences ... band 1 = hapax); band 0 = lemma not attested in the DCS corpus, which does NOT mean the word is unused, only uncorroborated by this corpus.",
      "Gender is the value reported by the highest-priority grammar-reliable dictionary present (MW > AP > PWG > PWK > WIL); VCP/SKD prose genders are not used.",
      "Lemma set is the reader lookup (attested in at least minDicts dictionaries).",
      "VisualDCS payloads are consumed at envelope vdcs-learner-v1-20260809 with verified sha256; a mismatch fails the build (never a partial card set).",
      "Paradigm collisions resolve to the highest-tokens lemmaId; alternatives stay on the card so a re-resolution is visible as an ID change (§7.3).",
      "Whitney root homonyms: all matching roots are shown with whitney_no, homonym index and gaṇa — never one picked (§7.2). The gaṇa is never inferred; absent stays absent."
    ],
    warnings,
    counts: {
      recordCount: entries.length, withFrequency: withFreq, byBand,
      tiers: tierCounts, tierDWithFreq, layerReach
    },
    entries
  };

  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUT_PATH, fs), payload);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  // Written compact (like lemma-lookup/lemma-dossier): one large data file.
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload)}\n`);
  console.log(`Wrote ${path.relative(ROOT, OUT_PATH)} (${entries.length} lemmas; schema ${SCHEMA_VERSION}; VisualDCS ${PIN.releaseId}).`);
  console.log(`  freq: ${withFreq} with a DCS band  by band: ${BAND_LEGEND.map(b => `${b.band}:${byBand[b.band]}`).join("  ")}`);
  console.log(`  layers: paradigm ${layerReach.paradigm}  root ${layerReach.root} (gaṇa ${layerReach.rootWithGana})  survival ${layerReach.survival}  hom-warn ${layerReach.homonymWarning}  all-four ${layerReach.allFourLayers}`);
  console.log(`  tiers: A ${tierCounts.A}  B ${tierCounts.B}  C ${tierCounts.C}  D ${tierCounts.D}  (tier D with a band: ${tierDWithFreq})`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();

export { representativeGender, BAND_LEGEND, tierOf, rankSenses, resolveParadigm, absenceCodes, ABSENCE_CODES };
