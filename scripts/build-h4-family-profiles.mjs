// Build the H4 semantic-field family profile artifact.
//
// This is an interpretation aid for the existing AMAR headword-coverage layer:
// it groups dictionaries by atlas family label, ranks fields within each
// family, and records likely convention explanations for high/low clusters.
//
// Usage: npm run build-h4-family-profiles

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const INPUT = path.resolve(process.cwd(), "src", "data", "dicts", "semantic-fields.json");
const OUT = path.resolve(process.cwd(), "data", "lexico", "semantic_field_family_profiles.json");
const TOP_LIMIT = 8;
const CONTRAST_LIMIT = 12;
const DISTINCTIVE_DELTA = 0.08;

const FAMILY_INTERPRETATIONS = {
  "western-tagged": {
    high: "High coverage usually reflects broad Sanskrit headword exposure in general lexica.",
    low: "Low fields are more likely scope, edition, or headword-policy effects than absence of knowledge.",
    family: "General Western dictionaries dominate broad AMAR coverage, but members still diverge by edition and headword policy."
  },
  "indigenous-prose": {
    high: "High coverage reflects exposed headword overlap, especially VCP-style headword presentation.",
    low: "Low coverage can be false-low when kosha material is embedded in prose, citation, or inflected wording rather than exposed as <k1>.",
    family: "Read indigenous coverage through convention: VCP and SKD can differ because their evidence is surfaced differently."
  },
  "index-catalogue": {
    high: "High fields mark catalogue/index scope overlap with AMAR topics, not general dictionary breadth.",
    low: "Low coverage is expected for reference tools whose task is indexing rather than lexical exposition.",
    family: "Indexes and catalogues need a separate baseline; H4 should not rank them as deficient general dictionaries."
  },
  "reverse-bilingual": {
    high: "Any high field is a lookup-direction exception and should be checked before interpretation.",
    low: "Low coverage is mainly an English-to-Sanskrit direction mismatch for a Sanskrit headword test.",
    family: "Reverse dictionaries are included as controls; strict Sanskrit headword coverage undercounts their practical usefulness."
  },
  specialized: {
    high: "High fields usually show topic overlap between the specialized work and the AMAR taxonomy.",
    low: "Low fields usually mean the work's subject scope sits elsewhere, not that the dictionary lacks quality.",
    family: "Specialized dictionaries require domain baselines instead of comparison to MW-style general coverage."
  },
  unknown: {
    high: "Interpret only after assigning the dictionary to a documented family.",
    low: "Interpret only after assigning the dictionary to a documented family.",
    family: "Unknown family rows are kept visible so missing classification is not silently hidden."
  }
};

export function mean(values) {
  const finite = values.filter(value => Number.isFinite(value));
  return finite.length ? finite.reduce((sum, value) => sum + value, 0) / finite.length : 0;
}

export function roundPct(value) {
  return Number(value.toFixed(4));
}

function fieldLabel(row) {
  return row.upavarga ? `${row.varga} / ${row.upavarga}` : row.varga;
}

function byKey(rows, keyFn) {
  const map = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return map;
}

function fieldMetaByKey(fields) {
  return new Map(fields.map(field => [field.fieldKey, field]));
}

function summarizeDictionary(row) {
  return {
    code: row.code,
    label: row.label,
    records: row.records,
    distinctHeadwords: row.distinctHeadwords,
    coveredAmarLemmas: row.coveredAmarLemmas,
    coveragePct: roundPct(row.coveragePct)
  };
}

function summarizeFieldRows(rows, fieldsByKey, globalByField) {
  return [...byKey(rows, row => row.fieldKey).entries()]
    .map(([fieldKey, fieldRows]) => {
      const meta = fieldsByKey.get(fieldKey) || fieldRows[0];
      const nonZero = fieldRows.filter(row => row.coveredLemmas > 0);
      const coverageValues = fieldRows.map(row => row.coveragePct);
      const globalMean = globalByField.get(fieldKey)?.meanCoveragePct ?? 0;
      const meanCoveragePct = mean(coverageValues);
      return {
        fieldKey,
        fieldOrder: meta.fieldOrder,
        kanda: meta.kanda,
        varga: meta.varga,
        upavarga: meta.upavarga,
        label: fieldLabel(meta),
        amarLemmas: meta.amarLemmas,
        dictionaryCount: fieldRows.length,
        dictionariesWithCoverage: nonZero.length,
        coveredLemmasTotal: fieldRows.reduce((sum, row) => sum + row.coveredLemmas, 0),
        meanCoveragePct: roundPct(meanCoveragePct),
        meanNonZeroCoveragePct: roundPct(mean(nonZero.map(row => row.coveragePct))),
        deltaFromGlobalMean: roundPct(meanCoveragePct - globalMean),
        coveredExamples: [...new Set(fieldRows.flatMap(row => row.coveredExamples).filter(Boolean))].slice(0, 8),
        missingExamples: [...new Set(fieldRows.flatMap(row => row.missingExamples).filter(Boolean))].slice(0, 8)
      };
    });
}

export function rankFamilyFields(fieldRows, direction = "high", limit = TOP_LIMIT) {
  const sorted = [...fieldRows].sort((a, b) => {
    const pct = direction === "high"
      ? b.meanCoveragePct - a.meanCoveragePct
      : a.meanCoveragePct - b.meanCoveragePct;
    return pct || b.dictionariesWithCoverage - a.dictionariesWithCoverage || a.fieldOrder - b.fieldOrder;
  });
  return sorted.slice(0, limit);
}

function addInterpretations(fields, text) {
  return fields.map(field => ({ ...field, interpretation: text }));
}

function buildGlobalFieldStats(coverage, fieldsByKey) {
  const stats = new Map();
  for (const [fieldKey, rows] of byKey(coverage, row => row.fieldKey)) {
    const meta = fieldsByKey.get(fieldKey) || rows[0];
    stats.set(fieldKey, {
      fieldKey,
      fieldOrder: meta.fieldOrder,
      label: fieldLabel(meta),
      meanCoveragePct: mean(rows.map(row => row.coveragePct))
    });
  }
  return stats;
}

function buildFamilyProfiles(data, fieldsByKey, globalByField) {
  const dictsByFamily = byKey(data.dictionaries, row => row.familyLabel);
  const coverageByFamily = byKey(data.coverage, row => row.familyLabel);
  const profiles = [];

  for (const family of data.familyLabels) {
    const dictionaries = (dictsByFamily.get(family) || [])
      .sort((a, b) => b.coveragePct - a.coveragePct || a.label.localeCompare(b.label));
    const coverage = coverageByFamily.get(family) || [];
    if (!dictionaries.length && !coverage.length) continue;
    const fieldRows = summarizeFieldRows(coverage, fieldsByKey, globalByField);
    const interpretation = FAMILY_INTERPRETATIONS[family] || FAMILY_INTERPRETATIONS.unknown;
    const distinctiveHigh = fieldRows
      .filter(row => row.deltaFromGlobalMean >= DISTINCTIVE_DELTA)
      .sort((a, b) => b.deltaFromGlobalMean - a.deltaFromGlobalMean || b.meanCoveragePct - a.meanCoveragePct)
      .slice(0, TOP_LIMIT);
    const distinctiveLow = fieldRows
      .filter(row => row.deltaFromGlobalMean <= -DISTINCTIVE_DELTA)
      .sort((a, b) => a.deltaFromGlobalMean - b.deltaFromGlobalMean || a.meanCoveragePct - b.meanCoveragePct)
      .slice(0, TOP_LIMIT);

    profiles.push({
      family,
      dictionaryCount: dictionaries.length,
      dictionaryCodes: dictionaries.map(row => row.code),
      meanCoveragePct: roundPct(mean(dictionaries.map(row => row.coveragePct))),
      meanNonZeroCoveragePct: roundPct(mean(dictionaries.filter(row => row.coveragePct > 0).map(row => row.coveragePct))),
      topDictionaries: dictionaries.slice(0, 8).map(summarizeDictionary),
      interpretation: interpretation.family,
      fieldProfiles: fieldRows.sort((a, b) => a.fieldOrder - b.fieldOrder),
      topFields: addInterpretations(rankFamilyFields(fieldRows, "high"), interpretation.high),
      lowFields: addInterpretations(rankFamilyFields(fieldRows, "low"), interpretation.low),
      distinctiveHighFields: addInterpretations(distinctiveHigh, interpretation.high),
      distinctiveLowFields: addInterpretations(distinctiveLow, interpretation.low)
    });
  }

  return profiles;
}

function buildFieldContrasts(profiles) {
  const rows = [];
  for (const profile of profiles) {
    for (const field of profile.fieldProfiles) {
      rows.push({ family: profile.family, fieldKey: field.fieldKey, value: field.meanCoveragePct, field });
    }
  }
  const allFields = byKey(rows, row => row.fieldKey);
  return [...allFields.entries()]
    .map(([fieldKey, fieldRows]) => {
      const sorted = [...fieldRows].sort((a, b) => b.value - a.value || a.family.localeCompare(b.family));
      const high = sorted[0];
      const low = sorted[sorted.length - 1];
      return {
        fieldKey,
        fieldOrder: high.field.fieldOrder,
        label: high.field.label,
        highFamily: high.family,
        highMeanCoveragePct: high.value,
        lowFamily: low.family,
        lowMeanCoveragePct: low.value,
        spreadPct: roundPct(high.value - low.value),
        interpretation: "Large spreads are family-profile prompts, not proof of semantic preference until review samples are checked."
      };
    })
    .sort((a, b) => b.spreadPct - a.spreadPct || a.fieldOrder - b.fieldOrder)
    .slice(0, CONTRAST_LIMIT);
}

function validate(payload) {
  const errors = [];
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (payload.familyProfiles.some(row => !row.family)) errors.push("family profile without family");
  if (payload.familyProfiles.some(row => !Array.isArray(row.topFields) || !Array.isArray(row.lowFields))) {
    errors.push("family profile without topFields/lowFields");
  }
  for (const profile of payload.familyProfiles) {
    for (const field of [...profile.topFields, ...profile.lowFields]) {
      if (field.meanCoveragePct < 0 || field.meanCoveragePct > 1) {
        errors.push(`${profile.family}/${field.fieldKey}: meanCoveragePct out of range`);
      }
      if (!field.interpretation) errors.push(`${profile.family}/${field.fieldKey}: missing interpretation`);
    }
  }
  if (errors.length) {
    console.error(`H4 family profile build failed with ${errors.length} error(s):`);
    for (const error of errors.slice(0, 25)) console.error(`  - ${error}`);
    process.exit(1);
  }
}

export function buildPayload(data) {
  const fieldsByKey = fieldMetaByKey(data.fields);
  const globalByField = buildGlobalFieldStats(data.coverage, fieldsByKey);
  const familyProfiles = buildFamilyProfiles(data, fieldsByKey, globalByField);
  const fieldContrasts = buildFieldContrasts(familyProfiles);

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "family-profile-artifact",
    claim: "H4-FIELD-FAMILY: AMAR field profiles differ by dictionary family, not only by gross coverage.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-h4-family-profiles",
    sourceGeneratedAt: data.generatedAt,
    sourceFiles: [
      "src/data/dicts/semantic-fields.json",
      "data/lexico/semantic_fields.csv",
      "data/lexico/semantic_field_coverage.csv",
      "data/lexico/semantic_field_report.json",
      "scripts/build-semantic-fields.mjs",
      "scripts/build-h4-family-profiles.mjs"
    ],
    outputs: [
      "data/lexico/semantic_field_family_profiles.json"
    ],
    counts: {
      familyCount: familyProfiles.length,
      dictionaryCount: data.counts.dictionaryRows,
      fieldCount: data.counts.fieldCount,
      coverageRows: data.counts.coverageRows,
      fieldContrasts: fieldContrasts.length
    },
    method: [
      "Group dictionaries by the existing atlas family labels from semantic-fields.json.",
      "Average per-field AMAR headword coverage within each family, including zero-coverage dictionaries.",
      "Rank top and low fields inside each family, then add family-specific convention explanations.",
      "Compute high-spread field contrasts as prompts for review samples, not as final semantic claims."
    ],
    familyProfiles,
    fieldContrasts,
    limitations: [
      "Headword coverage is not sense coverage, citation coverage, corpus frequency, or passage attestation.",
      "Family labels are interpretive scaffolding; they do not prove descent by themselves.",
      "SKD and other prose-heavy dictionaries can be false-low when AMAR material is not exposed as <k1> headwords.",
      "Specialized, index, and reverse-bilingual works require family-specific baselines."
    ],
    boundary: [
      "This artifact uses dictionary and AMAR headword evidence only.",
      "No DCS, corpus, TEI/OntoLex, FrAC, GitHub, or organization-process evidence is used."
    ]
  };
  validate(payload);
  return payload;
}

function main() {
  const data = JSON.parse(fs.readFileSync(INPUT, "utf8"));
  const payload = buildPayload(data);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT)} (${payload.counts.familyCount} family profiles).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
