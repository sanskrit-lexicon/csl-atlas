// H7101 — validate every frozen candidate-lane row against the provenance
// schema, and prove that no row can carry a human-review status.
//
// Deliberately dependency-free: the repo has no JSON Schema library, and a
// schema check that silently ignores an unknown keyword is worse than no check.
// This validator therefore implements a small, closed subset of draft 2020-12
// and THROWS on any keyword it does not understand, so a schema edit cannot
// quietly weaken the gate.
//
// Usage:
//   node scripts/validate-llm-candidate-lane.mjs
//   node scripts/validate-llm-candidate-lane.mjs --llm data/llm-candidate-lane/outputs/llm-run.jsonl
//
// Exit code 0 = every row valid and no promotion; 1 = at least one violation.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

export const SAMPLE_PATH = path.join("data", "llm-candidate-lane", "sample-500.jsonl");
export const SCHEMA_PATH = path.join("data", "llm-candidate-lane", "provenance.schema.json");
export const DEFAULT_OUTPUTS = Object.freeze([
  path.join("data", "llm-candidate-lane", "outputs", "rule-baseline.jsonl"),
  path.join("data", "llm-candidate-lane", "outputs", "llm-abstain.jsonl")
]);

const EDIT_TYPES = Object.freeze([
  "ocr-error",
  "sense-split",
  "source-mismatch",
  "markup-normalization",
  "no-correction"
]);

const ANNOTATION_KEYWORDS = new Set(["$schema", "$id", "title", "description", "$comment", "examples", "default"]);
const ASSERTION_KEYWORDS = new Set([
  "type",
  "required",
  "properties",
  "additionalProperties",
  "enum",
  "const",
  "pattern",
  "minimum",
  "maximum",
  "minLength",
  "items"
]);

function typeOf(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (Number.isInteger(value)) return "integer";
  return typeof value;
}

function matchesType(value, expected) {
  const actual = typeOf(value);
  if (expected === "number") return actual === "number" || actual === "integer";
  return actual === expected;
}

function deepEqual(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

/**
 * Validate `value` against the closed JSON-Schema subset used by the lane.
 * Returns an array of `{path, message}` violations (empty = valid).
 */
export function validateAgainstSchema(schema, value, pointer = "$") {
  const errors = [];
  if (schema === true || schema === undefined) return errors;
  if (schema === false) {
    errors.push({ path: pointer, message: "schema is false" });
    return errors;
  }
  for (const keyword of Object.keys(schema)) {
    if (!ANNOTATION_KEYWORDS.has(keyword) && !ASSERTION_KEYWORDS.has(keyword)) {
      throw new Error(`unsupported schema keyword "${keyword}" at ${pointer} — refusing to validate with a silent gap`);
    }
  }

  if (schema.type !== undefined) {
    const expected = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!expected.some(type => matchesType(value, type))) {
      errors.push({ path: pointer, message: `expected type ${expected.join("|")}, got ${typeOf(value)}` });
      return errors;
    }
  }
  if (schema.const !== undefined && !deepEqual(value, schema.const)) {
    errors.push({ path: pointer, message: `expected const ${JSON.stringify(schema.const)}` });
  }
  if (schema.enum !== undefined && !schema.enum.some(candidate => deepEqual(value, candidate))) {
    errors.push({ path: pointer, message: `value ${JSON.stringify(value)} not in enum` });
  }
  if (typeof value === "string") {
    if (schema.pattern !== undefined && !new RegExp(schema.pattern, "u").test(value)) {
      errors.push({ path: pointer, message: `value does not match ${schema.pattern}` });
    }
    if (schema.minLength !== undefined && value.length < schema.minLength) {
      errors.push({ path: pointer, message: `shorter than minLength ${schema.minLength}` });
    }
  }
  if (typeof value === "number") {
    if (schema.minimum !== undefined && value < schema.minimum) {
      errors.push({ path: pointer, message: `below minimum ${schema.minimum}` });
    }
    if (schema.maximum !== undefined && value > schema.maximum) {
      errors.push({ path: pointer, message: `above maximum ${schema.maximum}` });
    }
  }
  if (Array.isArray(value) && schema.items !== undefined) {
    value.forEach((item, index) => {
      errors.push(...validateAgainstSchema(schema.items, item, `${pointer}[${index}]`));
    });
  }
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    for (const key of schema.required ?? []) {
      if (!(key in value)) errors.push({ path: `${pointer}.${key}`, message: "required property missing" });
    }
    for (const [key, childSchema] of Object.entries(schema.properties ?? {})) {
      if (key in value) errors.push(...validateAgainstSchema(childSchema, value[key], `${pointer}.${key}`));
    }
    if (schema.additionalProperties === false) {
      const allowed = new Set(Object.keys(schema.properties ?? {}));
      for (const key of Object.keys(value)) {
        if (!allowed.has(key)) errors.push({ path: `${pointer}.${key}`, message: "additional property not allowed" });
      }
    } else if (schema.additionalProperties !== undefined && typeof schema.additionalProperties !== "object") {
      throw new Error(`unsupported additionalProperties at ${pointer}`);
    }
  }
  return errors;
}

export function readJsonl(filePath) {
  return fs
    .readFileSync(filePath, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

function checkSpan(prediction, input) {
  const errors = [];
  if (prediction.abstain === true) {
    if (prediction.span !== null) errors.push("abstained row must carry span: null");
    return errors;
  }
  if (!prediction.span) return ["non-abstained row must carry a span object"];
  const { start, end, text } = prediction.span;
  if (!(Number.isInteger(start) && Number.isInteger(end))) errors.push("span start/end must be integers");
  if (start > end) errors.push(`span start ${start} > end ${end}`);
  if (input?.windowEnd !== undefined && end > input.windowEnd) {
    errors.push(`span end ${end} exceeds input window ${input.windowEnd}`);
  }
  if (typeof text !== "string") errors.push("span text must be a string");
  return errors;
}

/**
 * Full-lane validation. Returns `{ sampleRows, outputs: {path: errors[]}, errors }`.
 * Any error is a failed handoff (schema drift or a promotion attempt).
 */
export function validateLane({ samplePath = SAMPLE_PATH, schemaPath = SCHEMA_PATH, outputPaths = DEFAULT_OUTPUTS } = {}) {
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  const sample = readJsonl(samplePath);
  const errors = [];

  if (sample.length !== 500) errors.push(`${samplePath}: expected 500 rows, found ${sample.length}`);
  const sampleIds = new Set();
  for (const row of sample) {
    const pointer = `${samplePath}:${row.id ?? "?"}`;
    if (typeof row.id !== "string" || !row.id) errors.push(`${pointer}: missing id`);
    if (sampleIds.has(row.id)) errors.push(`${pointer}: duplicate id`);
    sampleIds.add(row.id);
    if (row.split !== "eval") errors.push(`${pointer}: split must be "eval"`);
    if (!EDIT_TYPES.includes(row.gold?.editType)) errors.push(`${pointer}: bad gold.editType`);
    for (const forbidden of ["reviewStatus", "reviewedValue", "reviewedBy", "reviewer", "reviewedAt"]) {
      if (row[forbidden] !== undefined) errors.push(`${pointer}: sample row carries review field ${forbidden}`);
    }
  }

  const outputs = {};
  for (const outputPath of outputPaths) {
    const outputErrors = [];
    const rows = readJsonl(outputPath);
    const seen = new Set();
    if (rows.length !== sample.length) {
      outputErrors.push(`${outputPath}: expected ${sample.length} rows, found ${rows.length}`);
    }
    rows.forEach((row, index) => {
      const pointer = `${outputPath}[${index}]`;
      for (const violation of validateAgainstSchema(schema, row, pointer)) {
        outputErrors.push(`${violation.path}: ${violation.message}`);
      }
      if (seen.has(row.id)) outputErrors.push(`${pointer}: duplicate id ${row.id}`);
      seen.add(row.id);
      if (!sampleIds.has(row.id)) outputErrors.push(`${pointer}: id ${row.id} is not in the frozen sample`);
      for (const violation of checkSpan(row.prediction ?? {}, sample.find(item => item.id === row.id)?.input)) {
        outputErrors.push(`${pointer}: ${violation}`);
      }
      if (row.provenance?.revisionStatus !== "machine-candidate") {
        outputErrors.push(`${pointer}: promotion attempt — revisionStatus is ${JSON.stringify(row.provenance?.revisionStatus)}`);
      }
      if (row.provenance?.reviewedValue !== null || row.provenance?.reviewer !== null || row.provenance?.reviewedAt !== null) {
        outputErrors.push(`${pointer}: promotion attempt — a reviewed* field is non-null`);
      }
    });
    for (const id of sampleIds) {
      if (!seen.has(id)) outputErrors.push(`${outputPath}: no candidate row for frozen id ${id}`);
    }
    outputs[outputPath] = outputErrors;
    errors.push(...outputErrors);
  }

  return { sampleRows: sample.length, outputs, errors };
}

function main() {
  const args = process.argv.slice(2);
  const outputPaths = [];
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === "--llm") outputPaths.push(args[index + 1]);
  }
  const report = validateLane({ outputPaths: outputPaths.length ? [...DEFAULT_OUTPUTS, ...outputPaths] : DEFAULT_OUTPUTS });
  if (report.errors.length) {
    console.error(`FAIL — ${report.errors.length} violation(s)`);
    for (const error of report.errors.slice(0, 40)) console.error(`  ${error}`);
    if (report.errors.length > 40) console.error(`  ... ${report.errors.length - 40} more`);
    process.exitCode = 1;
    return;
  }
  const total = Object.values(report.outputs).reduce((sum, errors) => sum + errors.length, 0);
  console.log(JSON.stringify({
    status: "OK",
    sampleRows: report.sampleRows,
    outputs: Object.fromEntries(Object.keys(report.outputs).map(key => [key, "valid"])),
    violations: total
  }, null, 2));
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main();
}
