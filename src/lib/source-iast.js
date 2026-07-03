// Render a raw csl-orig source line into readable IAST for display.
//
// SLP1 is a machine key; a raw dictionary line like
//   {#aBAga#}¦, <lex>f.</lex> {#A#} <ls>TĀṆḌYA-BR. 6,7,5</ls>.
// is unreadable to a human. This transcodes the SLP1 Sanskrit to IAST and drops
// the markup shell, honoring each dictionary's own encoding:
//   - MW            : Sanskrit lives in <s>…</s>
//   - PW/PWG/AP/WIL : Sanskrit in {#…#} (or {@…@}); the meaning language sits in
//                     {%…%} and is left as-is (German/English, already roman)
//   - VCP/SKD       : the whole prose body is SLP1
// Non-SLP1 spans — English/German glosses, <ls> citations, grammar abbreviations
// like "f." — are preserved. Reuse anywhere a raw source snippet is shown.

import { from_slp1 } from "./sanskrit-util.js";

// Dictionaries whose entire body is SLP1 prose rather than markup-scoped SLP1.
const PROSE_SLP1 = new Set(["vcp", "skd"]);

// Transcode the maximal roman-letter runs of an SLP1 stream, leaving digits,
// punctuation and separators intact. Lowercase abbreviations (VCP "pu0", "na0")
// map to themselves; only the meaningful SLP1 capitals (A→ā, B→bh, …) change.
function transcodeProse(text) {
  return text.replace(/[A-Za-z~']+/g, (m) => from_slp1(m));
}

function stripMarkup(text) {
  return text
    .replace(/<info[^>]*\/?>/gi, "")   // metadata self-closing tags
    .replace(/\[Page[^\]]*\]/g, "")    // VCP/SKD page markers
    .replace(/<[^>]+>/g, "");          // any remaining tag shell (keep inner text)
}

/** One raw source line → readable IAST. `code` is the csl-orig dict code. */
export function sourceLineToIast(text, code) {
  if (text == null) return "";
  const c = String(code || "").toLowerCase();

  if (PROSE_SLP1.has(c)) {
    return stripMarkup(transcodeProse(String(text))).replace(/\s+/g, " ").trim();
  }

  let s = String(text);
  // Transcode delimiter-scoped SLP1 first, while the delimiters still mark it.
  s = s.replace(/\{[#@]([^#@]*)[#@]\}/g, (_, x) => from_slp1(x)); // {#…#}, {@…@}
  s = s.replace(/<s\d?>([^<]*)<\/s\d?>/gi, (_, x) => from_slp1(x)); // MW <s>…</s>
  s = s.replace(/\{%([^%]*)%\}/g, (_, x) => x);                    // meaning: unwrap, keep
  return stripMarkup(s).replace(/\s+/g, " ").trim();
}

/** Multi-line snippet → IAST, line by line (preserves line breaks). */
export function sourceTextToIast(text, code) {
  if (text == null) return "";
  return String(text).split("\n").map((l) => sourceLineToIast(l, code)).join("\n");
}
