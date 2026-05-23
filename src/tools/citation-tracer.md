---
title: Citation tracer
---

# Citation tracer

*(Tier 3 tool — placeholder. Requires per-source entry-index data not yet exported.)*

The plan: click an `<ls>` source (e.g. `RV.`, `MBh.`, `L.`), see all MW entries citing it. Filter by article type. Cross-reference to the actual textual passages where possible.

**Data prerequisite:** export `data/source-to-entries.json` — keyed by source label, valued as list of `<L>` record numbers. Currently not generated; would require a separate Python pass over `mw.txt`.

## See also

- 🔗 [Top-25 source list with Wikipedia identities](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md#top-25-most-cited-sources) (static reference)
- 🔗 [`<ls>` coverage stats](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md#coverage-of-ls-citations) — 311,932 citations / 821 unique labels
- 🔗 [Top orphan abbreviations](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md#top-orphan-abbreviations) — sources used but lacking authority records

---

*Tier 3 tool. Will land in a later iteration.*
