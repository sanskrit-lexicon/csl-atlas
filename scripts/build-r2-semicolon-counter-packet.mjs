// Build the R2 "semicolon-aware sense counter" parser-promotion review packet.
//
// Follow-up to the YAT artifact finding (#125): the inline-number sense splitter
// collapses run-on-gloss dictionaries (which pack senses with semicolons, not
// numbers) to 1 sense, producing the spurious wil→yat "condensation". A
// semicolon-aware counter would fix it — but that is a PARSER PROMOTION (it
// changes how senses are counted), so it must be reviewed before adoption, not
// applied silently. This script packages the proposal as a checkpoint review
// packet with empty human-decision fields, matching build-r2-checkpoint-packet.
//
// It also includes SHS as a CONTROL: SHS is genuinely sense-numbered, so the
// detection gate must keep the semicolon rule OFF for it.
//
// Read-only over csl-orig. Usage: npm run build-r2-semicolon-counter-packet

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict } from "./lib/dict-parser.mjs";
import { splitInlineNumber, stripMarkup } from "./build-r2-h2h3.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const OUT_FILE = path.join(OUT_DIR, "r2_semicolon_counter_packet.json");
const H2H3 = path.join(OUT_DIR, "r2_h2h3.json");

const CLASS_NUM = /\}\s*\d+\.\s*\{%/;          // noun-class/gender marker, not a sense number
const CANDIDATE_DICTS = ["yat", "shs"];        // the two inline-number-split dicts in H3R

// Semicolon-aware meaning count (the proposed rule): strip markup, drop the
// leading headword + class number, split on ';' / '.', keep alphabetic chunks > 2.
function semicolonMeanings(body) {
  const t = stripMarkup(body).replace(/^[^0-9]*\d+\.\s*/, "").replace(/^[a-z. ]+\b/i, "");
  return t.split(/[;.]/).map(s => s.replace(/[^a-zA-Z]/g, "")).filter(s => s.length > 2).length;
}

function loadPanelEntries(code, want) {
  const out = new Map();
  for (const r of iterateDict(code)) {
    const k = (r.k1 || "").replace(/\//g, "");
    if (want.has(k) && !out.has(k)) out.set(k, { body: r.body || "", startLine: r.startLine, href: r.href });
  }
  return out;
}

function main() {
  const panel = JSON.parse(fs.readFileSync(H2H3, "utf8")).panel;
  const want = new Set(panel);

  // Per-dict detection + per-lemma method comparison.
  const dictDetection = [];
  const candidateRows = [];
  for (const code of CANDIDATE_DICTS) {
    const entries = loadPanelEntries(code, want);
    let inlineSum = 0, semiSum = 0, classNum = 0, n = 0;
    const perLemma = [];
    for (const stem of panel) {
      const e = entries.get(stem); if (!e) continue;
      n++;
      const inlineSenses = splitInlineNumber(e.body).length;
      const semicolon = semicolonMeanings(e.body);
      const hasClassNum = CLASS_NUM.test(e.body);
      inlineSum += inlineSenses; semiSum += semicolon; if (hasClassNum) classNum++;
      perLemma.push({ stem, inlineSenses, semicolon, hasClassNum, startLine: e.startLine, href: e.href,
                      gloss: stripMarkup(e.body).slice(0, 100) });
    }
    const meanInline = n ? Math.round((inlineSum / n) * 100) / 100 : 0;
    const meanSemicolon = n ? Math.round((semiSum / n) * 100) / 100 : 0;
    // Detection gate: run-on-gloss iff senses aren't numbered but meanings are semicolon-packed.
    const runOnGloss = meanInline < 1.5 && meanSemicolon >= 3;
    dictDetection.push({
      dict: code, panelEntries: n, meanInlineSenses: meanInline, meanSemicolonMeanings: meanSemicolon,
      classNumberMarkerRate: n ? Math.round((classNum / n) * 100) / 100 : 0,
      verdict: runOnGloss ? "run-on-gloss (apply semicolon counter)" : "sense-numbered (keep inline-number)",
    });

    if (runOnGloss) {
      for (const r of perLemma) {
        if (r.inlineSenses > 1 || r.semicolon < 2) continue;   // only the under-split candidates
        candidateRows.push({
          checkpointId: `checkpoint:semicolon-counter:${r.stem}:${code}`,
          diagnosticId: `under-split:${code}:${r.stem}`,
          packetId: "run-on-gloss-sense-counter",
          packetTitle: "Semicolon-aware sense counter for run-on-gloss dictionaries",
          lemma: r.stem,
          dict: code,
          driftClass: "under-split-candidate",
          priority: r.semicolon >= 6 ? "high" : "medium",
          methodComparison: { inlineNumberSenses: r.inlineSenses, semicolonMeanings: r.semicolon, hasClassNumberMarker: r.hasClassNum },
          proposedRule: "Count senses by semicolon segmentation (after dropping the leading headword + noun-class number) for dicts the detection gate marks run-on-gloss.",
          sourcePointers: [{ kind: "source-record", rawHeadword: r.stem, sourceLine: r.startLine, href: r.href, gloss: r.gloss }],
          reviewQuestion: `Should ${code.toUpperCase()} '${r.stem}' count ${r.semicolon} senses (semicolon-aware) instead of ${r.inlineSenses} (inline-number)? Source-verify the gloss separates distinct meanings, not one sense's sub-list.`,
          nextAction: "source-read the linked entry; mark promote-parser-candidate / retain-inline-number / control-only",
          reviewedValue: null, reviewer: null, reviewedAt: null, note: "",
        });
      }
    }
  }
  candidateRows.sort((a, b) => b.methodComparison.semicolonMeanings - a.methodComparison.semicolonMeanings);

  const payload = {
    schemaVersion: "1.0.0",
    status: "r2-parser-promotion-review-packet",
    claim: "A semicolon-aware sense counter is proposed for run-on-gloss dictionaries (e.g. YAT), where the inline-number splitter under-counts senses to 1 and produces the spurious wil→yat 'condensation' (#125). Promotion is reviewer-gated.",
    evidenceLabel: "derived",
    reviewStatus: "needs-human-review",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-r2-semicolon-counter-packet",
    sourceFiles: ["../csl-orig/v02/yat/yat.txt", "../csl-orig/v02/shs/shs.txt", "data/lexico/r2_yat_artifact_check.json"],
    proposedRule: "If a dictionary's entries are not sense-numbered (mean inline-number senses < 1.5) but are semicolon-packed (mean semicolon meanings ≥ 3), count senses by semicolon segmentation instead of inline numbering.",
    detectionGate: "Per-dict gate over the panel: run-on-gloss iff meanInlineSenses < 1.5 AND meanSemicolonMeanings ≥ 3. SHS is the control (sense-numbered → gate OFF).",
    expectedImpactIfPromoted: [
      "YAT panel sense count rises ~1 → ~5.7; the wil→yat drift recomputes from −8 toward parity, retracting the 'drastic condensation' reading.",
      "H3R then has no condensation exemplar on this edge; only wil→shs (copy) and ap90→ap (revision) remain. A genuine condensation edge must be found elsewhere.",
      "No change to SHS (sense-numbered) or to numbered dicts generally.",
    ],
    counts: {
      candidateDicts: CANDIDATE_DICTS.length,
      runOnGlossDicts: dictDetection.filter(d => d.verdict.startsWith("run-on-gloss")).length,
      checkpointRows: candidateRows.length,
    },
    archiveParityPolicy: "Archive parity is a regression signal, not the optimization target; promotion must be justified by source-read meaning separation, not by matching any archived count.",
    limitations: [
      "Semicolons also separate items WITHIN a single sense (e.g. a synonym list); over-splitting is the main risk — each row needs source verification before promotion.",
      "Meaning count drops the leading headword + the first noun-class number heuristically; multi-gender entries ('m. n.') may carry more than one leading marker.",
      "Panel-scoped (28 nouns); a full-corpus pass should confirm the per-dict gate before promotion.",
    ],
    boundaryNote: "This is a parser-promotion proposal, not an applied change. The sense-counting rule is unchanged until a reviewer adjudicates these rows. Owner repo: csl-atlas; routes through the R2 checkpoint process (docs/R2_CHECKPOINT_DECISIONS.md).",
    dictDetection,
    checkpointRows: candidateRows,
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_FILE, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Semicolon-counter packet: ${candidateRows.length} checkpoint rows (needs-human-review)`);
  for (const d of dictDetection) console.log(`  ${d.dict}: inline ${d.meanInlineSenses} / semicolon ${d.meanSemicolonMeanings} -> ${d.verdict}`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT_FILE)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
