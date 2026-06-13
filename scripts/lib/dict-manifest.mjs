// Target dictionaries for the Comparative Dictionary Lab (Phase 2).
//
// `code` is the csl-orig directory/file code (note PWK lives at code "pw").
// `grammarReliable` marks the tagged bilingual dictionaries whose gender is
// extractable from <lex>; the prose Sanskrit-Sanskrit lexica (VCP, SKD)
// are coverage-only in this first slice.

import { CORE_COMPARISON_DICTS } from "./dict-scope.mjs";

// Capability flags per dictionary:
// - grammarReliable: gender extractable from <lex> (tagged bilingual dicts).
// - homonymMarked: records homonyms with an <h> index (MW, PWG, PWK).
// - citationTagged: cites sources with <ls> (MW, AP, PWG, PWK). WIL is
//   essentially untagged for citations; VCP/SKD cite in prose via `iti`.
// - senseSegmented: marks senses structurally — AP with `∙` bullets, PWG/PWK
//   with <div>. MW segments senses in prose (<div> is rare, ~0.05/entry), so a
//   structural sense count is unreliable for it; WIL/VCP/SKD are prose too.
export const DICTS = CORE_COMPARISON_DICTS;

// Sense-division marker per sense-segmented dictionary.
export const SENSE_MARKER = { ap: /∙/g, pwg: /<div\b/g, pw: /<div\b/g };

export const DICT_LABELS = Object.fromEntries(DICTS.map(d => [d.code, d.label]));

export function dictHref(code, line) {
  return `https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/${code}/${code}.txt#L${line}`;
}
