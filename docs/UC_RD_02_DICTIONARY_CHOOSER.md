# UC-RD-02 Dictionary Chooser

Date: 2026-06-05

Audience: readers, students, translators, and scholars who need a first
dictionary for a Sanskrit lookup task.

## Trust Block

- Evidence: dictionary metadata, reader-lookup coverage, dictionary pages,
  source links, and documented comparison outputs.
- Limitations: this page recommends starting points by task; it does not rank
  every dictionary globally, translate entries, or use corpus frequency.
- Validation: recommendations must remain consistent with
  `DICTIONARY_USER_GUIDE.md`, Reader Lookup v1 coverage, and visible source
  links.
- Owner repo: `csl-atlas`.
- Next use: make the public site route `/dictionary-chooser` the first reader
  decision page, then send users to Reader Lookup or a dictionary source link.

## Use Case

UC-RD-02 asks one public-reader question:

```text
I have a Sanskrit word or research task. Which dictionary should I open first?
```

The atlas answer should be a route, not a verdict. A good route starts from a
dictionary suited to the task, then asks the reader to verify the original
source record.

## Public Default

Use **MW** as the public default. It is not "the best Sanskrit dictionary" in a
global sense; it is the best first stop for most public atlas readers because it
is broad, English-facing, heavily linked, and familiar enough to make the first
lookup succeed.

The chooser should then help the reader decide what the second dictionary is
for:

- AP clarifies ordinary English reading.
- PWG/PWK recover source trail, nested structure, and variant detail.
- VCP/SKD recover Sanskrit-Sanskrit and indigenous authority conventions.
- WIL recovers older English-line wording.
- Specialized dictionaries answer scope-specific questions.

## Quick Choice

| Task | Start with | Then check | Why |
|---|---|---|---|
| Fast English meaning | MW | AP | MW is broad; AP is often clearer for practical reading after MW. |
| Classroom or translation aid | MW | AP | MW is the default atlas route; AP gives a compact reader-facing check. |
| Citation-heavy philology | MW | PWG, PWK | PWG/PWK can show source trail, variants, and nested structure that MW may compress. |
| Traditional Sanskrit-Sanskrit evidence | MW | VCP, SKD | Start from the public default, then inspect indigenous glossing and authority conventions. |
| Older English tradition | MW | WIL, SHS/KOW when available | Start from the public default, then compare Wilson-line wording and translation history. |
| German dictionary evidence | MW | PWG, PWK | Open them for evidence trail and structural detail, not because a newcomer needs the history first. |
| Grammar or gender check | MW/AP | VCP/SKD where visible | Compare visible grammar labels and keep review status in view. |
| Dictionary comparison | Reader Lookup | Dossier and comparison tools | Start with coverage, then inspect per-dictionary records. |

## Decision Path

1. Need an English gloss quickly? Start with MW, then compare AP.
2. Need source citations? Start with MW, then open PWG/PWK for apparatus.
3. Need indigenous lexicographic evidence? Start with MW, then open VCP and SKD.
4. Need to compare traditions? Use Reader Lookup, then open the source links.
5. Need corpus frequency or passage usage? Leave the atlas path; that belongs
   to VisualDCS first.

## PWG/PWK Public Wording

Avoid telling a newcomer "use PWG/PWK for Petersburg lineage" as the reason.
That is true for researchers, but it is not a useful public action. Use this
wording instead:

```text
Use PWG/PWK when MW is not enough: source trail, variant forms, nested
preverb/derivative structure, and fuller apparatus.
```

## What The Choice Means

Choosing a starting dictionary means only:

- this dictionary is likely useful for the task;
- its evidence can be checked in a source-linked record;
- other dictionaries may still disagree or add better evidence.

It does not mean:

- the chosen dictionary is globally best;
- an absent result proves the word is absent from Sanskrit;
- English dictionaries are stronger than German or Sanskrit dictionaries;
- dictionary evidence is the same as corpus attestation;
- machine-derived labels are human-reviewed.

## Reader Lookup Contract

Reader Lookup v1 supports a dictionary-first path:

- exact and prefix lookup over dictionary headwords;
- deterministic SLP1 and IAST query normalization;
- dictionary coverage and source links;
- visible caveats for omitted low-coverage lemmas;
- no backend, no full-text corpus search, no DCS passage lookup.

The chooser and Reader Lookup should therefore stay aligned: the chooser tells
the reader where to begin; Reader Lookup shows whether the lemma is actually
covered by the current compact data.

## Boundary

This page belongs to `csl-atlas` because it starts from dictionary choice,
dictionary evidence, and dictionary source links.

It must not absorb:

- DCS passage frequency or corpus attestation: `VisualDCS`;
- TEI/OntoLex/FrAC standards export: `csl-standards`;
- GitHub issue, contributor, or workflow evidence: `csl-observatory`;
- grammar analysis outside dictionary records: future grammar repo.

## Related Pages

- [`DICTIONARY_USER_GUIDE.md`](DICTIONARY_USER_GUIDE.md)
- [`READER_LOOKUP_EXPLAINER.md`](READER_LOOKUP_EXPLAINER.md)
- [`EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md)
- [`USE_CASES.md`](USE_CASES.md)
- [`BOUNDARY_RULES.md`](BOUNDARY_RULES.md)
