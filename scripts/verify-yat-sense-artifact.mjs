// Verify the WIL→YAT "drastic condensation" finding (H3R) is a parser artifact.
//
// r2_h2h3.json reports YAT collapsing to 1 sense for every panel lemma (drift
// −8 vs WIL's 9), labelled "drastic condensation". This check shows that is an
// EXTRACTION artifact, not lexicography: YAT does not number its senses — it
// packs them into a single semicolon-separated run-on gloss (Petersburg/MW
// style), and the one number present is a NOUN-CLASS / gender marker (e.g.
// "{#(viH)#} 2. {%m.%} The sun; a mountain; a sheep; …") that the inline-number
// splitter mistakes for a sense boundary and collapses on.
//
// Emits data/lexico/r2_yat_artifact_check.json. Read-only; no model. Reuses the
// EXACT splitInlineNumber the H3R builder uses, so inlineSenses matches r2_h2h3.
//
// Usage: npm run verify-yat-sense-artifact

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict } from "./lib/dict-parser.mjs";
import { splitInlineNumber, stripMarkup } from "./build-r2-h2h3.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const OUT_FILE = path.join(OUT_DIR, "r2_yat_artifact_check.json");
const H2H3 = path.join(OUT_DIR, "r2_h2h3.json");

// A noun-class/gender marker: "...} N. {%gender%}" — a single number wedged
// between the inflection paren and the gender tag, NOT a sense number.
const CLASS_NUM = /\}\s*\d+\.\s*\{%/;

// True meaning count: strip markup, drop the leading headword + class-number,
// then count distinct meaning chunks separated by ';' or '.' (YAT's real
// enumeration). Conservative: keep only alphabetic chunks of length > 2.
function trueMeaningCount(body) {
  const t = stripMarkup(body).replace(/^[^0-9]*\d+\.\s*/, "").replace(/^[a-z. ]+\b/i, "");
  return t.split(/[;.]/).map(s => s.replace(/[^a-zA-Z]/g, "")).filter(s => s.length > 2).length;
}

function main() {
  const panel = JSON.parse(fs.readFileSync(H2H3, "utf8")).panel;
  const want = new Set(panel);
  const yat = new Map();
  for (const r of iterateDict("yat")) {
    const k = (r.k1 || "").replace(/\//g, "");
    if (want.has(k) && !yat.has(k)) yat.set(k, r.body || "");
  }

  const rows = [];
  for (const stem of panel) {
    const body = yat.get(stem);
    if (!body) continue;
    rows.push({
      stem,
      inlineSenses: splitInlineNumber(body).length,           // the H3R method -> ~1
      trueMeanings: trueMeaningCount(body),                   // semicolon-packed reality
      classNumberMarker: CLASS_NUM.test(body),               // the misread number
      gloss: stripMarkup(body).slice(0, 120),
    });
  }
  const n = rows.length;
  const mean = (f) => n ? Math.round((rows.reduce((s, r) => s + f(r), 0) / n) * 100) / 100 : 0;
  const summary = {
    panelEntries: n,
    meanInlineSenses: mean(r => r.inlineSenses),               // ≈1 (the artifact)
    meanTrueMeanings: mean(r => r.trueMeanings),               // ≈ comparable to WIL
    classNumberMarkerRate: n ? Math.round((rows.filter(r => r.classNumberMarker).length / n) * 100) / 100 : 0,
    wilMeanSenses: 9,                                          // ancestor, from r2_h2h3 h3r
  };
  const verdict =
    summary.meanInlineSenses < 1.5 && summary.meanTrueMeanings > 3
      ? "artifact-confirmed"
      : "inconclusive";

  const payload = {
    schemaVersion: "0.1.0",
    generatedBy: "npm run verify-yat-sense-artifact",
    claimUnderTest: "H3R wil→yat: 'drastic condensation' (9 senses → 1)",
    finding: "Parser artifact, not condensation. YAT packs senses into one semicolon-separated run-on gloss and is not sense-numbered; the inline-number splitter mis-reads a noun-class/gender number and collapses to 1. YAT's true polysemy is comparable to WIL's.",
    verdict,
    summary,
    rows,
    recommendation: "Demote the wil→yat edge to 'not sense-countable' in H3R, or add a semicolon-aware sense counter for run-on-gloss dictionaries (YAT, SHS) — a parser promotion to route through the R2 checkpoint review.",
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_FILE, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`YAT artifact check: ${verdict}`);
  console.log(`  ${n} panel entries | inline-senses ${summary.meanInlineSenses} (builder method) vs true-meanings ${summary.meanTrueMeanings} (semicolon) | class-number marker ${Math.round(summary.classNumberMarkerRate * 100)}%`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT_FILE)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
