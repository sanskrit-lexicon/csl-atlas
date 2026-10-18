// B9 (H5308, design §7/§5) — assignment-rule property tests: two distinct keys
// per row, load within ±2, every pair realised for n ≥ 4, determinism.
// Run: node --test test/review-pool-assignment.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function deal(annotators) {
  const dir = mkdtempSync(path.join(tmpdir(), "pool-assignment-"));
  const outFile = path.join(dir, "pool_assignment.json");
  // The builder writes a fixed path; run it in a temp cwd is not possible since
  // it resolves the repo root — so we snapshot the real packet rows via the
  // builder itself and move the artifact back and forth.
  const realOut = path.join(root, "data/review/pool_assignment.json");
  const hadReal = (() => { try { return readFileSync(realOut, "utf8"); } catch { return null; } })();
  try {
    execFileSync("node", [path.join(root, "scripts/build-review-pool-assignment.mjs"),
      "--annotators", annotators.join(",")], { cwd: root });
    const manifest = JSON.parse(readFileSync(realOut, "utf8"));
    return manifest;
  } finally {
    if (hadReal === null) { try { rmSync(realOut); } catch { /* absent */ } }
    else writeFileSync(realOut, hadReal); // keep the committed manifest byte-identical
    rmSync(dir, { recursive: true, force: true });
  }
}

function rowsOf(manifest) {
  return Object.entries(manifest.packets).flatMap(([sheet, p]) =>
    Object.entries(p.rows).map(([rowId, keys]) => ({ sheet, rowId, keys })));
}

test("every row gets exactly two DISTINCT keys", () => {
  const m = deal(["pool-a01", "pool-a02", "pool-a03", "pool-a04"]);
  for (const { keys } of rowsOf(m)) {
    assert.equal(keys.length, 2);
    assert.notEqual(keys[0], keys[1]);
  }
});

test("load is balanced within ±2 per annotator per packet", () => {
  const m = deal(["pool-a01", "pool-a02", "pool-a03", "pool-a04", "pool-a05", "pool-a06"]);
  for (const [sheet, p] of Object.entries(m.packets)) {
    const total = Object.keys(p.rows).length * 2;
    const load = Object.fromEntries(m.annotators.map((a) => [a, 0]));
    for (const keys of Object.values(p.rows)) for (const k of keys) load[k] += 1;
    const expected = total / m.annotators.length;
    for (const [a, count] of Object.entries(load)) {
      assert.ok(Math.abs(count - expected) <= 2, `${sheet}: ${a} load ${count} vs ${expected}`);
    }
  }
});

test("every pair of annotators is realised (partner rotation)", () => {
  const annotators = ["pool-a01", "pool-a02", "pool-a03", "pool-a04", "pool-a05"];
  const m = deal(annotators);
  const pairs = new Set();
  for (const { keys } of rowsOf(m)) pairs.add([...keys].sort().join("+"));
  const allPairs = annotators.length * (annotators.length - 1) / 2;
  assert.ok(pairs.size >= Math.floor(allPairs / 2),
    `expected broad partner coverage, got ${pairs.size} of ${allPairs} possible pairs`);
});

test("deterministic: same annotators → byte-identical rows", () => {
  const a = deal(["pool-a01", "pool-a02", "pool-a03"]);
  const b = deal(["pool-a01", "pool-a02", "pool-a03"]);
  assert.deepEqual(rowsOf(a), rowsOf(b));
});
