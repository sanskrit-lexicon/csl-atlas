import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { parseTsv, buildPayload } from "../scripts/build-heritage-witness.mjs";

const FIXED_AT = "2026-07-08T00:00:00.000Z";

function mwRecord(overrides = {}) {
  return { L: "1.1", k1: "akAra", startLine: 10, href: "https://example.test/mw#L10", ...overrides };
}

function crosswalkRow(overrides = {}) {
  return { mw_key1: "akAra", covered_flag: "1", heritage_entry_anchor: "DICO/1.html#akaara", ...overrides };
}

test("parseTsv maps header to fields", () => {
  const rows = parseTsv("mw_key1\tcovered_flag\theritage_entry_anchor\nakAra\t1\tDICO/1.html#akaara\n");
  assert.equal(rows.length, 1);
  assert.equal(rows[0].mw_key1, "akAra");
  assert.equal(rows[0].covered_flag, "1");
});

test("buildPayload classifies anchored, covered-no-anchor, and absent", () => {
  const mwRecords = [
    mwRecord({ k1: "akAra", startLine: 10 }),
    mwRecord({ k1: "aMSa", startLine: 20 }),
    mwRecord({ k1: "afRin", startLine: 30 }),
    mwRecord({ k1: "a", startLine: 5 }) // uncovered, no crosswalk row at all
  ];
  const crosswalkRows = [
    crosswalkRow({ mw_key1: "akAra", covered_flag: "1", heritage_entry_anchor: "DICO/1.html#akaara" }),
    crosswalkRow({ mw_key1: "aMSa", covered_flag: "1", heritage_entry_anchor: "" }),
    crosswalkRow({ mw_key1: "afRin", covered_flag: "0", heritage_entry_anchor: "" })
  ];
  const p = buildPayload(mwRecords, crosswalkRows, { generatedAt: FIXED_AT });

  assert.equal(p.totals.mwEntries, 4);
  assert.equal(p.totals.anchored, 1);
  assert.equal(p.totals.coveredNoAnchor, 1);
  assert.equal(p.totals.absent, 2);
  assert.equal(p.totals.heritageCovered, 2);
  assert.equal(p.totals.coveragePct, 0.5);

  const akara = p.witnessed.find((w) => w.headword === "akAra");
  assert.equal(akara.matchTier, "anchored");
  assert.equal(akara.heritageAnchor, "DICO/1.html#akaara");
  assert.equal(akara.mwLine, 10);

  const amsa = p.witnessed.find((w) => w.headword === "aMSa");
  assert.equal(amsa.matchTier, "covered-no-anchor");
  assert.equal(amsa.heritageAnchor, null);

  assert.ok(!p.witnessed.some((w) => w.headword === "afRin"));
  assert.ok(!p.witnessed.some((w) => w.headword === "a"));

  const sumMw = p.perInitial.reduce((a, r) => a + r.mwEntries, 0);
  assert.equal(sumMw, p.totals.mwEntries);
});

test("buildPayload folds homonym-digit crosswalk rows onto one normalized key, anchor wins", () => {
  // normalizeLemma strips a trailing homonym digit, so two distinct raw
  // mw_key1 rows (e.g. from MW's own homonym-indexed keys) can collapse onto
  // one normalized headword with conflicting covered_flag/anchor values.
  const mwRecords = [mwRecord({ k1: "aMSaka", startLine: 1 }), mwRecord({ k1: "aMSaka", startLine: 2 })];
  const crosswalkRows = [
    crosswalkRow({ mw_key1: "aMSaka1", covered_flag: "1", heritage_entry_anchor: "" }),
    crosswalkRow({ mw_key1: "aMSaka2", covered_flag: "1", heritage_entry_anchor: "DICO/1.html#a.mzaka#2" })
  ];
  const p = buildPayload(mwRecords, crosswalkRows, { generatedAt: FIXED_AT });

  assert.equal(p.totals.mwEntries, 1); // both MW records collapse onto one normalized headword
  const row = p.witnessed.find((w) => w.headword === "aMSaka");
  assert.equal(row.matchTier, "anchored");
  assert.equal(row.heritageAnchor, "DICO/1.html#a.mzaka#2");
  assert.equal(row.occurrences, 2);
  assert.equal(row.mwLine, 1); // first occurrence
});

test("buildPayload treats an unknown headword (absent from the crosswalk entirely) as absent", () => {
  const mwRecords = [mwRecord({ k1: "nAstika", startLine: 1 })];
  const p = buildPayload(mwRecords, [], { generatedAt: FIXED_AT });
  assert.equal(p.totals.absent, 1);
  assert.equal(p.totals.heritageCovered, 0);
});

test("committed packet is internally consistent", () => {
  const file = path.resolve(process.cwd(), "src", "data", "heritage", "heritage_witness.json");
  assert.ok(fs.existsSync(file), "committed heritage_witness.json missing");
  const packet = JSON.parse(fs.readFileSync(file, "utf8"));
  assert.equal(packet.schemaVersion, "1.0.0");
  assert.equal(packet.totals.anchored + packet.totals.coveredNoAnchor, packet.totals.heritageCovered);
  assert.equal(packet.totals.heritageCovered + packet.totals.absent, packet.totals.mwEntries);
  assert.equal(packet.witnessed.length, packet.totals.heritageCovered);
  assert.ok(packet.limitations.length >= 3);
  for (const w of packet.witnessed) {
    assert.ok(w.matchTier === "anchored" || w.matchTier === "covered-no-anchor");
    if (w.matchTier === "anchored") assert.ok(w.heritageAnchor);
    else assert.equal(w.heritageAnchor, null);
  }
});
