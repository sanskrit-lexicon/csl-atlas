# R2 sense-splitter — first-slice findings (2026-05-31)

First real build of **R2** (the per-dict sense splitter, RESEARCH_LAYER_ROADMAP §5.1), run on the 5 anchor lemmas (`gam`, `dharma`, `rāma`, `iti`, `bodhisattva`) across the 8 Western-tagged dictionaries. Script: [`scripts/lexico/sense_split.py`](../scripts/lexico/sense_split.py). Data: `data/lexico/senses_<dict>.jsonl`, `r2_align_<lemma>.json`, `r2_summary.json`. Deterministic, stdlib-only, reads sibling `csl-orig`.

## What it does

1. **Heuristic per-dict sense split** — each dictionary's own markers: AP `∙²N`, AP90/BEN/BHS `{@N@}`, PWG `<div n="N"> N)/a)`, WIL `.²N`. The MW-family (MW, MW72, SCH) use **no per-sense markers** — a run-on `;`-list — flagged `lumped`.
2. **Sanskrit fingerprint per sense** — the SLP1 tokens it carries (`{#…#}`/`<s>`, headword excluded) **plus** `<ls>` citation sigla.
3. **Cross-dict alignment** — Jaccard overlap of fingerprints (A6 = *anchor on Sanskrit*, no gloss translation).

## Headline results

**① Sanskrit-anchoring aligns senses across the language barrier — with no translation.** For `dharma`:

| Aligned senses | J | Shared Sanskrit anchors | Meaning |
|---|---|---|---|
| `ap#4` ~ `ap90#4` | **1.0** | `ezaH`, `zazWAMSavftterapi` + Ms./Ś. | "Duty, prescribed course of conduct" (same sense, two Apte editions) |
| `ap#3` ~ `ap90#3` | 0.57 | `eka eva …` + Ku./H. | "Religious/moral merit, virtue" |
| **`pwg#b)` ~ `ap#3`** | 0.02 | `suhfdDarmo`, `eka`, `eva`, `yaH` + H. | **German** "Gesetz, Brauch, Vorschrift" ↔ **English** "moral merit, virtue" |

The last row is the proof of concept: a **German** PWG sense aligned to an **English** Apte sense purely through the Sanskrit material they share — exactly what A6 promised.

**② Sense granularity is a *tradition* trait, not (yet) a clean time-trend** — a refinement to H1. Explicit-sense counts for `dharma`, by year:

| Year | Dict | Senses |
|---|---|---|
| 1855 | PWG | 3 divisions (lumps within) |
| 1866 | BEN | 11 explicit |
| 1872 | MW72 | **lumped** (~136 `;`-clauses in one bundle) |
| 1890 | AP90 | 22 explicit |
| 1899 | MW | **lumped** |
| 1953 | BHS | 4 (proper-name senses) |
| 1957 | AP | 23 explicit |

The **Apte family** (AP/AP90) enumerates finely (~22); the **Petersburg/MW family** packs everything into one run-on gloss. So sense-granularity tracks lexicographic *school* more than publication year — H1 must control for family. (Within the Apte family, AP 1957 ≈ AP90 1890 — no inflation, as expected for a revision.)

## Limitations (next iteration → full R2)

- **MW splits a lemma across many `<L>` blocks** (homonyms + compounds; 33 for `dharma`); this slice reads only the first block, so MW's counts undercount. Need homonym-block aggregation (the `<hom>` grouping).
- **Verbs are messier than nominals** — `gam` (conjugation classes, preverb sub-entries) needs verb-specific markers (`€N`); nominal lemmas (`dharma`, `rāma`) are the clean demonstrators here.
- The **lumped clause-count** is a rough "implicit-sense" proxy, not a true sense count.
- Apte **compound** sub-senses may slightly inflate counts (Apte has no clean compound-section marker).

## Update — full clusters (2026-05-31, v2)

`sense_split.py` now covers **all four parser families** with **homonym aggregation** (all `<L>` blocks of a lemma, not just the first):

- **Western** (mw, mw72, pwg, ap, ap90, ben, sch, bhs, **wil, cae**) — explicit markers / lumped.
- **Indigenous** (**vcp, skd**) — raw-SLP1 scholastic prose; senses ≈ `iti.`-closed units; fingerprint = `…0` authority sigla (`jE0`=Jaimini) + `"…"`-quoted forms.
- **Reverse** (**ae** / ApteES) — English-keyed, reverse-indexed by its `<s>` Sanskrit equivalents, so a Sanskrit lemma finds the English senses that gloss it (e.g. *dharma* → ae "Duty" = `DarmaH, kartavyaM`).
- **Index** (acc/vei/mci/inm/…) — references, not senses; out of scope.

**Cross-cluster alignment now works** (strong-anchor filter: citation / siglum / content word ≥4 chars):
- `bodhisattva`: **`pwg#1 ~ skd#1`** — PWG (German, Western) ↔ SKD (Sanskrit, indigenous) via shared story-Sanskrit (`jImUtavAhanAt`, `kalpadrumaM`, `kftI`).
- `dharma`: `mw#bundle ~ ben/sch` via shared `<ls>` citations (MBh., Dharmaś.).

**Full-corpus scale proven** (runs in seconds): CAE **40,069** entries → 40,069 senses (1.00/entry — lumps); **BEN 17,310 → 36,177 senses (2.09/entry — enumerates)** — the family contrast holds across the whole dictionary, not just the anchor lemmas.

**Remaining (honest):** the AE reverse index over-matches very common roots (gam → 144 English senses — fine for distinctive words, noisy for `go`-class verbs); SKD headword coverage is partial (works for `Darmma`/`rAma`); indigenous sense-splitting is coarse (`iti`-units); verbs remain coarser than nominals.

## H1 — does sense granularity inflate over time? (family-controlled, full corpus)

[`scripts/lexico/h1_analysis.py`](../scripts/lexico/h1_analysis.py) → [`data/lexico/r2_h1.json`](../data/lexico/r2_h1.json) + `r2_h1.html` (SVG scatter, a Paper-L figure). Metric: **sense-units per entry** over each dictionary's *whole* corpus (explicit markers for enumerating dicts; `;`-meaning-clauses, citations stripped, for lumpers).

**Result: H1 (pure temporal inflation) is NOT supported.** Across 11 general dictionaries 1822–1957, the year-trend is essentially flat — **Pearson r = 0.06** (slope ≈ 0.001 units/year). The variance is captured by **lexicographic family**:

| Family | mean units/entry |
|---|---|
| Benfey | 2.53 |
| Apte | 2.35 |
| Monier-Williams | 2.06 |
| Wilson | 1.80 |
| Cappeller | 1.35 |
| Petersburg | 1.15 |
| indigenous | 1.09 |

**Caveat (recorded):** the per-entry metric is confounded by **headword-splitting policy** — MW splits compounds into ~286k separate short entries, diluting its units/entry (1.22) below MW72 (2.90) despite the same family. That's structural, not temporal, and doesn't change the no-trend conclusion. A fixed simple-lemma panel removes it; corroboration from the anchor lemmas — the enumerating dicts show **no** inflation 1866→1957 (BEN dharma=11, AP90=22, AP=23).

**For Paper L:** sense granularity is a **tradition / marking-style trait, to be controlled for** (a covariate), not a function of date — a clean, defensible result, and a useful corrective to the naïve "later = finer" intuition.

## H2 / H3 — sense survival & polysemy drift on inheritance edges (2026-05-31)

[`scripts/lexico/h2h3_analysis.py`](../scripts/lexico/h2h3_analysis.py) → [`data/lexico/r2_h2h3.json`](../data/lexico/r2_h2h3.json). A 28-noun panel across three documented, *sense-countable* inheritance edges (added SHS/YAT `N.` sense markers). Survival uses gloss-text overlap (the Wilson-line glosses are English with few per-sense Sanskrit anchors).

**H2 — citation density predicts sense survival: SUPPORTED.** Ancestor senses carrying ≥1 `<ls>` citation survive into the descendant at **70%** (n=96); uncited senses at **54%** (n=715) — a 16-point gap. Well-sourced senses are stickier.

**H3 — derivatives net-ADD senses: NOT supported.** They copy or condense:

| Edge | mean senses (anc → des) | drift | gloss overlap | pattern |
|---|---|---|---|---|
| Wilson 1832 → **Śabda-Sāgara 1900** | 7.9 → 8.5 | **+0.6** | **0.82** | **near-verbatim copy** |
| Wilson 1832 → Yates 1846 | 7.9 → 1.1 | −6.75 | 0.15 | drastic condensation |
| Apte 1890 → 1957 | 15.5 → 11.0 | −4.5 | 0.61 | revision, no expansion |

The headline is **forensic**: Śabda-Sāgara's sense glosses are **82% word-identical** to Wilson's, sense by sense — a microstructure-level confirmation of the WIL⊆SHS ≈ 0.953 lemma-containment edge. (The Apte direction may be partly a marker-parsing artifact — `∙²N` vs `{@N@}` — but no edge shows systematic net-addition.) The naïve "later dictionaries are richer" intuition is refuted on the edges where it can actually be measured.

## Next

- Tighten the AE reverse index (rank by equivalent-position); verb-marker grammar; finer indigenous splitting.
- ✅ **Done** — H1 de-confounded on a fixed 30-noun panel (`h1_panel.py` → `r2_h1_panel.{json,html}`): the year-trend stays flat (Pearson *r* = 0.01) after removing the headword-splitting artifact, confirming H1 is unsupported. (A weak *r* = 0.56 among the 5 explicit-marking dicts is n=5 non-significant + convention-confounded.)
- These results (H1 tradition-effect, H2 citation-survival, H3 verbatim-copy) are the empirical core of the **standalone methods paper** ([PUBLICATIONS.md](PUBLICATIONS.md)) on Sanskrit-anchored cross-language sense alignment.
- The cross-language + cross-cluster alignment feeds the **sense-alignment view** (R1 dashboard page) and the **divergence map** (maker worklist); the granularity-by-family result is the empirical seed for **H1** (Paper L), measured family-controlled next.
