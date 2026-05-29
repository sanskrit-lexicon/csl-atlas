// Validate review reports against data/schema/review-report.schema.json.
//
// Lightweight, data-driven check (no external validator dependency): it reads
// the schema's required lists and enums and verifies every report file under
// src/data/review/ conforms. Also confirms each item carries a source link.
//
// Usage: npm run validate-review-reports

import fs from "node:fs";
import path from "node:path";

const SCHEMA_FILE = path.resolve(process.cwd(), "data", "schema", "review-report.schema.json");
const REVIEW_DIR = path.resolve(process.cwd(), "src", "data", "review");

const errors = [];
const notes = [];

const schema = JSON.parse(fs.readFileSync(SCHEMA_FILE, "utf8"));
const itemSchema = schema.properties.items.items;
const itemRequired = itemSchema.required || [];
const enums = {
  queue: itemSchema.properties.queue.enum,
  "subject.kind": itemSchema.properties.subject.properties.kind.enum,
  evidenceLevel: itemSchema.properties.evidenceLevel.enum,
  reviewStatus: itemSchema.properties.reviewStatus.enum
};

function validateFile(file) {
  const rel = path.relative(process.cwd(), file);
  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`${rel}: not valid JSON (${e.message})`);
    return;
  }
  if (!Array.isArray(doc.items)) {
    errors.push(`${rel}: missing required "items" array`);
    return;
  }
  let withLinks = 0;
  doc.items.forEach((item, i) => {
    const at = `${rel}[${i}]`;
    for (const req of itemRequired) {
      if (item[req] === undefined) errors.push(`${at}: missing required field "${req}"`);
    }
    if (item.queue && !enums.queue.includes(item.queue)) errors.push(`${at}: invalid queue "${item.queue}"`);
    if (item.subject?.kind && !enums["subject.kind"].includes(item.subject.kind))
      errors.push(`${at}: invalid subject.kind "${item.subject.kind}"`);
    if (item.evidenceLevel && !enums.evidenceLevel.includes(item.evidenceLevel))
      errors.push(`${at}: invalid evidenceLevel "${item.evidenceLevel}"`);
    if (item.reviewStatus && !enums.reviewStatus.includes(item.reviewStatus))
      errors.push(`${at}: invalid reviewStatus "${item.reviewStatus}"`);
    if (Array.isArray(item.sourcePointers) && item.sourcePointers.some(p => p.href)) withLinks += 1;
  });
  if (withLinks < doc.items.length) {
    errors.push(`${rel}: ${doc.items.length - withLinks} items lack a source link`);
  }
  const statuses = {};
  for (const item of doc.items) statuses[item.reviewStatus] = (statuses[item.reviewStatus] || 0) + 1;
  notes.push(`${rel}: ${doc.items.length} items, status breakdown ${JSON.stringify(statuses)}`);
}

if (!fs.existsSync(REVIEW_DIR)) {
  console.log("No src/data/review/ directory; nothing to validate.");
  process.exit(0);
}
const files = fs.readdirSync(REVIEW_DIR).filter(f => f.endsWith(".json"));
if (files.length === 0) {
  console.log("No review reports found in src/data/review/.");
  process.exit(0);
}
for (const f of files) validateFile(path.join(REVIEW_DIR, f));

for (const n of notes) console.log(`ok  ${n}`);
if (errors.length) {
  console.error(`\nFAILED with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  x ${e}`);
  process.exit(1);
}
console.log("\nReview reports valid against review-report.schema.json.");
