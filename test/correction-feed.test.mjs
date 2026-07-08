import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { parseTsv, positionBin, buildPayload } from "../scripts/build-correction-feed.mjs";

const FIXED_AT = "2026-07-08T00:00:00.000Z";

function feedRow(overrides = {}) {
  return {
    dict: "mw",
    L: "376.1",
    pc_page: "10",
    pc_col: "1",
    k1: "akkA",
    k2: "akkA",
    line: "1358",
    batch: "batch_20240623",
    batch_date: "2024-06-23",
    process: "human",
    directive: "new",
    tag_context: "text",
    old: "a",
    new: "b",
    ...overrides
  };
}

test("parseTsv maps header to fields", () => {
  const rows = parseTsv("dict\tpc_page\nmw\t12\n");
  assert.equal(rows.length, 1);
  assert.equal(rows[0].dict, "mw");
  assert.equal(rows[0].pc_page, "12");
});

test("positionBin clamps to [0, bins)", () => {
  assert.equal(positionBin(0, 100, 40), 0);
  assert.equal(positionBin(100, 100, 40), 39); // last page stays in range
  assert.equal(positionBin(50, 100, 40), 20);
  assert.equal(positionBin(NaN, 100, 40), null);
  assert.equal(positionBin(10, 0, 40), null);
});

test("buildPayload aggregates per dict and per process", () => {
  const rows = [
    feedRow(),
    feedRow({ pc_page: "990", line: "99", process: "bulk", batch_date: "2026-01-05" }),
    feedRow({ pc_page: "1000", line: "100" }),
    feedRow({ dict: "stc", pc_page: "", pc_col: "", line: "5" })
  ];
  const entries = [
    { dict: "mw", entries: "1000", source: "test" },
    { dict: "stc", entries: "500", source: "test" }
  ];
  const p = buildPayload(rows, entries, { generatedAt: FIXED_AT });

  assert.equal(p.totals.records, 4);
  assert.equal(p.totals.human, 3);
  assert.equal(p.totals.bulk, 1);
  assert.equal(p.totals.pcResolved, 3);

  const mw = p.perDict.find((d) => d.dict === "mw");
  assert.equal(mw.records, 3);
  assert.equal(mw.per1k, 3);
  assert.equal(mw.per1kHuman, 2);
  assert.equal(mw.maxPage, 1000);
  assert.equal(mw.pcResolved, 3);

  const stc = p.perDict.find((d) => d.dict === "stc");
  assert.equal(stc.pcResolved, 0);
  assert.equal(stc.maxPage, null);

  // Below HEATMAP_MIN_LOCI, nothing qualifies for the heatmap.
  assert.deepEqual(p.heatmapDicts, []);
  assert.deepEqual(p.heatmapCells, []);

  // Top pages carry a sample line for the source viewer deep link.
  const top = p.topPages.find((t) => t.dict === "mw" && t.page === 10);
  assert.equal(top.sampleLine, 1358);
  assert.equal(top.human, 1);

  // Monthly rows split by process.
  assert.deepEqual(
    p.monthly.map((m) => `${m.month}|${m.process}|${m.count}`),
    ["2024-06|human|3", "2026-01|bulk|1"]
  );
});

test("buildPayload heatmap bins sum to pc-resolved count", () => {
  const rows = [];
  for (let i = 0; i < 60; i++) {
    rows.push(feedRow({ pc_page: String(1 + i * 5), line: String(100 + i), process: i % 3 === 0 ? "bulk" : "human" }));
  }
  const p = buildPayload(rows, [{ dict: "mw", entries: "1000" }], { generatedAt: FIXED_AT });
  assert.deepEqual(p.heatmapDicts, ["mw"]);
  const sum = p.heatmapCells.reduce((a, c) => a + c.count, 0);
  assert.equal(sum, 60);
  for (const c of p.heatmapCells) {
    assert.ok(c.bin >= 0 && c.bin < p.positionBins);
    assert.ok(c.process === "human" || c.process === "bulk");
  }
  // Regular column notation (1/2/3-style) gets column detail.
  assert.deepEqual(p.columnDicts, ["mw"]);
  const colSum = p.columnCells.reduce((a, c) => a + c.count, 0);
  assert.equal(colSum, 60);
});

test("committed packet is internally consistent", () => {
  const file = path.resolve(process.cwd(), "src", "data", "corrections", "correction_loci.json");
  assert.ok(fs.existsSync(file), "committed correction_loci.json missing");
  const packet = JSON.parse(fs.readFileSync(file, "utf8"));
  assert.equal(packet.schemaVersion, "1.0.0");
  const sum = packet.perDict.reduce((a, d) => a + d.records, 0);
  assert.equal(sum, packet.totals.records);
  for (const d of packet.perDict) assert.equal(d.human + d.bulk, d.records);
  assert.ok(packet.heatmapCells.length > 0);
  assert.ok(packet.limitations.length >= 3);
});
