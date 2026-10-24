// Shared helpers for review-layer generators.
//
// Every review queue emits reports conforming to data/schema/review-report.schema.json
// and treats human decisions as an overlay preserved across rebuilds by reviewId.
// This module factors out that contract so each generator only describes its own
// machine fields. See docs/REVIEW_REPORTS.md.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { generatedAtForPayload, generatedAtNow, licenseFields, readJsonIfExists } from "./dataset-meta.mjs";

const MODULE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");

export const SCHEMA_VERSION = "1.0.0";

// Statuses that mean a human has acted; such items are carried forward verbatim.
export const HUMAN_STATUSES = new Set(["reviewed-ok", "reviewed-corrected", "blocked", "deferred"]);

/**
 * Load human-decided items from an existing report file so a rebuild preserves
 * them. Returns Map<reviewId, {reviewStatus, reviewedValue, reviewer, reviewedAt, note}>.
 */
export function loadPreserved(outputPath) {
  const preserved = new Map();
  if (!fs.existsSync(outputPath)) return preserved;
  try {
    const doc = JSON.parse(fs.readFileSync(outputPath, "utf8"));
    for (const item of doc.items || []) {
      if (HUMAN_STATUSES.has(item.reviewStatus) || item.reviewer) {
        preserved.set(item.reviewId, {
          reviewStatus: item.reviewStatus,
          reviewedValue: item.reviewedValue ?? null,
          reviewer: item.reviewer ?? null,
          reviewedAt: item.reviewedAt ?? null,
          note: item.note ?? ""
        });
      }
    }
  } catch {
    // ignore malformed prior file; machine fields are regenerated anyway
  }
  return preserved;
}

/**
 * The five trailing review fields for an item: a preserved human decision if
 * one exists for reviewId, otherwise the machine default (needs-review).
 */
export function reviewFields(preserved, reviewId) {
  const c = preserved.get(reviewId);
  return {
    reviewStatus: c?.reviewStatus ?? "needs-review",
    reviewedValue: c?.reviewedValue ?? null,
    reviewer: c?.reviewer ?? null,
    reviewedAt: c?.reviewedAt ?? null,
    note: c?.note ?? ""
  };
}

/**
 * Assemble the report envelope in the canonical field order. `extra` is spread
 * after `queue` and before assumptions/warnings/items.
 */
export function reviewPayload({ queue, sourcePath, items, assumptions = [], warnings = [], extra = {} }) {
  return {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: generatedAtNow(),
    sourcePath,
    recordCount: items.length,
    queue,
    ...extra,
    assumptions,
    warnings,
    items
  };
}

// ── The reseed lock (H2892) ────────────────────────────────────────────────
//
// Thirteen of the fourteen review generators call loadPreserved and are
// overlay-preserving by construction. The fourteenth,
// scripts/build-r2-checkpoint-review.mjs, takes --reseed, which skips
// loadPreserved and blanks the human overlay back to the machine seed. That is
// the Uprava DANGER_FACTS "never --reseed" row, and until now the row was prose.
//
// The H2890 census measured what is behind it: of 19,368 review rows, 147 carry
// a reviewed-* status and only 10 of those are human-attributed. Ten human
// rulings is a small enough number to lose in one careless rebuild and a large
// enough number that nobody will reconstruct them from memory.

/** The one escape hatch, exact-matched on "1". */
export const OVERLAY_WIPE_HATCH = "ALLOW_OVERLAY_WIPE";

/** Refusal exit code, deliberately distinct from the scripts' own failures (1). */
export const RESEED_REFUSAL_EXIT = 2;

/** Verbatim from the Uprava danger row this lock enforces. */
export const RESEED_DANGER_SENTENCE =
  "--reseed blanks the human review overlay back to the machine seed";

// ── Protected paths (H6980) ────────────────────────────────────────────────
//
// The lock used to know one output path because it knew one generator. H6980
// moves the list out of the code: the guard refuses by PATH against the shared
// registry (canonical in kosha, vendored here), so a new generator that writes
// a human-reviewed file cannot slip past just because its script name is new.

/** Registry path, relative to the repo root. */
export const PROTECTED_PATHS_REGISTRY = path.join("data", "manifest", "protected_paths.tsv");

/** Only used when the registry file is absent — the H2890 review report. */
export const PROTECTED_PATH_FALLBACK = Object.freeze([
  "src/data/review/r2-checkpoint-review.json"
]);

/** Repo slug for registry rows, read from package.json (stable in worktrees). */
export function repoName(root = MODULE_ROOT) {
  try {
    const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
    if (pkg.name) return pkg.name;
  } catch {
    // fall through to the directory name
  }
  return path.basename(root);
}

function normaliseTarget(target, root = MODULE_ROOT) {
  const absolute = path.isAbsolute(target) ? target : path.resolve(root, target);
  return path.relative(root, absolute).split(path.sep).join("/");
}

function globToRegExp(glob) {
  let source = "^";
  for (let i = 0; i < glob.length; i += 1) {
    const char = glob[i];
    if (char === "*") {
      if (glob[i + 1] === "*") {
        source += ".*";
        i += 1;
      } else {
        source += "[^/]*";
      }
    } else if (char === "?") {
      source += "[^/]";
    } else {
      source += char.replace(/[.+^${}()|[\]\\]/g, "\\$&");
    }
  }
  return new RegExp(`${source}$`);
}

/**
 * This repo's protected globs, or null when the registry is missing/malformed.
 * A missing registry is not consent: callers fall back to the H2890 path.
 */
export function loadProtectedPaths({
  root = MODULE_ROOT,
  registry = path.join(root, PROTECTED_PATHS_REGISTRY),
  repo = repoName(root)
} = {}) {
  if (!registry || !fs.existsSync(registry)) return null;
  const lines = fs.readFileSync(registry, "utf8")
    .split(/\r?\n/)
    .filter(line => line.trim() && !line.trimStart().startsWith("#"));
  if (!lines.length) return null;
  const header = lines.shift().split("\t");
  const index = Object.fromEntries(header.map((name, i) => [name, i]));
  if (!["repo", "path_glob", "reason", "owner", "since"].every(field => field in index)) {
    return null;
  }
  const paths = [];
  for (const line of lines) {
    const cols = line.split("\t");
    if ((cols[index.repo] || "").trim() !== repo) continue;
    const glob = (cols[index.path_glob] || "").trim().replaceAll("\\", "/");
    if (glob) paths.push(glob);
  }
  return paths;
}

/** True when `target` matches a registry glob for this repo. */
export function isProtectedPath(target, {
  root = MODULE_ROOT,
  registry = path.join(root, PROTECTED_PATHS_REGISTRY),
  repo = repoName(root)
} = {}) {
  if (!target) return false;
  const normalised = normaliseTarget(target, root);
  const paths = loadProtectedPaths({ root, registry, repo });
  if (paths === null) return PROTECTED_PATH_FALLBACK.includes(normalised);
  return paths.some(glob => globToRegExp(glob).test(normalised));
}

/** True only for the exact string "1" — a half-set hatch is not consent. */
export function reseedIsHatched(env = process.env) {
  return env[OVERLAY_WIPE_HATCH] === "1";
}

export function reseedRefusalMessage({ script, outputPath }) {
  const target = outputPath ? path.relative(process.cwd(), outputPath) : "the review report";
  return [
    `REFUSED: ${script} --reseed is a guarded overlay wipe (H2892).`,
    "",
    RESEED_DANGER_SENTENCE,
    `  ${target}`,
    "",
    `Protected paths come from ${PROTECTED_PATHS_REGISTRY.split(path.sep).join("/")},`,
    "not from the script name (H6980).",
    "",
    "Nothing was written. A plain rebuild is always allowed and preserves every",
    "human decision:",
    "",
    `    node ${script}`,
    "",
    "If the overlay genuinely has to go back to the machine seed, say so",
    "explicitly and re-pin the tripwire in the same commit:",
    "",
    `    ${OVERLAY_WIPE_HATCH}=1 node ${script} --reseed`,
    "    python -m csl_pyutil.integrity_tripwire --extract \\",
    "           --pin data/integrity/csl_atlas_review.pin.json --write-pin \\",
    '           --reason "what changed and why" --updated DD-MM-YYYY',
    ""
  ].join("\n");
}

/**
 * Refuse a --reseed run unless the hatch is set. Returns true when it refused
 * (the caller should stop), false when the run may proceed. `exit` and `log`
 * are injectable so the lock can be tested without ending the test process.
 */
export function refuseReseedWithoutHatch({
  script,
  outputPath,
  env = process.env,
  exit = code => process.exit(code),
  log = message => console.error(message),
  root = MODULE_ROOT,
  registry = path.join(root, PROTECTED_PATHS_REGISTRY)
} = {}) {
  if (reseedIsHatched(env)) return false;
  if (outputPath && !isProtectedPath(outputPath, { root, registry })) return false;
  log(reseedRefusalMessage({ script, outputPath }));
  exit(RESEED_REFUSAL_EXIT);
  return true;
}

export function writeReport(outputPath, payload) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  const previous = readJsonIfExists(outputPath, fs);
  const finalPayload = payload?.generatedAt
    ? { ...payload, generatedAt: generatedAtForPayload(previous, payload) }
    : payload;
  fs.writeFileSync(outputPath, `${JSON.stringify(finalPayload, null, 2)}\n`);
}
