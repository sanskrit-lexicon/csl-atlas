// Target dictionaries for the Comparative Dictionary Lab (Phase 2).
//
// `code` is the csl-orig directory/file code (note PWK lives at code "pw").
// `grammarReliable` marks the tagged bilingual dictionaries whose gender is
// extractable from <lex>; the prose Sanskrit-Sanskrit lexica (VCP, SKD)
// are coverage-only in this first slice.

export const DICTS = [
  { code: "mw", label: "MW", grammarReliable: true },
  { code: "ap", label: "AP", grammarReliable: true },
  { code: "pwg", label: "PWG", grammarReliable: true },
  { code: "pw", label: "PWK", grammarReliable: true },
  { code: "wil", label: "WIL", grammarReliable: true },
  { code: "vcp", label: "VCP", grammarReliable: false },
  { code: "skd", label: "SKD", grammarReliable: false }
];

export const DICT_LABELS = Object.fromEntries(DICTS.map(d => [d.code, d.label]));

export function dictHref(code, line) {
  return `https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/${code}/${code}.txt#L${line}`;
}
