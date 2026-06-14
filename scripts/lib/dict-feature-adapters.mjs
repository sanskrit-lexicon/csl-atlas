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
    "MW, AP, PWG, PWK, WIL, CAE, MD, BHS, and PWKVN use validated <lex> adapters; VCP and SKD use dictionary-specific prose markers near the headword separator.",
    "ABCH, ACPH, and ACSJ use validated kosha synonym suffixes parsed by the headword layer.",
    "Unavailable dictionaries are excluded from gender conflict counts, never counted as zero evidence."
  ],
  citations: [
    "Supported citation adapters use tagged <ls> source citations and feed the source matrix/overlap.",
    "BEN, GRA, PWKVN, LAN, LRV, AP90, SCH, and BHS have validated <ls> adapters in addition to the Core 4.",
    "Prose/source-hint adapters such as VCP/SKD/KRM iti proxies are tracked separately and stay out of source overlap.",
    "Unavailable dictionaries are excluded from source overlap, never counted as zero evidence."
  ],
  homonyms: [
    "Supported homonym adapters use dictionary-specific <h> indices after validating that <h> encodes homonym splitting.",
    "BOP, GST, MW72, GRA, PWKVN, LAN, CCS, LRV, CAE, MD, INM, VEI, STC, PUI, BHS, PE, and MCI are promoted from the broad audit queue.",
    "AP and AP90 have only sparse <h> traces and remain unavailable until a dictionary-specific adapter can prove missing <h> is safe to interpret.",
    "Unavailable dictionaries are excluded from homonym split counts, never counted as one or zero evidence."
  ],
  senses: [
    "Supported sense adapters count structural sense-division markers; the count is a proxy, not a curated sense inventory.",
    "AP uses bullet divisions; MW, PWG/PWK, BEN, GST, LAN, INM, VEI, PE, IEG, SNP, MCI, and PGN use validated dictionary-specific numbered/section markers.",
    "Candidate <div> markers that encode prefix blocks, source examples, parallel language translations, or citation paragraphs stay unavailable until a separate metric is defined.",
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

function koshaSuffixGender(_body, record = {}) {
  const hint = String(record?.genderHint ?? "");
  if (!hint) return null;
  if (hint === "adj") return "adj";
  const genders = [...hint].filter(value => value === "m" || value === "f" || value === "n");
  return genders.length ? genders : null;
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

function markerSenseUnits(marker) {
  return body => {
    marker.lastIndex = 0;
    const n = (body || "").match(marker)?.length ?? 0;
    return Math.max(1, n);
  };
}

function leadingTextPlusMarkedUnits(marker) {
  return body => {
    marker.lastIndex = 0;
    const n = (body || "").match(marker)?.length ?? 0;
    return n ? n + 1 : 1;
  };
}

const NUMBERED_BRACE_SENSE_MARKER = /\{@\d+\.@\}/g;
const GST_SECTION_MARKER = /<div n="P"\/?>/g;
const LAN_NUMBERED_SENSE_MARKER = /<div n="2"\/?>/g;
const MW_SENSE_SECTION_MARKER = /<div n="(?:to|P|1)"\/?>/g;
const ENCYCLOPEDIC_PARAGRAPH_MARKER = /<div n="P"\/?>/g;
const NAMED_INDEX_SECTION_MARKER = /<div n="(?:P|HI)"\/?>/g;
const NUMBERED_INDEX_SECTION_MARKER = /<div n="NI"\/?>/g;

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
    pwkvn: supportedAdapter("pwkvn-lex-gender-pos", "PWKVN <lex> gender/POS", {
      extract: standardLexGender,
      notes: ["PWKVN Adj./Adv. tags are normalized to adjective/indeclinable evidence."]
    }),
    abch: supportedAdapter("kosha-synonym-gender-suffix", "Kosha synonym gender suffix", {
      extract: koshaSuffixGender,
      notes: ["Uses the parsed -puM/-strI/-klI/-a suffix on <syns> synonym headwords."]
    }),
    acph: supportedAdapter("kosha-synonym-gender-suffix", "Kosha synonym gender suffix", {
      extract: koshaSuffixGender,
      notes: ["Uses the parsed -puM/-strI/-klI/-a suffix on <syns> synonym headwords."]
    }),
    acsj: supportedAdapter("kosha-synonym-gender-suffix", "Kosha synonym gender suffix", {
      extract: koshaSuffixGender,
      notes: ["Uses the parsed -puM/-strI/-klI/-a suffix on <syns> synonym headwords."]
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
    ben: supportedAdapter("ls-source-citation", "<ls> source citation"),
    gra: supportedAdapter("ls-source-citation", "<ls> source citation"),
    pwkvn: supportedAdapter("ls-source-citation", "<ls> source citation", {
      notes: ["Local-only dictionary; source evidence uses line pointers without GitHub hrefs."]
    }),
    lan: supportedAdapter("ls-source-citation", "<ls> source citation", {
      notes: ["Lanman's reader references are encoded as <ls> labels and compared as source labels."]
    }),
    lrv: supportedAdapter("ls-source-citation", "<ls> source citation"),
    ap90: supportedAdapter("ls-source-citation", "<ls> source citation"),
    sch: supportedAdapter("ls-source-citation", "<ls> source citation"),
    bhs: supportedAdapter("ls-source-citation", "<ls> source citation"),
    wil: partialAdapter("weak", "iti-prose-proxy", "iti prose proxy"),
    vcp: partialAdapter("partial", "iti-prose-proxy", "iti prose proxy"),
    skd: partialAdapter("partial", "iti-prose-proxy", "iti prose proxy"),
    krm: partialAdapter("partial", "krm-iti-authority-proxy", "KRM iti authority/source-hint proxy", {
      notes: ["Counts standalone iti authority/source-hint markers for diagnostic density only; KRM is not included in <ls> source overlap."]
    })
  },
  homonyms: {
    bop: supportedAdapter("h-homonym-index", "<h> homonym index"),
    gst: supportedAdapter("h-homonym-index", "<h> homonym index", {
      notes: ["GST has a small but systematic <h> set; only marked homonym groups contribute split evidence."]
    }),
    mw: supportedAdapter("h-homonym-index", "<h> homonym index"),
    mw72: supportedAdapter("h-homonym-index", "<h> homonym index"),
    gra: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pwg: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pw: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pwkvn: supportedAdapter("h-homonym-index", "<h> homonym index", {
      notes: ["Local-only dictionary; examples use line pointers without GitHub hrefs."]
    }),
    lan: supportedAdapter("h-homonym-index", "<h> homonym index"),
    ccs: supportedAdapter("h-homonym-index", "<h> homonym index"),
    lrv: supportedAdapter("h-homonym-index", "<h> homonym index"),
    cae: supportedAdapter("h-homonym-index", "<h> homonym index"),
    md: supportedAdapter("h-homonym-index", "<h> homonym index"),
    inm: supportedAdapter("h-homonym-index", "<h> homonym index", {
      notes: ["Validated as distinct named-entity/referent homonym grouping."]
    }),
    vei: supportedAdapter("h-homonym-index", "<h> homonym index"),
    stc: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pui: supportedAdapter("h-homonym-index", "<h> homonym index", {
      notes: ["Uses Roman <h> labels for distinct puranic-person records."]
    }),
    bhs: supportedAdapter("h-homonym-index", "<h> homonym index"),
    pe: supportedAdapter("h-homonym-index", "<h> homonym index", {
      notes: ["Local-only dictionary with Roman <h> labels; examples use line pointers without GitHub hrefs."]
    }),
    mci: supportedAdapter("h-homonym-index", "<h> homonym index")
  },
  senses: {
    mw: supportedAdapter("mw-sense-section-div", "MW sense/section <div>", {
      extract: leadingTextPlusMarkedUnits(MW_SENSE_SECTION_MARKER),
      notes: ["Counts MW <div n=\"to\"> gloss dividers plus major <div n=\"P\">/<div n=\"1\"> sense sections; verb-prefix/table markers stay outside this adapter."]
    }),
    ap: supportedAdapter("ap-bullet-sense-marker", "AP bullet sense marker", { marker: SENSE_MARKER.ap }),
    pwg: supportedAdapter("pwg-div-sense-marker", "PWG <div> sense marker", { marker: SENSE_MARKER.pwg }),
    pw: supportedAdapter("pwk-div-sense-marker", "PWK <div> sense marker", { marker: SENSE_MARKER.pw }),
    gst: supportedAdapter("gst-roman-section-div", "GST Roman section <div>", {
      extract: leadingTextPlusMarkedUnits(GST_SECTION_MARKER),
      notes: ["GST marks sections II+ with <div n=\"P\"> after an unmarked leading Roman section."]
    }),
    ben: supportedAdapter("ben-numbered-brace-sense", "BEN numbered brace sense", {
      extract: markerSenseUnits(NUMBERED_BRACE_SENSE_MARKER)
    }),
    lan: supportedAdapter("lan-numbered-div-sense", "LAN numbered sense <div>", {
      extract: markerSenseUnits(LAN_NUMBERED_SENSE_MARKER),
      notes: ["Counts <div n=\"2\"/> numbered definition divisions; prefix paragraphs stay outside this adapter."]
    }),
    inm: supportedAdapter("inm-article-section-div", "INM article section <div>", {
      extract: markerSenseUnits(NAMED_INDEX_SECTION_MARKER),
      notes: ["Validated as article-section depth for index entries, not a curated semantic sense inventory."]
    }),
    vei: supportedAdapter("vei-article-section-div", "VEI article section <div>", {
      extract: markerSenseUnits(ENCYCLOPEDIC_PARAGRAPH_MARKER),
      notes: ["Validated as encyclopedic article-section depth for Vedic Index entries."]
    }),
    pe: supportedAdapter("pe-numbered-section-div", "PE numbered section <div>", {
      extract: markerSenseUnits(NUMBERED_INDEX_SECTION_MARKER),
      notes: ["Local-only dictionary; examples use line pointers without GitHub hrefs."]
    }),
    ieg: supportedAdapter("ieg-article-section-div", "IEG article section <div>", {
      extract: markerSenseUnits(ENCYCLOPEDIC_PARAGRAPH_MARKER),
      notes: ["Local-only dictionary; examples use line pointers without GitHub hrefs."]
    }),
    snp: supportedAdapter("snp-botanical-section-div", "SNP botanical section <div>", {
      extract: markerSenseUnits(ENCYCLOPEDIC_PARAGRAPH_MARKER),
      notes: ["Local-only dictionary; counts numbered botanical equivalence sections."]
    }),
    mci: supportedAdapter("mci-article-section-div", "MCI article section <div>", {
      extract: markerSenseUnits(ENCYCLOPEDIC_PARAGRAPH_MARKER),
      notes: ["Validated as article-section depth for Mahābhārata cultural index entries."]
    }),
    pgn: supportedAdapter("pgn-article-section-div", "PGN article section <div>", {
      extract: markerSenseUnits(NAMED_INDEX_SECTION_MARKER),
      notes: ["Local-only dictionary; counts article paragraph/heading section markers in the Gupta names index."]
    })
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
    languagePair: dict.languagePair ?? "",
    family: dict.family ?? "",
    deprecated: Boolean(dict.deprecated),
    sourceExists: dict.sourceExists ?? true,
    sourceLinkMode: dict.sourceLinkMode ?? "github",
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
    languagePair: dict.languagePair ?? "",
    family: dict.family ?? "",
    deprecated: Boolean(dict.deprecated),
    sourceExists: dict.sourceExists ?? true,
    sourceLinkMode: dict.sourceLinkMode ?? "github",
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

function grammarValues(value) {
  if (Array.isArray(value)) return value.filter(Boolean);
  return value ? [value] : [];
}

export function extractGrammar(code, body, record = {}) {
  const adapter = adapterFor("grammar", code);
  if (adapter?.status !== "supported" || typeof adapter.extract !== "function") return null;
  const values = grammarValues(adapter.extract(body || "", record));
  if (!values.length) return null;
  return values.length === 1
    ? { value: values[0], methodId: adapter.methodId, status: adapter.status }
    : { value: values[0], values, methodId: adapter.methodId, status: adapter.status };
}

export function citationAdapterForDict(code) {
  return adapterFor("citations", code);
}

export function homonymFeatureCodes(options = {}) {
  return supportedFeatureCodes("homonyms", options);
}

export function senseUnitsForDict(code, body) {
  const adapter = adapterFor("senses", code);
  if (adapter?.status !== "supported") return null;
  if (typeof adapter.extract === "function") return adapter.extract(body || "");
  if (!adapter.marker) return null;
  return markerSenseUnits(adapter.marker)(body || "");
}

export function senseMethodForDict(code) {
  return adapterFor("senses", code);
}
