#!/usr/bin/env node
// Validate the megastructure catalogue (H5324).
//
// 1. Every data/megastructure/<dict>.json passes the committed schema and the
//    semantic checks (unique ids and sequences, parents resolve, every page of
//    every scan-set inventory is covered by a component or explicitly excluded).
// 2. The committed src/data/megastructure/megastructure_catalogue.json matches
//    a fresh build of those inputs (ignoring generatedAt).
// 3. When sibling checkouts (../csl-orig, ../csl-pywork) are present, the counts
//    quoted in MW evidence strings are re-measured; absent siblings are noted, not failed.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSON_OUT, buildPayload, loadAndCheck } from "./build-megastructure.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SIBLINGS = path.resolve(ROOT, "..");

const fmt = (n) => n.toLocaleString("en-US");

function measureMwSupplement(text) {
  let current = null;
  let flagged = false;
  let supDecimal = 0;
  let supInteger = 0;
  for (const line of text.split("\n")) {
    const header = line.match(/^<L>([0-9.]+)<pc>/);
    if (header) {
      current = header[1];
      flagged = false;
    }
    if (current && !flagged && line.includes('n="sup"')) {
      flagged = true;
      if (current.includes(".")) supDecimal += 1;
      else supInteger += 1;
    }
    if (line.startsWith("<LEND>")) current = null;
  }
  const rev = [...text.matchAll(/<info n="rev" pc="(\d+)/g)].map((m) => Number(m[1]));
  return {
    supRecords: supDecimal + supInteger,
    supDecimal,
    supInteger,
    revMarkers: (text.match(/<info n="rev"/g) ?? []).length,
    revCdsl: (text.match(/<info n="rev" pc="cdsl"/g) ?? []).length,
    revNoPage: (text.match(/<info n="rev"\/>/g) ?? []).length,
    revListinfo: (text.match(/<listinfo n="rev"/g) ?? []).length,
    revInSupplement: rev.filter((page) => page >= 1308 && page <= 1333).length
  };
}

// Each claim: sibling file, how to measure, which component's evidence must quote each number.
export const SIBLING_CLAIMS = [
  {
    file: "csl-orig/v02/mw/mw.txt",
    componentId: "mw.bm.additions",
    measure: measureMwSupplement,
    quoted: ["supRecords", "supDecimal", "supInteger", "revMarkers", "revInSupplement", "revCdsl", "revNoPage", "revListinfo"]
  },
  {
    file: "csl-pywork/v02/distinctfiles/mw/pywork/mwauth/tooltip.txt",
    componentId: "mw.fm.works-authors",
    measure: (text) => {
      const rows = text.split("\n").filter((line) => line.trim().length > 0);
      const added = rows.filter((line) => line.includes("[Cologne Addition]")).length;
      return { rows: rows.length, added, printed: rows.length - added };
    },
    quoted: ["rows", "added", "printed"]
  },
  {
    file: "csl-pywork/v02/distinctfiles/mw/pywork/mwab/mwab_input.txt",
    componentId: "mw.fm.abbreviations",
    measure: (text) => ({ rows: text.split("\n").filter((line) => line.trim().length > 0).length }),
    quoted: ["rows"]
  }
];

function withoutGeneratedAt(payload) {
  const { generatedAt, ...rest } = payload;
  return rest;
}

function main() {
  const errors = [];
  const notes = [];
  const { catalogues, errors: checkErrors, coverage } = loadAndCheck();
  errors.push(...checkErrors);

  if (!fs.existsSync(JSON_OUT)) {
    errors.push(`${path.relative(ROOT, JSON_OUT)} is missing - run npm run build-megastructure`);
  } else {
    const committed = JSON.parse(fs.readFileSync(JSON_OUT, "utf8"));
    const fresh = buildPayload(catalogues, coverage, { generatedAt: committed.generatedAt });
    if (JSON.stringify(withoutGeneratedAt(committed)) !== JSON.stringify(withoutGeneratedAt(fresh))) {
      errors.push(`${path.relative(ROOT, JSON_OUT)} is stale against data/megastructure - run npm run build-megastructure`);
    }
  }

  const byId = new Map(catalogues.flatMap((catalogue) => catalogue.components.map((component) => [component.id, component])));
  for (const claim of SIBLING_CLAIMS) {
    const component = byId.get(claim.componentId);
    if (!component) continue;
    const file = path.join(SIBLINGS, claim.file);
    if (!fs.existsSync(file)) {
      notes.push(`sibling ${claim.file} absent - ${claim.componentId} counts not re-measured`);
      continue;
    }
    const measured = claim.measure(fs.readFileSync(file, "utf8"));
    const text = `${component.evidence} ${component.extent.items ?? ""}`;
    for (const key of claim.quoted) {
      const value = measured[key];
      if (!text.includes(fmt(value)) && !text.includes(String(value))) {
        errors.push(`${claim.componentId}: evidence does not quote the measured ${key} = ${fmt(value)} (${claim.file})`);
      }
    }
    notes.push(`${claim.componentId}: ${Object.entries(measured).map(([k, v]) => `${k}=${fmt(v)}`).join(", ")}`);
  }

  for (const row of coverage) notes.push(`${row.dict} ${row.scanSet}: ${row.covered}/${row.pages} pages covered (${row.excluded} excluded)`);
  for (const note of notes) console.log(`note: ${note}`);
  if (errors.length) {
    console.error(`validate-megastructure: ${errors.length} error(s)\n${errors.map((e) => `- ${e}`).join("\n")}`);
    process.exit(1);
  }
  const components = catalogues.reduce((sum, catalogue) => sum + catalogue.components.length, 0);
  console.log(`validate-megastructure: OK - ${catalogues.length} dictionaries, ${components} components`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
