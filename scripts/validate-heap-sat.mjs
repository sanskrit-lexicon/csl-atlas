// Validate the committed heap-sat packet (H1576, PH8).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// full rebuild cross-check against the sibling SanskritLexicography union
// runs only when that checkout is present (it is not on CI runners).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - steps don't accumulate (cumulativeTokens/cumulativeDistinct not the
//   running sums of lemmas/novelty), novelty exceeds lemmas, or the final
//   cumulativeDistinct disagrees with totals.unionLemmas;
// - steps are not in publication order (year ascending, siglum tie-break);
// - the Heaps fit is degenerate (beta outside (0,1) or r2 missing/low);
// - specialisedBreak p-values are outside (0,1], or the specialised roster
//   disagrees with the steps' family flags;
// - post1890General disagrees with the steps table;
// - (sibling present) rebuilding from the live inputs disagrees with the
//   committed totals, fit, or break statistic.
//
// Usage: npm run validate-heap-sat   (run after build-heap-sat)

import fs from "node:fs";
import path from "node:path";
import { parseTsv } from "./build-heritage-witness.mjs";
import { buildPayload } from "./build-heap-sat.mjs";
import { loadDictionaryInventory } from "./lib/dict-scope.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "heap_sat.json");
const SOURCE_OUT = path.join(OUT_DIR, "heap_sat.source.json");
const SYNCED_COPY = path.resolve(process.cwd(), "src", "data", "lexico", "heap_sat.json");
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "SanskritLexicography");
const UNION_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "union", "union_headwords.tsv");

const errors = [];
const notes = [];

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON: ${path.relative(process.cwd(), file)} (${e.message})`);
    return null;
  }
}

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);

if (packet) {
  const steps = packet.steps ?? [];
  let cumTok = 0;
  let cumDist = 0;
  let prev = null;
  for (const s of steps) {
    cumTok += s.lemmas;
    cumDist += s.novelty;
    if (s.cumulativeTokens !== cumTok) errors.push(`step ${s.code}: cumulativeTokens ${s.cumulativeTokens} != running sum ${cumTok}`);
    if (s.cumulativeDistinct !== cumDist) errors.push(`step ${s.code}: cumulativeDistinct ${s.cumulativeDistinct} != running sum ${cumDist}`);
    if (s.novelty > s.lemmas) errors.push(`step ${s.code}: novelty ${s.novelty} > lemmas ${s.lemmas}`);
    if (Math.abs(s.noveltyShare - s.novelty / s.lemmas) > 0.0011) errors.push(`step ${s.code}: noveltyShare mismatch`);
    if (prev && (s.year < prev.year || (s.year === prev.year && s.code < prev.code))) {
      errors.push(`steps not in publication order at ${prev.code} -> ${s.code}`);
    }
    if (s.specialised !== (s.family === "Specialized")) errors.push(`step ${s.code}: specialised flag disagrees with family`);
    prev = s;
  }
  if (steps.length !== packet.totals?.dictionaries) errors.push(`steps length ${steps.length} != totals.dictionaries`);
  if (cumDist !== packet.totals?.unionLemmas) errors.push(`final cumulativeDistinct ${cumDist} != totals.unionLemmas ${packet.totals?.unionLemmas}`);
  if (cumTok !== packet.totals?.totalLemmaListings) errors.push(`final cumulativeTokens ${cumTok} != totals.totalLemmaListings`);

  const fit = packet.heapsFit ?? {};
  if (!(fit.beta > 0 && fit.beta < 1)) errors.push(`Heaps beta ${fit.beta} outside (0,1) — not a saturating fit`);
  if (!(fit.r2LogLog > 0.9)) errors.push(`Heaps log-log R2 ${fit.r2LogLog} below 0.9`);

  const brk = packet.specialisedBreak ?? {};
  for (const [name, block] of [["orderPermutation", brk.orderPermutation], ["labelPermutation", brk.labelPermutation]]) {
    const p = block?.pOneSided;
    if (!(p > 0 && p <= 1)) errors.push(`specialisedBreak.${name}.pOneSided ${p} outside (0,1]`);
  }
  const specialisedFromSteps = steps.filter((s) => s.specialised).map((s) => s.code).sort();
  const specialisedDeclared = [...(packet.totals?.specialised ?? [])].sort();
  if (JSON.stringify(specialisedFromSteps) !== JSON.stringify(specialisedDeclared)) {
    errors.push(`totals.specialised ${specialisedDeclared} disagrees with steps' family flags ${specialisedFromSteps}`);
  }

  const expectedPost1890 = steps
    .filter((s) => !s.specialised && s.year >= 1890)
    .map((s) => ({ code: s.code, year: s.year, noveltyShare: s.noveltyShare }));
  if (JSON.stringify(expectedPost1890) !== JSON.stringify(packet.post1890General)) {
    errors.push("post1890General disagrees with the steps table");
  }
}

if (envelope && packet && envelope.generatedAt !== packet.generatedAt) {
  errors.push(`source envelope generatedAt ${envelope.generatedAt} != packet generatedAt ${packet.generatedAt}`);
}

if (packet && fs.existsSync(SYNCED_COPY)) {
  const synced = readJson(SYNCED_COPY);
  if (synced && JSON.stringify(synced) !== JSON.stringify(packet)) {
    errors.push("src/data/lexico/heap_sat.json (site copy) differs from data/lexico/heap_sat.json — run npm run sync-site-data");
  }
}

if (packet && fs.existsSync(UNION_PATH)) {
  const unionRows = parseTsv(fs.readFileSync(UNION_PATH, "utf8"));
  const rebuilt = buildPayload(unionRows, loadDictionaryInventory(), { generatedAt: packet.generatedAt });
  for (const key of ["totals", "heapsFit", "steps", "post1890General"]) {
    if (JSON.stringify(rebuilt[key]) !== JSON.stringify(packet[key])) {
      errors.push(`rebuild cross-check: ${key} disagrees with the committed packet — rerun npm run build-heap-sat`);
    }
  }
  if (rebuilt.specialisedBreak.statistic !== packet.specialisedBreak.statistic) {
    errors.push("rebuild cross-check: specialisedBreak.statistic disagrees — rerun npm run build-heap-sat");
  }
  notes.push("sibling union present: full rebuild cross-check ran");
} else {
  notes.push("sibling SanskritLexicography checkout absent: internal-consistency checks only (expected on CI)");
}

for (const note of notes) console.log(`note: ${note}`);
if (errors.length > 0) {
  console.error(`validate-heap-sat: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-heap-sat: OK");
