// DTB link-target pilot — Ṛgveda citations → VedaWeb (review layer).
//
// Month 2 of DHARMAMITRA_MONTHLY_PLAN.md / MITRA_ALIGNER_HANDOFF.md. The handoff
// framed link-targets around mitra-aligner (passage retrieval). But the data
// shows the high-value path needs NO alignment: MW cites the Ṛgveda with an
// EXPLICIT locus (e.g. <ls>RV. v, 86, 5</ls> = maṇḍala 5, hymn 86, verse 5), so
// the link-target is just locus-parsing → a stable digital-edition URL. VedaWeb
// (vedaweb.uni-koeln.de, a Cologne-family RV edition) is addressable by a
// zero-padded MMHHHVV stanza id, confirmed: 5.86.5 -> /rigveda/view/id/0508605.
//
// This deterministic build parses MW's RV citations, resolves each locus to a
// VedaWeb link, validates the maṇḍala/hymn range against the known RV structure,
// and emits a `citation-link-target` review queue of proposed links. A human
// ratifies before any link is written to csl-orig (per the org DTB workflow);
// the atlas only proposes. mitra-aligner remains the tool for the residual
// quote-only / vague citations (see the handoff) — out of scope for this pilot.
//
// Usage: npm run build-citation-link-pilot. No model, no network at build time.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const MW_SOURCE = path.resolve(process.cwd(), "..", "csl-orig", "v02", "mw", "mw.txt");
const MW_HREF = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt";
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "citation-link-pilot-review.json");
const VERSE_COUNTS_PATH = path.resolve(process.cwd(), "src", "data", "external", "rv-verse-counts.json");

const VEDAWEB_BASE = "https://vedaweb.uni-koeln.de/rigveda/view/id/";
const VEDAWEB_WORK = "https://vedaweb.uni-koeln.de/rigveda";

// One <ls>RV. ...</ls>; capture the locus text after "RV.".
const RV_CITE_RE = /<ls>\s*RV\.\s*([^<]*?)\s*<\/ls>/gi;
const ROMAN = { i: 1, ii: 2, iii: 3, iv: 4, v: 5, vi: 6, vii: 7, viii: 8, ix: 9, x: 10 };
// Known Ṛgveda structure: hymns per maṇḍala (1..10). Used to range-check loci.
const HYMNS_PER_MANDALA = { 1: 191, 2: 43, 3: 62, 4: 58, 5: 87, 6: 75, 7: 104, 8: 103, 9: 114, 10: 191 };

export function vedawebId(m, h, v) {
  return String(m).padStart(2, "0") + String(h).padStart(3, "0") + String(v).padStart(2, "0");
}

// Load the per-hymn stanza-count table (npm run import-rv-verse-counts). Absent
// snapshot → null, and validation falls back to the conservative global cap.
export function loadVerseCounts(file = VERSE_COUNTS_PATH) {
  try {
    const data = JSON.parse(fs.readFileSync(file, "utf8"));
    if (data?.versesPerHymn) return data;
  } catch { /* snapshot not present — fall back below */ }
  return null;
}

// Stanzas in (maṇḍala, hymn) per the table, or null when the table is absent or
// the hymn is unknown to it.
function stanzasIn(verseCounts, m, h) {
  const arr = verseCounts?.versesPerHymn?.[m];
  return arr ? (arr[h - 1] ?? null) : null;
}

// Parse the locus text after "RV.". Returns {kind, mandala?, hymn?, verse?}.
export function parseLocus(raw) {
  const s = raw.replace(/\.\s*$/, "").trim();
  if (!s) return { kind: "work-level" };               // bare "RV."
  if (/[;&]| and /i.test(s)) return { kind: "multi" };  // combined refs -> link-splitting
  const parts = s.split(",").map(p => p.trim()).filter(Boolean);
  const m = ROMAN[parts[0]?.toLowerCase()];
  if (!m) return { kind: "unparseable", raw: s };
  if (parts.length > 3) return { kind: "ambiguous", raw: s }; // e.g. "i, 1, 64, 6" (malformed)
  const h = parts[1] && /^\d+$/.test(parts[1]) ? Number(parts[1]) : null;
  const v = parts[2] && /^\d+$/.test(parts[2]) ? Number(parts[2]) : null;
  if (h == null) return parts.length === 1 ? { kind: "mandala-only", mandala: m } : { kind: "unparseable", raw: s };
  if (v == null) return { kind: "hymn-level", mandala: m, hymn: h };
  return { kind: "verse", mandala: m, hymn: h, verse: v };
}

// Range-check a verse locus. Maṇḍala and hymn are always validated exactly. The
// verse is validated against that hymn's actual stanza count when the per-hymn
// table (npm run import-rv-verse-counts) is present; otherwise it falls back to
// a conservative global cap (no RV hymn exceeds 58 stanzas).
const MAX_VERSE = 58;
export function inRange(m, h, v, verseCounts = null) {
  if (HYMNS_PER_MANDALA[m] == null || h < 1 || h > HYMNS_PER_MANDALA[m] || v < 1) return false;
  const stanzas = stanzasIn(verseCounts, m, h);
  return stanzas != null ? v <= stanzas : v <= MAX_VERSE;
}

function main() {
  const lines = fs.readFileSync(MW_SOURCE, "utf8").split(/\r?\n/);
  const verseCounts = loadVerseCounts();
  const verseValidation = verseCounts ? "exact-per-hymn" : "global-cap";
  const byLocus = new Map(); // "m.h.v" -> { mandala,hymn,verse, count, line, raw }
  const tally = { verse: 0, "hymn-level": 0, "mandala-only": 0, "work-level": 0, multi: 0, ambiguous: 0, unparseable: 0, "out-of-range": 0 };
  let totalCites = 0;
  let verseExceedsHymn = 0; // out-of-range citations caught specifically by the per-hymn table

  for (let i = 0; i < lines.length; i++) {
    let m;
    RV_CITE_RE.lastIndex = 0;
    while ((m = RV_CITE_RE.exec(lines[i])) !== null) {
      totalCites += 1;
      const loc = parseLocus(m[1]);
      if (loc.kind !== "verse") { tally[loc.kind] += 1; continue; }
      if (!inRange(loc.mandala, loc.hymn, loc.verse, verseCounts)) {
        tally["out-of-range"] += 1;
        const stanzas = stanzasIn(verseCounts, loc.mandala, loc.hymn);
        if (stanzas != null && loc.hymn <= HYMNS_PER_MANDALA[loc.mandala] && loc.verse > stanzas) verseExceedsHymn += 1;
        continue;
      }
      tally.verse += 1;
      const key = `${loc.mandala}.${loc.hymn}.${loc.verse}`;
      let e = byLocus.get(key);
      if (!e) { e = { ...loc, key, count: 0, line: i + 1, raw: m[1].trim() }; byLocus.set(key, e); }
      e.count += 1;
    }
  }

  const candidates = [...byLocus.values()].sort((a, b) =>
    a.mandala - b.mandala || a.hymn - b.hymn || a.verse - b.verse);

  const preserved = loadPreserved(OUTPUT);
  const items = [];
  let preservedCount = 0;
  for (const c of candidates) {
    const id = vedawebId(c.mandala, c.hymn, c.verse);
    const reviewId = `citation-link-target:RV:${c.key}`;
    if (preserved.has(reviewId)) preservedCount += 1;
    items.push({
      reviewId,
      queue: "citation-link-target",
      subject: { kind: "citation", lemma: null, dictionaries: ["MW"] },
      sourcePointers: [
        { dictionary: "MW", line: c.line, href: `${MW_HREF}#L${c.line}` },
        { dictionary: "VedaWeb RV", line: null, href: `${VEDAWEB_BASE}${id}` }
      ],
      machineValue: {
        source: "RV",
        locus: c.key,
        mandala: c.mandala, hymn: c.hymn, verse: c.verse,
        vedawebId: id,
        proposedLink: `${VEDAWEB_BASE}${id}`,
        citationCount: c.count,
        verdict: "link-proposed"
      },
      evidenceLevel: "derived", // deterministic locus parse, not a model guess
      ...reviewFields(preserved, reviewId)
    });
  }

  const payload = reviewPayload({
    queue: "citation-link-target",
    sourcePath: "../csl-orig/v02/mw/mw.txt (<ls>RV. ...</ls>) -> VedaWeb",
    items,
    extra: {
      source: "RV", linkTarget: VEDAWEB_BASE, workLink: VEDAWEB_WORK,
      totalRvCitations: totalCites, distinctVerseLoci: candidates.length,
      verseValidation, // "exact-per-hymn" once the table is imported, else "global-cap"
      verseCountsSource: verseCounts
        ? { name: verseCounts.source?.name, repository: verseCounts.source?.repository, totalHymns: verseCounts.totalHymns, totalStanzas: verseCounts.totalStanzas }
        : null,
      verseExceedsHymn, // citations the per-hymn table rejects that the ≤58 cap would have passed
      breakdown: tally
    },
    assumptions: [
      "Pilot scope: Monier-Williams citations to the Ṛgveda only; one source, the achievable explicit-locus path.",
      "Locus = roman maṇḍala + arabic hymn + verse (e.g. 'RV. v, 86, 5' -> 5.86.5); deduped by locus, citationCount = MW entries citing it.",
      "Link target is VedaWeb (vedaweb.uni-koeln.de) by zero-padded MMHHHVV stanza id.",
      verseCounts
        ? "Maṇḍala, hymn, AND verse are all range-checked exactly: verse against that hymn's stanza count from the VedaWeb stanza index (npm run import-rv-verse-counts)."
        : "Maṇḍala/hymn are range-checked against the known RV hymn counts; verse against a conservative global cap (run npm run import-rv-verse-counts to enable exact per-hymn validation).",
      "This proposes links for human review; it never writes links into csl-orig. Reviews preserved by reviewId across rebuilds."
    ],
    warnings: [
      verseCounts
        ? `Verse indices are validated exactly against each hymn's stanza count (VedaWeb stanza index: ${verseCounts.totalHymns} hymns, ${verseCounts.totalStanzas} stanzas); the per-hymn table rejected ${verseExceedsHymn} citation(s) the old ≤58 cap would have passed. A valid range still does not prove the citation is correct, only that the locus exists — reviewers should spot-check that VedaWeb resolves the stanza.`
        : "Verse uses only a conservative global cap (≤58), so a wrong-but-in-cap verse can still pass. Run npm run import-rv-verse-counts to validate the verse against each hymn's actual stanza count.",
      "Out of scope here: work-level/maṇḍala-only/multi-locus citations (multi = link-splitting, the second DTB sub-task) and quote-only citations (the mitra-aligner case in MITRA_ALIGNER_HANDOFF.md).",
      "VedaWeb is a single-page app: a 200 does not by itself confirm a stanza exists — hence the range-check and the review gate."
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} citation-link-target items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`  RV citations: ${totalCites} | verse validation: ${verseValidation} (per-hymn table rejected ${verseExceedsHymn}) | breakdown: ${JSON.stringify(tally)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
