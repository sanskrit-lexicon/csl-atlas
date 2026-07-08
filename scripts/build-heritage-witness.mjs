// Build the Heritage-witness packet: joins the MW <-> Sanskrit Heritage
// (INRIA) entry-level crosswalk onto the atlas's MW headword set (H346;
// Tier-2 roadmap item 4; sibling of the kosha ingest H345).
//
// The crosswalk is OWNED by SanskritLexicography
// (scripts/heritage_mw_crosswalk.py under HeadwordLists/) and consumed here
// read-only from the sibling checkout — never re-derived. Heritage is an
// independent, non-Cologne witness: "which MW headwords does Heritage
// independently confirm" is atlas-native evidence for the P-series papers'
// attestation arguments.
//
// Join key: normalized SLP1 headword (scripts/lib/dict-normalize.mjs
// normalizeLemma, the same key build-dictionary-comparison.mjs uses to align
// MW against the other dictionaries) on both the MW <k1> and the crosswalk's
// mw_key1 column.
//
// Usage: npm run build-heritage-witness   (then npm run validate-heritage-witness)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { iterateDict } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-heritage-witness";
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "SanskritLexicography");
const CROSSWALK_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "mw_heritage_crosswalk.tsv");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "heritage");
const JSON_OUT = path.join(OUT_DIR, "heritage_witness.json");
const SOURCE_OUT = path.join(OUT_DIR, "heritage_witness.source.json");

export function parseTsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function initialOf(normalized) {
  return normalized.length > 0 ? normalized[0] : "?";
}

// Fold the crosswalk's raw rows into one row per normalized SLP1 key: a row
// with an anchor always wins, then covered-without-anchor, then absent — a
// homonym split (e.g. mw_key1 "aMSaka#1"/"aMSaka#2") can otherwise collapse
// onto the same normalized key with conflicting covered_flag values.
function foldCrosswalk(crosswalkRows) {
  const rank = { anchored: 2, "covered-no-anchor": 1, absent: 0 };
  const byKey = new Map();
  for (const row of crosswalkRows) {
    const { normalized } = normalizeLemma(row.mw_key1);
    if (!normalized) continue;
    const anchor = (row.heritage_entry_anchor ?? "").trim();
    const covered = row.covered_flag === "1";
    const tier = covered ? (anchor ? "anchored" : "covered-no-anchor") : "absent";
    const prev = byKey.get(normalized);
    if (!prev || rank[tier] > rank[prev.tier]) {
      byKey.set(normalized, { tier, anchor: anchor || null });
    }
  }
  return byKey;
}

export function buildPayload(mwRecords, crosswalkRows, { generatedAt } = {}) {
  const crosswalk = foldCrosswalk(crosswalkRows);

  const byHeadword = new Map(); // normalized -> { occurrences, firstLine }
  for (const rec of mwRecords) {
    const { normalized } = normalizeLemma(rec.k1);
    if (!normalized) continue;
    let h = byHeadword.get(normalized);
    if (!h) {
      h = { occurrences: 0, firstLine: rec.startLine };
      byHeadword.set(normalized, h);
    }
    h.occurrences += 1;
  }

  let anchored = 0;
  let coveredNoAnchor = 0;
  let absent = 0;
  const perInitial = new Map(); // initial -> { mwEntries, anchored, coveredNoAnchor }
  const witnessed = [];

  for (const [headword, h] of byHeadword) {
    const match = crosswalk.get(headword);
    const tier = match?.tier ?? "absent";
    if (tier === "anchored") anchored += 1;
    else if (tier === "covered-no-anchor") coveredNoAnchor += 1;
    else absent += 1;

    const initial = initialOf(headword);
    let bucket = perInitial.get(initial);
    if (!bucket) {
      bucket = { initial, mwEntries: 0, anchored: 0, coveredNoAnchor: 0 };
      perInitial.set(initial, bucket);
    }
    bucket.mwEntries += 1;
    if (tier === "anchored") bucket.anchored += 1;
    else if (tier === "covered-no-anchor") bucket.coveredNoAnchor += 1;

    if (tier !== "absent") {
      witnessed.push({
        headword,
        matchTier: tier,
        heritageAnchor: match.anchor,
        occurrences: h.occurrences,
        mwLine: h.firstLine
      });
    }
  }

  witnessed.sort((a, b) => a.headword.localeCompare(b.headword));
  const perInitialRows = [...perInitial.values()].sort((a, b) => a.initial.localeCompare(b.initial));

  const mwEntries = byHeadword.size;
  const heritageCovered = anchored + coveredNoAnchor;

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "SanskritLexicography/HeadwordLists/mw_heritage_crosswalk.tsv",
      "csl-orig/v02/mw/mw.txt",
      "scripts/build-heritage-witness.mjs"
    ],
    method:
      "Iterate MW <L> records from csl-orig v02, normalize each <k1> to SLP1 (strip accents + trailing homonym digits, scripts/lib/dict-normalize.mjs) to get one row per distinct MW headword. Join the SanskritLexicography mw_heritage_crosswalk.tsv (built from the Heritage mirror's own MW<->DICO alignment, no OCR/fuzzy matching) on the same normalized key. matchTier is 'anchored' (covered_flag=1 with a resolved DICO/<file>.html#<key> anchor), 'covered-no-anchor' (covered_flag=1, MW's bare anchor drops DICO's #N homonym suffix and no fallback resolved), or 'absent' (covered_flag=0 or missing from the crosswalk).",
    totals: {
      mwEntries,
      crosswalkRows: crosswalkRows.length,
      heritageCovered,
      anchored,
      coveredNoAnchor,
      absent,
      coveragePct: round(heritageCovered / mwEntries),
      anchoredPct: round(anchored / mwEntries)
    },
    perInitial: perInitialRows,
    witnessed,
    limitations: [
      "Coverage is entry-existence only, not sense-level or definition-level agreement — a match confirms Heritage lists the headword, not that the two dictionaries agree on meaning.",
      "'covered-no-anchor' rows (crosswalk covered_flag=1, no resolved DICO anchor) are a documented crosswalk limitation: MW's plain anchor drops DICO's #N homonym-disambiguation suffix; the crosswalk's homonym-fallback picks the first homonym where possible, but a residual few keys have no DICO-side match at all.",
      "Both sides key on normalized SLP1 (accent-stripped, homonym-digit-stripped); MW records that differ only by homonym suffix or accent collapse onto one witnessed row here, with mwLine/mwHref pointing at the first occurrence and 'occurrences' recording how many MW <L> records share the key.",
      "Heritage coverage is a mirror-derived crosswalk, not a live INRIA query — it reflects the mirror snapshot's own MW<->DICO alignment (see SanskritLexicography/HERITAGE_MIRROR_INVENTORY.md), not the current online Heritage Platform."
    ],
    boundary: [
      "Crosswalk owner is SanskritLexicography (HeadwordLists/heritage_mw_crosswalk.py); this packet only joins and aggregates it onto the atlas's MW headword set — never re-derives the DICO alignment. Rendering owner repo csl-atlas."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  let commit = "unknown";
  let crosswalkCommit = "unknown";
  try {
    commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {}
  try {
    crosswalkCommit = execSync(`git -C "${SIBLING_ROOT}" rev-parse HEAD`, { encoding: "utf8" }).trim();
  } catch {}
  const envelope = {
    dataset: "heritage_witness",
    commit,
    crosswalkRepo: "https://github.com/gasyoun/SanskritLexicography",
    crosswalkPath: "HeadwordLists/mw_heritage_crosswalk.tsv",
    crosswalkCommit,
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  if (!fs.existsSync(CROSSWALK_PATH)) {
    console.error(
      `Crosswalk not found: ${CROSSWALK_PATH}\n` +
        "This builder needs a sibling SanskritLexicography checkout (the committed src/data/heritage/heritage_witness.json is the CI-safe artifact)."
    );
    process.exit(1);
  }
  const mwRecords = [...iterateDict("mw")];
  const crosswalkRows = parseTsv(fs.readFileSync(CROSSWALK_PATH, "utf8"));
  const payload = buildPayload(mwRecords, crosswalkRows);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(`Wrote heritage-witness packet (${payload.totals.mwEntries} MW headwords):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(
    `  heritage covered ${payload.totals.heritageCovered} (${(payload.totals.coveragePct * 100).toFixed(1)}%): ` +
      `anchored ${payload.totals.anchored}, covered-no-anchor ${payload.totals.coveredNoAnchor}`
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
