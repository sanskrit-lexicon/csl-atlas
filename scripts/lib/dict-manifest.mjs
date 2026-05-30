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
// - senseSegmented: marks senses structurally — AP with `∙` bullets, PWG/PWK
//   with <div>. MW segments senses in prose (<div> is rare, ~0.05/entry), so a
//   structural sense count is unreliable for it; WIL/VCP/SKD are prose too.
export const DICTS = [
  { code: "mw", label: "MW", grammarReliable: true, homonymMarked: true, citationTagged: true, senseSegmented: false },
  { code: "ap", label: "AP", grammarReliable: true, homonymMarked: false, citationTagged: true, senseSegmented: true },
  { code: "pwg", label: "PWG", grammarReliable: true, homonymMarked: true, citationTagged: true, senseSegmented: true },
  { code: "pw", label: "PWK", grammarReliable: true, homonymMarked: true, citationTagged: true, senseSegmented: true },
  { code: "wil", label: "WIL", grammarReliable: true, homonymMarked: false, citationTagged: false, senseSegmented: false },
  { code: "vcp", label: "VCP", grammarReliable: false, homonymMarked: false, citationTagged: false, senseSegmented: false },
  { code: "skd", label: "SKD", grammarReliable: false, homonymMarked: false, citationTagged: false, senseSegmented: false }
];

// Sense-division marker per sense-segmented dictionary.
export const SENSE_MARKER = { ap: /∙/g, pwg: /<div\b/g, pw: /<div\b/g };

export const DICT_LABELS = Object.fromEntries(DICTS.map(d => [d.code, d.label]));

export function dictHref(code, line) {
  return `https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/${code}/${code}.txt#L${line}`;
}
