// Recover archived R2 payloads from the static atlas pages.
//
// This is not the original R2 sense splitter. It preserves the archived page
// data as deterministic JSON so the next rebuild step has machine-readable
// fixtures and provenance.
//
// Usage: npm run recover-r2-archive

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const ROOT = process.cwd();
const EXPLORER_PATH = path.join(ROOT, "src", "tools", "r2-explorer.md");
const H1_PATH = path.join(ROOT, "src", "tools", "r2-h1.md");
const OUT_DIR = path.join(ROOT, "data", "lexico");
const EXPLORER_OUT = path.join(OUT_DIR, "r2_archive_explorer.json");
const H1_OUT = path.join(OUT_DIR, "r2_archive_h1.json");

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

function sha256(text) {
  return crypto.createHash("sha256").update(text).digest("hex");
}

function relative(file) {
  return path.relative(ROOT, file).replace(/\\/g, "/");
}

function evaluateObjectLiteral(source, label) {
  try {
    return vm.runInNewContext(`(${source})`, Object.freeze({}));
  } catch (error) {
    throw new Error(`Could not evaluate ${label}: ${error.message}`);
  }
}

function recoverExplorer() {
  const text = readText(EXPLORER_PATH);
  const dataMatch = text.match(/const DATA = ([\s\S]*?); const LABEL = /);
  const labelMatch = text.match(/const LABEL = ([\s\S]*?);\nconst sel =/);
  if (!dataMatch || !labelMatch) {
    throw new Error("Could not find DATA and LABEL blocks in r2-explorer.md");
  }

  const data = evaluateObjectLiteral(dataMatch[1], "R2 DATA");
  const labels = evaluateObjectLiteral(labelMatch[1], "R2 LABEL");
  const lemmas = Object.entries(data).map(([lemma, payload]) => {
    const sensesByDict = payload.senses ?? {};
    const senseCount = Object.values(sensesByDict).reduce((sum, rows) => sum + rows.length, 0);
    const alignments = payload.aligns ?? [];
    return {
      lemma,
      dictionaryCount: Object.keys(sensesByDict).length,
      senseCount,
      alignmentCount: alignments.length,
      crossAlignmentCount: alignments.filter(row => row.cross).length,
      senses: sensesByDict,
      alignments
    };
  });

  const payload = {
    schemaVersion: "1.0.0",
    status: "archived-static-page-recovery",
    claim: "Archived R2 sense-alignment explorer payload recovered from the static atlas page.",
    sourceFiles: [relative(EXPLORER_PATH)],
    sourceHashes: {[relative(EXPLORER_PATH)]: sha256(text)},
    limitations: [
      "This payload is recovered from the static page, not rebuilt from csl-orig.",
      "Use it as a fixture while restoring the real R2 splitter package.",
      "Encoding reflects the archived page text exactly."
    ],
    labels,
    counts: {
      lemmaCount: lemmas.length,
      dictionaryLabelCount: Object.keys(labels).length,
      senseRows: lemmas.reduce((sum, row) => sum + row.senseCount, 0),
      alignmentRows: lemmas.reduce((sum, row) => sum + row.alignmentCount, 0),
      crossAlignmentRows: lemmas.reduce((sum, row) => sum + row.crossAlignmentCount, 0)
    },
    lemmas
  };

  if (payload.counts.lemmaCount !== 5) throw new Error("Expected 5 archived R2 lemmas");
  if (payload.counts.dictionaryLabelCount < 10) throw new Error("Too few dictionary labels");
  if (payload.counts.alignmentRows === 0) throw new Error("No archived alignments found");
  return payload;
}

function recoverH1() {
  const text = readText(H1_PATH);
  const rows = [...text.matchAll(/<title>([^<]+)<\/title>/g)].map(match => {
    const title = match[1];
    const parsed = title.match(/^(.+?) \((\d{4}), (.+?)\): ([0-9.]+) units\/entry, ([0-9,]+) entries$/);
    if (!parsed) throw new Error(`Could not parse H1 point title: ${title}`);
    return {
      dict: parsed[1],
      year: Number(parsed[2]),
      family: parsed[3],
      senseUnitsPerEntry: Number(parsed[4]),
      entries: Number(parsed[5].replace(/,/g, ""))
    };
  });

  const byFamily = new Map();
  for (const row of rows) {
    if (!byFamily.has(row.family)) byFamily.set(row.family, []);
    byFamily.get(row.family).push(row);
  }
  const familyMeans = [...byFamily.entries()].map(([family, familyRows]) => ({
    family,
    dictionaryCount: familyRows.length,
    meanSenseUnitsPerEntry: Number(
      (familyRows.reduce((sum, row) => sum + row.senseUnitsPerEntry, 0) / familyRows.length).toFixed(3)
    )
  })).sort((a, b) => b.meanSenseUnitsPerEntry - a.meanSenseUnitsPerEntry || a.family.localeCompare(b.family));

  const payload = {
    schemaVersion: "1.0.0",
    status: "archived-static-page-recovery",
    claim: "Archived H1R sense-granularity scatter data recovered from the static atlas page.",
    sourceFiles: [relative(H1_PATH)],
    sourceHashes: {[relative(H1_PATH)]: sha256(text)},
    limitations: [
      "This payload is recovered from SVG titles, not rebuilt from csl-orig.",
      "Use it as a fixture while restoring the real R2 H1 generator.",
      "It preserves the plotted per-dictionary points only."
    ],
    counts: {
      dictionaryRows: rows.length,
      familyRows: familyMeans.length
    },
    rows,
    familyMeans
  };

  if (payload.counts.dictionaryRows !== 11) throw new Error("Expected 11 archived H1 dictionary rows");
  return payload;
}

function writeJson(file, payload) {
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${relative(file)}`);
}

writeJson(EXPLORER_OUT, recoverExplorer());
writeJson(H1_OUT, recoverH1());

