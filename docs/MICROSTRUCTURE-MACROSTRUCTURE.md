# Microstructure & Macrostructure typology of CDSL dictionaries

**Version**: 1.0 · **Date**: 2026-05-16
**Companion to**: [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md), [`L0_DESIGN.md`](L0_DESIGN.md), [`METALEXICOGRAPHY_ROADMAP.md`](METALEXICOGRAPHY_ROADMAP.md), [`PUBLICATIONS.md`](PUBLICATIONS.md)

Two complementary layers of dictionary structure:

- **Microstructure** — what's INSIDE an entry (gam ↦ what fields, subentries, citations, etymology)
- **Macrostructure** — how the dictionary AS A WHOLE is organised (alphabetisation, sectioning, volumes, indices, scope)

This doc captures empirical findings from the `gam` corpus extraction, the 30-dimensional microstructure typology, the 20-dimensional macrostructure typology, and 50+ visualisations that depict structural patterns.

---

## 1. Microstructure typology — empirical findings from `gam`

Based on direct extraction of entries headworded "gam" from MW, MW72, AP, AP90, PWG, BEN, BOP (six gam entries across six dicts). The `gam` verbal root is **the most-structured possible entry** — it's the canonical test case for microstructure complexity.

### 1.1 What's actually in MW's gam entry

```
<L>63409<pc>346,3<k1>gam<k2>gam<h>1<e>1
<hom>1.</hom> <s>gam</s> ¦ <lang>Ved.</lang> <ab>cl.</ab> 1. <ab>P.</ab> <s>ga/mati</s>
(<ls>Naigh.</ls>; <ab>Subj.</ab> <s>gamam</s>, <s>ga/mat</s>; <ab>Pot.</ab> <s>game/ma</s>;
<ab>inf.</ab> <s>ga/maDyE</s>, <ls>RV. i, 154, 6</ls>);
<ab>cl.</ab> 2. <ab>P.</ab> <s>ga/nti</s> (<ls>Naigh.</ls>; <ab>Impv.</ab> 3. <ab>sg.</ab> <s>gantu</s>...)
...
[hundreds of meaning blocks with citations]
...
<ab>Caus.</ab> <s>gamayati</s> (<ls>Pāṇ. ii, 4, 46</ls>; ...) [9 sub-meanings]
<ab>Desid.</ab> <s>ji/gamizati</s> [4 sub-meanings]
<ab>Intens.</ab> <s>ja/Nganti</s> [2 sub-meanings]
<info whitneyroots="gam,34"/>
<info verb="genuineroot" cp="1P,2P,3P,1Ā"/>
<LEND>
```

**MW has THREE separate entries for gam**:
- Entry 1: the main verb (huge, all senses)
- Entry 2: just etymology (`[cf. βαίνω; Goth. qvam; Eng. come; Lat. venio]`)
- Entry 3: the homonym "gam = earth" (cross-references kṣam)

### 1.2 Verb-entry microstructure dimensions (24 found)

Every verbal entry in CDSL dicts may have:

| # | Dimension | Example in MW gam | Present in (sample) |
|---|---|---|---|
| 1 | Homonym number | `<hom>1.</hom>` | MW, MW72, PWG |
| 2 | Lemma in SLP1 | `<s>gam</s>` | all |
| 3 | Verbal class | `<ab>cl.</ab> 1.` | all |
| 4 | Voice | `<ab>P.</ab>` (parasmaipada) | all |
| 5 | Primary present form | `gacchati` | all |
| 6 | Multi-class display | cl. 1, cl. 2, cl. 3 alternatives | MW, MW72, PWG |
| 7 | Tense/mood paradigm dump | Subj., Impv., Pot., impf., perf., aor. | MW, PWG, BOP |
| 8 | Vedic vs Classical distinction | `<lang>Ved.</lang>` | MW only (explicit tag) |
| 9 | Pāṇinian sūtra cross-references | `<ls>Pāṇ. viii, 2, 65</ls>` | MW, MW72, PWG |
| 10 | Native commentary references | Naighantuka, Padapāṭha, Kāś. | MW, PWG |
| 11 | Substitution forms | `gacch` for `gam` | MW, MW72, PWG, BOP |
| 12 | Meaning blocks (numbered) | 17+ meaning lines | all |
| 13 | Literary citations per meaning | `<ls>RV.</ls>`, `<ls>MBh.</ls>` etc. | all (density varies) |
| 14 | Verbal-phrase / idiom subentries | "jānubhyām avanīṃ-√gam = to kneel" | MW (heavy), AP (some), PWG (sparse) |
| 15 | Causative subentry (Caus.) | `<ab>Caus.</ab>` block with sub-meanings | all |
| 16 | Desiderative subentry (Desid.) | `<ab>Desid.</ab>` block | all (when attested) |
| 17 | Intensive / Frequentative (Intens. / Freq.) | `<ab>Intens.</ab>` block | MW, AP (with freq.) |
| 18 | Passive subentry (Pass.) | mentioned inline | MW, AP, MW72 |
| 19 | Denominative subentry (Den.) | not in gam (verb root) | applicable to nominals |
| 20 | Preverb-prefixed subentries (anu-, abhi-, ati-) | extensive in PWG ("`— anu`", "`— aDi`", etc.) | **PWG is dominant** |
| 21 | Past participle subentry | "gata" with own meanings | BEN (heavy), PWG (in supplements) |
| 22 | Compound subentry (Comp.) | "Tad-gat-" etc. | BEN (explicit Comp.), MW (inline) |
| 23 | Etymology (Western: cognates) | Goth., Eng., Lat., Gk. | MW, MW72, BOP (extensive) |
| 24 | Cross-references (cf., see) | "cf. kṣam" | all |

### 1.3 Nominal-entry microstructure (10 dimensions — simpler)

From the inventory of common nominal entries (rāma, deva, dharma, etc.):

| # | Dimension | Notes |
|---|---|---|
| 1 | Homonym number | for polysemous nominals |
| 2 | Lemma in SLP1 | `<s>rAma</s>` |
| 3 | Inflection sample | `(rāmaḥ)` — masculine -a stem in MW |
| 4 | Gender markers | `m.` / `f.` / `n.` / `mfn.` (= all three) |
| 5 | Numbered meanings | senses 1, 2, 3 ... |
| 6 | Literary citations per meaning | RV., MBh., etc. |
| 7 | Compound listings | nominals that take rāma as first/last element |
| 8 | Derivatives | rāmaka, rāmin, rāmaṇa etc. |
| 9 | Etymology | rare in nominal entries (more common in verb entries) |
| 10 | Cross-references | "see X", "cf. Y" |

### 1.4 Per-dict microstructure signatures

| Dict | gam entry character | Distinctive structural features |
|---|---|---|
| **MW** | Hugely deep + polished | 3 separate L-entries; modern <info whitneyroots> tags; densest Pāṇinian cross-refs |
| **MW72** | Prose-heavy, less granular | Single mega-entry with prose subsections; transitional to MW's structure |
| **AP** | Indian-edited, citation-rich | Numbered meanings (∙²1); ~7-8 sub-meanings per Caus.; heavy classical poetry citations |
| **AP90** | Pre-AP version | Same skeleton, different formatting ({@1@} vs ∙²1); more page-break artifacts |
| **PWG** | Citation-dense, preverb-rich | Hierarchical `<div n>` numbering; extensive preverb subentries (anu-, abhi-, ati-, vyapa-, api-, …); German prose |
| **BEN** | Etymology-comparative | English caps for root (GAM); Greek cognates; explicit `Ptcple.`, `Comp.` subentries; numbered meanings {@1@}-{@13@} |
| **BOP** | Latin-comparative | Latin definitions; IE comparative (Goth., Gk., Lat., Lith., Irish); Pott citation; older Indological prose style |
| **WIL** (not in sample but Nirukta-rich) | Nirukta `.E.` etymology in 89% of entries | Indian semantic etymology not Western linguistic |

---

## 2. Subentry analysis expansion — 15 categories (was 7)

The user's initial list (Caus./Pass./Desid./Inten./Den./Periphr./preverbs+verb) is 7 categories. The gam analysis reveals **8 more** sub-structure dimensions worth measuring:

### 2.1 Verbal-derivative subentries (the original 6)
1. **Caus.** (causative) — `gamayati`
2. **Pass.** (passive) — `gamyate`
3. **Desid.** (desiderative) — `jigamiṣati`
4. **Intens.** / **Frequent.** — `jaṅgamīti`
5. **Den.** (denominative) — N/A for `gam` (applies to nominals like `kāmayate` from `kāma`)
6. **Periphr.** (periphrastic conjugation) — when attested

### 2.2 Preverb-derived subentries (PWG's signature)
7. **`anu-`** + verb (anugacchati = follow)
8. **`abhi-`** + verb (abhigacchati = approach)
9. **`ati-`** + verb (atigacchati = surpass)
10. **`vyapa-`**, **`api-`**, **`vi-`**, **`upa-`**, **`pra-`**, **`prati-`**, **`adhi-`**, **`abhy-ā-`**, **`upā-`**, **`saṃ-`**, etc.

Each preverb × verb pair could be a separate "sublemma" with its own meanings + citations + Pāṇinian refs.

### 2.3 Idiom / verbal-phrase subentries (MW's signature)
11. **Object + verb idioms** — e.g. `manasā gam` ("to observe"), `jānubhyām avanīṃ gam` ("to kneel"), `doṣeṇa gam` ("to accuse")

### 2.4 Participle-as-subentry (BEN's signature)
12. **`gata`** (past passive participle) — with its own meanings + compounds + citations
13. **`gantum`** (infinitive), **`gatvā`** (absolutive), **`gamya`** / **`gatya`** (with preverbs) — derived forms as separate sub-lemmata

### 2.5 Compound / samāsa subentries (BEN's, MW's)
14. **Compound types**: bahuvrīhi, dvandva, tatpuruṣa, karmadhāraya — derived compounds containing the lemma
15. **Compounded preverbs** — `pratīpaṃ gam` ("go against") — adverbial + verb constructions

### 2.6 Subentry counting strategy

For each dict, count per entry:
- Total subentries
- Subentries by category (the 15 above)
- Depth (does Caus. have its own Pass.? does abhi-gam have its own Caus.?)
- Subentry-to-main-entry ratio
- Per-letter density (do verb roots in the first letters have more subentries because they're better-studied?)

Output: `data/microstructure_subentries.csv` with columns:
`dict, lemma, n_subentries, subentry_categories, max_depth, total_chars_subentries`

---

## 3. Macrostructure typology

While **microstructure** is what's INSIDE an entry, **macrostructure** is how the dictionary as a whole is ORGANISED.

### 3.1 Macrostructure dimensions to measure

| # | Dimension | Examples / values |
|---|---|---|
| 1 | Alphabetisation order | Sanskrit varṇamālā / IAST / German alphabetical (PWG) / English (WIL, MW) |
| 2 | Entry granularity | one lemma = one entry (MW) vs lemma + variants combined (PWG `gam (vgl. gā)`) |
| 3 | Homonym treatment | separate `<L>` entries (MW: 3× gam) vs hom-numbered same entry (PWG: 1. gam, 2. gam) |
| 4 | Compound treatment | each compound a headword (MW) vs nested under primary lemma (PWG `gata` subentries) |
| 5 | Section division | preface + body + indices + appendices structure |
| 6 | Volume division | by letter (PWG vol1=a-, vol4=n-p) vs by alphabet section vs by topic |
| 7 | Cross-referencing system | "see X" prose / `q.v.` / `<L>` reference numbers / hyperlinks |
| 8 | Index types | etymological / semantic / frequency / source-text / Pāṇinian-sūtra |
| 9 | Appendix presence | abbreviations / list of authors / citation conventions / errata |
| 10 | Numbering scheme | entry numbers / line numbers / page numbers (and granularity) |
| 11 | Headword normalisation convention | Patel-1 through Patel-7 (already measured) |
| 12 | Inclusion criteria | scope: classical only / Vedic only / Buddhist (BHS) / Mahābhārata (MCI, INM) |
| 13 | Exclusion criteria | what kinds of words explicitly omitted (vulgar, dialectal, post-classical) |
| 14 | Source-language acknowledgement | preface acknowledges which prior dicts used (foundational ground-truth) |
| 15 | Editorial-voice strategy | translator (e.g. Wilson translates Indian sources) vs original lexicographer (Apte composes) |
| 16 | Citation-format strategy | full reference (PWG) / abbreviated (MW) / minimal (newer dicts) |
| 17 | Typography / display | Devanagari + Roman / Roman-only / SLP1-tagged / IAST |
| 18 | Front-matter richness | preface length + introduction + grammar primer + abbreviations list |
| 19 | Versioning / edition history | first ed / revised / new ed / posthumous (per dict CITATION.cff) |
| 20 | Per-entry uniformity | every entry follows same template (modern) vs ad-hoc (older) |

### 3.2 Macrostructure × microstructure interaction

A dict at **macro-level "1 entry per compound"** (e.g. MW) will have **many more total entries** but **shorter individual microstructure** per entry. A dict at **macro-level "compounds nested under primary"** (PWG) will have **fewer total entries** but **deeper microstructure** per primary entry.

This explains the lemma-count differences:
- MW: 194k lemmas (many compounds as separate entries)
- PWG: 106k lemmas (compounds often nested)
- AP: 88k lemmas (mixed)

**KPI**: lemma-to-microstructure-depth ratio per dict.

---

## 4. Visualisation catalog (50+ chart types)

### 4.1 Already produced
1. **Bar**: per-dict lemma counts (sanhw1) — published
2. **Heatmap**: 41×41 Jaccard distance matrix — published
3. **Bar**: inheritance edges by containment — published
4. **Cladogram** (text-only Newick) — published; needs SVG render
5. **Heatmap**: contributor × repo commits — published
6. **Heatmap**: per-letter coverage per dict — published
7. **Stacked area**: issue typology over time — published

### 4.2 Microstructure-specific
8. **Anatomy diagram** per entry: radial chart showing which dimensions present (out of 24 verb-microstructure features)
9. **Side-by-side entry comparison**: same lemma across 5 dicts, color-coded by feature
10. **Subentry tree** per verb (root → Caus. → Pass-of-Caus → …)
11. **Preverb × verb matrix** per dict (which preverb-prefixed forms attested)
12. **Verb-class distribution** per dict (cl. 1 vs 2 vs 3 vs 4 vs 5 vs 6 vs 10)
13. **Subentry density** per dict (subentries per verb-root entry, distribution)
14. **Subentry-category proportion** per dict (stacked-bar)
15. **Meaning-count distribution** per entry per dict
16. **Citation-density per meaning** distribution
17. **Compound coverage** per nominal entry per dict

### 4.3 Etymology / Nirukta
18. **Nirukta-tradition heatmap**: which Pāṇinian terms (aff., neg., causal, krt, taddhita, upasarga, dhātu) appear per dict
19. **Bopp-cognate overlap heatmap**: MW × BOP cognate-set similarity
20. **Cognate-language coverage**: which languages (Goth., Gk., Lat., Lith., Slav., Russ.) cited per dict
21. **Etymology presence rate** per dict bar chart
22. **WIL .E. token cloud**: most-frequent Nirukta abbreviations

### 4.4 Genealogy / inheritance
23. **Bayesian DAG** of derivation: source → inheritor edges with confidence intervals
24. **Time-anchored stratigraphic plot**: dicts on vertical time axis, derivation arrows
25. **Animated cladogram**: growing tree as new dicts added 1822-2026
26. **Phylogenetic dendrogram** (rooted UPGMA / NJ / Bayesian comparison)
27. **Convention-fingerprint clustermap**

### 4.5 Citation analysis
28. **Citation truncation Sankey**: PWG `Rv. 1.22.16` → MW72 `Rv. 1.22.` → MW `RV.`
29. **Cited-source heatmap**: 35 dicts × ~100 Sanskrit texts cited
30. **Co-citation network**: text A frequently cited with text B in entries
31. **Per-letter citation density** (rare letters cite more from rare texts?)
32. **Pāṇinian sūtra reference network**: which sūtras most-cited per dict
33. **Vedic vs Classical citation balance** per dict

### 4.6 Coverage / completeness
34. **UpSet plot**: multi-set lemma intersections across top 10 dicts
35. **Per-letter publication-year matrix**: PWG vol1 1855 covered a-, vol4 1865 covered n-p…
36. **Coverage-tier histogram**: lemmas appearing in N dicts (N=1..41)
37. **Lemma exclusivity** per dict (unique contribution to canonical set)
38. **Print-page-to-digital-line ratio** per dict (density)

### 4.7 Cross-language
39. **Translation chains**: lemma → German (PWG) → English (MW) → Latin (BOP) → Russian (KCH/KOW)
40. **KOW vs WIL similarity matrix** for shared lemmas
41. **Bilingual gloss alignment** (per-lemma side-by-side)

### 4.8 Community / engineering
42. **Force-directed dict-similarity network**
43. **Per-dict richness radar** (10 KPIs on radar per dict)
44. **Specialisation matrix**: contributor × dict commits
45. **Tech-stack evolution timeline**

### 4.9 Macrostructure-specific
46. **Front-matter length distribution** (preface chars per dict)
47. **Index-types-present matrix** (which dicts have which index appendices)
48. **Per-section type detection** (preface / body / appendices breakdown per dict)
49. **Volume × letter coverage matrix** (when each letter was first published per dict)
50. **Editorial-voice classification** (translator-style vs original-author-style)

---

## 5. Research questions

This section is **open for additions** — each new question may become a focused study, a paper section, or a dashboard page.

### 5.1 Confirmed / in-progress (already answered or executing)
- [x] What fields exist in a Sanskrit-dictionary verb entry? (24 dims found in `gam` analysis)
- [x] What fields exist in a nominal entry? (10 dims)
- [x] How does each dict's microstructure differ? (per-dict signatures table)
- [x] Are WIL's `.E.` blocks etymology or Nirukta? (Nirukta; 89% of entries; ~16 top abbreviation tokens)
- [x] Does MW directly cite Bopp? (No — only 4 mentions of "Bopp" in MW72, 0 in MW; need indirect cognate-set comparison)
- [x] Does each dict's lemma-overlap reveal inheritance? (Yes — WIL→SHS, WIL→YAT, PWG→PW, MW72→MW, ARMH→MW, etc.)

### 5.2 New / added by author (captured 2026-05-16, prompting round 1)

Four structure-and-lineage questions surfaced via `AskUserQuestion` and answered by M. Gasūns. Each becomes a study/phase/section as noted.

**Q1. Dictionary-pair derivation hypotheses to test** (beyond the four already confirmed: WIL→YAT, WIL→SHS, ARMH→MW, ABCH→MW)
- **PW → MW** — the canonical claim everyone repeats but no one has empirically measured.
- **PWG → MW72** — 1855 PWG seeding the 1872 first Monier-Williams (rather than only PW → MW). Re-centers the lineage on PWG.
- **PWG → SHS** — PWG as European-Sanskrit backbone reaches Sanskrit-English dicts directly.
- **CCS → KCH** — Cappeller (1887 German) → Kochergina (1978 Russian); cross-language, cross-century edge.

*Cumulative implication*: PWG is the central node of the European-Sanskrit family, not PW alone. Phase L0 must include PWG-rooted edges as a first-class hypothesis class.

**Q2. Case-study lemma set**
- **Hapax legomena and rare technical terms** — chosen as the forensic instrument: a hapax shared between two dicts is the strongest possible copying signal. Implies a new **Phase L0.7 (hapax-overlap study)** feeding Q1's lineage tests.

**Q3. Editorial / methodological decisions to examine**
- **Treatment of grammatical info (gender, paradigm, root class)** — the most-variable microstructure feature across CDSL; ties into the 24 verb-entry + 10 nominal dimensions. Feeds a dedicated "grammatical-metadata inventory" paper (see PUBLICATIONS §6.2, Article 18).

**Q4. Lexicographer biographical / intellectual influence to study**
- **Böhtlingk & Roth (PW/PWG) — the Petersburg school** — coherent with Q1's PWG-as-backbone answers and the Russian-tradition thread in PUBLICATIONS §6.2 Q8. Framed as a Petersburg-institutional study (not isolated biographies of two German philologists who happened to live in Russia).

### 5.3 Further questions — open for input

Templates for any additional research questions:

- *"What is the [phenomenon] in [dict A] vs [dict B] and how does it correlate with [other dimension]?"*
- *"Is the [historical claim] visible in [data signal]?"*
- *"How does [structural dimension] change between [dict A 19th c.] and [dict B 20th c.]?"*

Each question becomes one of:
- A new Phase (L0.5, L0.6, L0.7, etc.) in the lexicography roadmap
- A new dashboard chart
- A paragraph in an existing article
- A whole new article if the scope warrants

---

## 6. Open questions (next round)

1. Should the visualisations be split out into a separate `VISUALIZATIONS.md` doc, or kept here?
2. Are there other dictionary entries besides `gam` you'd like sampled (e.g. a noun like `rāma`, a particle like `iti`, a Buddhist-Hybrid term)? Different test cases would reveal different microstructure patterns.
3. Should microstructure be measured for every entry, or sampled (10% / 5% / specific letter-bands)?
4. Should macrostructure be measured from preface text (Phase P) or from observable computational signals (sanhw1 already gives us alphabetisation hints, etc.)?
