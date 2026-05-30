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
      name: "Corpus (Phase 3)",
      pages: [
        { name: "DCS corpus inventory", path: "/tools/dcs-corpus-inventory" }
      ]
    },
    {
      name: "Review queues",
      pages: [
        { name: "Gender conflicts", path: "/tools/review-gender-conflicts" },
        { name: "Source layers", path: "/tools/review-source-layers" },
        { name: "Alignment confidence", path: "/tools/review-alignment" },
        { name: "Source-siglum aliases", path: "/tools/review-source-siglum" }
      ]
    },
    {
      name: "Interoperability & figures",
      pages: [
        { name: "Cross-dictionary comparison", path: "/tools/cross-dict" },
        { name: "All-dictionary coverage", path: "/tools/dictionary-coverage" },
        { name: "Matrix explorer", path: "/tools/matrix-explorer" },
        { name: "Lineage Sankey", path: "/tools/lineage-sankey" },
        { name: "Lexicographic timeline", path: "/tools/timeline" },
        { name: "Type comparator", path: "/tools/type-comparator" },
        { name: "Citation tracer", path: "/tools/citation-tracer" },
        { name: "Interoperability hard cases", path: "/tools/interoperability-hard-cases" }
      ]
    },
    {
      name: "Paper",
      pages: [
        { name: "Grounded framework (body)", path: "/paper/grounded" },
        { name: "Triangulation (§7)", path: "/paper/triangulation" },
        { name: "Framework appendices A·B·C", path: "/paper/appendices" }
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
        { name: "SKD (Śabdakalpadruma)", path: "/dicts/skd" },
        { name: "VCP (Vācaspatya)", path: "/dicts/vcp" },
        { name: "ARMH (Halāyudha)", path: "/dicts/armh" },
        { name: "ABCH (Hemacandra)", path: "/dicts/abch" }
      ]
    }
  ],
  footer: "Source: CDSL · CC-BY-SA-4.0 · build {sha}",
  head: '<link rel="icon" href="favicon.svg"><link rel="stylesheet" href="palette.css">',
  theme: "wide",
  toc: true,
  search: true
};
