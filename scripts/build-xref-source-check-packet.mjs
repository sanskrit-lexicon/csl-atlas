// Build a compact source-check packet for the xref hub review package.
//
// This generator reads only atlas xref artifacts plus dictionary source files
// for pointers. It records no human decisions and does not change parser,
// public-page, corpus, DCS, backend/runtime, or standards behavior.
//
// Usage: npm run build-xref-source-check-packet

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseCsv } from "./build-xref-hub-review.mjs";
import { dictExists, iterateDict } from "./lib/dict-parser.mjs";
import { cologneLinksFor, entryUrl } from "./lib/cologne-links.mjs";
import { generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-xref-source-check-packet";
const HUB_REVIEW_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_hub_review.json");
const XREF_EDGES_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_edges.csv");
const SHARED_EDGES_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_shared_edges.csv");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "xref_source_check_packet.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "MICROSTRUCTURE_XREF_SOURCE_CHECK.md");
const SHARED_CORE_LIMIT = 40;

// The candidate pool the 40 are sliced from. Computed, never typed: the figure was
// hardcoded as "642" and was wrong by one — a `wc -l` that counted the CSV header as a
// data row. It had propagated into the packet, both prose companions, FINDINGS and
// several PR bodies before a docs-vs-data test caught it (H1648).
function sharedEdgePoolSize() {
  const csv = fs.readFileSync(SHARED_EDGES_PATH, "utf8");
  return csv.trim().split(/\r?\n/).length - 1; // minus the header row
}
const PREFIX_CONTROL_TARGETS_PER_DICT = 5;
const PREFIX_CONTROL_EXAMPLES_PER_TARGET = 3;

export const EXPECTED_SHARED_CORE_SAMPLE_IDS = Object.freeze(
  Array.from({ length: SHARED_CORE_LIMIT }, (_, index) => `mw-pwg-shared:${String(index + 1).padStart(2, "0")}`)
);

export const EXPECTED_PREFIX_CONTROL_IDS = Object.freeze([
  "xref-prefix-control:pwg:01",
  "xref-prefix-control:pwg:02",
  "xref-prefix-control:pwg:03",
  "xref-prefix-control:pwg:04",
  "xref-prefix-control:pwg:05",
  "xref-prefix-control:mw:01",
  "xref-prefix-control:mw:02",
  "xref-prefix-control:mw:03",
  "xref-prefix-control:mw:04",
  "xref-prefix-control:mw:05"
]);

// The closed label vocabulary. Each entry carries the decision rule a reviewer needs:
// what the label asserts, what it explicitly does NOT assert, and two worked examples
// drawn from this packet — in English for the repo record and in Russian (`*Ru`) for
// the review sheet, which is the reviewer's instruction surface (H1648).
//
// H1646 wrote the shared-core justification as "both dictionaries, INDEPENDENTLY,
// print a cross-reference ... two editorial traditions made the same link". MG rejected
// that on 26-07-2026 — **MW depends on PWG and PW** — and the data agrees: on the 2,750
// headwords cross-referenced in both dictionaries, MW's target is also a PWG target
// 21.8% of the time against 0.007% expected by chance (~2950x enrichment, p < 0.005;
// scripts/lexico/m9_xref_marker_agreement.py → data/lexico/xref_marker_agreement.json).
// The independence claim is therefore gone. What survives is MG's other judgement:
// a shared edge can still be real and lexical, and THAT is what the label asserts.
//
// `appliesToSheet: false` marks labels the hub classifier uses upstream but that are
// NOT offered as answers on the 40-edge shared-core sheet.
export const XREF_LABEL_VOCABULARY = Object.freeze([
  {
    label: "lexical-shared-core",
    appliesToSheet: true,
    meaning: "The same source lemma points to the same meaningful Sanskrit target in MW and PWG.",
    meaningRu: "Один и тот же заголовок в MW и в PWG отсылает к одной и той же осмысленной санскритской цели.",
    asserts:
      "The cross-reference is real and lexical: the target is an actual lemma, not a piece of "
      + "markup convention, and the link between the two words is a linguistic one.",
    assertsRu:
      "Перекрёстная ссылка реальна и лексична: цель — настоящая лемма, а не элемент разметки, "
      + "и связь между двумя словами языковая, а не техническая.",
    doesNotAssert:
      "NOT two independent witnesses. MW (1899) rests on PW/PWG, and the edge data shows it: "
      + "where both dictionaries cross-reference the same headword they agree on the target 21.8% "
      + "of the time versus 0.007% expected by chance (~2950x enrichment, p < 0.005). A shared "
      + "reference does not double the evidence — MW may simply be carrying PWG's reference over. "
      + "Also NOT a synonymy claim, and NOT a claim about what kind of relation it is (variant, "
      + "derivative, cognate root, homophone) or in which direction it runs.",
    doesNotAssertRu:
      "НЕ утверждает, что перед нами два независимых свидетельства. MW (1899) опирается на PW/PWG, "
      + "и данные это подтверждают: там, где оба словаря дают перекрёстную ссылку от одного и того же "
      + "заголовка, цель совпадает в 21,8% случаев против 0,007%, ожидаемых случайно (обогащение "
      + "примерно в 2950 раз, p < 0,005). Общая ссылка не удваивает свидетельство — MW мог просто "
      + "перенести ссылку из PWG. Также НЕ утверждает синонимии и НЕ утверждает, какого рода это "
      + "отношение (вариант написания, дериват, однокоренное слово, омоним) и в какую сторону оно идёт. "
      + "Вритти, суффикс -ka и диалектный вариант подходят одинаково: вопрос только в том, реально ли "
      + "ребро и лексично ли оно.",
    examples: [
      {
        sampleId: "mw-pwg-shared:09",
        edge: "Awi -> Aqi (āṭi -> āḍi)",
        why:
          "MW prints '(cf. Aqi and Ati)' and PWG prints 'Vgl. Aqi und Ati' for the same bird name "
          + "(Turdus Ginginianus). A real by-form link — though not, on this evidence alone, two "
          + "independent records of it.",
        whyRu:
          "MW печатает «(cf. Aqi and Ati)», PWG — «Vgl. Aqi und Ati» для одного и того же названия "
          + "птицы (Turdus Ginginianus). Настоящая связь вариантов — но, по одному этому свидетельству, "
          + "не два независимых её фиксирования."
      },
      {
        sampleId: "mw-pwg-shared:14",
        edge: "BI -> Byas (bhī -> bhyas)",
        why:
          "A derivational/etymological relation between the root bhī 'fear' and bhyas. Not synonyms, "
          + "and that is fine — the edge is still lexical rather than an artifact.",
        whyRu:
          "Словообразовательная/этимологическая связь между корнем bhī «бояться» и bhyas. Не синонимы — "
          + "и это нормально: ребро всё равно лексическое, а не артефакт."
      }
    ]
  },
  {
    label: "prefix-convention",
    appliesToSheet: true,
    meaning: "The target is primarily a prefix or compound-reference convention, not rare lexical inheritance.",
    meaningRu: "Цель — это приставка или условное сокращение сложного слова, а не редкое лексическое наследование.",
    asserts:
      "The cross-reference target is not a headword at all but a piece of the dictionary's own "
      + "abbreviation machinery — a truncated compound member, or a prefix cited as a form.",
    assertsRu:
      "Цель ссылки вообще не заголовок, а часть словарного аппарата сокращений: усечённый член "
      + "сложного слова или приставка, приведённая как форма.",
    doesNotAssert:
      "NOT that the entry is wrong or the reference useless — only that it is house style for "
      + "compressing compounds, so it carries no evidence about lexical descent.",
    doesNotAssertRu:
      "НЕ утверждает, что статья ошибочна или ссылка бесполезна, — только что это издательская "
      + "условность для сокращения сложных слов, и потому она ничего не говорит о лексическом родстве.",
    examples: [
      {
        sampleId: "xref-prefix-control:pwg:01",
        edge: "target 'a˚' (320 references in PWG)",
        why:
          "'˚' is CDSL's truncation ring: 'a˚' abbreviates 'the compound beginning in a-', not a lemma. "
          + "Auto-resolved by this packet on the marker alone.",
        whyRu:
          "«˚» — знак усечения в CDSL: «a˚» сокращает «сложное слово, начинающееся на a-», а не лемму. "
          + "Пакет разрешает такие строки автоматически, по одному этому знаку."
      },
      {
        sampleId: "xref-prefix-control:mw:05",
        edge: "target 'aBi-' (11 references in MW)",
        why:
          "The trailing hyphen marks a prefix cited as a compound-forming element — same house-style "
          + "class as the ring, different mark.",
        whyRu:
          "Конечный дефис отмечает приставку, приведённую как элемент сложного слова, — тот же класс "
          + "издательской условности, что и кружок, только другой знак."
      }
    ]
  },
  {
    label: "normalization-risk",
    appliesToSheet: true,
    meaning: "A target string where normalization may create or hide an edge.",
    meaningRu: "Строка-цель, на которой нормализация может создать или, наоборот, скрыть ребро.",
    asserts:
      "The edge may be an artifact of string folding rather than a fact about the language. Two "
      + "mechanisms, in opposite directions. (a) CREATED: m6_xref_lineage.py strips MW's '-'/accent "
      + "marks and PWG's '°' ring before intersecting, so headwords the dictionaries spelt "
      + "differently can meet in the middle. (b) HIDDEN: MW and PWG follow documented and DIFFERENT "
      + "headword conventions (Patel 2016, docs/refs/Patel_2016_Normalizing_headwords.pdf) which this "
      + "pipeline does not reconcile — śatṛ stems MW '-at' vs PWG '-a' (conv. 3.1/3.2), vatup/matup "
      + "MW '-vat/-mat' vs PWG '-v/-m' (3.4/3.5), ṛ-stems MW '-ṛ' vs PWG '-ar' (6.1/6.2), and "
      + "vas/yas MW '-vas/-yas' vs PWG '-vaṃs/-yaṃs' (7.1/7.4). Reach for this label when source and "
      + "target differ only in vowel length, accent, or a diacritic the normaliser touches.",
    assertsRu:
      "Ребро может быть артефактом склейки строк, а не фактом языка. Два механизма, действующих в "
      + "противоположные стороны. (а) СОЗДАНО: m6_xref_lineage.py перед пересечением убирает у MW "
      + "дефисы и знаки ударения, а у PWG — кружок «°», поэтому заголовки, написанные словарями "
      + "по-разному, могут совпасть. (б) СКРЫТО: MW и PWG следуют задокументированным и РАЗНЫМ "
      + "конвенциям записи заголовков (Patel 2016, docs/refs/Patel_2016_Normalizing_headwords.pdf), "
      + "которые этот конвейер не согласует: причастия на śatṛ у MW «-at», у PWG «-a» (конв. 3.1/3.2); "
      + "vatup/matup у MW «-vat/-mat», у PWG «-v/-m» (3.4/3.5); основы на ṛ у MW «-ṛ», у PWG «-ar» "
      + "(6.1/6.2); vas/yas у MW «-vas/-yas», у PWG «-vaṃs/-yaṃs» (7.1/7.4). Выбирайте эту метку, "
      + "когда источник и цель различаются только долготой гласного, ударением или диакритикой, "
      + "которую трогает нормализатор.",
    doesNotAssert:
      "NOT that the words are unrelated — a length variant is often a genuine by-form. It flags that "
      + "THIS edge is not independent evidence, because the matching step could have manufactured it. "
      + `Note the (b) mechanism also means the ${sharedEdgePoolSize()}-edge intersection UNDERCOUNTS: a ṛ-stem edge can `
      + "never intersect while MW writes '-ṛ' and PWG writes '-ar'.",
    doesNotAssertRu:
      "НЕ утверждает, что слова не связаны, — вариант по долготе часто является настоящей побочной "
      + "формой. Метка говорит лишь о том, что ИМЕННО ЭТО ребро не является независимым свидетельством, "
      + "поскольку шаг сопоставления мог его изготовить. Заметьте: механизм (б) означает также, что "
      + `пересечение из ${sharedEdgePoolSize()} рёбер ЗАНИЖЕНО — ребро на основе с ṛ вообще не может попасть в пересечение, `
      + "пока MW пишет «-ṛ», а PWG «-ar».",
    examples: [
      {
        sampleId: "mw-pwg-shared:30",
        edge: "BuHKAra -> BUHKAra (buhkāra -> būhkāra)",
        why:
          "Source and target differ only in the length of the first vowel, and the reciprocal edge "
          + "mw-pwg-shared:15 runs the other way. Plausibly an artifact of which form each dictionary "
          + "chose as headword.",
        whyRu:
          "Источник и цель различаются только долготой первого гласного, а обратное ребро "
          + "mw-pwg-shared:15 идёт в другую сторону. Вероятно, артефакт того, какую форму каждый "
          + "словарь выбрал заголовком."
      },
      {
        sampleId: "mw-pwg-shared:21",
        edge: "BastrakA -> BastrAkA (bhastrakā -> bhastrākā)",
        why: "Same shape: only the placement of vowel length distinguishes the two strings.",
        whyRu: "Тот же случай: строки различаются только местом долготы гласного."
      }
    ]
  },
  {
    label: "too-sparse",
    appliesToSheet: true,
    meaning: "A pair has too few shared sources for lineage interpretation.",
    meaningRu: "У пары слишком мало общих источников, чтобы судить о происхождении.",
    asserts:
      "The evidence on the card is too thin to answer either way — typically only ONE dictionary's "
      + "record is attached (`missingExactEdgeDictionaries` is non-empty), so the 'shared' in "
      + "shared-core is not actually demonstrated here.",
    assertsRu:
      "Свидетельства на карточке слишком мало, чтобы ответить в любую сторону: обычно приложена запись "
      + "только ОДНОГО словаря (поле `missingExactEdgeDictionaries` непусто), так что «общность» "
      + "shared-core здесь фактически не показана.",
    doesNotAssert:
      "NOT a rejection of the edge. It is the honest answer when the card does not contain what the "
      + "question asks about — prefer it to guessing.",
    doesNotAssertRu:
      "НЕ отклонение ребра. Это честный ответ, когда на карточке нет того, о чём спрашивает вопрос; "
      + "он предпочтительнее догадки.",
    examples: [
      {
        sampleId: "mw-pwg-shared:07",
        edge: "ArAt -> Are (ārāt -> āre), PWG only",
        why:
          "Only the PWG record is attached; MW has no exact edge row. PWG's record shows an ablative "
          + "adverb pointing at a locative-shaped one, and there is no MW side to corroborate.",
        whyRu:
          "Приложена только запись PWG; точного ребра MW нет. В записи PWG наречие в аблативе отсылает "
          + "к форме локативного вида, и нет стороны MW, чтобы это подтвердить."
      },
      {
        sampleId: "mw-pwg-shared:03",
        edge: "Akzit -> anAkzit (ākṣit -> anākṣit), PWG only",
        why: "Single-dictionary evidence again: 4 of the 40 rows are in this state and are marked as such on the card.",
        whyRu: "Снова свидетельство одного словаря: в таком состоянии 4 строки из 40, и на карточке это отмечено."
      }
    ]
  },
  {
    label: "edition-continuity",
    appliesToSheet: false,
    meaning: "A stable edge across editions of the same dictionary family.",
    meaningRu: "Устойчивое ребро между изданиями одного словарного семейства.",
    asserts: "Used by the upstream hub classifier for within-family (e.g. PW/PWG) edges.",
    assertsRu: "Используется вышестоящим классификатором для рёбер внутри одного семейства (например, PW/PWG).",
    doesNotAssert: "Not an answer option on the MW/PWG shared-core sheet, which is cross-family by construction.",
    doesNotAssertRu: "Не вариант ответа на этом листе: MW/PWG — межсемейная пара по построению.",
    examples: []
  },
  {
    label: "lexical-target",
    appliesToSheet: false,
    meaning: "A top xref target that behaves like an ordinary lexical target rather than a convention hub.",
    meaningRu: "Частая цель ссылок, ведущая себя как обычная лексическая цель, а не как узел условностей.",
    asserts:
      "A property of a TARGET string in the hub profile (classifyHubTarget in build-xref-hub-review.mjs), "
      + "carried on each row as `hubClass`. It is the reason a row reached this sheet, not a verdict on it.",
    assertsRu:
      "Свойство строки-ЦЕЛИ в профиле узлов (classifyHubTarget в build-xref-hub-review.mjs), которое "
      + "переносится в каждую строку как `hubClass`. Это причина попадания строки на лист, а не приговор ей.",
    doesNotAssert: "Not an answer option; it describes the target, not the edge.",
    doesNotAssertRu: "Не вариант ответа: описывает цель, а не ребро.",
    examples: []
  }
]);

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

// H1646 raised this from 260. At 260 the PWG side of a long record was cut
// mid-sense ("... 1〉 aus der Ferne, von fern; fern, ...") and the reviewer could
// not see whether the cross-reference clause the edge rests on was even present.
// 900 keeps whole records for the shared-core sample while staying compact.
const EXCERPT_LENGTH = 900;

function compactText(value, length = EXCERPT_LENGTH) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1)}...` : text;
}

function edgeKey(dict, k1, target) {
  return `${String(dict).toLowerCase()}\u0000${k1}\u0000${target}`;
}

function recordKey(dict, L) {
  return `${String(dict).toLowerCase()}\u0000${L}`;
}

function pointerKey(edge, role) {
  return `${role}\u0000${String(edge.dict).toLowerCase()}\u0000${edge.L}\u0000${edge.k1}\u0000${edge.target}`;
}

function labelSet() {
  return new Set(XREF_LABEL_VOCABULARY.map(row => row.label));
}

function indexExactEdges(edgeRows) {
  const index = new Map();
  for (const row of edgeRows) {
    const key = edgeKey(row.dict, row.k1, row.target);
    if (!index.has(key)) index.set(key, []);
    index.get(key).push(row);
  }
  return index;
}

function sourceEdgesForSharedSample(sample, exactEdgeIndex) {
  return ["mw", "pwg"].flatMap(dict => exactEdgeIndex.get(edgeKey(dict, sample.sourceLemma, sample.target)) ?? []);
}

function prefixTargetsFor(hubReview, dict) {
  const profile = (hubReview.hubProfiles ?? []).find(row => row.code === dict);
  if (!profile) return [];
  return (profile.topTargets ?? [])
    .filter(row => row.hubClass === "prefix-convention")
    .slice(0, PREFIX_CONTROL_TARGETS_PER_DICT);
}

function selectPrefixControlSpecs(hubReview, edgeRows) {
  const specs = [];
  for (const dict of ["pwg", "mw"]) {
    for (const [index, target] of prefixTargetsFor(hubReview, dict).entries()) {
      const sampleEdges = edgeRows
        .filter(row => row.dict === dict && row.target === target.target)
        .slice(0, PREFIX_CONTROL_EXAMPLES_PER_TARGET);
      specs.push({
        controlId: `xref-prefix-control:${dict}:${String(index + 1).padStart(2, "0")}`,
        dictionary: dict,
        target: target.target,
        targetRank: index + 1,
        targetCount: target.count,
        hubClass: target.hubClass,
        interpretation: target.interpretation,
        sampleEdges
      });
    }
  }
  return specs;
}

function neededSourceRecords(edgeRows) {
  const needed = new Map();
  for (const row of edgeRows) {
    const dict = String(row.dict).toLowerCase();
    if (!needed.has(dict)) needed.set(dict, new Set());
    needed.get(dict).add(String(row.L));
  }
  return needed;
}

function buildSourceRecordIndex(edgeRows) {
  const needed = neededSourceRecords(edgeRows);
  const index = new Map();
  const warnings = [];
  for (const [dict, Ls] of needed) {
    if (!dictExists(dict)) {
      warnings.push(`Missing source dictionary ${dict}; source pointers for ${dict.toUpperCase()} retain xref_edges.csv L values only.`);
      continue;
    }
    for (const rec of iterateDict(dict)) {
      if (!Ls.has(String(rec.L))) continue;
      index.set(recordKey(dict, rec.L), {
        L: String(rec.L),
        line: rec.startLine,
        href: rec.href,
        pc: rec.pc ?? null,
        sourceLemma: rec.k1,
        bodyExcerpt: compactText(rec.body)
      });
    }
  }
  return { index, warnings };
}

export function preservedSourcePointerMap(packet) {
  const preserved = new Map();
  for (const row of [...(packet.sharedCoreRows ?? []), ...(packet.prefixControlRows ?? [])]) {
    for (const pointer of row.sourcePointers ?? []) {
      preserved.set(pointerKey({
        dict: pointer.dict,
        L: pointer.L,
        k1: pointer.sourceLemma,
        target: pointer.target
      }, pointer.role), pointer);
    }
  }
  return preserved;
}

function loadPreservedSourcePointers(outputPath) {
  if (!fs.existsSync(outputPath)) return new Map();
  try {
    return preservedSourcePointerMap(JSON.parse(fs.readFileSync(outputPath, "utf8")));
  } catch {
    return new Map();
  }
}

function pointerForEdge(edge, sourceRecordIndex, role, preservedSourcePointers = new Map()) {
  const source = sourceRecordIndex.get(recordKey(edge.dict, edge.L));
  const preserved = preservedSourcePointers.get(pointerKey(edge, role));
  // Cologne links are derived from (dict, headword, <pc>) alone, so a pointer
  // recovered from a previous packet still gets them — they do not depend on
  // csl-orig being present in this run.
  const pc = source?.pc ?? preserved?.pc ?? null;
  const headword = source?.sourceLemma ?? preserved?.sourceRecordLemma ?? edge.k1;
  const cologne = cologneLinksFor(edge.dict, headword, pc);
  if (!source && preserved) return { ...preserved, pc, ...cologne };
  return {
    role,
    dictionary: String(edge.dict).toUpperCase(),
    dict: edge.dict,
    L: edge.L,
    line: source?.line ?? preserved?.line ?? null,
    pc,
    href: source?.href ?? preserved?.href ?? null,
    ...cologne,
    sourceLemma: edge.k1,
    sourceRecordLemma: source?.sourceLemma ?? preserved?.sourceRecordLemma ?? null,
    target: edge.target,
    kind: edge.kind,
    bodyExcerpt: source?.bodyExcerpt ?? preserved?.bodyExcerpt ?? ""
  };
}

// A cross-reference has two ends, and the packet only ever carried records for the
// SOURCE end. Asking "is ARi -> aRi a real lexical edge?" while showing only the ARi
// entries makes the question unanswerable — H1646: "you do not give links to Cologne,
// to check what the entries actually contain, both aRi and ARi". These are the target
// end: a Cologne lookup of the target headword in each dictionary.
//
// Built from the target string, so it is only emitted when that string is a plain
// SLP1 headword. A truncation/prefix target (a˚, aBi-) is not a lemma and would send
// the reviewer to an empty result, which is worse than no link.
function isLookupableHeadword(target) {
  return /^[A-Za-z]+$/.test(String(target ?? ""));
}

function targetLinksFor(target) {
  if (!isLookupableHeadword(target)) return [];
  return ["mw", "pwg"]
    .map(dict => ({
      role: "target-lookup",
      dictionary: dict.toUpperCase(),
      dict,
      headword: target,
      cologneEntryHref: entryUrl(dict, target)
    }))
    .filter(link => link.cologneEntryHref);
}

function emptyHumanFields() {
  return {
    reviewStatus: "needs-source-check",
    reviewedValue: null,
    reviewer: "",
    reviewedAt: "",
    note: ""
  };
}

function sharedReviewQuestion(row) {
  return `Do the MW/PWG source records support ${row.sourceLemma} -> ${row.target} as a meaningful shared lexical xref rather than a normalization or convention artifact?`;
}

// The reviewer reads Russian; the sheet is his instruction surface (H1648), so the
// question ships in Russian too. Lemma tokens stay SLP1 here — the sheet builder
// swaps them for IAST and keeps the SLP1 key alongside.
function sharedReviewQuestionRu(row) {
  return `Подтверждают ли записи MW и PWG, что ${row.sourceLemma} -> ${row.target} — осмысленная общая лексическая перекрёстная ссылка, а не артефакт нормализации или издательской условности?`;
}

function prefixReviewQuestion(row) {
  return `Do the sampled ${row.dictionary.toUpperCase()} references to ${row.target} behave as prefix/compound convention rather than lexical lineage evidence?`;
}

function buildSharedCoreRows(hubReview, exactEdgeIndex, sourceRecordIndex, preservedSourcePointers = new Map()) {
  return (hubReview.sharedCoreSample ?? []).slice(0, SHARED_CORE_LIMIT).map(sample => {
    const sourceEdges = sourceEdgesForSharedSample(sample, exactEdgeIndex);
    const matched = new Set(sourceEdges.map(row => row.dict.toUpperCase()));
    const row = {
      sampleId: sample.sampleId,
      sampleClass: "shared-core",
      sourceLemma: sample.sourceLemma,
      target: sample.target,
      hubClass: sample.hubClass,
      proposedLabels: [sample.reviewLabel],
      machineInterpretation: sample.interpretation,
      sourcePointers: sourceEdges.map(edge => pointerForEdge(edge, sourceRecordIndex, "exact-shared-edge", preservedSourcePointers)),
      targetLinks: targetLinksFor(sample.target),
      matchedDictionaries: [...matched].sort(),
      missingExactEdgeDictionaries: ["MW", "PWG"].filter(dict => !matched.has(dict)),
      reviewQuestion: sharedReviewQuestion(sample),
      reviewQuestionRu: sharedReviewQuestionRu(sample),
      ...emptyHumanFields()
    };
    return row;
  });
}

function buildPrefixControlRows(prefixSpecs, sourceRecordIndex, preservedSourcePointers = new Map()) {
  return prefixSpecs.map(spec => ({
    controlId: spec.controlId,
    sampleClass: "prefix-control",
    dictionary: spec.dictionary.toUpperCase(),
    dict: spec.dictionary,
    target: spec.target,
    targetRank: spec.targetRank,
    targetCount: spec.targetCount,
    hubClass: spec.hubClass,
    proposedLabels: ["prefix-convention"],
    machineInterpretation: spec.interpretation,
    sourcePointers: spec.sampleEdges.map(edge => pointerForEdge(edge, sourceRecordIndex, "prefix-control-example", preservedSourcePointers)),
    reviewQuestion: prefixReviewQuestion(spec),
    ...emptyHumanFields()
  }));
}

function validatePayload(payload) {
  const errors = [];
  const allowed = labelSet();
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (payload.sharedCoreRows.length !== SHARED_CORE_LIMIT) {
    errors.push(`expected ${SHARED_CORE_LIMIT} shared-core rows, got ${payload.sharedCoreRows.length}`);
  }
  const sharedIds = payload.sharedCoreRows.map(row => row.sampleId);
  if (sharedIds.join("|") !== EXPECTED_SHARED_CORE_SAMPLE_IDS.join("|")) {
    errors.push(`shared-core row order changed: ${sharedIds.join(", ")}`);
  }
  const prefixIds = payload.prefixControlRows.map(row => row.controlId);
  if (prefixIds.join("|") !== EXPECTED_PREFIX_CONTROL_IDS.join("|")) {
    errors.push(`prefix-control row order changed: ${prefixIds.join(", ")}`);
  }
  if (payload.prefixControlRows.length !== EXPECTED_PREFIX_CONTROL_IDS.length) {
    errors.push(`expected ${EXPECTED_PREFIX_CONTROL_IDS.length} prefix-control rows, got ${payload.prefixControlRows.length}`);
  }
  for (const row of [...payload.sharedCoreRows, ...payload.prefixControlRows]) {
    const id = row.sampleId ?? row.controlId;
    if (!row.sourcePointers.length) errors.push(`${id}: missing source pointers`);
    if (!row.reviewQuestion) errors.push(`${id}: missing review question`);
    const autoResolved = row.autoTriage?.resolved === true;
    if (row.reviewStatus !== "needs-source-check" && row.reviewStatus !== "auto-resolved") {
      errors.push(`${id}: reviewStatus must be needs-source-check or auto-resolved`);
    }
    if (autoResolved !== (row.reviewStatus === "auto-resolved")) errors.push(`${id}: reviewStatus/autoTriage disagree`);
    if (autoResolved && !allowed.has(row.autoTriage.proposedDecision)) errors.push(`${id}: auto decision ${row.autoTriage.proposedDecision} out of vocabulary`);
    if (row.reviewedValue !== null) errors.push(`${id}: reviewedValue must stay null`);
    if (row.reviewer !== "") errors.push(`${id}: reviewer must stay empty`);
    if (row.reviewedAt !== "") errors.push(`${id}: reviewedAt must stay empty`);
    if (row.note !== "") errors.push(`${id}: note must stay empty`);
    for (const label of row.proposedLabels ?? []) {
      if (!allowed.has(label)) errors.push(`${id}: out-of-vocabulary label ${label}`);
    }
    for (const pointer of row.sourcePointers) {
      if (!pointer.dictionary || !pointer.L || !pointer.sourceLemma || !pointer.target) {
        errors.push(`${id}: incomplete source pointer`);
      }
      if (!pointer.href) errors.push(`${id}: source pointer ${pointer.dictionary} L${pointer.L} lacks href`);
      if (!pointer.cologneEntryHref) {
        errors.push(`${id}: source pointer ${pointer.dictionary} L${pointer.L} lacks cologneEntryHref`);
      }
    }
  }
  // Every shared-core row must let the reviewer read BOTH ends of the edge. A row
  // whose target is not a lookupable headword is a finding in itself, not a silent gap.
  for (const row of payload.sharedCoreRows) {
    if (!row.targetLinks?.length) {
      errors.push(`${row.sampleId}: no target-end Cologne links for target ${row.target}`);
    }
  }
  for (const row of payload.prefixControlRows) {
    if (row.sourcePointers.length !== PREFIX_CONTROL_EXAMPLES_PER_TARGET) {
      errors.push(`${row.controlId}: expected ${PREFIX_CONTROL_EXAMPLES_PER_TARGET} source examples`);
    }
  }
  if (payload.counts.sharedCoreRows !== payload.sharedCoreRows.length) errors.push("sharedCoreRows count mismatch");
  if (payload.counts.prefixControlRows !== payload.prefixControlRows.length) errors.push("prefixControlRows count mismatch");
  if (payload.counts.sourceCheckRows !== payload.sharedCoreRows.length + payload.prefixControlRows.length) {
    errors.push("sourceCheckRows count mismatch");
  }
  if (errors.length) {
    const error = new Error(`Xref source-check packet build failed with ${errors.length} error(s):\n${errors.map(line => `  - ${line}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

// Deterministic auto-triage. A cross-reference TARGET that is a truncation/prefix
// form — it carries the CDSL abbreviation ring "˚" or ends in a prefix hyphen "-"
// (e.g. a˚, su˚, aBi-) — is a prefix-convention hub by the dictionary's own markup,
// not a rare lexical inheritance, so auto-resolve it to `prefix-convention`
// (recording the target as evidence). The shared-core lexical edges, whose question
// is whether a genuine MW/PWG edge is *meaningful*, have no mechanical proof and
// stay for human source-check. String-only on the target, so no csl-orig is read.
function isTruncationTarget(target) {
  const t = target ?? "";
  return t.includes("˚") || t.endsWith("-");
}

export function applyAutoTriage(rows) {
  for (const row of rows) {
    if (isTruncationTarget(row.target)) {
      row.autoTriage = {
        resolved: true,
        proposedDecision: "prefix-convention",
        basis: "target-truncation-marker",
        evidence: { target: row.target }
      };
      row.reviewStatus = "auto-resolved";
    } else {
      row.autoTriage = { resolved: false };
    }
  }
  return rows;
}

export function buildPayload(hubReview, edgeRows, generatedAt = new Date().toISOString(), preservedSourcePointers = new Map()) {
  const exactEdgeIndex = indexExactEdges(edgeRows);
  const sharedSourceEdges = (hubReview.sharedCoreSample ?? [])
    .slice(0, SHARED_CORE_LIMIT)
    .flatMap(sample => sourceEdgesForSharedSample(sample, exactEdgeIndex));
  const prefixSpecs = selectPrefixControlSpecs(hubReview, edgeRows);
  const prefixSourceEdges = prefixSpecs.flatMap(spec => spec.sampleEdges);
  const { index: sourceRecordIndex, warnings } = buildSourceRecordIndex([...sharedSourceEdges, ...prefixSourceEdges]);
  const sharedCoreRows = buildSharedCoreRows(hubReview, exactEdgeIndex, sourceRecordIndex, preservedSourcePointers);
  const prefixControlRows = buildPrefixControlRows(prefixSpecs, sourceRecordIndex, preservedSourcePointers);
  const allRows = applyAutoTriage([...sharedCoreRows, ...prefixControlRows]);
  const unresolvedSourcePointers = allRows.flatMap(row => row.sourcePointers).filter(pointer => !pointer.href);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "xref-source-check-packet",
    claim: "XREF-CORE source checking must keep MW/PWG lexical shared-core rows separate from PWG/MW prefix-convention hub controls.",
    evidenceLabel: "derived-source-pointers",
    reviewStatus: "needs-source-check",
    ownerRepo: "csl-atlas",
    generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "data/lexico/xref_hub_review.json",
      "data/lexico/xref_edges.csv",
      "scripts/build-xref-hub-review.mjs",
      "scripts/build-xref-source-check-packet.mjs",
      "../csl-orig/v02/mw/mw.txt",
      "../csl-orig/v02/pwg/pwg.txt"
    ],
    sourceArtifact: {
      path: "data/lexico/xref_hub_review.json",
      generatedBy: hubReview.generatedBy,
      sourceGeneratedAt: hubReview.sourceGeneratedAt,
      sharedCoreSample: hubReview.counts?.sharedCoreSample ?? null
    },
    packetLabelVocabulary: XREF_LABEL_VOCABULARY,
    counts: {
      sourceCheckRows: allRows.length,
      autoResolved: allRows.filter(row => row.autoTriage?.resolved).length,
      needsHumanReview: allRows.filter(row => !row.autoTriage?.resolved).length,
      byAutoDecision: countBy(allRows.filter(row => row.autoTriage?.resolved), row => row.autoTriage.proposedDecision),
      sharedCoreRows: sharedCoreRows.length,
      prefixControlRows: prefixControlRows.length,
      sourcePointerRows: allRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      exactSharedCorePointers: sharedCoreRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      sharedCoreRowsWithMissingExactEdge: sharedCoreRows.filter(row => row.missingExactEdgeDictionaries.length).length,
      prefixControlPointers: prefixControlRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      bySampleClass: countBy(allRows, row => row.sampleClass),
      byProposedLabel: countBy(allRows.flatMap(row => row.proposedLabels), label => label),
      prefixControlsByDictionary: countBy(prefixControlRows, row => row.dict)
    },
    // H1646: the reviewer could not see "the list of methods used for sampling these
    // words", so this now states the actual mechanism end to end, including the
    // selection bias, rather than only the steps this script performs.
    selectionPolicy: [
      "Stage 1 — build the candidate pool: scripts/lexico/m6_xref_lineage.py reads MW's and PWG's "
        + "cross-reference edges, normalises each target (strips MW's '-' and accent marks and PWG's "
        + "'°' ring), and writes the MW-intersect-PWG set to data/lexico/xref_shared_edges.csv. "
        + `That intersection is ${sharedEdgePoolSize()} edges.`,
      "Stage 2 — take the sample: buildSharedCoreSample() in scripts/build-xref-hub-review.mjs takes "
        + "sharedEdges.slice(0, 40), i.e. the FIRST 40 rows of that CSV in file order.",
      "NOT A RANDOM SAMPLE, and the bias is visible on the sheet: the CSV is in headword order, so "
        + "all 40 cards are Ā-, B-, C-, D- and G-initial headwords. Findings from these 40 describe "
        + `the head of the alphabet, not the ${sharedEdgePoolSize()} as a whole. Re-running over a random or stratified `
        + "draw is a separate, unstarted job.",
      "Stage 3 — attach evidence: this script re-slices to 40, keeps the frozen sampleId order "
        + "(validatePayload rejects any reorder), and attaches the exact MW/PWG source records per edge "
        + "from xref_edges.csv, plus Cologne entry/scan links for both ends of the edge.",
      "Controls: the first five prefix-convention top targets for PWG and MW, with up to three source "
        + "examples each, are carried alongside as a contrast class; all ten auto-resolve on their "
        + "truncation marker and are not put to the reviewer.",
      "Deterministic throughout — no RNG anywhere in the three stages; re-running reproduces the same "
        + "40 cards in the same order.",
      "Labels on the cards are source-check prompts, not accepted lineage decisions."
    ],
    // H1648 — the Russian rendering the sheet actually shows the reviewer.
    selectionPolicyRu: [
      "Шаг 1 — построение пула кандидатов: scripts/lexico/m6_xref_lineage.py читает перекрёстные "
        + "ссылки MW и PWG, нормализует каждую цель (убирает у MW дефис и знаки ударения, у PWG — "
        + "кружок «°») и записывает пересечение MW ∩ PWG в data/lexico/xref_shared_edges.csv. "
        + `В пересечении ${sharedEdgePoolSize()} ребра.`,
      "Шаг 2 — взятие выборки: buildSharedCoreSample() в scripts/build-xref-hub-review.mjs берёт "
        + "sharedEdges.slice(0, 40), то есть ПЕРВЫЕ 40 строк этого CSV в порядке файла.",
      "ЭТО НЕ СЛУЧАЙНАЯ ВЫБОРКА, и смещение видно на листе: CSV упорядочен по заголовкам, поэтому "
        + "все 40 карточек — заголовки на Ā-, B-, C-, D- и G-. Выводы по этим 40 описывают начало "
        + `алфавита, а не все ${sharedEdgePoolSize()}. Прогон по случайной или стратифицированной выборке — отдельная, `
        + "ещё не начатая задача.",
      "Шаг 3 — приложение свидетельств: этот скрипт снова берёт 40, сохраняет замороженный порядок "
        + "sampleId (validatePayload отвергает любую перестановку) и прикладывает точные записи "
        + "MW/PWG для каждого ребра из xref_edges.csv, а также кёльнские ссылки на статью и скан "
        + "для обоих концов ребра.",
      "Контроли: первые пять частых prefix-convention целей у PWG и у MW, до трёх примеров-источников "
        + "на каждую, идут рядом как контрастный класс; все десять разрешаются автоматически по знаку "
        + "усечения и человеку не показываются.",
      "Всё детерминировано — ни на одном из трёх шагов нет генератора случайных чисел; повторный "
        + "прогон даёт те же 40 карточек в том же порядке.",
      "Метки на карточках — это подсказки для проверки по источнику, а не принятые решения о "
        + "происхождении."
    ],
    // H1648 — MG's ruling that MW depends on PW/PWG, measured rather than assumed.
    markerIndependence: {
      finding: "MW `cf.` and PWG `Vgl.` cross-references are NOT independent witnesses.",
      findingRu: "Перекрёстные ссылки MW («cf.») и PWG («Vgl.») НЕ являются независимыми свидетельствами.",
      headwordsInBoth: 2750,
      agreementRate: 0.218,
      expectedRate: 0.00007,
      enrichment: 2953.2,
      pValue: "< 0.005",
      artifact: "data/lexico/xref_marker_agreement.json",
      generatedBy: "python scripts/lexico/m9_xref_marker_agreement.py",
      noteRu: "MW (1899) опирается на PW/PWG. Общая ссылка не удваивает свидетельство."
    },
    sharedCoreRows,
    prefixControlRows,
    limitations: [
      "Machine labels are review prompts only; this packet records no source-check decisions.",
      `The 40 shared-core rows are the first 40 of ${sharedEdgePoolSize()} shared edges in headword order, not a random `
        + "sample: every card is an Ā-, B-, C-, D- or G-initial headword. Do not generalise a rate "
        + "measured on these 40 to the full intersection.",
      "Cologne entry links resolve a HEADWORD, not this exact record: where a dictionary has homonyms "
        + "the lookup shows all of them. The csl-orig blob link is the pointer to the precise record.",
      "Some shared-core sample rows are present in the shared-edge sample but lack an exact MW edge row in xref_edges.csv; those rows remain visible with missing-exact-edge metadata.",
      "Prefix controls test convention pressure and are not optimization targets for lineage claims.",
      "Cross-reference overlap remains dictionary-internal evidence and must not be mixed with DCS/corpus co-occurrence.",
      "No R2 splitter behavior, source-anchor generation, H5 review row, public page, backend/runtime LLM, corpus, DCS, or standards work is changed."
    ],
    limitationsRu: [
      "Машинные метки — только подсказки для проверки; этот пакет не фиксирует никаких решений.",
      `40 строк shared-core — это первые 40 из ${sharedEdgePoolSize()} общих рёбер в порядке заголовков, а не случайная `
        + "выборка: каждая карточка — заголовок на Ā-, B-, C-, D- или G-. Не переносите долю, "
        + "измеренную на этих 40, на всё пересечение.",
      "Кёльнская ссылка на статью открывает ЗАГОЛОВОК, а не именно эту запись: при омонимах поиск "
        + "покажет их все. Точную запись адресует ссылка на csl-orig.",
      "Часть строк присутствует в выборке общих рёбер, но не имеет точного ребра MW в xref_edges.csv; "
        + "такие строки остаются видимыми и помечены.",
      "MW и PWG следуют разным конвенциям записи заголовков (Patel 2016), которые конвейер не "
        + `согласует, поэтому пересечение из ${sharedEdgePoolSize()} рёбер занижено: часть настоящих общих рёбер `
        + "не может совпасть по строке в принципе.",
      "Prefix-control проверяют давление издательских условностей и не являются целью оптимизации.",
      "Пересечение перекрёстных ссылок остаётся внутрисловарным свидетельством и не должно "
        + "смешиваться с совстречаемостью по корпусу DCS."
    ],
    boundaryNote: "Atlas xref artifacts plus dictionary source pointers only; source checking is deferred to human review and does not promote parser or public-lineage behavior.",
    warnings: unresolvedSourcePointers.length ? warnings : []
  };
  validatePayload(payload);
  return payload;
}

function markdownCell(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/\|/g, "\\|");
}

function pointerMd(pointer) {
  const excerpt = pointer.bodyExcerpt ? ` - ${markdownCell(pointer.bodyExcerpt)}` : "";
  return `[${pointer.dictionary} L${pointer.L}](${pointer.href}) ${markdownCell(pointer.sourceLemma)} -> ${markdownCell(pointer.target)}${excerpt}`;
}

function countTable(title, counts) {
  return [
    `## ${title}`,
    "",
    "| Key | Rows |",
    "|---|---:|",
    ...Object.entries(counts).map(([key, count]) => `| \`${markdownCell(key)}\` | ${count} |`),
    ""
  ].join("\n");
}

function sharedCoreTable(rows) {
  return [
    "| Sample | Source lemma | Target | Proposed labels | Missing exact edge | Source pointers | Review question |",
    "|---|---|---|---|---|---|---|",
    ...rows.map(row => {
      const missing = row.missingExactEdgeDictionaries.length ? row.missingExactEdgeDictionaries.join(", ") : "none";
      return `| \`${row.sampleId}\` | \`${markdownCell(row.sourceLemma)}\` | \`${markdownCell(row.target)}\` | ${row.proposedLabels.map(label => `\`${label}\``).join(", ")} | ${missing} | ${row.sourcePointers.map(pointerMd).join("<br>")} | ${markdownCell(row.reviewQuestion)} |`;
    }),
    ""
  ].join("\n");
}

function prefixControlTable(rows) {
  return [
    "| Control | Dictionary | Target | Proposed labels | Source pointers | Review question |",
    "|---|---|---|---|---|---|",
    ...rows.map(row => `| \`${row.controlId}\` | \`${row.dictionary}\` | \`${markdownCell(row.target)}\` | ${row.proposedLabels.map(label => `\`${label}\``).join(", ")} | ${row.sourcePointers.map(pointerMd).join("<br>")} | ${markdownCell(row.reviewQuestion)} |`),
    ""
  ].join("\n");
}

export function buildMarkdown(payload) {
  const lines = [
    "# Xref Source-Check Packet",
    "",
    "Date: 2026-06-07",
    "",
    "Status: generated source-check packet; all rows remain `needs-source-check` and no human decisions are recorded.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.sharedCoreRows} shared-core rows, ${payload.counts.prefixControlRows} prefix-control rows, ${payload.counts.sourcePointerRows} source pointers.`,
    `- Auto-triage: ${payload.counts.autoResolved} of ${payload.counts.sourceCheckRows} rows deterministically auto-resolved as \`prefix-convention\` (the target carries a truncation marker \`˚\`/\`-\`, evidence in \`autoTriage.evidence.target\`); ${payload.counts.needsHumanReview} need human source-check. The shared-core lexical edges (is a genuine MW/PWG edge meaningful?) have no mechanical proof and stay for review; auto-resolved rows are overridable.`,
    `- Boundary note: ${payload.boundaryNote}`,
    "",
    "## Selection Policy",
    "",
    ...payload.selectionPolicy.map(item => `- ${item}`),
    "",
    countTable("Counts By Sample Class", payload.counts.bySampleClass),
    countTable("Counts By Proposed Label", payload.counts.byProposedLabel),
    countTable("Prefix Controls By Dictionary", payload.counts.prefixControlsByDictionary),
    "## Human Fields",
    "",
    "Every row keeps `reviewedValue = null`, `reviewer = \"\"`, `reviewedAt = \"\"`, and `note = \"\"`. Source-check decisions are outside this generated packet.",
    "",
    "## MW/PWG Shared-Core Rows",
    "",
    sharedCoreTable(payload.sharedCoreRows),
    "## PWG/MW Prefix Controls",
    "",
    prefixControlTable(payload.prefixControlRows),
    "## Limitations",
    "",
    ...payload.limitations.map(item => `- ${item}`),
    "",
    "## Boundary",
    "",
    `- ${payload.boundaryNote}`,
    ""
  ];
  return `${lines.join("\n")}\n`;
}

function main() {
  try {
    const hubReview = JSON.parse(fs.readFileSync(HUB_REVIEW_PATH, "utf8"));
    const edgeRows = parseCsv(fs.readFileSync(XREF_EDGES_PATH, "utf8"));
  const preservedSourcePointers = loadPreservedSourcePointers(JSON_OUT);
  const payload = buildPayload(hubReview, edgeRows, undefined, preservedSourcePointers);
  payload.generatedAt = generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
    fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
    fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
    fs.writeFileSync(MARKDOWN_OUT, buildMarkdown(payload));
    console.log(`Wrote ${payload.counts.sourceCheckRows} xref source-check rows to:`);
    console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
    console.log(`- ${path.relative(process.cwd(), MARKDOWN_OUT)}`);
    console.log(`Counts: ${JSON.stringify(payload.counts)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
