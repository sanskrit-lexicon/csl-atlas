// Validate the committed correction-loci packet (H306).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// cross-check against the sibling csl-corrections feed runs only when the
// sibling checkout is present (it is not on CI runners).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - per-dict human+bulk != records, or totals disagree with the perDict rows;
// - a per-1k value disagrees with records/entries beyond rounding;
// - heatmap cell sums disagree with each included dict's pc-resolved count,
//   or a cell references an unknown dict / out-of-range bin / bad process;
// - top-pages rows exceed per-dict record counts or lack a sample line;
// - monthly counts do not sum to the dated-record total;
// - (sibling present) feed row count or per-dict counts diverge.
//
// Usage: npm run validate-correction-feed   (run after build-correction-feed)

import fs from "node:fs";
import path from "node:path";
import { parseTsv } from "./build-correction-feed.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "corrections");
const JSON_OUT = path.join(OUT_DIR, "correction_loci.json");
const SOURCE_OUT = path.join(OUT_DIR, "correction_loci.source.json");
const FEED_PATH = path.resolve(process.cwd(), "..", "csl-corrections", "data", "derived", "correction_loci.tsv");

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
  const perDict = new Map((packet.perDict ?? []).map((d) => [d.dict, d]));

  // Per-dict internal consistency.
  let sumRecords = 0;
  let sumHuman = 0;
  let sumBulk = 0;
  let sumPc = 0;
  for (const d of packet.perDict ?? []) {
    sumRecords += d.records;
    sumHuman += d.human;
    sumBulk += d.bulk;
    sumPc += d.pcResolved;
    if (d.human + d.bulk !== d.records) {
      errors.push(`${d.dict}: human ${d.human} + bulk ${d.bulk} != records ${d.records}`);
    }
    if (d.pcResolved > d.records) {
      errors.push(`${d.dict}: pcResolved ${d.pcResolved} > records ${d.records}`);
    }
    if (d.entries != null && d.per1k != null) {
      const expected = (d.records / d.entries) * 1000;
      if (Math.abs(expected - d.per1k) > 0.011) {
        errors.push(`${d.dict}: per1k ${d.per1k} != records/entries*1000 (${expected.toFixed(3)})`);
      }
    }
    if (d.maxPage != null && d.distinctPages > d.maxPage + 1) {
      errors.push(`${d.dict}: distinctPages ${d.distinctPages} exceeds maxPage ${d.maxPage}`);
    }
  }
  const t = packet.totals ?? {};
  if (sumRecords !== t.records) errors.push(`totals.records ${t.records} != perDict sum ${sumRecords}`);
  if (sumHuman !== t.human) errors.push(`totals.human ${t.human} != perDict sum ${sumHuman}`);
  if (sumBulk !== t.bulk) errors.push(`totals.bulk ${t.bulk} != perDict sum ${sumBulk}`);
  if (sumPc !== t.pcResolved) errors.push(`totals.pcResolved ${t.pcResolved} != perDict sum ${sumPc}`);
  if ((packet.perDict ?? []).length !== t.dicts) errors.push(`totals.dicts ${t.dicts} != perDict length`);

  // Heatmap cells: known dicts, bin range, process values, per-dict sums.
  const bins = packet.positionBins ?? 0;
  const heatmapSet = new Set(packet.heatmapDicts ?? []);
  const cellSums = new Map();
  for (const c of packet.heatmapCells ?? []) {
    if (!heatmapSet.has(c.dict)) errors.push(`heatmap cell references non-heatmap dict ${c.dict}`);
    if (!Number.isInteger(c.bin) || c.bin < 0 || c.bin >= bins) errors.push(`heatmap cell bin out of range: ${c.dict} bin ${c.bin}`);
    if (c.process !== "human" && c.process !== "bulk") errors.push(`heatmap cell bad process: ${c.dict} ${c.process}`);
    cellSums.set(c.dict, (cellSums.get(c.dict) ?? 0) + c.count);
  }
  for (const dict of heatmapSet) {
    const d = perDict.get(dict);
    if (!d) {
      errors.push(`heatmapDicts entry ${dict} missing from perDict`);
      continue;
    }
    if (d.pcResolved < (packet.heatmapMinLoci ?? 0)) {
      errors.push(`${dict}: in heatmapDicts with pcResolved ${d.pcResolved} < min ${packet.heatmapMinLoci}`);
    }
    if ((cellSums.get(dict) ?? 0) !== d.pcResolved) {
      errors.push(`${dict}: heatmap cell sum ${cellSums.get(dict) ?? 0} != pcResolved ${d.pcResolved}`);
    }
  }

  // Column cells reference declared column dicts and stay within heatmap dicts.
  const columnSet = new Set(packet.columnDicts ?? []);
  for (const dict of columnSet) {
    if (!heatmapSet.has(dict)) errors.push(`columnDicts entry ${dict} not in heatmapDicts`);
  }
  for (const c of packet.columnCells ?? []) {
    if (!columnSet.has(c.dict)) errors.push(`column cell references non-column dict ${c.dict}`);
    if (!Number.isInteger(c.bin) || c.bin < 0 || c.bin >= bins) errors.push(`column cell bin out of range: ${c.dict} bin ${c.bin}`);
  }

  // Top pages: per-dict caps and sample lines for source deep links.
  const topByDict = new Map();
  for (const p of packet.topPages ?? []) {
    if (!perDict.has(p.dict)) errors.push(`topPages references unknown dict ${p.dict}`);
    if (p.human + p.bulk !== p.count) errors.push(`topPages ${p.dict} p.${p.page}: human+bulk != count`);
    if (!(p.sampleLine > 0)) errors.push(`topPages ${p.dict} p.${p.page}: missing sampleLine`);
    topByDict.set(p.dict, (topByDict.get(p.dict) ?? 0) + p.count);
  }
  for (const [dict, sum] of topByDict) {
    const d = perDict.get(dict);
    if (d && sum > d.pcResolved) errors.push(`${dict}: topPages counts ${sum} exceed pcResolved ${d.pcResolved}`);
  }

  // Monthly counts sum to the record total (all feed rows carry batch dates).
  const monthlySum = (packet.monthly ?? []).reduce((a, m) => a + m.count, 0);
  if (monthlySum > t.records) errors.push(`monthly sum ${monthlySum} > totals.records ${t.records}`);
  if (monthlySum < t.records) notes.push(`monthly sum ${monthlySum} < totals.records ${t.records} (records without a parseable batch_date)`);

  // Sibling cross-check, only when the feed is present (not on CI).
  if (fs.existsSync(FEED_PATH)) {
    const feedRows = parseTsv(fs.readFileSync(FEED_PATH, "utf8"));
    if (feedRows.length !== t.records) {
      errors.push(`sibling feed has ${feedRows.length} rows, packet totals.records is ${t.records} — rerun npm run build-correction-feed`);
    }
    const feedCounts = new Map();
    for (const r of feedRows) feedCounts.set(r.dict, (feedCounts.get(r.dict) ?? 0) + 1);
    for (const [dict, n] of feedCounts) {
      const d = perDict.get(dict);
      if (!d) errors.push(`sibling feed dict ${dict} missing from packet`);
      else if (d.records !== n) errors.push(`${dict}: packet records ${d.records} != sibling feed ${n}`);
    }
    notes.push(`sibling feed cross-check ran (${feedRows.length} rows)`);
  } else {
    notes.push("sibling csl-corrections checkout absent — internal-consistency checks only (expected on CI)");
  }
}

if (envelope) {
  if (envelope.dataset !== "correction_loci") errors.push(`envelope dataset ${envelope.dataset} != correction_loci`);
  if (!envelope.feedCommit) errors.push("envelope missing feedCommit");
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length > 0) {
  console.error(`validate-correction-feed FAILED (${errors.length}):`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-correction-feed OK");
