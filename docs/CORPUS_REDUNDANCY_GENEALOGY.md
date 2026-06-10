# Corpus-wide redundancy and dictionary genealogy (OBS-R)

Date: 2026-06-10

Corpus-wide (all 43 local `csl-orig` dicts) quantification of headword
redundancy and the inheritance stemma. This is the **content-containment axis**
of [`THREE_AXIS_COMPARISON.md`](THREE_AXIS_COMPARISON.md) measured across every
dictionary at once, and the all-dictionary generalisation of the panel results in
[`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md),
[`MICROSTRUCTURE_XREF_LINEAGE.md`](MICROSTRUCTURE_XREF_LINEAGE.md), and the
derivation notes already recorded in [`../data/dictionary_inventory.csv`](../data/dictionary_inventory.csv).

## Trust Block

- Evidence: `<L>`/`<k1>` extraction over `../csl-orig/v02/*/*.txt` (43 dicts,
  1,495,459 entries — the same scan base as `MICROSTRUCTURE_M1_M2_RESULTS.md`);
  pairwise containment from [`../data/sanhw1_jaccard.csv`](../data/sanhw1_jaccard.csv)
  (columns `a_in_b`, `b_in_a`); publication years and prior derivation notes from
  [`../data/dictionary_inventory.csv`](../data/dictionary_inventory.csv).
- Limitations: lemma-level, not sense-level; surface `<k1>` keys (already
  canonical SLP1 — light normalisation moved only 7 of 343,460 lemmas, so the
  lower-redundancy bound needs anusvāra/visarga folding). **Containment is a floor
  for structural overlap, not proof of direct copying** (same caution as
  `MICROSTRUCTURE_XREF_LINEAGE.md`). All 43 dictionaries are now included: the
  three Hemacandra kośas (abch, acph, acsj) carry no `<k1>` and are read from
  their `<syns><s>…</s>` synonym format by
  [`scripts/obs/headword_multiplicity.py`](../scripts/obs/headword_multiplicity.py),
  validated to reproduce the sanhw1 lemma counts exactly.
- Validation: re-run the extraction (command at foot); the entry total must
  reconcile with the canonical 1,495,459 and with `data/headwords.json` per-dict
  `<L>` counts.
- Owner repo: `csl-atlas`.
- Next use: read the stemma as a floor; adjudicate direction with the year + size
  asymmetry rule below before any "X derives from Y" claim reaches a paper.

## 1. Entry → lemma collapse

| Measure | Value |
|---|---|
| Raw `<L>` entries (43 dicts) | 1,495,459 |
| Distinct lemmas (`<k1>` + kośa `<syns>`) | 409,649 |
| **Collapse ratio** | **3.65 : 1** |
| Lemmas in ≥2 dicts (redundant) | **57.9 %** |
| Lemmas in exactly 1 dict (independent) | 42.1 % |
| Independence band (18-dict core+kosha, surface→aggressive norm) | 42.4 % → 36.5 % |
| Homonym-normalised entries (distinct `<k1>` per dict, summed) | 1,291,215 |
| **Entry split-inflation** (raw ÷ homonym-normalised) | **1.158** |

The 1.158 split-inflation is the corpus-wide counterpart of the macro/micro
trade-off in `MICROSTRUCTURE_M1_M2_RESULTS.md`: MW promotes derivatives and
preverbs to headwords (194,084 `<k1>` keys) where the Petersburg dictionaries nest
them, so ~13.7 % of all entries are homonym/sub-entry splits.

## 2. Redundancy is *structured* — not uniform

Per-dictionary **unique contribution** (lemmas found in no other dict) separates
two populations:

| Population | Dicts (unique %) | Reading |
|---|---|---|
| Mutually derivative core | pwg 1.9, yat 2.8, pw 4.4, mw72 4.7, mw 13.0 | the general European-tradition dicts re-lexicalise one another |
| Genuinely independent | bhs 57.6, ieg 57.6, acc 43.3, pui 38.6, skd 37.2, ap 34.7 | domain/indigenous lexica carry irreplaceable material |

The metric validates itself: the dictionaries we *expect* to be derivative score
low unique%, the specialised/indigenous ones score high. This is the
content-axis evidence behind `XREF-CORE` ("shared core, not wholesale descent").

A third pattern emerges once the kośas are parsed: the **thesaurus kośas are not
independent vocabulary**. Abhidhānacintāmaṇi (abch) supplies 11,584 synonym lemmas
but only **3.3 % are unique** (acph 14.2 %, acsj 7.6 %) — a synonym dictionary
re-groups already-attested common words rather than adding new ones, the opposite
of the citation-driven specialised lexica (bhs/ieg) above.

## 3. Inheritance stemma (containment + year + size asymmetry)

Direction rule: where `A ⊂ B` (high `a_in_b`, low `b_in_a`) **and** A and B differ
in publication year, the **older/larger** member is the ancestor. This reproduces
and systematises the derivation notes already in `dictionary_inventory.csv`.

| Edge (A ⊂ B) | `a_in_b` | Years | Direction | Inventory note |
|---|---:|---|---|---|
| YAT ⊂ WIL | ~0.91 | 1846 / 1832 | WIL → YAT | "YAT derived from WIL" |
| WIL ⊂ SHS | 0.953 | 1832 / 1900 | WIL → SHS | "SHS derives from WIL" |
| CCS ⊂ PW | 0.945 | 1887 / 1879 | PW → CCS | "PWK→CCS derivation" |
| PWKVN ⊂ PW | ~0.999 | (Nachträge) | PW ⊃ PWKVN | "99.9% subset of PW" |
| BEN ⊂ MW | 0.94 | 1866 / 1899 | (absorbed) MW | — |
| MD ⊂ MW | 0.93 | 1893 / 1899 | (absorbed) MW | — |
| BOP ⊂ MW | 0.94 | 1847 / 1899 | (absorbed) MW | — |
| ARMH/ABCH ⊂ MW | 0.92–0.93 | 1861/1896 / 1899 | (absorbed) MW | kośa headwords |
| GRA ⊂ MW | 0.88 | 1873 / 1899 | (absorbed) MW | — |

**MW (1899) is the great absorber** — by far the largest key set (194,084) and the
latest of the big three, it contains 88–94 % of nine other dictionaries' headword
stock. **PW (1879)** is the second hub (CCS, MD, CAE, BEN, PWKVN ⊂ PW), itself
downstream of **PWG (1855–75)**. The English line runs WIL (1832) → YAT/SHS. This
is the all-dictionary version of the `PET-MW-CITE` and `XREF-HUBS` hypotheses:
the floor-level structural skeleton onto which the citation-truncation and
rare-term tests can be layered for proof of direct copying.

## Reproduction

```sh
# Entry→lemma collapse + per-dict unique contribution (all 43 dicts, format-aware):
python scripts/obs/headword_multiplicity.py     # -> data/obs/headword_multiplicity.csv
# Stemma edges: read a_in_b / b_in_a from data/sanhw1_jaccard.csv;
#   assign direction by data/dictionary_inventory.csv `year`.
```

_Companion: org-process correction-sustainability evidence (OBS-Q) lives in
`csl-observatory/reports/obs_q_correction_sustainability.md`; the cross-repo bridge
memo that routed these numbers here is
`csl-observatory/reports/obs_rc_atlas_bridge.md`._
