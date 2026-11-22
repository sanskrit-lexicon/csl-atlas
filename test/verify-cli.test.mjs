import { test } from "node:test";
import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";

import { parseVerifyArgs, runTasks, verify } from "../scripts/verify.mjs";

test("verify CLI defaults to the original strict sequential mode", () => {
  assert.deepEqual(parseVerifyArgs([]), { fast: false, jobs: 1, help: false });
  assert.deepEqual(parseVerifyArgs(["--fast", "--jobs", "4"]), { fast: true, jobs: 4, help: false });
  assert.deepEqual(parseVerifyArgs(["--jobs=3"]), { fast: false, jobs: 3, help: false });
  assert.deepEqual(parseVerifyArgs(["--help"]), { fast: false, jobs: 1, help: true });
  assert.deepEqual(parseVerifyArgs(["-h"]), { fast: false, jobs: 1, help: true });
});

test("verify CLI rejects missing, invalid, and unknown options", () => {
  for (const args of [["--jobs"], ["--jobs", "0"], ["--jobs", "1.5"], ["--jobs=-2"], ["--jobs", "abc"]]) {
    assert.throws(() => parseVerifyArgs(args), /--jobs requires a positive integer/);
  }
  assert.throws(() => parseVerifyArgs(["--unknown"]), /Unknown verify option/);
});

test("runTasks respects the concurrency limit and reports elapsed time", async () => {
  let active = 0;
  let maximumActive = 0;
  const completed = [];
  const tasks = ["a", "b", "c", "d"].map(label => ({ label }));
  await runTasks(tasks, {
    jobs: 2,
    execute: async current => {
      active++;
      maximumActive = Math.max(maximumActive, active);
      await delay(10);
      active--;
      return { peakRss: null };
    },
    onComplete: (current, result) => {
      completed.push(current.label);
      assert.ok(result.durationMs >= 0);
    }
  });
  assert.equal(maximumActive, 2);
  assert.equal(completed.length, tasks.length);
});

test("runTasks stops dispatch after failure and waits for active work", async () => {
  const started = [];
  let slowTaskFinished = false;
  const tasks = ["fail", "slow", "not-started"].map(label => ({ label }));
  await assert.rejects(runTasks(tasks, {
    jobs: 2,
    execute: async current => {
      started.push(current.label);
      if (current.label === "fail") {
        await delay(5);
        throw new Error("synthetic failure");
      }
      await delay(15);
      slowTaskFinished = true;
      return { peakRss: null };
    }
  }), /synthetic failure/);
  assert.deepEqual(started.sort(), ["fail", "slow"]);
  assert.equal(slowTaskFinished, true);
});

test("fast verify keeps correctness gates but skips the second regeneration and audit", async () => {
  const executed = [];
  const cleanChecks = [];
  const logs = [];
  await verify({ fast: true, jobs: 4 }, {
    execute: async current => {
      executed.push(current.label);
      return { peakRss: 1024 };
    },
    assertClean: label => cleanChecks.push(label),
    log: message => logs.push(message)
  });
  assert.equal(executed.filter(label => label === "review-artifact regeneration").length, 1);
  assert.equal(executed.includes("production dependency audit"), false);
  assert.ok(executed.includes("node tests"));
  assert.ok(executed.includes("site build"));
  assert.deepEqual(cleanChecks, [
    "before verification",
    "after deterministic regeneration",
    "after build and audit"
  ]);
  assert.ok(logs.some(message => /fast verification passed/.test(message)));
  assert.ok(logs.some(message => /peak RSS 1\.0 KiB/.test(message)));
});

test("full verify preserves both determinism passes and the production audit", async () => {
  const executed = [];
  await verify({}, {
    execute: async current => {
      executed.push(current.label);
      return { peakRss: null };
    },
    assertClean: () => {},
    log: () => {}
  });
  assert.equal(executed.filter(label => label === "review-artifact regeneration").length, 2);
  assert.equal(executed.filter(label => label === "production dependency audit").length, 1);
  assert.equal(executed.at(-1), "production dependency audit");
});
