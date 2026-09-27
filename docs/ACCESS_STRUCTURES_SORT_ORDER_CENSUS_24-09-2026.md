_Created: 24-09-2026 · Last updated: 25-09-2026 (H5409 — §5a vowel-grade nest filter, refutation condition 3 resolved)_

# Access structures census — sort order of the seven narrative dictionaries

Handoff H5331 (epic E014), Claude Code Opus 5.5 `claude-opus-5-5`. Data: `csl-orig@f4c08c57`.

This page asks one question for each dictionary: *what alphabetisation rule produces the headword order that was actually printed?* The dictionaries are MW, PWG, PW (PWK), AP, WIL, SKD and VCP. It uses Wiegand's term *Zugriffsstruktur* (access structure): the ordering a reader relies on to find an entry. The two versified kośas (ARMH, ABCH) are ordered by concept, not by alphabet, so they are excluded. Their macrostructure is measured by M6 ([`m6_kosha_macrostructure.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_kosha_macrostructure.py)).

Outputs:

1. [`data/lexico/access_structures.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/access_structures.json) holds the per-dictionary verdicts, policy contrasts, segments, homonyms, nesting and AP root nests, plus a sample of counterexamples.
2. [`data/lexico/access_structures_rules.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/access_structures_rules.csv) gives the full rate table (7 dictionaries × views × 74 rules).
3. [`data/lexico/access_structures_counterexamples.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/access_structures_counterexamples.csv) lists all 6,217 best-fit violations with L-ids, page references and IAST.
4. The generator is [`scripts/lexico/m11_access_structures.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m11_access_structures.py) (`npm run build-access-structures`, stdlib only, ~3.5 min, deterministic). Hand-derived pins are in [`tests/forensic/test_m11_access_structures.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_m11_access_structures.py).

## 1. Result — best-fit collation rule per dictionary

| Dict | Best-fit rule | ṃ (anusvāra) | internal ḥ | final ḥ | r + geminate | Alphabet runs | Violations (within runs) | Displaced | Roman-order control |
|---|---|---|---|---|---|---|---|---|---|
| MW | ṃ = class nasal before a stop | class nasal — clear | own slot (vs *s*: clear; vs sibilant: undetermined) | undetermined | undetermined | 1 | 928 / 32,682 = **2.84 %** | 3.06 % | 35.1 % |
| PWG | ṃ = class nasal; ḥ before a sibilant = that sibilant | class nasal — clear | = following sibilant — clear | no final ḥ in the headwords | undetermined | 10 | 378 / 120,153 = **0.31 %** | 0.34 % | 31.1 % |
| PW (PWK) | same as PWG | class nasal — clear | = following sibilant — clear | no final ḥ in the headwords | undetermined | 9 | 250 / 154,422 = **0.16 %** | 0.17 % | 31.9 % |
| AP | ṃ = class nasal; final ḥ ignored | class nasal — clear | undetermined | ignored (vs *s*: clear; vs own slot: undetermined) | undetermined | 1 | 2,725 / 29,127 = **9.36 %** | 15.82 % | 32.8 % |
| WIL | ṃ at its own slot; r+geminate sorts single | own slot (vs *m*: clear; vs class nasal: undetermined) | own slot — clear | undetermined | single — clear | 1 | 726 / 43,962 = **1.65 %** | 1.82 % | 31.0 % |
| SKD | ṃ at its own slot; final ḥ at its own slot | own slot (vs *m*: clear; vs class nasal: undetermined) | own slot — clear | own slot — clear | undetermined | 1 | 467 / 40,537 = **1.15 %** | 1.23 % | 36.9 % |
| VCP | ṃ at its own slot; r+geminate sorts single | own slot (vs *m*: clear; vs class nasal: undetermined) | own slot — clear | undetermined | single — clear | 2 | 743 / 47,154 = **1.58 %** | 1.69 % | 32.3 % |

**Violations** = adjacent headword pairs that go down under the rule, counted within one alphabet run, divided by all within-run adjacent pairs. **Displaced** = the minimum share of headwords that would have to move for the order to satisfy the rule (units minus the longest non-decreasing subsequence, per run). **Roman-order control** = the violation rate if the same order were read as IAST in Latin-alphabet order. At 31–37 % it shows that every dictionary follows the varṇamālā. The best-fit rules score 0.16–9.4 %. Even the *worst* varṇamālā rule in the grid stays within 1.1–14.6 %, so the choice of alphabet is never in doubt. What the grid resolves is the treatment of ṃ, ḥ and geminates.

Two families emerge:

1. **The Petersburg family and its heirs (PWG, PW, MW, AP)** sort ṃ as the nasal of the following stop: aṃkura files as *aṅkura*. PWG and PW also sort ḥ before a sibilant as that sibilant: niḥsāra files as *nissāra*. MW keeps internal ḥ at its own slot against the *s* reading (34 pairs, clear). It cannot be told apart from the sibilant reading (only 14 disagreeing pairs).
2. **The indigenous tradition and Wilson (SKD, VCP, WIL)** keep ṃ at its own slot right after the vowels. They also sort a geminate after r as single: *karṇṇa* = *karṇa*, *varddha* = *vardha*. For VCP (76 pairs) and WIL (46) this is clear. For SKD it is undetermined (18). SKD keys its headwords in citation form (*akṣaraḥ*, *akṣaraṃ*). It files final ḥ at its own slot, and that result is decisive: 3,297 disagreeing pairs against *s* and 1,347 against *ignored*.

## 2. How the rules were tested

1. **The printed order.** The printed order is taken to be the csl-orig record order. Alias records (body `{{Lbody=N}}`) are extra spellings added by the Cologne digitisers, not printed entries, so they are removed. Counts: PW 12,186, AP 9,625, MW 4,352, VCP 1,765, SKD 335, PWG 9, WIL 0. MW and AP give every run-on compound or derivative its own record, marked with an `<e>` level. These nested records are scored separately (§5): the primary order is the level-1 heads. For AP, the heads view also removes paragraph run-ons (fractional L) and the prefix derivatives printed inside a verbal-root nest. Consecutive records with the same key collapse into one position.
2. **The sort key.** The key is `k1`, the accentless normalised SLP1 headword.
3. **The rule grid.** The base order is a ā i ī u ū ṛ ṝ ḷ ḹ e ai o au ṃ ḥ k kh g gh ṅ c ch j jh ñ ṭ ṭh ḍ ḍh ṇ t th d dh n p ph b bh m y r l v ś ṣ s h. Four factors vary, giving 4 × 3 × 3 × 2 = 72 rules:
   - ṃ: own slot / the class nasal before a stop / class nasal there and *m* elsewhere / always *m*
   - internal ḥ: own slot / the following sibilant / always *s*
   - final ḥ: own slot / *s* / ignored
   - r + geminate: kept / single
   Two controls are added: raw SLP1 byte order and Latin-alphabet IAST order.
4. **Alphabet runs.** Supplements and Nachträge are separately sorted runs. A drop is treated as a new run when the initial letter goes backwards *and* the next 10 headwords all sort below the previous 10. A single misplaced headword can never trigger this. Inside one initial letter, a block inversion stays a counted violation.
5. **Best fit.** The best fit has the fewest within-run violations. Ties go to fewer displaced headwords, then to grid order, and all tied rules are listed. Overall rates cannot settle a factor, because most adjacent pairs never touch ṃ or ḥ. Each factor is therefore judged by **pairwise contrasts**, using only the adjacent pairs where two of its policies disagree, with the other factors held at best fit:
   - fewer than 30 disagreeing pairs: *undetermined*
   - a winner at 3 : 1 or better: *clear*
   - otherwise: *weak*
   `factor_status` in the JSON states, for each factor, what the chosen policy rejects and what it cannot be told apart from.

The "undetermined" entries in §1 are real limits of the evidence, not guesses:

1. SKD, VCP and WIL already spell ṃ before a stop as the class nasal in `k1`. That leaves only 11–21 pairs on which *own slot* and *class nasal* could disagree.
2. PWG and PW headwords are stems and never end in ḥ.
3. MW, WIL and VCP have fewer than 10 pairs that separate the final-ḥ readings.

## 3. Alphabet runs (segments)

1. **PWG — 10 runs.** Main text vol. 1 (pp. 1-0001–1142). A short correction list, pp. 1143–1145 (*akūpāra* … *upavyākhyāna*). Then each volume's Nachträge, which continue alphabetically into the next volume's main text, restarting at:
   - 1-1147 *aṃśa*
   - 2-1101 *akaruṇa*
   - 3-1013 *jaṃh*
   - 4-1217 *naṭ*
   - 5-0941 *a*
   - 5-1677 *ativartavya*
   - 6-1511 *yathātatham*
   - 7-1685 *a*
2. **PW — 9 runs.** The main text of all seven volumes forms one ascending run of 131,908 headwords (*a* … *hvāla*). After it come the supplements, which csl-orig numbers from L 200002. The last supplement of vol. 7 splits in two (7-289-a and 7-384-1a).
3. **VCP — 2 runs.** pp. 35–1594 run *a* … *auṣmya*. p. 1597 opens with entries for the letters themselves (*a*, *ā*, *i*, *ī*, *u*, …) before the consonant words. That is the one restart.
4. **MW, AP, WIL, SKD — 1 run each.** MW's Additions and Corrections (pp. 1308 ff.) do not appear as a run: 6,202 of their 6,291 records carry fractional L-ids, meaning the digitisers merged them into alphabetical place. Their order therefore cannot be tested from the data.

## 4. What the violations are

Violations were classified by the common prefix of the two headwords in each violating pair:

| Dict | Violations | Ending variants (differ only at the end) | Common prefix ≥ 4 | Prefix 2–3 | Prefix 0–1 (long-range) |
|---|---|---|---|---|---|
| MW | 928 | 800 (86 %) | 50 | 70 | 8 |
| PWG | 378 | 53 | 129 | 131 | 65 |
| PW | 250 | 61 | 131 | 46 | 12 |
| AP | 2,725 | 1,198 (44 %) | 857 | 603 | 67 |
| WIL | 726 | 150 | 463 (64 %) | 108 | 5 |
| SKD | 467 | 167 | 199 | 83 | 18 |
| VCP | 743 | 215 | 388 | 126 | 14 |

Counterexamples (page, preceding → following headword):

1. **MW — a stem followed by its own forms and derivatives.** Examples: 1,3 *akarā* → *akaraṇa*; 2,1 *akāraṇe* → *akāraṇāt*; 2,1 *akāle* → *akālatas*. One merged-supplement case: 1308,1 *akiṃcid* → *akiñcana*. 86 % of MW's violations differ only at the end, which is a stem-grouping habit inside the level-1 sequence, not a collation error.
2. **PWG — scattered single misfilings.** Examples: 1-0058 *aṅghāri* → *aṅghas*; 1-0155 *adhośuka* → *adhokṣaja*; 1-0199 *anukārin* → *akārya*. The last is a long-range misfiling: *akārya* is a homonym also printed at 1-0009.
3. **PW.** Examples: 1-004-a *akṣapari* → *akṣaparājaya*; 1-022-c *atiprāpti* → *atiprāṇapriya*; 1-027-b *atyuvīśi* → *atyulbaṇa*.
4. **AP — derivatives that change the root vowel.** Examples: 0034-2 *añj* → *akta*; 0040-2 *atigam* → *atiga*; 0027-2 *aṅgīkṛ* → *aṅgīkāraḥ*. Nests like these escape the prefix-based heads filter (§5).
5. **WIL — local block reorders.** Examples: 001 *aṃśabhāj* → *aṃśana*; 002 *akarmman* → *akarmmakṛt*, where the *-an* stem is printed before its compounds; 003 *akrodha* → *akriya*.
6. **SKD.** Examples: 1-001-a *aḥ* → *aṛṇī*; 1-005-c *akṣaraḥ* → *akṣaraṃ*, citation-form keys in which the ending is not a sort level; 1-006-c *akṣīvaṃ* → *akṣībaḥ*.
7. **VCP.** Examples: 0037,a *aṃsatra* → *aṃsakūṭa*; 0041,a *akrāntā* → *akratu*; 0046,b *akheṭika* → *akhāta*.

The CSV holds every violation with both L-ids. It also flags the pairs that some alternative rule would have ordered correctly (`sensitive_to_anusvara_visarga_policy`).

## 5. Homonyms and nesting

**Homonyms** are the same key on two or more records within one run.

| Dict | Groups | Contiguous | Numbered with `<h>` | `<h>` ascending | `<h>` gapless from 1 |
|---|---|---|---|---|---|
| MW | 6,317 | 90.6 % | 340 | 99.7 % | 87.4 % |
| PWG | 2,655 | 98.8 % | 2,541 | 99.96 % | 97.2 % |
| PW | 3,336 | 99.8 % | 3,306 | 100 % | 99.4 % |
| AP | 482 | 47.5 % | 4 | — | — |
| WIL | 626 | 96.0 % | 0 | — | — |
| SKD | 1,396 | 98.1 % | 0 | — | — |
| VCP | 888 | 94.4 % | 0 | — | — |

1. **MW.** Most non-contiguous groups are a main-text record plus a merged supplement record, e.g. *akula* at 2,2 and at 1308,1.
2. **PWG and PW.** 12,353 and 9,923 headwords are repeated across runs: a Nachträge entry re-treats a main-text headword.
3. **AP.** Only 47.5 % of homonym groups are contiguous. The verbal root and the noun with the same key sit in different nests, e.g. *ativartanam* at 0045-2 and 0046-1.

**Nesting.**

1. **MW.** 81.8 % of printed records are nested sub-records. 54.7 % of them begin with their head's key. Sibling sub-records under one head descend in 2.4 % of adjacent pairs.
2. **AP.** 44.6 % of records are nested, 22.1 % extend the head's key, and the sibling descent rate is 9.1 %.
3. **AP root nests** — the 3,198 records marked as verbal roots, found by the conjugation mark `¦ €N`:
   - The roots, taken alone, are almost perfectly alphabetical: 16 violations in 3,184, or 0.50 %.
   - The pair right after a root descends 27.1 % of the time, against 5.9 % ten or more headwords later.
   - AP's 9.4 % rate is partly a nest effect, not a collation effect. The heads view already removes 8,316 paragraph run-ons and 7,322 prefix derivatives (the `main` view scores 10.6 %). H5331 hypothesised that the remainder is derivatives whose stem changes the root vowel (guṇa/vṛddhi) and so cannot be recognised by key prefix. **H5409 tested that hypothesis and it does not hold — see §5a.**

### 5a. The vowel-grade nest filter (H5409) — the hypothesis fails

The `heads_nest` view collapses a root and the following headwords whose stem is the root's guṇa, vṛddhi or zero grade into one sort unit keyed on the root. Grades are taken on the root's last vowel: √kṛ `kf` → *kf, kar, kār*, so *kāra* and *karaṇa* both fall into √kṛ's nest; √budh `buD` → *buD, boD, baud*; √gam → *gam, gām*.

| View | Units | Descent rate | Displaced rate |
|---|---|---|---|
| `main` | 44,403 | 10.63 % | 17.32 % |
| `heads` | 29,128 | 9.36 % | 15.82 % |
| `heads_nest` | 27,212 | **8.19 %** | 13.08 % |
| roots only | 3,184 | 0.50 % | — |

1. The filter removes a further **1,519 headwords** as vowel-grade derivatives (9,217 nest drops against the heads view's 7,322).
2. It removes **12.4 %** of AP's 9.36 % rate, and closes **13.1 %** of the distance between the heads view and the 0.50 % roots-only floor. The pre-registered bar was 75 % of that gap for *confirmed* and 25 % for *partly*.
3. **Verdict: refuted.** Vowel-grade nesting is real but small. It explains roughly one violation in eight, not the bulk.
4. The residual disorder is not concentrated at the root either. Right after a root the rate falls from 27.1 % to 19.8 %, but ten or more headwords later it is still 5.9 %, and 676 of the 2,229 remaining descents sit in that far bucket. Much of what is left is prefix-family ordering inside a section rather than root nesting at all: *atikrāntiḥ* → *atikramaṇam* (0040-1), *aticchedaḥ* → *aticchandaḥ* (0041-1), *atithin* → *atithigvaḥ* (0042-1) — Apte groups a preverb's derivatives semantically, and the vowel-grade filter never sees them because their heads are not root records.
5. Known limits of the grade mapping, each a source of surviving counterexamples: samprasāraṇa (√yaj → *iṣṭa*), nasal-infix loss (√añj → *akta*, visible at 0034-2 → 0036-1), and set/anit ā-roots whose derivatives take *-i-* (√sthā → *sthita*). A mapping that covered them would be a morphological analyser, not a collation census.

## 6. Unknowns and what would refute this

**Unknowns.**

1. **Running heads** — the catchwords at the top of the printed page — are not in csl-orig. This census cannot test them.
2. **Undetermined factors.** The factors marked undetermined in §1 need either more disagreeing pairs or the printed front-matter statement of the collation rule.
3. **MW's merged Additions** (pp. 1308 ff.) cannot be tested as a separate run from this data.
4. **Digitiser reordering.** csl-orig order is assumed to be print order. Where the digitisers reordered records (fractional L-ids), the census measures their order.

**Refutation conditions.**

1. A *printed* page image showing a sequence that the best-fit rule orders differently, where csl-orig follows the image, refutes that dictionary's rule. Example: an MW page with *aṃśa* before *aṅkura*.
2. Front matter that states a different treatment of ṃ, ḥ or geminates for a factor marked *clear* refutes that factor.
3. For AP: if a vowel-grade-aware root filter (guṇa/vṛddhi) does not bring the heads-view rate toward the 0.5 % roots-only rate, the nest explanation in §5 is wrong. **Tested (H5409, 24-09-2026): the condition fired — REFUTED.** The `heads_nest` view scores 8.19 % against the heads view's 9.36 %, closing 13.1 % of the gap to the 0.50 % floor, far below the pre-registered 75 % bar (§5a). Vowel-grade nesting accounts for about an eighth of AP's disorder; the rest needs a different explanation — prefix-family grouping is the leading candidate, and it is untested.

_Гасунс_
