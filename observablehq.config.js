// Observable Framework config for csl-atlas
// https://observablehq.com/framework/config

export default {
  root: "src",
  title: "Atlas of the Cologne Digital Sanskrit Lexicons",
  pages: [
    {
      name: "Overview",
      path: "/"
    },
    {
      name: "Which dictionary?",
      path: "/dictionary-chooser"
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
        { name: "Cross-dict divergence", path: "/tools/sense-divergence" }
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
  footer: "Source: CDSL · CC-BY-SA-4.0 · build {sha}",
  head: '<meta name="description" content="Atlas of the Cologne Digital Sanskrit Lexicons (CDSL). An interactive digital humanities exploration of historical Sanskrit dictionaries including Monier-Williams, PWG, and PWK."><meta name="theme-color" content="#1f78b4"><link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="favicon.svg"><link rel="icon" href="favicon.svg"><link rel="stylesheet" href="palette.css"><link rel="stylesheet" href="premium.css"><script>if ("serviceWorker" in navigator) { window.addEventListener("load", () => { let swPath = "/sw.js"; if (window.location.hostname.includes("github.io")) { swPath = "/csl-atlas/sw.js"; } navigator.serviceWorker.register(swPath); }); }</script>',
  theme: "wide",
  toc: true,
  search: true
};
