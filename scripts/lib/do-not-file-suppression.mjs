// Do-not-file suppression signal (H083; PROJECT_INTERLINKS "do-not-file
// suppression corpus" feed).
//
// SanskritSpellCheck maintains a standing list of headwords that LOOK like
// misspellings but are documented on purpose by a dictionary (w.r./v.l.
// apparatus readings, nopadesa roots, {{Lbody}} redirects, colophon
// spellings) -- 2,297 forms across 33 dicts as of the 2026-06-24 corpus.
// The list lives in a SIBLING repo and is not vendored here; it is resolved
// the same way scripts/forensic reads csl-orig: an env override, else the
// default sibling path, with graceful absence. If the file is missing,
// loadSuppression() returns an empty Set and every caller sees zero
// suppression hits -- behaviour is then unchanged from before this feed
// existed.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { normalizeLemma } from "./dict-normalize.mjs";

const _HERE = path.dirname(fileURLToPath(import.meta.url));
// scripts/lib -> scripts -> csl-atlas -> GitHub root -> SanskritSpellCheck sibling
const DEFAULT_PATH = path.resolve(
  _HERE, "..", "..", "..",
  "SanskritSpellCheck", "nochange", "do_not_file_suppress.txt"
);

export const SOURCE_LABEL = "SanskritSpellCheck do_not_file_suppress.txt";
export const SOURCE_AS_OF = "2026-06-24";

let _cache = null;

export function suppressionPath() {
  return process.env.DO_NOT_FILE_SUPPRESS_PATH || DEFAULT_PATH;
}

/** Return the normalized-SLP1 suppression set. Empty Set if the sibling asset is absent. */
export function loadSuppression(filePath) {
  if (filePath == null && _cache) return _cache;
  const resolved = filePath || suppressionPath();
  const out = new Set();
  if (fs.existsSync(resolved)) {
    for (const line of fs.readFileSync(resolved, "utf8").split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      out.add(normalizeLemma(trimmed).normalized);
    }
  }
  if (filePath == null) _cache = out;
  return out;
}

/**
 * Look up a headword. Returns null when there is no hit (or the sibling
 * asset is absent), otherwise a provenance annotation -- never a mutation of
 * the caller's review fields.
 */
export function suppressionHit(lemma, set) {
  const idx = set ?? loadSuppression();
  if (!idx.size) return null;
  const normalized = normalizeLemma(lemma ?? "").normalized;
  if (!idx.has(normalized)) return null;
  return {
    hit: true,
    classification: "deliberate-nonstandard",
    source: SOURCE_LABEL,
    asOf: SOURCE_AS_OF
  };
}
