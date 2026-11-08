_Created: 24-09-2026 · Last updated: 24-09-2026_

# Lemmatisation policy census — what counts as a lemma in each of the seven dictionaries

Handoff H5332 (epic E014), Claude Code Opus 5 `claude-opus-5`. Data: `csl-orig@f4c08c57`,
Whitney's 938 roots (853 testable), DCS lemma spine 83,239 (Hellwig, ~2021 snapshot).

M1 and M2 measured headword *promotion* — what earns a subentry, what a preverb does to the
macrostructure. They never asked the prior question: **which form of a paradigm carries the
entry?** Every dictionary must answer it four times over, once per word class: the verbal
root or a finite form; the nominal stem or its nominative citation form; the compound as its
own head or as a run-on inside its first member; the derivative as its own head or inside its
base's nest. Those four answers are the dictionary's lemmatisation policy. The seven
narrative dictionaries are MW, PWG, PW (PWK), AP, WIL, SKD and VCP. The two versified kośas
(ARMH, ABCH) are excluded: concept-ordered verse has no headword layer to lemmatise, and M6
([`m6_kosha_macrostructure.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_kosha_macrostructure.py))
measures them instead.

Outputs:

1. [`data/lexico/lemmatisation_policy.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/lemmatisation_policy.json)
   — per-dictionary policy per word class, with counts, thresholds and the DCS band table.
2. [`data/lexico/lemmatisation_policy_classes.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/lemmatisation_policy_classes.csv)
   — the 28-row dict × word-class verdict table (7 × 4).
3. [`data/lexico/lemmatisation_policy_exceptions.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/lemmatisation_policy_exceptions.csv)
   — the exception rows: off-policy key shapes, Whitney roots with no headword, the minority
   side of each nesting verdict, and absent DCS lemmas sampled per frequency band.
4. The generator is
   [`scripts/lexico/m12_lemmatisation_policy.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m12_lemmatisation_policy.py)
   (`npm run build-lemmatisation-policy`, stdlib only, ~20 s, deterministic). Hand-derived
   pins are in
   [`tests/forensic/test_m12_lemmatisation_policy.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_m12_lemmatisation_policy.py).

## 1. Result — the policy of each dictionary, per word class

| Dict | Nominal stems | Verbs | Compounds | Derivatives |
|---|---|---|---|---|
| MW | stem (0.04 % inflected keys) | **root form** — 802 / 853 Whitney roots (94.0 %) | **nested** — 135,978 / 148,332 (91.7 %) | **nested** — 25,922 / 27,075 (95.7 %) |
| PWG | stem (0.02 %) | **root form** — 769 / 853 (90.2 %) | own head — 51,312, no nesting recorded | own head — 8,449, no nesting recorded |
| PW (PWK) | stem (0.01 %) | **root form** — 775 / 853 (90.9 %) | own head — 69,756, no nesting recorded | own head — 9,357, no nesting recorded |
| AP | **citation form** (28.3 % inflected) | **root form** — 712 / 853 (83.5 %), 3,201 records carry the conjugation mark | **nested** — 13,071 / 23,805 (54.9 %) | own head — 1,985 / 2,066 (96.1 %) |
| WIL | stem (0.02 %) | marginal root layer — 159 / 853 (18.6 %) | own head — 13,663, no nesting recorded | own head — 2,390, no nesting recorded |
| SKD | **citation form** (67.2 % inflected) | marginal root layer — 127 / 853 (14.9 %) | own head — 6,696, no nesting recorded | own head — 41, no nesting recorded |
| VCP | stem (0.15 %) | marginal root layer — 153 / 853 (17.9 %) | own head — 14,211, no nesting recorded | own head — 1,525, no nesting recorded |

Each verdict is a threshold over a measured rate, not a judgement. The thresholds are fixed
for all seven dictionaries and recorded in `policy_thresholds` in the JSON:

1. **Nominal stems** — inflected keys ≥ 20 % ⇒ citation form; 2–20 % ⇒ mixed; below 2 % ⇒ stem.
2. **Verbs** — Whitney roots present as an exact headword ≥ 60 % ⇒ root form; 20–60 % ⇒ partial;
   below 20 % ⇒ marginal. A separate branch catches a dictionary that keys the root *with* a
   nominative ending (≥ 20 % of roots as `root` + ḥ/ṃ); no dictionary triggered it (§3).
3. **Compounds and derivatives** — nested ≥ 50 % ⇒ run-on policy; 5–50 % ⇒ mixed; below 5 %
   ⇒ own head. "No nesting recorded" means csl-orig carries no `<e>` sub-record level for
   that dictionary at all, so the verdict is about the *record structure*, not about the
   printed page (§6.2).

Three families come out of the table, and they are not the same three families that the
collation census (H5331,
[`ACCESS_STRUCTURES_SORT_ORDER_CENSUS_24-09-2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ACCESS_STRUCTURES_SORT_ORDER_CENSUS_24-09-2026.md))
found:

1. **The Petersburg pair (PWG, PW)** — stem keys, root-form verbs, every compound and
   derivative its own head. A flat macrostructure: one form, one entry.
2. **MW and AP** — the same stem-or-root decision at the top (MW stem keys, AP citation
   keys), but a *nested* macrostructure underneath: MW puts 92 % of its detected compounds
   and 96 % of its derivatives inside another entry as run-ons; AP nests 55 % of compounds
   but only 4 % of derivatives. MW's nesting is the deepest of the seven.
3. **The indigenous and Wilson group (SKD, VCP, WIL)** — no real root layer (15–19 % of
   Whitney's roots are exact headwords, against 84–94 % in the other four) and, for SKD, a
   thoroughly citation-form key set. Their verb material is reached through derivatives
   (§3.2), not through the bare dhātu.

## 2. Nominal stems — the citation-shape test

The test is the final character of the `k1` key over the level-1 records: final ḥ or ṃ is an
inflectional ending (a nominative singular *akṣaraḥ*, a neuter *akṣaraṃ*), a vowel or a
consonant is a stem.

| Dict | Level-1 records | Vowel-final | Consonant-final | final ḥ | final ṃ | Inflected share |
|---|---|---|---|---|---|---|
| MW | 51,359 | 41,593 | 9,746 | 12 | 8 | 0.04 % |
| PWG | 123,357 | 103,333 | 20,002 | 8 | 14 | 0.02 % |
| PW | 158,370 | 133,145 | 25,212 | 8 | 5 | 0.01 % |
| AP | 45,002 | 18,513 | 13,746 | 12,741 | 2 | **28.3 %** |
| WIL | 44,577 | 40,129 | 4,437 | 1 | 10 | 0.02 % |
| SKD | 42,196 | 12,832 | 1,005 | 20,727 | 7,632 | **67.2 %** |
| VCP | 48,370 | 44,229 | 4,070 | 50 | 21 | 0.15 % |

1. **SKD keys citation forms.** Two thirds of its headwords carry a nominative ending, and
   the visarga/anusvāra split is the gender split: *akṣaraḥ* masculine, *akṣaraṃ* neuter.
   This is the same fact the collation census met from the other side: SKD files final ḥ at
   its own slot in the alphabet, decisively (3,297 disagreeing pairs), *because* the ending
   is part of the key.
2. **AP is mixed but over the line.** 12,741 visarga-final headwords against 32,259 that are
   not — the 28 % puts it in the citation-form class, but the exception list is the larger
   side. Its consonant-final count (13,746) is the highest of the seven in share terms, and
   those are the verbal roots (§3).
3. **VCP is a stem dictionary** (0.15 %), which separates it from SKD despite the shared
   indigenous tradition and despite both keeping ṃ at its own slot in collation. The two
   indigenous dictionaries agree on the alphabet and disagree on the lemma.
4. **The exception rows** — 20 for MW, 22 for PWG, 13 for PW, 11 for WIL, 71 for VCP — are
   in the exceptions CSV with L-ids and pages. For AP and SKD the exception class is the
   *uninflected* minority instead (32,259 and 13,837 rows; the CSV samples 25 per dict).

## 3. Verbs — the Whitney spine test

938 roots from Whitney's *Roots, Verb-forms and Primary Derivatives* (1885), read in IAST,
transliterated to SLP1, deduplicated over the homonym numbers, minus the one-character roots
that nothing can be tested on: **853 testable roots**. Each root is looked up in four ways,
in this order: exact headword; headword = root + ḥ/ṃ (a citation-form root); headword = root
+ a present ending (`ti te ati ate anti ante yati yate`); any headword that extends the root.

| Dict | root exact | citation root | finite form | derived only | absent |
|---|---|---|---|---|---|
| MW | **802** | 0 | 2 | 40 | 9 |
| PWG | **769** | 0 | 14 | 55 | 15 |
| PW | **775** | 0 | 14 | 51 | 13 |
| AP | **712** | 0 | 0 | 86 | 55 |
| WIL | 159 | 0 | 35 | 577 | 82 |
| SKD | 127 | 3 | 2 | 632 | 89 |
| VCP | 153 | 0 | 35 | 592 | 73 |

1. **Four dictionaries lemmatise the verb as the bare root.** MW, PWG, PW and AP each give
   83–94 % of Whitney's roots a headword of their own. AP marks 3,201 of its records with the
   conjugation-class sign `¦ €N`, so its root layer is not only present but explicitly
   labelled — and it is the same layer the collation census found to be almost perfectly
   alphabetical on its own (0.50 % violations) while disordering the nest around it.
2. **SKD, VCP and WIL have no root layer in this sense.** Their `derived_only` counts —
   632, 592, 577 — say the root's *material* is there, reachable through a headword that
   extends the root, while the bare root is not a key. For SKD and VCP this is a keying
   convention, not an absence of verb lexicography: M4
   ([`m4_indigenous.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m4_indigenous.py))
   recovers gaṇa, pada and transitivity for thousands of their roots from the dhātupāṭha
   apparatus inside the entries. What this census measures is that the apparatus hangs off a
   key that is not Whitney's bare root — it carries anubandhas, a preverb, or a citation
   ending, so the root is a *prefix* of the key and lands in `derived_only`. The
   `citation_root` column shows the specific hypothesis "the root is keyed with a nominative
   ending" is false: 3 roots in SKD, 0 everywhere else.
3. **Finite forms are rare and the test is a lower bound.** 35 roots in WIL and VCP, 14 in
   PWG and PW, 2 in MW and SKD, 0 in AP. The test recognises thematic present forms only
   (`root` + ending); it does not build guṇa or vṛddhi grades, so *bhū* → *bhavati* is not
   caught. A dictionary that systematically lemmatised strong-grade finite forms would show
   up here as `derived_only`, not as `finite_form`. No dictionary shows a finite-form policy
   under this test; the claim the census supports is the weaker "none of the seven keys the
   *weak-stem thematic* present form as its verb lemma".
4. **The absent roots** — 9 in MW, 55 in AP, 89 in SKD — are the per-dictionary exception
   list, in the exceptions CSV with the root in SLP1 and IAST.

## 4. Compounds and derivatives — own head or run-on

Both tests are **self-referential**: the only word list used is the dictionary's own key set,
so each dictionary is measured against itself and no external segmenter is involved.

1. A headword is **compound-like** when its key splits into two pieces that are both
   headwords of the same dictionary, each at least 3 characters.
2. A headword is **derivative-like** when it ends in one of fifteen frequent kṛt/taddhita
   suffixes (tva, tā, tara, tama, maya, aka, ana, ita, in, mat, vat, tṛ, tas, ya, ka) and the
   remainder is itself a headword of the same dictionary.

Each hit is then scored by its record level: level 1 = its own head, level ≥ 2 = a run-on
nested inside another entry.

| Dict | Compound-like | own head | nested | Derivative-like | own head | nested |
|---|---|---|---|---|---|---|
| MW | 148,332 | 12,354 | **135,978 (91.7 %)** | 27,075 | 1,153 | **25,922 (95.7 %)** |
| PWG | 51,312 | 51,312 | 0 | 8,449 | 8,449 | 0 |
| PW | 69,756 | 69,756 | 0 | 9,357 | 9,357 | 0 |
| AP | 23,805 | 10,734 | **13,071 (54.9 %)** | 2,066 | 1,985 | 81 (3.9 %) |
| WIL | 13,663 | 13,663 | 0 | 2,390 | 2,390 | 0 |
| SKD | 6,696 | 6,696 | 0 | 41 | 41 | 0 |
| VCP | 14,211 | 14,211 | 0 | 1,525 | 1,525 | 0 |

1. **MW is the run-on dictionary.** 92 % of its compound-like headwords and 96 % of its
   derivative-like headwords are sub-records. Read together with §2 it gives MW's policy in
   one sentence: *the stem is the lemma, and everything built on it lives inside the stem's
   entry.*
2. **AP splits the two classes.** Compounds are nested more often than not (55 %), but
   derivatives are almost all their own heads (96 %). Its nesting is a nesting of
   **compounds under a first member and of prefixed forms under a verbal root**, not a
   general subordination of derivation.
3. **The five zero rows are a data fact, not a print fact.** csl-orig records an `<e>`
   sub-record level only for MW and AP. PWG, PW, WIL, SKD and VCP have no nesting layer in
   the digitisation at all, so this census can say every compound is its own *record* and
   cannot say whether it was its own *printed* head. §6.2 states what would settle it.
4. **SKD's derivative count (41) is an artefact of §2**, not a finding. Its keys carry
   nominative endings, so *guṇaḥ* + *tā* never matches *guṇatā*: the self-referential suffix
   test is blind in a citation-form dictionary. Its compound count (6,696, less than half of
   VCP's 14,211 on a similar corpus size) is depressed for the same reason. **Do not read
   SKD's two counts in this table as low derivational productivity.**

## 5. The DCS spine, stratified by frequency band

Every lemma of the DCS lemma summary carries a band: 1 hapax, 2 rare (2–9), 3 uncommon
(10–99), 4 common (100–999), 5 very common (1000+). The bands are the strata — asking
whether a dictionary lemmatises a hapax and whether it lemmatises a very common word are two
different questions, and one overall coverage figure hides the difference. Covered = an exact
headword *or* a citation-form key (lemma + ḥ/ṃ).

| Dict | Band 1 (hapax) | Band 2 | Band 3 | Band 4 | Band 5 | All 83,239 |
|---|---|---|---|---|---|---|
| MW | 52.7 % | 72.4 % | 87.4 % | 93.2 % | 97.0 % | **67.6 %** |
| PW | 43.2 % | 58.6 % | 71.0 % | 76.7 % | 90.8 % | 55.1 % |
| PWG | 35.9 % | 51.9 % | 68.1 % | 77.1 % | 90.9 % | 49.2 % |
| AP | 18.5 % | 32.6 % | 59.8 % | 81.9 % | 89.9 % | 33.8 % |
| VCP | 15.7 % | 26.8 % | 48.8 % | 66.8 % | 81.1 % | 28.0 % |
| WIL | 10.6 % | 21.0 % | 45.9 % | 65.4 % | 80.4 % | 23.2 % |
| SKD | 12.6 % | 21.0 % | 40.9 % | 61.1 % | 71.1 % | 23.0 % |

1. **The gradient is the same shape for all seven** — coverage rises monotonically with
   frequency — but its steepness is the policy signature. MW starts at 53 % on hapax legomena;
   AP starts at 19 % and catches up to 90 % by band 5. A dictionary's hapax coverage is a
   measure of how far its macrostructure reaches past the common vocabulary.
2. **The citation-form allowance matters only for SKD.** Everywhere else exact and covered
   are within a rounding of each other; for SKD the lemma + ḥ/ṃ key is what makes the row
   readable at all, which is §2's finding arriving as coverage.
3. **Band 5 is where the dictionaries agree** (71–97 %) and band 1 is where they diverge by a
   factor of five. Any downstream reader layer that joins on the DCS spine should carry the
   band, not the flat coverage figure — an 80 % overall claim about a dictionary is a claim
   about band 4 and 5 vocabulary.
4. **The exceptions CSV** samples 25 absent lemmas per dictionary per band, deterministically
   (first 25 in sorted SLP1 order), so the misses can be inspected stratum by stratum.

## 6. Unknowns and what would refute this

**Unknowns.**

1. **The finite-form test is thematic only.** It cannot see a strong-grade present
   (*bhavati*, *veda*), so "no dictionary lemmatises finite forms" is established only for
   weak-stem thematic forms (§3.3).
2. **Nesting is measured on csl-orig records, not on the printed page.** Five of the seven
   dictionaries carry no `<e>` level, so their run-ons — if the print has any — are invisible
   here (§4.3).
3. **The compound and derivative tests are self-referential** and therefore undercount any
   dictionary whose keys are inflected (SKD, and to a lesser degree AP). They also
   over-accept: a headword that happens to split into two other headwords is counted as
   compound-like whether or not it is historically a compound.
4. **Whitney's root list is one tradition's spine**, not a neutral one. A dictionary
   following a different dhātupāṭha recension will show spurious `absent` rows.
5. **The DCS spine is a ~2021 snapshot** of one corpus; its band assignment, not the
   dictionaries, defines the strata.

**Refutation conditions.**

1. A printed page showing SKD or AP keying bare stems in the stretch where this census counts
   citation forms refutes §2 for that dictionary.
2. For §3: a dictionary in the "marginal root layer" group that, on a hand-checked sample of
   50 of its `derived_only` roots, turns out to key the bare root after all (a parsing miss in
   `k1`, not a keying convention) refutes the verdict for that dictionary.
3. For §4: if a hand count of 100 printed MW pages finds its run-on compounds printed as
   independent heads, the `<e>` level is a digitisers' artefact and the 92 % figure measures
   csl-orig, not MW.
4. For §5: rebuilding the table against a newer DCS release and finding a band-1 coverage
   shift of more than ~5 points for any dictionary means the strata, not the dictionaries,
   are driving the gradient.

_Гасунс_
