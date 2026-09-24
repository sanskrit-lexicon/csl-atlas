// Validate kośa macrostructure instances (H5328) against
// data/schema/kosa-macrostructure.schema.json, plus the semantic rules a JSON
// Schema cannot express (unique ids, verse order, set kind vs section type,
// homonym-sense shape, gender-tag consistency, device table completeness).
//
// No external validator dependency (same stance as validate-review-reports.mjs):
// a small interpreter for the JSON-Schema subset the schema uses — type, const,
// enum, required, properties, additionalProperties:false, items, minItems,
// uniqueItems, minimum, minLength, pattern, anyOf, $ref to #/$defs.
//
// Usage: npm run validate-kosa-model  [files...]   (default: data/lexico/kosa_model_*_sample.json)

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SCHEMA_FILE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "data", "schema",
  "kosa-macrostructure.schema.json");

function typeOf(v) {
  if (v === null) return "null";
  if (Array.isArray(v)) return "array";
  if (Number.isInteger(v)) return "integer";
  return typeof v;
}

function typeMatches(v, t) {
  const actual = typeOf(v);
  return actual === t || (t === "number" && actual === "integer");
}

function resolveRef(root, ref) {
  if (!ref.startsWith("#/")) throw new Error(`unsupported $ref ${ref}`);
  return ref.slice(2).split("/").reduce((node, key) => node[key], root);
}

export function checkSchema(value, schema, root, at = "$", errors = []) {
  if (schema.$ref) return checkSchema(value, resolveRef(root, schema.$ref), root, at, errors);
  if (schema.anyOf) {
    const branches = schema.anyOf.map(sub => checkSchema(value, sub, root, at, []));
    if (branches.some(b => b.length === 0)) return errors;
    // Report the closest branch: one whose type matched (its errors are about content).
    const typed = branches.filter(b => !b.every(e => /: expected [a-z|]+, got /.test(e)));
    errors.push(...(typed.length ? typed.sort((a, b) => a.length - b.length)[0] : [`${at}: matches none of anyOf`]));
    return errors;
  }
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some(t => typeMatches(value, t))) {
      errors.push(`${at}: expected ${types.join("|")}, got ${typeOf(value)}`);
      return errors;
    }
  }
  if ("const" in schema && value !== schema.const) errors.push(`${at}: expected const ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(value)) errors.push(`${at}: ${JSON.stringify(value)} not in enum`);
  if (typeof value === "string") {
    if (schema.minLength !== undefined && value.length < schema.minLength) errors.push(`${at}: shorter than ${schema.minLength}`);
    if (schema.pattern && !new RegExp(schema.pattern, "u").test(value)) errors.push(`${at}: does not match ${schema.pattern}`);
  }
  if (typeof value === "number" && schema.minimum !== undefined && value < schema.minimum)
    errors.push(`${at}: below minimum ${schema.minimum}`);
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) errors.push(`${at}: fewer than ${schema.minItems} items`);
    if (schema.uniqueItems && new Set(value.map(v => JSON.stringify(v))).size !== value.length)
      errors.push(`${at}: items not unique`);
    if (schema.items) value.forEach((v, i) => checkSchema(v, schema.items, root, `${at}[${i}]`, errors));
  }
  if (typeOf(value) === "object") {
    for (const req of schema.required || []) {
      if (!(req in value)) errors.push(`${at}: missing required "${req}"`);
    }
    const props = schema.properties || {};
    for (const [key, v] of Object.entries(value)) {
      if (props[key]) checkSchema(v, props[key], root, `${at}.${key}`, errors);
      else if (schema.additionalProperties === false) errors.push(`${at}: unexpected property "${key}"`);
    }
  }
  return errors;
}

const KIND_FOR_SECTION = {
  synonymic: new Set(["synonym-set"]),
  homonymic: new Set(["homonym-sense"]),
  indeclinable: new Set(["indeclinable-set"])
};
const REQUIRED_DEVICES = ["kanda", "varga", "verse", "synonym-set", "gender-marking", "alphabetical-order"];
const GENDER_OF = { puM: "m", strI: "f", klI: "n" };
const TAG_TOKEN = /puM|strI|klI|tri|dvi|ba|vA|a/gy;

// The whole gender object follows from the tag (same parse as the builder's parse_tag):
// a validator that checked only some fields would pass an object contradicting its own tag.
export function expectedGender(tag) {
  TAG_TOKEN.lastIndex = 0;
  const toks = [];
  let m;
  while ((m = TAG_TOKEN.exec(tag))) toks.push(m[0]);
  const parsed = toks.join("") === tag;
  const triLinga = toks.includes("tri");
  const genders = triLinga ? ["m", "f", "n"]
    : Object.entries(GENDER_OF).filter(([t]) => toks.includes(t)).map(([, g]) => g);
  return {
    tag, genders,
    indeclinable: toks.includes("a") && genders.length === 0,
    triLinga,
    optional: toks.includes("vA"),
    number: toks.includes("dvi") ? "du" : toks.includes("ba") ? "pl" : null,
    parsed
  };
}

export function checkSemantics(doc) {
  const errors = [];
  const devices = new Map();
  for (const d of doc.orderingDevices || []) {
    if (devices.has(d.device)) errors.push(`orderingDevices: duplicate device "${d.device}"`);
    devices.set(d.device, d);
    if (d.evidence === "inferred" && d.layer !== "measurement")
      errors.push(`orderingDevices.${d.device}: inferred evidence must come from the measurement layer`);
    if (d.evidence === "observed" && d.layer === "measurement")
      errors.push(`orderingDevices.${d.device}: an observed device cannot rest on measurement alone`);
  }
  for (const req of REQUIRED_DEVICES) if (!devices.has(req)) errors.push(`orderingDevices: missing "${req}"`);
  const genderDevice = devices.get("gender-marking");
  if (genderDevice && (genderDevice.evidence === "observed") !== doc.genderMarking)
    errors.push(`gender-marking device (${genderDevice.evidence}) disagrees with genderMarking=${doc.genderMarking}`);

  const seenL = new Set();
  const seenEid = new Set();
  let lastEid = 0;
  let expandedGroups = 0;
  const seenLocator = new Set();
  (doc.kandas || []).forEach((k, ki) => {
    if (k.labelStatus === "stated-in-text" && !k.label) errors.push(`kandas[${ki}]: labelStatus stated-in-text needs a label`);
    (k.vargas || []).forEach((v, vi) => {
      const at = `kandas[${ki}].vargas[${vi}]`;
      if (v.groups.length > v.counts.groups) errors.push(`${at}: ${v.groups.length} groups exceed counts.groups ${v.counts.groups}`);
      if (v.groups.length < v.counts.groups && !doc.sample?.isSample)
        errors.push(`${at}: groups truncated but sample.isSample is false`);
      const nSets = v.groups.reduce((n, g) => n + g.sets.length, 0);
      const nMembers = v.groups.reduce((n, g) => n + g.sets.reduce((a, s) => a + s.members.length, 0), 0);
      const complete = v.groups.length === v.counts.groups;
      for (const [what, have, counted] of [["sets", nSets, v.counts.sets], ["members", nMembers, v.counts.members]]) {
        if (have > counted) errors.push(`${at}: ${have} expanded ${what} exceed counts.${what} ${counted}`);
        else if (complete && have !== counted) errors.push(`${at}: fully expanded but ${have} ${what} != counts.${what} ${counted}`);
      }
      if (v.labelStatus === "stated-in-text" && !v.label) errors.push(`${at}: labelStatus stated-in-text needs a label`);
      let lastVerse = 0;
      v.groups.forEach((g, gi) => {
        expandedGroups += 1;
        const gat = `${at}.groups[${gi}]`;
        if (seenL.has(g.L)) errors.push(`${gat}: duplicate L "${g.L}"`);
        seenL.add(g.L);
        if (doc.digitizationModel === "exploded") {
          if (!g.locator) errors.push(`${gat}: exploded model needs a locator`);
          else if (seenLocator.has(g.locator)) errors.push(`${gat}: duplicate locator "${g.locator}"`);
          seenLocator.add(g.locator);
          if (g.sets.length !== 1) errors.push(`${gat}: an exploded verse-group is exactly one unsegmented-verse set`);
        }
        for (const r of g.verseRefs.filter(r => !r.half)) {
          if (r.n < lastVerse) errors.push(`${gat}: verse ${r.n} after ${lastVerse} (verse order broken)`);
          lastVerse = r.n;
        }
        g.sets.forEach((s, si) => {
          const sat = `${gat}.sets[${si}]`;
          if (doc.digitizationModel === "exploded") {
            if (s.kind !== "unsegmented-verse") errors.push(`${sat}: exploded model admits only unsegmented-verse`);
            if (s.eid !== null) errors.push(`${sat}: exploded model has no eid segmentation (eid must be null)`);
          } else {
            if (!KIND_FOR_SECTION[v.sectionType].has(s.kind))
              errors.push(`${sat}: kind ${s.kind} not allowed in a ${v.sectionType} section`);
            if (s.eid === null) errors.push(`${sat}: grouped model needs an eid`);
            else {
              if (seenEid.has(s.eid)) errors.push(`${sat}: duplicate eid ${s.eid}`);
              if (s.eid <= lastEid) errors.push(`${sat}: eid ${s.eid} not increasing`);
              seenEid.add(s.eid);
              lastEid = s.eid;
            }
          }
          if (s.kind === "homonym-sense") {
            const heads = s.members.filter(m => m.role === "headword");
            const glosses = s.members.filter(m => m.role === "gloss");
            if (heads.length !== 1 || s.members[0].role !== "headword")
              errors.push(`${sat}: a homonym-sense needs exactly one leading headword`);
            if (glosses.length < 1) errors.push(`${sat}: a homonym-sense needs a gloss`);
          } else if (s.members.some(m => m.role === "headword")) {
            errors.push(`${sat}: role headword only occurs in a homonym-sense`);
          }
          s.members.forEach((m, mi) => {
            const mat = `${sat}.members[${mi}]`;
            if (m.gender === null) {
              if (doc.genderMarking && m.role !== "gloss") errors.push(`${mat}: untagged non-gloss member in a gender-marked kośa`);
              return;
            }
            if (!doc.genderMarking) errors.push(`${mat}: gender tag in a kośa declared genderMarking=false`);
            const want = expectedGender(m.gender.tag);
            for (const [field, value] of Object.entries(want)) {
              if (JSON.stringify(value) !== JSON.stringify(m.gender[field]))
                errors.push(`${mat}: ${field} ${JSON.stringify(m.gender[field])} disagree with tag ${m.gender.tag}`);
            }
          });
        });
      });
    });
  });
  if (expandedGroups === 0) errors.push("no expanded verse-group: nothing was validated below the division level");
  return errors;
}

export function validateKosaModel(doc, schema = JSON.parse(fs.readFileSync(SCHEMA_FILE, "utf8"))) {
  const structural = checkSchema(doc, schema, schema);
  // Semantic rules assume the structure holds; run them only on a structurally valid doc.
  return structural.length ? structural : checkSemantics(doc);
}

function main(argv) {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const files = argv.length
    ? argv
    : fs.readdirSync(path.join(root, "data", "lexico"))
      .filter(f => /^kosa_model_.*_sample\.json$/.test(f))
      .map(f => path.join(root, "data", "lexico", f));
  if (!files.length) {
    console.error("validate-kosa-model: no instances found");
    process.exit(1);
  }
  let failed = 0;
  for (const file of files) {
    const doc = JSON.parse(fs.readFileSync(file, "utf8"));
    const errors = validateKosaModel(doc);
    const rel = path.relative(process.cwd(), file);
    const groups = doc.kandas.flatMap(k => k.vargas).reduce((n, v) => n + v.groups.length, 0);
    if (errors.length) {
      failed += 1;
      console.error(`FAIL ${rel}: ${errors.length} error(s)`);
      errors.slice(0, 20).forEach(e => console.error(`  - ${e}`));
    } else {
      console.log(`PASS ${rel} (${doc.kosha.code}, ${doc.digitizationModel}, ${groups} verse-groups expanded)`);
    }
  }
  process.exit(failed ? 1 : 0);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main(process.argv.slice(2));
