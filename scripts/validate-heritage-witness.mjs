// Validate the committed heritage-witness packet (H346).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// cross-check against the sibling SanskritLexicography crosswalk runs only
// when that checkout is present (it is not on CI runners).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - anchored + coveredNoAnchor != heritageCovered, or heritageCovered + absent
//   != mwEntries;
// - coveragePct / anchoredPct disagree with the totals beyond rounding;
// - perInitial rows don't sum to the totals;
// - witnessed.length != heritageCovered, a row's matchTier is invalid, an
//   'anchored' row lacks a heritageAnchor, or a 'covered-no-anchor' row has one;
// - (sibling present) rebuilding from the live MW dict + crosswalk disagrees
//   with the committed totals.
//
// Usage: npm run validate-heritage-witness   (run after build-heritage-witness)

import fs from "node:fs";
import path from "node:path";
import { parseTsv, buildPayload } from "./build-heritage-witness.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "heritage");
const JSON_OUT = path.join(OUT_DIR, "heritage_witness.json");
const SOURCE_OUT = path.join(OUT_DIR, "heritage_witness.source.json");
const CROSSWALK_PATH = path.resolve(process.cwd(), "..", "SanskritLexicography", "HeadwordLists", "mw_heritage_crosswalk.tsv");

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
  const t = packet.totals ?? {};
  if (t.anchored + t.coveredNoAnchor !== t.heritageCovered) {
    errors.push(`totals: anchored ${t.anchored} + coveredNoAnchor ${t.coveredNoAnchor} != heritageCovered ${t.heritageCovered}`);
  }
  if (t.heritageCovered + t.absent !== t.mwEntries) {
    errors.push(`totals: heritageCovered ${t.heritageCovered} + absent ${t.absent} != mwEntries ${t.mwEntries}`);
  }
  const expectedCoverage = t.heritageCovered / t.mwEntries;
  if (Math.abs(expectedCoverage - t.coveragePct) > 0.0011) {
    errors.push(`totals.coveragePct ${t.coveragePct} != heritageCovered/mwEntries (${expectedCoverage.toFixed(4)})`);
  }
  const expectedAnchoredPct = t.anchored / t.mwEntries;
  if (Math.abs(expectedAnchoredPct - t.anchoredPct) > 0.0011) {
    errors.push(`totals.anchoredPct ${t.anchoredPct} != anchored/mwEntries (${expectedAnchoredPct.toFixed(4)})`);
  }

  let sumMw = 0;
  let sumAnchored = 0;
  let sumCoveredNoAnchor = 0;
  for (const row of packet.perInitial ?? []) {
    sumMw += row.mwEntries;
    sumAnchored += row.anchored;
    sumCoveredNoAnchor += row.coveredNoAnchor;
    if (row.anchored + row.coveredNoAnchor > row.mwEntries) {
      errors.push(`perInitial ${row.initial}: anchored ${row.anchored} + coveredNoAnchor ${row.coveredNoAnchor} > mwEntries ${row.mwEntries}`);
    }
  }
  if (sumMw !== t.mwEntries) errors.push(`perInitial mwEntries sum ${sumMw} != totals.mwEntries ${t.mwEntries}`);
  if (sumAnchored !== t.anchored) errors.push(`perInitial anchored sum ${sumAnchored} != totals.anchored ${t.anchored}`);
  if (sumCoveredNoAnchor !== t.coveredNoAnchor) errors.push(`perInitial coveredNoAnchor sum ${sumCoveredNoAnchor} != totals.coveredNoAnchor ${t.coveredNoAnchor}`);

  const witnessed = packet.witnessed ?? [];
  if (witnessed.length !== t.heritageCovered) {
    errors.push(`witnessed.length ${witnessed.length} != totals.heritageCovered ${t.heritageCovered}`);
  }
  let anchoredRows = 0;
  let coveredNoAnchorRows = 0;
  for (const w of witnessed) {
    if (w.matchTier !== "anchored" && w.matchTier !== "covered-no-anchor") {
      errors.push(`witnessed ${w.headword}: bad matchTier ${w.matchTier}`);
      continue;
    }
    if (w.matchTier === "anchored") {
      anchoredRows += 1;
      if (!w.heritageAnchor) errors.push(`witnessed ${w.headword}: anchored row missing heritageAnchor`);
    } else {
      coveredNoAnchorRows += 1;
      if (w.heritageAnchor) errors.push(`witnessed ${w.headword}: covered-no-anchor row has a heritageAnchor`);
    }
    if (!(w.mwLine > 0)) errors.push(`witnessed ${w.headword}: missing mwLine`);
    if (!(w.occurrences > 0)) errors.push(`witnessed ${w.headword}: missing occurrences`);
  }
  if (anchoredRows !== t.anchored) errors.push(`witnessed anchored rows ${anchoredRows} != totals.anchored ${t.anchored}`);
  if (coveredNoAnchorRows !== t.coveredNoAnchor) errors.push(`witnessed covered-no-anchor rows ${coveredNoAnchorRows} != totals.coveredNoAnchor ${t.coveredNoAnchor}`);

  // Sibling cross-check, only when both the MW dict and the crosswalk are present.
  if (dictExists("mw") && fs.existsSync(CROSSWALK_PATH)) {
    const mwRecords = [...iterateDict("mw")];
    const crosswalkRows = parseTsv(fs.readFileSync(CROSSWALK_PATH, "utf8"));
    const rebuilt = buildPayload(mwRecords, crosswalkRows, { generatedAt: packet.generatedAt });
    if (rebuilt.totals.mwEntries !== t.mwEntries) {
      errors.push(`sibling rebuild: mwEntries ${rebuilt.totals.mwEntries} != committed ${t.mwEntries} — rerun npm run build-heritage-witness`);
    }
    if (rebuilt.totals.heritageCovered !== t.heritageCovered) {
      errors.push(`sibling rebuild: heritageCovered ${rebuilt.totals.heritageCovered} != committed ${t.heritageCovered} — rerun npm run build-heritage-witness`);
    }
    notes.push(`sibling cross-check ran (${crosswalkRows.length} crosswalk rows, ${mwRecords.length} MW records)`);
  } else {
    notes.push("sibling SanskritLexicography checkout or MW dict absent — internal-consistency checks only (expected on CI)");
  }
}

if (envelope) {
  if (envelope.dataset !== "heritage_witness") errors.push(`envelope dataset ${envelope.dataset} != heritage_witness`);
  if (!envelope.crosswalkCommit) errors.push("envelope missing crosswalkCommit");
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length > 0) {
  console.error(`validate-heritage-witness FAILED (${errors.length}):`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-heritage-witness OK");
