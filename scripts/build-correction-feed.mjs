// Build the correction-loci packet: the atlas-side aggregation of the
// csl-corrections correction_loci.tsv feed (H306; DH_IMPROVEMENT_MEMO §2/§3).
//
// The feed is OWNED by csl-corrections (scripts/build_correction_loci.py) and
// consumed here read-only from the sibling checkout — never re-derived from
// the change files. This script filters/aggregates the 39k-row TSV into a
// page-sized committed JSON so no site page reads a sibling path and CI needs
// no sibling checkout (VISUALDCS_CONSUMPTION_CONTRACT pattern).
//
// Aggregations emitted (all split by process ∈ {bulk, human} — BOR + LRV
// machine batches are 76% of records and would otherwise dominate every view):
//   - perDict editorial KPIs: records, human/bulk, corrections per 1k entries
//     (entry counts from the feed's dict_entry_counts.tsv sidecar), human
//     share, corrected-page coverage, date span — the §2.6 editorial-overlay
//     axes for the METALEXICOGRAPHY_ROADMAP §3 per-dict radar.
//   - heatmap cells: dict × normalized page-position bin × process, for dicts
//     with enough <pc>-resolved records to bin honestly.
//   - per-dict column detail where the dict's column notation is regular.
//   - top corrected pages per dict, with a sample record for /tools/source
//     deep links.
//   - monthly batch-date counts by process.
//
// Usage: npm run build-correction-feed   (then npm run validate-correction-feed)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-correction-feed";
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "csl-corrections");
const FEED_PATH = path.join(SIBLING_ROOT, "data", "derived", "correction_loci.tsv");
const ENTRIES_PATH = path.join(SIBLING_ROOT, "data", "derived", "dict_entry_counts.tsv");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "corrections");
const JSON_OUT = path.join(OUT_DIR, "correction_loci.json");
const SOURCE_OUT = path.join(OUT_DIR, "correction_loci.source.json");

const POSITION_BINS = 40;      // normalized page-position bins per dict
const HEATMAP_MIN_LOCI = 30;   // min <pc>-resolved records for a heatmap row
const TOP_PAGES = 10;          // top corrected pages listed per dict
const MAX_COLUMN_KINDS = 4;    // column detail only for regular notations (1/2/3, a/b)

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

export function parseTsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

export function positionBin(page, maxPage, bins = POSITION_BINS) {
  if (!Number.isFinite(page) || !Number.isFinite(maxPage) || maxPage <= 0) return null;
  return Math.max(0, Math.min(bins - 1, Math.floor((page / maxPage) * bins)));
}

export function buildPayload(feedRows, entryRows, { generatedAt } = {}) {
  const entryCounts = new Map();
  for (const r of entryRows) {
    const n = Number(r.entries);
    if (r.dict && Number.isFinite(n)) entryCounts.set(r.dict, n);
  }

  const byDict = new Map();
  const monthly = new Map(); // "YYYY-MM|process" -> count
  let nRecords = 0;
  const processTotals = { human: 0, bulk: 0 };

  for (const row of feedRows) {
    const dict = row.dict;
    if (!dict) continue;
    nRecords += 1;
    const process = row.process === "bulk" ? "bulk" : "human";
    processTotals[process] += 1;

    let d = byDict.get(dict);
    if (!d) {
      d = {
        dict,
        records: 0,
        human: 0,
        bulk: 0,
        pcResolved: 0,
        maxPage: 0,
        pages: new Map(),         // page -> { count, human, bulk, sampleK1, sampleLine }
        cols: new Map(),          // col -> count (pc-resolved rows only)
        loci: [],                 // { page, col, process }
        directives: new Map(),
        tagContexts: new Map(),
        firstDate: null,
        lastDate: null
      };
      byDict.set(dict, d);
    }
    d.records += 1;
    d[process] += 1;
    d.directives.set(row.directive, (d.directives.get(row.directive) ?? 0) + 1);
    d.tagContexts.set(row.tag_context, (d.tagContexts.get(row.tag_context) ?? 0) + 1);

    const date = row.batch_date || "";
    if (/^\d{4}-\d{2}/.test(date)) {
      if (!d.firstDate || date < d.firstDate) d.firstDate = date;
      if (!d.lastDate || date > d.lastDate) d.lastDate = date;
      const key = `${date.slice(0, 7)}|${process}`;
      monthly.set(key, (monthly.get(key) ?? 0) + 1);
    }

    const page = Number(row.pc_page);
    if (Number.isFinite(page) && row.pc_page !== "") {
      d.pcResolved += 1;
      d.maxPage = Math.max(d.maxPage, page);
      d.loci.push({ page, col: row.pc_col || "", process });
      let p = d.pages.get(page);
      if (!p) {
        p = { count: 0, human: 0, bulk: 0, sampleK1: row.k1, sampleLine: Number(row.line) || null };
        d.pages.set(page, p);
      }
      p.count += 1;
      p[process] += 1;
      if (row.pc_col) d.cols.set(row.pc_col, (d.cols.get(row.pc_col) ?? 0) + 1);
    }
  }

  const dicts = [...byDict.keys()].sort(
    (a, b) => byDict.get(b).records - byDict.get(a).records || a.localeCompare(b)
  );

  const perDict = dicts.map((dict) => {
    const d = byDict.get(dict);
    const entries = entryCounts.get(dict) ?? null;
    const distinctPages = d.pages.size;
    return {
      dict,
      records: d.records,
      human: d.human,
      bulk: d.bulk,
      humanShare: round(d.human / d.records),
      entries,
      per1k: entries ? round((d.records / entries) * 1000, 2) : null,
      per1kHuman: entries ? round((d.human / entries) * 1000, 2) : null,
      pcResolved: d.pcResolved,
      pcResolvedShare: round(d.pcResolved / d.records),
      maxPage: d.maxPage || null,
      distinctPages,
      pageCoverage: d.maxPage > 0 ? round(distinctPages / d.maxPage) : null,
      firstDate: d.firstDate,
      lastDate: d.lastDate,
      directives: Object.fromEntries([...d.directives.entries()].sort((a, b) => b[1] - a[1])),
      topTagContexts: Object.fromEntries(
        [...d.tagContexts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
      )
    };
  });

  // Heatmap: dict × normalized-position bin × process.
  const heatmapDicts = dicts.filter((dict) => byDict.get(dict).pcResolved >= HEATMAP_MIN_LOCI);
  const heatmapCells = [];
  const columnCells = [];
  const columnDicts = [];
  for (const dict of heatmapDicts) {
    const d = byDict.get(dict);
    const binCounts = new Map(); // "bin|process" -> count
    for (const locus of d.loci) {
      const bin = positionBin(locus.page, d.maxPage);
      if (bin === null) continue;
      const key = `${bin}|${locus.process}`;
      binCounts.set(key, (binCounts.get(key) ?? 0) + 1);
    }
    for (const [key, count] of binCounts) {
      const [bin, process] = key.split("|");
      heatmapCells.push({ dict, bin: Number(bin), process, count });
    }

    // Column detail only where the notation is regular (e.g. MW 1/2/3, GRA a/b)
    // and covers most pc-resolved rows; LRV-style irregular codes are skipped.
    const colKinds = [...d.cols.keys()];
    const colCovered = [...d.cols.values()].reduce((a, b) => a + b, 0);
    if (colKinds.length > 0 && colKinds.length <= MAX_COLUMN_KINDS && colCovered / d.pcResolved >= 0.6) {
      columnDicts.push(dict);
      const colBinCounts = new Map(); // "bin|col|process" -> count
      for (const locus of d.loci) {
        if (!locus.col || !d.cols.has(locus.col)) continue;
        const bin = positionBin(locus.page, d.maxPage);
        if (bin === null) continue;
        const key = `${bin}|${locus.col}|${locus.process}`;
        colBinCounts.set(key, (colBinCounts.get(key) ?? 0) + 1);
      }
      for (const [key, count] of colBinCounts) {
        const [bin, col, process] = key.split("|");
        columnCells.push({ dict, bin: Number(bin), col, process, count });
      }
    }
  }
  heatmapCells.sort((a, b) => a.dict.localeCompare(b.dict) || a.bin - b.bin || a.process.localeCompare(b.process));
  columnCells.sort((a, b) => a.dict.localeCompare(b.dict) || a.bin - b.bin || a.col.localeCompare(b.col) || a.process.localeCompare(b.process));

  const topPages = [];
  for (const dict of dicts) {
    const d = byDict.get(dict);
    const ranked = [...d.pages.entries()]
      .sort((a, b) => b[1].count - a[1].count || a[0] - b[0])
      .slice(0, TOP_PAGES);
    for (const [page, p] of ranked) {
      topPages.push({
        dict,
        page,
        count: p.count,
        human: p.human,
        bulk: p.bulk,
        sampleK1: p.sampleK1,
        sampleLine: p.sampleLine
      });
    }
  }

  const monthlyRows = [...monthly.entries()]
    .map(([key, count]) => {
      const [month, process] = key.split("|");
      return { month, process, count };
    })
    .sort((a, b) => a.month.localeCompare(b.month) || a.process.localeCompare(b.process));

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "csl-corrections/data/derived/correction_loci.tsv",
      "csl-corrections/data/derived/dict_entry_counts.tsv",
      "scripts/build-correction-feed.mjs"
    ],
    method:
      "Read the csl-corrections correction_loci.tsv feed (one row per corrected source line, locus-resolved to the printed <pc> page where the change files carry it) plus its dict_entry_counts.tsv sidecar (grep -c '^<L>' per csl-orig v02 dict). Aggregate per dict and per process (bulk vs human batches); bin <pc>-resolved records into " +
      `${POSITION_BINS} normalized page-position bins, where position = page / that dictionary's highest corrected page seen in the feed (an underestimate of the true page count — see limitations).`,
    positionBins: POSITION_BINS,
    heatmapMinLoci: HEATMAP_MIN_LOCI,
    totals: {
      records: nRecords,
      human: processTotals.human,
      bulk: processTotals.bulk,
      dicts: dicts.length,
      pcResolved: perDict.reduce((a, d) => a + d.pcResolved, 0)
    },
    perDict,
    heatmapDicts,
    heatmapCells,
    columnDicts,
    columnCells,
    topPages,
    monthly: monthlyRows,
    limitations: [
      "Correction density measures REPORTED-AND-FIXED errors, not true error rate: reader traffic biases where errors get found (memo C6), so hot pages read as attention, not necessarily print quality.",
      "76% of records are machine batches (BOR digitization completion 21,990; LRV/markhom 8,063) — every view is split by process, and dictionary-level comparisons should default to the human series.",
      "Normalized page position divides by each dictionary's highest CORRECTED page in the feed, not the true printed page count — the far tail of a barely-corrected dictionary is invisible, and the last bin is anchored at the last corrected page by construction.",
      "Entry counts are current csl-orig v02 <L> record counts, not entry counts at correction time.",
      "pc resolution varies by dict (e.g. STC change files carry no <pc> headers); pcResolvedShare states the binnable fraction per dict."
    ],
    boundary: [
      "Feed owner is csl-corrections (scripts/build_correction_loci.py); this packet only aggregates it — never re-parses change files. Rendering owner repo csl-atlas."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  let commit = "unknown";
  let feedCommit = "unknown";
  try {
    commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {}
  try {
    feedCommit = execSync(`git -C "${SIBLING_ROOT}" rev-parse HEAD`, { encoding: "utf8" }).trim();
  } catch {}
  const envelope = {
    dataset: "correction_loci",
    commit,
    feedRepo: "https://github.com/sanskrit-lexicon/csl-corrections",
    feedCommit,
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  if (!fs.existsSync(FEED_PATH)) {
    console.error(
      `Feed not found: ${FEED_PATH}\n` +
        "This builder needs a sibling csl-corrections checkout (the committed src/data/corrections/correction_loci.json is the CI-safe artifact)."
    );
    process.exit(1);
  }
  const feedRows = parseTsv(fs.readFileSync(FEED_PATH, "utf8"));
  const entryRows = fs.existsSync(ENTRIES_PATH) ? parseTsv(fs.readFileSync(ENTRIES_PATH, "utf8")) : [];
  const payload = buildPayload(feedRows, entryRows);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(`Wrote correction-loci packet (${payload.totals.records} records, ${payload.totals.dicts} dicts):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(`  human ${payload.totals.human} / bulk ${payload.totals.bulk}; pc-resolved ${payload.totals.pcResolved}`);
  console.log(`  heatmap dicts: ${payload.heatmapDicts.join(", ")}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
