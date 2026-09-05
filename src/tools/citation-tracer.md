_Created: 23-05-2026 · Last updated: 05-09-2026_

---
title: Citation tracer
---

# Citation tracer

*(Tier 3 tool — placeholder. Requires per-source entry-index data not yet exported.)*

The plan: click an `<ls>` source (e.g. `RV.`, `MBh.`, `L.`), see all MW entries citing it. Filter by article type. Cross-reference to the actual textual passages where possible.

**Data prerequisite:** export `data/source-to-entries.json` — keyed by source label, valued as list of `<L>` record numbers. Currently not generated; would require a separate Python pass over `mw.txt`.

## Trust Block

- Evidence: no generated atlas data yet; current links point to static MWS reference notes.
- Limitations: placeholder only. It does not expose source-to-entry lookup and does not support passage cross-reference.
- Validation: checked by `npm run build`; data export remains future work.
- Owner repo: `csl-atlas`.
- Next use: follow citation rows back to dictionary source records before interpreting a source abbreviation.

## See also

- 🔗 [Top-25 source list with Wikipedia identities](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md#top-25-most-cited-sources) (static reference)
- 🔗 [`<ls>` coverage stats](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md#coverage-of-ls-citations) — 311,932 citations / 821 unique labels
- 🔗 [Top orphan abbreviations](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md#top-orphan-abbreviations) — sources used but lacking authority records

---

*Tier 3 tool. Will land in a later iteration.*

_Dr. Mārcis Gasūns_
