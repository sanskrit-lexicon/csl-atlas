_Created: 29-06-2026 · Last updated: 05-09-2026_

---
title: Student lesson track
toc: false
---

# Student Lesson Track

This page turns atlas tools into short classroom exercises. It is meant for
Sanskrit students who can read a headword and need practice deciding what a
dictionary record proves.

## Trust Block

- Evidence: atlas lookup/dossier pages, dictionary chooser guidance, learner
  reading layer, and linked `csl-guides` lessons.
- Limitations: teaching route only; examples are prompts, not final translations
  or philological decisions.
- Validation: linked atlas pages are checked by `npm run build`; exercises use
  existing public tools and do not introduce generated data.
- Owner repo: `csl-atlas`.
- Next use: assign one lesson, require a cited dictionary record, and ask the
  student to name the evidence level.

## Six Short Lessons

| Lesson | Question | Tool path | Student output |
|---|---|---|---|
| 1. First dictionary | Which dictionary should I open first for this word? | [Which dictionary?](dictionary-chooser) -> [Reader Lookup](tools/reader-lookup) | One first-stop dictionary and one reason. |
| 2. Coverage is not meaning | How many dictionaries know this lemma, and what does that not prove? | [Reader Lookup](tools/reader-lookup) -> [Lemma dossier](tools/dictionary-dossier) | Coverage count plus one limitation. |
| 3. Source trail | Does the gloss depend on a named source or only dictionary tradition? | [Citation apparatus](tools/dictionary-citations) -> dictionary page | One cited source link or a note that no source is explicit. |
| 4. Dictionary disagreement | Where do two dictionaries differ in grammar, sense, or convention? | [Lemma dossier](tools/dictionary-dossier) -> [Gender conflicts](tools/dictionary-conflicts) | Two records and a neutral description of the disagreement. |
| 5. Corpus caution | Does dictionary evidence equal corpus attestation? | [Learner layer](tools/learner-reading-layer) -> [Lemma dossier](tools/dictionary-dossier) | One sentence separating dictionary record from corpus signal. |
| 6. Do not correct too quickly | Is an odd spelling likely an error, variant, or apparatus note? | [Researcher Dashboard](researcher-dashboard) -> [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) | A cautious classification and the evidence needed before filing. |

## Suggested Word Sets

| Set | Words | Why this set works |
|---|---|---|
| Basic concepts | `agni`, `dharma`, `yoga`, `rAma` | Familiar enough that students can focus on evidence instead of vocabulary. |
| Grammar bridge | `gam`, `BU`, `dA`, `vid` | Shows why roots, classes, and dictionary lemmas are not the same surface. |
| Source-trail practice | `mokza`, `medas`, `mfga`, `Siva` | Encourages source links and dictionary-to-dictionary comparison. |
| Caution set | `divaraTa`, `akalkala`, `cApaqa` | Useful for discussing variant, correction, and source-check evidence. |

## Teaching Rules

| Rule | Classroom use |
|---|---|
| Cite records, not summaries | The atlas guides the path; the dictionary record carries the claim. |
| Keep both sides of disagreement | Do not force MW/AP/PWG/VCP/SKD into one artificial answer. |
| Say what kind of evidence it is | Use observed, derived, inferred, or reviewed in every note. |
| Stop before correction | A suspicious form needs source checking before it becomes a correction. |

## Related

- [Student Research Desk](research-desk)
- [Which dictionary should I use?](dictionary-chooser)
- [Reader Lookup](tools/reader-lookup)
- [Lemma dossier](tools/dictionary-dossier)
- [csl-guides](https://sanskrit-lexicon.github.io/csl-guides/)

_Dr. Mārcis Gasūns_
