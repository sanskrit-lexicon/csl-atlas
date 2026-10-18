// H5408 — the exact-edge lookup must fold MW's raw accented / hyphen-prefixed targets the
// way m6_xref_lineage.py does, or accented MW cf. targets read as "exact edge missing in MW".
import test from "node:test";
import assert from "node:assert/strict";
import { normalizeXrefKey } from "../scripts/lib/xref-normalize.mjs";
import { indexExactEdges, sourceEdgesForSharedSample } from "../scripts/build-xref-source-check-packet.mjs";

test("normalizeXrefKey mirrors m6_xref_lineage.py normalize()", () => {
  const cases = [
    ["a/nAkzit", "anAkzit"],      // udātta inside the target (MW L22386)
    ["Are/", "Are"],              // trailing udātta (MW L26162)
    ["Basa/d", "Basad"],          // udātta inside (MW L147529)
    ["-DArmyAyaRa", "DArmyAyaRa"], // hyphen-prefixed compound member (MW L100511)
    ["a\\-", "a"],                // anudātta + trailing compound hyphen
    ["mahA°", "mahA"],            // PWG compound-family ring
    ["aBi-", "aBi"],              // MW trailing prefix hyphen
    ["  gam  ", "gam"],
    ["a  b", "a b"],
    ["", ""],
    [undefined, ""]
  ];
  for (const [raw, expected] of cases) assert.equal(normalizeXrefKey(raw), expected, `normalize(${raw})`);
});

test("exact-edge lookup matches MW edges whose raw target carries an accent or a hyphen", () => {
  const samples = [
    ["mw-pwg-shared:03", "Akzit", "anAkzit", "a/nAkzit", "22386", "7882"],
    ["mw-pwg-shared:07", "ArAt", "Are", "Are/", "26162", "9148"],
    ["mw-pwg-shared:16", "BaMsas", "Basad", "Basa/d", "147529", "53690"],
    ["mw-pwg-shared:36", "Darmya", "DArmyAyaRa", "-DArmyAyaRa", "100511", "36453"]
  ];
  const edgeRows = samples.flatMap(([, k1, pwgTarget, mwRawTarget, mwL, pwgL]) => [
    { dict: "mw", L: mwL, k1, kind: "cf", target: mwRawTarget },
    { dict: "pwg", L: pwgL, k1, kind: "vgl", target: pwgTarget },
    // a neighbouring MW edge with a different target must NOT be pulled in by the fold
    { dict: "mw", L: `${mwL}.x`, k1, kind: "cf", target: `${mwRawTarget}Ya` }
  ]);
  const index = indexExactEdges(edgeRows);
  for (const [sampleId, sourceLemma, target, mwRawTarget, mwL, pwgL] of samples) {
    const hits = sourceEdgesForSharedSample({ sourceLemma, target }, index);
    assert.deepEqual(hits.map(e => e.dict).sort(), ["mw", "pwg"], `${sampleId}: both dictionaries match`);
    assert.deepEqual(hits.map(e => e.L).sort(), [mwL, pwgL].sort(), `${sampleId}: exactly the two source records`);
    const mw = hits.find(e => e.dict === "mw");
    assert.equal(mw.target, mwRawTarget, `${sampleId}: the MW pointer keeps the RAW target`);
  }
});
