import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const args = new Map();
for (let i = 2; i < process.argv.length; i += 1) {
  const arg = process.argv[i];
  if (arg.startsWith("--")) {
    const key = arg.slice(2);
    const next = process.argv[i + 1];
    if (next && !next.startsWith("--")) {
      args.set(key, next);
      i += 1;
    } else {
      args.set(key, "true");
    }
  }
}

const maxItems = Number.parseInt(args.get("max") || "50", 10);
const cslOrigArg = args.get("csl-orig") || path.resolve(repoRoot, "..", "csl-orig");
const cslV02 = path.basename(cslOrigArg).toLowerCase() === "v02"
  ? cslOrigArg
  : path.join(cslOrigArg, "v02");

const sources = {
  mw: path.join(cslV02, "mw", "mw.txt"),
  pwg: path.join(cslV02, "pwg", "pwg.txt"),
  pwk: path.join(cslV02, "pw", "pw.txt")
};

const publicSources = Object.fromEntries(
  Object.entries(sources).map(([code, filePath]) => [
    code,
    path.relative(repoRoot, filePath).split(path.sep).join("/")
  ])
);

for (const filePath of Object.values(sources)) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing source file: ${filePath}`);
  }
}

function parseRecords(filePath, dictionaryCode) {
  const lines = fs.readFileSync(filePath, "utf8").split(/\r?\n/);
  const records = [];
  let current = null;

  function finish() {
    if (!current) return;
    const raw = current.lines.join("\n").trim();
    const header = current.lines[0] || "";
    const parsed = parseHeader(header);
    records.push({
      dictionary: dictionaryCode,
      line: current.line,
      raw,
      ...parsed,
      citationCount: countMatches(raw, /<ls\b/g),
      hasHedge: /<ls>L\.<\/ls>/.test(raw),
      hasHom: /<hom>/.test(raw),
      hasInfo: /<info\b/.test(raw),
      hasRootMarker: /<info\b[^>]*verb="genuineroot"/.test(raw),
      hasCrossReference: /(<ab>cf\.<\/ab>|<ab>id\.<\/ab>|q\.v\.|qv\.)/i.test(raw)
    });
  }

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (line.startsWith("<L>")) {
      finish();
      current = { line: i + 1, lines: [line] };
    } else if (current) {
      current.lines.push(line);
    }
  }
  finish();
  return records;
}

function parseHeader(header) {
  const match = header.match(/^<L>([^<]+)<pc>([^<]+)<k1>([^<]+)<k2>([^<\n]+?)(?:<h>([^<]+))?(?:<e>([^<\n]+))?$/);
  if (!match) {
    return { L: null, pc: null, k1: null, k2: null, h: null, e: null };
  }
  return {
    L: match[1] || null,
    pc: match[2] || null,
    k1: match[3] || null,
    k2: match[4] || null,
    h: match[5] || null,
    e: match[6] || null
  };
}

function countMatches(text, regex) {
  return Array.from(text.matchAll(regex)).length;
}

function indexByKey(records) {
  const index = new Map();
  for (const record of records) {
    if (!record.k1) continue;
    if (!index.has(record.k1)) index.set(record.k1, []);
    index.get(record.k1).push(record);
  }
  return index;
}

function chooseCounterpart(records = []) {
  if (records.length === 0) return null;
  return records
    .slice()
    .sort((a, b) => {
      if (b.citationCount !== a.citationCount) return b.citationCount - a.citationCount;
      return b.raw.length - a.raw.length;
    })[0];
}

function isCompound(record) {
  return Boolean(
    record.e?.startsWith("3") ||
    /[—–]/.test(record.k2 || "")
  );
}

function isContinuation(record) {
  return Boolean(record.e?.startsWith("1A"));
}

function phenomenaFor(mw, pwg, pwk) {
  const phenomena = [];
  if (mw.hasHedge) phenomena.push("hedge");
  if (mw.hasRootMarker) phenomena.push("root");
  if (isCompound(mw)) phenomena.push("compound");
  if (isContinuation(mw)) phenomena.push("continuation");
  if (pwg && pwk) phenomena.push("tri-dict");
  if (pwg && pwg.citationCount > mw.citationCount) phenomena.push("pwg-rich");
  if (pwg && pwk && pwk.citationCount < pwg.citationCount) phenomena.push("pwk-abridged");
  if (pwg && mw.citationCount === 0 && pwg.citationCount > 0) phenomena.push("mw-uncited-pwg-cited");
  if (mw.hasHom) phenomena.push("homophone");
  return phenomena;
}

function scoreFor(phenomena) {
  const weights = {
    hedge: 6,
    root: 5,
    compound: 5,
    continuation: 4,
    "tri-dict": 3,
    "pwg-rich": 2,
    "pwk-abridged": 2,
    "mw-uncited-pwg-cited": 2,
    homophone: 1
  };
  return phenomena.reduce((sum, item) => sum + (weights[item] || 0), 0);
}

function summarize(record) {
  if (!record) return null;
  return {
    L: record.L,
    pc: record.pc,
    k1: record.k1,
    k2: record.k2,
    h: record.h,
    e: record.e,
    line: record.line,
    citationCount: record.citationCount,
    hasHedge: record.hasHedge,
    hasRootMarker: record.hasRootMarker,
    isCompound: isCompound(record),
    isContinuation: isContinuation(record),
    raw: compactRaw(record.raw)
  };
}

function compactRaw(raw) {
  const normalized = raw.replace(/\s+/g, " ").trim();
  if (normalized.length <= 1600) return normalized;
  return `${normalized.slice(0, 1560)} ... [truncated]`;
}

function preliminaryLossHints(phenomena) {
  const hints = [];
  if (phenomena.includes("hedge")) {
    hints.push("MW L. is not an ordinary textual citation; OntoLex needs an evidence/provenance class.");
  }
  if (phenomena.includes("root")) {
    hints.push("Root entries act as lexical entries, derivational bases, and grammatical infrastructure.");
  }
  if (phenomena.includes("compound")) {
    hints.push("Compounds need both TEI subentry preservation and OntoLex decomposition.");
  }
  if (phenomena.includes("continuation")) {
    hints.push("Continuation entries require parent recovery from adjacency before semantic modeling.");
  }
  if (phenomena.includes("pwg-rich") || phenomena.includes("pwk-abridged")) {
    hints.push("PWG/PWK citation differences may encode historical compression, not mere omission.");
  }
  return hints;
}

const mwRecords = parseRecords(sources.mw, "mw");
const pwgRecords = parseRecords(sources.pwg, "pwg");
const pwkRecords = parseRecords(sources.pwk, "pwk");

const pwgIndex = indexByKey(pwgRecords);
const pwkIndex = indexByKey(pwkRecords);

const candidates = [];
for (const mw of mwRecords) {
  if (!mw.k1) continue;
  const pwg = chooseCounterpart(pwgIndex.get(mw.k1));
  const pwk = chooseCounterpart(pwkIndex.get(mw.k1));
  const phenomena = phenomenaFor(mw, pwg, pwk);
  const isHard = phenomena.some((item) => ["hedge", "root", "compound", "continuation"].includes(item));
  if (!isHard) continue;
  candidates.push({
    key: mw.k1,
    score: scoreFor(phenomena),
    phenomena,
    mw,
    pwg,
    pwk
  });
}

candidates.sort((a, b) => {
  if (b.score !== a.score) return b.score - a.score;
  return a.key.localeCompare(b.key);
});

const selected = [];
const seen = new Set();
const quotas = [
  ["root", Math.ceil(maxItems * 0.24)],
  ["compound", Math.ceil(maxItems * 0.30)],
  ["continuation", Math.ceil(maxItems * 0.16)],
  ["hedge", Math.ceil(maxItems * 0.30)]
];

function addCandidate(candidate) {
  const id = `${candidate.mw.L}:${candidate.key}`;
  if (seen.has(id) || selected.length >= maxItems) return false;
  seen.add(id);
  selected.push(candidate);
  return true;
}

for (const [phenomenon, limit] of quotas) {
  let count = 0;
  const preferred = candidates.filter((candidate) => isPreferredForQuota(candidate, phenomenon));
  const fallback = candidates.filter((candidate) => candidate.phenomena.includes(phenomenon));
  for (const candidate of [...preferred, ...fallback]) {
    if (count >= limit || selected.length >= maxItems) break;
    if (addCandidate(candidate)) {
      count += 1;
    }
  }
}

for (const candidate of candidates) {
  if (selected.length >= maxItems) break;
  addCandidate(candidate);
}

const selectedKeyCounts = selected.reduce((counts, candidate) => {
  counts.set(candidate.key, (counts.get(candidate.key) || 0) + 1);
  return counts;
}, new Map());

const selectedArtifactStemCounts = selected.reduce((counts, candidate) => {
  const stem = `mw-pwg-pwk-${candidate.key}`.toLowerCase();
  counts.set(stem, (counts.get(stem) || 0) + 1);
  return counts;
}, new Map());

function caseIdFor(candidate) {
  const stem = `mw-pwg-pwk-${candidate.key}`.toLowerCase();
  const needsDisambiguator = selectedKeyCounts.get(candidate.key) > 1
    || selectedArtifactStemCounts.get(stem) > 1;
  const suffix = needsDisambiguator
    ? `-mw${candidate.mw.L}`
    : "";
  return `mw-pwg-pwk:${candidate.key}${suffix}`;
}

const output = {
  generatedAt: new Date().toISOString(),
  generator: "scripts/sample-hard-cases.mjs",
  maxItems,
  sources: publicSources,
  recordCounts: {
    mw: mwRecords.length,
    pwg: pwgRecords.length,
    pwk: pwkRecords.length
  },
  method: {
    description: "MW-led hard-case sample for TEI/OntoLex interoperability stress testing.",
    signatures: ["hedge", "root", "compound", "continuation", "pwg-rich", "pwk-abridged", "tri-dict"]
  },
  items: selected.map((candidate, index) => ({
    id: caseIdFor(candidate),
    rank: index + 1,
    key: candidate.key,
    score: candidate.score,
    phenomena: candidate.phenomena,
    lossHints: preliminaryLossHints(candidate.phenomena),
    records: {
      mw: summarize(candidate.mw),
      pwg: summarize(candidate.pwg),
      pwk: summarize(candidate.pwk)
    }
  }))
};

const outputPaths = [
  path.join(repoRoot, "data", "pilot", "hard-cases.json"),
  path.join(repoRoot, "src", "data", "pilot", "hard-cases.json")
];

for (const outputPath of outputPaths) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
}

console.log(`Wrote ${output.items.length} hard cases to ${outputPaths.join(", ")}`);
console.log(`Parsed MW=${mwRecords.length}, PWG=${pwgRecords.length}, PWK=${pwkRecords.length}`);

function isPreferredForQuota(candidate, phenomenon) {
  if (!candidate.phenomena.includes(phenomenon)) return false;
  if (phenomenon === "hedge") {
    return !candidate.phenomena.some((item) => ["root", "compound", "continuation"].includes(item));
  }
  if (phenomenon === "compound" || phenomenon === "continuation") {
    return !candidate.phenomena.includes("hedge");
  }
  return true;
}
