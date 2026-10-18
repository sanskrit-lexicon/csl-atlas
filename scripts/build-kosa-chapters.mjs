// Build the kośa-chapters packet (H5329, epic E014): one deterministic reshape of
// the committed kośa-macrostructure artifacts (H5328) into per-chapter data for
// the ARMH and ABCH dictionary pages, plus the AMAR comparison table both pages
// render.
//
// Inputs are consumed read-only and are ALL committed in-repo:
//   data/lexico/kosa_model_{amar,abch,armh}_sample.json — schema instances;
//     every division carries its full-text counts (only planned verse-groups
//     are expanded, which this packet never touches).
//   data/lexico/kosa_model_measures.json — whole-text measures (verse-numbering
//     integrity, colophons, set sizes, gender tags and contiguity, ordering
//     devices observed/inferred/absent).
//   data/parse-rules/{abch,armh}.json — CDSL field inventories (record counts,
//     tags, unmapped tags, caveats).
//
// No source corpus is read here: every number on a chapter page traces to one
// of these artifacts, named in the page's Chart Trust Block. AMAR has no
// parse-rules file (its source is the sanskrit-kosha markup, not CDSL v02), so
// its parseRules slot is null by construction, not by detector blindness.
//
// Usage: npm run build-kosa-chapters   (then npm run validate-kosa-chapters)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-kosa-chapters";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "kosa-chapters");
const JSON_OUT = path.join(OUT_DIR, "kosa_chapters.json");
const SOURCE_OUT = path.join(OUT_DIR, "kosa_chapters.source.json");

const INSTANCE_PATHS = {
  AMAR: "data/lexico/kosa_model_amar_sample.json",
  ABCH: "data/lexico/kosa_model_abch_sample.json",
  ARMH: "data/lexico/kosa_model_armh_sample.json",
};
const MEASURES_PATH = "data/lexico/kosa_model_measures.json";
const PARSE_RULES_PATHS = { ABCH: "data/parse-rules/abch.json", ARMH: "data/parse-rules/armh.json" };

const fmtInt = (n) => Number(n).toLocaleString("en-US");
const fmt4 = (n) => Number(n).toFixed(4);

/** Sum one kosha's instance into division rows + totals. Every number below is
 *  copied from the instance's own per-varga counts — nothing is recomputed from
 *  a source corpus here. */
function chapterFromArtifacts(inst, meas, pr, devices) {
  const divisions = inst.kandas.map((k) => ({
    n: k.n,
    label: k.label ?? null,
    labelIast: k.labelIast ?? null,
    labelStatus: k.labelStatus ?? null,
    vargas: k.vargas.map((v) => ({
      label: v.label ?? null,
      labelIast: v.labelIast ?? null,
      sectionType: v.sectionType,
      counts: v.counts,
    })),
  }));

  const totals = { kandas: divisions.length, vargas: 0, verseGroups: 0, sets: 0, members: 0, fullVerses: 0 };
  for (const d of divisions) {
    totals.vargas += d.vargas.length;
    for (const v of d.vargas) {
      totals.verseGroups += v.counts.groups;
      totals.sets += v.counts.sets;
      totals.members += v.counts.members;
      totals.fullVerses += v.counts.fullVerses;
    }
  }

  const grouped = meas.digitizationModel === "grouped";
  const nanartha = meas.nanarthaOrder
    ? {
        headwords: meas.nanarthaOrder.headwords,
        senses: meas.nanarthaOrder.senses,
        series: Array.isArray(meas.nanarthaOrder.series) ? meas.nanarthaOrder.series.length : meas.nanarthaOrder.series,
        violations: meas.nanarthaOrder.violations,
      }
    : null;

  return {
    code: inst.kosha.code,
    identity: {
      title: inst.kosha.title,
      author: inst.kosha.author,
      tradition: inst.kosha.tradition,
      date: inst.kosha.date,
      source: inst.kosha.source,
    },
    digitizationModel: inst.digitizationModel,
    genderMarking: inst.genderMarking,
    parseRules: pr
      ? {
          file: pr.__file,
          schema: pr.schema,
          title: pr.title,
          sourceFile: pr.source_file,
          recordCount: pr.record_count,
          tags: pr.field_inventory,
          unmappedTags: pr.unmapped_tags,
          caveats: pr.caveats,
        }
      : null,
    totals,
    divisions,
    numbering: grouped
      ? {
          scope: meas.verseNumberingScope.scope,
          sectionBoundaries: meas.verseNumberingScope.sectionBoundaries,
          restarts: meas.verseNumberingScope.restarts,
          fullVerseCount: meas.fullVerseCount,
        }
      : null,
    sectionColophons: meas.sectionColophons ?? null,
    setSizes: meas.setSizes ?? null,
    genderTags: meas.genderTags ?? null,
    genderContiguity: meas.genderContiguity ?? null,
    nanartha,
    alphabeticalAdjacency: meas.alphabeticalAdjacency ?? null,
    devices,
  };
}

/** The comparison table both chapter pages render. Each cell is computed from
 *  the loaded artifacts — the only hand-written part is the phrasing. */
function comparisonRows(chapters) {
  const m = (code) => chapters[code];
  const devNote = (code, name) => {
    const d = m(code).devices.find((x) => x.device === name);
    return d ? `${d.evidence}: ${d.note}` : "—";
  };
  const numbering = (code) => {
    const n = m(code).numbering;
    if (!n) return "grouped by the <vn> locator; no numbering below the kāṇḍa";
    return `${n.scope} — ${n.restarts} restart${n.restarts === 1 ? "" : "s"} at ${n.sectionBoundaries} section boundar${n.sectionBoundaries === 1 ? "y" : "ies"}`;
  };
  const colophons = (code) => {
    const c = m(code).sectionColophons;
    if (!c) return "headings present in the markup; colophon openings/closings not measured";
    return `${c.withOpeningAtha}/${c.sections} open with atha, ${c.withClosingIti}/${c.sections} close with iti`;
  };
  const gender = (code) => {
    const g = m(code).genderTags;
    if (!g) return "absent in markup";
    const topTag = Object.entries(g.top)[0];
    return `${g.distinctTags} distinct tags; most common ${topTag[0]} (${fmtInt(topTag[1])})`;
  };
  const contiguity = (code) => {
    const c = m(code).genderContiguity;
    if (!c) return "n/a — no gender tags";
    return `${fmt4(c.contiguousObserved)} observed vs ${fmt4(c.contiguousExpectedUnderPermutation)} under permutation`;
  };
  const alpha = (code) => {
    const a = m(code).alphabeticalAdjacency;
    return `${fmt4(a.nondecreasing)} non-decreasing over ${fmtInt(a.pairs)} pairs`;
  };
  const parse = (code) => {
    const p = m(code).parseRules;
    if (!p) return "n/a — sanskrit-kosha markup, not CDSL v02";
    return fmtInt(p.recordCount);
  };

  return [
    ["Digitization model", (c) => c.digitizationModel],
    ["Records (CDSL <L> entries)", (c) => parse(c.code)],
    ["Verse-groups (numbered verse units)", (c) => fmtInt(c.totals.verseGroups)],
    ["Sets (all kinds)", (c) => (c.setSizes ? fmtInt(c.totals.sets) : "not encoded")],
    ["Members (word forms)", (c) => fmtInt(c.totals.members)],
    ["Full verses", (c) => fmtInt(c.totals.fullVerses)],
    ["Verse numbering", (c) => numbering(c.code)],
    ["Section colophons", (c) => colophons(c.code)],
    ["Set boundaries", (c) => (c.setSizes ? "<eid> annotation (editorial)" : "not encoded — one record per synonym")],
    ["Gender (liṅga) marking", (c) => gender(c.code)],
    ["Homonym section", (c) => devNote(c.code, "homonym-section")],
    ["Gender-run contiguity", (c) => contiguity(c.code)],
    ["Alphabetical adjacency (chance check)", (c) => alpha(c.code)],
  ].map(([aspect, fn]) => ({ aspect, AMAR: fn(m("AMAR")), ABCH: fn(m("ABCH")), ARMH: fn(m("ARMH")) }));
}

export function buildPayload(artifacts, { generatedAt } = {}) {
  const { instances, measures, parseRules } = artifacts;
  const codes = ["AMAR", "ABCH", "ARMH"];
  const koshas = {};
  for (const code of codes) {
    const meas = measures.measures[code];
    const pr = parseRules[code] ? { ...parseRules[code], __file: PARSE_RULES_PATHS[code] } : null;
    koshas[code] = chapterFromArtifacts(instances[code], meas, pr, measures.devices[code]);
  }
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedBy: GENERATED_BY,
    generatedAt: null,
    ...licenseFields(),
    inputs: { instances: INSTANCE_PATHS, measures: MEASURES_PATH, parseRules: PARSE_RULES_PATHS },
    koshas,
    comparison: { rows: comparisonRows(koshas) },
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

export function loadArtifacts() {
  const read = (p) => JSON.parse(fs.readFileSync(path.resolve(process.cwd(), p), "utf8"));
  return {
    instances: Object.fromEntries(Object.entries(INSTANCE_PATHS).map(([c, p]) => [c, read(p)])),
    measures: read(MEASURES_PATH),
    parseRules: Object.fromEntries(Object.entries(PARSE_RULES_PATHS).map(([c, p]) => [c, read(p)])),
  };
}

function main() {
  const payload = buildPayload(loadArtifacts());
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);

  const commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  const envelope = {
    dataset: "kosa_chapters",
    commit,
    inputRevisions: Object.fromEntries(
      ["AMAR", "ABCH", "ARMH"].map((c) => [c, payload.koshas[c].identity.source.revision]),
    ),
    parseRulesGeneratedBy: "scripts/parse_rules/build_parse_rules.py",
    upstreamBuilder: "scripts/lexico/m10_kosa_macrostructure_model.py (H5328)",
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: [...Object.values(INSTANCE_PATHS), MEASURES_PATH, ...Object.values(PARSE_RULES_PATHS), "scripts/build-kosa-chapters.mjs"],
    schemaVersion: SCHEMA_VERSION,
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
  console.log(`wrote ${path.relative(process.cwd(), JSON_OUT)} (${payload.comparison.rows.length} comparison rows)`);
  console.log(`wrote ${path.relative(process.cwd(), SOURCE_OUT)}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
