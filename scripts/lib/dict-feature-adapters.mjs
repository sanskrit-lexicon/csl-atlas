import { DICT_LABELS, SENSE_MARKER } from "./dict-manifest.mjs";
import { genderFromLex, genderFromProse } from "./dict-parser.mjs";
import { buildBroadHeadwordDictionaries, coreComparisonDictionaries } from "./dict-scope.mjs";

export const FEATURE_ORDER = ["grammar", "citations", "homonyms", "senses"];

const FEATURE_LABELS = {
  grammar: "Grammar/POS",
  citations: "Citations",
  homonyms: "Homonyms",
  senses: "Senses"
};

const FEATURE_UNAVAILABLE_REASONS = {
  grammar: "No validated grammar/POS adapter for this dictionary yet.",
  citations: "No validated source-citation adapter for public citation overlap yet.",
  homonyms: "No validated homonym-index adapter for this dictionary yet.",
  senses: "No validated structural sense-marker adapter for this dictionary yet."
};

const FEATURE_METHOD_NOTES = {
  grammar: [
    "Supported grammar/POS adapters emit coarse m/f/n/adj/ind evidence only.",
    "MW, AP, PWG, PWK, and WIL use <lex>; VCP and SKD use dictionary-specific prose markers near the headword separator.",
    "Unavailable dictionaries are excluded from gender conflict counts, never counted as zero evidence."
  ],
  citations: [
    "Supported citation adapters use tagged <ls> source citations and feed the source matrix/overlap.",
    "Prose/source-hint adapters such as iti proxies are tracked separately until validated for source-level comparison.",
    "Unavailable dictionaries are excluded from source overlap, never counted as zero evidence."
  ],
  homonyms: [
    "Supported homonym adapters use dictionary-specific <h> indices after validating that <h> encodes homonym splitting.",
    "Unavailable dictionaries are excluded from homonym split counts, never counted as one or zero evidence."
  ],
  senses: [
    "Supported sense adapters count structural sense-division markers; the count is a proxy, not a curated sense inventory.",
    "AP uses bullet divisions; PWG/PWK use <div>. Prose-segmented dictionaries stay unavailable until separately validated.",
    "Unavailable dictionaries are excluded from depth/divergence counts, never counted as single-sense or zero evidence."
  ]
};

function lexGender(body) {
  return genderFromLex(body);
}

function lexValues(body) {
  return [...String(body ?? "").matchAll(/<lex>([^<]{1,32})<\/lex>/g)].map(match => match[1].trim());
}

function normalizeLexValue(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[.]+$/u, "")
    .replace(/[¹²³0-9]+$/u, "")
    .replace(/[.]+$/u, "");
}

function firstMappedLexGender(body, valueMap) {
  for (const value of lexValues(body)) {
    const mapped = valueMap[normalizeLexValue(value)];
    if (mapped) return mapped;
  }
  return null;
}

const STANDARD_LEX_VALUES = {
  m: "m",
  f: "f",
  n: "n",
  a: "adj",
  adj: "adj",
  ind: "ind",
  adv: "ind",
  pron: "ind"
};

const MD_LEX_VALUES = {
  ...STANDARD_LEX_VALUES,
  ad: "ind",
  prn: "ind"
};

const BHS_LEX_VALUES = {
  ...STANDARD_LEX_VALUES,
  nt: "n",
  fem: "f",
  indecl: "ind",
  ppp: "adj"
};

function standardLexGender(body) {
  return firstMappedLexGender(body, STANDARD_LEX_VALUES);
}

function mdLexGender(body) {
  return firstMappedLexGender(body, MD_LEX_VALUES);
}

function bhsLexGender(body) {
  return firstMappedLexGender(body, BHS_LEX_VALUES);
}

function vcpGender(body) {
  return genderFromProse(body, "vcp");
}

function skdGender(body) {
  return genderFromProse(body, "skd");
}

function supportedAdapter(methodId, methodLabel, extra = {}) {
  return {
    status: "supported",
    confidence: "validated",
    methodId,
    methodLabel,
    fixtureCoverage: "unit",
    ...extra
  };
}

function partialAdapter(status, methodId, methodLabel, extra = {}) {
  return {
    status,
    confidence: status === "partial" ? "diagnostic" : "weak",
    methodId,
    methodLabel,
    fixtureCoverage: "audit",
    ...extra
  };
}

export const FEATURE_ADAPTERS = {
  grammar: {
    mw: supportedAdapter("lex-gender-pos", "<lex> gender/POS", { extract: lexGender }),
    ap: supportedAdapter("lex-gender-pos", "<lex> gender/POS", { extract: lexGender }),
    pwg: supportedAdapter("lex-gender-pos", "<lex> gender/POS", { extract: lexGender }),
    pw: supportedAdapter("lex-gender-pos", "<lex> gender/POS", { extract: lexGender }),
    wil: supportedAdapter("lex-gender-pos", "<lex> gender/POS", { extract: lexGender }),
    cae: supportedAdapter("cae-lex-gender-pos", "CAE <lex> gender/POS", { extract: standardLexGender }),
    md: supportedAdapter("md-lex-gender-pos", "MD <lex> gender/POS", {
      extract: mdLexGender,
      notes: ["MD verb voice tags such as P. and Ā. are ignored; adverb/pronoun tags are normalized to indeclinable."]
    }),
    bhs: supportedAdapter("bhs-lex-gender-pos", "BHS <lex> gender/POS", {
      extract: bhsLexGender,
      notes: ["BHS nt./fem./indecl. are normalized; ppp. is treated as adjectival evidence."]
    }),
    vcp: supportedAdapter("vcp-prose-gender-pos", "VCP prose gender/POS marker", {
      confidence: "validated-with-limitations",
      extract: vcpGender,
      notes: ["VCP anchor markers reliably capture m/adj/ind, but under-mark some feminine/neuter entries."]
    }),
    skd: supportedAdapter("skd-prose-gender-pos", "SKD prose gender/POS marker", {
      confidence: "validated-with-limitations",
      extract: skdGender
    })
  },
  citations: {
    mw: supportedAdapter("ls-source-citation", "<ls> source citation"),
    ap: supportedAdapter("ls-source-citation", "<ls> source citation"),
    pwg: supportedAdapter("ls-source-citation", "<ls> source citation"),
    pw: supportedAdapter("ls-source-citation", "<ls> source citation"),
    wil: partialAdapter("weak", "iti-prose-proxy", "iti prose proxy"),
    vcp: partialAdapter("partial", "iti-prose-proxy", "iti prose proxy"),
    skd: partialAdapter("partial", "iti-prose-proxy", "iti prose proxy")
  },
  homonyms: {
    mw: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pwg: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pw: supportedAdapter("h-homonym-index", "<h> homonym index")
  },
  senses: {
    ap: supportedAdapter("ap-bullet-sense-marker", "AP bullet sense marker", { marker: SENSE_MARKER.ap }),
    pwg: supportedAdapter("pwg-div-sense-marker", "PWG <div> sense marker", { marker: SENSE_MARKER.pwg }),
    pw: supportedAdapter("pwk-div-sense-marker", "PWK <div> sense marker", { marker: SENSE_MARKER.pw })
  }
};

function dictionariesForScope(scope) {
  if (Array.isArray(scope)) return scope;
  return scope === "coreComparison" ? coreComparisonDictionaries() : buildBroadHeadwordDictionaries();
}

function labelFor(code) {
  return DICT_LABELS[code] ?? (code === "pw" ? "PWK" : code.toUpperCase());
}

function adapterFor(feature, code) {
  return FEATURE_ADAPTERS[feature]?.[code] ?? null;
}

function adapterMetadata(dict, adapter) {
  return {
    code: dict.code,
    label: dict.label ?? labelFor(dict.code),
    fullName: dict.fullName ?? dict.label ?? labelFor(dict.code),
    methodId: adapter.methodId,
    methodLabel: adapter.methodLabel,
    status: adapter.status,
    confidence: adapter.confidence,
    fixtureCoverage: adapter.fixtureCoverage,
    notes: adapter.notes ?? []
  };
}

function unavailableMetadata(dict, feature, adapter) {
  return {
    code: dict.code,
    label: dict.label ?? labelFor(dict.code),
    fullName: dict.fullName ?? dict.label ?? labelFor(dict.code),
    methodId: adapter?.methodId ?? null,
    methodLabel: adapter?.methodLabel ?? null,
    status: adapter?.status ?? "missing",
    reason: adapter
      ? `${adapter.status} adapter evidence is diagnostic only; not included in public deep metrics.`
      : FEATURE_UNAVAILABLE_REASONS[feature]
  };
}

export function featureAdapter(feature, code) {
  return adapterFor(feature, code);
}

export function supportedFeatureCodes(feature, { scope = "coreComparison" } = {}) {
  return dictionariesForScope(scope)
    .filter(dict => adapterFor(feature, dict.code)?.status === "supported")
    .map(dict => dict.code);
}

export function featureSupport(feature, { scope = "broadHeadword" } = {}) {
  const dictionaries = dictionariesForScope(scope);
  const includedDictionaries = [];
  const unavailableDictionaries = [];
  const diagnosticDictionaries = [];

  for (const dict of dictionaries) {
    const adapter = adapterFor(feature, dict.code);
    if (adapter?.status === "supported") {
      includedDictionaries.push(adapterMetadata(dict, adapter));
    } else {
      const unavailable = unavailableMetadata(dict, feature, adapter);
      unavailableDictionaries.push(unavailable);
      if (adapter) diagnosticDictionaries.push(unavailable);
    }
  }

  return {
    feature,
    featureLabel: FEATURE_LABELS[feature],
    adapterScope: scope,
    includedDictionaries,
    unavailableDictionaries,
    diagnosticDictionaries,
    methodNotes: FEATURE_METHOD_NOTES[feature] ?? []
  };
}

export function extractGrammar(code, body) {
  const adapter = adapterFor("grammar", code);
  if (adapter?.status !== "supported" || typeof adapter.extract !== "function") return null;
  const value = adapter.extract(body || "");
  return value ? { value, methodId: adapter.methodId, status: adapter.status } : null;
}

export function citationAdapterForDict(code) {
  return adapterFor("citations", code);
}

export function homonymFeatureCodes(options = {}) {
  return supportedFeatureCodes("homonyms", options);
}

export function senseUnitsForDict(code, body) {
  const adapter = adapterFor("senses", code);
  if (adapter?.status !== "supported" || !adapter.marker) return null;
  adapter.marker.lastIndex = 0;
  const n = (body || "").match(adapter.marker)?.length ?? 0;
  return Math.max(1, n);
}

export function senseMethodForDict(code) {
  return adapterFor("senses", code);
}
