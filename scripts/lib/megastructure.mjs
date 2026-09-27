// Megastructure catalogue checks (H5324).
//
// The repo carries no JSON Schema library, so `checkSchema` implements the
// draft-2020-12 subset that data/schema/megastructure-component.schema.json
// uses: type (incl. type arrays), enum, const, required, properties,
// additionalProperties:false, pattern, minItems, items, minimum,
// exclusiveMinimum, minLength and local $ref. A keyword outside that subset is
// an error, so a later schema edit cannot be silently ignored.

const SUPPORTED = new Set([
  "$schema", "$id", "$ref", "$defs", "title", "description", "type", "enum", "const", "required",
  "properties", "additionalProperties", "pattern", "minItems", "items", "minimum",
  "exclusiveMinimum", "minLength"
]);

function typeOf(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (typeof value === "number") return Number.isInteger(value) ? "integer" : "number";
  return typeof value;
}

function typeMatches(value, wanted) {
  const actual = typeOf(value);
  return actual === wanted || (wanted === "number" && actual === "integer");
}

function resolveRef(root, ref) {
  if (!ref.startsWith("#/")) throw new Error(`unsupported $ref ${ref}`);
  return ref.slice(2).split("/").reduce((node, key) => node?.[key], root);
}

/** Validate `value` against `schema`; returns a list of "path: message" strings. */
export function checkSchema(schema, value, root = schema, at = "$") {
  const errors = [];
  for (const key of Object.keys(schema)) {
    if (!SUPPORTED.has(key)) errors.push(`${at}: schema keyword "${key}" is not supported by checkSchema`);
  }
  if (schema.$ref) {
    const target = resolveRef(root, schema.$ref);
    if (!target) return [`${at}: unresolvable $ref ${schema.$ref}`];
    return errors.concat(checkSchema(target, value, root, at));
  }
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some((type) => typeMatches(value, type))) {
      return errors.concat(`${at}: expected ${types.join("|")}, got ${typeOf(value)}`);
    }
  }
  if ("const" in schema && value !== schema.const) errors.push(`${at}: must equal ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(value)) errors.push(`${at}: ${JSON.stringify(value)} not in enum`);
  if (typeof value === "string") {
    if (schema.minLength != null && value.length < schema.minLength) errors.push(`${at}: shorter than ${schema.minLength}`);
    if (schema.pattern && !new RegExp(schema.pattern, "u").test(value)) errors.push(`${at}: "${value}" does not match ${schema.pattern}`);
  }
  if (typeof value === "number") {
    if (schema.minimum != null && value < schema.minimum) errors.push(`${at}: below minimum ${schema.minimum}`);
    if (schema.exclusiveMinimum != null && value <= schema.exclusiveMinimum) errors.push(`${at}: must exceed ${schema.exclusiveMinimum}`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems != null && value.length < schema.minItems) errors.push(`${at}: fewer than ${schema.minItems} items`);
    if (schema.items) value.forEach((item, i) => errors.push(...checkSchema(schema.items, item, root, `${at}[${i}]`)));
  }
  if (typeOf(value) === "object") {
    for (const key of schema.required ?? []) {
      if (!(key in value)) errors.push(`${at}: missing required "${key}"`);
    }
    for (const [key, child] of Object.entries(value)) {
      const sub = schema.properties?.[key];
      if (sub) errors.push(...checkSchema(sub, child, root, `${at}.${key}`));
      else if (schema.additionalProperties === false) errors.push(`${at}: unexpected property "${key}"`);
    }
  }
  return errors;
}

/** Parse data/megastructure/scan_inventory.tsv into row objects. */
export function parseInventory(text) {
  const lines = text.split(/\r?\n/).filter((line) => line.length > 0);
  const header = lines.shift().split("\t");
  return lines.map((line) => {
    const cells = line.split("\t");
    return Object.fromEntries(header.map((name, i) => [name, cells[i] ?? ""]));
  });
}

/** Expand a scanLocus ref ("t05", or a range "1308..1333") to inventory refs, in inventory order. */
export function expandRef(ref, setRows) {
  const refs = setRows.map((row) => row.ref);
  const range = ref.split("..");
  if (range.length === 1) return refs.includes(ref) ? [ref] : null;
  const [first, last] = range;
  const a = refs.indexOf(first);
  const b = refs.indexOf(last);
  if (a < 0 || b < 0 || b < a) return null;
  return refs.slice(a, b + 1);
}

const POSITION_OF = { fm: "front", bm: "back", in: "inset" };

/**
 * Checks the schema cannot express. `inventory` = parsed scan_inventory rows;
 * `fileExists(path)` resolves repo-relative atlasRef paths.
 */
export function semanticChecks(catalogue, inventory, fileExists = () => true) {
  const errors = [];
  const dict = catalogue.dict;
  const components = catalogue.components ?? [];
  const ids = new Set();
  const sequences = new Set();
  for (const component of components) {
    const [prefix, section] = component.id.split(".");
    if (ids.has(component.id)) errors.push(`${component.id}: duplicate id`);
    ids.add(component.id);
    if (prefix !== dict) errors.push(`${component.id}: id prefix "${prefix}" is not the catalogue dict "${dict}"`);
    if (POSITION_OF[section] !== component.position) errors.push(`${component.id}: id section "${section}" disagrees with position "${component.position}"`);
    if (sequences.has(component.sequence)) errors.push(`${component.id}: sequence ${component.sequence} used twice`);
    sequences.add(component.sequence);
    if (component.componentType === "other" && !component.componentTypeNote) errors.push(`${component.id}: componentType "other" needs componentTypeNote`);
    for (const decode of component.decodes ?? []) {
      if (decode.atlasRef && !fileExists(decode.atlasRef)) errors.push(`${component.id}: atlasRef ${decode.atlasRef} does not exist`);
    }
  }
  const byId = new Map(components.map((component) => [component.id, component]));
  for (const component of components) {
    if (component.parent == null) continue;
    if (!byId.has(component.parent)) errors.push(`${component.id}: parent ${component.parent} is not a component`);
    const seen = new Set([component.id]);
    let cursor = byId.get(component.parent);
    while (cursor) {
      if (seen.has(cursor.id)) {
        errors.push(`${component.id}: parent chain loops`);
        break;
      }
      seen.add(cursor.id);
      cursor = cursor.parent ? byId.get(cursor.parent) : null;
    }
  }
  for (const misfit of catalogue.misfits ?? []) {
    if (misfit.componentId && !byId.has(misfit.componentId)) errors.push(`misfit "${misfit.label}": componentId ${misfit.componentId} is not a component`);
  }

  // Scan coverage: every inventory page of every scan set is covered or excluded.
  const coverage = [];
  const setIds = new Set((catalogue.scanSets ?? []).map((set) => set.id));
  const rowsOf = (setId) => inventory.filter((row) => row.dict === dict && row.scanSet === setId);
  for (const setId of setIds) {
    if (rowsOf(setId).length === 0) errors.push(`scanSet ${setId}: no rows for dict ${dict} in the inventory`);
  }
  const covered = new Map([...setIds].map((setId) => [setId, new Set()]));
  const place = (owner, scanSet, ref) => {
    if (!setIds.has(scanSet)) {
      errors.push(`${owner}: scanSet ${scanSet} is not declared in scanSets`);
      return;
    }
    const refs = expandRef(ref, rowsOf(scanSet));
    if (!refs) errors.push(`${owner}: ref ${ref} is not in the ${scanSet} inventory`);
    else refs.forEach((r) => covered.get(scanSet).add(r));
  };
  for (const component of components) {
    for (const locus of component.scanLocus ?? []) place(component.id, locus.scanSet, locus.ref);
  }
  const excluded = new Set();
  for (const item of catalogue.excludedScans ?? []) {
    const key = `${item.scanSet}:${item.ref}`;
    if (covered.get(item.scanSet)?.has(item.ref)) errors.push(`excludedScans ${key}: also covered by a component`);
    place(`excludedScans ${key}`, item.scanSet, item.ref);
    excluded.add(key);
  }
  for (const setId of setIds) {
    const rows = rowsOf(setId);
    const missing = rows.filter((row) => !covered.get(setId).has(row.ref));
    if (missing.length) errors.push(`scanSet ${setId}: pages with no component and no exclusion: ${missing.map((row) => row.ref).join(", ")}`);
    coverage.push({ scanSet: setId, pages: rows.length, covered: rows.length - missing.length, excluded: rows.filter((row) => excluded.has(`${setId}:${row.ref}`)).length });
  }
  return { errors, coverage };
}

/** Per-dictionary counts for the built catalogue and the atlas page. */
export function summarize(catalogue) {
  const tally = (key) => {
    const out = {};
    for (const component of catalogue.components) out[component[key]] = (out[component[key]] ?? 0) + 1;
    return Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b)));
  };
  return {
    dict: catalogue.dict,
    components: catalogue.components.length,
    topLevel: catalogue.components.filter((component) => component.parent == null).length,
    front: catalogue.components.filter((component) => component.position === "front").length,
    back: catalogue.components.filter((component) => component.position === "back").length,
    inset: catalogue.components.filter((component) => component.position === "inset").length,
    decoding: catalogue.components.filter((component) => component.decodes.length > 0).length,
    byType: tally("componentType"),
    byFunction: tally("function"),
    byDisposition: tally("digitalDisposition"),
    byEvidence: tally("evidenceLevel"),
    knownGaps: catalogue.knownGaps.length,
    misfits: catalogue.misfits.length
  };
}
