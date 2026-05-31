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
import { iterateDict, dictExists, genderForDict } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { presentDicts, lemmaConfidence, genderConflict } from "./lib/dict-align.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const SAMPLE = 50;
// A lemma enters the dossier when it is attested in at least this many of the
// 7 target dictionaries. Keeps the static dossier dataset compact while
// covering the well-attested shared vocabulary (full-corpus lookup over all
// ~300k lemmas would need a search backend — see the comparison plan).
const DOSSIER_MIN_DICTS = 5;
const GENDER_TOKENS = new Set(["m", "f", "n", "adj", "ind"]);
const HREF_BASE = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02";

const ORDER = DICTS.map(d => d.code);
const TAGGED = DICTS.filter(d => d.grammarReliable).map(d => d.code);
const HOMONYM_DICTS = DICTS.filter(d => d.homonymMarked).map(d => d.code);

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
        slot = { records: 0, raws: new Set(), genders: new Set(), homs: new Set(), example: null };
        entry[code] = slot;
      }
      slot.records += 1;
      slot.raws.add(rec.k1.trim());
      if (rec.h) slot.homs.add(rec.h.trim());
      const g = genderForDict(code, rec.body);
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
  const dossier = [];
  const homonymSplits = [];
  let homonymSplitCount = 0;

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

    // gender conflict across all gender-bearing dicts (lex + prose)
    const gc = genderConflict(entry, ORDER);
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
            "Gender is taken from <lex> for the tagged dictionaries (MW, AP, PWG, PWK, WIL) and from prose markers for VCP and SKD.",
            "A conflict means two dictionaries assert disjoint specific genders ({m,f,n}); adjective/indeclinable tags never trigger one.",
            "Within-dictionary polysemy (a lemma listed under several genders) does not count as a conflict."
          ],
          warnings: ["VCP prose markers reliably capture m/adj/ind but under-mark f/n at the anchor position, so some VCP feminine/neuter genders are absent (missed conflicts, never false ones)."]
        }
      )
    )
  );

  // 5b. Homonym split: where the homonym-marking dictionaries disagree on
  // how many homonyms a lemma has (UC-LX-10). Sorted by spread then max.
  homonymSplits.sort((a, b) => b.spread - a.spread || b.maxHomonyms - a.maxHomonyms || a.lemma.localeCompare(b.lemma));
  written.push(
    writeJson(
      "homonym-split.json",
      envelope(
        {
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
            "Differing homonymy is usually legitimate lexicographic practice, not an error; this is an analysis view, not a correction queue."
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
        { distribution: confidenceDist, lowConfidence },
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

  // 8. Validation report.
  const report = {
    distinctLemmas,
    dossierEntries: dossier.length,
    recordsByDict: Object.fromEntries(ORDER.map(c => [DICT_LABELS[c], perDictRecords[c]])),
    intersectionAll: intersectionAll.count,
    genderConflicts: conflictCount,
    homonymSplits: homonymSplitCount,
    warnings
  };
  written.push(writeJson("dictionary-comparison-validation.json", envelope(report, { warnings })));

  console.log(`\nIndexed ${distinctLemmas} distinct lemmas. Wrote:`);
  for (const w of written) console.log(`- ${w}`);
  if (warnings.length) for (const w of warnings) console.log(`  ! ${w}`);
}

main();
