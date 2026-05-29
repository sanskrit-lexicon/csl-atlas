import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const errors = [];
const warnings = [];
const PROFILE_VERSION = "ontolex-frac-profile-v0.1";
const VALIDATION_SCOPE = "full-50-ontolex-shacl-profile";

function safeCaseId(id) {
  return id.replace(/:/g, "-");
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function writeJson(relativePath, value) {
  const file = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function check(condition, message, bucket = errors) {
  if (!condition) bucket.push(message);
}

function asArray(value) {
  return Array.isArray(value) ? value : value ? [value] : [];
}

function validateShaclShapes() {
  const relative = "data/schema/ontolex-frac-profile.shacl.ttl";
  const file = path.join(root, relative);
  check(fs.existsSync(file), `${relative}: missing SHACL profile`);
  if (!fs.existsSync(file)) return;

  const shapes = fs.readFileSync(file, "utf8");
  for (const prefix of ["@prefix sh:", "@prefix ontolex:", "@prefix lexicog:", "@prefix frac:", "@prefix prov:", "@prefix csl:"]) {
    check(shapes.includes(prefix), `${relative}: missing ${prefix}`);
  }
  for (const shape of ["csl:LexicalEntryShape", "csl:SourceRecordShape", "csl:AttestationShape"]) {
    check(shapes.includes(shape), `${relative}: missing ${shape}`);
  }
  for (const required of [PROFILE_VERSION, VALIDATION_SCOPE, "ontolex:canonicalForm", "frac:attestation", "prov:wasDerivedFrom"]) {
    check(shapes.includes(required), `${relative}: missing required shape marker ${required}`);
  }
}

function nodeTypes(node) {
  return asArray(node?.["@type"]);
}

function validateCase(model, reviewIds) {
  const stem = safeCaseId(model.id);
  const jsonRelative = `data/pilot/ontolex/${stem}.json`;
  const ttlRelative = `data/pilot/rdf/${stem}.ttl`;
  const jsonFile = path.join(root, jsonRelative);
  const ttlFile = path.join(root, ttlRelative);
  const caseErrors = [];
  const caseWarnings = [];
  const caseCheck = (condition, message) => check(condition, `${jsonRelative}: ${message}`, caseErrors);
  const caseWarn = (condition, message) => check(condition, `${jsonRelative}: ${message}`, caseWarnings);

  caseCheck(fs.existsSync(jsonFile), "missing OntoLex JSON-LD file");
  caseCheck(fs.existsSync(ttlFile), `missing RDF/Turtle mirror ${ttlRelative}`);
  if (!fs.existsSync(jsonFile) || !fs.existsSync(ttlFile)) {
    return {id: model.id, key: model.key, status: "fail", errors: caseErrors, warnings: caseWarnings};
  }

  const doc = readJson(jsonRelative);
  const graph = doc["@graph"] || [];
  const context = doc["@context"] || {};
  const ttl = fs.readFileSync(ttlFile, "utf8");
  const expectedStatus = reviewIds.has(model.id) ? "validated-slice" : "full-50-machine-review";

  for (const prefix of ["ontolex", "lexicog", "decomp", "frac", "prov", "dct", "rdf", "rdfs", "skos", "csl"]) {
    caseCheck(Boolean(context[prefix]), `missing ${prefix} context`);
  }
  caseCheck(graph.length >= 5, "graph is too small to be beyond a stub");

  const entry = graph.find(node => nodeTypes(node).includes("ontolex:LexicalEntry"));
  caseCheck(Boolean(entry), "missing ontolex:LexicalEntry");
  if (!entry) {
    return {id: model.id, key: model.key, status: "fail", errors: caseErrors, warnings: caseWarnings};
  }

  caseCheck(nodeTypes(entry).includes("lexicog:Entry"), "missing lexicog:Entry type");
  caseCheck(Boolean(entry["ontolex:canonicalForm"]?.["@id"]), "missing canonical form link");
  caseCheck(entry["csl:profileVersion"] === PROFILE_VERSION, "profile version mismatch");
  caseCheck(entry["csl:validationScope"] === VALIDATION_SCOPE, "validation scope mismatch");
  caseCheck(entry["csl:reviewStatus"] === expectedStatus, `review status expected ${expectedStatus}, found ${entry["csl:reviewStatus"] || "none"}`);
  caseCheck(entry["csl:caseId"] === model.id, "case id mismatch");
  caseCheck(entry["csl:key"] === model.key, "key mismatch");

  const form = graph.find(node => node["@id"] === entry["ontolex:canonicalForm"]["@id"]);
  caseCheck(Boolean(form), "canonical form node missing");
  caseCheck(nodeTypes(form).includes("ontolex:Form"), "canonical node is not an ontolex:Form");
  caseCheck(Boolean(form?.["ontolex:writtenRep"]?.["@value"]), "canonical writtenRep missing");

  const sourceRecords = graph.filter(node => node["@type"] === "csl:SourceRecord");
  caseCheck(sourceRecords.length === 3, `expected 3 source records, found ${sourceRecords.length}`);
  for (const dict of ["mw", "pwg", "pwk"]) {
    const record = sourceRecords.find(node => node["csl:dictionary"] === dict);
    caseCheck(Boolean(record), `missing source record for ${dict}`);
    caseCheck(Boolean(record?.["rdf:value"]), `source record for ${dict} lacks raw value`);
    caseCheck(String(record?.["csl:recordNumber"] || "") === String(model.records?.[dict]?.L || ""), `source record number mismatch for ${dict}`);
  }

  const attestations = graph.filter(node => node["@type"] === "frac:Attestation");
  caseCheck(attestations.length > 0, "expected at least one FrAC attestation");
  for (const attestation of attestations) {
    caseCheck(Boolean(attestation["frac:attests"]?.["@id"]), `attestation ${attestation["@id"]} lacks attests link`);
    caseCheck(attestation["frac:attests"]?.["@id"] === entry["@id"], `attestation ${attestation["@id"]} points to a different entry`);
    caseCheck(Boolean(attestation["prov:wasDerivedFrom"]?.["@id"]), `attestation ${attestation["@id"]} lacks provenance link`);
    caseCheck(Boolean(attestation["csl:evidenceType"]), `attestation ${attestation["@id"]} lacks evidence type`);
  }

  if (model.phenomena.includes("hedge")) {
    caseCheck(
      attestations.some(node => node["csl:evidenceType"] === "generic-lexicographer-hedge"),
      "missing generic lexicographer hedge attestation"
    );
  }
  if (model.phenomena.includes("root")) {
    caseCheck(graph.some(node => node["@type"] === "csl:RootRelation"), "missing root relation");
  }
  if (model.phenomena.includes("compound")) {
    caseCheck(graph.some(node => node["@type"] === "decomp:ComponentList"), "missing decomp component list");
  }
  if (model.phenomena.includes("continuation")) {
    caseCheck(graph.some(node => node["@type"] === "csl:ContinuationRelation"), "missing continuation relation");
  }

  for (const prefix of ["@prefix ontolex:", "@prefix lexicog:", "@prefix frac:", "@prefix prov:", "@prefix rdf:", "@prefix csl:"]) {
    caseCheck(ttl.includes(prefix), `${ttlRelative}: missing ${prefix}`);
  }
  caseCheck(ttl.includes(`<${entry["@id"]}> a ontolex:LexicalEntry, lexicog:Entry`), `${ttlRelative}: missing entry type triple`);
  caseCheck(ttl.includes(`csl:profileVersion "${PROFILE_VERSION}"`), `${ttlRelative}: missing profile version triple`);
  caseCheck(ttl.includes(`csl:validationScope "${VALIDATION_SCOPE}"`), `${ttlRelative}: missing validation scope triple`);
  caseCheck(ttl.includes("frac:Attestation"), `${ttlRelative}: missing FrAC attestation triples`);
  caseCheck((ttl.match(/a csl:SourceRecord/g) || []).length === 3, `${ttlRelative}: expected 3 csl:SourceRecord triples`);
  caseWarn(ttl.includes("ontolex:sense") || !entry["ontolex:sense"]?.length, `${ttlRelative}: JSON-LD senses are not mirrored in Turtle`);

  return {
    id: model.id,
    key: model.key,
    status: caseErrors.length ? "fail" : "pass",
    reviewStatus: entry["csl:reviewStatus"],
    profileVersion: entry["csl:profileVersion"],
    validationScope: entry["csl:validationScope"],
    graphNodes: graph.length,
    sourceRecords: sourceRecords.length,
    attestations: attestations.length,
    phenomena: model.phenomena || [],
    errors: caseErrors,
    warnings: caseWarnings
  };
}

validateShaclShapes();

const models = readJson("data/pilot/neutral-model.json");
const review = readJson("data/pilot/review-cases.json");
const reviewIds = new Set(review.items.map(item => item.id));

check(models.length === 50, `expected 50 neutral models, found ${models.length}`);
check(review.items.length === 15, `expected 15 initial review cases, found ${review.items.length}`);

const items = models.map(model => validateCase(model, reviewIds));
for (const item of items) {
  errors.push(...item.errors);
  warnings.push(...item.warnings);
}

const report = {
  generatedAt: new Date().toISOString(),
  generator: "scripts/validate-ontolex-profile.mjs",
  profileVersion: PROFILE_VERSION,
  validationScope: VALIDATION_SCOPE,
  shaclProfile: "data/schema/ontolex-frac-profile.shacl.ttl",
  reviewType: "machine-review",
  caveat: "This is full 50-case machine review and project SHACL/profile validation, not a human philological review.",
  totals: {
    cases: items.length,
    passed: items.filter(item => item.status === "pass").length,
    failed: items.filter(item => item.status === "fail").length,
    warnings: warnings.length
  },
  items
};

writeJson("data/pilot/ontolex-review.json", report);
writeJson("src/data/pilot/ontolex-review.json", report);

if (errors.length) {
  console.error(`OntoLex/FrAC SHACL/profile validation failed with ${errors.length} problem(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`OntoLex/FrAC SHACL/profile validation passed: ${items.length} JSON-LD graphs and Turtle RDF files; ${warnings.length} warning(s).`);
