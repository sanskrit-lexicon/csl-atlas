_Created: 11-06-2026 · Last updated: 05-09-2026_

# Convention Fingerprints as Parse-Rules

Date: 2026-06-11

Audience: maintainers and reviewers deciding how the atlas's convention and
microstructure outputs relate to machine dictionary-digitisation pipelines, and how
to describe that relationship in grant and paper framing.

## Trust Block

- Evidence: this repo's convention-fingerprint outputs (`src/data/lexicographic-structure/L0/`), microstructure fingerprint (`data/lexico/microstructure_fingerprint.json`), the eighteen-block apparatus in the [MWS microanalysis paper](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md), Setiawan et al., *MUDIDI* ([DavidSamuell/MUDIDI](https://github.com/DavidSamuell/MUDIDI); local PDF kept with the project sources, not redistributed here), and Coward, D. F. & Grimes, C. E. (2000). *Making Dictionaries: A Guide to Lexicography and the Multi-Dictionary Formatter.* Waxhaw, NC: SIL International — the primary definition of the MDF standard-format-marker schema (Appendix A field inventory).
- Limitations: a framing/positioning document, not a generator. The "~6 F1" figure is from a recent preprint and describes MUDIDI's dictionaries, not a re-run on CDSL data; treat it as motivation, not a measured atlas result.
- Validation: convention claims are checked by `npm run build` and `docs/L0_RESULTS.md`; microstructure by `python scripts/lexico/validate_lexico.py`.
- Owner repo: `csl-atlas`.
- Next use: read with the [related-work note](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/related-work.md) and the candidate [MDF export profile](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md).

## The Claim

The MUDIDI benchmark decomposes machine dictionary digitisation into two stages —
faithful page transcription (Stage 1) and parsing into SIL's MDF schema (Coward &
Grimes 2000, the standard-format-marker inventory of Appendix A) (Stage 2) —
and runs a "parse-rules" pass once per dictionary before parsing pages. That pass
produces a JSON object with three parts:

1. the dictionary's **MDF field inventory**;
2. its **abbreviation key**; and
3. its **structural rules for entry boundaries**.

MUDIDI's headline Stage 2 result is that *this prior knowledge dominates model size*.
Supplying a dictionary's own introduction and a formal field schema each lift
entry-field-assignment F1 by ~3–6 points; replacing the model-inferred parse-rules
with a **human-validated** version adds ~6 points on average — the single largest
intervention in the paper.

**The atlas already produces exactly this layer for the CDSL dictionaries, by hand and
deterministically.** What MUDIDI calls per-dictionary parse-rules, the atlas calls
convention fingerprints, the structural register, and the eighteen-block apparatus.
Reframed: the atlas's convention scholarship is not only descriptive — it is the
**human-validated parse-rule layer** that machine pipelines pay the most to obtain.

## The Correspondence

| MUDIDI parse-rules component | Atlas artifact | Where |
|---|---|---|
| MDF field inventory | eighteen-block apparatus + tag→MDF map | [MWS PAPER §3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md); [MDF export profile](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md) |
| Abbreviation key | `<ab>` inventory (194,879 in MW) + dictionary intros + `MWS/mwabbreviations/abbr.html` | CDSL source markup; per-dict abbreviation HTML |
| Entry-boundary / structural rules | convention fingerprints (25 dims) + microstructure (headword-promotion M1, preverb M2, continuation, homonym) | `src/data/lexicographic-structure/L0/`; `data/lexico/microstructure_fingerprint.json`; [convention fingerprints page](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lexicographic-conventions.md) |
| House-style normalisation (anusvāra, ṛ-stems, -at vs -ant …) | Patel's seven canonical conventions, per-dictionary | `src/data/lexicographic-structure/L0/patel2016_assignments.csv` |

The convention-fingerprint work even carries a result MUDIDI's setup implies but does
not isolate: **convention lineage is distinct from content lineage**. Monier-Williams
absorbed the Petersburg *lexicon* (89–94 % content containment) while imposing its own
orthographic house style (near-zero convention similarity). For a parsing pipeline this
is the precise statement that *you cannot reuse one dictionary's parse-rules for its
content-descendant* — the heir was re-typeset. That is a reusable, machine-actionable
prior, not a philological footnote.

## Why This Strengthens The Hypothesis

The atlas's central methodological bet is that **house-style conventions are the
controlling signal for correct structural interpretation**, which is why it invests in
fingerprints and registers rather than treating markup as incidental. MUDIDI is
independent, quantified corroboration from a different method (frontier VLMs/LLMs on 30
dictionaries) and a different schema (MDF, not TEI/OntoLex). It lets the atlas restate
its contribution in pipeline terms: *the convention profiles are the validated
parse-rules that the largest single F1 gain in current digitisation comes from.*

## Caveats

- **Direction.** The atlas works *downstream* of digitisation, on already-keyed CDSL
  text; MUDIDI works *upstream*, recovering structure from scans. The shared object is
  the per-dictionary convention layer, not the task.
- **No LLM inference in the atlas.** This framing does not propose adding a model to the
  atlas. The atlas's `observed`/`derived`/`inferred`/`reviewed` labelling is precisely
  the discipline MUDIDI recommends ("treat model output as provisional, human-validate").
- **The numbers are external.** ~3–6 F1 and ~6 F1 describe MUDIDI's dictionaries on a
  preprint benchmark; they motivate the framing and are not a measurement on CDSL.

## Next Steps (Optional)

1. Emit a **parse-rules-shaped JSON per dictionary** — field inventory, `<ab>`
   abbreviation list, and entry-boundary rules — as a by-product of the existing
   fingerprint and microstructure builds, in the MUDIDI Pass-1 shape.
2. Offer the Sanskrit parse-rules + the source-linked MDF sample as a contribution to
   the MUDIDI dataset, whose parsing subset omits Sanskrit.
3. Add an experiment note: does feeding the atlas convention fingerprint as parse-rules
   measurably help a model parse a held-out CDSL page? (Would be the first *measured*
   atlas claim here, replacing the external ~6 F1.)

_Dr. Mārcis Gasūns_
