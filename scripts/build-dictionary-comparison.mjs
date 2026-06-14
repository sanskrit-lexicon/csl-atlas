// Build Comparative Dictionary Lab outputs (Phase 2, first slice).
//
// Deterministic cross-dictionary comparison of MW, AP, PWG, PWK, WIL, VCP, SKD.
// Coverage / overlap / intersection / unique use broad headword presence by default.
// Deep metrics use validated feature adapters and never count unavailable markup as zero.
//
// Usage: npm run build-dict-comparison. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { DICTS, DICT_LABELS } from "./lib/dict-manifest.mjs";
import { iterateHeadwords } from "./lib/dict-headwords.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { presentDicts, lemmaConfidence, genderConflict } from "./lib/dict-align.mjs";
import { buildBroadHeadwordDictionaries, coreComparisonDictionaries } from "./lib/dict-scope.mjs";
import { extractGrammar, featureSupport, supportedFeatureCodes } from "./lib/dict-feature-adapters.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const SAMPLE = 50;
// A lemma enters the dossier when it is attested in at least this many of the
// 7 target dictionaries. Keeps the static dossier dataset compact while
// covering the well-attested shared vocabulary (full-corpus lookup over all
// ~300k lemmas would need a search backend — see the comparison plan).
const DOSSIER_MIN_DICTS = 5;
const LOOKUP_MIN_DICTS = 4;
const GENDER_TOKENS = new Set(["m", "f", "n", "adj", "ind"]);
const HREF_BASE = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02";

const ORDER = DICTS.map(d => d.code);
const BROAD_HEADWORD_DICTS = buildBroadHeadwordDictionaries();
const CORE_COMPARISON_DICTS = coreComparisonDictionaries();
const BROAD_BY_CODE = new Map(BROAD_HEADWORD_DICTS.map(d => [d.code, d]));
const CORE_BY_CODE = new Map(CORE_COMPARISON_DICTS.map(d => [d.code, d]));
const ALL_LABELS = {
  ...Object.fromEntries(BROAD_HEADWORD_DICTS.map(d => [d.code, d.label])),
  ...DICT_LABELS
};
const BROAD_GRAMMAR_DICTS = supportedFeatureCodes("grammar", { scope: "broadHeadword" });
const GRAMMAR_DICTS = [
  ...ORDER.filter(code => BROAD_GRAMMAR_DICTS.includes(code)),
  ...BROAD_GRAMMAR_DICTS.filter(code => !ORDER.includes(code))
];
const GRAMMAR_DICTIONARIES = GRAMMAR_DICTS.map(code => BROAD_BY_CODE.get(code) ?? CORE_BY_CODE.get(code) ?? { code, label: ALL_LABELS[code] ?? code.toUpperCase() });
const HOMONYM_DICTS = supportedFeatureCodes("homonyms", { scope: "coreComparison" });
const DICT_INDEX = Object.fromEntries(ORDER.map((code, index) => [code, index]));
const COVERAGE_SCOPES = {
  broadHeadword: {
    label: "Broad 40",
    dictionaries: BROAD_HEADWORD_DICTS
  },
  coreComparison: {
    label: "Core 7",
    dictionaries: CORE_COMPARISON_DICTS
  }
};

function envelope(extra, { assumptions = [], warnings = [] }) {
  return {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    dictionaries: DICTS.map(d => ({ code: d.code, label: d.label, grammarReliable: d.grammarReliable })),
    assumptions,
    warnings,
    ...extra
  };
}

function writeJson(name, payload) {
  fs.writeFileSync(path.join(OUT_DIR, name), `${JSON.stringify(payload, null, 2)}\n`);
  return path.relative(process.cwd(), path.join(OUT_DIR, name));
}

function neutralEnvelope(extra, { assumptions = [], warnings = [] } = {}) {
  return {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    assumptions,
    warnings,
    ...extra
  };
}

function coverageLabelMap(dictionaries) {
  return Object.fromEntries(dictionaries.map(d => [d.code, d.label]));
}

function emptyCounts(dictionaries) {
  return Object.fromEntries(dictionaries.map(d => [d.code, 0]));
}

function sourcePointer(dict, line) {
  return dict?.sourceLinkMode === "github" && line ? `${HREF_BASE}/${dict.code}/${dict.code}.txt#L${line}` : null;
}

function buildCoverageScope(scope, warnings) {
  const { label, dictionaries } = scope;
  const order = dictionaries.map(d => d.code);
  const labels = coverageLabelMap(dictionaries);
  const index = new Map();
  const recordsByCode = emptyCounts(dictionaries);
  const lemmasByCode = emptyCounts(dictionaries);

  for (const dict of dictionaries) {
    if (!dictExists(dict.code)) {
      warnings.push(`${label}: missing source for ${dict.code}; skipped.`);
      continue;
    }
    const lemmaSet = new Set();
    let records = 0;
    for (const rec of iterateHeadwords(dict)) {
      if (!rec.k1) continue;
      const { normalized } = normalizeLemma(rec.k1);
      if (!normalized) continue;
      records += 1;
      lemmaSet.add(normalized);

      let entry = index.get(normalized);
      if (!entry) {
        entry = {};
        index.set(normalized, entry);
      }
      let slot = entry[dict.code];
      if (!slot) {
        slot = { records: 0, raws: new Set(), example: null };
        entry[dict.code] = slot;
      }
      slot.records += 1;
      slot.raws.add(rec.k1.trim());
      if (!slot.example) {
        slot.example = { k1: rec.k1, line: rec.startLine, href: sourcePointer(dict, rec.startLine) };
      }
    }
    recordsByCode[dict.code] = records;
    lemmasByCode[dict.code] = lemmaSet.size;
    console.log(`  ${label} ${dict.code}: ${records.toLocaleString()} headword records, ${lemmaSet.size.toLocaleString()} distinct lemmas`);
  }

  const pair = {};
  for (let i = 0; i < order.length; i++)
    for (let j = i + 1; j < order.length; j++) pair[`${order[i]}|${order[j]}`] = 0;

  const comboCounts = new Map();
  const coverageHistogram = {};
  const uniqueByCode = Object.fromEntries(order.map(c => [c, { count: 0, examples: [] }]));
  const intersectionAll = { count: 0, examples: [] };

  for (const [normalized, entry] of index) {
    const codes = presentDicts(entry, order);
    const k = codes.length;
    coverageHistogram[k] = (coverageHistogram[k] || 0) + 1;
    const comboKey = codes.join("+");
    comboCounts.set(comboKey, (comboCounts.get(comboKey) || 0) + 1);

    if (k === 1) {
      const u = uniqueByCode[codes[0]];
      u.count += 1;
      if (u.examples.length < SAMPLE) u.examples.push({ lemma: normalized, href: entry[codes[0]].example.href });
    }

    if (k === order.length) {
      intersectionAll.count += 1;
      if (intersectionAll.examples.length < SAMPLE) intersectionAll.examples.push({ lemma: normalized });
    }

    for (let i = 0; i < codes.length; i++)
      for (let j = i + 1; j < codes.length; j++) pair[`${codes[i]}|${codes[j]}`] += 1;
  }

  const topCombinations = [...comboCounts.entries()]
    .map(([key, count]) => ({ dicts: key.split("+").map(c => labels[c]), size: key.split("+").length, count }))
    .sort((a, b) => b.count - a.count);

  const pairwise = [];
  for (let i = 0; i < order.length; i++) {
    for (let j = i + 1; j < order.length; j++) {
      const a = order[i], b = order[j];
      const shared = pair[`${a}|${b}`];
      const union = lemmasByCode[a] + lemmasByCode[b] - shared;
      pairwise.push({
        a: labels[a],
        b: labels[b],
        aCode: a,
        bCode: b,
        shared,
        jaccard: union ? Number((shared / union).toFixed(4)) : 0
      });
    }
  }
  pairwise.sort((x, y) => y.shared - x.shared);

  return {
    scope: scope.id,
    scopeLabel: label,
    dictionaryCount: dictionaries.length,
    dictionaries,
    distinctLemmas: index.size,
    recordsByDict: Object.fromEntries(order.map(c => [labels[c], recordsByCode[c]])),
    lemmasByDict: Object.fromEntries(order.map(c => [labels[c], lemmasByCode[c]])),
    coverageHistogram,
    topCombinations: topCombinations.slice(0, 60),
    unique: Object.fromEntries(order.map(c => [labels[c], uniqueByCode[c]])),
    intersectionAll,
    pairwise
  };
}

function buildCoverageScopes(warnings) {
  console.log("Indexing broad/core coverage scopes...");
  return Object.fromEntries(Object.entries(COVERAGE_SCOPES).map(([id, scope]) => [id, buildCoverageScope({ ...scope, id }, warnings)]));
}

function orderIncludedDictionaries(support, codes) {
  const byCode = new Map(support.includedDictionaries.map(dict => [dict.code, dict]));
  return {
    ...support,
    includedDictionaries: codes.map(code => byCode.get(code)).filter(Boolean)
  };
}

function buildIndex(warnings, dictionaries = DICTS) {
  const index = new Map();
  const perDictRecords = {};
  const perDictLemmas = {};

  for (const { code } of dictionaries) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; skipped.`);
      perDictRecords[code] = 0;
      perDictLemmas[code] = 0;
      continue;
    }
    let records = 0;
    const lemmaSet = new Set();
    for (const rec of iterateDict(code)) {
      if (!rec.k1) continue;
      records += 1;
      const { normalized } = normalizeLemma(rec.k1);
      if (!normalized) continue;
      lemmaSet.add(normalized);

      let entry = index.get(normalized);
      if (!entry) {
        entry = {};
        index.set(normalized, entry);
      }
      let slot = entry[code];
      if (!slot) {
        slot = { records: 0, raws: new Set(), genders: new Set(), homs: new Set(), example: null };
        entry[code] = slot;
      }
      slot.records += 1;
      slot.raws.add(rec.k1.trim());
      if (rec.h) slot.homs.add(rec.h.trim());
      const g = extractGrammar(code, rec.body);
      if (g) slot.genders.add(g.value);
      if (!slot.example) slot.example = { k1: rec.k1, line: rec.startLine, href: rec.href };
    }
    perDictRecords[code] = records;
    perDictLemmas[code] = lemmaSet.size;
    console.log(`  ${code}: ${records} records, ${lemmaSet.size} distinct lemmas`);
  }
  return { index, perDictRecords, perDictLemmas };
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const warnings = [];
  const coverageScopes = buildCoverageScopes(warnings);
  console.log("Indexing core deep-analysis dictionaries...");
  const { index, perDictRecords } = buildIndex(warnings, DICTS);
  console.log("Indexing grammar/POS feature dictionaries...");
  const { index: grammarIndex } = buildIndex(warnings, GRAMMAR_DICTIONARIES);

  // Accumulators, single pass over the index.
  const confidenceDist = { high: 0, medium: 0 };
  const conflicts = [];
  let conflictCount = 0;
  const lowConfidence = [];
  const dossier = [];
  const lookup = [];
  const homonymSplits = [];
  let homonymSplitCount = 0;

  for (const [normalized, entry] of index) {
    const codes = presentDicts(entry, ORDER);
    const k = codes.length;

    // confidence (multi-dict lemmas only)
    if (k >= 2) {
      const conf = lemmaConfidence(entry, codes);
      confidenceDist[conf] += 1;
      if (conf === "medium") {
        // Complete (not sampled): low-confidence alignments are intrinsically
        // rare, and the review layer needs every one with a source link.
        lowConfidence.push({
          lemma: normalized,
          dicts: codes.map(c => ({ dict: DICT_LABELS[c], href: entry[c].example.href })),
          variants: [...new Set(codes.flatMap(c => [...entry[c].raws]))]
        });
      }
    }

    // per-lemma dossier (well-attested vocabulary only). Compact tuple form
    // [code, records, firstLine, gender] keeps the static dataset small; the
    // page reconstructs the source href from HREF_BASE + code.
    if (k >= DOSSIER_MIN_DICTS) {
      dossier.push({
        l: normalized,
        c: k,
        d: codes.map(code => [
          code,
          entry[code].records,
          entry[code].example.line,
          [...entry[code].genders].filter(g => GENDER_TOKENS.has(g)).sort().join("")
        ])
      });
    }

    // Reader Lookup v1: exact/prefix lookup over cross-attested headwords. The
    // low-coverage tail is intentionally omitted to keep the public page
    // responsive without adding a backend search service.
    if (k >= LOOKUP_MIN_DICTS) {
      lookup.push([
        normalized,
        codes.map(code => {
          const gender = [...entry[code].genders].filter(g => GENDER_TOKENS.has(g)).sort().join("");
          const tuple = [DICT_INDEX[code], entry[code].records, entry[code].example.line];
          if (gender) tuple.push(gender);
          return tuple;
        })
      ]);
    }

    // homonym split: among the homonym-marking dicts (MW, PWG, PWK) that
    // contain the lemma, do they disagree on how many homonyms it has?
    // homonymCount = distinct <h> indices, or 1 when none are marked.
    const homDicts = HOMONYM_DICTS.filter(c => entry[c]);
    if (homDicts.length >= 2) {
      const counts = {};
      for (const c of homDicts) counts[c] = entry[c].homs.size || 1;
      const vals = Object.values(counts);
      const max = Math.max(...vals);
      const min = Math.min(...vals);
      if (max >= 2 && max !== min) {
        homonymSplitCount += 1;
        if (homonymSplits.length < 400) {
          homonymSplits.push({
            lemma: normalized,
            byDict: Object.fromEntries(homDicts.map(c => [DICT_LABELS[c], counts[c]])),
            maxHomonyms: max,
            spread: max - min,
            examples: homDicts.map(c => ({ dict: DICT_LABELS[c], href: entry[c].example.href }))
          });
        }
      }
    }

  }

  for (const [normalized, entry] of grammarIndex) {
    const gc = genderConflict(entry, GRAMMAR_DICTS);
    if (gc.conflict) {
      conflictCount += 1;
      if (conflicts.length < SAMPLE * 4) {
        conflicts.push({
          lemma: normalized,
          byDict: Object.fromEntries(
            Object.entries(gc.byDict).map(([c, g]) => [ALL_LABELS[c] ?? c.toUpperCase(), g])
          ),
          examples: Object.keys(gc.byDict).map(c => ({
            dict: ALL_LABELS[c] ?? c.toUpperCase(),
            href: entry[c].example.href
          }))
        });
      }
    }
  }

  const distinctLemmas = index.size;
  const written = [];
  const grammarSupport = orderIncludedDictionaries(featureSupport("grammar", { scope: "broadHeadword" }), GRAMMAR_DICTS);
  const homonymSupport = featureSupport("homonyms", { scope: "broadHeadword" });
  const headwordAlignmentSupport = {
    feature: "headwordAlignment",
    featureLabel: "Headword alignment",
    adapterScope: "coreComparison",
    includedDictionaries: DICTS.map(d => ({
      code: d.code,
      label: d.label,
      fullName: d.fullName ?? d.label,
      methodId: "cdsl-k1-normalized-headword",
      methodLabel: "CDSL <k1> normalized headword",
      status: "supported",
      confidence: "validated",
      fixtureCoverage: "unit"
    })),
    unavailableDictionaries: [],
    methodNotes: [
      "Alignment confidence is a neutral headword metric over Core 7 <k1> entries.",
      "Broad coverage/overlap uses the separate broadHeadword layer; this compact alignment review remains Core 7."
    ]
  };

  // 1-4. Neutral headword coverage outputs. Top-level fields mirror the broad
  // default, while `scopes.coreComparison` preserves the legacy Core 7 view.
  const defaultScope = "broadHeadword";
  const broadCoverage = coverageScopes[defaultScope];
  const coreCoverage = coverageScopes.coreComparison;
  written.push(
    writeJson(
      "coverage-matrix.json",
      neutralEnvelope(
        {
          defaultScope,
          scopeLabels: { broadHeadword: broadCoverage.scopeLabel, coreComparison: coreCoverage.scopeLabel },
          distinctLemmas: broadCoverage.distinctLemmas,
          dictionaryCount: broadCoverage.dictionaryCount,
          dictionaries: broadCoverage.dictionaries,
          recordsByDict: broadCoverage.recordsByDict,
          lemmasByDict: broadCoverage.lemmasByDict,
          coverageHistogram: broadCoverage.coverageHistogram,
          topCombinations: broadCoverage.topCombinations,
          scopes: {
            broadHeadword: {
              scope: broadCoverage.scope,
              scopeLabel: broadCoverage.scopeLabel,
              dictionaryCount: broadCoverage.dictionaryCount,
              dictionaries: broadCoverage.dictionaries,
              distinctLemmas: broadCoverage.distinctLemmas,
              recordsByDict: broadCoverage.recordsByDict,
              lemmasByDict: broadCoverage.lemmasByDict,
              coverageHistogram: broadCoverage.coverageHistogram,
              topCombinations: broadCoverage.topCombinations
            },
            coreComparison: {
              scope: coreCoverage.scope,
              scopeLabel: coreCoverage.scopeLabel,
              dictionaryCount: coreCoverage.dictionaryCount,
              dictionaries: coreCoverage.dictionaries,
              distinctLemmas: coreCoverage.distinctLemmas,
              recordsByDict: coreCoverage.recordsByDict,
              lemmasByDict: coreCoverage.lemmasByDict,
              coverageHistogram: coreCoverage.coverageHistogram,
              topCombinations: coreCoverage.topCombinations
            }
          }
        },
        {
          assumptions: [
            "Lemmas are grouped by normalized SLP1 headword forms; kosha synonym dictionaries use validated <syns> headword extraction.",
            "Broad coverage is headword coverage only. Deep analyses use validated feature adapters and do not treat missing markup as zero evidence."
          ],
          warnings
        }
      )
    )
  );

  written.push(
    writeJson(
      "pairwise-overlap.json",
      neutralEnvelope(
        {
          defaultScope,
          scopeLabels: { broadHeadword: broadCoverage.scopeLabel, coreComparison: coreCoverage.scopeLabel },
          dictionaries: broadCoverage.dictionaries,
          pairwise: broadCoverage.pairwise,
          scopes: {
            broadHeadword: {
              scope: broadCoverage.scope,
              scopeLabel: broadCoverage.scopeLabel,
              dictionaryCount: broadCoverage.dictionaryCount,
              dictionaries: broadCoverage.dictionaries,
              pairwise: broadCoverage.pairwise
            },
            coreComparison: {
              scope: coreCoverage.scope,
              scopeLabel: coreCoverage.scopeLabel,
              dictionaryCount: coreCoverage.dictionaryCount,
              dictionaries: coreCoverage.dictionaries,
              pairwise: coreCoverage.pairwise
            }
          }
        },
        {
          assumptions: ["Jaccard = shared normalized headwords / union of normalized headwords."],
          warnings
        }
      )
    )
  );

  written.push(
    writeJson(
      "all-intersection.json",
      neutralEnvelope(
        {
          defaultScope,
          scopeLabels: { broadHeadword: broadCoverage.scopeLabel, coreComparison: coreCoverage.scopeLabel },
          count: broadCoverage.intersectionAll.count,
          examples: broadCoverage.intersectionAll.examples,
          scopes: {
            broadHeadword: {
              scope: broadCoverage.scope,
              scopeLabel: broadCoverage.scopeLabel,
              dictionaryCount: broadCoverage.dictionaryCount,
              count: broadCoverage.intersectionAll.count,
              examples: broadCoverage.intersectionAll.examples
            },
            coreComparison: {
              scope: coreCoverage.scope,
              scopeLabel: coreCoverage.scopeLabel,
              dictionaryCount: coreCoverage.dictionaryCount,
              count: coreCoverage.intersectionAll.count,
              examples: coreCoverage.intersectionAll.examples
            }
          }
        },
        {
          assumptions: [
            "Broad all-dictionary intersection may be zero because the 40-dictionary set includes specialized and genre-specific dictionaries.",
            "Core 7 intersection remains the legacy non-empty comparison invariant."
          ],
          warnings
        }
      )
    )
  );

  written.push(
    writeJson(
      "dictionary-unique.json",
      neutralEnvelope(
        {
          defaultScope,
          scopeLabels: { broadHeadword: broadCoverage.scopeLabel, coreComparison: coreCoverage.scopeLabel },
          unique: broadCoverage.unique,
          scopes: {
            broadHeadword: {
              scope: broadCoverage.scope,
              scopeLabel: broadCoverage.scopeLabel,
              dictionaryCount: broadCoverage.dictionaryCount,
              unique: broadCoverage.unique
            },
            coreComparison: {
              scope: coreCoverage.scope,
              scopeLabel: coreCoverage.scopeLabel,
              dictionaryCount: coreCoverage.dictionaryCount,
              unique: coreCoverage.unique
            }
          }
        },
        {
          assumptions: ["A lemma is unique when it appears in exactly one dictionary within the selected scope."],
          warnings
        }
      )
    )
  );

  // 5. POS/gender disagreement (tagged dicts only).
  written.push(
    writeJson(
      "pos-disagreement.json",
      envelope(
        {
          feature: grammarSupport.feature,
          featureLabel: grammarSupport.featureLabel,
          adapterScope: grammarSupport.adapterScope,
          includedDictionaries: grammarSupport.includedDictionaries,
          unavailableDictionaries: grammarSupport.unavailableDictionaries,
          methodNotes: grammarSupport.methodNotes,
          conflictCount,
          shown: conflicts.length,
          conflicts
        },
        {
          assumptions: [
            "Gender/POS evidence comes only from supported feature adapters.",
            "A conflict means two dictionaries assert disjoint specific genders ({m,f,n}); adjective/indeclinable tags never trigger one.",
            "Within-dictionary polysemy (a lemma listed under several genders) does not count as a conflict.",
            "Unavailable dictionaries are excluded from this metric, never counted as zero evidence."
          ],
          warnings: ["VCP prose markers reliably capture m/adj/ind but under-mark f/n at the anchor position, so some VCP feminine/neuter genders are absent (missed conflicts, never false ones)."]
        }
      )
    )
  );

  // 5b. Homonym split: where the homonym-marking dictionaries disagree on
  // how many homonyms a lemma has. Sorted by spread then max.
  homonymSplits.sort((a, b) => b.spread - a.spread || b.maxHomonyms - a.maxHomonyms || a.lemma.localeCompare(b.lemma));
  written.push(
    writeJson(
      "homonym-split.json",
      envelope(
        {
          feature: homonymSupport.feature,
          featureLabel: homonymSupport.featureLabel,
          adapterScope: homonymSupport.adapterScope,
          includedDictionaries: homonymSupport.includedDictionaries,
          unavailableDictionaries: homonymSupport.unavailableDictionaries,
          methodNotes: homonymSupport.methodNotes,
          homonymDicts: HOMONYM_DICTS.map(c => DICT_LABELS[c]),
          candidateCount: homonymSplitCount,
          shown: homonymSplits.length,
          candidates: homonymSplits
        },
        {
          assumptions: [
            `Homonym counts use the <h> index; only the homonym-marking dictionaries carry it: ${HOMONYM_DICTS.map(c => DICT_LABELS[c]).join(", ")}.`,
            "homonymCount = distinct <h> values for the lemma, or 1 when none are marked.",
            "A candidate is a lemma present in >=2 of those dictionaries where the homonym count differs and the maximum is >=2 (one dictionary splits what another merges).",
            "Differing homonymy is usually legitimate lexicographic practice, not an error; this is an analysis view, not a correction queue.",
            "Unavailable dictionaries are excluded from this metric, never counted as one or zero evidence."
          ],
          warnings: ["AP, WIL, VCP, SKD do not mark homonyms with <h> and are excluded."]
        }
      )
    )
  );

  // 6. Alignment confidence + low-confidence review queue.
  written.push(
    writeJson(
      "alignment-confidence.json",
      envelope(
        {
          feature: headwordAlignmentSupport.feature,
          featureLabel: headwordAlignmentSupport.featureLabel,
          adapterScope: headwordAlignmentSupport.adapterScope,
          includedDictionaries: headwordAlignmentSupport.includedDictionaries,
          unavailableDictionaries: headwordAlignmentSupport.unavailableDictionaries,
          methodNotes: headwordAlignmentSupport.methodNotes,
          distribution: confidenceDist,
          lowConfidence
        },
        {
          assumptions: [
            "high = every contributing dictionary used the identical raw <k1>; medium = matched only after normalization.",
            "Only lemmas present in >=2 dictionaries are scored."
          ]
        }
      )
    )
  );

  // 7. Per-lemma dossier (well-attested vocabulary). Written without
  // indentation: it is the one large data file and stays a flat compact array.
  dossier.sort((a, b) => b.c - a.c || a.l.localeCompare(b.l));
  const dossierPayload = envelope(
    {
      minDicts: DOSSIER_MIN_DICTS,
      hrefBase: HREF_BASE,
      tupleFields: ["code", "records", "firstLine", "gender"],
      count: dossier.length,
      entries: dossier
    },
    {
      assumptions: [
        `Includes lemmas attested in at least ${DOSSIER_MIN_DICTS} of the ${ORDER.length} target dictionaries.`,
        "Each dict tuple is [code, records, firstLine, gender]; href = hrefBase + /code/code.txt#L firstLine.",
        "gender (from <lex>) is empty for VCP/SKD (prose) and for entries without a <lex> tag."
      ],
      warnings: [
        "Lemmas in fewer than the threshold number of dictionaries are omitted; full-corpus lookup needs a search backend (deferred)."
      ]
    }
  );
  fs.writeFileSync(path.join(OUT_DIR, "lemma-dossier.json"), `${JSON.stringify(dossierPayload)}\n`);
  written.push(path.relative(process.cwd(), path.join(OUT_DIR, "lemma-dossier.json")));

  // 8. Reader lookup index. Written compactly like the dossier.
  lookup.sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0);
  const lookupPayload = envelope(
    {
      hrefBase: HREF_BASE,
      minDicts: LOOKUP_MIN_DICTS,
      tupleFields: ["lemma", "dicts"],
      dictTupleFields: ["dictIndex", "records", "firstLine", "gender?"],
      inputSchemes: ["SLP1", "IAST"],
      count: lookup.length,
      entries: lookup
    },
    {
      assumptions: [
        `Includes normalized lemmas attested in at least ${LOOKUP_MIN_DICTS} of the ${ORDER.length} target dictionaries.`,
        "Each entry is [lemma, dictTuples]; each dict tuple is [dictIndex, records, firstLine, gender?].",
        "Dictionary code is dictionaries[dictIndex].code; href = hrefBase + /code/code.txt#L firstLine.",
        "Reader Lookup v1 is exact/prefix lookup over dictionary headwords, not full-text search and not a corpus lookup."
      ],
      warnings: [
        "Lemmas below the coverage threshold are omitted from Reader Lookup v1; use dictionary source files or a future search backend for the long tail.",
        "Search is static and client-side; very broad prefixes are capped in the page.",
        "IAST input is transliterated deterministically, but ambiguous surface forms and sandhi are not resolved."
      ]
    }
  );
  fs.writeFileSync(path.join(OUT_DIR, "lemma-lookup.json"), `${JSON.stringify(lookupPayload)}\n`);
  written.push(path.relative(process.cwd(), path.join(OUT_DIR, "lemma-lookup.json")));

  // 9. Validation report.
  const report = {
    distinctLemmas,
    dossierEntries: dossier.length,
    lookupEntries: lookup.length,
    recordsByDict: Object.fromEntries(ORDER.map(c => [DICT_LABELS[c], perDictRecords[c]])),
    coverageScopes: Object.fromEntries(Object.entries(coverageScopes).map(([scope, data]) => [scope, {
      dictionaryCount: data.dictionaryCount,
      distinctLemmas: data.distinctLemmas,
      intersectionAll: data.intersectionAll.count,
      pairwiseRows: data.pairwise.length
    }])),
    featureAdapters: {
      grammar: {
        included: grammarSupport.includedDictionaries.length,
        unavailable: grammarSupport.unavailableDictionaries.length
      },
      homonyms: {
        included: homonymSupport.includedDictionaries.length,
        unavailable: homonymSupport.unavailableDictionaries.length
      },
      headwordAlignment: {
        included: headwordAlignmentSupport.includedDictionaries.length,
        unavailable: headwordAlignmentSupport.unavailableDictionaries.length
      }
    },
    intersectionAll: coverageScopes.coreComparison.intersectionAll.count,
    genderConflicts: conflictCount,
    homonymSplits: homonymSplitCount,
    warnings
  };
  written.push(writeJson("dictionary-comparison-validation.json", envelope(report, { warnings })));

  console.log(`\nIndexed ${distinctLemmas} distinct lemmas. Wrote:`);
  for (const w of written) console.log(`- ${w}`);
  if (warnings.length) for (const w of warnings) console.log(`  ! ${w}`);
}

// Run only when executed directly, not when imported by tests.
if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
