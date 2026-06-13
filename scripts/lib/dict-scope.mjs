import fs from "node:fs";
import path from "node:path";

export const SOURCE_ROOT = path.resolve(process.cwd(), "..", "csl-orig", "v02");
export const INVENTORY_PATH = path.resolve(process.cwd(), "src", "data", "lexicographic-structure", "dictionary_inventory.csv");

export const CORE_COMPARISON_DICTS = [
  { code: "mw", label: "MW", grammarReliable: true, homonymMarked: true, citationTagged: true, senseSegmented: false },
  { code: "ap", label: "AP", grammarReliable: true, homonymMarked: false, citationTagged: true, senseSegmented: true },
  { code: "pwg", label: "PWG", grammarReliable: true, homonymMarked: true, citationTagged: true, senseSegmented: true },
  { code: "pw", label: "PWK", grammarReliable: true, homonymMarked: true, citationTagged: true, senseSegmented: true },
  { code: "wil", label: "WIL", grammarReliable: true, homonymMarked: false, citationTagged: false, senseSegmented: false },
  { code: "vcp", label: "VCP", grammarReliable: false, homonymMarked: false, citationTagged: false, senseSegmented: false },
  { code: "skd", label: "SKD", grammarReliable: false, homonymMarked: false, citationTagged: false, senseSegmented: false }
];

export const BROAD_HEADWORD_SHARD_PREFIXES = [
  "a", "A", "i", "I", "u", "U", "f", "F", "x", "X", "e", "E", "o", "O",
  "k", "K", "g", "G", "N", "c", "C", "j", "J", "Y", "w", "W", "q", "Q", "R",
  "t", "T", "d", "D", "n", "p", "P", "b", "B", "m", "y", "r", "l", "v",
  "S", "z", "s", "h"
];

const CORE_FLAGS = new Map(CORE_COMPARISON_DICTS.map(d => [d.code, d]));
const BROAD_LANGUAGE_PAIRS = new Set(["BHS-Eng"]);

function parseCsvLine(line) {
  const out = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      if (quoted && line[i + 1] === '"') {
        cell += '"';
        i++;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      out.push(cell);
      cell = "";
    } else {
      cell += char;
    }
  }
  out.push(cell);
  return out;
}

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter(line => line.trim().length);
  if (!lines.length) return [];
  const header = parseCsvLine(lines[0]);
  return lines.slice(1).map(line => {
    const cells = parseCsvLine(line);
    return Object.fromEntries(header.map((key, i) => [key, cells[i] ?? ""]));
  });
}

function normalizeCode(code) {
  return String(code ?? "").trim().toLowerCase();
}

function boolField(value) {
  return String(value ?? "").trim().toLowerCase() === "yes";
}

function numericField(value) {
  const n = Number(value);
  return Number.isFinite(n) && value !== "" ? n : null;
}

function labelForCode(code) {
  return code === "pw" ? "PWK" : code.toUpperCase();
}

function dictPath(code) {
  return path.join(SOURCE_ROOT, code, `${code}.txt`);
}

export function loadDictionaryInventory(inventoryPath = INVENTORY_PATH) {
  return parseCsv(fs.readFileSync(inventoryPath, "utf8")).map(row => ({
    ...row,
    code: normalizeCode(row.code),
    year: numericField(row.year),
    start_year: numericField(row.start_year),
    end_year: numericField(row.end_year),
    deprecated: boolField(row.deprecated),
    in_github: boolField(row.in_github),
    in_sanhw1: boolField(row.in_sanhw1),
    sanhw1_lemmas: numericField(row.sanhw1_lemmas)
  }));
}

export function discoverLocalDictionaryCodes(sourceRoot = SOURCE_ROOT) {
  if (!fs.existsSync(sourceRoot)) return new Set();
  return new Set(fs.readdirSync(sourceRoot, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => normalizeCode(dirent.name))
    .filter(code => fs.existsSync(path.join(sourceRoot, code, `${code}.txt`))));
}

export function isBroadHeadwordEligible(row, localCodes = discoverLocalDictionaryCodes()) {
  const code = normalizeCode(row?.code);
  const languagePair = String(row?.language_pair ?? "").trim();
  if (!code || !localCodes.has(code)) return false;
  if (languagePair.startsWith("Eng-")) return false;
  return languagePair.startsWith("Skt-") || BROAD_LANGUAGE_PAIRS.has(languagePair);
}

export function dictionaryMetadata(row, { localCodes = discoverLocalDictionaryCodes() } = {}) {
  const code = normalizeCode(row.code);
  const core = CORE_FLAGS.get(code) ?? {};
  const sourceExists = localCodes.has(code);
  const inGithub = Boolean(row.in_github);
  return {
    code,
    label: core.label ?? labelForCode(code),
    fullName: row.full_name || labelForCode(code),
    languagePair: row.language_pair || "",
    family: row.family || "",
    deprecated: Boolean(row.deprecated),
    sourceExists,
    sourceLinkMode: sourceExists && inGithub ? "github" : "local-only",
    grammarReliable: Boolean(core.grammarReliable),
    citationTagged: Boolean(core.citationTagged),
    senseSegmented: Boolean(core.senseSegmented),
    homonymMarked: Boolean(core.homonymMarked),
    year: row.year ?? null,
    startYear: row.start_year ?? null,
    endYear: row.end_year ?? null,
    letterCoverage: row.letter_coverage || "",
    inGithub,
    inSanhw1: Boolean(row.in_sanhw1),
    sanhw1Lemmas: row.sanhw1_lemmas ?? null,
    notes: row.notes || ""
  };
}

export function coreComparisonDictionaries({ inventoryRows = null, localCodes = discoverLocalDictionaryCodes() } = {}) {
  const inventoryByCode = new Map((inventoryRows ?? loadDictionaryInventory()).map(row => [normalizeCode(row.code), row]));
  return CORE_COMPARISON_DICTS.map(dict => {
    const row = inventoryByCode.get(dict.code);
    return row ? { ...dictionaryMetadata(row, { localCodes }), ...dict } : { ...dict };
  });
}

export function buildBroadHeadwordDictionaries({ inventoryRows = null, localCodes = discoverLocalDictionaryCodes() } = {}) {
  return (inventoryRows ?? loadDictionaryInventory())
    .filter(row => isBroadHeadwordEligible(row, localCodes))
    .map(row => dictionaryMetadata(row, { localCodes }))
    .sort((a, b) => {
      const ay = a.startYear ?? a.year ?? 9999;
      const by = b.startYear ?? b.year ?? 9999;
      return ay - by || a.code.localeCompare(b.code);
    });
}

export function excludedBroadHeadwordDictionaries({ inventoryRows = null, localCodes = discoverLocalDictionaryCodes() } = {}) {
  return (inventoryRows ?? loadDictionaryInventory())
    .filter(row => localCodes.has(normalizeCode(row.code)) && !isBroadHeadwordEligible(row, localCodes))
    .map(row => ({
      code: normalizeCode(row.code),
      label: labelForCode(normalizeCode(row.code)),
      languagePair: row.language_pair || "",
      reason: String(row.language_pair ?? "").startsWith("Eng-")
        ? "reverse English-headword dictionary"
        : "not a Sanskrit/BHS headword dictionary"
    }))
    .sort((a, b) => a.code.localeCompare(b.code));
}

export function shardIdForLemma(lemma) {
  const first = String(lemma ?? "")[0];
  return BROAD_HEADWORD_SHARD_PREFIXES.includes(first)
    ? first.charCodeAt(0).toString(16)
    : "other";
}

export function shardPrefixForId(id) {
  if (id === "other") return "";
  const prefix = String.fromCharCode(parseInt(id, 16));
  return BROAD_HEADWORD_SHARD_PREFIXES.includes(prefix) ? prefix : "";
}

export function sourceFileExists(code) {
  return fs.existsSync(dictPath(normalizeCode(code)));
}
