// Passage-level citation index for the MW citation graph (H7100).
//
// The cross-dictionary graph in data/citations/ is frequency-level: it says
// WHICH text a dictionary cites, not WHICH entry cites it. This builder adds
// the missing source -> MW-entry axis:
//
//   data/citations/source-to-entries.json
//     canonical source label -> MW <L> records (plus the source line pointer),
//     resolved from every <ls> citation in csl-orig/v02/mw/mw.txt.
//
//   data/citations/citation-passage-links.json
//     a 100-link pilot from MW's explicit RV loci to GRETIL's per-verse
//     anchors. Verification is a separate, non-deterministic step
//     (npm run verify-citation-passage-links); this builder only merges the
//     committed verification snapshot.
//
// Design rules:
//   - No DCS ingest. The pilot links OUT to a stable external edition.
//   - Canonical source labels are the data/citations node labels, matched by
//     the diacritic/case fold of the node's canonical_text + variant_forms.
//   - MW abbreviations and their expansions are vendored from the MWS
//     mwauthorities/tooltip.txt (data/citations/mw-source-abbreviations.tsv),
//     because csl-guides has no MW works key. This is what lifts MW from
//     5 resolvable texts in the frequency graph to the full source inventory.
//
// Usage: npm run build-citation-passage-index
//        npm run verify-citation-passage-links
//        npm run build-citation-passage-index   (merges the verification)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import { iterateDict } from "./lib/dict-parser.mjs";
import { extractCitations, normalizeSource } from "./lib/mw-classifiers.mjs";
import { baseForm } from "./lib/mw-source-layers.mjs";
import { parseLocus, inRange, loadVerseCounts } from "./build-citation-link-pilot.mjs";
import { generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-citation-passage-index";
const NODES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_nodes.tsv");
const ABBR_PATH = path.resolve(process.cwd(), "data", "citations", "mw-source-abbreviations.tsv");
const INDEX_OUT = path.resolve(process.cwd(), "data", "citations", "source-to-entries.json");
const LINKS_OUT = path.resolve(process.cwd(), "data", "citations", "citation-passage-links.json");
const VERIFY_PATH = path.resolve(process.cwd(), "data", "citations", "citation-passage-link-verification.json");
const PILOT_TSV = path.resolve(process.cwd(), "data", "citations", "passage_pilot.tsv");
const CHECKS_TSV = path.resolve(process.cwd(), "data", "citations", "passage_pilot_checks.tsv");
const PILOT_CSV = path.resolve(process.cwd(), "data", "citations", "passage_pilot.csv");
const PROVENANCE_PATH = path.resolve(process.cwd(), "data", "citations", "source-to-entries.source.json");
const MW_SOURCE_LABEL = "Ṛgveda";
const MW_HREF = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt";
const GRETIL_RV = "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_Rgveda-edAufrecht.htm";
const GRETIL_SOURCE = "GRETIL, Ṛgveda-Saṃhitā (Aufrecht 1877), TEI transformation";

// Editorial / non-bibliographic MW markers. They stay in the index as named
// buckets (they are genuinely cited) but are never presented as texts.
export const NONTEXT_LABELS = new Set([
  "L", "ib", "W", "MW", "Cat", "Kāv", "Buddh", "Pur", "Col", "Ed", "Comm", "Sch"
]);

const PILOT_SIZE = 100;

/** Diacritic- and case-insensitive fold used by data/citations. */
export function foldText(value) {
  return (value || "")
    // Anusvara is written ṃ in MWS expansions but ṅ/n in several node labels
    // (Rājataraṃgiṇī vs Rājataraṅgiṇī); fold both to n before stripping marks.
    .replace(/[ṃṁ]/g, "n")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");
}

// High-confidence title/author corrections where the MWS tooltip names the
// author or a generic genre rather than the cited work. Each target is an
// existing canonical_text node.
export const SOURCE_OVERRIDES = {
  "Pāṇ": "Aṣṭādhyāyī (Pāṇini)"
};

function normKey(value) {
  return (value || "").normalize("NFC").replace(/\s+/g, " ").trim().replace(/[.,;:]+$/, "");
}

export function parseTsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((line) => line.length > 0);
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

/** Build fold -> canonical_text from the committed node table (canonical + variants). */
export function buildCanonicalAliases(nodeRows) {
  const aliases = new Map();
  for (const row of nodeRows) {
    const canonical = row.canonical_text;
    if (!canonical) continue;
    aliases.set(foldText(canonical), canonical);
    // "Nirukta (Yāska)" should also answer to "Nirukta".
    const bare = canonical.replace(/\s*\([^)]*\)\s*$/, "").trim();
    if (bare && bare !== canonical) aliases.set(foldText(bare), canonical);
    for (const variant of (row.variant_forms || "").split(";")) {
      const v = variant.trim();
      if (v) aliases.set(foldText(v), canonical);
    }
  }
  return aliases;
}

/** MW abbreviation -> IAST expansion, from the vendored MWS tooltip table. */
export function buildAbbreviationMap(rows) {
  const map = new Map();
  for (const row of rows) {
    const key = normKey(row.abbreviation);
    const expansion = (row.expansion_iast || "").trim();
    if (key && expansion) map.set(key, { expansion, type: row.type || "", code: row.code || "" });
  }
  return map;
}

// Candidate strings to match against the node aliases. Expansions carry
// editorial tails ("of the Mahābhārata", "by Yāska", "'s Bṛhatsaṃhitā") that
// the node label omits; each candidate is still a literal substring of the
// MWS expansion, never an inferred identity.
export function expansionCandidates(expansion) {
  const out = new Set();
  let e = (expansion || "").trim();
  if (!e) return [];
  out.add(e);
  e = e.replace(/,\s*by\s+.*$/i, "").replace(/\s+by\s+[^,]+$/i, "");
  out.add(e);
  e = e.replace(/^[^']*'s\s+/u, "");
  out.add(e);
  for (const m of expansion.matchAll(/(?:of|in|the)\s+([^,;)]+)/gi)) {
    // "X of the Mahābhārata" -> Mahābhārata
    out.add(m[1].replace(/^the\s+/i, "").trim());
  }
  const parts = expansion.split(/\s+of\s+(?:the\s+)?|\s*[,;]\s*|\s+or\s+/i);
  for (const part of parts) out.add(part.trim());
  return [...out].filter(Boolean);
}

export function resolveSourceLabel(rawLabel, abbreviationMap, canonicalAliases) {
  const key = normKey(rawLabel);
  if (SOURCE_OVERRIDES[key] && canonicalAliases.has(foldText(SOURCE_OVERRIDES[key]))) {
    return { canonical: SOURCE_OVERRIDES[key], expansion: null, reason: "curated-override" };
  }
  const hit = abbreviationMap.get(key);
  if (!hit) return { canonical: null, expansion: null, reason: "no-abbreviation" };
  for (const candidate of expansionCandidates(hit.expansion)) {
    const canonical = canonicalAliases.get(foldText(candidate));
    if (canonical) return { canonical, expansion: hit.expansion, reason: "expansion-match" };
  }
  return { canonical: null, expansion: hit.expansion, reason: "expansion-unmatched" };
}

/** GRETIL per-verse anchor for the Aufrecht RV edition. */
export function gretilRvId(mandala, hymn, verse) {
  return `RV_${mandala}.${String(hymn).padStart(3, "0")}.${String(verse).padStart(2, "0")}`;
}

export function gretilRvUrl(mandala, hymn, verse) {
  return `${GRETIL_RV}#${gretilRvId(mandala, hymn, verse)}`;
}

function addRecord(source, L, line) {
  if (!source.records.includes(L)) source.records.push(L);
  source.lines[L] = line;
}

// MW sometimes puts the siglum in the tag attribute and leaves only the locus
// in the text: <ls n="RV.">ix, 62, 25</ls>. extractCitations() returns the text
// only, so those citations were previously filed under the bare locus ("ix").
export function extractCitationsWithAttrs(body) {
  const out = [];
  for (const match of (body || "").matchAll(/<ls\b([^>]*)>([\s\S]*?)<\/ls>/gi)) {
    const attrs = match[1] || "";
    const content = match[2].trim();
    const n = (attrs.match(/\bn\s*=\s*"([^"]*)"/) || [])[1] || null;
    out.push({ content, n, raw: match[0] });
  }
  return out;
}

export function buildIndex({ nodeRows, abbreviationRows, limit = null }) {
  const canonicalAliases = buildCanonicalAliases(nodeRows);
  const abbreviationMap = buildAbbreviationMap(abbreviationRows);
  const sources = new Map(); // canonical label -> { citations, records, lines, rawForms }
  const unresolved = new Map(); // raw base -> { citations, expansion, reason }
  const nontext = new Map();
  const rvLoci = new Map();
  let citations = 0;
  let records = 0;
  let scanned = 0;

  for (const rec of iterateDict("mw")) {
    scanned += 1;
    if (limit && scanned > limit) break;
    if (!rec.k1) continue;
    records += 1;
    for (const citation of extractCitationsWithAttrs(rec.body || "")) {
      citations += 1;
      const normalized = normalizeSource(citation.content);
      let rawBase = baseForm(normalized);
      let rawCitation = normalized;
      if (citation.n && /^[ivxlcdm0-9]/i.test(rawBase)) {
        rawBase = baseForm(normalizeSource(citation.n));
        rawCitation = `${normalizeSource(citation.n)} ${normalized}`.trim();
      }
      if (!rawBase) continue;
      const resolved = resolveSourceLabel(rawBase, abbreviationMap, canonicalAliases);

      // Editorial markers are checked before resolution: the MWS tooltip for
      // L. ("Lexicographers, esp. such as Amarasiṃha, Halāyudha, ...") would
      // otherwise fold-match Halāyudha and turn an editorial hedge into a text.
      if (NONTEXT_LABELS.has(rawBase)) {
        const entry = nontext.get(rawBase) || { citations: 0, expansion: resolved.expansion, reason: "editorial-marker" };
        entry.citations += 1;
        nontext.set(rawBase, entry);
      } else if (resolved.canonical) {
        let source = sources.get(resolved.canonical);
        if (!source) {
          source = { citations: 0, records: [], lines: {}, rawForms: {}, rawCitations: new Set() };
          sources.set(resolved.canonical, source);
        }
        source.citations += 1;
        source.rawForms[rawBase] = (source.rawForms[rawBase] || 0) + 1;
        source.rawCitations.add(citation.raw);
        addRecord(source, rec.L, rec.startLine);

        if (resolved.canonical === MW_SOURCE_LABEL) {
          const locus = parseLocus(normalized.replace(/^.*?\.\s*/, ""));
          if (locus.kind === "verse") {
            const key = `${locus.mandala}.${locus.hymn}.${locus.verse}`;
            let item = rvLoci.get(key);
            if (!item) {
              item = { ...locus, key, citations: 0, records: [], lines: {}, raws: new Map() };
              rvLoci.set(key, item);
            }
            item.citations += 1;
            item.raws.set(rawCitation, (item.raws.get(rawCitation) || 0) + 1);
            addRecord(item, rec.L, rec.startLine);
          }
        }
      } else {
        const entry = unresolved.get(rawBase) || { citations: 0, expansion: resolved.expansion, reason: resolved.reason };
        entry.citations += 1;
        unresolved.set(rawBase, entry);
      }
    }
  }

  return { sources, unresolved, nontext, rvLoci, citations, records, scanned, canonicalAliases };
}

function sortObjectByKey(value) {
  return Object.fromEntries(Object.keys(value).sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)).map((key) => [key, value[key]]));
}

function verificationIndex() {
  const snapshot = readJsonIfExists(VERIFY_PATH, fs);
  const results = new Map();
  for (const result of snapshot?.results || []) results.set(result.url, result);
  return { snapshot, results };
}

function writeIndex(index, cslOrig) {
  const sources = {};
  for (const [label, source] of [...index.sources.entries()].sort((a, b) => b[1].citations - a[1].citations || (a[0] < b[0] ? -1 : 1))) {
    sources[label] = {
      dict: "MW",
      citations: source.citations,
      entryCount: source.records.length,
      records: source.records,
      lines: source.lines,
      rawForms: sortObjectByKey(source.rawForms),
      rawCitations: [...source.rawCitations].sort()
    };
  }
  const unresolved = {};
  for (const [raw, entry] of [...index.unresolved.entries()].sort((a, b) => b[1].citations - a[1].citations)) {
    unresolved[raw] = entry;
  }
  const nontext = {};
  for (const [raw, entry] of [...index.nontext.entries()].sort((a, b) => b[1].citations - a[1].citations)) {
    nontext[raw] = entry;
  }
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    license: "CC-BY-SA-4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
    ownerRepo: "csl-atlas",
    generatedBy: GENERATED_BY,
    generatedAt: generatedAtForPayload(readJsonIfExists(INDEX_OUT, fs), {
      schemaVersion: SCHEMA_VERSION,
      generatedBy: GENERATED_BY,
      sources
    }),
    sourceFiles: [
      "../csl-orig/v02/mw/mw.txt",
      "data/citations/ls_citation_nodes.tsv",
      "data/citations/mw-source-abbreviations.tsv",
      "scripts/build-citation-passage-index.mjs"
    ],
    provenance: {
      cslOrig,
      abbreviationSource: "https://github.com/sanskrit-lexicon/MWS/blob/main/mwauthorities/tooltip.txt",
      canonicalLabels: "data/citations/ls_citation_nodes.tsv (canonical_text + variant_forms, diacritic-folded)"
    },
    method: "Parse every MW <L> record and its <ls> citations; reduce each citation to its base abbreviation; expand through the vendored MWS tooltip table; fold the IAST expansion to a canonical_text node label. A source label is canonical only when its expansion fold-matches a committed node (or variant); otherwise the raw label is reported under `unresolved` with its MWS expansion.",
    counts: {
      mwRecordsScanned: index.scanned,
      mwRecordsWithHeadword: index.records,
      citations: index.citations,
      canonicalSources: Object.keys(sources).length,
      indexedCitations: Object.values(sources).reduce((sum, s) => sum + s.citations, 0),
      nontextCitations: Object.values(nontext).reduce((sum, s) => sum + s.citations, 0),
      unresolvedCitations: Object.values(unresolved).reduce((sum, s) => sum + s.citations, 0)
    },
    sources,
    nontext,
    unresolved,
    assumptions: [
      "One canonical source label can own many MW <L> records; records are deduplicated per label and keep the first citing source line.",
      "An <ls> base form is resolved only through the MWS abbreviation table and a literal canonical-node match; no model inference or fuzzy title matching.",
      "Editorial markers (L., ib., W., MW., Cat., ...) are reported separately under `nontext`; they are not bibliographic works and receive no passage links.",
      "Unresolved labels keep their MWS expansion for review; they are deliberately not folded into a node by guesswork."
    ],
    warnings: [
      "The index records WHICH MW entry cites a source, not that the quoted passage is the one the label denotes; it is a retrieval aid, not a quotation verification.",
      "Only MW is indexed here. Other dictionaries can be added with the same per-dictionary abbreviation strategy."
    ]
  };
  fs.writeFileSync(INDEX_OUT, `${JSON.stringify(payload)}\n`);
  return payload;
}

function writeLinks(index, cslOrig) {
  const { snapshot, results } = verificationIndex();
  const verseCounts = loadVerseCounts();
  const candidates = [...index.rvLoci.values()]
    .filter((locus) => !verseCounts || inRange(locus.mandala, locus.hymn, locus.verse, verseCounts))
    .sort((a, b) => b.citations - a.citations || a.mandala - b.mandala || a.hymn - b.hymn || a.verse - b.verse);
  const items = candidates.slice(0, PILOT_SIZE).map((locus) => {
    const url = gretilRvUrl(locus.mandala, locus.hymn, locus.verse);
    const verification = results.get(url) || null;
    return {
      reviewId: `citation-passage:RV:${locus.key}`,
      canonicalText: MW_SOURCE_LABEL,
      rawLabel: "RV",
      rawLocus: [...locus.raws.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? `RV ${locus.key}`,
      locus: locus.key,
      mandala: locus.mandala,
      hymn: locus.hymn,
      verse: locus.verse,
      gretilId: gretilRvId(locus.mandala, locus.hymn, locus.verse),
      url,
      vedawebUrl: `https://vedaweb.uni-koeln.de/rigveda/view/id/${String(locus.mandala).padStart(2, "0")}${String(locus.hymn).padStart(3, "0")}${String(locus.verse).padStart(2, "0")}`,
      mwCitations: locus.citations,
      mwRecords: locus.records,
      mwLines: locus.lines,
      sourcePointer: { dictionary: "MW", line: locus.lines[locus.records[0]] ?? null, href: `${MW_HREF}#L${locus.lines[locus.records[0]] ?? 1}` },
      httpStatus: verification?.httpStatus ?? null,
      anchorVerified: verification?.anchorVerified ?? null,
      verified: Boolean(verification?.ok)
    };
  });

  const verifiedCount = items.filter((item) => item.verified).length;
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    license: "CC-BY-SA-4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
    ownerRepo: "csl-atlas",
    generatedBy: GENERATED_BY,
    generatedAt: generatedAtForPayload(readJsonIfExists(LINKS_OUT, fs), {
      schemaVersion: SCHEMA_VERSION,
      generatedBy: GENERATED_BY,
      items
    }),
    sourceFiles: [
      "data/citations/source-to-entries.json",
      "data/citations/citation-passage-link-verification.json",
      "scripts/build-citation-passage-index.mjs",
      "scripts/verify-citation-passage-links.mjs"
    ],
    provenance: {
      cslOrig,
      linkTarget: GRETIL_RV,
      linkTargetLabel: GRETIL_SOURCE,
      selection: "Top 100 distinct MW Ṛgveda verse loci by citation count, range-checked against the committed per-hymn stanza table."
    },
    summary: {
      pilotSize: items.length,
      requiredPilotSize: PILOT_SIZE,
      verified: verifiedCount,
      http200: items.filter((item) => item.httpStatus === 200).length,
      anchorVerified: items.filter((item) => item.anchorVerified === true).length,
      checkedAt: snapshot?.checkedAt ?? null,
      verificationMethod: snapshot?.method ?? null
    },
    items,
    assumptions: [
      "Locus = MW's explicit RV maṇḍala, hymn, verse (e.g. 'RV. v, 86, 5' -> 5.86.5); work-level and malformed citations are excluded.",
      "The stable passage URL is GRETIL's Aufrecht RV edition with its per-verse anchor RV_<maṇḍala>.<hymn:3>.<verse:2>.",
      "VedaWeb is carried as a second, independently addressable edition; the verified target is GRETIL.",
      "DCS is link-out only and is NOT the verified target: its search pages sit behind an interactive browser challenge, so a machine HTTP check cannot establish a stable passage URL."
    ],
    warnings: [
      "HTTP 200 + anchor presence proves the edition page and verse anchor exist; it does not prove MW's quotation matches the verse. Human spot-checks remain required.",
      "Only MW RV citations are piloted. Epic/purāṇa sources need per-text GRETIL files or another edition with verse anchors."
    ]
  };
  fs.writeFileSync(LINKS_OUT, `${JSON.stringify(payload)}\n`);
  return payload;
}

function tsvCell(value) {
  return String(value ?? "").replace(/\t/g, " ").replace(/[\r\n]+/g, " ").trim();
}

function writePilotTables(pilot) {
  const header = ["dict", "L", "canonical_text", "raw_locus", "dcs_id", "dcs_url", "gretil_url", "vedaweb_url", "status", "evidence"];
  const rows = pilot.items.map((item) => [
    item.sourcePointer?.dictionary ?? "MW",
    item.mwRecords?.[0] ?? "",
    item.canonicalText,
    item.rawLocus,
    "",
    "no-stable-url",
    item.url,
    item.vedawebUrl,
    item.httpStatus ?? "",
    item.verified ? "observed" : "derived"
  ]);
  fs.writeFileSync(PILOT_TSV, [header, ...rows].map((row) => row.map(tsvCell).join("\t")).join("\n") + "\n");

  const checkHeader = ["gretil_url", "status", "final_url", "checked_at", "anchor_verified"];
  const checkRows = pilot.items.map((item) => [
    item.url,
    item.httpStatus ?? "",
    item.url,
    pilot.summary.checkedAt ?? "",
    item.anchorVerified === true ? "yes" : "no"
  ]);
  fs.writeFileSync(CHECKS_TSV, [checkHeader, ...checkRows].map((row) => row.map(tsvCell).join("\t")).join("\n") + "\n");

  const csvCell = (value) => {
    const text = String(value ?? "");
    return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  };
  fs.writeFileSync(PILOT_CSV, [header, ...rows].map((row) => row.map(csvCell).join(",")).join("\n") + "\n");
}

function writeProvenance(cslOrig) {
  const sha256 = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedBy: GENERATED_BY,
    generatedAt: new Date().toISOString(),
    cslOrig,
    abbreviations: {
      path: "data/citations/mw-source-abbreviations.tsv",
      source: "https://github.com/sanskrit-lexicon/MWS/blob/main/mwauthorities/tooltip.txt",
      sha256: sha256(ABBR_PATH)
    },
    outputs: {
      "source-to-entries.json": sha256(INDEX_OUT),
      "citation-passage-links.json": sha256(LINKS_OUT),
      "passage_pilot.tsv": sha256(PILOT_TSV),
      "passage_pilot.csv": sha256(PILOT_CSV),
      "passage_pilot_checks.tsv": sha256(CHECKS_TSV)
    }
  };
  fs.writeFileSync(PROVENANCE_PATH, `${JSON.stringify(payload, null, 2)}\n`);
}

function readCslOrigProvenance() {
  const git = (args) => {
    try {
      return execSync(`git -C ../csl-orig ${args}`, { encoding: "utf8" }).trim();
    } catch {
      return null;
    }
  };
  const dirtyPaths = (git("status --porcelain -- v02/mw/mw.txt") || "").split("\n").filter(Boolean);
  const mwPath = path.resolve(process.cwd(), "..", "csl-orig", "v02", "mw", "mw.txt");
  const mwSha256 = crypto.createHash("sha256").update(fs.readFileSync(mwPath)).digest("hex");
  return {
    revision: git("rev-parse HEAD"),
    dirty: dirtyPaths.length > 0,
    dirtyPaths,
    path: "../csl-orig",
    mwTxtSha256: mwSha256
  };
}

function main() {
  if (!fs.existsSync(ABBR_PATH)) throw new Error(`missing ${path.relative(process.cwd(), ABBR_PATH)}`);
  const nodeRows = parseTsv(fs.readFileSync(NODES_PATH, "utf8"));
  const abbreviationRows = parseTsv(fs.readFileSync(ABBR_PATH, "utf8"));
  const cslOrig = readCslOrigProvenance();
  const index = buildIndex({ nodeRows, abbreviationRows });
  const indexPayload = writeIndex(index, cslOrig);
  const linksPayload = writeLinks(index, cslOrig);
  writePilotTables(linksPayload);
  writeProvenance(cslOrig);
  console.log(`Wrote ${Object.keys(indexPayload.sources).length} canonical sources / ${indexPayload.counts.indexedCitations} indexed citations to:`);
  console.log(`- ${path.relative(process.cwd(), INDEX_OUT)}`);
  console.log(`Wrote ${linksPayload.summary.pilotSize} RV passage links (${linksPayload.summary.verified} verified) to:`);
  console.log(`- ${path.relative(process.cwd(), LINKS_OUT)}`);
  if (linksPayload.summary.pilotSize < PILOT_SIZE) {
    console.log(`  NOTE: only ${linksPayload.summary.pilotSize} distinct RV verse loci available (target ${PILOT_SIZE}).`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
