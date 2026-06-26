// Etymology / derivation oracle: consume csl-orig's pre-built derivation layer
// (10 dictionaries' *_etymology.tsv extracts + the etymology_stats aggregates)
// instead of re-extracting or re-deriving derivations inside the atlas. csl-orig
// now owns this layer (per-dict analyze_*_etymology scripts emit
// <dict>_etymology.{tsv,jsonl}; etymology_stats/stats_etymology.py pools them
// into cross-dict agreement + productivity tables). This builder reads those and
// presents an atlas-native derivation view for the P4 / root-agreement analyses
// (PROJECT_INTERLINKS "etymology.tsv -> csl-atlas" feed).
//
// IMPORTANT — cross-dict ROOT AGREEMENT is NOT recomputed here. It is the
// established result owned by csl-orig/v02/etymology_stats
// (cross_dict_root_agreement.csv, Wilson-CI pairwise, kAraka-aware, with WIL's
// "first-etymon" caveat). We consume it verbatim rather than reinvent a naive
// exact-match metric (which conflates citation-form variants and kAraka senses).
//
// Read-only: writes ONLY a new dataset (src/data/etymology-oracle.json + mirror).
// Touches no reviewed packet, checkpoint, or app overlay; not wired into
// sync-site-data / the main build. Run `npm run build-etymology-oracle`.
//
// Per-dict root key by extraction style: root_slp1 (ap, ap90, krm, mw, shs, skd,
// vcp), source_slp1 (pw, pwg — German Von/Wurzel = immediate source), root (wil,
// IAST, = first etymon, often a prefix). topRoots are reported in each dict's own
// surface form; rootStyle records which is which so they are not naively mixed.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { generatedAtForPayload, licenseFields, readJsonIfExists } from "./lib/dataset-meta.mjs";

const ROOT = path.resolve(process.cwd(), process.env.CSL_ORIG_ROOT ?? path.join("..", "csl-orig", "v02"));
const STATS = path.join(ROOT, "etymology_stats");
const OUT = [
  path.resolve(process.cwd(), "src", "data", "etymology-oracle.json"),
  path.resolve(process.cwd(), "data", "etymology-oracle.json")
];

const DISPLAY_CODE = new Map([["pw", "PWK"]]);
const TOP_ROOTS = 10;

const ROOT_FIELDS = ["root_slp1", "source_slp1", "root"]; // checked in order
const STYLE_BY_FIELD = { root_slp1: "root_slp1", source_slp1: "source_slp1", root: "iast-root" };

function parseDelimited(text, delim) {
  const lines = text.split(/\r?\n/).filter(line => line.length > 0);
  if (!lines.length) return [];
  const header = lines[0].split(delim);
  return lines.slice(1).map(line => {
    const cells = line.split(delim);
    const row = {};
    header.forEach((h, i) => { row[h] = cells[i] ?? ""; });
    return row;
  });
}

function analyseDict(code) {
  const file = path.join(ROOT, code, `${code}_etymology.tsv`);
  const rows = parseDelimited(fs.readFileSync(file, "utf8"), "\t");
  const header = rows.length ? Object.keys(rows[0]) : [];
  const rootField = ROOT_FIELDS.find(f => header.includes(f)) ?? null;

  const rootCounts = new Map();
  let withRoot = 0;
  for (const row of rows) {
    const rk = rootField ? (row[rootField] ?? "").trim() : "";
    if (!rk) continue;
    withRoot += 1;
    rootCounts.set(rk, (rootCounts.get(rk) ?? 0) + 1);
  }

  const topRoots = [...rootCounts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, TOP_ROOTS)
    .map(([root, count]) => ({ root, count }));

  return {
    code: DISPLAY_CODE.get(code) ?? code.toUpperCase(),
    sourceCode: code,
    sourceFile: `../csl-orig/v02/${code}/${code}_etymology.tsv`,
    rootStyle: rootField ? STYLE_BY_FIELD[rootField] : "none",
    rows: rows.length,
    headwordsWithRoot: withRoot,
    rootCoveragePct: rows.length ? Number(((100 * withRoot) / rows.length).toFixed(2)) : 0,
    distinctRoots: rootCounts.size,
    topRoots
  };
}

function consumeAgreement() {
  const file = path.join(STATS, "cross_dict_root_agreement.csv");
  if (!fs.existsSync(file)) return null;
  const pairs = parseDelimited(fs.readFileSync(file, "utf8"), ",").map(r => ({
    dictA: r.dict_a,
    dictB: r.dict_b,
    sharedHeadwords: Number(r.shared_headwords),
    rootAgrees: Number(r.root_agrees),
    pct: Number(r.pct),
    ci95Low: Number(r.ci95_low),
    ci95High: Number(r.ci95_high)
  }));
  const ranked = [...pairs].filter(p => p.sharedHeadwords >= 50).sort((a, b) => b.pct - a.pct);
  return {
    source: "../csl-orig/v02/etymology_stats/cross_dict_root_agreement.csv",
    method: "pairwise headword-level root agreement, Wilson 95% CI (csl-orig stats_etymology.py §6b)",
    pairCount: pairs.length,
    highestAgreement: ranked.slice(0, 5),
    lowestAgreement: ranked.slice(-5).reverse(),
    pairs
  };
}

function consumeProductivity() {
  const file = path.join(STATS, "root_productivity.csv");
  if (!fs.existsSync(file)) return null;
  const rows = parseDelimited(fs.readFileSync(file, "utf8"), ",").map(r => ({
    root: r.root,
    derivatives: Number(r.derivatives)
  }));
  return {
    source: "../csl-orig/v02/etymology_stats/root_productivity.csv",
    note: "verbal-root dicts + MW; WIL excluded upstream (its root is the first etymon, not a dhAtu)",
    topRoots: rows
  };
}

function discoverDicts() {
  return fs.readdirSync(ROOT)
    .filter(name => {
      const dir = path.join(ROOT, name);
      return fs.statSync(dir).isDirectory() && fs.existsSync(path.join(dir, `${name}_etymology.tsv`));
    })
    .sort();
}

function main() {
  if (!fs.existsSync(ROOT)) throw new Error(`Missing source root: ${ROOT}`);
  const codes = discoverDicts();
  if (!codes.length) throw new Error(`No *_etymology.tsv found under ${ROOT}`);

  const dicts = codes.map(analyseDict)
    .sort((a, b) => b.headwordsWithRoot - a.headwordsWithRoot || a.code.localeCompare(b.code));

  const rootAgreement = consumeAgreement();
  const rootProductivity = consumeProductivity();

  const payload = {
    generatedAt: new Date().toISOString(),
    ...licenseFields(),
    sourceRoot: "../csl-orig/v02",
    derivedFrom: "csl-orig <dict>_etymology.tsv + etymology_stats aggregates",
    provenance: "derivation-oracle (read-only consume; the atlas does not re-extract or recompute)",
    note: "Per-dict summaries are read from the TSVs. Cross-dict root agreement and productivity "
      + "are consumed verbatim from csl-orig/etymology_stats, NOT recomputed here.",
    dictionaryCount: dicts.length,
    totals: {
      etymologyRows: dicts.reduce((s, d) => s + d.rows, 0),
      headwordsWithRoot: dicts.reduce((s, d) => s + d.headwordsWithRoot, 0)
    },
    rootAgreement,
    rootProductivity,
    dicts
  };

  for (const out of OUT) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    payload.generatedAt = generatedAtForPayload(readJsonIfExists(out, fs), payload);
    fs.writeFileSync(out, `${JSON.stringify(payload, null, 2)}\n`);
  }

  const top = rootAgreement?.highestAgreement?.[0];
  console.log(`Etymology oracle: ${dicts.length} dicts, ${payload.totals.headwordsWithRoot} rooted headwords.`);
  if (top) console.log(`  agreement consumed: ${rootAgreement.pairCount} pairs; top ${top.dictA}~${top.dictB} ${top.pct}%`);
  for (const out of OUT) console.log(`- ${path.relative(process.cwd(), out)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
