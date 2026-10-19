// H7101 — freeze the 500-row LLM candidate-lane evaluation sample.
//
// This builder is deliberately offline and deterministic. It freezes a
// held-out sample from two owner repos:
//
//   * csl-corrections correction_loci.tsv — one row per corrected source line
//     (old text / accepted new text). Gold edit type is a *weak* label derived
//     from the diff; it records what the human correction actually changed,
//     not a fresh editorial judgement.
//   * csl-atlas H5 anomaly review — rows whose reviewedValue is already human
//     adjudicated (possible-typo, parser-artifact, legitimate-form, ...).
//
// The committed sample is the frozen artifact. Re-freezing needs the upstream
// TSV and is gated behind --freeze so a rebuild can never silently reshuffle
// the evaluation set.
//
// Usage:
//   node scripts/build-llm-candidate-lane.mjs
//   node scripts/build-llm-candidate-lane.mjs --freeze \
//     --source /path/to/correction_loci.tsv
//
// No row is promoted to reviewed. Model outputs are candidates only.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { generatedAtNow, licenseFields, readJsonIfExists } from "./lib/dataset-meta.mjs";

export const LANE_DIR = path.join("data", "llm-candidate-lane");
export const SAMPLE_PATH = path.join(LANE_DIR, "sample-500.jsonl");
export const PROMPTS_PATH = path.join(LANE_DIR, "prompts.json");
export const SCHEMA_PATH = path.join(LANE_DIR, "provenance.schema.json");
export const MANIFEST_PATH = path.join(LANE_DIR, "manifest.json");
export const RULE_OUTPUT_PATH = path.join(LANE_DIR, "outputs", "rule-baseline.jsonl");
export const LLM_OUTPUT_PATH = path.join(LANE_DIR, "outputs", "llm-abstain.jsonl");
export const H5_REVIEW_PATH = path.join("src", "data", "review", "h5-anomaly-review.json");

export const TARGET_ROWS = 500;
export const SAMPLE_SEED = "H7101-2026-10-19";
export const SOURCE_COMMIT = "307bad2631a0f764138bbc98f77b04b92dfb7c41";
export const SOURCE_SHA256 = "4e89b93f48859c73c0eee9d41ab9c802888693cf651125bcc31504899399a907";

export const EDIT_TYPES = Object.freeze([
  "ocr-error",
  "sense-split",
  "source-mismatch",
  "markup-normalization",
  "no-correction"
]);

export const TARGET_ERROR_TYPES = Object.freeze(["ocr-error", "sense-split", "source-mismatch"]);

const CORRECTION_QUOTA = Object.freeze({
  "ocr-error": 100,
  "source-mismatch": 60,
  "sense-split": 17,
  "markup-normalization": 223
});

const H5_QUOTA = Object.freeze({
  "ocr-error": 22,
  "markup-normalization": 12,
  "no-correction": 66
});

const H5_LABEL_MAP = Object.freeze({
  "possible-typo": "ocr-error",
  "parser-artifact": "markup-normalization",
  "variant-convention": "markup-normalization",
  "legitimate-form": "no-correction",
  "lineage-only": "no-correction"
});

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function sortedHashOrder(rows, keyFn) {
  return [...rows].sort((a, b) => {
    const ha = sha256(`${SAMPLE_SEED}\0${keyFn(a)}`);
    const hb = sha256(`${SAMPLE_SEED}\0${keyFn(b)}`);
    return ha.localeCompare(hb) || keyFn(a).localeCompare(keyFn(b));
  });
}

/** Common-prefix/suffix diff. Returns the changed middle of `a` and `b`. */
export function diffSpan(a, b) {
  let prefix = 0;
  while (prefix < a.length && prefix < b.length && a[prefix] === b[prefix]) prefix += 1;
  let suffix = 0;
  while (
    suffix < a.length - prefix &&
    suffix < b.length - prefix &&
    a[a.length - 1 - suffix] === b[b.length - 1 - suffix]
  ) {
    suffix += 1;
  }
  return {
    prefix,
    old: a.slice(prefix, a.length - suffix),
    new: b.slice(prefix, b.length - suffix)
  };
}

function lastUnclosedTag(text, position, tag) {
  const open = text.lastIndexOf(`<${tag}`, position);
  if (open < 0) return false;
  const close = text.lastIndexOf(`</${tag}>`, position);
  return open > close;
}

function stripMarkup(text) {
  let current = text;
  let previous;
  do {
    previous = current;
    current = current.replace(/<[^>]*>/g, "");
  } while (current !== previous);
  return current.replace(/[\s\p{P}\p{S}]/gu, "");
}

/**
 * Weak gold edit type for a human correction pair.
 *
 * Order matters: citation text wins over punctuation, an added sense boundary
 * wins over ordinary punctuation churn, and a changed letter (case-insensitive)
 * is the only thing called an OCR/lexical error.
 */
export function classifyEdit(oldText, newText) {
  if (oldText === newText) return "no-correction";
  const diff = diffSpan(oldText, newText);
  const oldMid = diff.old;
  const newMid = diff.new;

  if (lastUnclosedTag(oldText, diff.prefix, "ls")) return "source-mismatch";
  if (lastUnclosedTag(oldText, diff.prefix, "pc") || lastUnclosedTag(oldText, diff.prefix, "L")) {
    return "markup-normalization";
  }

  const count = (text, re) => (text.match(re) || []).length;
  const addedSeparators = count(newMid, /[;|]/g) - count(oldMid, /[;|]/g);
  const addedDivs = count(newMid, /<div/g) - count(oldMid, /<div/g);
  const addedSenseNumbers = count(newMid, /[—–-]\s*\d+\)/g) - count(oldMid, /[—–-]\s*\d+\)/g);
  if (addedSeparators > 0 || addedDivs > 0 || addedSenseNumbers > 0) return "sense-split";

  const oldLetters = stripMarkup(oldMid);
  const newLetters = stripMarkup(newMid);
  if (oldLetters.toLowerCase() !== newLetters.toLowerCase()) return "ocr-error";
  return "markup-normalization";
}

function parseCorrectionTsv(tsv) {
  const lines = tsv.split(/\r?\n/).filter(Boolean);
  const header = lines.shift().split("\t");
  return lines.map(line => {
    const cells = line.split("\t");
    return Object.fromEntries(header.map((name, index) => [name, cells[index] ?? ""]));
  });
}

function rowKey(row) {
  return `${row.dict}\0${row.L}\0${row.line}\0${row.k1}\0${row.batch}`;
}

function correctionRecord(row) {
  const editType = classifyEdit(row.old, row.new);
  const gold = makeGold(editType, row.old, row.new, "weak-diff-label");
  const window = makeWindow(row.old, gold.span);
  if (window.windowStart > 0) {
    gold.span = {
      ...gold.span,
      start: Math.max(0, gold.span.start - window.windowStart),
      end: Math.max(0, gold.span.end - window.windowStart)
    };
  }
  return {
    id: `h7101:corr:${row.dict}:${row.L}:${row.line}`,
    source: "correction-loci",
    sourceRef: {
      repo: "csl-corrections",
      commit: SOURCE_COMMIT,
      path: "data/derived/correction_loci.tsv",
      dict: row.dict,
      L: row.L,
      line: row.line,
      process: row.process,
      batch: row.batch,
      batchDate: row.batch_date
    },
    input: window,
    gold,
    split: "eval"
  };
}

function makeWindow(text, span = null) {
  const maxChars = 1800;
  const focus = span ? span.start : Math.floor(text.length / 2);
  let start = Math.max(0, focus - Math.floor(maxChars / 2));
  let end = Math.min(text.length, start + maxChars);
  start = Math.max(0, Math.min(start, end - maxChars));
  return {
    text: text.slice(start, end),
    windowStart: start,
    windowEnd: end,
    truncated: start > 0 || end < text.length
  };
}

function makeGold(editType, oldText, newText, labelProvenance) {
  const diff = diffSpan(oldText, newText);
  const span = editType === "no-correction"
    ? null
    : {
      start: diff.prefix,
      end: diff.prefix + diff.old.length,
      text: diff.old
    };
  return {
    editType,
    needsCorrection: editType !== "no-correction",
    targetError: TARGET_ERROR_TYPES.includes(editType),
    span,
    labelProvenance,
    oldSha256: sha256(oldText),
    newSha256: sha256(newText)
  };
}

function h5Record(item) {
  const reviewed = typeof item.reviewedValue === "string" ? item.reviewedValue : "legitimate-form";
  const editType = H5_LABEL_MAP[reviewed] ?? "no-correction";
  const mv = item.machineValue ?? {};
  const pair =
    mv.petOld && mv.petNew ? { old: mv.petOld, new: mv.petNew }
      : mv.mwOld && mv.mwNew ? { old: mv.mwOld, new: mv.mwNew }
        : null;
  const fallback = editType === "no-correction"
    ? pair?.new ?? mv.headword ?? item.subject?.lemma ?? item.reviewId
    : pair?.old ?? mv.headword ?? item.subject?.lemma ?? item.reviewId;
  const gold = pair
    ? makeGold(editType, pair.old, pair.new, "human-reviewed")
    : {
      editType,
      needsCorrection: editType !== "no-correction",
      targetError: TARGET_ERROR_TYPES.includes(editType),
      span: null,
      labelProvenance: "human-reviewed",
      oldSha256: sha256(fallback),
      newSha256: null
    };
  const window = makeWindow(fallback, gold.span);
  if (gold.span && window.windowStart > 0) {
    gold.span = {
      ...gold.span,
      start: Math.max(0, gold.span.start - window.windowStart),
      end: Math.max(0, gold.span.end - window.windowStart)
    };
  }
  return {
    id: `h7101:h5:${item.reviewId}`,
    source: "review-queue",
    sourceRef: {
      repo: "csl-atlas",
      path: H5_REVIEW_PATH.split(path.sep).join("/"),
      reviewId: item.reviewId,
      queue: item.queue,
      reviewedValue: reviewed,
      reviewer: item.reviewer,
      reviewedAt: item.reviewedAt
    },
    input: window,
    gold,
    split: "eval"
  };
}

export function buildSample(correctionsTsv, h5Review) {
  const corrections = parseCorrectionTsv(correctionsTsv)
    .filter(row => row.process === "human")
    .filter(row => row.old !== row.new && row.old !== "<LEND>")
    .map(row => ({ row, editType: classifyEdit(row.old, row.new) }));

  const byType = new Map(EDIT_TYPES.map(type => [type, []]));
  for (const entry of corrections) byType.get(entry.editType)?.push(entry);

  const picked = [];
  for (const [type, quota] of Object.entries(CORRECTION_QUOTA)) {
    const ordered = sortedHashOrder(byType.get(type) ?? [], entry => rowKey(entry.row));
    if (ordered.length < quota) {
      throw new Error(`correction pool too small for ${type}: ${ordered.length} < ${quota}`);
    }
    picked.push(...ordered.slice(0, quota));
  }

  const h5Rows = [];
  for (const item of h5Review.items ?? []) {
    const record = h5Record(item);
    h5Rows.push({ record, editType: record.gold.editType });
  }
  const h5ByType = new Map(EDIT_TYPES.map(type => [type, []]));
  for (const entry of h5Rows) h5ByType.get(entry.editType)?.push(entry);
  const h5Picked = [];
  for (const [type, quota] of Object.entries(H5_QUOTA)) {
    const ordered = sortedHashOrder(h5ByType.get(type) ?? [], entry => entry.record.id);
    if (ordered.length < quota) {
      throw new Error(`H5 pool too small for ${type}: ${ordered.length} < ${quota}`);
    }
    h5Picked.push(...ordered.slice(0, quota));
  }

  const sample = [
    ...picked.map(entry => correctionRecord(entry.row)),
    ...h5Picked.map(entry => entry.record)
  ];
  if (sample.length !== TARGET_ROWS) {
    throw new Error(`sample has ${sample.length} rows, expected ${TARGET_ROWS}`);
  }
  return sample.sort((a, b) => a.id.localeCompare(b.id));
}

export function compositionOf(sample) {
  const byType = {};
  const bySource = {};
  for (const row of sample) {
    byType[row.gold.editType] = (byType[row.gold.editType] || 0) + 1;
    bySource[row.source] = (bySource[row.source] || 0) + 1;
  }
  return { byType, bySource };
}

export function renderPrompt(variant, row) {
  return variant.template
    .replaceAll("{{DICT}}", row.sourceRef.dict ?? "unknown")
    .replaceAll("{{LOCUS}}", row.sourceRef.L ?? row.sourceRef.reviewId ?? "unknown")
    .replaceAll("{{TEXT}}", row.input.text);
}

function promptPack() {
  const labelGuide = [
    "ocr-error — a letter inside lexical text (headword, gloss, or citation content) is wrong and should be corrected.",
    "sense-split — the correction inserts or removes a sense boundary (semicolon/pipe, <div>, or a numbered sense marker).",
    "source-mismatch — the correction changes the citation/source label inside <ls>...</ls> by more than punctuation or case.",
    "markup-normalization — punctuation, tags, whitespace, case, or metadata only; text is not lexically wrong.",
    "no-correction — the line is already acceptable; do not propose an edit."
  ].join("\n");
  const schema = [
    '{"editType":"ocr-error|sense-split|source-mismatch|markup-normalization|no-correction",',
    '"span":{"text":"exact changed text or empty string","start":0,"end":0},',
    '"confidence":0.0,"abstain":false,"rationale":"one sentence"}'
  ].join("");
  const variants = [
    {
      id: "P1",
      purpose: "zero-shot direct classification",
      template: [
        "You are auditing one line of a Sanskrit dictionary.",
        "Classify what kind of edit the line needs. Allowed labels:",
        labelGuide,
        "Source: {{DICT}} {{LOCUS}}",
        "Line:",
        "{{TEXT}}",
        "Return one JSON object and nothing else: " + schema,
        "Abstain (abstain=true) if the line has no defensible single edit. Never invent a correction."
      ].join("\n")
    },
    {
      id: "P2",
      purpose: "abstention-first, then classify",
      template: [
        "Step 1: decide whether this line contains a defensible editorial defect.",
        "Step 2: only if yes, classify it.",
        "Labels: " + EDIT_TYPES.join(", ") + ".",
        labelGuide,
        "Line ({{DICT}} {{LOCUS}}):",
        "{{TEXT}}",
        "JSON only: " + schema,
        "Prefer abstain=true over a low-confidence guess."
      ].join("\n")
    },
    {
      id: "P3",
      purpose: "span-first extraction",
      template: [
        "Find the smallest span in the line that a human editor would change.",
        "Then classify the change using these labels: " + EDIT_TYPES.join(", ") + ".",
        labelGuide,
        "Line ({{DICT}} {{LOCUS}}):",
        "{{TEXT}}",
        "Return JSON only. If no span is defensible, set abstain=true and span.text to an empty string.",
        schema
      ].join("\n")
    },
    {
      id: "P4",
      purpose: "critical-difference prompt with explicit null control",
      template: [
        "Two kinds of lines occur here: lines that were already acceptable and lines that a human corrected.",
        "For the line below, name the correction type and the exact changed span.",
        "Labels: " + EDIT_TYPES.join(", ") + ". " + labelGuide,
        "A markup-only change is still a correction, but it is not an OCR error.",
        "Line ({{DICT}} {{LOCUS}}):",
        "{{TEXT}}",
        "JSON only: " + schema,
        "Abstain when the evidence is insufficient; do not promote the row to reviewed."
      ].join("\n")
    },
    {
      id: "P5",
      purpose: "citation-aware classification",
      template: [
        "You are reviewing a Cologne Digital Sanskrit lexicon line.",
        "Pay special attention to <ls> citation content and to sense boundaries.",
        "Allowed labels: " + EDIT_TYPES.join(", ") + ". " + labelGuide,
        "Line ({{DICT}} {{LOCUS}}):",
        "{{TEXT}}",
        "Return JSON only: " + schema,
        "If the only change would be punctuation outside a citation, prefer markup-normalization."
      ].join("\n")
    },
    {
      id: "P6",
      purpose: "conservative production prompt (selected for a credentialed run)",
      template: [
        "Task: generate a candidate correction for one lexicon line, with span provenance.",
        "Do not rewrite the line. Do not mark anything reviewed. Output a candidate only.",
        "Allowed edit types and their meanings:",
        labelGuide,
        "Rules:",
        "1. span.text must be copied exactly from the input line.",
        "2. If two labels fit, choose the narrowest lexical label; use markup-normalization for punctuation only.",
        "3. If confidence < 0.6, set abstain=true and confidence to the measured value.",
        "Line ({{DICT}} {{LOCUS}}):",
        "{{TEXT}}",
        "Return exactly one JSON object: " + schema
      ].join("\n")
    }
  ];
  return {
    schemaVersion: "1.0.0",
    ...licenseFields(),
    dataset: "h7101_llm_candidate_prompts",
    task: "classify-and-span a candidate correction with confidence and abstention",
    selectedVariant: "P6",
    variants: variants.map(variant => ({
      ...variant,
      sha256: sha256(variant.template)
    })),
    labelGuide,
    outputSchema: schema
  };
}

function firstMatchSpan(text, re) {
  const match = re.exec(text);
  if (!match) return { text: "", start: 0, end: 0 };
  return { text: match[0], start: match.index, end: match.index + match[0].length };
}

function rulePrediction(row) {
  const text = row.input.text;
  const semicolons = (text.match(/;/g) || []).length;
  let editType = "markup-normalization";
  let confidence = 0.55;
  let rationale = "No high-precision surface trigger; default to markup normalization.";
  let span = { text: "", start: 0, end: 0 };

  if (/\uFFFD/.test(text) || /<s>[^<]*[A-Za-z][^<]*[\u0900-\u097F]/.test(text)) {
    editType = "ocr-error";
    confidence = 0.6;
    rationale = "Mixed script or replacement character inside lexical text.";
    span = firstMatchSpan(text, /<s>[^<]*[\u0900-\u097F][^<]*<\/s>/);
  } else if (/<ls>[^<]*[.,;:]<\/ls>/.test(text)) {
    editType = "source-mismatch";
    confidence = 0.58;
    rationale = "Citation content carries trailing punctuation inside <ls>.";
    span = firstMatchSpan(text, /<ls>[^<]*[.,;:]<\/ls>/);
  } else if ((text.match(/[¦|]/g) || []).length > 0 && semicolons >= 2 && !/<div/.test(text)) {
    editType = "sense-split";
    confidence = 0.52;
    rationale = "Several sense separators without an explicit <div> boundary.";
    span = firstMatchSpan(text, /[;|]/);
  }

  return {
    editType,
    span,
    confidence,
    abstain: false,
    rationale
  };
}

function outputRecord(row, prediction, run) {
  return {
    schemaVersion: "1.0.0",
    id: row.id,
    split: row.split,
    sourceRef: row.sourceRef,
    inputSha256: sha256(row.input.text),
    prompt: run.prompt,
    model: run.model,
    prediction,
    provenance: {
      editType: prediction.editType,
      source: row.source,
      model: run.model.name,
      confidence: prediction.confidence,
      abstain: prediction.abstain,
      revisionStatus: "machine-candidate",
      reviewedValue: null,
      reviewer: null,
      reviewedAt: null
    }
  };
}

function jsonl(rows) {
  return rows.map(row => JSON.stringify(row)).join("\n") + "\n";
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function writeJson(filePath, value) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function provenanceSchema() {
  return {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    $id: "https://sanskrit-lexicon.github.io/csl-atlas/data/llm-candidate-lane/provenance.schema.json",
    title: "H7101 LLM candidate span-provenance record",
    type: "object",
    required: ["schemaVersion", "id", "split", "sourceRef", "inputSha256", "prompt", "model", "prediction", "provenance"],
    additionalProperties: false,
    properties: {
      schemaVersion: { const: "1.0.0" },
      id: { type: "string", minLength: 1 },
      split: { enum: ["eval"] },
      sourceRef: {
        type: "object",
        required: ["repo", "path"],
        properties: {
          repo: { type: "string" },
          path: { type: "string" },
          commit: { type: "string" },
          dict: { type: "string" },
          L: { type: "string" },
          line: { type: "string" },
          process: { enum: ["human", "bulk"] },
          batch: { type: "string" },
          batchDate: { type: "string" },
          reviewId: { type: "string" },
          queue: { type: "string" },
          reviewedValue: { type: "string" },
          reviewer: { type: "string" },
          reviewedAt: { type: "string" }
        }
      },
      inputSha256: { type: "string", pattern: "^[0-9a-f]{64}$" },
      prompt: {
        type: "object",
        required: ["id", "version", "sha256"],
        properties: {
          id: { type: "string" },
          version: { type: "string" },
          sha256: { type: "string", pattern: "^[0-9a-f]{64}$" }
        }
      },
      model: {
        type: "object",
        required: ["provider", "name", "revision", "temperature"],
        properties: {
          provider: { type: "string" },
          name: { type: "string" },
          revision: { type: "string" },
          temperature: { type: "number" }
        }
      },
      prediction: {
        type: "object",
        required: ["editType", "span", "confidence", "abstain", "rationale"],
        properties: {
          editType: { enum: [...EDIT_TYPES, null] },
          span: {
            type: ["object", "null"],
            required: ["text", "start", "end"],
            properties: {
              text: { type: "string" },
              start: { type: "integer", minimum: 0 },
              end: { type: "integer", minimum: 0 }
            }
          },
          confidence: { type: "number", minimum: 0, maximum: 1 },
          abstain: { type: "boolean" },
          rationale: { type: "string" }
        }
      },
      provenance: {
        type: "object",
        required: ["editType", "source", "model", "confidence", "abstain", "revisionStatus", "reviewedValue", "reviewer", "reviewedAt"],
        properties: {
          editType: { enum: [...EDIT_TYPES, null] },
          source: { type: "string" },
          model: { type: "string" },
          confidence: { type: "number", minimum: 0, maximum: 1 },
          abstain: { type: "boolean" },
          revisionStatus: { const: "machine-candidate" },
          reviewedValue: { type: "null" },
          reviewer: { type: "null" },
          reviewedAt: { type: "null" }
        }
      }
    }
  };
}

function readSample(filePath) {
  return fs.readFileSync(filePath, "utf8").split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}

function main() {
  const args = process.argv.slice(2);
  const freeze = args.includes("--freeze");
  const sourceIndex = args.indexOf("--source");
  const sourcePath = sourceIndex >= 0 ? args[sourceIndex + 1] : null;

  if (freeze) {
    if (!sourcePath || !fs.existsSync(sourcePath)) {
      throw new Error("--freeze requires --source <correction_loci.tsv>");
    }
    const tsv = fs.readFileSync(sourcePath, "utf8");
    const h5 = JSON.parse(fs.readFileSync(H5_REVIEW_PATH, "utf8"));
    const sample = buildSample(tsv, h5);
    ensureDir(SAMPLE_PATH);
    fs.writeFileSync(SAMPLE_PATH, jsonl(sample));
    const frozenAt = generatedAtNow();
    console.log(`froze ${sample.length} rows to ${SAMPLE_PATH} at ${frozenAt}`);
  }

  if (!fs.existsSync(SAMPLE_PATH)) {
    throw new Error(`missing ${SAMPLE_PATH}; run with --freeze --source <tsv>`);
  }
  const sample = readSample(SAMPLE_PATH);
  if (sample.length !== TARGET_ROWS) {
    throw new Error(`committed sample has ${sample.length} rows, expected ${TARGET_ROWS}`);
  }

  const prompts = promptPack();
  writeJson(PROMPTS_PATH, prompts);

  const prompt = {
    id: prompts.selectedVariant,
    version: prompts.schemaVersion,
    sha256: prompts.variants.find(variant => variant.id === prompts.selectedVariant).sha256
  };

  const ruleModel = {
    provider: "csl-atlas",
    name: "surface-rule-baseline",
    revision: "H7101-v1",
    temperature: 0
  };
  const ruleRows = sample.map(row =>
    outputRecord(row, rulePrediction(row), { prompt, model: ruleModel })
  );
  writeJson(RULE_OUTPUT_PATH, { schemaVersion: "1.0.0", recordCount: ruleRows.length, rows: ruleRows });
  fs.writeFileSync(RULE_OUTPUT_PATH, jsonl(ruleRows));

  const llmModel = {
    provider: "not-run",
    name: "no-credentials-in-offline-unit",
    revision: "n/a",
    temperature: 0
  };
  const llmRows = sample.map(row =>
    outputRecord(
      row,
      {
        editType: null,
        span: null,
        confidence: 0,
        abstain: true,
        rationale: "LLM inference was not available in this offline unit; conservative abstention, no promotion."
      },
      { prompt, model: llmModel }
    )
  );
  writeJson(LLM_OUTPUT_PATH, { schemaVersion: "1.0.0", recordCount: llmRows.length, runStatus: "not-run-no-credentials", rows: llmRows });
  fs.writeFileSync(LLM_OUTPUT_PATH, jsonl(llmRows));

  writeJson(SCHEMA_PATH, provenanceSchema());

  const composition = compositionOf(sample);
  const previous = readJsonIfExists(MANIFEST_PATH, fs);
  const payload = {
    schemaVersion: "1.0.0",
    ...licenseFields(),
    dataset: "h7101_llm_candidate_lane",
    generatedAt: generatedAtNow(),
    samplePath: SAMPLE_PATH.split(path.sep).join("/"),
    sampleSha256: sha256(fs.readFileSync(SAMPLE_PATH)),
    recordCount: sample.length,
    seed: SAMPLE_SEED,
    frozen: true,
    split: "eval",
    sources: {
      "correction-loci": {
        repo: "csl-corrections",
        commit: SOURCE_COMMIT,
        path: "data/derived/correction_loci.tsv",
        sha256: SOURCE_SHA256
      },
      "review-queue": {
        repo: "csl-atlas",
        path: H5_REVIEW_PATH.split(path.sep).join("/")
      }
    },
    composition,
    prompts: {
      path: PROMPTS_PATH.split(path.sep).join("/"),
      selected: prompts.selectedVariant,
      variants: prompts.variants.length,
      sha256: sha256(fs.readFileSync(PROMPTS_PATH))
    },
    outputs: {
      ruleBaseline: {
        path: RULE_OUTPUT_PATH.split(path.sep).join("/"),
        sha256: sha256(fs.readFileSync(RULE_OUTPUT_PATH))
      },
      llm: {
        path: LLM_OUTPUT_PATH.split(path.sep).join("/"),
        sha256: sha256(fs.readFileSync(LLM_OUTPUT_PATH)),
        runStatus: "not-run-no-credentials"
      }
    },
    promotionPolicy: {
      autoPromote: false,
      revisionStatus: "machine-candidate",
      humanReviewRequired: true
    },
    boundary: "Candidate generation only. No row is promoted to reviewed; no full-corpus run before this 500-row evaluation is scored."
  };
  const stable = previous && previous.sampleSha256 === payload.sampleSha256 && previous.outputs?.llm?.sha256 === payload.outputs.llm.sha256
    ? previous.generatedAt
    : payload.generatedAt;
  payload.generatedAt = stable;
  writeJson(MANIFEST_PATH, payload);

  console.log(`sample rows: ${sample.length}`);
  console.log(`composition: ${JSON.stringify(composition)}`);
  console.log(`prompt variants: ${prompts.variants.length} (selected ${prompts.selectedVariant})`);
  console.log(`rule baseline: ${RULE_OUTPUT_PATH}`);
  console.log(`llm outputs: ${LLM_OUTPUT_PATH} (runStatus=not-run-no-credentials)`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
