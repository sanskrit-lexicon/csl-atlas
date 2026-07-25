// Validate the committed period-signatures packet (H1576, PH3).
//
// CI-safe: internal-consistency checks run from the committed JSON alone; the
// full rebuild cross-check against the sibling SanskritLexicography union and
// kosha frequency release runs only when both checkouts are present (they are
// not on CI runners).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - the period vocabulary drifts from kosha's canonical period_order;
// - a dictionary's typeShare doesn't sum to ~1, its modalCounts don't sum to
//   its matched count, or matched exceeds lemmas;
// - a bootstrap CI doesn't bracket its mean, or chi-square/effect fields are
//   non-finite where matched > 0;
// - the baseline modalCounts don't sum to the matched-lemma total;
// - the Kruskal-Wallis block loses its descriptive evidence grade (the
//   honesty gate) or its family roster disagrees with perDict;
// - (siblings present) rebuilding from the live inputs disagrees with the
//   committed totals, baseline, or perDict rows.
//
// Usage: npm run validate-period-signatures   (run after build-period-signatures)

import fs from "node:fs";
import path from "node:path";
import { parseTsv } from "./build-heritage-witness.mjs";
import { buildPayload, PERIODS } from "./build-period-signatures.mjs";
import { loadDictionaryInventory } from "./lib/dict-scope.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "period_signatures.json");
const SOURCE_OUT = path.join(OUT_DIR, "period_signatures.source.json");
const SYNCED_COPY = path.resolve(process.cwd(), "src", "data", "lexico", "period_signatures.json");
const SIBLING_LEX = path.resolve(process.cwd(), "..", "SanskritLexicography");
const SIBLING_KOSHA = path.resolve(process.cwd(), "..", "kosha");
const UNION_PATH = path.join(SIBLING_LEX, "HeadwordLists", "union", "union_headwords.tsv");
const FREQ_PATH = path.join(SIBLING_KOSHA, "data", "frequency", "lemma_frequency.tsv");

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
  const canonical = PERIODS.map((p) => p.key);
  const declared = (packet.periods ?? []).map((p) => p.key);
  if (JSON.stringify(declared) !== JSON.stringify(canonical)) {
    errors.push(`period vocabulary drifted from kosha period_order: ${declared}`);
  }
  const nP = canonical.length;

  for (const d of packet.perDict ?? []) {
    if (d.matched > d.lemmas) errors.push(`${d.code}: matched ${d.matched} > lemmas ${d.lemmas}`);
    if (Math.abs(d.matchRate - d.matched / d.lemmas) > 0.0011) errors.push(`${d.code}: matchRate mismatch`);
    const shareSum = (d.typeShare ?? []).reduce((a, v) => a + v, 0);
    if (d.matched > 0 && Math.abs(shareSum - 1) > 0.001) errors.push(`${d.code}: typeShare sums to ${shareSum}, not ~1`);
    if ((d.typeShare ?? []).length !== nP) errors.push(`${d.code}: typeShare length != ${nP}`);
    const modalSum = (d.modalCounts ?? []).reduce((a, v) => a + v, 0);
    if (modalSum !== d.matched) errors.push(`${d.code}: modalCounts sum ${modalSum} != matched ${d.matched}`);
    if (d.matched > 0) {
      for (const field of ["chi2VsUnion", "cramersV", "tvdVsUnion"]) {
        if (!Number.isFinite(d[field])) errors.push(`${d.code}: ${field} is not finite`);
      }
      if (!(d.chi2P >= 0 && d.chi2P <= 1)) errors.push(`${d.code}: chi2P ${d.chi2P} outside [0,1]`);
    }
    if (d.meanChron !== null && d.chronCiLo !== null && d.chronCiHi !== null) {
      if (!(d.chronCiLo <= d.meanChron + 1 && d.meanChron - 1 <= d.chronCiHi)) {
        errors.push(`${d.code}: bootstrap CI [${d.chronCiLo}, ${d.chronCiHi}] does not bracket meanChron ${d.meanChron}`);
      }
    }
  }

  const baseline = packet.baseline ?? {};
  const baseModalSum = (baseline.modalCounts ?? []).reduce((a, v) => a + v, 0);
  if (baseModalSum !== packet.totals?.matchedLemmas) {
    errors.push(`baseline modalCounts sum ${baseModalSum} != totals.matchedLemmas ${packet.totals?.matchedLemmas}`);
  }
  const baseShareSum = (baseline.typeShare ?? []).reduce((a, v) => a + v, 0);
  if (Math.abs(baseShareSum - 1) > 0.001) errors.push(`baseline typeShare sums to ${baseShareSum}, not ~1`);

  const kw = packet.kruskalWallis ?? {};
  if (kw.evidenceGrade !== "descriptive") errors.push("kruskalWallis.evidenceGrade must stay `descriptive` (the honesty gate)");
  const perDictFamilies = new Map();
  for (const d of packet.perDict ?? []) {
    if (d.meanChron === null) continue;
    perDictFamilies.set(d.family, (perDictFamilies.get(d.family) ?? 0) + 1);
  }
  for (const fam of kw.families ?? []) {
    if (perDictFamilies.get(fam.family) !== fam.dictionaries) {
      errors.push(`kruskalWallis family ${fam.family} count ${fam.dictionaries} disagrees with perDict`);
    }
    if (fam.dictionaries < 2) errors.push(`kruskalWallis family ${fam.family} has <2 dictionaries`);
  }
}

if (envelope && packet && envelope.generatedAt !== packet.generatedAt) {
  errors.push(`source envelope generatedAt ${envelope.generatedAt} != packet generatedAt ${packet.generatedAt}`);
}

if (packet && fs.existsSync(SYNCED_COPY)) {
  const synced = readJson(SYNCED_COPY);
  if (synced && JSON.stringify(synced) !== JSON.stringify(packet)) {
    errors.push("src/data/lexico/period_signatures.json (site copy) differs from data/lexico/period_signatures.json — run npm run sync-site-data");
  }
}

if (packet && fs.existsSync(UNION_PATH) && fs.existsSync(FREQ_PATH)) {
  const unionRows = parseTsv(fs.readFileSync(UNION_PATH, "utf8"));
  const freqRows = parseTsv(fs.readFileSync(FREQ_PATH, "utf8"));
  const rebuilt = buildPayload(unionRows, freqRows, loadDictionaryInventory(), { generatedAt: packet.generatedAt });
  for (const key of ["totals", "baseline", "perDict", "kruskalWallis"]) {
    if (JSON.stringify(rebuilt[key]) !== JSON.stringify(packet[key])) {
      errors.push(`rebuild cross-check: ${key} disagrees with the committed packet — rerun npm run build-period-signatures`);
    }
  }
  notes.push("sibling union + kosha present: full rebuild cross-check ran");
} else {
  notes.push("sibling checkouts absent: internal-consistency checks only (expected on CI)");
}

for (const note of notes) console.log(`note: ${note}`);
if (errors.length > 0) {
  console.error(`validate-period-signatures: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-period-signatures: OK");
