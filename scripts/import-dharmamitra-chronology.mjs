// Import a compact Dharmamitra Sanskrit Dating chronology snapshot.
//
// This is a networked refresh step by design; normal atlas builds consume the
// generated JSON under src/data/external/ and do not refetch upstream data.
//
// Usage: npm run import-dharmamitra-chronology

import fs from "node:fs";
import path from "node:path";

const OUT = path.resolve(process.cwd(), "src", "data", "external", "dharmamitra-chronology.json");
const REPO = "https://github.com/dharmamitra/sanskrit-dating";
const INTERACTIVE = "https://dharmamitra.github.io/sanskrit-dating/sanskrit_chronology_interactive.html";
const RAW = "https://raw.githubusercontent.com/dharmamitra/sanskrit-dating/main";
const DATED_TSV = `${RAW}/dated_gibbs_full.tsv`;
const TEXT_INFO = `${RAW}/text-information.json`;

const ERA_ORDER = [
  { key: "vedic", label: "Vedic", start: -1700, end: -500 },
  { key: "epic-sutra", label: "Epic & Sutra", start: -500, end: 200 },
  { key: "classical", label: "Classical", start: 200, end: 650 },
  { key: "early-medieval", label: "Early Medieval", start: 650, end: 1200 },
  { key: "late-medieval", label: "Late Medieval", start: 1200, end: 1900 },
  { key: "outside-range", label: "Outside display range", start: null, end: null }
];

function parseNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function parseTsv(text) {
  const [headerLine, ...lines] = text.trimEnd().split(/\r?\n/);
  const headers = headerLine.split("\t");
  return lines.filter(Boolean).map(line => {
    const cols = line.split("\t");
    return Object.fromEntries(headers.map((h, i) => [h, cols[i] ?? ""]));
  });
}

function eraForYear(year) {
  if (!Number.isFinite(year)) return ERA_ORDER.at(-1);
  return ERA_ORDER.find(era =>
    era.start !== null && era.end !== null && year >= era.start && year < era.end
  ) ?? ERA_ORDER.at(-1);
}

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Fetch failed ${response.status} ${response.statusText}: ${url}`);
  return response.text();
}

function main() {
  return Promise.all([fetchText(DATED_TSV), fetchText(TEXT_INFO)]).then(([tsv, infoJson]) => {
    const textInfo = JSON.parse(infoJson);
    const rows = parseTsv(tsv);

    const works = rows.map(row => {
      const info = textInfo[row.work] ?? {};
      const postMedian = parseNumber(row.post_median);
      const credibleLow95 = parseNumber(row.crI_lo95);
      const credibleHigh95 = parseNumber(row.crI_hi95);
      const era = eraForYear(postMedian);
      const work = row.work;
      return {
        work,
        title: info.title || row.title || work,
        author: info.author || "",
        genre: info.genre || "",
        tradition: info.tradition || "",
        dateEstimate: info.date_estimate || "",
        confidence: info.confidence || "",
        source: row.source,
        nChunks: parseNumber(row.n_chunks),
        linguisticEstimate: parseNumber(row.ling_est),
        priorStart: parseNumber(row.nb),
        priorEnd: parseNumber(row.na),
        postMedian,
        credibleLow95,
        credibleHigh95,
        eraKey: era.key,
        era: era.label,
        dharmaNexusUrl: `https://dharmamitra.org/nexus/db/sa/${work}/text`
      };
    });

    const eraCounts = ERA_ORDER.map(era => {
      const subset = works.filter(work => work.eraKey === era.key);
      return {
        key: era.key,
        label: era.label,
        start: era.start,
        end: era.end,
        count: subset.length,
        anchored: subset.filter(work => work.source === "anchor").length,
        inferred: subset.filter(work => work.source !== "anchor").length
      };
    });

    const payload = {
      schemaVersion: "1.0.0",
      generatedAt: new Date().toISOString(),
      generatedBy: "npm run import-dharmamitra-chronology",
      source: {
        name: "Dharmamitra Sanskrit Dating",
        repository: REPO,
        interactiveUrl: INTERACTIVE,
        rawFiles: [DATED_TSV, TEXT_INFO],
        license: {
          label: "Dharmamitra GitHub organization license",
          url: "https://github.com/dharmamitra",
          note: "License/attribution source requested by the importer; verify upstream terms before redistributing outside this atlas."
        }
      },
      assumptions: [
        "Imported fields are a compact snapshot for comparison, not a replacement for MW source-layer buckets.",
        "postMedian and crI_lo95/crI_hi95 are model outputs from Dharmamitra Sanskrit Dating.",
        "Era buckets mirror the public Dharmamitra interactive page and are used only for external context."
      ],
      warnings: [
        "Dharmamitra chronology estimates are posterior/model estimates, not established facts.",
        "Do not use these imported dates to rewrite MW source layers automatically."
      ],
      eraOrder: ERA_ORDER,
      eraCounts,
      workCount: works.length,
      works
    };

    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
    console.log(`Wrote ${works.length} Dharmamitra chronology rows to ${path.relative(process.cwd(), OUT)}`);
  });
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
