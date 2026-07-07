// Validate the citation-canon topology packet (PH1 / CANON-CORE).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - matrix dimensions or edge count diverge from the committed TSVs;
// - per-dict distinct-text counts disagree with the edge list;
// - the canon curve does not sum to the text count;
// - required stats fields (NODF, Q, permutation p, nNull) are absent or the
//   verdict is inconsistent with the reported stats;
// - a heatmap cell references a dict/text outside the nested orderings.
//
// Usage: npm run validate-citation-canon   (run after build-citation-canon)

import fs from "node:fs";
import path from "node:path";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "citations");
const JSON_OUT = path.join(OUT_DIR, "citation_canon.json");
const SOURCE_OUT = path.join(OUT_DIR, "citation_canon.source.json");
const EDGES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_edges.tsv");

const errors = [];
const notes = [];

function parseTsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON: ${path.relative(process.cwd(), file)} (${e.message})`);
    return null;
  }
}

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);
const edgeRows = fs.existsSync(EDGES_PATH) ? parseTsv(fs.readFileSync(EDGES_PATH, "utf8")) : null;

if (packet && edgeRows) {
  // Recompute matrix facts from the source of truth.
  const dictTexts = new Map();
  const textDicts = new Map();
  let edgeKeys = new Set();
  for (const e of edgeRows) {
    if (!e.dict || !e.canonical_text) continue;
    edgeKeys.add(`${e.dict}\t${e.canonical_text}`);
  }
  for (const key of edgeKeys) {
    const [dict, text] = key.split("\t");
    if (!dictTexts.has(dict)) dictTexts.set(dict, new Set());
    dictTexts.get(dict).add(text);
    if (!textDicts.has(text)) textDicts.set(text, 0);
    textDicts.set(text, textDicts.get(text) + 1);
  }
  const nDicts = dictTexts.size;
  const nTexts = textDicts.size;
  const nEdges = edgeKeys.size;

  if (packet.matrix?.nDicts !== nDicts) errors.push(`matrix.nDicts ${packet.matrix?.nDicts} != ${nDicts} from edges`);
  if (packet.matrix?.nTexts !== nTexts) errors.push(`matrix.nTexts ${packet.matrix?.nTexts} != ${nTexts} from edges`);
  if (packet.matrix?.nEdges !== nEdges) errors.push(`matrix.nEdges ${packet.matrix?.nEdges} != ${nEdges} from edges`);

  // Nested dict order lists all dicts exactly once.
  const order = packet.nestedDictOrder || [];
  if (order.length !== nDicts) errors.push(`nestedDictOrder length ${order.length} != ${nDicts}`);
  if (new Set(order).size !== order.length) errors.push("nestedDictOrder has duplicates");
  for (const d of order) if (!dictTexts.has(d)) errors.push(`nestedDictOrder references unknown dict ${d}`);

  // Per-dict distinct-text counts match the edge list.
  for (const pd of packet.perDict || []) {
    const truth = dictTexts.get(pd.dict);
    if (!truth) errors.push(`perDict references unknown dict ${pd.dict}`);
    else if (pd.distinctTexts !== truth.size) errors.push(`perDict[${pd.dict}].distinctTexts ${pd.distinctTexts} != ${truth.size}`);
  }

  // Nested order is non-increasing in distinct texts.
  const degByDict = new Map((packet.perDict || []).map((p) => [p.dict, p.distinctTexts]));
  for (let i = 1; i < order.length; i += 1) {
    if ((degByDict.get(order[i - 1]) ?? Infinity) < (degByDict.get(order[i]) ?? 0)) {
      errors.push(`nestedDictOrder not degree-sorted at ${order[i - 1]} -> ${order[i]}`);
    }
  }

  // Canon curve sums to the text count.
  const curveSum = (packet.canonCurve || []).reduce((a, c) => a + c.texts, 0);
  if (curveSum !== nTexts) errors.push(`canonCurve sums to ${curveSum} != ${nTexts} texts`);
  // Canon curve k range is 1..nDicts, no text cited by >nDicts.
  for (const c of packet.canonCurve || []) {
    if (c.nDicts < 1 || c.nDicts > nDicts) errors.push(`canonCurve has out-of-range nDicts=${c.nDicts}`);
  }

  // Heatmap cells reference only known dicts and top-texts.
  const topTextSet = new Set((packet.topTexts || []).map((t) => t.text));
  for (const cell of packet.heatmapCells || []) {
    if (!dictTexts.has(cell.dict)) errors.push(`heatmap cell references unknown dict ${cell.dict}`);
    if (!topTextSet.has(cell.text)) errors.push(`heatmap cell references text not in topTexts: ${cell.text}`);
    if (!(cell.count >= 0)) errors.push(`heatmap cell for ${cell.dict}/${cell.text} has bad count ${cell.count}`);
  }
  if ((packet.heatmapCells || []).length !== nDicts * topTextSet.size) {
    notes.push(`heatmap has ${packet.heatmapCells?.length} cells for ${nDicts} dicts × ${topTextSet.size} texts.`);
  }

  // topText nDicts matches recomputed dict count.
  for (const t of packet.topTexts || []) {
    const truth = textDicts.get(t.text);
    if (truth === undefined) errors.push(`topText references unknown text ${t.text}`);
    else if (t.nDicts !== truth) errors.push(`topText[${t.text}].nDicts ${t.nDicts} != ${truth}`);
  }

  // Stats block completeness.
  const s = packet.stats || {};
  for (const stat of ["nodf", "modularity"]) {
    const b = s[stat];
    if (!b) { errors.push(`stats.${stat} missing`); continue; }
    for (const f of ["observed", "nullMean", "p", "nNull"]) {
      if (b[f] === undefined || b[f] === null) errors.push(`stats.${stat}.${f} missing`);
    }
    if (b.nNull < 1000) errors.push(`stats.${stat}.nNull ${b.nNull} < 1000 (PH1 requires >=1,000 nulls)`);
    if (!(b.p > 0 && b.p <= 1)) errors.push(`stats.${stat}.p out of (0,1]: ${b.p}`);
  }

  // Verdict consistency with stats.
  const nested = s.nodf && s.nodf.p <= 0.05 && s.nodf.observed > s.nodf.nullMean;
  const modular = s.modularity && s.modularity.p <= 0.05 && s.modularity.observed > s.modularity.nullMean;
  const expected = nested && !modular ? "nested"
    : modular && !nested ? "modular"
    : nested && modular ? "nested-and-modular"
    : "neither-detected";
  if (packet.verdict !== expected) errors.push(`verdict "${packet.verdict}" inconsistent with stats (expected "${expected}")`);

  // Provenance envelope.
  if (packet.evidenceLabel !== "derived") errors.push(`evidenceLabel is "${packet.evidenceLabel}", expected "derived"`);
  if (packet.ownerRepo !== "csl-atlas") errors.push(`ownerRepo is "${packet.ownerRepo}", expected "csl-atlas"`);
  if (!envelope) errors.push("citation_canon.source.json envelope missing");
  else if (!envelope.commit) errors.push("source envelope has no commit");

  notes.push(`matrix ${nDicts} dicts × ${nTexts} texts, ${nEdges} edges.`);
  notes.push(`verdict: ${packet.verdict}; NODF ${s.nodf?.observed} (p ${s.nodf?.p}); Q ${s.modularity?.observed} (p ${s.modularity?.p}).`);
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length) {
  console.error(`\nvalidate-citation-canon FAILED with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log("validate-citation-canon OK.");
