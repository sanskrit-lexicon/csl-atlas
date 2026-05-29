// MW (Monier-Williams) record parser.
//
// Parses every record in ../csl-orig/v02/mw/mw.txt from <L> through <LEND>,
// preserving source line numbers so every metric can link back to the record.
//
// No LLM inference: this is deterministic markup parsing only.

import fs from "node:fs";
import path from "node:path";

export const MW_SOURCE = path.resolve(process.cwd(), "..", "csl-orig", "v02", "mw", "mw.txt");

export const MW_HREF_BASE =
  "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt";

function field(headerLine, tag) {
  // Header tags are flat, e.g. <L>1<pc>1,1<k1>a<k2>a<h>1<e>1
  const m = headerLine.match(new RegExp(`<${tag}>([^<\\r\\n]*)`));
  return m ? m[1] : null;
}

/**
 * Parse a single record's header line into structured fields.
 */
export function parseHeader(headerLine) {
  return {
    L: field(headerLine, "L"),
    pc: field(headerLine, "pc"),
    k1: field(headerLine, "k1"),
    k2: field(headerLine, "k2"),
    h: field(headerLine, "h"),
    ecode: field(headerLine, "e")
  };
}

/**
 * Iterate MW records. Yields one object per <L>..<LEND> record.
 *
 * @param {string} text full mw.txt contents
 */
export function* iterateRecords(text) {
  const lines = text.split(/\r?\n/);
  let header = null;
  let startLine = 0;
  let bodyLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("<L>")) {
      header = line;
      startLine = i + 1; // 1-based, matches GitHub line anchors
      bodyLines = [];
    } else if (line.startsWith("<LEND>")) {
      if (header == null) continue;
      const fields = parseHeader(header);
      const body = bodyLines.join("\n");
      yield {
        ...fields,
        startLine,
        href: `${MW_HREF_BASE}#L${startLine}`,
        body,
        raw: `${header}\n${body}`
      };
      header = null;
      bodyLines = [];
    } else if (header != null) {
      bodyLines.push(line);
    }
  }
}

/**
 * Read and parse all MW records into an array.
 */
export function parseMwFile(file = MW_SOURCE) {
  if (!fs.existsSync(file)) {
    throw new Error(`Missing MW source: ${file}`);
  }
  const text = fs.readFileSync(file, "utf8");
  return [...iterateRecords(text)];
}
