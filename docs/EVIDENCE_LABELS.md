# Evidence Labels

Date: 2026-05-29

Audience: every atlas user. This is the single explainer for the certainty labels that appear next to claims, tables, and charts.

The atlas exists to make scholarly claims **traceable**:

```text
Claim -> Evidence -> Source
```

A label tells you *how a claim was produced*, so you know how much weight it can bear. No visualization in the atlas should hide whether a number is observed, derived, inferred, or reviewed.

## The Four Labels

These are the canonical labels used in all generated data (`evidenceLevels` fields, table cells, chart legends).

| Label | Reader-friendly name | Meaning | Example |
|---|---|---|---|
| `observed` | in the source | Directly present in a dictionary, corpus export, or source file | An MW record contains `<lex>m.</lex>` |
| `derived` | computed | Produced by a fixed, reproducible rule from observed data | The record is classified as `noun-m` because of that `<lex>m.</lex>` |
| `inferred` | probable | A useful heuristic that has not been verified; may be wrong | A lexical family inferred from a shared headword prefix |
| `reviewed` | checked | A human has confirmed or corrected the value | A reviewer accepted a dictionary alignment |

## How To Read Them

Think of the labels as a ladder of trust:

```text
observed   strongest — the source says so
derived    strong — a rule restated what the source says
inferred   weakest — a guess the atlas is being honest about
reviewed   strongest of all — a human verified it
```

`reviewed` does not replace the other labels; it sits on top of them. A claim can be "derived, and then reviewed-ok," meaning a rule produced it and a human confirmed the rule was right for that case.

## Why This Matters

Dictionary data can *look* more certain than it is. Three common traps:

- **Inferred lexical families.** Grouping words by a shared prefix is convenient but sometimes wrong. These are labeled `inferred` and must be shown with a visible warning.
- **Diachronic / period layers.** The atlas maps source abbreviations to conservative period layers (`vedic`, `epic`, `classical`, …). This is `derived` at best and often `inferred`. It is **not** exact dating. See `ARCHITECTURE.md` for the period-layer policy.
- **Lexicographer-only entries.** A word whose only citation is `L.` is genuine lexicographic evidence but weaker than a textual attestation. It is flagged so readers do not over-trust it.

The project's anti-goals (`docs/USE_CASES.md`, AUC-05) state the rule plainly: **weak evidence must be visibly marked.** Inferred families, uncertain period layers, low-confidence alignments, and dictionary-only claims are never presented as if they were observed facts.

## Where Labels Appear

- **In tables and cards** — as a small tag or column next to the value.
- **In generated JSON** — every output file carries `assumptions`, `warnings`, and (where relevant) per-field `evidenceLevels`, so the label travels with the data when it is reused.
- **In charts** — through legends, caveat notes, and links to the underlying examples.

If you reuse atlas data elsewhere, keep the evidence label attached. A number without its label has lost the part that makes it scholarship.

## Relationship To Review Status

The evidence labels describe *how a value was produced*. Review status describes *how far human checking has gone*. They are complementary:

| Evidence label | Typical review status before review | After review |
|---|---|---|
| `observed` | `machine` | usually stays trusted; rarely needs review |
| `derived` | `machine` / `needs-review` | `reviewed-ok` or `reviewed-corrected` |
| `inferred` | `needs-review` | `reviewed-ok`, `reviewed-corrected`, or `blocked` |

For the full review-status vocabulary and how corrections are recorded, see [`docs/REVIEW_REPORTS.md`](REVIEW_REPORTS.md).

## Related Documents

- [`docs/DICTIONARY_USER_GUIDE.md`](DICTIONARY_USER_GUIDE.md) — the reader-facing lookup guide.
- [`docs/REVIEW_REPORTS.md`](REVIEW_REPORTS.md) — how machine claims become reviewed claims.
- `ARCHITECTURE.md` — the core certainty principle and the diachronic-scale caveats.
- `docs/USE_CASES.md` — UC-RD-15, UC-TEACH-03, and the anti-goals on hiding weak evidence.
