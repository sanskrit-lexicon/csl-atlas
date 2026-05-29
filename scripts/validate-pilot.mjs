import fs from "fs";
import path from "path";

const root = process.cwd();
const errors = [];

function readJson(relativePath) {
  try {
    return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf-8"));
  } catch (error) {
    errors.push(`${relativePath}: ${error.message}`);
    return null;
  }
}

function check(condition, message) {
  if (!condition) errors.push(message);
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function sameFile(left, right) {
  if (!exists(left) || !exists(right)) return false;
  return fs.readFileSync(path.join(root, left)).equals(fs.readFileSync(path.join(root, right)));
}

const hardCases = readJson("data/pilot/hard-cases.json");
const hardCasesForApp = readJson("src/data/pilot/hard-cases.json");
const neutral = readJson("data/pilot/neutral-model.json");
const neutralForApp = readJson("src/data/pilot/neutral-model.json");
const reports = readJson("data/pilot/loss-reports.json");
const reportsForApp = readJson("src/data/pilot/loss-reports.json");
const reviewCases = readJson("data/pilot/review-cases.json");
const reviewCasesForApp = readJson("src/data/pilot/review-cases.json");
const lossSchema = readJson("data/schema/loss-report.schema.json");

const items = hardCases?.items || [];
const hardIds = items.map(item => item.id);
const hardIdSet = new Set(hardIds);
const artifactStems = hardIds.map(id => id.replace(/:/g, "-"));
const neutralIds = new Set((neutral || []).map(item => item.id));
const allowedReviewStatus = new Set(lossSchema?.items?.properties?.reviewStatus?.enum || []);
const allowedFailureClassification = new Set(lossSchema?.items?.properties?.failureClassification?.enum || []);

check(Array.isArray(items), "data/pilot/hard-cases.json must contain an items array");
check(items.length === 50, `expected 50 hard cases, found ${items.length}`);
check(hardCasesForApp?.items?.length === items.length, "src hard-cases JSON is out of sync");
check(neutral?.length === items.length, "neutral model count must match hard-case count");
check(neutralForApp?.length === neutral?.length, "src neutral-model JSON is out of sync");
check(Array.isArray(reports) && reports.length > 0, "loss reports must be a non-empty array");
check(reportsForApp?.length === reports?.length, "src loss-reports JSON is out of sync");
check(reviewCases?.items?.length === 15, `expected 15 review cases, found ${reviewCases?.items?.length || 0}`);
check(reviewCasesForApp?.items?.length === reviewCases?.items?.length, "src review-cases JSON is out of sync");

check(hardIds.every(id => /^mw-pwg-pwk:/.test(id)), "every hard case id must start with mw-pwg-pwk:");
check(new Set(hardIds).size === hardIds.length, "hard case ids must be unique");
check(
  new Set(artifactStems.map(stem => stem.toLowerCase())).size === artifactStems.length,
  "case artifact filenames must remain unique on case-insensitive filesystems"
);
for (const item of items) {
  check(neutralIds.has(item.id), `neutral model is missing ${item.id}`);
  for (const dict of ["mw", "pwg", "pwk"]) {
    check(item.records?.[dict]?.raw, `${item.id} is missing ${dict.toUpperCase()} raw record text`);
  }
}

const sourceString = JSON.stringify(hardCases?.sources || {});
check(!/[A-Za-z]:\\|\\\\Users\\\\|\/Users\/|\/home\//.test(sourceString), "hard-case sources must not contain local absolute paths");

for (const report of reports || []) {
  check(hardIdSet.has(report.caseId), `loss report points to unknown case ${report.caseId}`);
  check(["tei", "ontolex"].includes(report.target), `loss report ${report.id} has invalid target ${report.target}`);
  check(["clean", "partial", "lossy"].includes(report.status), `loss report ${report.id} has invalid status ${report.status}`);
  check(allowedReviewStatus.has(report.reviewStatus), `loss report ${report.id} has invalid reviewStatus ${report.reviewStatus}`);
  check(
    !report.failureClassification || allowedFailureClassification.has(report.failureClassification),
    `loss report ${report.id} has invalid failureClassification ${report.failureClassification}`
  );
}

check(sameFile("data/pilot/hard-cases.json", "src/data/pilot/hard-cases.json"), "hard-cases JSON differs between data/ and src/data/");
check(sameFile("data/pilot/neutral-model.json", "src/data/pilot/neutral-model.json"), "neutral-model JSON differs between data/ and src/data/");
check(sameFile("data/pilot/loss-reports.json", "src/data/pilot/loss-reports.json"), "loss-reports JSON differs between data/ and src/data/");
check(sameFile("data/pilot/review-cases.json", "src/data/pilot/review-cases.json"), "review-cases JSON differs between data/ and src/data/");

for (const loader of [
  "src/data/pilot/hard-cases.json.js",
  "src/data/pilot/neutral-model.json.js",
  "src/data/pilot/loss-reports.json.js"
]) {
  check(!exists(loader), `${loader} should not exist; Observable must load the real JSON file`);
}

for (const model of neutral || []) {
  const safeId = model.id.replace(/:/g, "-");
  const teiPath = `data/pilot/tei/${safeId}.xml`;
  const ontolexPath = `data/pilot/ontolex/${safeId}.json`;
  check(exists(teiPath), `missing TEI stub ${teiPath}`);
  check(exists(ontolexPath), `missing OntoLex stub ${ontolexPath}`);

  if (exists(teiPath)) {
    const xml = fs.readFileSync(path.join(root, teiPath), "utf-8");
    check(xml.includes(`<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="${safeId}">`), `${teiPath} has the wrong TEI id`);
    check(xml.includes(`<entry xml:id="${safeId}-entry"`), `${teiPath} has the wrong entry id`);
    check(!xml.includes("<L>") && !xml.includes("<k1>"), `${teiPath} appears to contain unescaped raw CDSL tags`);
  }

  if (exists(ontolexPath)) {
    const jsonld = readJson(ontolexPath);
    check(Array.isArray(jsonld?.["@graph"]) && jsonld["@graph"].length >= 5, `${ontolexPath} does not contain a modeled JSON-LD graph`);
  }
}

if (errors.length) {
  console.error(`Pilot validation failed with ${errors.length} problem(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Pilot validation passed: ${items.length} cases, ${neutral.length} neutral models, ${reports.length} loss reports.`);
