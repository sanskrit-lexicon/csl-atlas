// Observable Framework config for csl-atlas
// https://observablehq.com/framework/config

import { execSync } from "node:child_process";

// Production origin for canonical / Open Graph URLs (GitHub Pages).
const ORIGIN = "https://sanskrit-lexicon.github.io/csl-atlas";

// Real build identity for the site footer. `{sha}` used to ship as a literal,
// unsubstituted placeholder (Observable Framework's `footer` option is a plain
// string — it never interpolates it). GITHUB_SHA is set by Actions; the local
// git HEAD is the fallback for `npm run dev`/`build` outside CI.
function buildSha() {
  const sha = process.env.GITHUB_SHA || execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  return sha ? sha.slice(0, 7) : "unknown";
}
const BUILD_SHA = (() => { try { return buildSha(); } catch { return "unknown"; } })();
const BUILD_DATE = new Date().toISOString().slice(0, 10);
const FOOTER =
  `<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem">` +
  `<span>Source: CDSL · CC-BY-SA-4.0 · build ${BUILD_SHA} (${BUILD_DATE})</span>` +
  `<span>Atlas tooling: Dr. Mārcis Gasūns</span>` +
  `</div>`;

// Fallback description for any route without a PAGE_DESCRIPTIONS entry.
const DEFAULT_DESCRIPTION =
  "An interactive digital-humanities atlas of the Cologne Digital Sanskrit Lexicon (CDSL): " +
  "compare, trace, and explore historical Sanskrit dictionaries from Monier-Williams and the " +
  "Petersburg Wörterbücher to the classical koshas — coverage, overlap, genealogy, and sense structure.";

// Per-page meta descriptions, keyed by route. Observable Framework drops any
// non-whitelisted front-matter key (no `description:`), so descriptions live
// here in the config rather than in each page's front matter.
const PAGE_DESCRIPTIONS = {
  "/": "An interactive digital-humanities atlas of the Cologne Digital Sanskrit Lexicon (CDSL): compare, trace, and explore historical Sanskrit dictionaries from Monier-Williams to the koshas.",
  "/dictionary-chooser": "Which Cologne Sanskrit dictionary should you use? A guided chooser from your goal to the right CDSL dictionary, starting from Monier-Williams.",
  "/research-desk": "Student research desk: a reliable path from a Sanskrit word to trustworthy dictionary evidence across the Cologne Digital Sanskrit Lexicon.",
  "/student-lessons": "Student lesson track: short classroom exercises built on the atlas's Cologne Sanskrit dictionary tools.",
  "/researcher-dashboard": "The atlas working surface for researcher-builders: entry points into every Cologne Sanskrit dictionary comparison and review tool.",
  "/evidence-bridges": "Which nearby Sanskrit research repositories feed the atlas — a map of the evidence sources behind its Cologne dictionary comparisons.",
  "/tools/reader-lookup": "Reader lookup: type a Sanskrit word and read it across the Cologne Digital Sanskrit Lexicon dictionaries side by side.",
  "/tools/learner-reading-layer": "Learner's reading layer: a graded reading aid over the Cologne Sanskrit dictionaries for students working through a text.",
  "/tools/dictionary-dossier": "Lemma dossier: a single Sanskrit headword assembled across every Cologne dictionary with senses, gender, and source citations.",
  "/tools/mw-depth-dashboard": "Synchronic anatomy of Monier-Williams (1899): article types, counts, and structure generated deterministically from the CDSL source.",
  "/tools/mw-diachronic-layers": "A conservative view of which source layers Monier-Williams entries cite — coarse comparison buckets, not dates.",
  "/tools/mw-family-depth": "The deepest lexical families in Monier-Williams, ranked by a composite depth score over shared word bases.",
  "/tools/typology-treemap": "The composition of Monier-Williams's 286,561 records by article type, as a squarified treemap.",
  "/tools/dictionary-coverage-matrix": "Headword coverage across the eligible Cologne Sanskrit/BHS dictionaries, grouped by normalized headword, with a legacy Core 7 scope.",
  "/tools/dictionary-overlap": "How much vocabulary each pair of Cologne Sanskrit dictionaries shares, by normalized headword.",
  "/tools/dictionary-conflicts": "Lemmas where two Cologne dictionaries assert disjoint grammatical genders — review candidates with source links, not verdicts.",
  "/tools/dictionary-homonyms": "Where Cologne dictionaries disagree on how many homonyms a Sanskrit lemma has — one splits an entry another keeps whole.",
  "/tools/dictionary-citations": "How heavily each Cologne Sanskrit dictionary cites sources, how broad its apparatus is, and what it cites most.",
  "/tools/citation-canon": "The shared citation canon across Cologne Sanskrit dictionaries as a dict×text matrix — is it a nested core–periphery or disjoint tradition communities (PH1 CANON-CORE, NODF + bipartite modularity vs permutation nulls).",
  "/tools/dictionary-senses": "Which Cologne Sanskrit dictionary treats a lemma's senses most richly, measured by structural sense divisions.",
  "/tools/lexicography": "Dictionary genealogy: first empirical findings on how the Cologne Sanskrit dictionaries descend from one another, derived from canonical headword data.",
  "/tools/lexicographic-conventions": "Convention fingerprints: how the Cologne Sanskrit dictionaries relate by house style — orthographic and citation formatting — as a cladogram.",
  "/tools/structural-register": "Structural register scatter (H6): whether citation style plus grammar marking predicts a Cologne dictionary's family.",
  "/tools/semantic-fields": "Semantic fields (H4): whether the Cologne Sanskrit dictionaries show measurable topical coverage profiles.",
  "/tools/xref-lineage": "Cross-reference lineage (M6): whether dictionary-internal cross-reference graphs preserve lexicographic lineage.",
  "/tools/r2-explorer": "R2 sense explorer: browse cross-dictionary sense structure across the Cologne Sanskrit lexicons.",
  "/tools/r2-h1": "R2 sense granularity: how finely the Cologne Sanskrit dictionaries subdivide senses (hypothesis H1).",
  "/tools/r2-h2h3": "R2 sense survival and drift: how senses persist or change across the Cologne Sanskrit dictionaries (hypotheses H2–H3).",
  "/tools/review-gender-conflicts": "Review queue: cross-dictionary gender disagreements among the tagged Cologne dictionaries, as candidates for human judgment.",
  "/tools/review-source-layers": "Review queue: Monier-Williams source abbreviations not yet mapped to a diachronic layer, cited at least five times.",
  "/tools/review-alignment": "Alignment confidence: how confidently lemmas align across the seven core Cologne dictionaries, and the queue that doesn't align cleanly.",
  "/tools/review-source-siglum": "Review queue: source sigla cited by only one tagged Cologne dictionary — genuinely unique, or the same source under different aliases.",
  "/tools/sense-divergence": "Cross-dict entry-coverage divergence: which Sanskrit headwords each Cologne dictionary treats very differently from its peers.",
  "/tools/h4-review": "H4 semantic-field review: per dictionary and Amarakośa field, whether an apparent coverage anomaly is real or an artifact.",
  "/tools/cross-dict": "Cross-dictionary comparison: nine Cologne dictionaries on a format-robust common-block vocabulary, showing citation density and structure.",
  "/tools/dictionary-coverage": "All-dictionary coverage: the nine-chapter comparison extended to every CDSL v02 dictionary with a main source file.",
  "/tools/matrix-explorer": "Matrix explorer: an 18×14 block-by-article-type heatmap of Monier-Williams, with per-cell counts and filtering.",
  "/tools/lineage-sankey": "Lineage Sankey: the visual evidence for the kosha-collapse finding — PWG source labels flowing into Monier-Williams's single hedge.",
  "/tools/timeline": "Lexicographic timeline: from the indigenous kośa tradition (~6th c.) to the Cologne Digital Sanskrit Lexicon.",
  "/tools/type-comparator": "Type comparator: pick two Monier-Williams article types and compare their block profiles side by side.",
  "/tools/citation-tracer": "Citation tracer: trace source citations across the Cologne Sanskrit dictionaries (Tier-3 tool, in progress).",
  "/paper/grounded": "The grounded framework: the atlas paper's body, building its analysis from Monier-Williams's own data before any external theory.",
  "/paper/triangulation": "Triangulation (§7): how three analytic frameworks converge on the atlas's findings about the Cologne Sanskrit dictionaries.",
  "/paper/appendices": "Framework appendices A·B·C: three external-framework treatments condensed as appendices to the atlas paper.",
  "/paper/related-work": "Related work: where the atlas sits in the Sanskrit digitisation pipeline relative to current machine-readable dictionary efforts.",
  "/dicts/mw": "MW — Monier-Williams Sanskrit-English Dictionary (1899): an atlas chapter on its structure, sources, and place among the Cologne dictionaries.",
  "/dicts/pwg": "PWG — the Grosses Petersburger Wörterbuch (1855–1875): an atlas chapter on its structure and lineage within the Cologne dictionaries.",
  "/dicts/pwk": "PWK — Sanskrit-Wörterbuch in kürzerer Fassung (1879–1889): an atlas chapter on this shorter Petersburg dictionary.",
  "/dicts/ap": "AP — Apte's Practical Sanskrit-English Dictionary (1890/1957): an atlas chapter on its structure and sources.",
  "/dicts/wil": "WIL — Wilson's Dictionary in Sanscrit and English (1832): an atlas chapter on this early Cologne dictionary.",
  "/dicts/ben": "BEN — Benfey's Sanskrit-English Dictionary (1866): an atlas chapter on its structure and sources.",
  "/dicts/cae": "CAE — Cappeller's Sanskrit-English Dictionary (1891): an atlas chapter on its structure and sources.",
  "/dicts/skd": "SKD — Śabdakalpadruma (1822–1858): an atlas chapter on this classical Sanskrit encyclopaedic kosha.",
  "/dicts/vcp": "VCP — Vācaspatyam (1873–1884): an atlas chapter on this classical Sanskrit encyclopaedic kosha.",
  "/dicts/armh": "ARMH — Abhidhānaratnamālā (Halāyudhakośa, ~10th c.): an atlas chapter on this classical Sanskrit synonymic kosha.",
  "/dicts/abch": "ABCH — Abhidhānacintāmaṇi (~12th c.): an atlas chapter on Hemacandra's classical Sanskrit synonymic kosha."
};

// Escape a string for safe interpolation into an HTML attribute value.
const attr = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// Per-page <head>: SEO tags (canonical, description, Open Graph, Twitter) plus
// the site's existing PWA/favicon/stylesheet markup and service-worker
// registration. Receives {title, data, path} from Observable Framework.
const head = ({title, data, path}) => {
  const canonicalPath = path === "/index" || path === "/" ? "/" : path;
  const url = ORIGIN + canonicalPath;
  const pageTitle = (data && data.title) || title || "Atlas of the Cologne Digital Sanskrit Lexicons";
  const description = PAGE_DESCRIPTIONS[canonicalPath] || DEFAULT_DESCRIPTION;
  const image = ORIGIN + "/atlas-card.png"; // 1200×630, scripts/make_social_card.py
  return `<meta name="description" content="${attr(description)}">
<link rel="canonical" href="${attr(url)}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#1f78b4">
<meta name="author" content="Cologne Digital Sanskrit Lexicon project (sanskrit-lexicon)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Atlas of the Cologne Digital Sanskrit Lexicons">
<meta property="og:locale" content="en">
<meta property="og:title" content="${attr(pageTitle)}">
<meta property="og:description" content="${attr(description)}">
<meta property="og:url" content="${attr(url)}">
<meta property="og:image" content="${attr(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Atlas of the Cologne Digital Sanskrit Lexicons">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${attr(pageTitle)}">
<meta name="twitter:description" content="${attr(description)}">
<meta name="twitter:image" content="${attr(image)}">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="favicon.svg">
<link rel="icon" href="favicon.svg">
<link rel="stylesheet" href="palette.css">
<link rel="stylesheet" href="premium.css">
<script>if ("serviceWorker" in navigator) { window.addEventListener("load", () => { let swPath = "/sw.js"; if (window.location.hostname.includes("github.io")) { swPath = "/csl-atlas/sw.js"; } navigator.serviceWorker.register(swPath); }); }</script>`;
};

export default {
  root: "src",
  title: "Atlas of the Cologne Digital Sanskrit Lexicons",
  pages: [
    {
      name: "Overview",
      path: "/"
    },
    {
      name: "Research paths",
      pages: [
        { name: "Student research desk", path: "/research-desk" },
        { name: "Student lesson track", path: "/student-lessons" },
        { name: "Researcher dashboard", path: "/researcher-dashboard" },
        { name: "Evidence bridges", path: "/evidence-bridges" },
        { name: "Which dictionary?", path: "/dictionary-chooser" },
        { name: "Reader lookup", path: "/tools/reader-lookup" }
      ]
    },
    {
      name: "Reader mode",
      pages: [
        { name: "Reader lookup", path: "/tools/reader-lookup" },
        { name: "Learner's reading layer", path: "/tools/learner-reading-layer" },
        { name: "Lemma dossier", path: "/tools/dictionary-dossier" }
      ]
    },
    {
      name: "MW depth (Phase 1)",
      pages: [
        { name: "Depth dashboard", path: "/tools/mw-depth-dashboard" },
        { name: "Diachronic layers", path: "/tools/mw-diachronic-layers" },
        { name: "Family depth", path: "/tools/mw-family-depth" },
        { name: "Typology treemap", path: "/tools/typology-treemap" }
      ]
    },
    {
      name: "Dictionary comparison (Phase 2)",
      pages: [
        { name: "Coverage matrix", path: "/tools/dictionary-coverage-matrix" },
        { name: "Pairwise overlap", path: "/tools/dictionary-overlap" },
        { name: "Gender conflicts", path: "/tools/dictionary-conflicts" },
        { name: "Homonym splits", path: "/tools/dictionary-homonyms" },
        { name: "Citation apparatus", path: "/tools/dictionary-citations" },
        { name: "Citation canon", path: "/tools/citation-canon" },
        { name: "Sense depth", path: "/tools/dictionary-senses" },
        { name: "Lemma dossier", path: "/tools/dictionary-dossier" }
      ]
    },
    {
      name: "Dictionary structure",
      pages: [
        { name: "Dictionary genealogy", path: "/tools/lexicography" },
        { name: "Convention fingerprints", path: "/tools/lexicographic-conventions" },
        { name: "Structural register", path: "/tools/structural-register" },
        { name: "Semantic fields", path: "/tools/semantic-fields" },
        { name: "Cross-reference lineage", path: "/tools/xref-lineage" },
        { name: "R2 sense explorer", path: "/tools/r2-explorer" },
        { name: "R2 sense granularity", path: "/tools/r2-h1" },
        { name: "R2 survival and drift", path: "/tools/r2-h2h3" }
      ]
    },
    {
      name: "Review queues",
      pages: [
        { name: "Gender conflicts", path: "/tools/review-gender-conflicts" },
        { name: "Source layers", path: "/tools/review-source-layers" },
        { name: "Alignment confidence", path: "/tools/review-alignment" },
        { name: "Source-siglum aliases", path: "/tools/review-source-siglum" },
        { name: "Cross-dict divergence", path: "/tools/sense-divergence" },
        { name: "H4 semantic fields", path: "/tools/h4-review" }
      ]
    },
    {
      name: "Atlas figures",
      pages: [
        { name: "Cross-dictionary comparison", path: "/tools/cross-dict" },
        { name: "All-dictionary coverage", path: "/tools/dictionary-coverage" },
        { name: "Matrix explorer", path: "/tools/matrix-explorer" },
        { name: "Lineage Sankey", path: "/tools/lineage-sankey" },
        { name: "Lexicographic timeline", path: "/tools/timeline" },
        { name: "Type comparator", path: "/tools/type-comparator" },
        { name: "Citation tracer", path: "/tools/citation-tracer" }
      ]
    },
    {
      name: "Paper",
      pages: [
        { name: "Grounded framework (body)", path: "/paper/grounded" },
        { name: "Triangulation (§7)", path: "/paper/triangulation" },
        { name: "Framework appendices A·B·C", path: "/paper/appendices" },
        { name: "Related work & positioning", path: "/paper/related-work" }
      ]
    },
    {
      name: "Dictionaries",
      pages: [
        { name: "MW (Monier-Williams 1899)", path: "/dicts/mw" },
        { name: "PWG (Petersburg Wörterbuch)", path: "/dicts/pwg" },
        { name: "PWK (Kürzerer Fassung)", path: "/dicts/pwk" },
        { name: "AP (Apte 1957)", path: "/dicts/ap" },
        { name: "WIL (Wilson 1832)", path: "/dicts/wil" },
        { name: "BEN (Benfey 1866)", path: "/dicts/ben" },
        { name: "CAE (Cappeller 1891)", path: "/dicts/cae" },
        { name: "SKD (Śabdakalpadruma)", path: "/dicts/skd" },
        { name: "VCP (Vācaspatya)", path: "/dicts/vcp" },
        { name: "ARMH (Halāyudha)", path: "/dicts/armh" },
        { name: "ABCH (Hemacandra)", path: "/dicts/abch" }
      ]
    }
  ],
  footer: FOOTER,
  head,
  theme: "wide",
  toc: true,
  search: true
};
