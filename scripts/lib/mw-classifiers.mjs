// MW article-type classifier.
//
// Reproduces the classifier used for the committed treemap counts
// (src/data/article-type-counts.json). Types intentionally OVERLAP:
// a record can be both noun-m and vedic-accented. Counts are membership
// counts, not an exclusive partition.
//
// Rules follow docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md.

// Compound markers seen in <k2>: em dash, hyphen, plus.
const COMPOUND_MARKER = /[—\-+]/;

/**
 * Extract all <ls>...</ls> citation source strings from a record body.
 */
export function extractCitations(body) {
  return [...body.matchAll(/<ls\b[^>]*>([\s\S]*?)<\/ls>/gi)].map(m => m[1].trim());
}

/**
 * Normalize a source abbreviation for "lexicographer-only" detection.
 * Strips a single trailing period and surrounding whitespace.
 */
export function normalizeSource(value) {
  return value.replace(/\s+/g, " ").trim().replace(/\.$/, "");
}

/**
 * True when a record cites at least one source and EVERY citation is "L."
 * (the Monier-Williams lexicographer hedge).
 */
export function isLexicographerOnly(citations) {
  if (citations.length === 0) return false;
  return citations.every(c => normalizeSource(c) === "L");
}

/**
 * Classify a parsed record into the overlapping article-type set.
 * Returns an array of type labels.
 */
export function classifyTypes(record) {
  const { body = "", k2 = "", ecode = "" } = record;
  const types = [];
  const citations = extractCitations(body);

  // Structural types from ecode / k2.
  const isCompound = ecode.startsWith("3") && COMPOUND_MARKER.test(k2);
  const isContinuation = ecode.startsWith("1A");
  const isDerived = ecode.startsWith("2");
  if (body.includes("genuineroot")) types.push("root");
  if (isCompound) types.push("compound");
  if (isContinuation) types.push("continuation");
  if (isDerived) types.push("derived");

  // Grammar types from <lex> markers. These attach only to primary entries
  // (not compound, derived, or continuation) and are mutually exclusive:
  // a record takes a single gender/POS by priority m > f > n > mfn > ind.
  if (!isCompound && !isDerived && !isContinuation) {
    if (/<lex>m\.<\/lex>/.test(body)) types.push("noun-m");
    else if (/<lex>f\.<\/lex>/.test(body)) types.push("noun-f");
    else if (/<lex>n\.<\/lex>/.test(body)) types.push("noun-n");
    else if (/<lex>mfn\.<\/lex>/.test(body)) types.push("adjective-mfn");
    else if (/<lex>ind\.<\/lex>/.test(body)) types.push("indeclinable");
  }

  // Domain / etymology markers.
  if (/<bot\b/.test(body)) types.push("botanical");
  if (/<bio\b/.test(body)) types.push("biographical");
  if (/<lang\b/.test(body)) types.push("etymological-ie");

  // Accent + evidence.
  if (k2.includes("/")) types.push("vedic-accented");
  if (isLexicographerOnly(citations)) types.push("lexicographer-only");

  if (types.length === 0) types.push("other");
  return types;
}

// The canonical type order used in outputs.
export const ARTICLE_TYPES = [
  "root",
  "noun-m",
  "noun-f",
  "noun-n",
  "adjective-mfn",
  "indeclinable",
  "compound",
  "derived",
  "continuation",
  "lexicographer-only",
  "etymological-ie",
  "botanical",
  "biographical",
  "vedic-accented",
  "other"
];
