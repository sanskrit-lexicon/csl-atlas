// Import an authoritative Ṛgveda per-hymn stanza-count table.
//
// The DTB citation-link pilot (build-citation-link-pilot.mjs) resolves MW's
// <ls>RV. m, h, v</ls> citations to VedaWeb stanza URLs. It validates maṇḍala
// and hymn exactly, but the verse index could only be range-checked against a
// conservative global cap (no RV hymn exceeds 58 stanzas) — so a wrong-but-small
// verse still passed. This snapshot lets the build validate the verse exactly:
// the number of stanzas in each (maṇḍala, hymn) of the Ṛgveda.
//
// Source: VedaWeb's own curated stanza index (vedaweb-data, rv_locations.tsv) —
// the same Cologne-family edition the pilot links to, so the structure matches
// the link target by construction. Per-hymn count = max stanza index per hymn.
//
// This is a networked refresh step by design; normal atlas builds consume the
// generated JSON under src/data/external/ and do not refetch upstream data.
//
// Usage: npm run import-rv-verse-counts

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const OUT = path.resolve(process.cwd(), "src", "data", "external", "rv-verse-counts.json");
const REPO = "https://github.com/VedaWebProject/vedaweb-data";
const RAW = "https://raw.githubusercontent.com/VedaWebProject/vedaweb-data/HEAD";
const LOCATIONS_TSV = `${RAW}/rigveda/info/rv_locations.tsv`;

// Cross-check: the long-known hymns-per-maṇḍala counts. The derived table must
// agree with these exactly, or the upstream file changed shape and we should
// look before trusting it.
const EXPECTED_HYMNS_PER_MANDALA = { 1: 191, 2: 43, 3: 62, 4: 58, 5: 87, 6: 75, 7: 104, 8: 103, 9: 114, 10: 191 };

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Fetch failed ${response.status} ${response.statusText}: ${url}`);
  return response.text();
}

// Parse the rv_locations.tsv `DOTS` column (e.g. "1.1.3" = maṇḍala.hymn.stanza)
// into a per-maṇḍala array of per-hymn stanza counts (index 0 = hymn 1).
export function deriveVerseCounts(tsv) {
  const [headerLine, ...lines] = tsv.trimEnd().split(/\r?\n/);
  const headers = headerLine.split("\t");
  const dotsCol = headers.indexOf("DOTS");
  if (dotsCol === -1) throw new Error('rv_locations.tsv missing the "DOTS" column');

  const max = new Map(); // "m.h" -> highest stanza index seen
  let totalStanzas = 0;
  for (const line of lines) {
    if (!line) continue;
    const dots = line.split("\t")[dotsCol];
    const [m, h, v] = dots.split(".").map(Number);
    if (!Number.isInteger(m) || !Number.isInteger(h) || !Number.isInteger(v)) {
      throw new Error(`Unparseable locus in DOTS column: ${JSON.stringify(dots)}`);
    }
    const key = `${m}.${h}`;
    if (v > (max.get(key) ?? 0)) max.set(key, v);
    totalStanzas += 1;
  }

  const versesPerHymn = {};
  const hymnsPerMandala = {};
  for (const [key, count] of max) {
    const [m, h] = key.split(".").map(Number);
    (versesPerHymn[m] ??= [])[h - 1] = count;
  }
  for (const m of Object.keys(versesPerHymn).map(Number).sort((a, b) => a - b)) {
    const arr = versesPerHymn[m];
    for (let i = 0; i < arr.length; i++) {
      if (arr[i] == null) throw new Error(`Gap in maṇḍala ${m}: hymn ${i + 1} has no stanzas`);
    }
    hymnsPerMandala[m] = arr.length;
  }
  return { versesPerHymn, hymnsPerMandala, totalStanzas };
}

function assertStructure({ hymnsPerMandala, totalStanzas, versesPerHymn }) {
  for (const [m, expected] of Object.entries(EXPECTED_HYMNS_PER_MANDALA)) {
    if (hymnsPerMandala[m] !== expected) {
      throw new Error(`Maṇḍala ${m}: derived ${hymnsPerMandala[m]} hymns, expected ${expected}. Upstream structure changed — verify before committing.`);
    }
  }
  const summed = Object.values(versesPerHymn).reduce((acc, arr) => acc + arr.reduce((a, b) => a + b, 0), 0);
  if (summed !== totalStanzas) throw new Error(`Stanza tally mismatch: per-hymn sum ${summed} ≠ row count ${totalStanzas}`);
}

async function main() {
  const tsv = await fetchText(LOCATIONS_TSV);
  const { versesPerHymn, hymnsPerMandala, totalStanzas } = deriveVerseCounts(tsv);
  assertStructure({ hymnsPerMandala, totalStanzas, versesPerHymn });

  const totalHymns = Object.values(hymnsPerMandala).reduce((a, b) => a + b, 0);
  const longestHymn = Object.values(versesPerHymn).reduce((a, arr) => Math.max(a, ...arr), 0);

  const payload = {
    schemaVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    generatedBy: "npm run import-rv-verse-counts",
    source: {
      name: "VedaWeb curated Ṛgveda stanza index",
      repository: REPO,
      rawFiles: [LOCATIONS_TSV],
      license: {
        label: "VedaWebProject vedaweb-data license",
        url: REPO,
        note: "Structural metadata (stanza counts) re-derived from the VedaWeb edition the pilot links to; verify upstream terms before redistributing outside this atlas."
      }
    },
    assumptions: [
      "Per-hymn stanza count = the highest stanza index attested for that (maṇḍala, hymn) in rv_locations.tsv.",
      "The DOTS column is maṇḍala.hymn.stanza in the same edition VedaWeb serves, so counts match the link target by construction.",
      "Hymns-per-maṇḍala derived here is cross-checked against the long-known counts (1:191 … 10:191)."
    ],
    warnings: [
      "Stanza counts follow VedaWeb's hymn numbering (e.g. the Vālakhilya appended within maṇḍala 8); other editions may number hymns differently.",
      "This validates that a verse index is within a hymn's stanza range — it does not certify a specific MW citation is correct, only that the locus is structurally possible."
    ],
    totalHymns,
    totalStanzas,
    longestHymn,
    hymnsPerMandala,
    versesPerHymn
  };

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote RV verse counts (${totalHymns} hymns, ${totalStanzas} stanzas, longest ${longestHymn}) to ${path.relative(process.cwd(), OUT)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(error => {
    console.error(error);
    process.exit(1);
  });
}
