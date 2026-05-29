import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(process.cwd(), "..", "csl-orig", "v02");
const OUT = [
  path.resolve(process.cwd(), "src", "data", "dictionary-coverage.json"),
  path.resolve(process.cwd(), "data", "dictionary-coverage.json")
];

const DISPLAY_CODE = new Map([
  ["pw", "PWK"]
]);

const CURATED_VOLUME_OVERRIDES = new Map([
  ["mw", 1],
  ["pwg", 7],
  ["pw", 7],
  ["ap", 3],
  ["ben", 1],
  ["cae", 1],
  ["wil", 1],
  ["skd", 7],
  ["vcp", 7],
  ["armh", 1],
  ["abch", 1],
  ["acph", 1],
  ["acsj", 1]
]);

const TYPE_LABELS = {
  rootVerb: "root / verbal lemma",
  nounMasculine: "noun masculine",
  nounFeminine: "noun feminine",
  nounNeuter: "noun neuter",
  adjective: "adjective",
  indeclinable: "indeclinable / particle",
  compoundOrSubentry: "compound / continuation",
  properOrEncyclopedic: "proper / encyclopedic",
  other: "other / untyped"
};

const BLOCK_LABELS = {
  head: "head metadata",
  body: "entry body",
  gram: "grammatical marking",
  citeTagged: "tagged source citation",
  citeInlineIti: "inline iti citation",
  hom: "homograph marking",
  etym: "etymology / derivation",
  xref: "cross-reference",
  hedge: "L. hedge",
  info: "digitization info",
  div: "division / paragraph marker"
};

function percent(n, d) {
  if (!d) return 0;
  return Number(((100 * n) / d).toFixed(2));
}

function mean(xs) {
  if (!xs.length) return 0;
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}

function median(xs) {
  if (!xs.length) return 0;
  const sorted = [...xs].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function countMatches(text, re) {
  return [...text.matchAll(re)].length;
}

function charMass(text, re) {
  return [...text.matchAll(re)].reduce((sum, m) => sum + m[0].length, 0);
}

function stripTags(s) {
  return s
    .replace(/<foreign\b[^>]*>(.*?)<\/foreign>/g, "$1")
    .replace(/<name\b[^>]*>(.*?)<\/name>/g, "$1")
    .replace(/<title\b[^>]*>(.*?)<\/title>/g, "$1")
    .replace(/<date\b[^>]*>(.*?)<\/date>/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function firstHeaderTitle(code) {
  const header = path.join(ROOT, code, `${code}header.xml`);
  if (!fs.existsSync(header)) return DISPLAY_CODE.get(code) ?? code.toUpperCase();
  const xml = fs.readFileSync(header, "utf8");
  const key = xml.match(/<title\s+type="key"[^>]*>([\s\S]*?)<\/title>/i);
  const main = xml.match(/<title\s+type="main"[^>]*>([\s\S]*?)<\/title>/i);
  return stripTags((key ?? main)?.[1] ?? DISPLAY_CODE.get(code) ?? code.toUpperCase());
}

function volumeCount(code) {
  if (CURATED_VOLUME_OVERRIDES.has(code)) return CURATED_VOLUME_OVERRIDES.get(code);
  const header = path.join(ROOT, code, `${code}header.xml`);
  if (!fs.existsSync(header)) return null;
  const xml = fs.readFileSync(header, "utf8");
  const volumeMeasure = xml.match(/<measure\b[^>]*unit="volumes"[^>]*quantity="(\d+)"/i);
  if (volumeMeasure) return Number(volumeMeasure[1]);
  const textVolume = xml.match(/(\d+)\s+vols?\./i);
  return textVolume ? Number(textVolume[1]) : null;
}

function splitEntries(text) {
  const entries = text.match(/<L>[\s\S]*?<LEND>/g) ?? [];
  if (entries.length) return entries;
  return text.split(/\r?\n\r?\n+/).filter(Boolean);
}

function keyOf(entry) {
  return entry.match(/<k1>([^<\r\n]+)/)?.[1] ?? "";
}

function hasTaggedGrammar(entry) {
  return /<lex\b[^>]*>[\s\S]*?<\/lex>|<ab\b[^>]*>(?:m\.|f\.|n\.|mfn|mf\.|adj\.|a\.|ind\.|adv\.|cl\.|P\.|A\.|Ā\.|Atm\.|Par\.)<\/ab>/i.test(entry);
}

function hasInlineGrammar(entry) {
  return /\b(?:puMsi|striyAm|napuMsake|liNgam|pulliNga|strIliNga|klIba|avyaya)\b/i.test(entry);
}

function hasRootVerb(entry) {
  return /<info\b[^>]*\bverb=|<root\b|<ab\b[^>]*>cl\.<\/ab>|<ab\b[^>]*>(?:P\.|A\.|Ā\.|Atm\.|Par\.)<\/ab>|\bDh?Atu\b/i.test(entry);
}

function hasCompound(entry, k1) {
  return /[-+]/.test(k1) || /<e>\d+[A-Z]/.test(entry) || /<div\b[^>]*>|<s\b[^>]*>[-+]/i.test(entry);
}

function hasProper(entry) {
  return /<bio\b|<bot\b|<s1\b|<ab\b[^>]*>(?:N\.|Nom\. pr\.|Name)<\/ab>|\b(?:nAmA|iti nAma)\b/i.test(entry);
}

function classify(entry) {
  const k1 = keyOf(entry);
  if (hasRootVerb(entry)) return "rootVerb";
  if (hasCompound(entry, k1)) return "compoundOrSubentry";
  if (hasProper(entry)) return "properOrEncyclopedic";
  if (/<lex\b[^>]*>(?:m\.|masc\.|m\b)[\s\S]*?<\/lex>|<ab\b[^>]*>m\.<\/ab>/i.test(entry)) return "nounMasculine";
  if (/<lex\b[^>]*>(?:f\.|fem\.|f\b)[\s\S]*?<\/lex>|<ab\b[^>]*>f\.<\/ab>/i.test(entry)) return "nounFeminine";
  if (/<lex\b[^>]*>(?:n\.|neut\.|n\b)[\s\S]*?<\/lex>|<ab\b[^>]*>n\.<\/ab>/i.test(entry)) return "nounNeuter";
  if (/<lex\b[^>]*>(?:adj\.|a\.|mfn|mf\.)[\s\S]*?<\/lex>|<ab\b[^>]*>(?:adj\.|a\.)<\/ab>/i.test(entry)) return "adjective";
  if (/<lex\b[^>]*>(?:ind\.|adv\.|prep\.|conj\.|interj\.)[\s\S]*?<\/lex>|<ab\b[^>]*>(?:ind\.|adv\.)<\/ab>/i.test(entry)) return "indeclinable";
  return "other";
}

function blockPresence(entry) {
  return {
    head: /<L>/.test(entry) && /<k1>/.test(entry),
    body: entry.replace(/<L>.*?(\r?\n|$)/, "").replace(/<LEND>/, "").trim().length > 0,
    gram: hasTaggedGrammar(entry) || hasInlineGrammar(entry),
    citeTagged: /<ls\b/i.test(entry),
    citeInlineIti: /\biti\b/i.test(entry),
    hom: /<hom\b|<h>[2-9A-Z]/i.test(entry),
    etym: hasRootVerb(entry) || /<etym\b|<ab\b[^>]*>cf\.<\/ab>|\b(?:deriv|fr\.|from)\b/i.test(entry),
    xref: /<srs\b|<xr\b|<ab\b[^>]*>(?:q\.v\.|cf\.)<\/ab>|\b(?:q\.v\.|see)\b/i.test(entry),
    hedge: /<ls\b[^>]*>\s*L\.\s*<\/ls>/i.test(entry),
    info: /<info\b/i.test(entry),
    div: /<div\b/i.test(entry)
  };
}

function blockSizes(entry) {
  const head = entry.match(/^<L>.*?(?:\r?\n|$)/)?.[0]?.length ?? 0;
  const body = Math.max(0, entry.length - head - "<LEND>".length);
  return {
    head,
    body,
    gram: charMass(entry, /<lex\b[^>]*>[\s\S]*?<\/lex>|<ab\b[^>]*>(?:m\.|f\.|n\.|mfn|mf\.|adj\.|a\.|ind\.|adv\.|cl\.|P\.|A\.|Ā\.|Atm\.|Par\.)<\/ab>/gi),
    citeTagged: charMass(entry, /<ls\b[^>]*>[\s\S]*?<\/ls>/gi),
    citeInlineIti: charMass(entry, /\biti\b(?:\s+.{0,80})?/gi),
    hom: charMass(entry, /<hom\b[^>]*>[\s\S]*?<\/hom>|<h>[2-9A-Z]/gi),
    etym: charMass(entry, /<info\b[^>]*\bverb=[^>]*>|<root\b[^>]*>[\s\S]*?<\/root>|<ab\b[^>]*>cl\.<\/ab>/gi),
    xref: charMass(entry, /<srs\b[^>]*>[\s\S]*?<\/srs>|<xr\b[^>]*>[\s\S]*?<\/xr>|<ab\b[^>]*>(?:q\.v\.|cf\.)<\/ab>/gi),
    hedge: charMass(entry, /<ls\b[^>]*>\s*L\.\s*<\/ls>/gi),
    info: charMass(entry, /<info\b[^>]*>[\s\S]*?<\/info>|<info\b[^>]*\/>/gi),
    div: charMass(entry, /<div\b[^>]*>/gi)
  };
}

function fitBand(score, records, pct, structuredSignals) {
  if (!records) return "empty";
  if (pct.head >= 90 && pct.body >= 90 && pct.gram >= 20 && structuredSignals >= 4) return "full structured fit";
  if (pct.head >= 80 && pct.body >= 80 && pct.citeTagged < 1 && pct.citeInlineIti >= 5) return "prose / iti fit";
  if (pct.head >= 90 && pct.body >= 90 && (pct.gram >= 5 || pct.citeTagged >= 5 || structuredSignals >= 2)) return "partial structured fit";
  if (pct.head >= 80 && pct.body >= 80) return "entry-shell fit";
  return score >= 20 ? "weak fit" : "outside scheme";
}

function analyseDictionary(code) {
  const file = path.join(ROOT, code, `${code}.txt`);
  const text = fs.readFileSync(file, "utf8");
  const entries = splitEntries(text);
  const lengths = [];
  const typeCounts = Object.fromEntries(Object.keys(TYPE_LABELS).map(t => [t, 0]));
  const blockCounts = Object.fromEntries(Object.keys(BLOCK_LABELS).map(b => [b, 0]));
  const blockChars = Object.fromEntries(Object.keys(BLOCK_LABELS).map(b => [b, 0]));
  let lsTotal = 0;
  let inlineItiTotal = 0;

  for (const entry of entries) {
    lengths.push(entry.length);
    typeCounts[classify(entry)] += 1;
    lsTotal += countMatches(entry, /<ls\b/gi);
    inlineItiTotal += countMatches(entry, /\biti\b/gi);

    const presence = blockPresence(entry);
    for (const [block, present] of Object.entries(presence)) {
      if (present) blockCounts[block] += 1;
    }

    const sizes = blockSizes(entry);
    for (const [block, chars] of Object.entries(sizes)) {
      blockChars[block] += chars;
    }
  }

  const records = entries.length;
  const totalChars = lengths.reduce((a, b) => a + b, 0);
  const blockPct = Object.fromEntries(Object.entries(blockCounts).map(([k, v]) => [k, percent(v, records)]));
  const blockCharPct = Object.fromEntries(Object.entries(blockChars).map(([k, v]) => [k, percent(v, totalChars)]));
  const typePct = Object.fromEntries(Object.entries(typeCounts).map(([k, v]) => [k, percent(v, records)]));
  const structuredSignals = ["gram", "citeTagged", "hom", "etym", "xref", "hedge", "info", "div"]
    .filter(k => blockPct[k] >= 1).length;
  const score = Math.round(
    (Math.min(blockPct.head, 100) * 0.15) +
    (Math.min(blockPct.body, 100) * 0.15) +
    (Math.min(blockPct.gram, 100) * 0.2) +
    (Math.min(blockPct.citeTagged, 100) * 0.16) +
    (Math.min(blockPct.hom, 100) * 0.08) +
    (Math.min(blockPct.etym, 100) * 0.08) +
    (Math.min(blockPct.xref, 100) * 0.08) +
    (Math.min(blockPct.info, 100) * 0.05) +
    (Math.min(blockPct.div, 100) * 0.05)
  );

  return {
    code: DISPLAY_CODE.get(code) ?? code.toUpperCase(),
    sourceCode: code,
    title: firstHeaderTitle(code),
    sourceFile: `../csl-orig/v02/${code}/${code}.txt`,
    volumes: volumeCount(code),
    records,
    bytes: Buffer.byteLength(text, "utf8"),
    totalChars,
    meanChars: Math.round(mean(lengths)),
    medianChars: Math.round(median(lengths)),
    maxChars: lengths.reduce((m, n) => Math.max(m, n), 0),
    lsTotal,
    lsPerRecord: Number((lsTotal / Math.max(records, 1)).toFixed(3)),
    inlineItiTotal,
    inlineItiPerRecord: Number((inlineItiTotal / Math.max(records, 1)).toFixed(3)),
    nonzeroTypes: Object.entries(typeCounts).filter(([, count]) => count > 0).length,
    typeCounts,
    typePct,
    blockCounts,
    blockPct,
    blockChars,
    blockCharPct,
    structuredSignals,
    fitScore: score,
    fitBand: fitBand(score, records, blockPct, structuredSignals)
  };
}

function main() {
  if (!fs.existsSync(ROOT)) {
    throw new Error(`Missing source root: ${ROOT}`);
  }

  const codes = fs.readdirSync(ROOT)
    .filter(name => fs.statSync(path.join(ROOT, name)).isDirectory())
    .filter(code => fs.existsSync(path.join(ROOT, code, `${code}.txt`)))
    .sort();

  const dicts = codes.map(analyseDictionary)
    .sort((a, b) => b.fitScore - a.fitScore || b.records - a.records || a.code.localeCompare(b.code));

  const payload = {
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    scheme: "Exploratory CDSL-wide projection of the MWS §3 block vocabulary; not a replacement for per-dictionary philological review.",
    typeLabels: TYPE_LABELS,
    blockLabels: BLOCK_LABELS,
    dictionaryCount: dicts.length,
    totals: {
      records: dicts.reduce((sum, d) => sum + d.records, 0),
      bytes: dicts.reduce((sum, d) => sum + d.bytes, 0),
      chars: dicts.reduce((sum, d) => sum + d.totalChars, 0)
    },
    dicts
  };

  for (const out of OUT) {
    fs.mkdirSync(path.dirname(out), {recursive: true});
    fs.writeFileSync(out, `${JSON.stringify(payload, null, 2)}\n`);
  }

  console.log(`Wrote ${dicts.length} dictionaries to:`);
  for (const out of OUT) console.log(`- ${path.relative(process.cwd(), out)}`);
}

main();
