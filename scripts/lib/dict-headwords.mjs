import { dictFile, iterateDict } from "./dict-parser.mjs";
import { dictHref } from "./dict-manifest.mjs";
import fs from "node:fs";

export const KOSHA_SYNONYM_CODES = new Set(["abch", "acph", "acsj"]);

const KOSHA_GENDER_SUFFIXES = new Map([
  ["puMstrI", ["m", "f"]],
  ["strIpuM", ["f", "m"]],
  ["puMklI", ["m", "n"]],
  ["klIpuM", ["n", "m"]],
  ["strIba", ["f"]],
  ["strI", ["f"]],
  ["puM", ["m"]],
  ["klI", ["n"]],
  ["a", ["adj"]]
]);

function normalizeCode(code) {
  return String(code ?? "").trim().toLowerCase();
}

function dictMeta(input) {
  return typeof input === "string" ? { code: normalizeCode(input), sourceLinkMode: "github" } : {
    ...input,
    code: normalizeCode(input?.code)
  };
}

function linkFor(dict, line) {
  return dict?.sourceLinkMode === "github" ? dictHref(dict.code, line) : null;
}

function headerField(headerLine, tag) {
  const m = headerLine.match(new RegExp(`<${tag}>([^<\\r\\n]*)`));
  return m ? m[1] : null;
}

export function parseKoshaSynonymToken(token) {
  const raw = String(token ?? "").trim().replace(/\s+/g, "");
  if (!raw) return null;
  const m = raw.match(/^(.+)-([A-Za-z]+)$/);
  if (!m) return { k1: raw, genderSuffix: null, genders: [] };
  const [, k1, suffix] = m;
  const genders = KOSHA_GENDER_SUFFIXES.get(suffix) ?? [];
  return { k1, genderSuffix: suffix, genders };
}

export function parseKoshaSynonyms(body) {
  const out = [];
  const re = /<syns><s>([\s\S]*?)<\/s>/g;
  let m;
  while ((m = re.exec(body))) {
    for (const token of m[1].split(",")) {
      const parsed = parseKoshaSynonymToken(token);
      if (parsed?.k1) out.push(parsed);
    }
  }
  return out;
}

export function* iterateKoshaHeadwordsFromText(code, text, options = {}) {
  const dict = dictMeta({ code, sourceLinkMode: options.sourceLinkMode ?? "github" });
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
      const body = bodyLines.join("\n");
      const L = headerField(header, "L");
      for (const synonym of parseKoshaSynonyms(body)) {
        yield {
          L,
          k1: synonym.k1,
          raw: synonym.k1,
          h: null,
          body,
          startLine,
          href: linkFor(dict, startLine),
          adapter: "kosha-syns",
          genderSuffix: synonym.genderSuffix,
          genderHint: synonym.genders.join("")
        };
      }
      header = null;
      bodyLines = [];
    } else if (header != null) {
      bodyLines.push(line);
    }
  }
}

export function* iterateHeadwords(input) {
  const dict = dictMeta(input);
  if (KOSHA_SYNONYM_CODES.has(dict.code)) {
    yield* iterateKoshaHeadwordsFromText(dict.code, fs.readFileSync(dictFile(dict.code), "utf8"), {
      sourceLinkMode: dict.sourceLinkMode
    });
    return;
  }

  for (const rec of iterateDict(dict.code)) {
    if (!rec.k1) continue;
    yield {
      ...rec,
      raw: rec.k1,
      href: linkFor(dict, rec.startLine),
      adapter: "k1",
      genderSuffix: null,
      genderHint: null
    };
  }
}
