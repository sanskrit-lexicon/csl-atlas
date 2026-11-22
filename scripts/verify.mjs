/** Production acceptance command used locally and by GitHub Actions. */
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { performance } from "node:perf_hooks";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const VALIDATORS = [
  "validate-mw-depth.mjs",
  "validate-dictionary-comparison.mjs",
  "validate-citation-canon.mjs",
  "validate-tradition-tags.mjs",
  "validate-correction-feed.mjs",
  "validate-heritage-witness.mjs",
  "validate-ghost-stock.mjs",
  "validate-plan-deviation.mjs",
  "validate-kosa-chapters.mjs",
  "validate-heap-sat.mjs",
  "validate-period-signatures.mjs",
  "validate-four-axis-independence.mjs",
  "validate-l0-gqd.mjs",
  // ADR-0001 (MG 21-11-2026): census badges stay tiered — every Patel witness
  // classified (authority tier + origin), Grundlagen in Tier A, flat badge banned.
  "validate-dict-authority-tiers.mjs",
  "validate-learner-index.mjs",
  "validate-review-reports.mjs",
  // H7101: the candidate-lane provenance contract (machine-candidate only,
  // no reviewed status, every row validated against the committed schema).
  "validate-llm-candidate-lane.mjs"
];

const HELP = `Usage: npm run verify -- [options]

Options:
  --fast       Skip the second determinism regeneration and npm audit.
               Tests, validators, one regeneration, build, and clean-tree
               checks still run. Use the default full mode before release.
  --jobs N     Run up to N independent checks concurrently (default: 1).
               Regeneration, build, and audit remain sequential.
  -h, --help   Show this help.

Each step reports elapsed time. Peak child RSS is sampled on Linux via /proc;
other platforms report n/a. Output from parallel checks is printed per completed
step to avoid interleaving.`;

export function parseVerifyArgs(args) {
  const options = { fast: false, jobs: 1, help: false };
  for (let index = 0; index < args.length; index++) {
    const arg = args[index];
    if (arg === "--fast") {
      options.fast = true;
    } else if (arg === "--help" || arg === "-h") {
      options.help = true;
    } else if (arg === "--jobs" || arg.startsWith("--jobs=")) {
      const value = arg === "--jobs" ? args[++index] : arg.slice("--jobs=".length);
      if (!value || !/^[1-9]\d*$/.test(value)) {
        throw new Error("--jobs requires a positive integer.");
      }
      options.jobs = Number(value);
      if (!Number.isSafeInteger(options.jobs)) throw new Error("--jobs is too large.");
    } else {
      throw new Error(`Unknown verify option: ${arg}. Use --help for usage.`);
    }
  }
  return options;
}

function task(label, command, args) {
  return { label, command, args };
}

function nodeTask(label, args) {
  return task(label, process.execPath, args);
}

function pythonTask(label, args) {
  return task(label, "python", args);
}

function commandFor(task) {
  // On Windows, spawn cannot directly execute npm.cmd (EINVAL). npm exposes its
  // CLI script to lifecycle commands, so run it with Node rather than a shell.
  if (task.command === "npm" && process.env.npm_execpath) {
    return { executable: process.execPath, args: [process.env.npm_execpath, ...task.args] };
  }
  return { executable: task.command, args: task.args };
}

function readLinuxPeakRss(pid) {
  try {
    const status = fs.readFileSync(`/proc/${pid}/status`, "utf8");
    const match = status.match(/^VmHWM:\s+(\d+)\s+kB$/m);
    return match ? Number(match[1]) * 1024 : null;
  } catch {
    return null;
  }
}

function monitorPeakRss(pid) {
  if (process.platform !== "linux" || !pid) return { stop() {}, peak: () => null };
  let maximum = readLinuxPeakRss(pid);
  const timer = setInterval(() => {
    const current = readLinuxPeakRss(pid);
    if (current !== null) maximum = Math.max(maximum ?? 0, current);
  }, 100);
  timer.unref();
  return {
    stop() { clearInterval(timer); },
    peak: () => maximum
  };
}

async function executeTask(task) {
  const { executable, args } = commandFor(task);
  const child = spawn(executable, args, {
    cwd: ROOT,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true
  });
  child.stdout.setEncoding("utf8");
  child.stderr.setEncoding("utf8");
  let stdout = "";
  let stderr = "";
  child.stdout.on("data", chunk => { stdout += chunk; });
  child.stderr.on("data", chunk => { stderr += chunk; });
  const memory = monitorPeakRss(child.pid);
  const outcome = await new Promise(resolve => {
    child.once("error", error => resolve({ error }));
    child.once("close", (status, signal) => resolve({ status, signal }));
  });
  memory.stop();
  if (stdout) process.stdout.write(stdout);
  if (stderr) process.stderr.write(stderr);
  if (outcome.error) throw new Error(`${task.label}: ${outcome.error.message}`);
  if (outcome.status !== 0) {
    const detail = outcome.signal ? `signal ${outcome.signal}` : `exit code ${outcome.status}`;
    throw new Error(`${task.label} failed with ${detail}.`);
  }
  return { peakRss: memory.peak() };
}

function assertClean(label) {
  const result = spawnSync("git", ["diff", "--quiet", "--exit-code"], { cwd: ROOT, encoding: "utf8" });
  const staged = spawnSync("git", ["diff", "--cached", "--quiet", "--exit-code"], { cwd: ROOT, encoding: "utf8" });
  if (result.status !== 0 || staged.status !== 0) throw new Error(`${label}: tracked files are not clean.`);
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return "n/a";
  const units = ["B", "KiB", "MiB", "GiB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit++;
  }
  return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}

export async function runTasks(tasks, { jobs = 1, execute = executeTask, onComplete = () => {} } = {}) {
  let cursor = 0;
  let firstError = null;
  async function worker() {
    while (!firstError) {
      const index = cursor++;
      if (index >= tasks.length) return;
      const current = tasks[index];
      const started = performance.now();
      try {
        const result = await execute(current);
        await onComplete(current, { ...result, durationMs: performance.now() - started });
      } catch (error) {
        firstError = error;
      }
    }
  }
  const workers = Array.from({ length: Math.min(jobs, tasks.length) }, () => worker());
  await Promise.all(workers);
  if (firstError) throw firstError;
}

function verificationTasks() {
  const checks = [
    pythonTask("review-decision tests", ["-m", "unittest", "scripts.test_validate_review_decisions"]),
    pythonTask("review-pool merge tests", ["-m", "unittest", "scripts.test_merge_review_pool_decisions"]),
    pythonTask("review-pool kappa tests", ["-m", "unittest", "scripts.lexico.test_lexico_review_pool_kappa"]),
    // H7096: the PD generators' --check parity gates. A hand edit to a
    // generated data/pd file (the #598 failure mode) must go RED here, not
    // sit unnoticed until someone runs the gate by hand.
    pythonTask("PD regeneration gates", [path.join("scripts", "pd_regen_gate.py")]),
    // H5303 (G6): every data JSON envelope must carry its matrix licence.
    pythonTask("dataset licence validation", [path.join("scripts", "validate_dataset_licences.py")]),
    ...VALIDATORS.map(validator => nodeTask(validator, [path.join("scripts", validator)]))
  ];
  return {
    nodeTests: nodeTask("node tests", ["--test"]),
    checks,
    regenerate: nodeTask("review-artifact regeneration", [path.join("scripts", "regen-review-artifacts.mjs")]),
    build: task("site build", "npm", ["run", "build"]),
    // --omit=dev: the deployed artifact is static HTML; the whole toolchain is
    // devDependencies, and docs/DEPENDENCY_SECURITY.md already scopes dev-only
    // advisories as non-blocking (they cannot ship). Production deps stay gated.
    audit: task("production dependency audit", "npm", ["audit", "--omit=dev", "--audit-level=high"])
  };
}

export async function verify(options = {}, dependencies = {}) {
  const { fast = false, jobs = 1 } = options;
  const execute = dependencies.execute ?? executeTask;
  const clean = dependencies.assertClean ?? assertClean;
  const log = dependencies.log ?? console.log;
  const tasks = verificationTasks();
  const started = performance.now();
  let maximumRss = null;

  const onComplete = (current, result) => {
    if (Number.isFinite(result.peakRss)) maximumRss = Math.max(maximumRss ?? 0, result.peakRss);
    log(`[verify] ${current.label}: ${(result.durationMs / 1000).toFixed(2)}s; peak RSS ${formatBytes(result.peakRss)}`);
  };
  const runGroup = group => runTasks(group, { jobs, execute, onComplete });
  const runOne = current => runTasks([current], { jobs: 1, execute, onComplete });

  clean("before verification");
  // Some Node tests temporarily replace repository files and restore them in
  // finally blocks. Keep this suite isolated from validators that read the
  // same artifacts; the remaining read-only checks can safely run in parallel.
  await runOne(tasks.nodeTests);
  await runGroup(tasks.checks);
  await runOne(tasks.regenerate);
  if (!fast) await runOne(tasks.regenerate);
  clean("after deterministic regeneration");
  await runOne(tasks.build);
  if (!fast) await runOne(tasks.audit);
  clean("after build and audit");

  const elapsed = ((performance.now() - started) / 1000).toFixed(2);
  const mode = fast ? "fast verification" : "full verification";
  log(`verify: ${mode} passed in ${elapsed}s; max step RSS ${formatBytes(maximumRss)}.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const options = parseVerifyArgs(process.argv.slice(2));
    if (options.help) console.log(HELP);
    else await verify(options);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}
