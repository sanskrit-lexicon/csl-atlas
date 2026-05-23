// Observable Framework config for csl-atlas
// https://observablehq.com/framework/config

export default {
  title: "Atlas of the Cologne Digital Sanskrit Lexicons",
  pages: [
    {
      name: "Overview",
      path: "/"
    },
    {
      name: "Papers",
      pages: [
        { name: "Wiegand", path: "/papers/wiegand" },
        { name: "Atkins–Rundell", path: "/papers/atkins-rundell" },
        { name: "Hausmann–Wiegand", path: "/papers/hausmann" },
        { name: "Grounded", path: "/papers/grounded" }
      ]
    },
    {
      name: "Tools",
      pages: [
        { name: "Matrix explorer", path: "/tools/matrix-explorer" },
        { name: "Lineage Sankey", path: "/tools/lineage-sankey" },
        { name: "Typology treemap", path: "/tools/typology-treemap" },
        { name: "Lexicographic timeline", path: "/tools/timeline" },
        { name: "Type comparator", path: "/tools/type-comparator" },
        { name: "Citation tracer", path: "/tools/citation-tracer" }
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
