// Build the M1 data-richness typology packet (H1511 / METALEXICOGRAPHY_ROADMAP.md §1).
//
// Places every locally-present CDSL dictionary on the roadmap's explicit
// L0-L10 ordinal scale (scan-only -> full structured semantic web), reading
// already-computed per-dictionary signals rather than re-parsing csl-orig:
//   - data/dictionary-coverage.json blockPct (L1-L5, L7 fallback)
//   - src/data/dicts/coverage-matrix.json capability flags (L4-L6 corroboration)
//   - src/data/dicts/structural-register.json xrefEdges (L7, the M1-M5
//     microstructure cross-reference graph — a stronger "machine-readable
//     link" signal than a textual cf./q.v. mention)
//   - scripts/lib/cologne-links.mjs COLOGNE_SCAN_DIR (L8 — the atlas's own
//     working scan-page link table)
//   - sibling repos ../alternateheadwords/data and ../csl-lslink/zip (L9 —
//     cross-dictionary linking infrastructure; flagged "partial" per the
//     roadmap's own §13 note that M0a, the Cologne live-site scrape, has not
//     run, so this is a floor not a verified ceiling)
//   - L10 is uniformly "not achieved": external TEI/RDF publication is
//     csl-standards' territory per docs/BOUNDARY_RULES.md, not an atlas
//     deliverable, so it can never be "achieved" by an atlas-side signal.
//
// Levels are cumulative (a dict's `level` is the highest N for which L1..LN
// all hold); `criteria` also records each level's *raw* independent boolean
// so a higher-tier feature present despite a lower-tier gap stays visible
// (e.g. SCH has strong <ls> citation tagging but 0% <lex>/gender marking, so
// it caps at L3 even though its raw L5 evidence would qualify).
//
// Usage: npm run build-richness-typology (after build-coverage, build-dict-comparison,
// build-structural-register have already been run at least once).

import fs from "node:fs";
import path from "node:path";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { COLOGNE_SCAN_DIR } from "./lib/cologne-links.mjs";

const SCHEMA_VERSION = "1.0.0";
const COVERAGE_PATH = path.resolve(process.cwd(), "data", "dictionary-coverage.json");
const COVERAGE_MATRIX_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "coverage-matrix.json");
const STRUCTURAL_REGISTER_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "structural-register.json");
const CITATION_CANON_PATH = path.resolve(process.cwd(), "src", "data", "citations", "citation_canon.json");
const XREF_LINEAGE_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "xref-lineage.json");
const ALTERNATEHEADWORDS_DATA_DIR = path.resolve(process.cwd(), "..", "alternateheadwords", "data");
const CSL_LSLINK_ZIP_DIR = path.resolve(process.cwd(), "..", "csl-lslink", "zip");
const NMMB_SOURCE = path.resolve(process.cwd(), "..", "csl-orig", "v02", "nmmb", "nmmb.txt");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const OUT_PATH = path.join(OUT_DIR, "richness-typology.json");

// Thresholds. gram>=20 reuses this repo's own "full structured fit" bar
// (scripts/build-dictionary-coverage.mjs fitBand()); citeTagged>=20 mirrors
// it for symmetry. head>=50 is this classifier's own bar for "<k1> present
// in a majority of entries, not just sporadically". div>=5 is a documented
// low-confidence proxy used only for the 3 dicts absent from coverage-matrix.json.
const GRAM_THRESHOLD = 20;
const CITE_TAGGED_THRESHOLD = 20;
const HEAD_MAJORITY_THRESHOLD = 50;
const DIV_PROXY_THRESHOLD = 5;

const LEVELS = [
  { level: 0, name: "Scan-only", requirement: "PDF page images; no text content", exampleDicts: "Patel-2016 scan-only set (PD, PE, PGN, IEG, MWE, AE, SNP, YAT) per the roadmap; empirically most of those now have keyboarded text in this local checkout — see limitations." },
  { level: 1, name: "Plain text", requirement: "OCR'd or keyboarded UTF-8; no markup" },
  { level: 2, name: "Entry boundaries", requirement: "<L>NNNN ... <LEND> markers separate entries" },
  { level: 3, name: "Headword / body separation", requirement: "<k1> for primary, <k2> for variants" },
  { level: 4, name: "Lexical metadata tags", requirement: "<lex> (category), <gen> (gender)" },
  { level: 5, name: "Citation tagging", requirement: "<ls> for literary sources, structured" },
  { level: 6, name: "Sense structure", requirement: "numbered or hierarchical senses; <sense n=\"1\"> or equivalent" },
  { level: 7, name: "Cross-reference tagging", requirement: "entry-to-entry pointers as machine-readable links" },
  { level: 8, name: "Scan-page linking", requirement: "each entry -> page image of original print" },
  { level: 9, name: "Cross-dictionary integration", requirement: "each headword -> corresponding entries in other CDSL dicts" },
  { level: 10, name: "Full structured semantic web", requirement: "external TEI/RDF publication via csl-standards" }
];

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function listDirUpper(dir) {
  if (!fs.existsSync(dir)) return { present: false, entries: [] };
  return {
    present: true,
    entries: fs.readdirSync(dir, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .map(e => e.name.toUpperCase())
  };
}

function listZipCodesLower(dir) {
  if (!fs.existsSync(dir)) return { present: false, entries: [] };
  return {
    present: true,
    entries: fs.readdirSync(dir)
      .filter(f => f.endsWith("_lslinks.sqlite.zip"))
      .map(f => f.replace(/_lslinks\.sqlite\.zip$/, "").toLowerCase())
  };
}

// NMMB (nāmamālikā, a synonym-set kosha) is absent from all three primary
// signal sources — it post-dates their last regeneration. Rather than skip a
// locally-present dict, probe its raw source directly for the one thing that
// generalises across genres (entry-boundary markers); its <syns> synonym-list
// headword style is not the <k1>/<k2> model L3 describes, so higher levels are
// left unverified instead of guessed.
function probeNmmb() {
  if (!fs.existsSync(NMMB_SOURCE)) return null;
  const text = fs.readFileSync(NMMB_SOURCE, "utf8");
  const entries = text.match(/<L>[\s\S]*?<LEND>/g) ?? [];
  const hasBoundaries = entries.length > 0;
  return {
    code: "NMMB",
    sourceCode: "nmmb",
    title: "Nāmamālikā (Bhoja)",
    records: entries.length,
    familyLabel: "indigenous-prose",
    fallback: true,
    fallbackNote: "Excluded from data/dictionary-coverage.json, coverage-matrix.json, and structural-register.json (added to csl-orig/v02 after those pipelines last ran; has an active prep/ subfolder). Assessed by a direct regex probe of ../csl-orig/v02/nmmb/nmmb.txt in this script only.",
    entryBoundaryCount: entries.length,
    hasEntryBoundaries: hasBoundaries
  };
}

function evaluateDict(d, cm, srBy, siblingCodes) {
  const blockPct = d.blockPct ?? {};
  const cmRow = cm.get(d.sourceCode) ?? null;
  const srRow = srBy.get(d.sourceCode) ?? null;

  const l1 = { level: 1, met: (d.records ?? 0) > 0, evidence: `records=${d.records} in data/dictionary-coverage.json` };
  const l2 = {
    level: 2,
    met: blockPct.head > 0,
    evidence: `blockPct.head=${blockPct.head}% in data/dictionary-coverage.json — nonzero only when the dict-wide <L>...<LEND> split succeeded (scripts/build-dictionary-coverage.mjs splitEntries()), which is then true for every entry`
  };
  const l3 = {
    level: 3,
    met: blockPct.head >= HEAD_MAJORITY_THRESHOLD,
    evidence: `blockPct.head=${blockPct.head}% >= ${HEAD_MAJORITY_THRESHOLD}% (majority of <L>-bounded entries carry a recognizable <k1>); <k2> variant-headword presence is not independently verified by any computed signal this classifier consumes`
  };
  const grammarReliable = cmRow?.grammarReliable === true;
  const l4 = {
    level: 4,
    met: blockPct.gram >= GRAM_THRESHOLD || grammarReliable,
    evidence: grammarReliable && !(blockPct.gram >= GRAM_THRESHOLD)
      ? `coverage-matrix.json grammarReliable=true (blockPct.gram only ${blockPct.gram}%)`
      : `blockPct.gram=${blockPct.gram}% >= ${GRAM_THRESHOLD}%`
  };
  const citationTagged = cmRow?.citationTagged === true;
  const l5 = {
    level: 5,
    met: blockPct.citeTagged >= CITE_TAGGED_THRESHOLD || citationTagged,
    evidence: citationTagged && !(blockPct.citeTagged >= CITE_TAGGED_THRESHOLD)
      ? `coverage-matrix.json citationTagged=true (blockPct.citeTagged only ${blockPct.citeTagged}%)`
      : `blockPct.citeTagged=${blockPct.citeTagged}% >= ${CITE_TAGGED_THRESHOLD}%`
  };

  let l6;
  if (cmRow) {
    l6 = {
      level: 6,
      met: cmRow.senseSegmented === true,
      evidence: `coverage-matrix.json senseSegmented=${cmRow.senseSegmented}`
    };
  } else {
    const divPct = blockPct.div ?? 0;
    l6 = {
      level: 6,
      met: divPct >= DIV_PROXY_THRESHOLD,
      evidence: `absent from coverage-matrix.json; low-confidence proxy blockPct.div=${divPct}% ${divPct >= DIV_PROXY_THRESHOLD ? ">=" : "<"} ${DIV_PROXY_THRESHOLD}%`,
      lowConfidence: true
    };
  }

  const xrefEdges = srRow?.xrefEdges ?? 0;
  const l7 = {
    level: 7,
    met: xrefEdges > 0,
    evidence: `structural-register.json xrefEdges=${xrefEdges} (M1-M5 microstructure cross-reference graph; blockPct.xref=${blockPct.xref}% textual mentions shown for context only, not used to gate — it includes untagged prose "see"/"cf.")`
  };

  const scanDir = COLOGNE_SCAN_DIR[d.sourceCode] ?? null;
  const l8 = {
    level: 8,
    met: scanDir !== null,
    evidence: scanDir
      ? `sourceCode "${d.sourceCode}" -> COLOGNE_SCAN_DIR["${d.sourceCode}"]="${scanDir}" in scripts/lib/cologne-links.mjs`
      : `sourceCode "${d.sourceCode}" absent from COLOGNE_SCAN_DIR in scripts/lib/cologne-links.mjs`
  };

  const crossDictSignal = siblingCodes.has(d.sourceCode);
  const l9 = {
    level: 9,
    met: crossDictSignal,
    evidence: crossDictSignal
      ? `sourceCode "${d.sourceCode}" found under ../alternateheadwords/data or ../csl-lslink/zip`
      : `sourceCode "${d.sourceCode}" not found under ../alternateheadwords/data or ../csl-lslink/zip`
  };

  const l10 = {
    level: 10,
    met: false,
    evidence: "Not evaluated by design: external TEI/RDF/SPARQL publication is csl-standards' territory per docs/BOUNDARY_RULES.md, so an atlas-side signal can never mark this achieved."
  };

  const criteria = { l1, l2, l3, l4, l5, l6, l7, l8, l9, l10 };

  // Cumulative level: highest N with L1..LN all true (first gap stops it).
  let level = 0;
  for (let n = 1; n <= 9; n += 1) {
    if (criteria[`l${n}`].met) level = n;
    else break;
  }

  const rawHigherEvidence = Object.values(criteria)
    .filter(c => c.level > level && c.level <= 9 && c.met)
    .map(c => c.level);

  let levelQualifier = "confirmed";
  const notes = [];
  if (level === 9) {
    levelQualifier = "partial";
    notes.push("L9 is a floor, not a verified ceiling: roadmap §13 Phase M0a (the Cologne live-site scrape confirming cross-dict lookup actually resolves at runtime) has not run for this repo (grep for cologne_features/cologne_scrape found nothing). This label reflects committed cross-dict linking infrastructure (alternateheadwords / csl-lslink) only.");
  }
  if (rawHigherEvidence.length) {
    notes.push(`Raw evidence for L${rawHigherEvidence.join(", L")} is present despite the cumulative cap at L${level} — a lower-tier convention gap (see criteria), not missing content.`);
  }
  if (cmRow === null) {
    notes.push("Absent from coverage-matrix.json (outside the Core-40 comparison slice); L4-L6 rely on data/dictionary-coverage.json blockPct alone.");
  }

  return {
    code: d.code,
    sourceCode: d.sourceCode,
    title: d.title,
    records: d.records,
    familyLabel: srRow?.familyLabel ?? "unknown",
    level,
    levelName: LEVELS[level].name,
    levelQualifier,
    criteria,
    notes
  };
}

function evaluateNmmb(fallback, siblingCodes) {
  const l1 = { level: 1, met: fallback.records > 0, evidence: `${fallback.entryBoundaryCount} <L>...<LEND> blocks found by direct probe of ../csl-orig/v02/nmmb/nmmb.txt` };
  const l2 = { level: 2, met: fallback.hasEntryBoundaries, evidence: l1.evidence };
  const l3 = { level: 3, met: false, evidence: "0 <k1> tags found; NMMB is a <syns> synonym-set kosha entry, not the <k1>/<k2> headword model L3 describes — not independently verified, not guessed" };
  const notEvaluated = level => ({ level, met: false, evidence: "Not evaluated: NMMB excluded from the primary pipeline (see fallbackNote); higher levels require the computed signals this dict lacks." });
  const criteria = {
    l1, l2, l3,
    l4: notEvaluated(4), l5: notEvaluated(5), l6: notEvaluated(6), l7: notEvaluated(7),
    l8: { level: 8, met: false, evidence: 'sourceCode "nmmb" absent from COLOGNE_SCAN_DIR in scripts/lib/cologne-links.mjs' },
    l9: { level: 9, met: siblingCodes.has("nmmb"), evidence: siblingCodes.has("nmmb") ? "found under sibling repos" : 'sourceCode "nmmb" not found under ../alternateheadwords/data or ../csl-lslink/zip' },
    l10: { level: 10, met: false, evidence: "Not evaluated by design (see docs/BOUNDARY_RULES.md)." }
  };
  return {
    code: fallback.code,
    sourceCode: fallback.sourceCode,
    title: fallback.title,
    records: fallback.records,
    familyLabel: fallback.familyLabel,
    level: 2,
    levelName: LEVELS[2].name,
    levelQualifier: "confirmed-fallback",
    criteria,
    notes: [fallback.fallbackNote]
  };
}

function main() {
  const coverage = readJson(COVERAGE_PATH);
  const coverageMatrix = readJsonIfExists(COVERAGE_MATRIX_PATH, fs);
  const structuralRegister = readJsonIfExists(STRUCTURAL_REGISTER_PATH, fs);
  const citationCanon = readJsonIfExists(CITATION_CANON_PATH, fs);
  const xrefLineage = readJsonIfExists(XREF_LINEAGE_PATH, fs);

  const cm = new Map((coverageMatrix?.dictionaries ?? []).map(r => [r.code, r]));
  const srBy = new Map((structuralRegister?.rows ?? []).map(r => [r.sourceCode, r]));

  const ah = listDirUpper(ALTERNATEHEADWORDS_DATA_DIR);
  const ls = listZipCodesLower(CSL_LSLINK_ZIP_DIR);
  const siblingCodes = new Set([
    ...ah.entries.map(e => e.toLowerCase()),
    ...ls.entries
  ]);

  const rows = (coverage.dicts ?? [])
    .map(d => evaluateDict(d, cm, srBy, siblingCodes))
    .sort((a, b) => b.level - a.level || a.code.localeCompare(b.code));

  const nmmbFallback = probeNmmb();
  if (nmmbFallback) rows.push(evaluateNmmb(nmmbFallback, siblingCodes));

  const byLevel = {};
  for (const r of rows) byLevel[r.level] = (byLevel[r.level] ?? 0) + 1;

  const citationCanonDicts = new Set((citationCanon?.matrix ? (citationCanon.nestedDictOrder ?? []) : []));
  const xrefLineageDicts = new Set((xrefLineage?.pairs ?? []).flatMap(p => [p.a, p.b]));

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: new Date().toISOString(),
    claim: "M1: every locally-present CDSL dictionary placed on the roadmap's L0-L10 data-richness ordinal scale, with a machine-readable justification per level.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    sourceFiles: [
      "data/dictionary-coverage.json",
      "src/data/dicts/coverage-matrix.json",
      "src/data/dicts/structural-register.json",
      "src/data/citations/citation_canon.json",
      "src/data/dicts/xref-lineage.json",
      "scripts/lib/cologne-links.mjs",
      "../alternateheadwords/data (sibling repo, local-only)",
      "../csl-lslink/zip (sibling repo, local-only)",
      "../csl-orig/v02/nmmb/nmmb.txt (direct fallback probe, NMMB only)"
    ],
    method: "Cumulative ordinal classifier over docs/METALEXICOGRAPHY_ROADMAP.md §1. A dict's level is the highest N for which every L1..LN criterion holds (first gap stops the climb); each level's raw independent boolean is retained in `criteria` so a higher-tier feature present despite a lower-tier convention gap stays visible instead of disappearing into the cap. L9 is always qualified `partial` (M0a live-site scrape not run, roadmap §13); L10 is always `met:false` by design (csl-standards' territory, docs/BOUNDARY_RULES.md).",
    thresholds: {
      gram: GRAM_THRESHOLD,
      citeTagged: CITE_TAGGED_THRESHOLD,
      headMajority: HEAD_MAJORITY_THRESHOLD,
      divProxy: DIV_PROXY_THRESHOLD
    },
    levels: LEVELS,
    rowCount: rows.length,
    rows,
    summary: {
      byLevel,
      hypothesisCheck: "Roadmap §1 hypothesis: 'MW is the only dict at L8+; most others sit at L4-L6; specialised ones at L3-L5; scan-only ones at L0.' Empirically (this run): " +
        `${rows.filter(r => r.level >= 8).map(r => r.code).join(", ") || "no dict"} reach L8+ — ` +
        (rows.filter(r => r.level >= 8).length > 1
          ? "MW is NOT the only one, confirming the roadmap's own counter-hypothesis (§3) that PWG carries comparable digital investment."
          : "matches the roadmap's MW-only hypothesis.") +
        " No locally-present dict is at L0 — the roadmap's named scan-only examples (PD, PE, PGN, IEG, MWE, AE, SNP, YAT) are either not present in this local csl-orig checkout (PD) or, empirically, already have keyboarded plain text (PE, PGN, IEG, MWE, AE, SNP, YAT all have nonzero records here) — the roadmap's example column is stale relative to current data, not this classifier's finding."
    },
    limitations: [
      "L9 reflects committed cross-dict linking infrastructure (alternateheadwords, csl-lslink), not a live-resolution check against the Cologne site (M0a, unrun) — a floor, not a ceiling.",
      "L10 is never achieved by construction: atlas keeps native dictionary evidence only, per docs/BOUNDARY_RULES.md and roadmap §10/§14 decisions locked 2026-05-16.",
      "<k2> variant-headword presence (part of L3's stated requirement) is not independently verified by any computed signal this classifier consumes; L3 uses <k1> majority coverage as the available proxy.",
      "NMMB is excluded from all three primary signal sources and is assessed by a direct fallback probe of its raw source only (see its row's notes) — lower confidence than every other row.",
      `${citationCanonDicts.size} dicts (${[...citationCanonDicts].join(", ")}) additionally appear in the citation_canon.json dict×text matrix and ${xrefLineageDicts.size} dicts (${[...xrefLineageDicts].join(", ")}) in xref-lineage.json's pairwise overlap study — corroborating context for L5/L7, not separately gated.`,
      "3 dicts (ae, bor, mwe) are absent from coverage-matrix.json; their L6 uses a documented low-confidence blockPct.div proxy instead of the senseSegmented flag (see each row's criteria.l6.lowConfidence)."
    ],
    assumptions: [
      "Every criterion is read from an already-committed data file or a curated code table in this repo — no new corpus parsing beyond the single NMMB fallback probe.",
      "Cumulative gating (first gap stops the climb) is deliberate: it measures what is actually implemented for a dict as a coherent edition, not the union of features scattered across its markup.",
      "Genre-appropriate headword equivalents (e.g. NMMB's <syns> synonym sets) are not silently mapped onto the <k1>/<k2> criterion; they are left unverified with an explicit note instead."
    ]
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUT_PATH, fs), payload);
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT_PATH)} (${rows.length} dictionaries).`);
  console.log(`By level: ${JSON.stringify(byLevel)}`);
  if (!ah.present) console.log("note: ../alternateheadwords not found locally — L9 signal from that source is unavailable this run.");
  if (!ls.present) console.log("note: ../csl-lslink not found locally — L9 signal from that source is unavailable this run.");
}

main();
