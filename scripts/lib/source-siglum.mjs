// Cross-dictionary source-siglum canonicalization.
//
// Dictionaries cite the same source under different siglum conventions
// (MW "MBh" vs PWG "MBH"; "RV" vs "ṚV"; "BhP" vs "Bhāg"). To compare citation
// apparatus across dictionaries we need a canonical identity per source.
//
// Two layers:
//   1. foldSiglum() — strip diacritics, lowercase, drop non-alphanumerics,
//      then strip a trailing locator suffix (chapter/volume roman numerals
//      dictionaries tack onto a bare siglum, e.g. "Ragh. iii" -> "raghiii").
//      This auto-aligns the common case/diacritic/locator variants.
//   2. a reviewed alias table (src/data/dicts/dict-source-aliases.json) for
//      the scheme differences the fold cannot catch (bhagpedbomb -> bhagp).
//
// canonicalSiglum() = alias(fold(siglum)). This is a growing reviewed dataset;
// the source-siglum review queue surfaces candidates to add to the alias table.

import fs from "node:fs";
import path from "node:path";

const ALIAS_FILE = path.resolve(process.cwd(), "src", "data", "dicts", "dict-source-aliases.json");

// Bases named in the curated table's foldRuleFixes note as having locator-
// suffixed pseudo-members (chapter/volume roman numerals a dictionary tacks
// onto its own bare siglum, e.g. "Ragh. iii" -> "raghiii" -> "ragh"). Kept as
// an explicit allowlist rather than a generic trailing-roman-numeral strip:
// a generic strip corrupts unrelated real sigla that merely end in valid
// roman-numeral letters (ratnam -> ratna, mahav -> maha, sabdac/sabdam both
// -> sabda, harsac -> harsa, panc -> pan, ...) — verified empty-collision
// against every key in dict-source-aliases.json (aliases/distinctWorks/
// uncertain) before adopting this list. Sync with scripts/obs/siglum_families.py.
const LOCATOR_BASES = [
  "ragh", "susr", "dhatup", "pan", "mbh", "aitbr", "laty", "mrcch", "nais",
  "gobh", "yajn", "katysr", "maitrs", "sarvad", "bhatt", "vikr", "prab",
  "balar", "dasar", "rajat", "kathas", "naigh",
].sort((a, b) => b.length - a.length); // longest base first

const IVX_ONLY = /^[ivx]+$/;

/**
 * Strip a trailing lowercase roman-numeral locator token for a known base,
 * e.g. "raghiii" -> "ragh", "dhatupxxxii" -> "dhatup". Only fires when the
 * key starts with one of LOCATOR_BASES and the remainder is composed solely
 * of i/v/x (the numeral letters actually seen in this corpus's locators) —
 * this is what keeps it from eating real sigla like hariv/divyav/malav/
 * rajav/vikram, none of which start with a listed base.
 */
function stripLocatorSuffix(key) {
  for (const base of LOCATOR_BASES) {
    if (key.length > base.length && key.startsWith(base) && IVX_ONLY.test(key.slice(base.length))) {
      return base;
    }
  }
  return key;
}

/** Diacritic- and case-insensitive fold of a source abbreviation. */
export function foldSiglum(siglum) {
  const key = (siglum || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "") // combining marks
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");
  return stripLocatorSuffix(key);
}

let reverse = null; // fold-key -> canonical id
let aliasMeta = null; // canonical id -> display name (distinctWorks note)

function loadAliases() {
  if (reverse) return;
  reverse = new Map();
  aliasMeta = {};
  if (!fs.existsSync(ALIAS_FILE)) return;
  const data = JSON.parse(fs.readFileSync(ALIAS_FILE, "utf8"));
  for (const [id, name] of Object.entries(data.distinctWorks || {})) {
    aliasMeta[id] = name;
    reverse.set(id, id); // the canonical id's own fold-key maps to itself
  }
  for (const [alias, id] of Object.entries(data.aliases || {})) {
    reverse.set(foldSiglum(alias), id);
  }
  // data.uncertain keys are deliberately NOT merged — canonicalSiglum falls
  // back to the bare fold key for them, same as any unreviewed key.
}

/**
 * Canonical identity for a source siglum: the reviewed alias if one applies,
 * else the bare fold key.
 */
export function canonicalSiglum(siglum) {
  loadAliases();
  const k = foldSiglum(siglum);
  return reverse.get(k) ?? k;
}

export function canonicalName(id) {
  loadAliases();
  return aliasMeta[id] ?? null;
}
