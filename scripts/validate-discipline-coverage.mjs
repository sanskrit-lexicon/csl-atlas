// Validate the committed discipline-coverage packet (H4178 flip 3).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// cross-check against the sibling IndologyScholars crosswalk runs only when
// the sibling checkout is present (it is not on CI runners).
//
// Fails (exit 1) when:
// - the output JSON / source envelope / assignments file is missing or unparseable;
// - totals disagree (assigned + unassigned != dicts) or perDiscipline lists
//   do not re-derive from the per-dict rows;
// - a per-dict confidence value disagrees with
//   assignmentConfidence x crosswalkConfidence beyond rounding, or rows are
//   not sorted by descending confidence;
// - an unassigned dict carries disciplines or a nonzero assignment confidence;
// - a dict from dictionary-coverage.json lacks an assignment row, or an
//   assignment row references a dict absent from the coverage inventory;
// - (sibling present) an assigned meso code is absent from the crosswalk, a
//   joined discipline code is absent from disciplines.csv, or the pinned
//   feedCommit no longer matches the sibling HEAD (stale pin warning only).
//
// Usage: npm run validate-discipline-coverage   (run after build-discipline-coverage)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { parseCsv } from "./build-discipline-coverage.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "disciplines");
const JSON_OUT = path.join(OUT_DIR, "discipline_coverage.json");
const SOURCE_OUT = path.join(OUT_DIR, "discipline_coverage.source.json");
const ASSIGNMENTS_PATH = path.join(OUT_DIR, "dict_meso_assignments.json");
const COVERAGE_PATH = path.resolve(process.cwd(), "src", "data", "dictionary-coverage.json");
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "IndologyScholars");
const CROSSWALK_PATH = path.join(SIBLING_ROOT, "curation", "meso_discipline_crosswalk.csv");
const DISCIPLINES_PATH = path.join(SIBLING_ROOT, "curation", "disciplines.csv");

const errors = [];
const notes = [];

function fail(msg) {
  errors.push(msg);
}
function round(value, digits = 4) {
  return Number(value.toFixed(digits));
}

const payload = JSON.parse(fs.readFileSync(JSON_OUT, "utf8"));
const source = JSON.parse(fs.readFileSync(SOURCE_OUT, "utf8"));
const assignmentsDoc = JSON.parse(fs.readFileSync(ASSIGNMENTS_PATH, "utf8"));
const coverage = JSON.parse(fs.readFileSync(COVERAGE_PATH, "utf8"));

if (payload.schemaVersion !== "1.0.0") fail(`unexpected schemaVersion ${payload.schemaVersion}`);
if (source.dataset !== "discipline_coverage") fail("source envelope dataset mismatch");
if (!source.feedCommit) notes.push("source envelope has no feedCommit (sibling absent at build time)");

// totals
if (payload.totals.assigned + payload.totals.unassigned !== payload.totals.dicts) {
  fail("totals do not add up");
}
if (payload.dicts.length !== payload.totals.dicts) fail("dicts[] length != totals.dicts");

// assignment layer vs coverage inventory
const coverageCodes = new Set(coverage.dicts.map((d) => d.code));
const assignmentDicts = assignmentsDoc.assignments.map((a) => a.dict);
for (const code of coverageCodes) {
  if (!assignmentDicts.includes(code)) fail(`coverage dict ${code} has no assignment row`);
}
const seen = new Set();
for (const a of assignmentsDoc.assignments) {
  if (seen.has(a.dict)) fail(`duplicate assignment row for ${a.dict}`);
  seen.add(a.dict);
  if (!coverageCodes.has(a.dict)) fail(`assignment row for unknown dict ${a.dict}`);
  if (a.mesoCode === null && a.confidence !== 0) {
    fail(`unassigned dict ${a.dict} has nonzero assignment confidence`);
  }
  if (a.mesoCode === null && !a.rationale) {
    fail(`unassigned dict ${a.dict} lacks an unassignment rationale`);
  }
}

// per-dict consistency
const perDisciplineDerived = new Map();
for (const d of payload.dicts) {
  if (!d.mesoCode) {
    if (d.disciplines.length > 0) fail(`unassigned dict ${d.dict} carries disciplines`);
    continue;
  }
  if (d.disciplines.length === 0) fail(`assigned dict ${d.dict} has empty disciplines[]`);
  let prev = Infinity;
  for (const disc of d.disciplines) {
    const expect = round(Math.min(1, d.assignmentConfidence * disc.crosswalkConfidence));
    if (disc.confidence !== expect) {
      fail(`dict ${d.dict} discipline ${disc.code}: confidence ${disc.confidence} != ${expect}`);
    }
    if (disc.confidence > prev) fail(`dict ${d.dict}: disciplines[] not sorted by confidence`);
    prev = disc.confidence;
    if (!perDisciplineDerived.has(disc.code)) perDisciplineDerived.set(disc.code, new Set());
    perDisciplineDerived.get(disc.code).add(d.dict);
  }
}

// perDiscipline re-derivation
for (const pd of payload.perDiscipline) {
  const derived = perDisciplineDerived.get(pd.code);
  if (!derived) fail(`perDiscipline ${pd.code} absent from per-dict rows`);
  else if (derived.size !== pd.dicts.length) {
    fail(`perDiscipline ${pd.code}: ${pd.dicts.length} dicts listed, ${derived.size} derived`);
  }
}
if (payload.perDiscipline.length !== perDisciplineDerived.size) {
  fail("perDiscipline count disagrees with derived map");
}

// not-mapped sentinels: deliberate rows must stay surfaced
if (payload.notMappedSentinels.length === 0) {
  notes.push("crosswalk emitted zero NOT-MAPPED sentinel rows (unexpected for the 29-08 snapshot)");
}

// sibling cross-check (only when the checkout is present)
if (fs.existsSync(CROSSWALK_PATH) && fs.existsSync(DISCIPLINES_PATH)) {
  const crosswalkRows = parseCsv(fs.readFileSync(CROSSWALK_PATH, "utf8"));
  const disciplines = new Set(
    parseCsv(fs.readFileSync(DISCIPLINES_PATH, "utf8")).map((r) => r.discipline_code)
  );
  const crosswalkMeso = new Set(crosswalkRows.map((r) => r.meso_code));
  for (const d of payload.dicts) {
    if (!d.mesoCode) continue;
    if (!crosswalkMeso.has(d.mesoCode)) fail(`meso code ${d.mesoCode} (dict ${d.dict}) not in sibling crosswalk`);
    for (const disc of d.disciplines) {
      if (!disciplines.has(disc.code)) {
        fail(`discipline ${disc.code} (dict ${d.dict}) not in sibling disciplines.csv`);
      }
    }
  }
  try {
    const head = execSync("git rev-parse HEAD", { cwd: SIBLING_ROOT, encoding: "utf8" }).trim();
    if (source.feedCommit && head !== source.feedCommit) {
      notes.push(`sibling feed moved: pinned ${source.feedCommit.slice(0, 10)}, HEAD ${head.slice(0, 10)} (rebuild to refresh)`);
    }
  } catch {
    // detached/shallow sibling; skip
  }
} else {
  notes.push("sibling IndologyScholars checkout absent - crosswalk cross-check skipped (CI mode)");
}

if (errors.length) {
  console.error(`validate-discipline-coverage: FAIL (${errors.length})`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
for (const n of notes) console.log(`note: ${n}`);
console.log(
  `validate-discipline-coverage: OK (${payload.totals.dicts} dicts, ${payload.totals.assigned} assigned, ` +
    `${payload.totals.disciplines} disciplines, ${payload.notMappedSentinels.length} sentinel rows)`
);
