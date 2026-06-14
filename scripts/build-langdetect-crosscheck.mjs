// Build the detect-language markup cross-check review queue (review layer).
//
// PWG (Petersburg Sanskrit-Wörterbuch) marks Sanskrit object-language as
// {#...#} (SLP1) and German metalanguage as {%...%}. This queue validates the
// SANSKRIT side: it runs the Dharmamitra detect-language classifier (eng vs skt
// SentencePiece fertility) over the distinct single-word {#...#} spans and flags
// the ones that do NOT look like Sanskrit — i.e. German, Latin, or OCR garbage
// mistakenly wrapped in Sanskrit markup.
//
// Direction matters: SLP1/IAST Sanskrit is highly distinctive, so genuine
// Sanskrit reliably classifies "sa" and only true non-Sanskrit spans surface —
// far higher precision than checking the German-gloss side (where the unmodelled
// German fools the classifier). See docs/DHARMAMITRA_INTEGRATION.md.
//
// Two-step pattern: this build extracts candidate spans
// (src/data/external/langdetect-candidates.json), then joins the classification
// snapshot (src/data/external/dharmamitra-langdetect.json) from
// import-dharmamitra-langdetect.py. Both intermediates are large and gitignored;
// only this review queue (the confident mismatches) is committed.
//
// detect-language runs on CPU, so this queue carries REAL findings, not
// model-pending placeholders. It never rewrites PWG markup. No LLM inference.
//
// Usage: npm run build-langdetect-crosscheck

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { dictHref } from "./lib/dict-manifest.mjs";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const MIN_LEN = 4;          // drop 1-3 char fragments (pure noise for SPM)
const MARGIN_RATIO = 0.25;  // flag only when eng is >=25% fewer pieces than skt

const PWG_SOURCE = path.resolve(process.cwd(), "..", "csl-orig", "v02", "pwg", "pwg.txt");
const CANDIDATES = path.resolve(process.cwd(), "src", "data", "external", "langdetect-candidates.json");
const SNAPSHOT = path.resolve(process.cwd(), "src", "data", "external", "dharmamitra-langdetect.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "langdetect-markup-crosscheck-review.json");

const MODEL_POINTER = {
  dictionary: "Dharmamitra detect-language",
  line: null,
  href: "https://github.com/dharmamitra/detect-language"
};
const SPAN_RE = /\{#([^#]*)#\}/g;
const K1_RE = /<k1>([^<]+)/;            // PWG headword on an <L> header line
const SLP1_ACCENTS = /[/\\^~]/g;
const EDGE_PUNCT = /^[^a-zA-Z']+|[^a-zA-Z']+$/g; // strip leading/trailing parens, digits, dots

// Normalize an SLP1 token: drop accents, edge punctuation, and a trailing
// homonym digit, so spans and headwords compare apples-to-apples.
function normToken(raw) {
  return raw.replace(SLP1_ACCENTS, "").replace(EDGE_PUNCT, "").replace(/\d+$/, "").trim();
}

// Single-word Sanskrit spans only (a stray non-Sanskrit token is clearest in
// isolation). Also collect the PWG headword set so genuine Sanskrit words —
// which English has often absorbed as loanwords (yogin, stupa, cakravartin) —
// can be excluded from the flags.
function extractSpansAndHeadwords() {
  const text = fs.readFileSync(PWG_SOURCE, "utf8");
  const lines = text.split(/\r?\n/);
  const bySpan = new Map();
  const headwords = new Set();
  for (let i = 0; i < lines.length; i++) {
    const k1 = lines[i].match(K1_RE);
    if (k1) {
      const h = normToken(k1[1]);
      if (h) headwords.add(h);
    }
    let m;
    SPAN_RE.lastIndex = 0;
    while ((m = SPAN_RE.exec(lines[i])) !== null) {
      const span = normToken(m[1]);
      if (span.length < MIN_LEN) continue;
      if (/[\s+]/.test(span)) continue; // single token only
      if (!bySpan.has(span)) bySpan.set(span, { span, line: i + 1 });
    }
  }
  const candidates = [...bySpan.values()].sort((a, b) => a.span.localeCompare(b.span));
  return { candidates, headwords };
}

function main() {
  const { candidates, headwords } = extractSpansAndHeadwords();

  fs.mkdirSync(path.dirname(CANDIDATES), { recursive: true });
  fs.writeFileSync(CANDIDATES, `${JSON.stringify({
    schemaVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    generatedBy: "npm run build-langdetect-crosscheck",
    note: "Distinct single-word PWG {#...#} SLP1 spans for detect-language; consumed by import-dharmamitra-langdetect.py (which transliterates to IAST).",
    minLen: MIN_LEN,
    count: candidates.length,
    candidates: candidates.map(c => ({ key: c.span, text: c.span }))
  }, null, 2)}\n`);

  let byKey = {};
  let snapshotMeta = null;
  const warnings = [];
  if (fs.existsSync(SNAPSHOT)) {
    const snap = JSON.parse(fs.readFileSync(SNAPSHOT, "utf8"));
    byKey = snap.byKey || {};
    snapshotMeta = { generatedAt: snap.generatedAt, revision: snap.source?.revision, candidateCount: snap.candidateCount };
  } else {
    warnings.push(
      "No detect-language snapshot found (src/data/external/dharmamitra-langdetect.json); " +
      "no mismatches emitted. Run `npm run import-dharmamitra-langdetect` over the candidates file."
    );
  }

  // A confident mismatch: Sanskrit-marked span where eng tokenizes >=25% fewer pieces than skt.
  const preserved = loadPreserved(OUTPUT);
  const items = [];
  let preservedCount = 0;
  let classified = 0;
  let droppedHeadword = 0;

  for (const c of candidates) {
    const rec = byKey[c.span];
    if (!rec) continue;
    classified += 1;
    const { engPieces: e, sktPieces: s } = rec;
    const marginRatio = s > 0 ? (s - e) / s : 0;
    if (!(e < s && marginRatio >= MARGIN_RATIO)) continue; // keep only confident "not Sanskrit"
    if (headwords.has(c.span)) { droppedHeadword += 1; continue; } // genuine Sanskrit loanword, not an error

    const reviewId = `langdetect-markup-crosscheck:${c.span}`;
    if (preserved.has(reviewId)) preservedCount += 1;

    items.push({
      reviewId,
      queue: "langdetect-markup-crosscheck",
      subject: { kind: "markup-span", lemma: c.span, dictionaries: ["PWG"] },
      sourcePointers: [
        { dictionary: "PWG", line: c.line, href: dictHref("pwg", c.line) },
        MODEL_POINTER
      ],
      machineValue: {
        span: c.span,
        iast: rec.iast ?? null,
        markedAs: "sanskrit",
        detected: "not-sanskrit",
        engPieces: e,
        sktPieces: s,
        marginRatio: Math.round(marginRatio * 100) / 100,
        verdict: "marked-sanskrit-looks-foreign"
      },
      evidenceLevel: "inferred", // SPM fertility is a probabilistic signal
      ...reviewFields(preserved, reviewId)
    });
  }

  items.sort((a, b) => b.machineValue.marginRatio - a.machineValue.marginRatio);

  const payload = reviewPayload({
    queue: "langdetect-markup-crosscheck",
    sourcePath: "../csl-orig/v02/pwg/pwg.txt + src/data/external/dharmamitra-langdetect.json",
    items,
    extra: {
      minLen: MIN_LEN,
      marginRatio: MARGIN_RATIO,
      candidateCount: candidates.length,
      classifiedCount: classified,
      headwordCount: headwords.size,
      droppedAsHeadword: droppedHeadword,
      snapshot: snapshotMeta
    },
    assumptions: [
      `Candidates are the ${candidates.length} distinct single-word PWG {#...#} SLP1 spans (length >= ${MIN_LEN}, accents + edge punctuation stripped).`,
      "Each span is transliterated SLP1 -> IAST (in the importer) before classification.",
      "A span is flagged when the English SentencePiece model tokenizes it into >=25% fewer pieces than the Sanskrit one — it does not read as Sanskrit despite Sanskrit markup.",
      "Spans that are PWG headwords are dropped: those are genuine Sanskrit (often loanwords English knows, e.g. yogin/stupa/cakravartin), not markup errors.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "SentencePiece fertility is a heuristic and detect-language models English-vs-Sanskrit, not German; inflected Sanskrit forms and short spans can still misfire. Each flag is a candidate for human review, not a confirmed error.",
      "This queue never rewrites PWG markup or source.",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} langdetect markup-crosscheck items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`  candidates: ${candidates.length} | classified: ${classified} | dropped as PWG headword: ${droppedHeadword} | flagged: ${items.length}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
