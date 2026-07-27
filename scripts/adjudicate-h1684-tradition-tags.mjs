// H1684 — agent adjudication of the 119 unreviewed tradition tags (В2 stage).
//
// The sheet `csl-atlas-tradition-tags_119texts` asks a reviewer to confirm or
// correct the text→tradition hypothesis in data/citations/tradition_tags.tsv
// against the closed TRADITION_VOCAB. This script rules on every row and
// attaches catalogue evidence from the ACC×NCC works catalogue (H1657 P0
// outputs: SanskritLexicography/HeadwordLists/works_catalogue/{acc,ncc}.jsonl).
//
// ── The trap this script is built around ────────────────────────────────────
// Title-only matching into ACC/NCC is HOMONYM-DENSE. Both catalogues list many
// distinct works under one title, so the first folded-key hit is frequently a
// different work than the one the citation graph means. Measured examples:
//   Lalitavistara   → NCC hit is a *Śaiva* Śiva-Pārvatī dialogue
//   Bhāvaprakāśa    → ACC hit is Śāradātanaya's *alaṃkāra* work, not the āyurveda one
//   Līlāvatī        → ACC hit is *Nyāya*līlāvatī, not Bhāskara's gaṇita
//   Bṛhatsaṃhitā    → ACC hit is a *dharma* text "by Vyāsa", not Varāhamihira's
//   Ratnāvalī       → ACC hit is "an elementary grammar", not Harṣa's nāṭikā
// So a catalogue hit is treated as CORROBORATION when its subject siglum agrees
// with the proposed tradition, and as a CONFLICT otherwise — and a conflict
// demotes the row to human review unless an explicit override records why the
// homonym is known and the canonical attribution stands. Nothing is confirmed
// on the strength of an unexamined first hit.
//
// Usage: node scripts/adjudicate-h1684-tradition-tags.mjs
// Read-only against the catalogue. Writes the packet + decisions.json only.

import fs from "node:fs";
import zlib from "node:zlib";
import path from "node:path";
import readline from "node:readline";
import { pathToFileURL } from "node:url";
import { parseTsv, TRADITION_VOCAB } from "./build-tradition-tags.mjs";

const ROOT = process.cwd();
const TAGS_PATH = path.join(ROOT, "data/citations/tradition_tags.tsv");
const CATALOGUE = path.resolve(ROOT, "..", "SanskritLexicography", "HeadwordLists", "works_catalogue");
const PACKET_PATH = path.join(ROOT, "data/citations/h1684_tradition_adjudication_packet.json");
const DECISIONS_PATH = path.join(ROOT, "review/csl-atlas-tradition-tags_119texts_decisions.json");
const HANDOFF = "H1684";
const REVIEWER = "Opus 5 1M (`claude-opus-5[1m]`) — H1684 agent; evidence: ACC×NCC works catalogue (H1657 P0) + canonical attribution";

// ---------------------------------------------------------------------------
// ACC/NCC subject sigla → this repo's closed tradition vocabulary.
// ---------------------------------------------------------------------------
const SIGLUM_TRADITION = new Map(Object.entries({
  "dh.": "dharma-sastra", "smṛti": "dharma-sastra",
  "jy.": "jyotisa",
  "ny.": "darsana", "vaiś.": "darsana", "mīm.": "darsana", "vedānta": "darsana",
  "vedānta.": "darsana", "yoga.": "darsana", "sāṃkhya": "darsana", "phil.": "darsana",
  "med.": "medical", "vaid.": "medical",
  "gr.": "grammar-sastra", "grammarian.": "grammar-sastra",
  "alaṃk.": "poetics-sastra", "chandas": "poetics-sastra",
  "lex.": "lexical-kosa",
  "kāvya": "classical-kavya", "kāvya.": "classical-kavya", "nāṭaka": "classical-kavya",
  "nāṭaka.": "classical-kavya", "poet.": "classical-kavya",
  "paur.": "purana",
  "śr.": "vedic", "Rv.": "vedic", "Sv.": "vedic", "Yv.": "vedic", "Av.": "vedic", "Vs.": "vedic",
  "tantr.": "tantra", "tantra.": "tantra", "śaiva.": "tantra",
  "Bud.": "buddhist", "jain.": "jain"
}));

// ---------------------------------------------------------------------------
// Per-row overrides. Every row NOT listed here is ruled by the default:
// `canonical-attribution` — the seed tag names a text whose tradition is
// uncontested in the scholarly canon, confirmed and corroborated by the
// catalogue where the catalogue has a matching entry.
// ---------------------------------------------------------------------------
const NOT_A_WORK = {
  rule: "not-a-work",
  tradition: "other",
  why: "The citation label names a person, place, modern publication or catalogue — not a Sanskrit work — so it carries no tradition of its own."
};
const GENERIC_LABEL = {
  rule: "generic-tradition-label",
  why: "Not a specific work: an unspecified collective label. It carries no title, but it does name its tradition directly, so the tradition tag is the informative part and stands."
};
const COMMENTATOR = {
  rule: "commentator-follows-base-text",
  why: "The label names a commentator, not a work. In a lexicon citation graph the source is their commentary, so the row inherits the tradition of the base text they comment on."
};

const OVERRIDES = new Map(Object.entries({
  // — labels that are not Sanskrit works ————————————————————————————————
  "AUFRECHT": NOT_A_WORK,
  "Bombay": NOT_A_WORK,
  "my Sanskrit Chrestomathy": NOT_A_WORK,
  "GALANO's Wörterbuch": NOT_A_WORK,
  "Classified Index to the Sanskrit Mss": NOT_A_WORK,
  "Inscriptions": NOT_A_WORK,
  "Boehtlingk and Roth": NOT_A_WORK,

  // — generic collective labels ——————————————————————————————————————
  "Buddhist": { ...GENERIC_LABEL, tradition: "buddhist" },
  "Brāhmaṇa": {
    ...GENERIC_LABEL,
    tradition: "vedic",
    why: GENERIC_LABEL.why + " ACC carries the same usage explicitly: \"brāhmaṇa¦ without further statement\"."
  },

  // — commentators —————————————————————————————————————————————————
  "Kullūka": { ...COMMENTATOR, tradition: "dharma-sastra", why: COMMENTATOR.why + " Kullūka Bhaṭṭa's Manvarthamuktāvalī is the standard commentary on Manu." },
  "Mitākṣarā": { ...COMMENTATOR, tradition: "dharma-sastra", why: COMMENTATOR.why + " Vijñāneśvara's Mitākṣarā comments on the Yājñavalkyasmṛti. (ACC's folded-key hit is Haradatta's same-named commentary on Gautama — a different work, but also dharma-śāstra, so the tag is unaffected.)" },
  "Sāyaṇa": { ...COMMENTATOR, tradition: "vedic", why: COMMENTATOR.why + " Sāyaṇa's bhāṣyas are on the Saṃhitās and Brāhmaṇas.", homonymKnown: true },
  "Mallinātha": { ...COMMENTATOR, tradition: "classical-kavya", why: COMMENTATOR.why + " Mallinātha is the standard commentator on the five mahākāvyas and Meghadūta; every base text is kāvya.", homonymKnown: true },

  // — canonical attribution stands against a known catalogue homonym ————
  "Bṛhatsaṃhitā": { rule: "homonym-conflict-canonical-stands", tradition: "jyotisa", homonymKnown: true, why: "Varāhamihira's Bṛhatsaṃhitā is the astral/omen compendium PW cites. ACC's folded-key hit (\"dh. by Vyāsa\") is a different, same-titled dharma text." },
  "Līlāvatī": { rule: "homonym-conflict-canonical-stands", tradition: "jyotisa", homonymKnown: true, why: "Bhāskara II's Līlāvatī, part 1 of the Siddhāntaśiromaṇi. ACC's hit redirects to Nyāyalīlāvatī, a different work. Filed under jyotisa because the closed vocabulary has no gaṇita bucket — a vocabulary gap, not a misattribution." },
  "Bhāvaprakāśa": { rule: "homonym-conflict-canonical-stands", tradition: "medical", homonymKnown: true, why: "Bhāvamiśra's āyurvedic Bhāvaprakāśa. ACC's hit is Śāradātanaya's alaṃkāra work of the same name." },
  "Ratnāvalī": { rule: "homonym-conflict-canonical-stands", tradition: "classical-kavya", homonymKnown: true, why: "Harṣa's nāṭikā. ACC's folded-key hits are an elementary grammar and a different Ratnāvalī — same title, different works." },
  "Halāyudha": { rule: "homonym-conflict-canonical-stands", tradition: "lexical-kosa", homonymKnown: true, why: "Halāyudha the lexicographer (Abhidhānaratnamālā) is the kośa authority cited in this apparatus. ACC's hit (\"one of the gurus of Govinda\") is a different Halāyudha." },
  "Lalitavistara": { rule: "homonym-conflict-canonical-stands", tradition: "buddhist", homonymKnown: true, why: "The Mahāyāna Lalitavistara. NCC's folded-key hit is a Śaiva Śiva–Pārvatī dialogue of the same title." },
  "Laṅkāvatāra-sūtra": { rule: "homonym-conflict-canonical-stands", tradition: "buddhist", homonymKnown: true, why: "The Mahāyāna Laṅkāvatāra. NCC's folded-key hit is a Hindu tantric medical work." },
  "Śṛṅgāratilaka": { rule: "homonym-conflict-canonical-stands", tradition: "classical-kavya", homonymKnown: true, why: "ACC corroborates directly: \"śṛṅgāratilaka¦ kāvya … attributed to Kālidāsa\". Rudraṭa's same-titled poetics treatise exists but is not what this short kāvya citation names." },
  "Kirātārjunīya": { rule: "homonym-conflict-canonical-stands", tradition: "classical-kavya", homonymKnown: true, why: "Bhāravi's mahākāvya. ACC's entry lists only the Mahābhārata/Padmapurāṇa episode extracts, not Bhāravi's poem." },
  "Siddhāntakaumudi": { rule: "homonym-conflict-canonical-stands", tradition: "grammar-sastra", homonymKnown: true, why: "Bhaṭṭoji Dīkṣita's Siddhāntakaumudī (NCC corroborates the attribution). ACC's hit is a different Siddhāntasaṃgrahaṭīkā." },
  "Mahāvastu": { rule: "homonym-conflict-canonical-stands", tradition: "buddhist", homonymKnown: true, why: "NCC marks it \"Bud.\" — corroborated; the entry's prose is bibliography, not a competing attribution." },
  "Saddharmapuṇḍarīka": { rule: "homonym-conflict-canonical-stands", tradition: "buddhist", homonymKnown: true, why: "The Mahāyāna sūtra; NCC's own first entry redirects to Saddharmapuṇḍarīkasūtra. The sibling NCC entry marked \"med.\" (an āyurvedic text found in Central Asia, mixed with Prakrit) is a different work sharing the folded key." },
  "Hitopadeśa": { rule: "homonym-conflict-canonical-stands", tradition: "classical-kavya", homonymKnown: true, why: "Nārāyaṇa's nīti fable collection — ACC corroborates in prose (\"a collection of apologues, by Nārāyaṇa\"). The sibling ACC entry \"hitopadeśa¦ med. See Vaidyahitopadeśa\" is a medical work of the same title." },

  // — nearest-bucket calls where the closed vocabulary has no exact slot ——
  "Śrutabodha": { rule: "nearest-bucket-vocabulary-gap", tradition: "poetics-sastra", homonymKnown: true, why: "ACC: \"a poor compendium of Saṃskṛt metres\" — chandas, not alaṃkāra. The closed vocabulary has no prosody bucket; poetics-sastra is the nearest and is where the other kāvya-ancillary śāstras sit." },
  "Harivaṃśa": { rule: "homonym-conflict-canonical-stands", tradition: "epic", homonymKnown: true, why: "ACC corroborates directly: \"a supplement to the Mahābhārata\" — the khila, so epic rather than purana despite its purāṇic material. The sibling ACC entries marked \"kāvya\" and \"poet.\" are a different poem and a poet of the same name." },
  "Bhagavadgītā": { rule: "canonical-attribution", tradition: "epic", why: "ACC corroborates directly: \"an episode from the Bhīṣmaparvan of the Mahābhārata\". The darsana bucket in this vocabulary holds the śāstric systems, not devotional-philosophical poetry embedded in the epic." },

  // — OCR / spelling variants of another row on the same sheet ——————————
  "Raghuvanśa": { rule: "ocr-variant", tradition: "classical-kavya", why: "OCR variant of Raghuvaṃśa; inherits that row's tradition." },
  "Manusmṛiti": { rule: "ocr-variant", tradition: "dharma-sastra", why: "Spelling variant of Manusmṛti; inherits that row's tradition." },
  "Yājnyavalkyasmṛiti": { rule: "ocr-variant", tradition: "dharma-sastra", why: "Spelling variant of Yājñavalkyasmṛti; inherits that row's tradition." },
  "Mārkandeyapuraṇa": { rule: "ocr-variant", tradition: "purana", why: "Spelling variant of Mārkaṇḍeyapurāṇa; ACC corroborates the work." },
  "Bhāminīivilāsa": { rule: "ocr-variant", tradition: "classical-kavya", why: "OCR variant of Bhāminīvilāsa; inherits that row's tradition." },
  "Bhartṛihaṛiśataka [": { rule: "ocr-variant", tradition: "classical-kavya", why: "Garbled Bhartṛhari-śataka, including a stray bracket. The śataka — not the grammarian — so classical-kavya." },
  "HEĀDRI'S K4ATURVARGAK4INTĀMAṆI": { rule: "ocr-variant", tradition: "dharma-sastra", why: "OCR-garbled Hemādri, Caturvargacintāmaṇi — a dharma-nibandha." },
  "Rigveda": { rule: "ocr-variant", tradition: "vedic", why: "Non-diacritic variant of Ṛgveda; inherits that row's tradition." },
  "Bhāgavata": { rule: "ocr-variant", tradition: "purana", why: "Short form of Bhāgavata-Purāṇa; inherits that row's tradition." },
  "ŚUKASAPTATI in LASSEN'S Anthologie": { rule: "work-named-via-modern-anthology", tradition: "classical-kavya", why: "The label names a Sanskrit work (Śukasaptati) reached through a modern anthology. The work is named, so it carries its own tradition — unlike labels that name only the anthology." },

  // — genuine forks: NOT agent-decidable, routed to the human arm ————————
  "Mahāvyutpatti": {
    rule: "policy-fork-kosa-genre-vs-community",
    certain: false,
    why: "Both tags are defensible and the sheet's own precedent is inconsistent. Mahāvyutpatti is a Buddhist bilingual terminological lexicon: `buddhist` reads the tradition-community, `lexical-kosa` reads the genre. The same fork governs the Hemacandra row, where the seed data chose genre over community — so a single human ruling should settle both."
  },
  "Hemacandra": {
    rule: "policy-fork-kosa-genre-vs-community",
    certain: false,
    why: "The twin of the Mahāvyutpatti fork, decided the other way in the seed data: Hemacandra is a Jain polymath (the vocabulary has a `jain` bucket) whose kośas are what this apparatus cites, and the seed tag chose the genre (`lexical-kosa`) over the community (`jain`). One human ruling should set the policy for both rows."
  },
  "Bhartṛhari": {
    rule: "author-ambiguous-two-namesakes",
    certain: false,
    why: "Two distinct authors share the name and both are cited in this apparatus: the śataka poet (classical-kavya) and the grammarian-philosopher of the Vākyapadīya (grammar-sastra). ACC's entry for the folded key is the GRAMMARIAN (Vākyapadīya, Mahābhāṣyadīpikā), which is evidence against the seed tag rather than for it. Resolving this needs the citing entries, not the title."
  },
  "Āpastamba": {
    rule: "author-ambiguous-two-works",
    certain: false,
    why: "Āpastamba authored both a Śrautasūtra (vedic ritual) and a Dharmasūtra (dharma-sastra), and the bare label does not say which. ACC's entry enumerates the ŚRAUTASŪTRA first and at length, so the catalogue leans vedic while the seed tag says dharma-sastra. The sheet's separate `Āpastamba-Dharmasūtra` row shows the explicit form exists, which makes the bare one likelier to be the other work — but that is an inference, not evidence."
  },
  "Indische Sprüche": {
    rule: "policy-fork-modern-anthology",
    certain: false,
    why: "Böhtlingk's Indische Sprüche is a modern anthology, not a Sanskrit work, so by the rule applied to `my Sanskrit Chrestomathy` and `GALANO's Wörterbuch` it would be `other`; but unlike those, its cited content is entirely classical subhāṣita verse, which is what the seed tag records. The sheet applies both principles elsewhere without stating which wins."
  }
}));

// ---------------------------------------------------------------------------

function fold(s) {
  return String(s ?? "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z]/g, "");
}

/** The crosswalk's Tier-B normalization (build_works_crosswalk.py
 *  nasal_and_geminate_fold), applied on top of the plain fold: n→m, then
 *  collapse runs of one letter. Catches the anusvāra-vs-place-nasal and
 *  geminate spellings that the plain fold treats as different titles —
 *  e.g. the sheet's OCR variant "Raghuvanśa" against ACC's "raghuvamsa". */
function foldNG(key) {
  const folded = key.replace(/n/g, "m");
  let out = "";
  for (const ch of folded) if (ch !== out[out.length - 1]) out += ch;
  return out;
}

function stripHtml(s) {
  return String(s ?? "").replace(/<[^>]+>/g, " ").replace(/\\n/g, " ").replace(/\s+/g, " ").trim();
}

/** Subject sigla present in the opening of a catalogue entry.
 *
 *  Two deliberate restrictions, both learned from false positives:
 *  - CASE-SENSITIVE. ACC/NCC shelfmarks collide with subject sigla only across
 *    case: the Paris Grantha shelfmark "(Gr. I. II)" is not the grammar siglum
 *    "gr.", and "Bd."/"Bud." differ the same way. Case-insensitive matching read
 *    "taittirīyasaṃhitā¦ … Paris (Gr. I. II)" as a *grammar* text.
 *  - WINDOWED to the first 40 characters. In both catalogues the subject siglum
 *    is the first token after the headword separator; anything further in is the
 *    manuscript-reference run, where abbreviations are shelfmarks, not subjects. */
const SIGLUM_WINDOW = 40;

function siglaOf(text) {
  const head = String(text ?? "").slice(0, SIGLUM_WINDOW);
  const out = [];
  for (const [siglum, tradition] of SIGLUM_TRADITION) {
    const re = new RegExp(`(^|[\\s.,;(¦])${siglum.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`);
    if (re.test(head)) out.push({ siglum, tradition });
  }
  return out;
}

const MAX_ENTRIES_PER_KEY = 6;

function accEntry(r) {
  const body = r.body ?? "";
  return {
    catalogue: "ACC",
    id: `ACC L${r.acc_L}`,
    title: r.k2 ?? r.k1_slp1,
    body,
    sigla: siglaOf(body.includes("¦") ? body.split("¦")[1] : body)
  };
}

function nccEntry(r) {
  const body = stripHtml(r.body_html);
  return { catalogue: "NCC", id: `NCC ${r.ncc_id}`, title: r.iast, body, sigla: siglaOf(body) };
}

/** Read a JSONL catalogue, keeping records whose match_key hits either the raw
 *  or the Tier-B-folded key set. Indexed under the RAW query key so lookup is
 *  a single get. */
async function readCatalogue(file, wantRaw, wantNG, ngToRaw, makeEntry) {
  const sink = new Map();
  const full = path.join(CATALOGUE, file);
  if (!fs.existsSync(full)) {
    console.warn(`WARNING: catalogue missing: ${full} — those rows fall back to canonical attribution only.`);
    return sink;
  }
  const rl = readline.createInterface({ input: fs.createReadStream(full, { encoding: "utf8" }), crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    let r;
    try { r = JSON.parse(line); } catch { continue; }
    const mk = r.match_key;
    if (mk == null) continue;
    // Both lookups are ADDITIVE. Gating the Tier-B lookup on "the raw key
    // missed" is wrong whenever two query keys are spelling variants of one
    // title: the ACC record for `raghuvamsa` matches the sheet's `Raghuvaṃśa`
    // row raw, which would suppress its delivery to the sheet's `Raghuvanśa`
    // (OCR variant) row — exactly the row that has no raw hit of its own.
    const targets = new Set();
    if (wantRaw.has(mk)) targets.add(mk);
    if (wantNG.has(foldNG(mk))) for (const raw of ngToRaw.get(foldNG(mk)) || []) targets.add(raw);
    if (!targets.size) continue;
    const entry = makeEntry(r);
    entry.viaTierB = !wantRaw.has(mk);
    for (const t of targets) {
      if (!sink.has(t)) sink.set(t, []);
      if (sink.get(t).length < MAX_ENTRIES_PER_KEY) sink.get(t).push(entry);
    }
  }
  return sink;
}

/** ACC↔NCC pairs from the H1657 crosswalk, Tier A/B ONLY.
 *
 *  Tiers C (prefix containment) and D (edit distance) are documented in
 *  P1_COUNTS.md as "flagged for adjudication, NOT auto-merged" — that human
 *  adjudication has not happened, so consuming them here would silently import
 *  unadjudicated links as evidence. A/B are the deterministic-equality tiers.
 *
 *  A pair is what makes combining sigla across the two catalogues legitimate:
 *  an ACC hit and an NCC hit that merely share a folded title may be homonyms,
 *  but a crosswalk pair asserts they are the same work. */
async function loadCrosswalk(wantRaw, wantNG, ngToRaw) {
  const pairs = new Map();
  const full = path.join(CATALOGUE, "crosswalk_candidates.jsonl.gz");
  if (!fs.existsSync(full)) {
    console.warn(`WARNING: crosswalk missing: ${full} — ACC/NCC evidence stays unjoined.`);
    return pairs;
  }
  const rl = readline.createInterface({
    input: fs.createReadStream(full).pipe(zlib.createGunzip()),
    crlfDelay: Infinity
  });
  for await (const line of rl) {
    if (!line) continue;
    let r;
    try { r = JSON.parse(line); } catch { continue; }
    if (r.tier !== "A" && r.tier !== "B") continue;
    const targets = new Set();
    for (const mk of [r.acc_match_key, r.ncc_match_key]) {
      if (mk == null) continue;
      if (wantRaw.has(mk)) targets.add(mk);
      if (wantNG.has(foldNG(mk))) for (const raw of ngToRaw.get(foldNG(mk)) || []) targets.add(raw);
    }
    if (!targets.size) continue;
    const accBody = r.acc_body ?? "";
    const nccBody = stripHtml(r.ncc_body_html);
    const pair = {
      tier: r.tier,
      accId: `ACC L${r.acc_L}`,
      nccId: `NCC ${r.ncc_id}`,
      accTitle: r.acc_k1_slp1,
      nccTitle: r.ncc_iast,
      sigla: [
        ...siglaOf(accBody.includes("¦") ? accBody.split("¦")[1] : accBody),
        ...siglaOf(nccBody)
      ],
      accExcerpt: accBody.slice(0, 200),
      nccExcerpt: nccBody.slice(0, 200)
    };
    for (const t of targets) {
      if (!pairs.has(t)) pairs.set(t, []);
      if (pairs.get(t).length < MAX_ENTRIES_PER_KEY) pairs.get(t).push(pair);
    }
  }
  return pairs;
}

async function loadCatalogue(keys) {
  const wantRaw = new Set(keys);
  const ngToRaw = new Map();
  for (const k of keys) {
    const ng = foldNG(k);
    if (!ngToRaw.has(ng)) ngToRaw.set(ng, []);
    ngToRaw.get(ng).push(k);
  }
  const wantNG = new Set(ngToRaw.keys());
  const acc = await readCatalogue("acc.jsonl", wantRaw, wantNG, ngToRaw, accEntry);
  const ncc = await readCatalogue("ncc.jsonl", wantRaw, wantNG, ngToRaw, nccEntry);
  const pairs = await loadCrosswalk(wantRaw, wantNG, ngToRaw);
  return { acc, ncc, pairs };
}

async function main() {
  const tagRows = parseTsv(fs.readFileSync(TAGS_PATH, "utf8")).filter((r) => r.reviewed !== "yes");
  const keys = new Set(tagRows.map((r) => fold(r.canonical_text)));
  console.log(`Adjudicating ${tagRows.length} tradition rows; probing catalogue for ${keys.size} folded keys…`);
  const t0 = Date.now();
  const { acc, ncc, pairs } = await loadCatalogue(keys);
  console.log(`  catalogue probe: ${acc.size} ACC keys, ${ncc.size} NCC keys, ${pairs.size} keys with a Tier-A/B ACC↔NCC pair (${Date.now() - t0}ms)`);

  const rows = [];
  const items = [];
  const tally = { confirm: 0, correct: 0, uncertain: 0 };
  const byRule = new Map();

  for (const r of tagRows) {
    const text = r.canonical_text;
    const proposed = r.tradition;
    const key = fold(text);
    const accHits = acc.get(key) || [];
    const nccHits = ncc.get(key) || [];
    const entries = [...accHits, ...nccHits];
    const pairHits = pairs.get(key) || [];
    const traditionsSeen = [...new Set(entries.flatMap((e) => e.sigla.map((s) => s.tradition)))];
    // Traditions asserted by a crosswalk-PAIRED ACC↔NCC record. Because the
    // pair asserts same-work identity, a siglum from either side is joint
    // evidence rather than a possible homonym's.
    const pairedTraditions = [...new Set(pairHits.flatMap((p) => p.sigla.map((s) => s.tradition)))];
    const catalogues = [accHits.length ? "ACC" : null, nccHits.length ? "NCC" : null].filter(Boolean);

    const ov = OVERRIDES.get(text);
    const rule = ov?.rule ?? "canonical-attribution";
    const agentTradition = ov?.tradition ?? proposed;
    let certain = ov?.certain !== false;

    // Catalogue verdict. A crosswalk-paired corroboration is the strongest
    // class available: both catalogues, joined as the same work, agree.
    let evidenceClass;
    if (!entries.length && !pairHits.length) evidenceClass = "catalogue-absent";
    else if (pairedTraditions.includes(agentTradition)) evidenceClass = "crosswalk-pair-corroborated";
    else if (traditionsSeen.includes(agentTradition)) evidenceClass = "catalogue-corroborated";
    else if (!traditionsSeen.length && !pairedTraditions.length) evidenceClass = "catalogue-hit-no-siglum";
    else evidenceClass = "catalogue-conflict";

    // A conflict the override table did NOT anticipate is not silently
    // confirmed: it becomes a human call. This is the safety property that
    // keeps an unexamined first hit from ever deciding a row.
    let unanticipated = false;
    if (evidenceClass === "catalogue-conflict" && !ov?.homonymKnown) {
      certain = false;
      unanticipated = true;
    }

    if (!TRADITION_VOCAB.includes(agentTradition)) {
      throw new Error(`override for "${text}" produced out-of-vocabulary tradition "${agentTradition}"`);
    }

    let verdict;
    if (!certain) verdict = "uncertain";
    else if (agentTradition === proposed) verdict = "confirm";
    else verdict = "correct";
    tally[verdict] += 1;
    byRule.set(rule, (byRule.get(rule) || 0) + 1);

    const why = ov?.why
      ?? "Tradition is uncontested in the scholarly canon for this text; no competing attribution in the catalogue.";
    const evidenceNote = (entries.length || pairHits.length)
      ? `${evidenceClass}: ${entries.length} entr${entries.length === 1 ? "y" : "ies"} under folded key "${key}"`
        + (catalogues.length ? ` in ${catalogues.join("+")}` : "")
        + (pairHits.length ? `, ${pairHits.length} Tier-${[...new Set(pairHits.map((p) => p.tier))].join("/")} ACC↔NCC crosswalk pair(s)` : ", no crosswalk pair")
        + (traditionsSeen.length ? `; sigla → [${traditionsSeen.join(", ")}]` : "; no subject siglum")
        + (pairedTraditions.length ? `; paired sigla → [${pairedTraditions.join(", ")}]` : "")
        + (unanticipated ? ". Conflict was NOT anticipated by the ruling table → routed to human." : ".")
      : `catalogue-absent: no ACC/NCC entry and no crosswalk pair under folded key "${key}".`;

    rows.push({
      reviewId: text,
      canonicalText: text,
      proposedTradition: proposed,
      seedConfidence: r.confidence,
      seedNote: r.note,
      agentTradition,
      verdict,
      rule,
      certain,
      evidenceClass,
      cataloguesHit: catalogues,
      catalogueTraditions: traditionsSeen,
      crosswalkPairedTraditions: pairedTraditions,
      catalogueEntries: entries.map((e) => ({ catalogue: e.catalogue, id: e.id, title: e.title, viaTierB: !!e.viaTierB, sigla: e.sigla.map((s) => s.siglum), excerpt: e.body.slice(0, 240) })),
      crosswalkPairs: pairHits.map((p) => ({ tier: p.tier, accId: p.accId, nccId: p.nccId, accTitle: p.accTitle, nccTitle: p.nccTitle, sigla: p.sigla.map((s) => s.siglum), accExcerpt: p.accExcerpt, nccExcerpt: p.nccExcerpt })),
      why,
      evidenceNote
    });
    items.push({
      id: text,
      decision: verdict === "confirm" ? "approve" : verdict === "correct" ? "reject" : "defer",
      note: (verdict === "correct" ? `corrected-label: ${agentTradition}. ` : "") + `${why} [${evidenceNote}]`
    });
  }

  const byEvidence = {};
  for (const r of rows) byEvidence[r.evidenceClass] = (byEvidence[r.evidenceClass] || 0) + 1;
  const byProposed = {};
  for (const r of rows) {
    byProposed[r.proposedTradition] = byProposed[r.proposedTradition] || { n: 0, confirm: 0, correct: 0, uncertain: 0 };
    byProposed[r.proposedTradition].n += 1;
    byProposed[r.proposedTradition][r.verdict] += 1;
  }

  const packet = {
    schemaVersion: "1.0.0",
    handoff: HANDOFF,
    sheetId: "csl-atlas-tradition-tags_119texts",
    reviewer: REVIEWER,
    evidenceLabel: "agent-adjudicated",
    source: {
      tags: "data/citations/tradition_tags.tsv",
      catalogue: "../SanskritLexicography/HeadwordLists/works_catalogue/{acc,ncc}.jsonl (H1657 P0, read-only)",
      crosswalk: "../SanskritLexicography/HeadwordLists/works_catalogue/crosswalk_candidates.jsonl.gz (H1657 P1, Tier A/B only)",
      vocabulary: "TRADITION_VOCAB in scripts/build-tradition-tags.mjs"
    },
    method: {
      match: "NFD-stripped lowercase a–z fold of canonical_text against ACC and NCC match_key, plus the crosswalk's Tier-B nasal/geminate fold as a secondary key",
      catalogueUse: "BOTH catalogues are probed for every row, and joined through the H1657 ACC↔NCC crosswalk at Tier A/B. Tiers C (prefix) and D (edit distance) are excluded: P1_COUNTS.md marks them 'flagged for adjudication, not auto-merged', and that adjudication has not run.",
      siglumWindow: SIGLUM_WINDOW,
      caveat: "Title-only matching is homonym-dense; a hit corroborates only when its subject siglum agrees with the ruled tradition, and an unanticipated conflict demotes the row to human review. Sigla from an ACC entry and an NCC entry may only be pooled as one work's evidence when a crosswalk pair asserts they ARE one work.",
      rules: [
        "canonical-attribution (default) — uncontested tradition, catalogue corroborates where present",
        "not-a-work → other",
        "generic-tradition-label → the tradition the label itself names",
        "commentator-follows-base-text → tradition of the base text",
        "ocr-variant → tradition of the row it is a variant of",
        "homonym-conflict-canonical-stands → catalogue hit is a different same-titled work, recorded",
        "nearest-bucket-vocabulary-gap → closed vocabulary has no exact slot",
        "policy-fork-* / author-ambiguous-* → not agent-decidable, human arm"
      ]
    },
    counts: {
      rows: rows.length,
      ...tally,
      byRule: Object.fromEntries([...byRule.entries()].sort((a, b) => b[1] - a[1])),
      byEvidenceClass: byEvidence,
      byProposedTradition: byProposed
    },
    rows
  };

  fs.writeFileSync(PACKET_PATH, `${JSON.stringify(packet, null, 2)}\n`);
  fs.mkdirSync(path.dirname(DECISIONS_PATH), { recursive: true });
  fs.writeFileSync(
    DECISIONS_PATH,
    `${JSON.stringify({ sheet_id: "csl-atlas-tradition-tags_119texts", handoff: HANDOFF, reviewer: REVIEWER, items }, null, 2)}\n`
  );

  console.log(`Wrote ${path.relative(ROOT, PACKET_PATH)}`);
  console.log(`Wrote ${path.relative(ROOT, DECISIONS_PATH)} (${items.length} items)`);
  console.log(`confirm=${tally.confirm} correct=${tally.correct} uncertain=${tally.uncertain}`);
  console.log("by evidence class:");
  for (const [k, v] of Object.entries(byEvidence).sort((a, b) => b[1] - a[1])) console.log(`  ${k}: ${v}`);
  console.log("by rule:");
  for (const [k, v] of [...byRule.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${k}: ${v}`);
  const human = rows.filter((r) => r.verdict === "uncertain");
  console.log(`human-owed (${human.length}):`);
  for (const r of human) console.log(`  ${r.canonicalText} [${r.proposedTradition}] — ${r.rule}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
