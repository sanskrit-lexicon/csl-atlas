_Created: 29-06-2026 · Last updated: 05-09-2026_

---
title: Evidence bridges
toc: false
---

# Evidence Bridges

This page records which nearby Sanskrit research repos are relevant to the
atlas and how their work should enter the atlas, if at all. The rule is simple:
link first, import only when a dictionary-facing artifact has a clear contract.

## Trust Block

- Evidence: current atlas boundary rules, `.ai_state.md`, and inspected
  cross-repo session journals for `WhitneyRoots`, `VisualDCS`,
  `SanskritSpellCheck`, `MWS`, `CommentaryStrategies`, `csl-guides`, and
  `csl-standards`.
- Limitations: routing map only; no external repository data is copied into
  this page and no external pipeline is made part of the atlas build.
- Validation: route links are checked by `npm run build`; external repositories
  remain independently validated in their own projects.
- Owner repo: `csl-atlas`.
- Next use: decide whether a bridge should stay a link, become a small atlas
  chip, or wait for a formal data contract.

## Bridge Map

| Repo | Atlas value | Product shape | Boundary |
|---|---|---|---|
| [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) | Root/class, Whitney grammar sections, MW/Apte root entries, DCS frequency, generated paradigms | Future grammar bridge chip on lemma/dossier pages | Link now; import only a compact root-summary contract later. |
| [VisualDCS](https://github.com/gasyoun/VisualDCS) | Corpus/genre context and modern 2026 CoNLL-U-derived lemma evidence | DCS frequency/context chip already belongs only as dictionary-facing summary | Do not add corpus dashboards here. |
| [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) | Typo vs variant vs wrong-reading vs orthographic drift teaching material | “Do not correct too quickly” lessons and correction-caution examples | No correction filing from atlas pages. |
| [MWS](https://github.com/sanskrit-lexicon/MWS) | MW authority records, `ib.`, Register B, source-link candidates | Citation-trust notes and source-authority links | Keep MW source work in MWS; atlas consumes only evidence summaries. |
| [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies) | Examples of commentary explaining differently from dictionaries | Occasional teaching contrast, not a data layer | Do not merge commentary pipeline into dictionary atlas. |
| [csl-guides](https://sanskrit-lexicon.github.io/csl-guides/) | Beginner-facing dictionary and script/grammar lessons | Student lesson prerequisites and follow-up drills | Guides teach basics; atlas teaches evidence use. |
| [csl-standards](https://github.com/sanskrit-lexicon/csl-standards) | TEI/OntoLex/loss-report interpretation | Research appendix links for interoperability | Standards work is not the atlas front door. |

## Import Readiness

| Status | Meaning | Current examples |
|---|---|---|
| Link only | Useful context, but not an atlas data input. | CommentaryStrategies, csl-standards, csl-guides. |
| Chip candidate | Small dictionary-facing summary could improve a lemma page. | WhitneyRoots root/class; VisualDCS lemma context. |
| Teaching example | Best used as exercises or cautionary notes. | SanskritSpellCheck, MWS Register B/source authority. |
| Contract required | Needs a stable manifest or schema before build integration. | Any future root-summary or corpus-summary import. |

## Near-Term Uses

1. Add a grammar bridge chip only after `WhitneyRoots` exposes a compact
   root-keyed manifest suitable for static lookup.
2. Keep VisualDCS to lemma-level context and resist moving corpus dashboards
   into this repository.
3. Turn SanskritSpellCheck examples into student correction-caution exercises
   before any source-editing workflow.
4. Use MWS authority work to improve citation-trust wording, not to duplicate
   MWS source files.

## Related

- [Researcher Dashboard](researcher-dashboard)
- [Student Lesson Track](student-lessons)
- [Boundary rules](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md)
- [VisualDCS consumption contract](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/VISUALDCS_CONSUMPTION_CONTRACT.md)

_Dr. Mārcis Gasūns_
