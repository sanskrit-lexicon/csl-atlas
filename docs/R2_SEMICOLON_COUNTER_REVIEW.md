# R2 review packet — semicolon-aware sense counter (parser promotion)

Status: **needs-human-review** — a parser-promotion proposal, not an applied change.
Owner: `csl-atlas`. Routes through the R2 checkpoint process
([`R2_CHECKPOINT_DECISIONS.md`](R2_CHECKPOINT_DECISIONS.md)). Machine fields are filled;
human decision fields are empty.

Packet data: [`data/lexico/r2_semicolon_counter_packet.json`](../data/lexico/r2_semicolon_counter_packet.json)
(`npm run build-r2-semicolon-counter-packet`). Evidence: [`data/lexico/r2_yat_artifact_check.json`](../data/lexico/r2_yat_artifact_check.json) (#125).

---

## Why

The H3R `wil→yat` "drastic condensation" (9 senses → 1) is a parser artifact (#125): YAT
does not number its senses — it packs them into one **semicolon-separated run-on gloss**
(Petersburg/MW style), and the one number present is a **noun-class / gender marker** that the
inline-number splitter (`\b\d+\.\s+`) mis-reads, collapsing every YAT entry to 1.

Fixing this means counting senses *semicolon-aware* for such dictionaries — which changes how
senses are counted, i.e. a **parser promotion**. Per the R2 contract, parser promotions are
reviewed before adoption, never applied silently. Hence this packet.

## Proposed rule

> If a dictionary's entries are **not sense-numbered** (mean inline-number senses < 1.5) but
> are **semicolon-packed** (mean semicolon meanings ≥ 3), count senses by semicolon
> segmentation (after dropping the leading headword + noun-class number) instead of inline
> numbering.

## Detection gate — evidence (28-noun panel)

| dict | mean inline-number senses | mean semicolon meanings | class-number marker | gate verdict |
|---|--:|--:|--:|---|
| **YAT** | **1.0** | **5.71** | 75% | run-on-gloss → **apply** semicolon counter |
| SHS *(control)* | 9.0 | 11.75 | — | sense-numbered → **keep** inline-number |

SHS is the control: it genuinely numbers its senses (mean 9, matching its WIL ancestor), so the
gate correctly leaves it on the inline-number method. Only YAT crosses the gate.

## What changes if promoted

- YAT panel sense count rises ~1 → ~5.7; the `wil→yat` drift recomputes from −8 toward parity —
  **retracting the "drastic condensation" reading** of that edge.
- H3R then has **no condensation exemplar** on this edge; only `wil→shs` (verbatim copy) and
  `ap90→ap` (revision) remain. A genuine condensation edge must be found elsewhere.
- No change to SHS or to any sense-numbered dictionary.

## Decision protocol (per checkpoint row)

Each of the 26 rows links the YAT source entry. Source-read the gloss, then mark `reviewedValue`:

- **`promote-parser-candidate`** — the semicolon segments are distinct senses; adopt the counter.
- **`retain-inline-number`** — the segments are one sense's sub-list (synonyms/examples), not
  distinct senses; keep the current method.
- **`control-only`** — ambiguous; record as evidence, do not promote.

## Risks / limitations

- **Over-splitting is the main risk:** semicolons also separate items *within* one sense (a
  synonym list). Source verification per row is required before promotion.
- The meaning counter drops the leading headword + the first noun-class number heuristically;
  multi-gender entries (`m. n.`) may carry more than one leading marker.
- Panel-scoped (28 nouns). A full-corpus per-dict gate pass should precede any promotion.
- Archive parity is a regression signal, **not** the optimization target: promote on
  source-read meaning separation, never to match an archived count.

## Boundary

The sense-counting rule is **unchanged** until a reviewer adjudicates these rows. This packet
proposes; it does not edit the parser or `csl-orig`.
