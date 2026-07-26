// Drift guard for the two hand-written xref taxonomy companions (H1648).
//
// XREF_SHARED_CORE_LABEL_TAXONOMY.md and its Russian sibling .ru.md restate figures that
// actually live in two committed JSON artifacts. Prose companions in two languages are
// exactly the kind of thing that goes stale silently: someone re-runs the measurement,
// updates one file, and the other keeps quoting a number that is no longer true. These
// tests pin every load-bearing figure in BOTH documents to the data, so that drift fails
// CI instead of misleading a reviewer.
//
// Deliberately NOT a full translation-parity check — wording is allowed to differ, and
// asserting sentence-level equivalence across languages would be noise. Only the numbers
// and the closed label vocabulary are contractual.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (...p) => fs.readFileSync(path.join(root, ...p), "utf8");

const agreement = JSON.parse(read("data", "lexico", "xref_marker_agreement.json"));
const packet = JSON.parse(read("data", "lexico", "xref_source_check_packet.json"));

const DOCS = [
  ["en", read("docs", "XREF_SHARED_CORE_LABEL_TAXONOMY.md")],
  ["ru", read("docs", "XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md")],
];

/** Digits only, so "2,750" (en) and "2 750" (ru) compare equal. */
const digits = s => String(s).replace(/[^0-9]/g, "");
/** All numeric tokens in a document, separators stripped. */
const numbersIn = doc => new Set((doc.match(/\d[\d  ,.]*/g) ?? []).map(digits).filter(Boolean));

function assertPresent(label, doc, lang, value) {
  assert.ok(
    numbersIn(doc).has(digits(value)),
    `${lang} taxonomy doc is missing ${label} = ${value} (data changed? regenerate the prose)`,
  );
}

test("both taxonomy docs quote the committed marker-agreement figures", () => {
  const a = agreement.agreement;
  const c = agreement.counts;
  for (const [lang, doc] of DOCS) {
    assertPresent("headwordsInBoth", doc, lang, c.headwordsInBoth);
    assertPresent("opportunityEdges", doc, lang, a.opportunityEdges);
    assertPresent("agreeingEdges", doc, lang, a.agreeingEdges);
    assertPresent("mwCfEdges", doc, lang, c.mwCfEdges);
    assertPresent("pwgAllEdges", doc, lang, c.pwgAllEdges);
    assertPresent("nullDraws", doc, lang, a.nullDraws);
    assertPresent("seed", doc, lang, a.seed);
    // Percentages and the enrichment multiplier, as rendered.
    assertPresent("agreementRate %", doc, lang, (100 * a.agreementRate).toFixed(1));
    assertPresent("expectedRate %", doc, lang, (100 * a.expectedRate).toFixed(3));
    assertPresent("enrichment", doc, lang, Math.round(a.enrichment));
  }
});

test("both taxonomy docs quote the committed sample counts", () => {
  const rows = packet.counts.sharedCoreRows;
  const sparse = packet.counts.sharedCoreRowsWithMissingExactEdge;
  const controls = packet.counts.prefixControlRows;
  for (const [lang, doc] of DOCS) {
    assertPresent("sharedCoreRows", doc, lang, rows);
    assertPresent("sharedCoreRowsWithMissingExactEdge", doc, lang, sparse);
    assertPresent("prefixControlRows", doc, lang, controls);
    // The candidate pool the 40 are sliced from; not in the packet counts, so pinned
    // to the shared-edge CSV itself rather than to a number typed twice.
    const pool = read("data", "lexico", "xref_shared_edges.csv").trim().split(/\r?\n/).length - 1;
    assertPresent("shared-edge pool", doc, lang, pool);
  }
});

test("both taxonomy docs cover every sheet-applicable label, and no retired one", () => {
  const onSheet = packet.packetLabelVocabulary.filter(e => e.appliesToSheet).map(e => e.label);
  const offSheet = packet.packetLabelVocabulary.filter(e => !e.appliesToSheet).map(e => e.label);
  for (const [lang, doc] of DOCS) {
    for (const label of onSheet) {
      assert.ok(doc.includes(`\`${label}\``), `${lang} doc never mentions sheet label \`${label}\``);
    }
    for (const label of offSheet) {
      assert.ok(
        doc.includes(`\`${label}\``),
        `${lang} doc should still explain why \`${label}\` is not an answer option`,
      );
    }
  }
});

test("neither taxonomy doc still claims the retracted independence justification", () => {
  // H1648: "both dictionaries, independently" was the justification MG rejected. It must
  // survive only inside the section that explicitly retracts it.
  for (const [lang, doc] of DOCS) {
    const retractionHeading = lang === "en"
      ? "What a shared reference does *not* prove"
      : "Что общая ссылка НЕ доказывает";
    assert.ok(doc.includes(retractionHeading), `${lang} doc lost its retraction section`);
    const beforeRetraction = doc.slice(0, doc.indexOf(retractionHeading));
    const claim = lang === "en" ? /independently[,]? print/i : /независимо[^.]{0,40}печата/i;
    assert.ok(
      !claim.test(beforeRetraction),
      `${lang} doc asserts the retracted "independently print" justification before retracting it`,
    );
  }
});

test("the Russian doc is actually Russian, and the English one is not", () => {
  const cyrillicShare = s => (s.match(/[А-Яа-яЁё]/g) ?? []).length / s.length;
  const ru = DOCS.find(([l]) => l === "ru")[1];
  const en = DOCS.find(([l]) => l === "en")[1];
  assert.ok(cyrillicShare(ru) > 0.2, "the .ru.md companion is not predominantly Cyrillic");
  assert.ok(cyrillicShare(en) < 0.02, "the English companion has drifted into Russian");
});
