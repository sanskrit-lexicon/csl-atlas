// H2892 — the --reseed lock over the human review overlay.
//
// Run with: npm test  (node --test, no external dependency)
//
// Two directions are tested, and both matter:
//
//   * --reseed without ALLOW_OVERLAY_WIPE=1 exits 2 and writes nothing;
//   * the plain overlay-preserving rebuild still works and still preserves
//     every human decision.
//
// The second is the one a lock like this usually breaks. A guard that refuses
// everything is not a fix — it just moves the damage from the data to the
// pipeline.
//
// The end-to-end cases run the real generator in a temporary tree copied from
// the repo, never against src/data/review/ itself. The one case that runs in
// the checkout is the refusal, which by definition writes nothing — and the
// test hashes the committed report before and after to prove it.

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  OVERLAY_WIPE_HATCH,
  RESEED_DANGER_SENTENCE,
  RESEED_REFUSAL_EXIT,
  refuseReseedWithoutHatch,
  reseedIsHatched,
  reseedRefusalMessage
} from "../scripts/lib/review-report.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const GENERATOR = path.join("scripts", "build-r2-checkpoint-review.mjs");
const REPORT = path.join("src", "data", "review", "r2-checkpoint-review.json");
const PACKET = path.join("data", "lexico", "r2_checkpoint_review_packet.json");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function envWithoutHatch(extra = {}) {
  const env = { ...process.env, ...extra };
  delete env[OVERLAY_WIPE_HATCH];
  return env;
}

/** A minimal tree holding just the generator's input, output and libraries. */
function stagingTree() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "csl-atlas-reseed-"));
  for (const rel of [PACKET, REPORT]) {
    const target = path.join(root, rel);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(repoRoot, rel), target);
  }
  fs.cpSync(path.join(repoRoot, "scripts"), path.join(root, "scripts"), { recursive: true });
  return root;
}

function humanRulings(reportPath) {
  const doc = JSON.parse(fs.readFileSync(reportPath, "utf8"));
  return doc.items
    .filter(item => item.reviewer || ["reviewed-ok", "reviewed-corrected", "blocked", "deferred"].includes(item.reviewStatus))
    .map(item => `${item.reviewId}|${item.reviewStatus}|${item.reviewer}|${item.reviewedValue}|${item.note}`)
    .sort();
}

test("the hatch is exact — only the string \"1\" is consent", () => {
  for (const value of ["", "0", "true", "TRUE", "yes", "2", " 1"]) {
    assert.equal(reseedIsHatched({ [OVERLAY_WIPE_HATCH]: value }), false, `${JSON.stringify(value)} must not consent`);
  }
  assert.equal(reseedIsHatched({ [OVERLAY_WIPE_HATCH]: "1" }), true);
  assert.equal(reseedIsHatched({}), false);
});

test("refuseReseedWithoutHatch refuses with exit 2 and says why", () => {
  const exits = [];
  const logs = [];
  const refused = refuseReseedWithoutHatch({
    script: GENERATOR,
    outputPath: path.join(repoRoot, REPORT),
    env: {},
    exit: code => exits.push(code),
    log: message => logs.push(message)
  });
  assert.equal(refused, true);
  assert.deepEqual(exits, [RESEED_REFUSAL_EXIT]);
  // Literal substring match: the refusal must carry the danger sentence
  // verbatim. (Building a RegExp from the sentence with partial escaping trips
  // CodeQL js/incomplete-sanitization; includes() needs no escaping at all.)
  assert.ok(logs.join("\n").includes(RESEED_DANGER_SENTENCE));
});

test("refuseReseedWithoutHatch lets a hatched run through untouched", () => {
  let exited = false;
  const refused = refuseReseedWithoutHatch({
    script: GENERATOR,
    env: { [OVERLAY_WIPE_HATCH]: "1" },
    exit: () => { exited = true; },
    log: () => {}
  });
  assert.equal(refused, false);
  assert.equal(exited, false);
});

test("the refusal names the plain rebuild as the way forward", () => {
  const message = reseedRefusalMessage({ script: GENERATOR, outputPath: path.join(repoRoot, REPORT) });
  assert.match(message, /Nothing was written/);
  assert.match(message, /A plain rebuild is always allowed/);
  assert.match(message, new RegExp(`${OVERLAY_WIPE_HATCH}=1`));
});

test("--reseed without the hatch exits 2 and does not touch the committed report", () => {
  const report = path.join(repoRoot, REPORT);
  const before = sha256(report);
  const run = spawnSync(process.execPath, [GENERATOR, "--reseed"], {
    cwd: repoRoot,
    env: envWithoutHatch(),
    encoding: "utf8"
  });
  assert.equal(run.status, RESEED_REFUSAL_EXIT, `stdout: ${run.stdout}\nstderr: ${run.stderr}`);
  assert.match(run.stderr, /REFUSED/);
  assert.equal(sha256(report), before, "--reseed CHANGED the report while refusing");
});

test("the overlay-preserving rebuild still runs and still preserves every human ruling", () => {
  const root = stagingTree();
  try {
    const report = path.join(root, REPORT);
    const expected = humanRulings(report);
    assert.ok(expected.length > 0, "fixture must carry at least one human ruling");

    execFileSync(process.execPath, [GENERATOR], { cwd: root, env: envWithoutHatch(), encoding: "utf8" });

    assert.deepEqual(humanRulings(report), expected,
      "a plain rebuild must carry every human decision forward verbatim");
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("a hatched --reseed does blank the overlay — the lock gates it, nothing else", () => {
  const root = stagingTree();
  try {
    const report = path.join(root, REPORT);
    assert.ok(humanRulings(report).length > 0);

    execFileSync(process.execPath, [GENERATOR, "--reseed"], {
      cwd: root,
      env: { ...process.env, [OVERLAY_WIPE_HATCH]: "1" },
      encoding: "utf8"
    });

    assert.deepEqual(humanRulings(report), [],
      "with the hatch set the reseed must still do what it says on the tin");
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
