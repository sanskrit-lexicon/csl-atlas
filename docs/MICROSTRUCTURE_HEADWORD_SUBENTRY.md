_Created: 06-06-2026 · Last updated: 05-09-2026_

# Microstructure Headword And Subentry Structure

Date: 2026-06-06

Audience: scholars who need the first, easiest-to-parse layer of dictionary
microstructure before moving to citation practice, grammar/gender marking,
sense segmentation, citation practice, grammar/gender marking, or
cross-references.

## Trust Block

- Evidence: `data/lexico/microstructure_subentries.csv`,
  `data/lexico/preverb_subentries.csv`,
  `data/lexico/microstructure_profile.csv`,
  `data/lexico/microstructure_fingerprint.json`,
  `scripts/lexico/m1_subentries.py`, `scripts/lexico/m2_preverbs.py`, and
  `scripts/lexico/m5_profile.py`.
- Limitations: this page counts recoverable headword/subentry conventions; it
  does not prove that unmarked dictionaries lack derivatives, preverbs, or
  grammatical structure.
- Validation: rerun M1, M2, M5, and `python scripts/lexico/validate_lexico.py`;
  public pages are checked by `npm run build`.
- Owner repo: `csl-atlas`.
- Next use: use this page as the first microstructure reading layer, then move
  to sense segmentation before citation practice, grammar/gender marking, and
  cross-references.

## Why This Comes First

Headword/subentry structure is the easiest microstructure layer to parse because
it asks a concrete layout question:

```text
Does the dictionary promote a form to its own headword, or nest it inside
another entry?
```

This question is easier than sense segmentation because it can often be tested
with visible markers:

- `<ab>` derivative markers such as causative, passive, desiderative,
  intensive, denominative, periphrastic, and compound;
- `<div n="p">` preverb-subentry blocks in Petersburg-style entries;
- the absence of these markers, when a dictionary instead promotes forms to
  separate headwords or writes structure in prose.

## Main Finding

The first structural contrast is a macro/micro trade-off:

| Pattern | Typical dictionaries | Reading |
|---|---|---|
| Promote forms to headwords | MW | Many derivatives and preverb forms become separate lookup forms. |
| Nest forms inside entries | PWG, PW/PWK, CAE, WIL | Preverb and derivative material often lives under a parent headword. |
| Write structure in prose or indigenous conventions | SKD, VCP, KRM, SHS, YAT | Western subentry detectors can read low while real grammatical structure remains present. |
| Narrow or reverse-direction structure | specialized and English-to-Sanskrit works | A low score may reflect genre or lookup direction, not weakness. |

This is why MW is a good public lookup default while PWG/PWK remain crucial for
scholar-facing detail. MW is easier to start with; PWG/PWK often preserve more
nested apparatus once the reader knows what to inspect.

## M1: Derivative Subentries

M1 counts derivative markers visible in `<ab>` tags. It works well for
European-style dictionaries that expose derivative categories in markup.

Typical recoverable categories:

| Category | Examples of marker family | Use |
|---|---|---|
| causative | `caus.` | Secondary verbal derivation. |
| passive | `pass.` | Voice or derived verbal form. |
| desiderative | `desid.` | Desire-form evidence. |
| intensive | `intens.` | Intensive/frequentative evidence. |
| denominative | `den.`, `denom.` | Verb from nominal base. |
| periphrastic | `periphr.` | Periphrastic construction marker. |
| compound | `comp.` | Compound or compound-derived subentry marker. |

Interpret M1 comparatively. A high M1 density means that the dictionary exposes
derivative material in the counted convention. A low M1 density can mean:

- the dictionary promotes those forms to headwords;
- the dictionary uses prose instead of `<ab>`;
- the dictionary is not a narrative Sanskrit-to-English/German dictionary;
- the detector has not yet learned that dictionary's local convention.

## M2: Preverb Subentries

M2 counts `<div n="p">` preverb blocks. This is the cleanest visible signature
of Petersburg-style nesting.

The practical reading:

| If M2 is high | If M2 is low |
|---|---|
| The dictionary often keeps preverb verbs under a parent root or verb entry. | The dictionary may promote preverb forms to separate headwords, use another marker, or be outside the preverb-subentry genre. |

MW is expected to be low under M2 because it often makes preverb compounds and
derivatives searchable as headwords. That is not a defect; it is a different
macrostructure.

## Reading Zeros

Do not read zero as "no structure" until the convention is checked. Use this
order:

1. Is the dictionary a narrative Sanskrit dictionary or a narrow/index/reverse
   tool?
2. Does it use `<ab>` or `<div n="p">` at all?
3. Does it expose the same information as headwords instead of subentries?
4. Does it write the structure in prose, Sanskrit grammatical notation, or an
   indigenous authority convention?
5. Has a dictionary-specific detector already been written?

Only after these checks can a zero become evidence for true absence.

## Reproduce

```sh
python scripts/lexico/m1_subentries.py --all
python scripts/lexico/m2_preverbs.py --all
python scripts/lexico/m5_profile.py
python scripts/lexico/validate_lexico.py
```

Recommended public-page check:

```sh
npm test
npm run build
```

## Next Microstructure Layers

This page should be the first in the scholar-facing sequence:

1. Headword/subentry structure.
2. Sense segmentation.
3. Citation practice.
4. Grammar/gender marking.
5. Cross-references.

The sequence is intentionally parse-first: start with visible layout, then move
toward interpretation-heavy layers.

## Related

- [`MICROSTRUCTURE_PROFILE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_PROFILE.md)
- [`MICROSTRUCTURE_METHODS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_METHODS.md)
- [`MICROSTRUCTURE_FINDINGS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_FINDINGS.md)
- [`MICROSTRUCTURE_SENSE_SEGMENTATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SENSE_SEGMENTATION.md)
- [`MICROSTRUCTURE_M1_M2_RESULTS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_M1_M2_RESULTS.md)
- [`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md)
- [`H6_STRUCTURAL_REGISTER_SCATTER.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H6_STRUCTURAL_REGISTER_SCATTER.md)

_Dr. Mārcis Gasūns_
