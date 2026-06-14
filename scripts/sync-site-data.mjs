// Copy generated top-level data artifacts into Observable's src root.
//
// Observable Framework only packages FileAttachment paths under `src/`. Some
// atlas generators intentionally keep canonical research artifacts under
// top-level `data/`; this script creates the site-facing copies before build.

import fs from "node:fs";
import path from "node:path";

const COPIES = [
  {
    source: "data/dcs/dcs_lemma_summary.json",
    target: "src/data/dcs/dcs_lemma_summary.json",
    optionalFallback: JSON.stringify({ lemmas: {} }, null, 2) + "\n"
  },
  {
    source: "data/lexico/sense_divergence.json",
    target: "src/data/lexico/sense_divergence.json"
  }
];

function readIfExists(file) {
  try {
    return fs.readFileSync(file);
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

function writeIfChanged(target, content) {
  const current = readIfExists(target);
  if (current && Buffer.compare(current, content) === 0) return false;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content);
  return true;
}

let changed = 0;

for (const entry of COPIES) {
  const source = path.resolve(entry.source);
  const target = path.resolve(entry.target);
  const sourceContent = readIfExists(source);

  if (!sourceContent) {
    if (entry.optionalFallback !== undefined) {
      if (writeIfChanged(target, Buffer.from(entry.optionalFallback))) changed++;
      console.warn(`Optional site data missing: ${entry.source}; wrote empty fallback.`);
      continue;
    }
    throw new Error(`Required site data missing: ${entry.source}`);
  }

  if (writeIfChanged(target, sourceContent)) changed++;
}

console.log(`Synced site data (${changed} file${changed === 1 ? "" : "s"} changed).`);
