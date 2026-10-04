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
import { parseTsv, buildPayload, loadKoshaHeritageRows, koshaRowsToCrosswalkRows } from "./build-heritage-witness.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";

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

  // Kosha witness-anchoring check (H4720 consumer edge): when the sibling
  // kosha checkout is present, verify the committed packet's witness values
  // against kosha's heritage_anchor table — totals can only under-count the
  // kosha raw rows (the normalized fold collapses homonyms), and a
  // deterministic sample of witnessed rows must be reproducible from kosha.
  const kosha = await loadKoshaHeritageRows();
  if (kosha) {
    const koshaCovered = kosha.rows.filter((r) => r.covered).length;
    const koshaAnchored = kosha.rows.filter((r) => r.covered && (r.anchor ?? "") !== "").length;
    if (t.heritageCovered > koshaCovered) {
      errors.push(`kosha totals: packet heritageCovered ${t.heritageCovered} > kosha covered rows ${koshaCovered}`);
    }
    if (t.anchored > koshaAnchored) {
      errors.push(`kosha totals: packet anchored ${t.anchored} > kosha anchor-resolved rows ${koshaAnchored}`);
    }
    const koshaByNorm = new Map(); // normalized mw_key1 -> crosswalk-shaped rows
    for (const r of koshaRowsToCrosswalkRows(kosha.rows)) {
      const { normalized } = normalizeLemma(r.mw_key1);
      if (!normalized) continue;
      if (!koshaByNorm.has(normalized)) koshaByNorm.set(normalized, []);
      koshaByNorm.get(normalized).push(r);
    }
    const witnessed = packet.witnessed ?? [];
    const step = Math.max(1, Math.floor(witnessed.length / 400));
    let sampled = 0;
    for (let i = 0; i < witnessed.length; i += step) {
      sampled += 1;
      const w = witnessed[i];
      const cands = koshaByNorm.get(w.headword) ?? [];
      if (cands.length === 0) {
        errors.push(`kosha sample ${w.headword}: no kosha heritage_anchor row normalizes to this witnessed key`);
        continue;
      }
      if (w.matchTier === "anchored") {
        const hit = cands.some((c) => c.covered_flag === "1" && (c.heritage_entry_anchor ?? "") === w.heritageAnchor);
        if (!hit) {
          errors.push(`kosha sample ${w.headword}: no covered kosha row carries the packet anchor ${w.heritageAnchor}`);
        }
      } else {
        if (!cands.some((c) => c.covered_flag === "1")) {
          errors.push(`kosha sample ${w.headword}: kosha has no covered row but the packet says covered-no-anchor`);
        }
        const stray = cands.find((c) => (c.heritage_entry_anchor ?? "") !== "");
        if (stray) {
          errors.push(`kosha sample ${w.headword}: kosha row ${stray.mw_key1} has an anchor but the packet says covered-no-anchor`);
        }
      }
    }
    notes.push(
      `kosha witness check ran (${sampled} of ${witnessed.length} witnessed rows sampled against ${kosha.rows.length} kosha heritage_anchor rows; kosha raw covered ${koshaCovered}/anchored ${koshaAnchored})`
    );
  } else {
    notes.push("sibling kosha checkout absent — kosha witness-anchoring check skipped (expected on CI)");
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
