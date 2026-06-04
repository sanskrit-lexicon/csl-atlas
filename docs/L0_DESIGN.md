# Phase L0 Design — Convention-fingerprint cladogram

**Version**: 1.0 · **Date**: 2026-05-16 · **Status**: design-locked, ready to implement
**Companion to**: [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md)

L0 is the **cheapest, fastest, most validatable** phase in the lexicography stream. It produces the first phylogenetic tree of CDSL dictionaries using only Patel-2016-style "convention fingerprints" — no XML parsing of any source dictionary. Estimated effort: 2-3 days end-to-end.

---

## 1. Goal

Produce a **defensible, multi-encoding, multi-metric, validated** convention-fingerprint cladogram of all 35 GitHub CDSL dictionaries (and the 8 scan-only dicts where Patel 2016 supplies fingerprints). The cladogram is published to the dashboard, the data is downloadable, and the analysis is the empirical core of **Paper M §4.1.5** and **Paper H §5**.

---

## 2. Fingerprint dimensions (extended from Patel's 7)

Per author decision: include all three suggested dimensions plus *as many additional as feasible*.

### 2.1 Patel's 7 (canonical from PDF)
1. Anusvāra before consonants (6 options)
2. Duplication after `r` (2 options)
3. Words ending with `-at` from śatṛ/vatup (5 options across 3+2 sub-conventions)
4. Inflected vs uninflected headword form
5. Anusvāra of verbs
6. ṛkārānta words (3 options)
7. vas/yas suffixes (4 options)

### 2.2 Sandhi & compound handling (3 new dimensions)
8. **Sandhi handling at compound boundary** — preserved (e.g. `dharmakarman`) vs split (e.g. `dharma-karman`) vs both forms listed
9. **Compound-headword separation** — hyphen vs space vs merged-into-one-word
10. **Variant-headword inclusion (`<k2>`)** — none / few (<5%) / many (>5% of entries)

### 2.3 Polysemy & sense numbering (3 new dimensions)
11. **Sense numbering style** — Arabic `1./2./3.` vs Roman `I./II./III.` vs alpha `a)/b)/c)` vs Sanskrit `prathama/dvitīya` vs unnumbered
12. **Sense-internal separator** — semicolon `;` vs comma `,` vs period `.` vs colon `:`
13. **Sub-sense indentation** — present (hierarchical) or flat

### 2.4 Citation conventions (3 new dimensions — captures the truncation insight)
14. **Citation depth** — full (`Rv. 1.22.16`) / partial (`Rv. 1.22`) / minimal (`RV.`) / mixed
15. **Citation format style** — abbreviated text-name (`RV.`) vs full (`Rigveda`) vs Sanskrit (`ṛgveda`)
16. **Mahābhārata edition reference** — Pune/Bombay vs critical edition (`MBh. 1.2.3` vs `MBh. crit. 1.2.3`)

### 2.5 Grammar / gender markers (2 new dimensions)
17. **Grammar marker style** — abbreviated (`m.`/`f.`/`n.`) vs full (`masc.`/`fem.`/`neut.`) vs Sanskrit (`puṃ.`/`strī.`/`napuṃ.`)
18. **Verb-class marker style** — Roman (`P.IX`) vs Arabic (`9.P`) vs Sanskrit (`paraspariṣi 9`)

### 2.6 Etymology & cross-reference (3 new dimensions)
19. **Etymology presence** — none / partial / full IE-cognate
20. **Cross-reference syntax** — explicit pointer (`see X`) vs `<k1>X</k1>` vs italic vs absent
21. **Loanword marker** — Persian/Arabic/Greek loanword tagged or not

### 2.7 Vedic & accent (2 new dimensions)
22. **Vedic accent preservation** — present (`āgnís`) or absent (`āgnis`)
23. **Vedic-only marker** — does the dict flag Vedic-only forms

### 2.8 Loose ends (4 new dimensions)
24. **Frequency / rarity marker** — present (e.g. `(rare)`) or absent
25. **Indeclinable marker style** — `ind.` vs `inv.` vs `nipāta` vs unmarked
26. **Pāṇinian sūtra reference** — `Pāṇ. 3.1.4` cited or not
27. **Source-language identification within entries** — bilingual gloss markers

### 2.9 Etymology / derivation richness (3 new dimensions, added 2026-05-16)
28. **Etymology presence rate** — % of entries containing an etymology marker (e.g. WIL's `E.` prefix, AP's `der` block, MW's `√` root pointer). Binary if rate >5%
29. **Etymology mean-length** — average chars in etymology block per entry containing one
30. **Distinct etym-marker patterns** — count of unique opening tokens (e.g. `E.`, `der.`, `from`, `cf.`, `√`, `Skr.`) → captures editorial style consistency

**Total: 30 fingerprint dimensions** (Patel's 7 + 23 additions).

Each dimension is encoded as a categorical variable with 2-6 possible options. Many options are extracted directly from each dict's published documentation; others require a brief sample-survey of 10-50 entries per dict.

---

## 3. Three encoding schemes (computed in parallel)

For each (dict, dimension) pair where the dict follows multiple options:

### Encoding A: Set-membership (binary vector)
```
PWG[convention_1] = [0, 0, 0, 0, 1, 0]    # only option 1.5
AP90[convention_1] = [1, 0, 0, 0, 1, 0]   # options 1.1 + 1.5
```
- Matrix shape: 35 × (sum of options across all dimensions ≈ 100)
- Distance: Hamming on bits OR Jaccard on option sets

### Encoding B: Primary + secondary (rank-ordered)
```
PWG[convention_1] = [5, _]                # primary 1.5, no secondary
AP90[convention_1] = [5, 1]               # primary 1.5, secondary 1.1
```
- Matrix shape: 35 × (27 dims × 2 ranks = 54)
- Distance: rank-aware (e.g. Spearman per dim, then averaged)

### Encoding C: Inconsistency-flagged (single primary, with consistency score)
```
PWG[convention_1] = (5, 1.0)              # option 5, fully consistent
AP90[convention_1] = (5, 0.6)             # mostly 5, but inconsistent
```
- Matrix shape: 35 × 27 + 35 × 27 inconsistency scores
- Distance: weighted by inconsistency penalty

---

## 4. Three distance metrics (computed in parallel for each encoding)

### Metric 1: Weighted Hamming
```
d(A, B) = sum over dims i of: weight_i * (A[i] != B[i])
weight_i = -log(probability of i across all dicts)  # rare options weighted higher
```

### Metric 2: Plain Hamming
```
d(A, B) = sum over dims i of: (A[i] != B[i])
```

### Metric 3: Jaccard (for set-membership encoding)
```
d(A, B) = 1 - |A ∩ B| / |A ∪ B|
```

For encodings B and C, Jaccard adapts via dim-wise computation.

---

## 5. Cladogram production (3 algorithms × 3 encodings × 3 metrics = 27 trees)

For each (encoding, metric) combination:
- **UPGMA** (Unweighted Pair Group Method with Arithmetic Mean) — assumes molecular-clock-like
- **Neighbor-Joining** — handles uneven divergence rates
- **Bayesian** (MrBayes-style or simple beam-search posterior) — full posterior over trees

Output: 27 candidate trees. Cluster comparison via **Robinson-Foulds distance** between trees → identify which choices matter most.

The **canonical published tree** is the Bayesian consensus across the 9 (3 encodings × 3 metrics) configurations.

---

## 6. Validation

### 6.1 Known-edge recovery score
For each known/likely edge (PWG→PWK, MW72→MW, AP90→AP, PWG→MW, etc. — 14 edges in roadmap §9):
- Check whether the edge appears in the predicted tree (parent-of relation)
- Recovery rate = recovered_edges / total_known_edges

Target: ≥10/14 = 71% on the canonical tree.

### 6.2 Leave-one-out cross-validation
- For each known edge (A → B):
  1. Remove edge from training set
  2. Build tree without that knowledge
  3. Check whether B's nearest neighbour in the tree is A (or A's predicted descendant)
- Score: per-edge accuracy.

### 6.3 Bootstrap confidence intervals
- 1000 bootstrap resamples of the fingerprint matrix
- For each resample, build the tree
- Compute frequency of each edge across bootstrap trees
- Report 95% CI for each predicted edge

### 6.4 Acceptance criteria
- Known-edge recovery ≥ 70%
- LOO accuracy ≥ 60%
- All "strongest" edges (PWG→PWK, MW72→MW, AP90→AP) appear with ≥80% bootstrap support

If criteria not met → re-examine encoding/metric choices, document failure modes in paper as honest limitation.

---

## 7. Outputs

### 7.1 Data products (downloadable from `/data/`)
| File | Description |
|---|---|
| `convention_fingerprint.csv` | 35 × 27 matrix, primary option per dim per dict |
| `convention_fingerprint_setmember.csv` | 35 × 100 binary matrix (encoding A) |
| `convention_inconsistency.csv` | 35 × 27 consistency scores (encoding C) |
| `pairwise_distances/<encoding>_<metric>.csv` | 35 × 35 distance matrix per config |
| `trees/<encoding>_<metric>_<algo>.newick` | 27 trees in Newick format |
| `tree_comparison_robinson_foulds.csv` | 27 × 27 RF distances between configs |
| `bootstrap_support.csv` | edge-level bootstrap support |
| `validation_report.json` | recovery scores + LOO + CIs |

### 7.2 Dashboard page
**New page**: `/lexicography/conventions.md`

Sections:
1. The convention-fingerprint method (textual explanation, 2-3 paragraphs)
2. Per-dict fingerprint table (interactive, sortable, 35 × 27)
3. Pairwise distance heatmap (35 × 35, switchable by encoding+metric via dropdown)
4. **Lead chart**: the canonical Bayesian-consensus cladogram
5. Tree comparison: small-multiples grid of all 27 trees, each labelled
6. Validation panel: recovery score + LOO accuracy + bootstrap CIs
7. Discussion: which conventions discriminate most + which dicts are outliers

### 7.3 Paper sections
- **Paper M §4.1.5**: convention fingerprint as cheap inheritance signal
- **Paper M §4.4.1**: validation methodology (known-edge recovery, LOO, bootstrap)
- **Paper M §5.2**: results from the 9-configuration sensitivity analysis
- **Paper H §5.1**: PWG → PWK → SCH chain confirmed at >95% bootstrap support
- **Paper H §5.2**: MW lineage from PWG/PWK at quantified strength
- **Paper H §5.3**: SKD as outlier — quantified evidence of indigenous origin

---

## 8. Implementation steps (ordered, ~3 days total)

| Step | Task | Effort |
|---|---|---|
| 1 | Extract Patel's 7 conventions into structured CSV from the PDF | 0.5 day |
| 2 | Manual annotation of 20 additional dimensions for top 15 dicts (PWG, PWK, MWS, MD, AP, AP90, GRA, FRI, SCH, BHS, VEI, BUR, BEN, CCS, CAE) | 1 day |
| 3 | Auto-detect remaining annotations from each dict's source XML where parseable | 0.5 day |
| 4 | Build encoding scripts (A, B, C) | 0.25 day |
| 5 | Build distance scripts (3 metrics) | 0.25 day |
| 6 | Build clustering scripts (UPGMA, NJ, Bayesian) | 0.5 day |
| 7 | Validation: known-edge recovery, LOO, bootstrap | 0.5 day |
| 8 | Render trees + comparison heatmaps as Observable charts | 0.5 day |
| 9 | Write `/lexicography/conventions.md` page | 0.25 day |
| 10 | Draft Paper M §4.1.5 + §5.2 + Paper H §5 paragraphs | 0.5 day |

**Total: ~4.75 days** (was estimated 1-2; expanded due to 27-dim scope + 9-config rigour).

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Patel's per-dict annotations don't cover all 36 dicts for all 7 conventions | Mark as "unknown" in cell; allow Hamming to skip unknowns; report missing-data ratio |
| Adding 20 new dimensions requires manual annotation; risk of bias | Multi-annotator (you + me + a 3rd if available); inter-rater agreement κ |
| Bayesian tree posterior is computationally expensive for 35 dicts | Use heuristic search with 1000 iterations; full MCMC only for paper-final tree |
| Bootstrap with multi-encoding × multi-metric is exponential | Cap at 100 bootstraps for non-canonical configs; full 1000 only for canonical |
| Some dicts (e.g. KRM with verbs only) may not fit the 27-dim schema | Mark as "scope-limited"; exclude from primary tree but annotate in supplementary tree |
| Russian dicts (KNA, KOW) and Czech (FRI) have no Patel coverage | Phase L0 + manual annotation by you/me; proxy from sample entries |

---

## 10. Decision log (locked in 2026-05-16)

| Question | Decision |
|---|---|
| Fingerprint dimensions beyond Patel's 7 | **27 total** (added 20: sandhi, polysemy, citation, grammar, etymology, Vedic, etc.) |
| Multi-option encoding | **All three in parallel** (set-membership + primary/secondary + inconsistency-flagged) |
| Distance metric | **All three in parallel** (weighted Hamming + plain Hamming + Jaccard) |
| Clustering algorithm | **All three** (UPGMA + NJ + Bayesian) |
| Validation | **All three** (known-edge recovery + LOO + bootstrap CIs) |
| Tree count | **27 candidate trees** (3 encodings × 3 metrics × 3 algos) |
| Canonical tree | **Bayesian consensus across 9 configs** (excluding the 3 algorithm sweep dimension since Bayesian is the most rigorous) |

---

## 11. Decisions locked (2026-05-16 round 2)

| Question | Decision |
|---|---|
| Manual annotation split | **Co-annotation**: M.G. annotates ~1-2 hours; Claude annotates ~2-3 hours. Inter-rater Cohen's κ reported in paper |
| Auto-extraction sample size | **Adaptive**: sample until per-convention assignment converges at 95% confidence (typical: 10-50 entries) |
| Russian/Czech (KNA, KOW, FRI) | **Include in main tree** with explicit "limited prior literature" caveat; add Russian-tradition convention options where they appear |
| Specialised (AMAR, KRM, VEI, PUI, INM, MCI, BHS) | **Supplementary tree only**, with focused per-dict commentary; main tree = general bilingual dicts |
| Annotation tool | CSV editing in shared spreadsheet (fastest; reproducible diff via git) |
| Ready to start L0? | **HOLD** — one more clarification pending from M.G. |

## 12. Annotation workflow (locked)

1. Claude generates `data/fingerprint_annotation_template.csv` — 35 rows (dicts) × 27 cols (dimensions) + 27 confidence cols
2. Claude pre-fills:
   - Patel's 7 conventions from the PDF (free)
   - Auto-extracted dimensions where parseable from XML (e.g. `<k2>` count)
3. Hands off to M.G. for the high-judgement dimensions (~30-50 cells, 1-2 hours): citation depth conventions, etymological style, anything where M.G.'s domain expertise outperforms Claude's pattern matching
4. M.G. returns the file via PR or direct push; Claude completes the remaining cells
5. Both annotators independently review a 10% overlap sample → Cohen's κ
6. Final fingerprint matrix versioned in `data/convention_fingerprint.csv` with columns: `dim_value, source (patel|auto|annotator|consensus), confidence`

This makes the L0 inter-rater agreement defensible and the annotation provenance traceable.

## 13. Multi-volume publication-year handling (added 2026-05-16)

Many CDSL dictionaries are **multi-volume publications spanning years or decades**, not single-year publications. This affects the temporal-plausibility check in the inheritance score.

### Examples of multi-volume dicts

| Dict | Range | Vols | Notes |
|---|---|---|---|
| PWG | 1855-1875 | 7 | vol1 1855 (a-), vol2 1858, vol3 1861, vol4 1865, vol5 1868, vol6 1871, vol7 1875 |
| PW | 1879-1889 | 7 | abridged Petersburger; same fascicle structure |
| VCP | 1873-1884 | many | indigenous Skt-Skt; multi-fascicle |
| SKD | 1822-1886 | many | original 1822, Cologne uses later 1886 edition |
| AP | 1957-1959 | 3 | revised Apte 3-volume Pune edition |
| PD | 1976-ongoing | 37+ planned | only first ~6 vols (a- through aMS-) published |
| MCI | 1976-1993 | 15+ planned | partial-by-letter publication |

### MW72 ⊂ PWG case study (the prefatory evidence)

> "MW72 (1872) preface notes use of early PWG volumes (1855-1865 fascicles)"

Means: MW72's terminus a quo for PWG-derivation is volume 4 (1865). Vols 5-7 of PWG (1868-1875) **could not** have been used by MW72 because they post-date it. So a "PWG → MW72" inheritance edge applies **only** to the lemmas in vols 1-4 (typically letters a- through approx. p-).

### Updated temporal-plausibility logic

For source A, inheritor B:

```python
# Old (single-year):
plausible = (year_A <= year_B)

# New (range-aware):
A_start, A_end = year_range(A)
B_start, B_end = year_range(B)

# Strong: every volume of A predates B's start
strong_plausible = (A_end <= B_start)

# Partial: A started before B finished, so SOME vols of A predate B
partial_plausible = (A_start < B_end)

# Lemma weighting: if partial, restrict inheritance scoring to lemmas
# that fall in A's published-by-year(B_start) letter range
```

The new inventory CSV `data/dictionary_inventory.csv` includes columns:
- `start_year` — earliest volume publication year
- `end_year` — latest volume publication year (or "ongoing")
- `n_volumes` — number of volumes
- `letter_coverage` — `full`, `partial-a-only`, `partial-by-letter`, etc.

### Per-letter (fascicle) granularity (Phase P, deferred)

Even finer: per-letter coverage per dict (e.g. PWG vol1 covers `a-`, vol4 covers `n-p`). Requires:
- Fascicle metadata extraction from each dict's preface (Phase P — Preface Analysis, deferred)
- Per-lemma "first published by" date attribution

For L0, we use range-only. Per-letter detail comes in Phase P.

## 14. KCH (Kochergina 1978) added (2026-05-16)

The standard modern Sanskrit-Russian dictionary (Vera A. Kochergina, ~30k entries) is added to the inventory as `in_github=planned`, `in_sanhw1=no`, source TBD. KCH joins the Sanskrit-Russian family (with KOW, KNA) — three Sanskrit-Russian dictionaries spanning 124 years (KOW 1854 → KNA 1893 → KCH 1978).

**Comparison angle for Paper L**: this is the most coherent national lexicographic tradition in the corpus (entirely Russian-target, no other languages in this family).

## 15. Etymology / derivation measurement plan (added 2026-05-16)

Per author decision: **all three signals** (binary + frequency + length distribution).

### Operationalisation per dict

For each dict's source XML:

```python
def measure_etymology(dict_xml):
    entries = parse_entries(dict_xml)
    n = len(entries)
    etym_count = 0
    etym_lengths = []
    marker_patterns = set()
    
    for entry in entries:
        text = entry.body
        # Search for etymology markers (per-dict pattern)
        for pattern in ETYM_PATTERNS[dict_code]:
            match = pattern.match(text)
            if match:
                etym_count += 1
                etym_block = extract_etym_block(text, match)
                etym_lengths.append(len(etym_block))
                marker_patterns.add(match.group(0)[:10])  # opening token
                break
    
    return {
        'etym_presence_pct': etym_count / n,
        'etym_mean_chars': mean(etym_lengths) if etym_lengths else 0,
        'etym_marker_patterns': len(marker_patterns)
    }
```

### Per-dict known etym-marker patterns

| Dict | Marker | Notes |
|---|---|---|
| WIL | `E.` prefix | Wilson's standard etymology marker |
| AP | `der.` block at end | derivation block |
| MW | `√` for verbal roots; `cf.` for cognates | most extensive |
| PWG | full etymological prose | not just markers |
| MD | `Skr.` for Sanskrit cognates | sparse |
| BHS | `Pkt.` for Prakrit, `Pa.` for Pali cognates | comparative |
| BOP | full Latin etymology prose | extensive (Latin tradition) |

This becomes fingerprint dimensions 28-30 (added in §2.9 above).

## 16. Phase P — Preface Analysis (NEW, deferred)

A dedicated phase for parsing the **preface text** of each digital dict to extract:

- **Documented derivation** (e.g. MW72 preface says "used PWG vols 1-4")
- **Per-volume publication years**
- **Per-letter coverage**
- **Acknowledged sources** (other dicts cited in the preface)
- **Editorial methodology** (e.g. "we corrected typos in PWG by reference to manuscript X")

**Effort**: ~2 days per dict × 35 dicts = 6-8 weeks (could be parallelised)
**Output**: `data/dict_prefaces.csv` with structured per-dict ground-truth lineage
**Use**: Phase P data validates the L0/L8 cladograms; supplies Paper H §2's narrative
**Status**: deferred until L0 + L1.5 + L2 results are reviewed

## 17. WIL Nirukta deep-dive (Phase L0.5, added 2026-05-16)

WIL's `.E.` is **Indian Nirukta** (semantic etymology via Pāṇinian morphology), not Western linguistic etymology. Per author decision, all three sub-analyses are planned:

### L0.5.A — Token extraction
For each of WIL's 39,701 `.E.` blocks:
- Extract every SLP1 token between `{#…#}` markers (these are dhātu/morpheme references)
- Build a frequency table: which dhātus appear most often as derivation sources?
- Build a frequency table: which suffixes/affixes are most common (`vun`, `ghaY`, `ac`, `kvip`, etc.)?
- Build a frequency table: which upasargas (preverbs) appear?

Output: `data/wil_nirukta_dhatus.csv`, `data/wil_nirukta_suffixes.csv`, `data/wil_nirukta_upasargas.csv`

### L0.5.B — Pāṇinian framework classification
Each `.E.` block is one of:
- **kṛt-derivation** (verb root + primary suffix → noun: e.g. `kṛ + ghaY → kāra`)
- **taddhita-derivation** (noun + secondary suffix → derived noun: e.g. `puruṣa + a → pauruṣa`)
- **uṇādi-derivation** (irregular kṛt-like suffixes from the Uṇādi-sūtras)
- **samāsa-decomposition** (compound analysis)
- **upasarga-prefixation** (preverb + verb)
- **other** (women's-name particles, denominative verbs, etc.)

Method: regex-based classifier on suffix forms; manual labeling of 200 sample `.E.` blocks; build classifier; report precision/recall.

Output: `data/wil_nirukta_classification.csv`

### L0.5.C — Comparison with classical Nirukta sources
- Yāska's Nirukta (the foundational work, ~6th c. BCE) — his own dhātu-derivation method
- Pāṇini's Aṣṭādhyāyī sūtras — formal grammatical rules
- Are WIL's derivations ANY of: (a) verbatim from Yāska, (b) from Pāṇinian rules, (c) Wilson's own scholarly inference?

Method: cross-reference WIL's most-cited dhātu derivations against (a) digital Yāska's Nirukta, (b) Pāṇinian sūtra-corpus.

Effort: ~2 weeks (substantial Sanskrit-philology research). Output: paper-quality table.

**This becomes a possible separate paper N — *The Nirukta tradition embedded in 19th-century Indological lexicography: a corpus analysis of Wilson's etymological notation*.**

## 18. Bopp-dependence test for MW (Phase M3-Bopp, added 2026-05-16)

MW (1899) has 0 direct "Bopp" citations — but per author intuition, MW's etymology approach derives from Bopp's *Glossarium Sanscritum* (1847).

Test method: **shared cognate-set analysis**.

For lemmas appearing in both MW and BOP:
- Extract MW's cognate notes (`cf. Lat. X`, `Gk. Y`, `Goth. Z`, `Slav. W`)
- Extract BOP's full Latin gloss + cognate prose
- For each shared lemma, compute:
  - Set of cognate languages mentioned (BOP vs MW)
  - Set of cognate forms cited (BOP vs MW)
  - String similarity of cognate phrases
- Aggregate: % of shared lemmas where MW's cognate set ⊆ BOP's

If ≥70%: strong evidence MW used BOP. If 30-70%: partial influence. If <30%: independent traditions.

Output: `data/mw_bopp_cognate_overlap.csv` + paper paragraph in Paper L §6.

## 19. AP-Hindi missing data (action item)

V.S. Apte's **Practical Sanskrit-Hindi dictionary** is the only Apte work with derivation data, and it is **NOT in Cologne**.

**Action item**: contact Prof. Amba Kulkarni (IIT Hyderabad) — known Sanskrit computational linguist — to request the digital data.

Status: deferred until contact made and data received. When/if obtained, Apte derivation analysis joins L0.5 framework.

## 20. Subentry analysis (Phase L0.6, added 2026-05-16)

Per author decision: all three sub-analyses planned.

### L0.6.A — Subentry density per dict
Count occurrences per entry of:
- `Caus.` (causative verbal subentry)
- `Pass.` (passive)
- `Desid.` (desiderative)
- `Inten.` / `Frequent.` (intensive / frequentative)
- `Den.` (denominative)
- `Periphr.` (periphrastic conjugation)
- `WITH` / `with` patterns (preverb-prefixed verbs as subentries)

KPI: mean subentries per entry per dict; distribution.

### L0.6.B — Subentry depth tracking
Does `Caus.` itself have a `Pass.` of the causative? Does the causative have its own `Desid.`? Build a tree of nested subentries per verb.

KPI: max depth per dict; mean depth.

### L0.6.C — Verb × derivation matrix
For every verb in the dict, mark presence/absence of each derivative type. Output: per-dict matrix (n_verbs × ~7 derivation columns).

Use: identify which dicts have most COMPLETE verbal-paradigm coverage. AP and MW expected to have richest coverage. WIL likely sparser.

Output: `data/subentry_density.csv`, `data/subentry_depth.csv`, `data/verb_derivation_matrix_<dict>.csv` per dict.

## 21. Open question

Awaiting clarification.
