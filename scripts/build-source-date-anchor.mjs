// Source-date anchoring (Month 3) — review layer.
//
// Deepens #90 (which gave 6 coarse layer date-bands) to the PER-SIGLUM level: it
// joins the committed Dharmamitra chronology snapshot
// (src/data/external/dharmamitra-chronology.json, 1,618 dated works) to the
// individual <ls> source sigla the atlas tracks — the 184 mapped sigla
// (mw-source-layers.json) and the 449 `unknown` ones
// (unknown-source-layers-review.json) — and attaches, per siglum it can
// confidently resolve to a dated work, both a concrete DATE and the source's
// CORPUS VOLUME (nChunks + a 1-5 band) in the Dharmamitra dated corpus.
//
// The corpus-volume band is corpus-frequency at the SOURCE level. Per-LEMMA
// frequency is NOT added here — the atlas already carries it via DCS
// (dcs_lemma_summary.json), and dharmanexus-sanskrit is raw corpus text with no
// committable per-lemma frequency export, so re-deriving it would duplicate DCS.
//
// Deliberately date-only. The atlas's source LAYERS mix chronology
// (vedic/epic/classical/puranic) with genre (technical/lexicographic), so a
// model date cannot be mapped to a layer — Āryabhaṭīya is `technical` AND
// classical-dated, which is no contradiction. The date is the value-add; the
// reviewer decides any layer for the unknowns (the date informs it).
//
// Bridge: siglum -> canonical name (curated expansion of major Vedic/epic sigla,
// then dict-source-aliases.json) -> match chronology work titles. Matching is
// EXACT or unambiguous-long-prefix only (a wrong date is worse than no date).
// Chronology dates are posterior estimates; review evidence only, never rewrites
// mw-source-layers.json. Authorial chronology (the cited text) is distinct from
// MW's editorial date. No model call at build time.
//
// Usage: npm run build-source-date-anchor.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const ROOT = process.cwd();
const CHRONOLOGY = path.resolve(ROOT, "src", "data", "external", "dharmamitra-chronology.json");
const LAYERS = path.resolve(ROOT, "src", "data", "mw-source-layers.json");
const UNKNOWNS = path.resolve(ROOT, "src", "data", "review", "unknown-source-layers-review.json");
const ALIASES = path.resolve(ROOT, "src", "data", "dict-source-aliases.json");
const OUTPUT = path.resolve(ROOT, "src", "data", "review", "source-date-anchor-review.json");

const MW_HREF = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt";

// Curated expansion for major MW sigla the (lit-focused) alias table lacks.
const SIGLUM_EXPANSION = {
  RV: "Ṛgveda", AV: "Atharvaveda", VS: "Vājasaneyisaṃhitā", TS: "Taittirīyasaṃhitā",
  "ŚBr": "Śatapathabrāhmaṇa", AB: "Aitareyabrāhmaṇa", "AitBr": "Aitareyabrāhmaṇa",
  "TBr": "Taittirīyabrāhmaṇa", "ChUp": "Chāndogya-Upaniṣad", "BĀrUp": "Bṛhadāraṇyaka-Upaniṣad",
  MBh: "Mahābhārata", R: "Rāmāyaṇa", Mn: "Manusmṛti", "BhG": "Bhagavadgītā", "Bhag": "Bhagavadgītā",
  Ragh: "Raghuvaṃśa", Megh: "Meghadūta", Kum: "Kumārasambhava", "KSS": "Kathāsaritsāgara",
  "Kathās": "Kathāsaritsāgara", "BhP": "Bhāgavata-purāṇa", VP: "Viṣṇupurāṇa", Yogas: "Yogasūtra",
  Nyāyas: "Nyāyasūtra", "Pañcat": "Pañcatantra"
};

function norm(s) {
  return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
}
function median(xs) {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  const mid = s.length >> 1;
  return s.length % 2 ? s[mid] : Math.round((s[mid - 1] + s[mid]) / 2);
}
function mode(xs) {
  const c = new Map();
  for (const x of xs) c.set(x, (c.get(x) || 0) + 1);
  return [...c.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
}
// Corpus-volume band from the Dharmamitra dated corpus chunk count (log-scale,
// 1–5 to mirror the DCS per-lemma frequency bands). Source-level, NOT per-lemma:
// per-lemma frequency stays with the existing DCS layer (dcs_lemma_summary.json).
function corpusBand(chunks) {
  if (!chunks) return 0;
  if (chunks >= 1000) return 5;
  if (chunks >= 100) return 4;
  if (chunks >= 10) return 3;
  if (chunks >= 2) return 2;
  return 1;
}

function main() {
  const chronology = JSON.parse(fs.readFileSync(CHRONOLOGY, "utf8"));
  const layers = JSON.parse(fs.readFileSync(LAYERS, "utf8"));
  const unknownsDoc = JSON.parse(fs.readFileSync(UNKNOWNS, "utf8"));
  const aliasDoc = JSON.parse(fs.readFileSync(ALIASES, "utf8"));

  // 1. Chronology index: normalised base name -> aggregated dated sections.
  const chrono = new Map();
  for (const w of chronology.works) {
    if (!Number.isFinite(w.postMedian)) continue;
    const base = w.title.split(/[:(\[]/)[0].trim();
    const key = norm(base);
    if (!key) continue;
    let e = chrono.get(key);
    if (!e) { e = { base, dates: [], eras: [], sections: 0, chunks: 0 }; chrono.set(key, e); }
    e.dates.push(w.postMedian); e.eras.push(w.eraKey); e.sections += 1;
    e.chunks += Number.isFinite(w.nChunks) ? w.nChunks : 0;
  }

  // 2. siglum (lowercased) -> canonical name, from the alias table.
  const aliasName = new Map();
  for (const [k, v] of Object.entries(aliasDoc.canonical || {})) {
    aliasName.set(k.toLowerCase(), v.name);
    for (const a of v.aliases || []) aliasName.set(a.toLowerCase(), v.name);
  }

  // Resolve a siglum to a chronology entry — EXACT match first (any source),
  // then an unambiguous prefix (>=5 chars, exactly one chronology base). A wrong
  // date is worse than none, so loose/ambiguous prefixes are rejected.
  function resolve(siglum) {
    const tried = [];
    if (SIGLUM_EXPANSION[siglum]) tried.push({ name: SIGLUM_EXPANSION[siglum], via: "expansion" });
    if (aliasName.has(siglum.toLowerCase())) tried.push({ name: aliasName.get(siglum.toLowerCase()), via: "alias" });
    tried.push({ name: siglum, via: "siglum" });

    for (const t of tried) {
      const n = norm(t.name);
      if (n.length >= 3 && chrono.has(n)) return { entry: chrono.get(n), via: t.via, name: t.name, confidence: "high" };
    }
    for (const t of tried) {
      const n = norm(t.name);
      if (n.length < 5) continue;
      const hits = [...chrono.entries()].filter(([k]) => k.startsWith(n));
      if (hits.length === 1) return { entry: hits[0][1], via: t.via, name: t.name, confidence: "medium" };
    }
    return null;
  }

  // 3. Collect sigla: mapped (current layer + line) + unknown.
  const sigla = new Map();
  for (const [s, layer] of Object.entries(layers.map || {})) sigla.set(s, { siglum: s, currentLayer: layer });
  for (const it of unknownsDoc.items || []) {
    const s = it.subject?.source ?? it.machineValue?.source;
    if (!s) continue;
    sigla.set(s, { siglum: s, currentLayer: "unknown", line: it.sourcePointers?.[0]?.line ?? null, frequency: it.machineValue?.frequency ?? null });
  }

  const preserved = loadPreserved(OUTPUT);
  const items = [];
  let preservedCount = 0;
  const stat = { mappedMatched: 0, mappedTotal: 0, unknownMatched: 0, unknownTotal: 0, high: 0, medium: 0 };

  for (const meta of [...sigla.values()].sort((a, b) => a.siglum.localeCompare(b.siglum))) {
    const isUnknown = meta.currentLayer === "unknown";
    if (isUnknown) stat.unknownTotal += 1; else stat.mappedTotal += 1;
    const r = resolve(meta.siglum);
    if (!r) continue;
    if (isUnknown) stat.unknownMatched += 1; else stat.mappedMatched += 1;
    stat[r.confidence] += 1;

    const reviewId = `source-date-anchor:${meta.siglum}`;
    if (preserved.has(reviewId)) preservedCount += 1;
    const pointers = [];
    if (meta.line) pointers.push({ dictionary: "MW", line: meta.line, href: `${MW_HREF}#L${meta.line}` });
    pointers.push({ dictionary: "Dharmamitra dating", line: null, href: "https://github.com/dharmamitra/sanskrit-dating" });

    items.push({
      reviewId,
      queue: "source-date-anchor",
      subject: { kind: "source-abbreviation", source: meta.siglum, lemma: null, dictionaries: ["MW"] },
      sourcePointers: pointers,
      machineValue: {
        siglum: meta.siglum,
        currentLayer: meta.currentLayer,
        matchedWork: r.entry.base,
        matchVia: r.via,
        matchConfidence: r.confidence,
        datedSections: r.entry.sections,
        dateMedian: median(r.entry.dates),
        dateRange: [Math.min(...r.entry.dates), Math.max(...r.entry.dates)],
        chronologicalEra: mode(r.entry.eras),
        corpusChunks: r.entry.chunks,
        corpusVolumeBand: corpusBand(r.entry.chunks),
        verdict: isUnknown ? "date-proposed (unknown source)" : "date-anchored"
      },
      evidenceLevel: "inferred", // chronology is a model posterior
      ...reviewFields(preserved, reviewId)
    });
  }

  const payload = reviewPayload({
    queue: "source-date-anchor",
    sourcePath: "src/data/external/dharmamitra-chronology.json + src/data/mw-source-layers.json + unknown-source-layers-review.json",
    items,
    extra: {
      chronologyWorks: chronology.workCount, distinctChronologyTexts: chrono.size, ...stat,
      unknownDateProposals: stat.unknownMatched
    },
    assumptions: [
      "A siglum is dated by resolving it to a canonical name (curated expansion of major sigla, then dict-source-aliases.json, then the siglum) and matching chronology work titles — EXACT or unambiguous >=5-char prefix only.",
      "dateMedian is the median postMedian over the matched work's dated sections; dateRange is the span; chronologicalEra is the modal era.",
      "corpusChunks / corpusVolumeBand (1-5, log-scale) is the source's text volume in the Dharmamitra dated corpus — corpus-frequency at the SOURCE level. Per-LEMMA frequency stays with the existing DCS layer (dcs_lemma_summary.json); dharmanexus exposes no committable per-lemma frequency, so this avoids duplicating DCS.",
      "Date-only by design: atlas layers mix chronology with genre (technical/lexicographic), so a date does NOT imply a layer. For unknown sigla the date informs the reviewer's layer choice; it is not applied automatically.",
      "Chronology dates are posterior model estimates; review evidence only — never rewrites mw-source-layers.json. Reviews preserved by reviewId."
    ],
    warnings: [
      `Coverage: ${stat.mappedMatched}/${stat.mappedTotal} mapped and ${stat.unknownMatched}/${stat.unknownTotal} unknown sigla dated (${stat.high} high-confidence exact, ${stat.medium} medium-confidence prefix). Most unmatched unknowns are commentaries/minor texts absent from the dating corpus.`,
      "Verify each anchor — a wrong name match yields a wrong date. Authorial chronology (the cited text) is distinct from MW's editorial date.",
      "Sectioned works (e.g. Mahābhārata, Ṛgveda) are aggregated by base title; dateRange shows the section spread."
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} source-date-anchor items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(ROOT, OUTPUT)}`);
  console.log(`  mapped ${stat.mappedMatched}/${stat.mappedTotal} | unknown ${stat.unknownMatched}/${stat.unknownTotal} | high ${stat.high} medium ${stat.medium}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
