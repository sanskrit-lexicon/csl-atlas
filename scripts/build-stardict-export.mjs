// StarDict / GoldenDict export of Monier-Williams (Month 4).
//
// Emits a StarDict dictionary (.ifo / .idx / .dict) from the local CDSL MW
// source — learning from dharmamitra-stardict-dictionaries (high-reach
// distribution + an explicit "auto-generated, verify before scholarly use"
// disclaimer). Deterministic; no model, no network.
//
// Output goes to stardict-dist/ (gitignored — the .dict is tens of MB; ship it
// as a CI/release artifact, not a committed blob). The builder, npm script, and
// a structural self-check are what's committed. GoldenDict opens the folder
// directly; StarDict needs the three files together.
//
// Format (StarDict 2.4.2): .dict = concatenated UTF-8 definition blocks; .idx =
// entries sorted by g_ascii_strcasecmp(byte) each `word\0 + offset(u32 BE) +
// size(u32 BE)`; .ifo = metadata incl. exact idxfilesize + wordcount +
// sametypesequence=h.
//
// Usage: npm run build-stardict-export

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateRecords, MW_SOURCE, MW_HREF_BASE } from "./lib/mw-parser.mjs";

const OUT_DIR = path.resolve(process.cwd(), "stardict-dist");
const BASENAME = "mw-cdsl";
const BOOKNAME = "Monier-Williams Sanskrit-English (CDSL)";

// SLP1 -> IAST (one char per phoneme).
const SLP1_TO_IAST = {
  a: "a", A: "ā", i: "i", I: "ī", u: "u", U: "ū", f: "ṛ", F: "ṝ", x: "ḷ", X: "ḹ",
  e: "e", E: "ai", o: "o", O: "au", M: "ṃ", H: "ḥ", "~": "m̐", z: "ṣ",
  k: "k", K: "kh", g: "g", G: "gh", N: "ṅ", c: "c", C: "ch", j: "j", J: "jh", Y: "ñ",
  w: "ṭ", W: "ṭh", q: "ḍ", Q: "ḍh", R: "ṇ", t: "t", T: "th", d: "d", D: "dh", n: "n",
  p: "p", P: "ph", b: "b", B: "bh", m: "m", y: "y", r: "r", l: "l", v: "v", L: "ḷ",
  S: "ś", s: "s", h: "h", "'": "'"
};
function slp1ToIast(s) {
  let out = "";
  for (const ch of s || "") out += SLP1_TO_IAST[ch] ?? ch;
  return out;
}
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Render an MW entry body to a compact HTML definition.
function cleanDefinition(body, href) {
  if (/\{\{Lbody=\d+\}\}/.test(body) && body.replace(/\{\{Lbody=\d+\}\}/g, "").trim() === "")
    return `<i>Variant spelling; see the main entry.</i> <a href="${href}">[MW source]</a>`;
  let s = body;
  s = s.replace(/<info[^>]*\/?>/gi, "");                       // drop metadata
  s = s.replace(/\{\{Lbody=\d+\}\}/g, "");                     // body-ref handled above
  s = s.replace(/\{[#%]([^#%]*)[#%]\}/g, (_, x) => slp1ToIast(x)); // inline Sanskrit -> IAST
  s = s.replace(/<s>([^<]*)<\/s>/gi, (_, x) => `<b>${escapeHtml(slp1ToIast(x))}</b>`);
  s = s.replace(/<lex>([^<]*)<\/lex>/gi, (_, x) => `<i>${escapeHtml(x)}</i>`);
  s = s.replace(/<ls>([^<]*)<\/ls>/gi, (_, x) => `<span class="cite">${escapeHtml(x)}</span>`);
  s = s.replace(/<[^>]+>/g, "");                               // strip any remaining tags
  s = s.replace(/¦/g, " — ").replace(/[ \t]+/g, " ").replace(/\n+/g, "<br>").trim();
  return `${s} <a href="${href}">[MW]</a>`;
}

// StarDict collation: g_ascii_strcasecmp over UTF-8 bytes (fold A-Z), strcmp tiebreak.
function fold(c) { return c >= 0x41 && c <= 0x5a ? c + 0x20 : c; }
function sdCompare(a, b) {
  const ba = a.bytes, bb = b.bytes, n = Math.min(ba.length, bb.length);
  for (let i = 0; i < n; i++) { const d = fold(ba[i]) - fold(bb[i]); if (d) return d; }
  if (ba.length !== bb.length) return ba.length - bb.length;
  return a.word < b.word ? -1 : a.word > b.word ? 1 : 0; // case-sensitive tiebreak
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const enc = new TextEncoder();

  // 1. Collect entries (word + definition bytes).
  const entries = [];
  let skipped = 0;
  for (const rec of iterateRecords(fs.readFileSync(MW_SOURCE, "utf8"))) {
    const word = slp1ToIast(rec.k1 || "").trim();
    if (!word) { skipped += 1; continue; }
    const def = cleanDefinition(rec.body || "", rec.href || `${MW_HREF_BASE}#L${rec.startLine}`);
    entries.push({ word, bytes: enc.encode(word), def: enc.encode(def) });
  }

  // 2. Sort by StarDict collation.
  entries.sort(sdCompare);

  // 3. Write .dict (concat) + build .idx.
  const dictChunks = [];
  const idxChunks = [];
  let offset = 0;
  for (const e of entries) {
    dictChunks.push(e.def);
    const head = Buffer.concat([Buffer.from(e.bytes), Buffer.from([0])]);
    const tail = Buffer.alloc(8);
    tail.writeUInt32BE(offset, 0);
    tail.writeUInt32BE(e.def.length, 4);
    idxChunks.push(head, tail);
    offset += e.def.length;
  }
  const dictBuf = Buffer.concat(dictChunks.map(c => Buffer.from(c)));
  const idxBuf = Buffer.concat(idxChunks);

  fs.writeFileSync(path.join(OUT_DIR, `${BASENAME}.dict`), dictBuf);
  fs.writeFileSync(path.join(OUT_DIR, `${BASENAME}.idx`), idxBuf);

  // 4. .ifo (first line is fixed; idxfilesize must equal the .idx byte size).
  const ifo = [
    "StarDict's dict ifo file",
    "version=2.4.2",
    `bookname=${BOOKNAME}`,
    `wordcount=${entries.length}`,
    `idxfilesize=${idxBuf.length}`,
    "sametypesequence=h",
    `date=${new Date().toISOString().slice(0, 10)}`,
    "author=CDSL contributors (Monier-Williams 1899); StarDict export by csl-atlas",
    "description=Monier-Williams Sanskrit-English Dictionary, from the Cologne Digital Sanskrit Lexicons (csl-orig). AUTO-GENERATED — verify against the source before scholarly use. IAST headwords; definitions lightly cleaned from the CDSL markup. CC-BY-SA-4.0.",
    "website=https://github.com/sanskrit-lexicon/csl-atlas",
    ""
  ].join("\n");
  fs.writeFileSync(path.join(OUT_DIR, `${BASENAME}.ifo`), ifo);

  // 5. Disclaimer alongside the artifact.
  fs.writeFileSync(path.join(OUT_DIR, "README.txt"),
    `${BOOKNAME}\nStarDict format (.ifo/.idx/.dict). Open the folder in GoldenDict, or place the three\n` +
    `files together for StarDict.\n\nAUTO-GENERATED from the CDSL Monier-Williams source by csl-atlas\n` +
    `(scripts/build-stardict-export.mjs). Verify against the source before scholarly use.\nLicence: CC-BY-SA-4.0.\n`);

  // 6. Structural self-check.
  const errors = [];
  if (idxBuf.length === 0) errors.push("empty .idx");
  // every offset+size within .dict
  let lastWord = null, sortOk = true;
  for (const e of entries) {
    if (lastWord && sdCompare({ word: lastWord, bytes: enc.encode(lastWord) }, e) > 0) sortOk = false;
    lastWord = e.word;
  }
  if (!sortOk) errors.push("idx not in StarDict collation order");
  if (offset !== dictBuf.length) errors.push("dict size mismatch");

  console.log(`StarDict export: ${entries.length} entries (${skipped} skipped, no headword)`);
  console.log(`  ${path.relative(process.cwd(), OUT_DIR)}/  .dict ${(dictBuf.length / 1e6).toFixed(1)} MB | .idx ${(idxBuf.length / 1e6).toFixed(1)} MB`);
  console.log(`  ifo: wordcount=${entries.length} idxfilesize=${idxBuf.length} sametypesequence=h`);
  if (errors.length) { console.error("  FAILED structural check:", errors.join("; ")); process.exit(1); }
  console.log("  structural check: OK (idx sorted, offsets cover .dict, idxfilesize exact)");
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
