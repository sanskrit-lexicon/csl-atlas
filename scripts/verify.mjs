/** Production acceptance command used locally and by GitHub Actions. */
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const VALIDATORS = [
  "validate-mw-depth.mjs",
  "validate-dictionary-comparison.mjs",
  "validate-citation-canon.mjs",
  "validate-tradition-tags.mjs",
  "validate-correction-feed.mjs",
  "validate-heritage-witness.mjs",
  "validate-four-axis-independence.mjs",
  "validate-review-reports.mjs"
];

function run(command, args) {
  const result = spawnSync(command, args, { cwd: ROOT, encoding: "utf8", stdio: "inherit", shell: process.platform === "win32" });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed with exit code ${result.status}`);
}

function assertClean(label) {
  const result = spawnSync("git", ["diff", "--quiet", "--exit-code"], { cwd: ROOT, encoding: "utf8", shell: process.platform === "win32" });
  const staged = spawnSync("git", ["diff", "--cached", "--quiet", "--exit-code"], { cwd: ROOT, encoding: "utf8", shell: process.platform === "win32" });
  if (result.status !== 0 || staged.status !== 0) throw new Error(`${label}: tracked files are not clean.`);
}

export function verify() {
  assertClean("before verification");
  run(process.execPath, ["--test"]);
  for (const validator of VALIDATORS) run(process.execPath, [path.join("scripts", validator)]);
  run(process.execPath, [path.join("scripts", "regen-review-artifacts.mjs")]);
  run(process.execPath, [path.join("scripts", "regen-review-artifacts.mjs")]);
  assertClean("after deterministic regeneration");
  run("npm", ["run", "build"]);
  run("npm", ["audit", "--audit-level=high"]);
  assertClean("after build and audit");
  console.log("verify: all tests, validators, deterministic regeneration, build, audit, and clean-tree checks passed.");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    verify();
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}
