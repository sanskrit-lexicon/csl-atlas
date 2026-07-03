// Extract the exact source text of a dictionary entry so a reader can see the
// line without opening the whole (often 30–55 MB) csl-orig file — GitHub refuses
// to render blobs that large, so a plain #L<line> anchor never fires.
//
// Two products, both build-time and deterministic:
//   entrySnippet() — a compact <L>..<LEND> window embedded inline in review data.
//   rawHref()      — a raw.githubusercontent.com URL the standalone viewer page
//                    streams for full surrounding context.

import fs from "node:fs";
import { dictFile } from "./dict-parser.mjs";

export const CSL_ORIG_RAW_BASE =
  "https://raw.githubusercontent.com/sanskrit-lexicon/csl-orig/master/v02";

const cache = new Map(); // code -> string[] lines

function linesFor(code) {
  if (!cache.has(code)) cache.set(code, fs.readFileSync(dictFile(code), "utf8").split(/\r?\n/));
  return cache.get(code);
}

/**
 * Compact source snippet for the entry beginning at 1-based `startLine` (the
 * <L> header line). The <L>/<LEND> markup shell is skipped — only the readable
 * body lines are returned, capped at `maxLines`, trailing whitespace trimmed.
 * Returns { bodyStart, end, truncated, text }, or null if out of range / no body.
 */
export function entrySnippet(code, startLine, { maxLines = 3 } = {}) {
  const all = linesFor(code);
  const idx = startLine - 1; // the <L> line
  if (idx < 0 || idx >= all.length) return null;
  const bodyStart = idx + 1;
  const body = [];
  let end = idx;
  let hitEnd = false;
  for (let i = bodyStart; i < all.length; i++) {
    if (all[i].startsWith("<LEND>")) { hitEnd = true; end = i; break; }
    body.push(all[i].replace(/\s+$/, ""));
    end = i;
    if (body.length >= maxLines) break;
  }
  if (!body.length) return null;
  return { bodyStart: bodyStart + 1, end: end + 1, truncated: !hitEnd, text: body.join("\n") };
}

/** raw.githubusercontent.com URL for a dictionary file (no line anchor — raw is text/plain). */
export function rawHref(code, base = CSL_ORIG_RAW_BASE) {
  const c = String(code ?? "").trim().toLowerCase();
  return c ? `${base}/${c}/${c}.txt` : null;
}
