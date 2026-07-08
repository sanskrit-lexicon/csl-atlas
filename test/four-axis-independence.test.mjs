import test from "node:test";
import assert from "node:assert/strict";
import {
  buildPayload,
  cosineOfCounts,
  exactPermutationP,
  pearson,
  spearman,
  APPARATUS_CODE,
  GRAPH_CODE,
  parseGraphEdges,
} from "../scripts/build-four-axis-independence.mjs";

test("cosineOfCounts normalises by each dict's own total", () => {
  // Same canon shape at different apparatus sizes → cosine 1.
  assert.ok(Math.abs(cosineOfCounts({ a: 10, b: 20 }, { a: 1, b: 2 }) - 1) < 1e-12);
  // Disjoint canons → cosine 0.
  assert.equal(cosineOfCounts({ a: 5 }, { b: 7 }), 0);
  // Empty vector → NaN, not a silent 0.
  assert.ok(Number.isNaN(cosineOfCounts({}, { a: 1 })));
});

test("exactPermutationP enumerates all n! permutations and is exact on perfect correlation", () => {
  const xs = [1, 2, 3, 4, 5];
  const perfect = exactPermutationP(xs, [2, 4, 6, 8, 10]);
  assert.equal(perfect.nPermutations, 120);
  // Only the identity and the full reversal reach |r|=1 → p = 2/120.
  assert.ok(Math.abs(perfect.p - 2 / 120) < 1e-12);
  assert.throws(() => exactPermutationP(new Array(9).fill(0), new Array(9).fill(0)));
});

test("pearson and spearman behave on known inputs", () => {
  assert.ok(Math.abs(pearson([1, 2, 3], [10, 20, 30]) - 1) < 1e-12);
  assert.ok(Math.abs(spearman([1, 2, 3], [1, 4, 9]) - 1) < 1e-12); // monotone → rank-perfect
  assert.ok(Number.isNaN(pearson([1, 1, 1], [1, 2, 3]))); // zero variance → NaN
});

test("parseGraphEdges builds per-dict count maps", () => {
  const vecs = parseGraphEdges("dict\tcanonical_text\tcount\nap\tX\t3\nap\tY\t2\nmw\tX\t7\n");
  assert.deepEqual(vecs.ap, { X: 3, Y: 2 });
  assert.deepEqual(vecs.mw, { X: 7 });
});

function fixtureRow(parent, child, content, convention, micro) {
  return {
    rowId: `three-axis:${parent}:${child}`,
    parent,
    child,
    tier: "A",
    contentAxis: { parentInChild: content },
    conventionAxis: { conventionSimilarity: convention },
    microstructureAxis: { microstructureSimilarity01: micro },
  };
}

const FIXTURE_COMPARISON = {
  generatedAt: "2026-01-01T00:00:00.000Z",
  comparisonRows: [
    fixtureRow("PWG", "PW", 0.9, 0.7, 0.6),
    fixtureRow("AP90", "AP", 0.8, 0.6, 0.9),
    fixtureRow("PWG", "MW", 0.85, 0.4, 0.7),
    fixtureRow("PWG", "SCH", 0.1, 0.65, 0.2),
    fixtureRow("BEN", "MW", 0.9, 0.5, 0.68),
    fixtureRow("WIL", "YAT", 0.5, 0.5, 0.5), // no adapter → excluded
  ],
};

const FIXTURE_APPARATUS = {
  sourceMatrix: [
    { source: "T1", byDict: { PWG: 10, PWK: 8, MW: 5, AP90: 2, AP: 2, SCH: 1, BEN: 4 } },
    { source: "T2", byDict: { PWG: 5, PWK: 4, MW: 9, AP90: 6, AP: 5, SCH: 0, BEN: 1 } },
    { source: "T3", byDict: { PWG: 1, PWK: 0, MW: 2, AP90: 7, AP: 8, SCH: 3, BEN: 0 } },
  ],
};

const FIXTURE_GRAPH = "dict\tcanonical_text\tcount\npwg\tT1\t10\npw\tT1\t8\nmw\tT2\t9\nap90\tT3\t7\nap\tT3\t8\nsch\tT3\t3\nben\tT1\t4\n";

test("buildPayload: edge accounting, exact permutation, matrix symmetry", () => {
  const payload = buildPayload(FIXTURE_COMPARISON, FIXTURE_APPARATUS, FIXTURE_GRAPH, "2026-01-02T00:00:00.000Z");
  assert.equal(payload.n, 5);
  assert.equal(payload.edgeShrinkage.excludedEdges.length, 1);
  assert.equal(payload.edgeShrinkage.excludedEdges[0].parent, "WIL");
  assert.equal(payload.n + payload.edgeShrinkage.excludedEdges.length, payload.nDocumentedEdges);
  for (const c of payload.citationCorrelations) {
    assert.equal(c.nPermutations, 120);
    assert.ok(c.permutationP >= 0 && c.permutationP <= 1);
  }
  // 4x4 matrix: 16 cells, unit diagonal, symmetric.
  assert.equal(payload.correlationMatrix.length, 16);
  const at = (a, b) => payload.correlationMatrix.find((m) => m.a === a && m.b === b);
  for (const ax of ["content", "convention", "microstructure", "citation"]) {
    assert.equal(at(ax, ax).pearson, 1);
  }
  assert.equal(at("citation", "content").pearson, at("content", "citation").pearson);
  // Cosines within [0,1]; deterministic given pinned generatedAt.
  for (const e of payload.edges) assert.ok(e.citationAxis >= 0 && e.citationAxis <= 1);
  const again = buildPayload(FIXTURE_COMPARISON, FIXTURE_APPARATUS, FIXTURE_GRAPH, "2026-01-02T00:00:00.000Z");
  assert.deepEqual(again, payload);
});

test("dict-code maps cover exactly the adapter-validated three-axis dictionaries", () => {
  assert.deepEqual(Object.keys(APPARATUS_CODE).sort(), ["AP", "AP90", "BEN", "MW", "PW", "PWG", "SCH"]);
  assert.deepEqual(Object.keys(GRAPH_CODE).sort(), Object.keys(APPARATUS_CODE).sort());
  assert.equal(APPARATUS_CODE.PW, "PWK"); // the apparatus labels the pw adapter PWK
});
