// Build Comparative Dictionary Lab outputs (Phase 2, first slice).
//
// Deterministic cross-dictionary comparison of MW, AP, PWG, PWK, WIL, VCP, SKD.
// Coverage / overlap / intersection / unique use lemma presence across all 7.
// POS/gender disagreement uses the 5 grammar-reliable tagged dictionaries.
// Sense depth and citation apparatus are deferred (see DICTIONARY_COMPARISON_PLAN).
//
// Usage: npm run build-dict-comparison. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { DICTS, DICT_LABELS } from "./lib/dict-manifest.mjs";
import { iterateDict, dictExists, genderFromLex } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { presentDicts, lemmaConfidence, genderConflict } from "./lib/dict-align.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const SAMPLE = 50;

const ORDER = DICTS.map(d => d.code);
const TAGGED = DICTS.filter(d => d.grammarReliable).map(d => d.code);

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

function buildIndex(warnings) {
  const index = new Map();
  const perDictRecords = {};
  const perDictLemmas = {};

  for (const { code } of DICTS) {
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
        slot = { records: 0, raws: new Set(), genders: new Set(), example: null };
        entry[code] = slot;
      }
      slot.records += 1;
      slot.raws.add(rec.k1.trim());
      const g = genderFromLex(rec.body);
      if (g) slot.genders.add(g);
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
  console.log("Indexing dictionaries...");
  const { index, perDictRecords, perDictLemmas } = buildIndex(warnings);

  // Accumulators, single pass over the index.
  const pair = {}; // "a|b" -> shared count
  for (let i = 0; i < ORDER.length; i++)
    for (let j = i + 1; j < ORDER.length; j++) pair[`${ORDER[i]}|${ORDER[j]}`] = 0;

  const comboCounts = new Map(); // dict-set key -> count
  const coverageHistogram = {}; // number-of-dicts -> count
  const uniqueByDict = Object.fromEntries(ORDER.map(c => [c, { count: 0, examples: [] }]));
  const intersectionAll = { count: 0, examples: [] };
  const confidenceDist = { high: 0, medium: 0 };
  const conflicts = [];
  let conflictCount = 0;
  const lowConfidence = [];

  for (const [normalized, entry] of index) {
    const codes = presentDicts(entry, ORDER);
    const k = codes.length;
    coverageHistogram[k] = (coverageHistogram[k] || 0) + 1;

    const comboKey = codes.join("+");
    comboCounts.set(comboKey, (comboCounts.get(comboKey) || 0) + 1);

    if (k === 1) {
      const u = uniqueByDict[codes[0]];
      u.count += 1;
      if (u.examples.length < SAMPLE) u.examples.push({ lemma: normalized, href: entry[codes[0]].example.href });
    }

    if (k === ORDER.length) {
      intersectionAll.count += 1;
      if (intersectionAll.examples.length < SAMPLE) intersectionAll.examples.push({ lemma: normalized });
    }

    // pairwise
    for (let i = 0; i < codes.length; i++)
      for (let j = i + 1; j < codes.length; j++) pair[`${codes[i]}|${codes[j]}`] += 1;

    // confidence (multi-dict lemmas only)
    if (k >= 2) {
      const conf = lemmaConfidence(entry, codes);
      confidenceDist[conf] += 1;
      if (conf === "medium" && lowConfidence.length < SAMPLE) {
        lowConfidence.push({
          lemma: normalized,
          dicts: codes.map(c => DICT_LABELS[c]),
          variants: [...new Set(codes.flatMap(c => [...entry[c].raws]))]
        });
      }
    }

    // gender conflict (tagged dicts)
    const gc = genderConflict(entry, TAGGED);
    if (gc.conflict) {
      conflictCount += 1;
      if (conflicts.length < SAMPLE * 4) {
        conflicts.push({
          lemma: normalized,
          byDict: Object.fromEntries(
            Object.entries(gc.byDict).map(([c, g]) => [DICT_LABELS[c], g])
          ),
          examples: Object.keys(gc.byDict).map(c => ({ dict: DICT_LABELS[c], href: entry[c].example.href }))
        });
      }
    }
  }

  const distinctLemmas = index.size;
  const written = [];

  // 1. Coverage matrix (UpSet-style combination summary).
  const combos = [...comboCounts.entries()]
    .map(([key, count]) => ({ dicts: key.split("+").map(c => DICT_LABELS[c]), size: key.split("+").length, count }))
    .sort((a, b) => b.count - a.count);
  written.push(
    writeJson(
      "coverage-matrix.json",
      envelope(
        {
          distinctLemmas,
          recordsByDict: Object.fromEntries(ORDER.map(c => [DICT_LABELS[c], perDictRecords[c]])),
          lemmasByDict: Object.fromEntries(ORDER.map(c => [DICT_LABELS[c], perDictLemmas[c]])),
          coverageHistogram,
          topCombinations: combos.slice(0, 60)
        },
        {
          assumptions: [
            "Lemmas are grouped by normalized SLP1 <k1> (accents and trailing homonym digits stripped).",
            "Counts are distinct normalized lemmas; homonym record counts are preserved per dictionary but not split here."
          ]
        }
      )
    )
  );

  // 2. Pairwise overlap (+ jaccard).
  const pairwise = [];
  for (let i = 0; i < ORDER.length; i++) {
    for (let j = i + 1; j < ORDER.length; j++) {
      const a = ORDER[i], b = ORDER[j];
      const shared = pair[`${a}|${b}`];
      const union = perDictLemmas[a] + perDictLemmas[b] - shared;
      pairwise.push({
        a: DICT_LABELS[a],
        b: DICT_LABELS[b],
        shared,
        jaccard: union ? Number((shared / union).toFixed(4)) : 0
      });
    }
  }
  written.push(
    writeJson("pairwise-overlap.json", envelope({ pairwise: pairwise.sort((x, y) => y.shared - x.shared) }, {}))
  );

  // 3. All-dictionary intersection.
  written.push(
    writeJson(
      "all-intersection.json",
      envelope({ count: intersectionAll.count, examples: intersectionAll.examples }, {
        assumptions: [`Lemmas present in all ${ORDER.length} target dictionaries.`]
      })
    )
  );

  // 4. Dictionary-unique vocabulary.
  written.push(
    writeJson(
      "dictionary-unique.json",
      envelope(
        { unique: Object.fromEntries(ORDER.map(c => [DICT_LABELS[c], uniqueByDict[c]])) },
        { assumptions: ["A lemma is 'unique' when it appears in exactly one target dictionary (after normalization)."] }
      )
    )
  );

  // 5. POS/gender disagreement (tagged dicts only).
  written.push(
    writeJson(
      "pos-disagreement.json",
      envelope(
        { conflictCount, shown: conflicts.length, conflicts },
        {
          assumptions: [
            `Gender conflicts are computed only across grammar-reliable tagged dictionaries: ${TAGGED.map(c => DICT_LABELS[c]).join(", ")}.`,
            "A conflict means two dictionaries assert disjoint specific genders ({m,f,n}); adjective/indeclinable tags never trigger one.",
            "Within-dictionary polysemy (a lemma listed under several genders) does not count as a conflict."
          ],
          warnings: ["VCP and SKD encode gender in prose and are excluded from conflict detection in this slice."]
        }
      )
    )
  );

  // 6. Alignment confidence + low-confidence review queue.
  written.push(
    writeJson(
      "alignment-confidence.json",
      envelope(
        { distribution: confidenceDist, reviewQueueSample: lowConfidence },
        {
          assumptions: [
            "high = every contributing dictionary used the identical raw <k1>; medium = matched only after normalization.",
            "Only lemmas present in >=2 dictionaries are scored."
          ]
        }
      )
    )
  );

  // 7. Validation report.
  const report = {
    distinctLemmas,
    recordsByDict: Object.fromEntries(ORDER.map(c => [DICT_LABELS[c], perDictRecords[c]])),
    intersectionAll: intersectionAll.count,
    genderConflicts: conflictCount,
    warnings
  };
  written.push(writeJson("dictionary-comparison-validation.json", envelope(report, { warnings })));

  console.log(`\nIndexed ${distinctLemmas} distinct lemmas. Wrote:`);
  for (const w of written) console.log(`- ${w}`);
  if (warnings.length) for (const w of warnings) console.log(`  ! ${w}`);
}

main();
