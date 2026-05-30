// Target dictionaries for the Comparative Dictionary Lab (Phase 2).
//
// `code` is the csl-orig directory/file code (note PWK lives at code "pw").
// `grammarReliable` marks the tagged bilingual dictionaries whose gender is
// extractable from <lex>; the prose Sanskrit-Sanskrit lexica (VCP, SKD)
// are coverage-only in this first slice.

// Capability flags per dictionary:
// - grammarReliable: gender extractable from <lex> (tagged bilingual dicts).
// - homonymMarked: records homonyms with an <h> index (MW, PWG, PWK).
// - citationTagged: cites sources with <ls> (MW, AP, PWG, PWK). WIL is
//   essentially untagged for citations; VCP/SKD cite in prose via `iti`.
export const DICTS = [
  { code: "mw", label: "MW", grammarReliable: true, homonymMarked: true, citationTagged: true },
  { code: "ap", label: "AP", grammarReliable: true, homonymMarked: false, citationTagged: true },
  { code: "pwg", label: "PWG", grammarReliable: true, homonymMarked: true, citationTagged: true },
  { code: "pw", label: "PWK", grammarReliable: true, homonymMarked: true, citationTagged: true },
  { code: "wil", label: "WIL", grammarReliable: true, homonymMarked: false, citationTagged: false },
  { code: "vcp", label: "VCP", grammarReliable: false, homonymMarked: false, citationTagged: false },
  { code: "skd", label: "SKD", grammarReliable: false, homonymMarked: false, citationTagged: false }
];

export const DICT_LABELS = Object.fromEntries(DICTS.map(d => [d.code, d.label]));

export function dictHref(code, line) {
  return `https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/${code}/${code}.txt#L${line}`;
}
