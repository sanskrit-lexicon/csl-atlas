import test from "node:test";
import assert from "node:assert/strict";
import { vedawebId, parseLocus, inRange, loadVerseCounts } from "../scripts/build-citation-link-pilot.mjs";
import { deriveVerseCounts } from "../scripts/import-rv-verse-counts.mjs";

test("vedawebId zero-pads to the MMHHHVV stanza id", () => {
  assert.equal(vedawebId(5, 86, 5), "0508605");   // the pilot's worked example
  assert.equal(vedawebId(1, 1, 1), "0100101");
  assert.equal(vedawebId(10, 191, 4), "1019104"); // the last RV stanza
});

test("parseLocus classifies the RV citation shapes", () => {
  assert.deepEqual(parseLocus("v, 86, 5"), { kind: "verse", mandala: 5, hymn: 86, verse: 5 });
  assert.equal(parseLocus("").kind, "work-level");            // bare "RV."
  assert.deepEqual(parseLocus("v, 86"), { kind: "hymn-level", mandala: 5, hymn: 86 });
  assert.deepEqual(parseLocus("v"), { kind: "mandala-only", mandala: 5 });
  assert.equal(parseLocus("i, 1, 64, 6").kind, "ambiguous");  // malformed 4-part
  assert.equal(parseLocus("v, 86, 5; vi, 1").kind, "multi");  // combined -> link-splitting
  assert.equal(parseLocus("z, 1, 1").kind, "unparseable");    // not a roman maṇḍala
});

test("inRange validates the verse exactly when the per-hymn table is present", () => {
  // Synthetic table: maṇḍala 1, hymn 1 has 9 stanzas; hymn 2 is unknown to the table.
  const table = { versesPerHymn: { 1: [9] } };
  assert.ok(inRange(1, 1, 9, table), "verse 9 is the last stanza of 1.1");
  assert.ok(!inRange(1, 1, 10, table), "verse 10 exceeds 1.1's 9 stanzas");
  assert.ok(!inRange(1, 1, 0, table), "verse 0 is invalid");
  // Hymn not in the table -> fall back to the global cap, not a hard reject.
  assert.ok(inRange(1, 2, 5, table));
});

test("inRange falls back to the global cap when no table is supplied", () => {
  assert.ok(inRange(1, 1, 58, null), "≤58 passes under the cap");
  assert.ok(!inRange(1, 1, 59, null), "59 exceeds the global cap");
  assert.ok(!inRange(99, 1, 1, null), "unknown maṇḍala is always rejected");
  assert.ok(!inRange(2, 44, 1, null), "hymn beyond the maṇḍala is rejected");
});

test("deriveVerseCounts reduces the DOTS column to per-hymn stanza counts", () => {
  const tsv = ["DOTS\tBOOK_INDEX", "1.1.1\t0", "1.1.2\t0", "1.2.1\t0", "2.1.1\t0"].join("\n");
  const { versesPerHymn, hymnsPerMandala, totalStanzas } = deriveVerseCounts(tsv);
  assert.deepEqual(versesPerHymn, { 1: [2, 1], 2: [1] });
  assert.deepEqual(hymnsPerMandala, { 1: 2, 2: 1 });
  assert.equal(totalStanzas, 4);
});

test("deriveVerseCounts flags a gap in a maṇḍala's hymn sequence", () => {
  const tsv = ["DOTS", "1.1.1", "1.3.1"].join("\n"); // hymn 2 missing
  assert.throws(() => deriveVerseCounts(tsv), /Gap in maṇḍala 1/);
});

test("loadVerseCounts returns null for an absent snapshot", () => {
  assert.equal(loadVerseCounts("does/not/exist.json"), null);
});

test("the committed RV stanza snapshot loads and matches the known RV shape", () => {
  const data = loadVerseCounts(); // default path = src/data/external/rv-verse-counts.json
  assert.ok(data, "snapshot is committed");
  assert.equal(data.totalHymns, 1028);
  assert.equal(data.totalStanzas, 10552);
  assert.equal(data.versesPerHymn["1"][0], 9);     // RV 1.1 has 9 stanzas
  assert.equal(data.versesPerHymn["5"][85], 6);    // RV 5.86 has 6 stanzas (the worked example)
});
