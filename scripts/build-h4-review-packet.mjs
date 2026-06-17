// Build a compact H4 semantic-field review sample packet.
//
// This generator turns the documented H4 review plan into stable machine-only
// rows. It records no human decisions and does not use corpus, DCS, public-page,
// backend/runtime, parser, source-anchor, or standards work.
//
// Usage: npm run build-h4-review-packet

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseCsv } from "./build-h5-anomaly-review.mjs";
import { dictExists, iterateDict } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { slp1_form_key } from "../src/lib/sanskrit-util.js";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-h4-review-packet";
const SEMANTIC_FIELDS_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "semantic-fields.json");
const FAMILY_PROFILES_PATH = path.resolve(process.cwd(), "data", "lexico", "semantic_field_family_profiles.json");
const SEMANTIC_ROWS_PATH = path.resolve(process.cwd(), "data", "lexico", "semantic_fields.csv");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "h4_semantic_field_review_packet.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md");

const SOURCE_FILES = Object.freeze([
  "src/data/dicts/semantic-fields.json",
  "data/lexico/semantic_field_family_profiles.json",
  "data/lexico/semantic_fields.csv",
  "data/lexico/semantic_field_coverage.csv",
  "scripts/build-semantic-fields.mjs",
  "scripts/build-h4-family-profiles.mjs",
  "scripts/build-h4-review-packet.mjs"
]);

export const EXPECTED_H4_SAMPLE_COUNTS = Object.freeze({
  "skd-false-low": 25,
  "vcp-high-coverage": 20,
  "ap-ap90-delta": 20,
  "specialized-baseline": 20,
  "index-reverse-control": 20
});

export const H4_MACHINE_LABEL_VOCABULARY = Object.freeze([
  {
    label: "false-low-risk",
    sampleType: "skd-false-low",
    meaning: "Strict SKD headword coverage may undercount prose, citation, or variant-headword evidence."
  },
  {
    label: "high-coverage-check",
    sampleType: "vcp-high-coverage",
    meaning: "VCP high AMAR coverage should be checked as exposed, usable headword coverage."
  },
  {
    label: "edition-delta-check",
    sampleType: "ap-ap90-delta",
    meaning: "AP/AP90 deltas need edition, parser, and normalization separation."
  },
  {
    label: "scope-baseline-check",
    sampleType: "specialized-baseline",
    meaning: "Specialized dictionaries should be judged against their own topic scope."
  },
  {
    label: "direction-index-control",
    sampleType: "index-reverse-control",
    meaning: "Reverse-bilingual and index works are controls for lookup direction and genre."
  }
]);

const DECISION_LABELS = Object.freeze({
  "skd-false-low": ["true-low", "variant-headword", "prose-present", "parser-gap"],
  "vcp-high-coverage": ["true-covered", "thin-entry", "normalization-risk"],
  "ap-ap90-delta": ["edition-delta", "parser-gap", "normalization-risk", "true-delta"],
  "specialized-baseline": ["scope-match", "incidental-match", "scope-mismatch"],
  "index-reverse-control": ["direction-artifact", "index-artifact", "meaningful-exception"]
});

const SAMPLE_LABELS = Object.freeze({
  "skd-false-low": "H4-R1 SKD false-low",
  "vcp-high-coverage": "H4-R2 VCP high coverage",
  "ap-ap90-delta": "H4-R3 AP/AP90 delta",
  "specialized-baseline": "H4-R4 specialized baseline",
  "index-reverse-control": "H4-R5 index/reverse controls"
});

const SAMPLE_QUESTIONS = Object.freeze({
  "skd-false-low": row => `Is ${row.dictionary.code.toUpperCase()} missing AMAR lemma ${row.lemma} in ${row.field.varga}, or is it present under a variant headword, prose passage, or parser-missed source form?`,
  "vcp-high-coverage": row => `Does the ${row.dictionary.code.toUpperCase()} headword ${row.lemma} represent real usable coverage for AMAR field ${row.field.varga}, or is it thin or normalization-sensitive?`,
  "ap-ap90-delta": row => `Why does ${row.lemma} appear in AP coverage but not AP90 coverage for ${row.field.varga}: edition history, parser gap, normalization risk, or true delta?`,
  "specialized-baseline": row => `Does ${row.dictionary.code.toUpperCase()} coverage of ${row.lemma} in ${row.field.varga} match the dictionary scope, or is it incidental or out of scope?`,
  "index-reverse-control": row => `Is ${row.dictionary.code.toUpperCase()} coverage of ${row.lemma} in ${row.field.varga} meaningful, or a lookup-direction/index artifact?`
});

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort(([a], [b]) => a.localeCompare(b)));
}

function compactText(value, length = 260) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1)}...` : text;
}

function norm(value) {
  return normalizeLemma(value ?? "").normalized;
}

function keyFor(code, lemma) {
  return `${String(code).toLowerCase()}:${norm(lemma)}`;
}

function labelForField(field) {
  return field.upavarga ? `${field.varga} / ${field.upavarga}` : field.varga;
}

function fieldsByKey(data) {
  return new Map(data.fields.map(field => [field.fieldKey, field]));
}

function dictionariesByCode(data) {
  return new Map(data.dictionaries.map(dict => [dict.code, dict]));
}

function coverageByCodeAndField(data) {
  return new Map(data.coverage.map(row => [`${row.code}\u0000${row.fieldKey}`, row]));
}

function coverageFor(coverageIndex, code, fieldKey) {
  return coverageIndex.get(`${code}\u0000${fieldKey}`);
}

function familyProfile(profiles, family) {
  return profiles.familyProfiles.find(profile => profile.family === family);
}

function semanticRowIndex(rows) {
  const index = new Map();
  for (const row of rows) {
    index.set(`${row.field_key}\u0000${row.lemma}`, row);
  }
  return index;
}

function compactField(field) {
  return {
    fieldKey: field.fieldKey,
    fieldOrder: field.fieldOrder,
    kanda: field.kanda,
    varga: field.varga,
    upavarga: field.upavarga,
    label: labelForField(field),
    amarLemmas: field.amarLemmas
  };
}

function compactDictionary(dict) {
  return {
    code: dict.code,
    label: dict.label,
    familyLabel: dict.familyLabel,
    coveragePct: dict.coveragePct
  };
}

function compactCoverage(row) {
  return {
    dictionary: row.code,
    fieldKey: row.fieldKey,
    coveredLemmas: row.coveredLemmas,
    amarLemmas: row.amarLemmas,
    coveragePct: row.coveragePct
  };
}

function lemmaMeta(semanticRows, fieldKey, lemma) {
  const row = semanticRows.get(`${fieldKey}\u0000${lemma}`);
  return {
    slp1: lemma,
    rawForms: row?.raw_forms ? row.raw_forms.split("|").filter(Boolean) : [],
    genders: row?.genders ? row.genders.split("|").filter(Boolean) : [],
    firstAmarL: row?.first_amar_L ? Number(row.first_amar_L) : null,
    firstEid: row?.first_eid ? Number(row.first_eid) : null,
    occurrences: row?.occurrences ? Number(row.occurrences) : null
  };
}

function addUniqueCandidate(out, seen, candidate) {
  const key = `${candidate.sampleType}\u0000${candidate.dictionaryCode}\u0000${candidate.lemma}`;
  if (seen.has(key)) return;
  seen.add(key);
  out.push(candidate);
}

function candidatesFromFields({
  data,
  coverageIndex,
  fields,
  dictionaryCode,
  sampleType,
  exampleKey,
  seen = new Set()
}) {
  const out = [];
  for (const field of fields) {
    const coverage = coverageFor(coverageIndex, dictionaryCode, field.fieldKey);
    for (const lemma of coverage?.[exampleKey] ?? []) {
      addUniqueCandidate(out, seen, {
        sampleType,
        dictionaryCode,
        fieldKey: field.fieldKey,
        lemma,
        machineState: exampleKey === "coveredExamples" ? "covered" : "missing"
      });
    }
  }
  return out;
}

function takeCandidates(candidates, limit, sampleType) {
  const selected = candidates.slice(0, limit);
  if (selected.length !== limit) {
    throw new Error(`${sampleType}: expected ${limit} candidates, got ${selected.length}`);
  }
  return selected;
}

function roundRobin(candidateLists, limit, sampleType) {
  const out = [];
  const seen = new Set();
  let madeProgress = true;
  while (out.length < limit && madeProgress) {
    madeProgress = false;
    for (const list of candidateLists) {
      while (list.index < list.rows.length) {
        const candidate = list.rows[list.index++];
        const key = `${candidate.dictionaryCode}\u0000${candidate.fieldKey}\u0000${candidate.lemma}`;
        if (seen.has(key)) continue;
        seen.add(key);
        out.push(candidate);
        madeProgress = true;
        break;
      }
      if (out.length === limit) break;
    }
  }
  if (out.length !== limit) {
    throw new Error(`${sampleType}: expected ${limit} candidates, got ${out.length}`);
  }
  return out;
}

function selectSkdFalseLow(data, profiles, coverageIndex) {
  const profile = familyProfile(profiles, "indigenous-prose");
  return takeCandidates(candidatesFromFields({
    data,
    coverageIndex,
    fields: profile.lowFields,
    dictionaryCode: "skd",
    sampleType: "skd-false-low",
    exampleKey: "missingExamples"
  }), EXPECTED_H4_SAMPLE_COUNTS["skd-false-low"], "skd-false-low");
}

function selectVcpHighCoverage(data, profiles, coverageIndex) {
  const profile = familyProfile(profiles, "indigenous-prose");
  return takeCandidates(candidatesFromFields({
    data,
    coverageIndex,
    fields: profile.topFields,
    dictionaryCode: "vcp",
    sampleType: "vcp-high-coverage",
    exampleKey: "coveredExamples"
  }), EXPECTED_H4_SAMPLE_COUNTS["vcp-high-coverage"], "vcp-high-coverage");
}

function selectApDelta(data, coverageIndex) {
  const candidates = [];
  const seen = new Set();
  for (const field of data.fields) {
    const ap = coverageFor(coverageIndex, "ap", field.fieldKey);
    const ap90 = coverageFor(coverageIndex, "ap90", field.fieldKey);
    const ap90Missing = new Set(ap90?.missingExamples ?? []);
    for (const lemma of ap?.coveredExamples ?? []) {
      if (!ap90Missing.has(lemma)) continue;
      addUniqueCandidate(candidates, seen, {
        sampleType: "ap-ap90-delta",
        dictionaryCode: "ap",
        comparisonDictionaryCode: "ap90",
        fieldKey: field.fieldKey,
        lemma,
        machineState: "delta",
        coverageDeltaPct: Number(((ap.coveragePct ?? 0) - (ap90.coveragePct ?? 0)).toFixed(4))
      });
    }
  }
  candidates.sort((a, b) =>
    b.coverageDeltaPct - a.coverageDeltaPct ||
    a.fieldKey.localeCompare(b.fieldKey) ||
    a.lemma.localeCompare(b.lemma)
  );
  return takeCandidates(candidates, EXPECTED_H4_SAMPLE_COUNTS["ap-ap90-delta"], "ap-ap90-delta");
}

function specializedFieldsFor(data, profiles, code) {
  const dict = data.dictionaries.find(row => row.code === code);
  const profile = familyProfile(profiles, "specialized");
  const top = (dict.topFields ?? []).slice(0, 2).map(row => ({ fieldKey: row.fieldKey }));
  const weak = (profile.lowFields ?? []).find(field => coverageFor(coverageByCodeAndField(data), code, field.fieldKey)?.coveredExamples?.length);
  return [...top, ...(weak ? [weak] : [])];
}

function selectSpecializedBaseline(data, profiles, coverageIndex) {
  const lists = ["armh", "fri", "bhs"].map(code => ({
    index: 0,
    rows: candidatesFromFields({
      data,
      coverageIndex,
      fields: specializedFieldsFor(data, profiles, code),
      dictionaryCode: code,
      sampleType: "specialized-baseline",
      exampleKey: "coveredExamples"
    })
  }));
  return roundRobin(lists, EXPECTED_H4_SAMPLE_COUNTS["specialized-baseline"], "specialized-baseline");
}

function selectIndexReverseControls(data, coverageIndex) {
  const lists = ["ae", "mwe", "pui", "inm", "ieg"].map(code => {
    const dict = data.dictionaries.find(row => row.code === code);
    return {
      index: 0,
      rows: candidatesFromFields({
        data,
        coverageIndex,
        fields: (dict.topFields ?? []).slice(0, 3),
        dictionaryCode: code,
        sampleType: "index-reverse-control",
        exampleKey: "coveredExamples"
      })
    };
  });
  return roundRobin(lists, EXPECTED_H4_SAMPLE_COUNTS["index-reverse-control"], "index-reverse-control");
}

function selectCandidates(data, profiles, coverageIndex) {
  return [
    ...selectSkdFalseLow(data, profiles, coverageIndex),
    ...selectVcpHighCoverage(data, profiles, coverageIndex),
    ...selectApDelta(data, coverageIndex),
    ...selectSpecializedBaseline(data, profiles, coverageIndex),
    ...selectIndexReverseControls(data, coverageIndex)
  ];
}

function sourcePointerKey(pointer) {
  return [
    pointer.role,
    String(pointer.dictionary ?? "").toLowerCase(),
    norm(pointer.lemma ?? pointer.form ?? ""),
    String(pointer.L ?? "")
  ].join("\u0000");
}

export function preservedSourcePointerMap(packet) {
  const preserved = new Map();
  for (const row of packet.sampleRows ?? []) {
    preserved.set(row.reviewId, new Map((row.sourcePointers ?? [])
      .filter(pointer => pointer.href)
      .map(pointer => [sourcePointerKey(pointer), pointer])));
  }
  return preserved;
}

function loadPreservedSourcePointers(outputPath) {
  if (!fs.existsSync(outputPath)) return new Map();
  try {
    return preservedSourcePointerMap(JSON.parse(fs.readFileSync(outputPath, "utf8")));
  } catch {
    return new Map();
  }
}

function collectNeededLemmas(candidates) {
  const needed = new Map();
  function add(code, lemma) {
    if (!code || !lemma) return;
    const normalizedCode = String(code).toLowerCase();
    if (!needed.has(normalizedCode)) needed.set(normalizedCode, new Set());
    needed.get(normalizedCode).add(norm(lemma));
  }
  for (const candidate of candidates) {
    add(candidate.dictionaryCode, candidate.lemma);
    add(candidate.comparisonDictionaryCode, candidate.lemma);
  }
  return needed;
}

function buildSourceIndex(needed) {
  const index = new Map();
  for (const [code, lemmas] of needed) {
    if (!dictExists(code)) continue;
    for (const rec of iterateDict(code)) {
      const key = keyFor(code, rec.k1);
      if (!lemmas.has(norm(rec.k1))) continue;
      if (!index.has(key)) {
        index.set(key, {
          role: "exact-dictionary-headword",
          dictionary: code.toUpperCase(),
          lemma: rec.k1,
          L: rec.L ?? null,
          line: rec.startLine,
          href: rec.href,
          bodyExcerpt: compactText(rec.body)
        });
      }
    }
  }
  return index;
}

function pointerFromSource(index, preserved, reviewId, code, lemma, role) {
  const fresh = index.get(keyFor(code, lemma));
  const pointer = fresh ? { ...fresh, role, dictionary: code.toUpperCase(), lemma } : null;
  if (pointer) return pointer;
  const preservedForRow = preserved.get(reviewId);
  if (!preservedForRow) return null;
  const preservedKeyPrefix = `${role}\u0000${String(code).toLowerCase()}\u0000${norm(lemma)}`;
  return [...preservedForRow.entries()].find(([key]) => key.startsWith(preservedKeyPrefix))?.[1] ?? null;
}

function baseSourcePointers(row) {
  return [
    {
      role: "amar-field-lemma",
      sourceFile: "data/lexico/semantic_fields.csv",
      fieldKey: row.field.fieldKey,
      lemma: row.lemma,
      firstAmarL: row.lemmaMeta.firstAmarL,
      firstEid: row.lemmaMeta.firstEid
    },
    {
      role: "semantic-coverage-row",
      sourceFile: "data/lexico/semantic_field_coverage.csv",
      dictionary: row.dictionary.code.toUpperCase(),
      fieldKey: row.field.fieldKey,
      machineState: row.machineState,
      coveredLemmas: row.coverage.coveredLemmas,
      amarLemmas: row.coverage.amarLemmas,
      coveragePct: row.coverage.coveragePct
    }
  ];
}

function reviewIdFor(candidate, rank, field) {
  return `h4-${candidate.sampleType}:${candidate.dictionaryCode}:${String(rank).padStart(2, "0")}:${field.varga}:${candidate.lemma}`;
}

function buildSampleRows(data, profiles, semanticRows, preservedSourcePointers) {
  const fieldIndex = fieldsByKey(data);
  const dictIndex = dictionariesByCode(data);
  const coverageIndex = coverageByCodeAndField(data);
  const candidates = selectCandidates(data, profiles, coverageIndex);
  const sourceIndex = buildSourceIndex(collectNeededLemmas(candidates));
  const ranksByType = new Map();

  return candidates.map(candidate => {
    const rank = (ranksByType.get(candidate.sampleType) ?? 0) + 1;
    ranksByType.set(candidate.sampleType, rank);
    const field = compactField(fieldIndex.get(candidate.fieldKey));
    const dictionary = compactDictionary(dictIndex.get(candidate.dictionaryCode));
    const comparisonDictionary = candidate.comparisonDictionaryCode
      ? compactDictionary(dictIndex.get(candidate.comparisonDictionaryCode))
      : null;
    const coverage = compactCoverage(coverageFor(coverageIndex, candidate.dictionaryCode, candidate.fieldKey));
    const comparisonCoverage = candidate.comparisonDictionaryCode
      ? compactCoverage(coverageFor(coverageIndex, candidate.comparisonDictionaryCode, candidate.fieldKey))
      : null;
    const reviewId = reviewIdFor(candidate, rank, field);
    const proposedLabel = H4_MACHINE_LABEL_VOCABULARY.find(row => row.sampleType === candidate.sampleType).label;
    const row = {
      reviewId,
      rank,
      sampleType: candidate.sampleType,
      sampleLabel: SAMPLE_LABELS[candidate.sampleType],
      dictionary,
      comparisonDictionary,
      field,
      lemma: candidate.lemma,
      lemmaMeta: lemmaMeta(semanticRows, candidate.fieldKey, candidate.lemma),
      machineState: candidate.machineState,
      proposedLabel,
      expectedDecisionLabels: DECISION_LABELS[candidate.sampleType],
      coverage,
      comparisonCoverage,
      coverageDeltaPct: candidate.coverageDeltaPct ?? null,
      reviewQuestion: SAMPLE_QUESTIONS[candidate.sampleType]({
        dictionary,
        comparisonDictionary,
        field,
        lemma: candidate.lemma
      }),
      reviewStatus: "needs-review",
      reviewedValue: null,
      reviewer: "",
      reviewedAt: "",
      note: ""
    };
    const primaryRole = candidate.machineState === "missing"
      ? "candidate-dictionary-headword"
      : "exact-dictionary-headword";
    const primaryPointer = pointerFromSource(sourceIndex, preservedSourcePointers, reviewId, candidate.dictionaryCode, candidate.lemma, primaryRole);
    const comparisonPointer = candidate.comparisonDictionaryCode
      ? pointerFromSource(sourceIndex, preservedSourcePointers, reviewId, candidate.comparisonDictionaryCode, candidate.lemma, "comparison-dictionary-headword")
      : null;
    row.sourcePointers = [
      ...baseSourcePointers(row),
      ...(primaryPointer ? [primaryPointer] : []),
      ...(comparisonPointer ? [comparisonPointer] : [])
    ];
    return row;
  });
}

function validatePayload(payload) {
  const errors = [];
  const machineLabels = new Set(H4_MACHINE_LABEL_VOCABULARY.map(row => row.label));
  const decisionLabels = new Set(Object.values(DECISION_LABELS).flat());
  const expectedTotal = Object.values(EXPECTED_H4_SAMPLE_COUNTS).reduce((sum, value) => sum + value, 0);
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (payload.generatedBy !== GENERATED_BY) errors.push(`generatedBy must be ${GENERATED_BY}`);
  if (payload.counts.sampleRows !== expectedTotal) errors.push(`expected ${expectedTotal} sample rows, got ${payload.counts.sampleRows}`);
  for (const [sampleType, count] of Object.entries(EXPECTED_H4_SAMPLE_COUNTS)) {
    if (payload.counts.bySampleType[sampleType] !== count) {
      errors.push(`${sampleType}: expected ${count} rows, got ${payload.counts.bySampleType[sampleType] ?? 0}`);
    }
  }
  const ids = new Set();
  for (const row of payload.sampleRows) {
    if (ids.has(row.reviewId)) errors.push(`${row.reviewId}: duplicate reviewId`);
    ids.add(row.reviewId);
    if (!machineLabels.has(row.proposedLabel)) errors.push(`${row.reviewId}: unknown proposedLabel ${row.proposedLabel}`);
    for (const label of row.expectedDecisionLabels ?? []) {
      if (!decisionLabels.has(label)) errors.push(`${row.reviewId}: unknown decision label ${label}`);
    }
    if (!row.sourcePointers?.length) errors.push(`${row.reviewId}: missing sourcePointers`);
    if (!row.reviewQuestion) errors.push(`${row.reviewId}: missing reviewQuestion`);
    const autoResolved = row.autoTriage?.resolved === true;
    if (row.reviewStatus !== "needs-review" && row.reviewStatus !== "auto-resolved") {
      errors.push(`${row.reviewId}: reviewStatus must be needs-review or auto-resolved`);
    }
    if (autoResolved !== (row.reviewStatus === "auto-resolved")) {
      errors.push(`${row.reviewId}: reviewStatus/autoTriage.resolved disagree`);
    }
    if (autoResolved && !(row.expectedDecisionLabels ?? []).includes(row.autoTriage.proposedDecision)) {
      errors.push(`${row.reviewId}: auto-resolved decision ${row.autoTriage.proposedDecision} not in vocabulary`);
    }
    if (row.reviewedValue !== null) errors.push(`${row.reviewId}: reviewedValue must be null`);
    if (row.reviewer !== "" || row.reviewedAt !== "" || row.note !== "") {
      errors.push(`${row.reviewId}: human fields must remain empty`);
    }
  }
  if (errors.length) {
    throw new Error(`H4 review packet build failed with ${errors.length} error(s):\n${errors.map(error => `  - ${error}`).join("\n")}`);
  }
}

// Deterministic auto-triage: a `missing` row is mechanically explained when the
// AMAR lemma IS present in the dictionary under a looser headword fold
// (slp1_form_key folds the gender suffix / accent / visarga / final homonym
// digit that the strict key keeps). Such a row is a `variant-headword`, not a
// genuine gap — auto-resolve it (recording the matched headword as evidence) so
// the reviewer only works the rows that aren't mechanically explainable. Rows
// stay in the packet with reviewStatus "auto-resolved" so a human can audit or
// override; nothing here is written to csl-orig. Only fires when the proposed
// decision is in that sample type's vocabulary.
const AUTO_TRIAGE_DECISION = { "skd-false-low": "variant-headword" };

export function applyAutoTriage(rows, iterate = iterateDict, exists = dictExists) {
  const codes = new Set(
    rows.filter(row => AUTO_TRIAGE_DECISION[row.sampleType] && row.machineState === "missing")
      .map(row => row.dictionary.code)
  );
  const foldIndex = new Map(); // code -> Map<foldKey, headword>
  for (const code of codes) {
    const m = new Map();
    if (exists(code)) {
      for (const rec of iterate(code)) {
        if (!rec.k1) continue;
        const fk = slp1_form_key(rec.k1);
        if (!m.has(fk)) m.set(fk, rec.k1);
      }
    }
    foldIndex.set(code, m);
  }
  for (const row of rows) {
    const decision = AUTO_TRIAGE_DECISION[row.sampleType];
    const eligible = decision && row.machineState === "missing"
      && (row.expectedDecisionLabels ?? []).includes(decision);
    const matched = eligible ? foldIndex.get(row.dictionary.code)?.get(slp1_form_key(row.lemma)) : null;
    if (matched && norm(matched) !== norm(row.lemma)) {
      row.autoTriage = {
        resolved: true,
        proposedDecision: decision,
        basis: "loose-fold-headword-match",
        evidence: { matchedHeadword: matched, foldKey: slp1_form_key(row.lemma) }
      };
      row.reviewStatus = "auto-resolved";
    } else {
      row.autoTriage = { resolved: false };
    }
  }
  return rows;
}

export function buildPayload(
  semanticData,
  familyProfiles,
  semanticFieldRows,
  generatedAt = new Date().toISOString(),
  preservedSourcePointers = new Map()
) {
  const semanticRows = semanticRowIndex(semanticFieldRows);
  const sampleRows = applyAutoTriage(buildSampleRows(semanticData, familyProfiles, semanticRows, preservedSourcePointers));
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "h4-semantic-field-review-packet",
    claim: "H4-FIELD-FAMILY: AMAR field profiles differ by dictionary family, not only by gross coverage.",
    evidenceLabel: "machine-review-sample",
    reviewStatus: "needs-human-review",
    ownerRepo: "csl-atlas",
    generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: SOURCE_FILES,
    outputs: [
      "data/lexico/h4_semantic_field_review_packet.json",
      "docs/H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md"
    ],
    counts: {
      sampleRows: sampleRows.length,
      autoResolved: sampleRows.filter(row => row.autoTriage?.resolved).length,
      needsHumanReview: sampleRows.filter(row => !row.autoTriage?.resolved).length,
      byAutoDecision: countBy(sampleRows.filter(row => row.autoTriage?.resolved), row => row.autoTriage.proposedDecision),
      bySampleType: countBy(sampleRows, row => row.sampleType),
      byProposedLabel: countBy(sampleRows, row => row.proposedLabel),
      byDictionary: countBy(sampleRows, row => row.dictionary.code),
      sourcePointers: sampleRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      exactDictionaryPointers: sampleRows.reduce((sum, row) => sum + row.sourcePointers.filter(pointer => pointer.href).length, 0),
      familyProfiles: familyProfiles.counts.familyCount,
      fieldContrasts: familyProfiles.counts.fieldContrasts,
      dictionaryCount: semanticData.counts.dictionaryRows,
      fieldCount: semanticData.counts.fieldCount
    },
    labelVocabulary: H4_MACHINE_LABEL_VOCABULARY,
    decisionVocabulary: DECISION_LABELS,
    method: [
      "Select SKD missing examples from indigenous-prose low fields for false-low review.",
      "Select VCP covered examples from indigenous-prose high fields for high-coverage review.",
      "Select AP covered examples that AP90 marks missing to isolate edition/parser/normalization deltas.",
      "Round-robin ARMH, FRI, and BHS examples from strong fields plus weak-field controls for specialized baselines.",
      "Round-robin AE, MWE, and index-family non-zero examples as lookup-direction and index controls."
    ],
    sampleRows,
    limitations: [
      "Rows are machine-selected review prompts, not human decisions.",
      "Strict AMAR headword coverage is not sense coverage, citation coverage, prose coverage, corpus frequency, or passage attestation.",
      "Missing rows may still be present under variant headwords, prose, or citation wording.",
      "Covered rows still need source review before paper-level topical claims."
    ],
    boundaryNote: "Atlas H4 artifacts only; no corpus/DCS evidence, public page update, parser promotion, source-anchor generation, R2/H5 row change, backend/runtime LLM work, or standards work is included.",
    warnings: []
  };
  validatePayload(payload);
  return payload;
}

function mdCell(value) {
  return String(value ?? "")
    .replace(/\r?\n/g, " ")
    .replace(/\|/g, "\\|")
    .trim();
}

function pointerSummary(row) {
  const exact = row.sourcePointers.find(pointer => pointer.href);
  if (exact) return `[${exact.dictionary} L=${exact.L}](${exact.href})`;
  const coverage = row.sourcePointers.find(pointer => pointer.role === "semantic-coverage-row");
  return `${coverage.dictionary} coverage row`;
}

function pct(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

export function buildMarkdown(packet) {
  const lines = [];
  lines.push("# H4 Semantic-Field Review Samples");
  lines.push("");
  lines.push(`Date: ${packet.generatedAt.slice(0, 10)}`);
  lines.push("");
  lines.push(`Status: generated machine-only H4 review worksheet. ${packet.counts.autoResolved} of ${packet.counts.sampleRows} rows are deterministically auto-resolved (\`variant-headword\` — the lemma is present in the dictionary under a loose-fold headword match, evidence in \`autoTriage.evidence.matchedHeadword\`); ${packet.counts.needsHumanReview} still need human review. No human decisions are recorded here, and auto-resolved rows can be audited or overridden.`);
  lines.push("");
  lines.push("## Trust Block");
  lines.push("");
  lines.push(`- Evidence: ${packet.sourceFiles.map(file => `\`${file}\``).join(", ")}.`);
  lines.push(`- Validation: \`${packet.generatedBy}\`, \`npm test\`, \`npm run validate-review-reports\`, and \`npm run build\`.`);
  lines.push("- Owner repo: `csl-atlas`.");
  lines.push("- Next use: source-check these rows before H4 semantic-field contrasts become paper-level claims.");
  lines.push(`- Boundary note: ${packet.boundaryNote}`);
  lines.push("");
  lines.push("## Counts");
  lines.push("");
  lines.push("| Metric | Count |");
  lines.push("|---|---:|");
  lines.push(`| Sample rows | ${packet.counts.sampleRows} |`);
  lines.push(`| Auto-resolved (variant-headword) | ${packet.counts.autoResolved} |`);
  lines.push(`| Needs human review | ${packet.counts.needsHumanReview} |`);
  lines.push(`| Source pointers | ${packet.counts.sourcePointers} |`);
  lines.push(`| Exact dictionary pointers | ${packet.counts.exactDictionaryPointers} |`);
  lines.push(`| Family profiles | ${packet.counts.familyProfiles} |`);
  lines.push(`| Field contrasts | ${packet.counts.fieldContrasts} |`);
  lines.push("");
  lines.push("## Sample Groups");
  lines.push("");
  lines.push("| Sample type | Rows | Machine label | Decision labels |");
  lines.push("|---|---:|---|---|");
  for (const label of packet.labelVocabulary) {
    lines.push(`| \`${label.sampleType}\` | ${packet.counts.bySampleType[label.sampleType]} | \`${label.label}\` | ${packet.decisionVocabulary[label.sampleType].map(value => `\`${value}\``).join(", ")} |`);
  }
  lines.push("");
  for (const sampleType of Object.keys(EXPECTED_H4_SAMPLE_COUNTS)) {
    const rows = packet.sampleRows.filter(row => row.sampleType === sampleType);
    lines.push(`## ${SAMPLE_LABELS[sampleType]}`);
    lines.push("");
    lines.push("| Review ID | Dict | Field | Lemma | Coverage | Label | Source | Review question |");
    lines.push("|---|---|---|---|---:|---|---|---|");
    for (const row of rows) {
      const coverage = row.coverageDeltaPct == null ? pct(row.coverage.coveragePct) : `${pct(row.coverage.coveragePct)} / ${pct(row.comparisonCoverage.coveragePct)}`;
      lines.push(`| ${[
        `\`${mdCell(row.reviewId)}\``,
        mdCell(row.comparisonDictionary ? `${row.dictionary.label}/${row.comparisonDictionary.label}` : row.dictionary.label),
        mdCell(row.field.label),
        `\`${mdCell(row.lemma)}\``,
        coverage,
        `\`${row.proposedLabel}\``,
        mdCell(pointerSummary(row)),
        mdCell(row.reviewQuestion)
      ].join(" | ")} |`);
    }
    lines.push("");
  }
  lines.push("## Human Fields");
  lines.push("");
  lines.push("Every row keeps `reviewedValue = null`, `reviewer = \"\"`, `reviewedAt = \"\"`, and `note = \"\"`. Review decisions are outside this generated packet.");
  lines.push("");
  lines.push("## Limitations");
  lines.push("");
  for (const limitation of packet.limitations) lines.push(`- ${limitation}`);
  lines.push("");
  lines.push("Archive/corpus parity is not an H4 optimization target; H4 remains dictionary-first and AMAR-native until a separate corpus-facing question is opened.");
  lines.push("");
  return `${lines.join("\n")}\n`;
}

function main() {
  const semanticData = JSON.parse(fs.readFileSync(SEMANTIC_FIELDS_PATH, "utf8"));
  const familyProfiles = JSON.parse(fs.readFileSync(FAMILY_PROFILES_PATH, "utf8"));
  const semanticRows = parseCsv(fs.readFileSync(SEMANTIC_ROWS_PATH, "utf8"));
  const preserved = loadPreservedSourcePointers(JSON_OUT);
  const payload = buildPayload(semanticData, familyProfiles, semanticRows, new Date().toISOString(), preserved);
  const markdown = buildMarkdown(payload);
  fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
  fs.mkdirSync(path.dirname(MARKDOWN_OUT), { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  fs.writeFileSync(MARKDOWN_OUT, markdown);
  console.log(`Wrote ${path.relative(process.cwd(), JSON_OUT)} (${payload.counts.sampleRows} H4 review rows).`);
  console.log(`Wrote ${path.relative(process.cwd(), MARKDOWN_OUT)}.`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
