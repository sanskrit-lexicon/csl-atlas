// Validate the dictionary authority tiers contract (ADR-0001, MG 21-11-2026).
//
// The Patel census (data/L0/patel2016_assignments.csv) counts dictionary
// witnesses for citation-convention options. ADR-0001 rules that badges over
// that census must be tiered — authority tiers A (Grundlagen: PWG, PW) / A2
// (SCH supplement) / B / C / D plus the IND/EUR origin axis, with membership
// in data/L0/dict_authority_tiers.csv and flag-never-flip on conflicts. This
// validator keeps that contract from drifting: the census stays fully
// classified, the Grundlagen stay in Tier A, the sheet generator keeps
// consuming the tiers CSV, and the flat anonymous badge stays out of the code.
//
// Fails (exit 1) when:
// - data/L0/dict_authority_tiers.csv is missing/unparseable or drops a column;
// - a siglum is duplicated, or has tier outside {A,A2,B,C,D} or origin
//   outside {IND,EUR};
// - a siglum listed in patel2016_assignments.csv member_dicts is missing from
//   the tiers CSV or marked census_member=no;
// - PWG/PW are not census Tier A (the Grundlagen invariant);
// - the sheet generator no longer consumes the tiers CSV (load_tiers);
// - the flat anonymous badge literal reappears in scripts/, src/ or tools/.
//
// Usage: node scripts/validate-dict-authority-tiers.mjs   (also runs inside npm run verify)
// Test seam (mirrors the estate's CLAUDE_TEST_GH_ROOT, H8089): set
// DICT_TIERS_CSV to validate an alternative tiers file (negative testing).

import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(process.cwd());
const L0 = path.join(ROOT, "data", "L0");
const TIERS = process.env.DICT_TIERS_CSV
  ? path.resolve(process.env.DICT_TIERS_CSV)
  : path.join(L0, "dict_authority_tiers.csv");
const PATEL_GOLD = path.join(L0, "patel2016_assignments.csv");
const GENERATOR = path.join(ROOT, "scripts", "L0", "gen_lrv_fri_annotation_sheet.py");
const SCAN_DIRS = ["scripts", "src", "tools"].map((d) => path.join(ROOT, d));
const SCAN_EXT = new Set([".py", ".mjs", ".js"]);
const FLAT_BADGE = "dicts use this";
const TIER_VALUES = new Set(["A", "A2", "B", "C", "D"]);
const ORIGIN_VALUES = new Set(["IND", "EUR"]);

const errors = [];
const notes = [];
const SELF = path.resolve(process.argv[1] || "");

function readText(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required file: ${path.relative(ROOT, file)}`);
    return null;
  }
  return fs.readFileSync(file, "utf8");
}

// Minimal RFC-4180-ish parser: quotes, doubled quotes, commas in fields.
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (ch === '"') inQuotes = false;
      else field += ch;
    } else if (ch === '"') inQuotes = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n") { row.push(field); field = ""; rows.push(row); row = []; }
    else if (ch !== "\r") field += ch;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.length > 1 || (r[0] || "").trim() !== "");
}

function toObjects(rows) {
  const head = rows[0].map((h) => h.trim());
  return rows.slice(1).map((r) =>
    Object.fromEntries(head.map((h, i) => [h, (r[i] ?? "").trim()])));
}

// --- tiers CSV ---
const tiersRows = readText(TIERS) === null ? null : toObjects(parseCsv(readText(TIERS)));
const tiers = new Map();
if (tiersRows) {
  const required = ["siglum", "tier", "origin", "full_name", "year", "census_member", "rationale"];
  for (const col of required) {
    if (tiersRows.length && !(col in tiersRows[0])) {
      errors.push(`tiers CSV drops required column '${col}'`);
    }
  }
  for (const r of tiersRows) {
    const sig = r.siglum;
    if (!sig) { errors.push("tiers CSV row without siglum"); continue; }
    if (tiers.has(sig)) errors.push(`duplicate siglum in tiers CSV: ${sig}`);
    if (!TIER_VALUES.has(r.tier)) errors.push(`${sig}: tier '${r.tier}' outside A/A2/B/C/D`);
    if (!ORIGIN_VALUES.has(r.origin)) errors.push(`${sig}: origin '${r.origin}' outside IND/EUR`);
    if (r.census_member !== "yes" && r.census_member !== "no") {
      errors.push(`${sig}: census_member '${r.census_member}' is not yes/no`);
    }
    tiers.set(sig, r);
  }
  notes.push(`tiers: ${tiers.size} sigla classified`);
  const grundlagen = ["PWG", "PW"].filter(
    (s) => tiers.get(s)?.tier === "A" && tiers.get(s)?.census_member === "yes");
  if (grundlagen.length < 2) {
    errors.push(`Grundlagen invariant broken: PWG+PW must be census Tier A (found ${grundlagen.join(",") || "none"})`);
  }
}

// --- census coverage: every Patel witness is classified ---
const patelRows = readText(PATEL_GOLD) === null ? null : toObjects(parseCsv(readText(PATEL_GOLD)));
if (patelRows) {
  const census = new Set();
  for (const r of patelRows) {
    for (const sig of (r.member_dicts || "").split(/\s+/).filter(Boolean)) census.add(sig);
  }
  const missing = [...census].filter((s) => !tiers.has(s));
  const nonmember = [...census].filter((s) => tiers.get(s)?.census_member !== "yes");
  if (missing.length) errors.push(`census sigla not in tiers CSV: ${missing.sort().join(", ")}`);
  if (nonmember.length) errors.push(`census sigla with census_member!=yes: ${nonmember.sort().join(", ")}`);
  notes.push(`census: ${census.size} sigla covered by Patel assignments`);
}

// --- generator consumes the tiers CSV ---
const gen = readText(GENERATOR);
if (gen !== null) {
  if (!gen.includes("dict_authority_tiers.csv") || !gen.includes("load_tiers")) {
    errors.push(`generator no longer consumes the tiers CSV: ${path.relative(ROOT, GENERATOR)}`);
  }
}

// --- flat anonymous badge literal banned from code ---
function* walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory() && e.name !== "node_modules" && e.name !== "__pycache__") yield* walk(p);
    else if (e.isFile() && SCAN_EXT.has(path.extname(e.name))) yield p;
  }
}
if (fs.existsSync(path.join(ROOT, "scripts"))) {
  for (const dir of SCAN_DIRS) {
    if (!fs.existsSync(dir)) continue;
    for (const file of walk(dir)) {
      if (path.resolve(file) === SELF) continue; // the ban lives in this validator's own source
      const text = fs.readFileSync(file, "utf8");
      if (text.includes(FLAT_BADGE)) {
        errors.push(`flat census badge literal in ${path.relative(ROOT, file)} — tier it (ADR-0001)`);
      }
    }
  }
}

for (const note of notes) console.log(`note: ${note}`);
if (errors.length > 0) {
  console.error(`validate-dict-authority-tiers: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-dict-authority-tiers: OK");
