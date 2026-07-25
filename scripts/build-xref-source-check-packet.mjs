// Build a compact source-check packet for the xref hub review package.
//
// This generator reads only atlas xref artifacts plus dictionary source files
// for pointers. It records no human decisions and does not change parser,
// public-page, corpus, DCS, backend/runtime, or standards behavior.
//
// Usage: npm run build-xref-source-check-packet

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseCsv } from "./build-xref-hub-review.mjs";
import { dictExists, iterateDict } from "./lib/dict-parser.mjs";
import { cologneLinksFor, entryUrl } from "./lib/cologne-links.mjs";
import { generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-xref-source-check-packet";
const HUB_REVIEW_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_hub_review.json");
const XREF_EDGES_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_edges.csv");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "xref_source_check_packet.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "MICROSTRUCTURE_XREF_SOURCE_CHECK.md");
const SHARED_CORE_LIMIT = 40;
const PREFIX_CONTROL_TARGETS_PER_DICT = 5;
const PREFIX_CONTROL_EXAMPLES_PER_TARGET = 3;

export const EXPECTED_SHARED_CORE_SAMPLE_IDS = Object.freeze(
  Array.from({ length: SHARED_CORE_LIMIT }, (_, index) => `mw-pwg-shared:${String(index + 1).padStart(2, "0")}`)
);

export const EXPECTED_PREFIX_CONTROL_IDS = Object.freeze([
  "xref-prefix-control:pwg:01",
  "xref-prefix-control:pwg:02",
  "xref-prefix-control:pwg:03",
  "xref-prefix-control:pwg:04",
  "xref-prefix-control:pwg:05",
  "xref-prefix-control:mw:01",
  "xref-prefix-control:mw:02",
  "xref-prefix-control:mw:03",
  "xref-prefix-control:mw:04",
  "xref-prefix-control:mw:05"
]);

// The closed label vocabulary. Each entry carries not just a one-line `meaning`
// but the decision rule a reviewer actually needs: what the label asserts, what
// it explicitly does NOT assert, and two worked examples drawn from this very
// packet. H1646: the previous one-line-per-label form was unusable at the sheet —
// a reviewer was asked to choose between `prefix-convention`, `normalization-risk`
// and `too-sparse` with no definition of any of them on screen.
//
// `appliesToSheet: false` marks labels the hub classifier uses upstream but that
// are NOT offered as answers on the 40-edge shared-core sheet; they are documented
// so the vocabulary reads as a whole, not rendered as choices.
export const XREF_LABEL_VOCABULARY = Object.freeze([
  {
    label: "lexical-shared-core",
    appliesToSheet: true,
    meaning: "The same source lemma points to the same meaningful Sanskrit target in MW and PWG.",
    asserts:
      "Both dictionaries, independently, print a cross-reference from this headword to this target, "
      + "and the target is a real lemma rather than a markup convention. Two editorial traditions "
      + "made the same link.",
    doesNotAssert:
      "NOT that the two words are synonyms. NOT a claim about what kind of relation it is "
      + "(variant spelling, derivative, cognate root, homophone) or in which direction it runs. "
      + "A vṛddhi derivative, a -ka suffix formation and a dialectal by-form all qualify equally: "
      + "the question is only whether the shared edge is real and lexical.",
    examples: [
      {
        sampleId: "mw-pwg-shared:09",
        edge: "Awi -> Aqi (āṭi -> āḍi)",
        why:
          "MW prints '(cf. Aqi and Ati)' and PWG prints 'Vgl. Aqi und Ati' for the same bird name "
          + "(Turdus Ginginianus). Two independent editors recorded the same by-form link."
      },
      {
        sampleId: "mw-pwg-shared:14",
        edge: "BI -> Byas (bhī -> bhyas)",
        why:
          "A derivational/etymological relation between the root bhī 'fear' and bhyas, carried by both "
          + "dictionaries. Not synonyms, and that is fine — the edge is still lexical, not an artifact."
      }
    ]
  },
  {
    label: "prefix-convention",
    appliesToSheet: true,
    meaning: "The target is primarily a prefix or compound-reference convention, not rare lexical inheritance.",
    asserts:
      "The cross-reference target is not a headword at all but a piece of the dictionary's own "
      + "abbreviation machinery — a truncated compound member, or a prefix cited as a form.",
    doesNotAssert:
      "NOT that the entry is wrong or the reference useless — only that it is house style for "
      + "compressing compounds, so it carries no evidence about lexical descent.",
    examples: [
      {
        sampleId: "xref-prefix-control:pwg:01",
        edge: "target 'a˚' (320 references in PWG)",
        why:
          "'˚' is CDSL's truncation ring: 'a˚' abbreviates 'the compound beginning in a-', not a lemma. "
          + "Auto-resolved by this packet on the marker alone."
      },
      {
        sampleId: "xref-prefix-control:mw:05",
        edge: "target 'aBi-' (11 references in MW)",
        why:
          "The trailing hyphen marks a prefix cited as a compound-forming element — same house-style "
          + "class as the ring, different mark."
      }
    ]
  },
  {
    label: "normalization-risk",
    appliesToSheet: true,
    meaning: "A target string where normalization may create or hide an edge.",
    asserts:
      "The edge may exist only because the pipeline folded MW and PWG spellings together. "
      + "m6_xref_lineage.py strips MW's '-'/accent marks and PWG's '°' before intersecting, so two "
      + "headwords the dictionaries spelt differently can meet in the middle. Reach for this label "
      + "when source and target differ ONLY in vowel length, accent, or a diacritic the normaliser touches.",
    doesNotAssert:
      "NOT that the words are unrelated — a length variant is often a genuine by-form. It flags that "
      + "THIS edge is not independent evidence, because the matching step could have manufactured it.",
    examples: [
      {
        sampleId: "mw-pwg-shared:30",
        edge: "BuHKAra -> BUHKAra (buhkāra -> būhkāra)",
        why:
          "Source and target differ only in the length of the first vowel, and the reciprocal edge "
          + "mw-pwg-shared:15 runs the other way. A spelling pair, plausibly an artifact of which form "
          + "each dictionary chose as headword."
      },
      {
        sampleId: "mw-pwg-shared:21",
        edge: "BastrakA -> BastrAkA (bhastrakā -> bhastrākā)",
        why: "Same shape: only the placement of vowel length distinguishes the two strings."
      }
    ]
  },
  {
    label: "too-sparse",
    appliesToSheet: true,
    meaning: "A pair has too few shared sources for lineage interpretation.",
    asserts:
      "The evidence on the card is too thin to answer either way — typically only ONE dictionary's "
      + "record is attached (`missingExactEdgeDictionaries` is non-empty), so the 'shared' in "
      + "shared-core is not actually demonstrated here.",
    doesNotAssert:
      "NOT a rejection of the edge. It is the honest answer when the card does not contain what the "
      + "question asks about — prefer it to guessing.",
    examples: [
      {
        sampleId: "mw-pwg-shared:07",
        edge: "ArAt -> Are (ārāt -> āre), PWG only",
        why:
          "Only the PWG record is attached; MW has no exact edge row. PWG's record shows an ablative "
          + "adverb pointing at a locative-shaped one, and there is no MW side to corroborate a shared "
          + "editorial judgement."
      },
      {
        sampleId: "mw-pwg-shared:03",
        edge: "Akzit -> anAkzit (ākṣit -> anākṣit), PWG only",
        why: "Single-dictionary evidence again: 4 of the 40 rows are in this state and are marked as such on the card."
      }
    ]
  },
  {
    label: "edition-continuity",
    appliesToSheet: false,
    meaning: "A stable edge across editions of the same dictionary family.",
    asserts: "Used by the upstream hub classifier for within-family (e.g. PW/PWG) edges.",
    doesNotAssert: "Not an answer option on the MW/PWG shared-core sheet, which is cross-family by construction.",
    examples: []
  },
  {
    label: "lexical-target",
    appliesToSheet: false,
    meaning: "A top xref target that behaves like an ordinary lexical target rather than a convention hub.",
    asserts:
      "A property of a TARGET string in the hub profile (classifyHubTarget in build-xref-hub-review.mjs), "
      + "carried on each row as `hubClass`. It is the reason a row reached this sheet, not a verdict on it.",
    doesNotAssert: "Not an answer option; it describes the target, not the edge.",
    examples: []
  }
]);

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

// H1646 raised this from 260. At 260 the PWG side of a long record was cut
// mid-sense ("... 1〉 aus der Ferne, von fern; fern, ...") and the reviewer could
// not see whether the cross-reference clause the edge rests on was even present.
// 900 keeps whole records for the shared-core sample while staying compact.
const EXCERPT_LENGTH = 900;

function compactText(value, length = EXCERPT_LENGTH) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1)}...` : text;
}

function edgeKey(dict, k1, target) {
  return `${String(dict).toLowerCase()}\u0000${k1}\u0000${target}`;
}

function recordKey(dict, L) {
  return `${String(dict).toLowerCase()}\u0000${L}`;
}

function pointerKey(edge, role) {
  return `${role}\u0000${String(edge.dict).toLowerCase()}\u0000${edge.L}\u0000${edge.k1}\u0000${edge.target}`;
}

function labelSet() {
  return new Set(XREF_LABEL_VOCABULARY.map(row => row.label));
}

function indexExactEdges(edgeRows) {
  const index = new Map();
  for (const row of edgeRows) {
    const key = edgeKey(row.dict, row.k1, row.target);
    if (!index.has(key)) index.set(key, []);
    index.get(key).push(row);
  }
  return index;
}

function sourceEdgesForSharedSample(sample, exactEdgeIndex) {
  return ["mw", "pwg"].flatMap(dict => exactEdgeIndex.get(edgeKey(dict, sample.sourceLemma, sample.target)) ?? []);
}

function prefixTargetsFor(hubReview, dict) {
  const profile = (hubReview.hubProfiles ?? []).find(row => row.code === dict);
  if (!profile) return [];
  return (profile.topTargets ?? [])
    .filter(row => row.hubClass === "prefix-convention")
    .slice(0, PREFIX_CONTROL_TARGETS_PER_DICT);
}

function selectPrefixControlSpecs(hubReview, edgeRows) {
  const specs = [];
  for (const dict of ["pwg", "mw"]) {
    for (const [index, target] of prefixTargetsFor(hubReview, dict).entries()) {
      const sampleEdges = edgeRows
        .filter(row => row.dict === dict && row.target === target.target)
        .slice(0, PREFIX_CONTROL_EXAMPLES_PER_TARGET);
      specs.push({
        controlId: `xref-prefix-control:${dict}:${String(index + 1).padStart(2, "0")}`,
        dictionary: dict,
        target: target.target,
        targetRank: index + 1,
        targetCount: target.count,
        hubClass: target.hubClass,
        interpretation: target.interpretation,
        sampleEdges
      });
    }
  }
  return specs;
}

function neededSourceRecords(edgeRows) {
  const needed = new Map();
  for (const row of edgeRows) {
    const dict = String(row.dict).toLowerCase();
    if (!needed.has(dict)) needed.set(dict, new Set());
    needed.get(dict).add(String(row.L));
  }
  return needed;
}

function buildSourceRecordIndex(edgeRows) {
  const needed = neededSourceRecords(edgeRows);
  const index = new Map();
  const warnings = [];
  for (const [dict, Ls] of needed) {
    if (!dictExists(dict)) {
      warnings.push(`Missing source dictionary ${dict}; source pointers for ${dict.toUpperCase()} retain xref_edges.csv L values only.`);
      continue;
    }
    for (const rec of iterateDict(dict)) {
      if (!Ls.has(String(rec.L))) continue;
      index.set(recordKey(dict, rec.L), {
        L: String(rec.L),
        line: rec.startLine,
        href: rec.href,
        pc: rec.pc ?? null,
        sourceLemma: rec.k1,
        bodyExcerpt: compactText(rec.body)
      });
    }
  }
  return { index, warnings };
}

export function preservedSourcePointerMap(packet) {
  const preserved = new Map();
  for (const row of [...(packet.sharedCoreRows ?? []), ...(packet.prefixControlRows ?? [])]) {
    for (const pointer of row.sourcePointers ?? []) {
      preserved.set(pointerKey({
        dict: pointer.dict,
        L: pointer.L,
        k1: pointer.sourceLemma,
        target: pointer.target
      }, pointer.role), pointer);
    }
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

function pointerForEdge(edge, sourceRecordIndex, role, preservedSourcePointers = new Map()) {
  const source = sourceRecordIndex.get(recordKey(edge.dict, edge.L));
  const preserved = preservedSourcePointers.get(pointerKey(edge, role));
  // Cologne links are derived from (dict, headword, <pc>) alone, so a pointer
  // recovered from a previous packet still gets them — they do not depend on
  // csl-orig being present in this run.
  const pc = source?.pc ?? preserved?.pc ?? null;
  const headword = source?.sourceLemma ?? preserved?.sourceRecordLemma ?? edge.k1;
  const cologne = cologneLinksFor(edge.dict, headword, pc);
  if (!source && preserved) return { ...preserved, pc, ...cologne };
  return {
    role,
    dictionary: String(edge.dict).toUpperCase(),
    dict: edge.dict,
    L: edge.L,
    line: source?.line ?? preserved?.line ?? null,
    pc,
    href: source?.href ?? preserved?.href ?? null,
    ...cologne,
    sourceLemma: edge.k1,
    sourceRecordLemma: source?.sourceLemma ?? preserved?.sourceRecordLemma ?? null,
    target: edge.target,
    kind: edge.kind,
    bodyExcerpt: source?.bodyExcerpt ?? preserved?.bodyExcerpt ?? ""
  };
}

// A cross-reference has two ends, and the packet only ever carried records for the
// SOURCE end. Asking "is ARi -> aRi a real lexical edge?" while showing only the ARi
// entries makes the question unanswerable — H1646: "you do not give links to Cologne,
// to check what the entries actually contain, both aRi and ARi". These are the target
// end: a Cologne lookup of the target headword in each dictionary.
//
// Built from the target string, so it is only emitted when that string is a plain
// SLP1 headword. A truncation/prefix target (a˚, aBi-) is not a lemma and would send
// the reviewer to an empty result, which is worse than no link.
function isLookupableHeadword(target) {
  return /^[A-Za-z]+$/.test(String(target ?? ""));
}

function targetLinksFor(target) {
  if (!isLookupableHeadword(target)) return [];
  return ["mw", "pwg"]
    .map(dict => ({
      role: "target-lookup",
      dictionary: dict.toUpperCase(),
      dict,
      headword: target,
      cologneEntryHref: entryUrl(dict, target)
    }))
    .filter(link => link.cologneEntryHref);
}

function emptyHumanFields() {
  return {
    reviewStatus: "needs-source-check",
    reviewedValue: null,
    reviewer: "",
    reviewedAt: "",
    note: ""
  };
}

function sharedReviewQuestion(row) {
  return `Do the MW/PWG source records support ${row.sourceLemma} -> ${row.target} as a meaningful shared lexical xref rather than a normalization or convention artifact?`;
}

function prefixReviewQuestion(row) {
  return `Do the sampled ${row.dictionary.toUpperCase()} references to ${row.target} behave as prefix/compound convention rather than lexical lineage evidence?`;
}

function buildSharedCoreRows(hubReview, exactEdgeIndex, sourceRecordIndex, preservedSourcePointers = new Map()) {
  return (hubReview.sharedCoreSample ?? []).slice(0, SHARED_CORE_LIMIT).map(sample => {
    const sourceEdges = sourceEdgesForSharedSample(sample, exactEdgeIndex);
    const matched = new Set(sourceEdges.map(row => row.dict.toUpperCase()));
    const row = {
      sampleId: sample.sampleId,
      sampleClass: "shared-core",
      sourceLemma: sample.sourceLemma,
      target: sample.target,
      hubClass: sample.hubClass,
      proposedLabels: [sample.reviewLabel],
      machineInterpretation: sample.interpretation,
      sourcePointers: sourceEdges.map(edge => pointerForEdge(edge, sourceRecordIndex, "exact-shared-edge", preservedSourcePointers)),
      targetLinks: targetLinksFor(sample.target),
      matchedDictionaries: [...matched].sort(),
      missingExactEdgeDictionaries: ["MW", "PWG"].filter(dict => !matched.has(dict)),
      reviewQuestion: sharedReviewQuestion(sample),
      ...emptyHumanFields()
    };
    return row;
  });
}

function buildPrefixControlRows(prefixSpecs, sourceRecordIndex, preservedSourcePointers = new Map()) {
  return prefixSpecs.map(spec => ({
    controlId: spec.controlId,
    sampleClass: "prefix-control",
    dictionary: spec.dictionary.toUpperCase(),
    dict: spec.dictionary,
    target: spec.target,
    targetRank: spec.targetRank,
    targetCount: spec.targetCount,
    hubClass: spec.hubClass,
    proposedLabels: ["prefix-convention"],
    machineInterpretation: spec.interpretation,
    sourcePointers: spec.sampleEdges.map(edge => pointerForEdge(edge, sourceRecordIndex, "prefix-control-example", preservedSourcePointers)),
    reviewQuestion: prefixReviewQuestion(spec),
    ...emptyHumanFields()
  }));
}

function validatePayload(payload) {
  const errors = [];
  const allowed = labelSet();
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (payload.sharedCoreRows.length !== SHARED_CORE_LIMIT) {
    errors.push(`expected ${SHARED_CORE_LIMIT} shared-core rows, got ${payload.sharedCoreRows.length}`);
  }
  const sharedIds = payload.sharedCoreRows.map(row => row.sampleId);
  if (sharedIds.join("|") !== EXPECTED_SHARED_CORE_SAMPLE_IDS.join("|")) {
    errors.push(`shared-core row order changed: ${sharedIds.join(", ")}`);
  }
  const prefixIds = payload.prefixControlRows.map(row => row.controlId);
  if (prefixIds.join("|") !== EXPECTED_PREFIX_CONTROL_IDS.join("|")) {
    errors.push(`prefix-control row order changed: ${prefixIds.join(", ")}`);
  }
  if (payload.prefixControlRows.length !== EXPECTED_PREFIX_CONTROL_IDS.length) {
    errors.push(`expected ${EXPECTED_PREFIX_CONTROL_IDS.length} prefix-control rows, got ${payload.prefixControlRows.length}`);
  }
  for (const row of [...payload.sharedCoreRows, ...payload.prefixControlRows]) {
    const id = row.sampleId ?? row.controlId;
    if (!row.sourcePointers.length) errors.push(`${id}: missing source pointers`);
    if (!row.reviewQuestion) errors.push(`${id}: missing review question`);
    const autoResolved = row.autoTriage?.resolved === true;
    if (row.reviewStatus !== "needs-source-check" && row.reviewStatus !== "auto-resolved") {
      errors.push(`${id}: reviewStatus must be needs-source-check or auto-resolved`);
    }
    if (autoResolved !== (row.reviewStatus === "auto-resolved")) errors.push(`${id}: reviewStatus/autoTriage disagree`);
    if (autoResolved && !allowed.has(row.autoTriage.proposedDecision)) errors.push(`${id}: auto decision ${row.autoTriage.proposedDecision} out of vocabulary`);
    if (row.reviewedValue !== null) errors.push(`${id}: reviewedValue must stay null`);
    if (row.reviewer !== "") errors.push(`${id}: reviewer must stay empty`);
    if (row.reviewedAt !== "") errors.push(`${id}: reviewedAt must stay empty`);
    if (row.note !== "") errors.push(`${id}: note must stay empty`);
    for (const label of row.proposedLabels ?? []) {
      if (!allowed.has(label)) errors.push(`${id}: out-of-vocabulary label ${label}`);
    }
    for (const pointer of row.sourcePointers) {
      if (!pointer.dictionary || !pointer.L || !pointer.sourceLemma || !pointer.target) {
        errors.push(`${id}: incomplete source pointer`);
      }
      if (!pointer.href) errors.push(`${id}: source pointer ${pointer.dictionary} L${pointer.L} lacks href`);
      if (!pointer.cologneEntryHref) {
        errors.push(`${id}: source pointer ${pointer.dictionary} L${pointer.L} lacks cologneEntryHref`);
      }
    }
  }
  // Every shared-core row must let the reviewer read BOTH ends of the edge. A row
  // whose target is not a lookupable headword is a finding in itself, not a silent gap.
  for (const row of payload.sharedCoreRows) {
    if (!row.targetLinks?.length) {
      errors.push(`${row.sampleId}: no target-end Cologne links for target ${row.target}`);
    }
  }
  for (const row of payload.prefixControlRows) {
    if (row.sourcePointers.length !== PREFIX_CONTROL_EXAMPLES_PER_TARGET) {
      errors.push(`${row.controlId}: expected ${PREFIX_CONTROL_EXAMPLES_PER_TARGET} source examples`);
    }
  }
  if (payload.counts.sharedCoreRows !== payload.sharedCoreRows.length) errors.push("sharedCoreRows count mismatch");
  if (payload.counts.prefixControlRows !== payload.prefixControlRows.length) errors.push("prefixControlRows count mismatch");
  if (payload.counts.sourceCheckRows !== payload.sharedCoreRows.length + payload.prefixControlRows.length) {
    errors.push("sourceCheckRows count mismatch");
  }
  if (errors.length) {
    const error = new Error(`Xref source-check packet build failed with ${errors.length} error(s):\n${errors.map(line => `  - ${line}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

// Deterministic auto-triage. A cross-reference TARGET that is a truncation/prefix
// form — it carries the CDSL abbreviation ring "˚" or ends in a prefix hyphen "-"
// (e.g. a˚, su˚, aBi-) — is a prefix-convention hub by the dictionary's own markup,
// not a rare lexical inheritance, so auto-resolve it to `prefix-convention`
// (recording the target as evidence). The shared-core lexical edges, whose question
// is whether a genuine MW/PWG edge is *meaningful*, have no mechanical proof and
// stay for human source-check. String-only on the target, so no csl-orig is read.
function isTruncationTarget(target) {
  const t = target ?? "";
  return t.includes("˚") || t.endsWith("-");
}

export function applyAutoTriage(rows) {
  for (const row of rows) {
    if (isTruncationTarget(row.target)) {
      row.autoTriage = {
        resolved: true,
        proposedDecision: "prefix-convention",
        basis: "target-truncation-marker",
        evidence: { target: row.target }
      };
      row.reviewStatus = "auto-resolved";
    } else {
      row.autoTriage = { resolved: false };
    }
  }
  return rows;
}

export function buildPayload(hubReview, edgeRows, generatedAt = new Date().toISOString(), preservedSourcePointers = new Map()) {
  const exactEdgeIndex = indexExactEdges(edgeRows);
  const sharedSourceEdges = (hubReview.sharedCoreSample ?? [])
    .slice(0, SHARED_CORE_LIMIT)
    .flatMap(sample => sourceEdgesForSharedSample(sample, exactEdgeIndex));
  const prefixSpecs = selectPrefixControlSpecs(hubReview, edgeRows);
  const prefixSourceEdges = prefixSpecs.flatMap(spec => spec.sampleEdges);
  const { index: sourceRecordIndex, warnings } = buildSourceRecordIndex([...sharedSourceEdges, ...prefixSourceEdges]);
  const sharedCoreRows = buildSharedCoreRows(hubReview, exactEdgeIndex, sourceRecordIndex, preservedSourcePointers);
  const prefixControlRows = buildPrefixControlRows(prefixSpecs, sourceRecordIndex, preservedSourcePointers);
  const allRows = applyAutoTriage([...sharedCoreRows, ...prefixControlRows]);
  const unresolvedSourcePointers = allRows.flatMap(row => row.sourcePointers).filter(pointer => !pointer.href);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "xref-source-check-packet",
    claim: "XREF-CORE source checking must keep MW/PWG lexical shared-core rows separate from PWG/MW prefix-convention hub controls.",
    evidenceLabel: "derived-source-pointers",
    reviewStatus: "needs-source-check",
    ownerRepo: "csl-atlas",
    generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "data/lexico/xref_hub_review.json",
      "data/lexico/xref_edges.csv",
      "scripts/build-xref-hub-review.mjs",
      "scripts/build-xref-source-check-packet.mjs",
      "../csl-orig/v02/mw/mw.txt",
      "../csl-orig/v02/pwg/pwg.txt"
    ],
    sourceArtifact: {
      path: "data/lexico/xref_hub_review.json",
      generatedBy: hubReview.generatedBy,
      sourceGeneratedAt: hubReview.sourceGeneratedAt,
      sharedCoreSample: hubReview.counts?.sharedCoreSample ?? null
    },
    packetLabelVocabulary: XREF_LABEL_VOCABULARY,
    counts: {
      sourceCheckRows: allRows.length,
      autoResolved: allRows.filter(row => row.autoTriage?.resolved).length,
      needsHumanReview: allRows.filter(row => !row.autoTriage?.resolved).length,
      byAutoDecision: countBy(allRows.filter(row => row.autoTriage?.resolved), row => row.autoTriage.proposedDecision),
      sharedCoreRows: sharedCoreRows.length,
      prefixControlRows: prefixControlRows.length,
      sourcePointerRows: allRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      exactSharedCorePointers: sharedCoreRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      sharedCoreRowsWithMissingExactEdge: sharedCoreRows.filter(row => row.missingExactEdgeDictionaries.length).length,
      prefixControlPointers: prefixControlRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      bySampleClass: countBy(allRows, row => row.sampleClass),
      byProposedLabel: countBy(allRows.flatMap(row => row.proposedLabels), label => label),
      prefixControlsByDictionary: countBy(prefixControlRows, row => row.dict)
    },
    // H1646: the reviewer could not see "the list of methods used for sampling these
    // words", so this now states the actual mechanism end to end, including the
    // selection bias, rather than only the steps this script performs.
    selectionPolicy: [
      "Stage 1 — build the candidate pool: scripts/lexico/m6_xref_lineage.py reads MW's and PWG's "
        + "cross-reference edges, normalises each target (strips MW's '-' and accent marks and PWG's "
        + "'°' ring), and writes the MW-intersect-PWG set to data/lexico/xref_shared_edges.csv. "
        + "That intersection is 642 edges.",
      "Stage 2 — take the sample: buildSharedCoreSample() in scripts/build-xref-hub-review.mjs takes "
        + "sharedEdges.slice(0, 40), i.e. the FIRST 40 rows of that CSV in file order.",
      "NOT A RANDOM SAMPLE, and the bias is visible on the sheet: the CSV is in headword order, so "
        + "all 40 cards are Ā-, B-, C-, D- and G-initial headwords. Findings from these 40 describe "
        + "the head of the alphabet, not the 642 as a whole. Re-running over a random or stratified "
        + "draw is a separate, unstarted job.",
      "Stage 3 — attach evidence: this script re-slices to 40, keeps the frozen sampleId order "
        + "(validatePayload rejects any reorder), and attaches the exact MW/PWG source records per edge "
        + "from xref_edges.csv, plus Cologne entry/scan links for both ends of the edge.",
      "Controls: the first five prefix-convention top targets for PWG and MW, with up to three source "
        + "examples each, are carried alongside as a contrast class; all ten auto-resolve on their "
        + "truncation marker and are not put to the reviewer.",
      "Deterministic throughout — no RNG anywhere in the three stages; re-running reproduces the same "
        + "40 cards in the same order.",
      "Labels on the cards are source-check prompts, not accepted lineage decisions."
    ],
    sharedCoreRows,
    prefixControlRows,
    limitations: [
      "Machine labels are review prompts only; this packet records no source-check decisions.",
      "The 40 shared-core rows are the first 40 of 642 shared edges in headword order, not a random "
        + "sample: every card is an Ā-, B-, C-, D- or G-initial headword. Do not generalise a rate "
        + "measured on these 40 to the full intersection.",
      "Cologne entry links resolve a HEADWORD, not this exact record: where a dictionary has homonyms "
        + "the lookup shows all of them. The csl-orig blob link is the pointer to the precise record.",
      "Some shared-core sample rows are present in the shared-edge sample but lack an exact MW edge row in xref_edges.csv; those rows remain visible with missing-exact-edge metadata.",
      "Prefix controls test convention pressure and are not optimization targets for lineage claims.",
      "Cross-reference overlap remains dictionary-internal evidence and must not be mixed with DCS/corpus co-occurrence.",
      "No R2 splitter behavior, source-anchor generation, H5 review row, public page, backend/runtime LLM, corpus, DCS, or standards work is changed."
    ],
    boundaryNote: "Atlas xref artifacts plus dictionary source pointers only; source checking is deferred to human review and does not promote parser or public-lineage behavior.",
    warnings: unresolvedSourcePointers.length ? warnings : []
  };
  validatePayload(payload);
  return payload;
}

function markdownCell(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/\|/g, "\\|");
}

function pointerMd(pointer) {
  const excerpt = pointer.bodyExcerpt ? ` - ${markdownCell(pointer.bodyExcerpt)}` : "";
  return `[${pointer.dictionary} L${pointer.L}](${pointer.href}) ${markdownCell(pointer.sourceLemma)} -> ${markdownCell(pointer.target)}${excerpt}`;
}

function countTable(title, counts) {
  return [
    `## ${title}`,
    "",
    "| Key | Rows |",
    "|---|---:|",
    ...Object.entries(counts).map(([key, count]) => `| \`${markdownCell(key)}\` | ${count} |`),
    ""
  ].join("\n");
}

function sharedCoreTable(rows) {
  return [
    "| Sample | Source lemma | Target | Proposed labels | Missing exact edge | Source pointers | Review question |",
    "|---|---|---|---|---|---|---|",
    ...rows.map(row => {
      const missing = row.missingExactEdgeDictionaries.length ? row.missingExactEdgeDictionaries.join(", ") : "none";
      return `| \`${row.sampleId}\` | \`${markdownCell(row.sourceLemma)}\` | \`${markdownCell(row.target)}\` | ${row.proposedLabels.map(label => `\`${label}\``).join(", ")} | ${missing} | ${row.sourcePointers.map(pointerMd).join("<br>")} | ${markdownCell(row.reviewQuestion)} |`;
    }),
    ""
  ].join("\n");
}

function prefixControlTable(rows) {
  return [
    "| Control | Dictionary | Target | Proposed labels | Source pointers | Review question |",
    "|---|---|---|---|---|---|",
    ...rows.map(row => `| \`${row.controlId}\` | \`${row.dictionary}\` | \`${markdownCell(row.target)}\` | ${row.proposedLabels.map(label => `\`${label}\``).join(", ")} | ${row.sourcePointers.map(pointerMd).join("<br>")} | ${markdownCell(row.reviewQuestion)} |`),
    ""
  ].join("\n");
}

export function buildMarkdown(payload) {
  const lines = [
    "# Xref Source-Check Packet",
    "",
    "Date: 2026-06-07",
    "",
    "Status: generated source-check packet; all rows remain `needs-source-check` and no human decisions are recorded.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.sharedCoreRows} shared-core rows, ${payload.counts.prefixControlRows} prefix-control rows, ${payload.counts.sourcePointerRows} source pointers.`,
    `- Auto-triage: ${payload.counts.autoResolved} of ${payload.counts.sourceCheckRows} rows deterministically auto-resolved as \`prefix-convention\` (the target carries a truncation marker \`˚\`/\`-\`, evidence in \`autoTriage.evidence.target\`); ${payload.counts.needsHumanReview} need human source-check. The shared-core lexical edges (is a genuine MW/PWG edge meaningful?) have no mechanical proof and stay for review; auto-resolved rows are overridable.`,
    `- Boundary note: ${payload.boundaryNote}`,
    "",
    "## Selection Policy",
    "",
    ...payload.selectionPolicy.map(item => `- ${item}`),
    "",
    countTable("Counts By Sample Class", payload.counts.bySampleClass),
    countTable("Counts By Proposed Label", payload.counts.byProposedLabel),
    countTable("Prefix Controls By Dictionary", payload.counts.prefixControlsByDictionary),
    "## Human Fields",
    "",
    "Every row keeps `reviewedValue = null`, `reviewer = \"\"`, `reviewedAt = \"\"`, and `note = \"\"`. Source-check decisions are outside this generated packet.",
    "",
    "## MW/PWG Shared-Core Rows",
    "",
    sharedCoreTable(payload.sharedCoreRows),
    "## PWG/MW Prefix Controls",
    "",
    prefixControlTable(payload.prefixControlRows),
    "## Limitations",
    "",
    ...payload.limitations.map(item => `- ${item}`),
    "",
    "## Boundary",
    "",
    `- ${payload.boundaryNote}`,
    ""
  ];
  return `${lines.join("\n")}\n`;
}

function main() {
  try {
    const hubReview = JSON.parse(fs.readFileSync(HUB_REVIEW_PATH, "utf8"));
    const edgeRows = parseCsv(fs.readFileSync(XREF_EDGES_PATH, "utf8"));
  const preservedSourcePointers = loadPreservedSourcePointers(JSON_OUT);
  const payload = buildPayload(hubReview, edgeRows, undefined, preservedSourcePointers);
  payload.generatedAt = generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
    fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
    fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
    fs.writeFileSync(MARKDOWN_OUT, buildMarkdown(payload));
    console.log(`Wrote ${payload.counts.sourceCheckRows} xref source-check rows to:`);
    console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
    console.log(`- ${path.relative(process.cwd(), MARKDOWN_OUT)}`);
    console.log(`Counts: ${JSON.stringify(payload.counts)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
