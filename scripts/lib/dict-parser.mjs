// Generic CDSL dictionary parser.
//
// All target dictionaries share the <L>..<LEND> record shell with an <k1>
// headword. This parser is config-light: it yields line-accurate records and
// extracts the headword plus a normalized gender from <lex> for the tagged
// bilingual dictionaries. Prose lexica (VCP, SKD) yield headword-only records.

import fs from "node:fs";
import path from "node:path";
import { dictHref } from "./dict-manifest.mjs";

const ROOT = path.resolve(process.cwd(), "..", "csl-orig", "v02");

export function dictFile(code) {
  return path.join(ROOT, code, `${code}.txt`);
}

export function dictExists(code) {
  return fs.existsSync(dictFile(code));
}

function headerField(headerLine, tag) {
  const m = headerLine.match(new RegExp(`<${tag}>([^<\\r\\n]*)`));
  return m ? m[1] : null;
}

/**
 * Map a <lex> value to a coarse gender/POS token.
 * Returns one of m, f, n, adj, ind, or null.
 */
export function genderFromLex(body) {
  const m = body.match(/<lex>([^<]{1,8})<\/lex>/);
  if (!m) return null;
  const v = m[1].trim().toLowerCase().replace(/\.$/, "");
  if (v === "m") return "m";
  if (v === "f") return "f";
  if (v === "n") return "n";
  if (v === "mfn" || v === "mf" || v === "a" || v === "adj") return "adj";
  if (v === "ind" || v === "adv" || v === "pron") return "ind";
  return null;
}

// Prose gender/POS markers for the Sanskrit-Sanskrit lexica (VCP, SKD).
// VCP writes them as "<token>0" right after the headword separator ¦;
// SKD writes them as a comma-delimited "<token>," token.
const PROSE_GENDER = {
  pu: "m", puM: "m",
  strI: "f",
  klI: "n", napuM: "n",
  tri: "adj",
  avya: "ind", vya: "ind"
};

/**
 * Extract a coarse gender/POS from a prose lexicon entry (VCP, SKD), anchored
 * to the first marker token after the headword separator ¦. Returns
 * m / f / n / adj / ind, or null when the leading token is not a gender/POS
 * marker (e.g. a verb-class marker or an unrecognized token).
 */
export function genderFromProse(body, code) {
  const i = body.indexOf("¦");
  if (i === -1) return null;
  let s = body.slice(i + 1).replace(/^[\s,]+/, "");
  s = s.replace(/^\[[^\]]*\]\s*,?\s*/, ""); // skip a leading bracket note like [n]
  const m = code === "vcp" ? s.match(/^([A-Za-z]+)0/) : s.match(/^([A-Za-z]+)\s*,/);
  if (!m) return null;
  return PROSE_GENDER[m[1]] ?? null;
}

const PROSE_GENDER_DICTS = new Set(["vcp", "skd"]);

/**
 * Coarse gender/POS for any dictionary: from <lex> for the tagged dictionaries,
 * from prose markers for the Sanskrit-Sanskrit lexica (VCP, SKD).
 */
export function genderForDict(code, body) {
  return PROSE_GENDER_DICTS.has(code) ? genderFromProse(body, code) : genderFromLex(body);
}

/**
 * Iterate records of one dictionary file.
 * Yields { k1, body, startLine, href }.
 */
export function* iterateDict(code) {
  const text = fs.readFileSync(dictFile(code), "utf8");
  const lines = text.split(/\r?\n/);
  let header = null;
  let startLine = 0;
  let bodyLines = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("<L>")) {
      header = line;
      startLine = i + 1;
      bodyLines = [];
    } else if (line.startsWith("<LEND>")) {
      if (header == null) continue;
      const k1 = headerField(header, "k1");
      const h = headerField(header, "h"); // homonym index, where the dictionary marks one
      yield { k1, h, body: bodyLines.join("\n"), startLine, href: dictHref(code, startLine) };
      header = null;
      bodyLines = [];
    } else if (header != null) {
      bodyLines.push(line);
    }
  }
}
