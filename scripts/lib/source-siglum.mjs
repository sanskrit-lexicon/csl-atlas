// Cross-dictionary source-siglum canonicalization.
//
// Dictionaries cite the same source under different siglum conventions
// (MW "MBh" vs PWG "MBH"; "RV" vs "ṚV"; "BhP" vs "Bhāg"). To compare citation
// apparatus across dictionaries we need a canonical identity per source.
//
// Two layers:
//   1. foldSiglum() — strip diacritics, lowercase, drop non-alphanumerics.
//      This auto-aligns the common case/diacritic variants (MBh/MBH -> mbh).
//   2. a reviewed alias table (src/data/dict-source-aliases.json) for the
//      scheme differences the fold cannot catch (bhag -> bhp).
//
// canonicalSiglum() = alias(fold(siglum)). This is a growing reviewed dataset;
// the source-siglum review queue surfaces candidates to add to the alias table.

import fs from "node:fs";
import path from "node:path";

const ALIAS_FILE = path.resolve(process.cwd(), "src", "data", "dict-source-aliases.json");

/** Diacritic- and case-insensitive fold of a source abbreviation. */
export function foldSiglum(siglum) {
  return (siglum || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "") // combining marks
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");
}

let reverse = null; // fold-key -> canonical id
let aliasMeta = null;

function loadAliases() {
  if (reverse) return;
  reverse = new Map();
  aliasMeta = {};
  if (!fs.existsSync(ALIAS_FILE)) return;
  const data = JSON.parse(fs.readFileSync(ALIAS_FILE, "utf8"));
  for (const [id, entry] of Object.entries(data.canonical || {})) {
    aliasMeta[id] = entry.name || id;
    reverse.set(id, id); // the canonical id's own fold-key maps to itself
    for (const alias of entry.aliases || []) reverse.set(foldSiglum(alias), id);
  }
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
