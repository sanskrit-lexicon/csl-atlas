# Paper (methods) — Sanskrit-Anchored Cross-Language Sense Alignment

**Status**: Methods (§3) + Validation/Results (§4–5) drafted 2026-05-31 · feeds Paper L.
**Type**: short computational-lexicography / digital-humanities methods paper.
**Owner**: M. Gasūns + Claude. **Evidence base**: [R2_FINDINGS.md](R2_FINDINGS.md), `scripts/lexico/`, `data/lexico/`.

## Working title

*Anchoring on Sanskrit: deterministic cross-language sense alignment across 15 historical Sanskrit dictionaries.*

## Thesis / abstract

Historical Sanskrit dictionaries gloss the **same** Sanskrit headwords into different metalanguages — German (Petersburg, Schmidt), English (Wilson, Monier-Williams, Apte, Benfey), French (Stchoupak), and Sanskrit itself (Vācaspatya, Śabdakalpadruma). Comparing their **senses** has therefore required translation. We show this is unnecessary: because every tradition exposes Sanskrit material *inside* each sense — cited forms, synonyms, cognates, and citation sigla — senses can be aligned **deterministically, with no translation**, by the Sanskrit they share ("anchor on Sanskrit"). We split each dictionary's entries into senses with per-tradition heuristic grammars, fingerprint each sense by its Sanskrit tokens + `<ls>` citations, and align by fingerprint overlap. Applied to 15 CDSL dictionaries (1822–1957), the method aligns German↔English↔Sanskrit senses and yields three results on dictionary genealogy.

## Contributions

1. **A deterministic, translation-free sense-alignment method** for multilingual historical lexicography (reproducible; no LLM), with per-tradition sense-splitter grammars (Western / indigenous-quotation / reverse English→Sanskrit).
2. **H1** — sense granularity is a **lexicographic-tradition trait, not temporal** (full corpus, 11 dicts; year-trend r = 0.06). A covariate to control for, correcting the "later = finer" intuition.
3. **H2** — **citation density predicts a sense's survival** into descendant dictionaries (cited 70% vs uncited 54%).
4. **H3** — derivatives **copy or condense, they do not net-add** senses; forensic centerpiece: Śabda-Sāgara (1900) reproduces Wilson (1832) sense glosses **82% word-identical**, a microstructure-level confirmation of the lemma-overlap edge (WIL ⊆ SHS ≈ 0.953).

## Structure (provisional)

1. Introduction — the multilingual-metalanguage problem; why translation-based comparison is brittle.
2. Data — the CDSL `csl-orig` corpus; the four structural clusters.
3. Method — per-tradition sense splitting; the Sanskrit fingerprint; alignment.
4. Validation — within-edition (Apte 1890/1957) and cross-language (PWG↔Apte) alignments.
5. Results — H1 (granularity×tradition), H2 (citation→survival), H3 (copy/condense).
6. The interactive explorer (reproducibility + a practitioner artifact).
7. Limitations — coarse indigenous/verb grammars; AE reverse over-match; headword-splitting confound.
8. Conclusion — Sanskrit as the language-agnostic alignment anchor for the whole CDSL family.

---

## Draft — §3 Method

### 3.1 Corpus

We work directly on the canonical CDSL source texts (`csl-orig/v02/<dict>.txt`), in which every entry is delimited by an `<L>`…`<LEND>` block carrying a headword (`<k1>`, in SLP1 transliteration), an optional grammatical and etymological preamble, and a gloss. Sanskrit material throughout is in SLP1, whether wrapped in `{#…#}`/`<s>…</s>` markup (the Western and reverse dictionaries) or written as bare SLP1 prose (the indigenous Sanskrit-to-Sanskrit lexica). Headwords are resolved across the normalisation conventions catalogued by Patel (2016) — the doubling of a consonant after *r* (*dharma* → *Darmma*) and inflected nominative endings (*DarmaH*, *DarmaM*) — so that the same lemma is retrieved whatever a given dictionary does, and all `<L>` blocks sharing a headword (a word's homonyms) are aggregated.

### 3.2 Sense splitting by tradition

Dictionaries do not mark senses uniformly, but each is internally consistent, so a small deterministic grammar per **tradition cluster** suffices. We distinguish four:

- **Western-tagged** (Wilson, Monier-Williams, Apte, Benfey, Cappeller, Schmidt, the Petersburg dictionaries, …). Senses are introduced by an explicit marker that we match per dictionary: Apte's `∙²N`, Apte-1890/Benfey/Edgerton's `{@N@}`, Wilson and its descendants' `N.`, Böhtlingk-Roth's `<div n="N"> N)/a)`. A residual sub-family — chiefly Monier-Williams and the German Petersburg tradition — marks no senses at all, instead concatenating near-synonyms into a single run-on gloss; we label these *lumped* and, where a count is needed, fall back to counting `;`-separated meaning clauses (with citation lists stripped), noting that this is a lower-confidence proxy, not a true sense count.
- **Indigenous-quotation** (Vācaspatya, Śabdakalpadruma). The entry is a scholastic Sanskrit exposition; we segment it at `iti`-closed quotation units and anchor on the authority sigla (`jE0` = Jaimini, `BA0` = Bhāṣya, …) and the quoted forms themselves.
- **Reverse, English→Sanskrit** (Apte's *Student's English-Sanskrit Dictionary*). The headword is English; we index every entry by the SLP1 equivalents it lists in `<s>…</s>`, so that a Sanskrit lemma retrieves the English senses that gloss it.
- **Index / catalogue** (the Vedic and Mahābhārata indexes, etc.). These enumerate references, not word-senses, and are excluded.

### 3.3 The Sanskrit fingerprint and alignment

Each sense receives a **Sanskrit fingerprint**: the set of SLP1 content tokens it contains (synonyms, cited forms, cognates — the headword's own variants excluded, as they do not discriminate) together with the source sigla of its `<ls>` citations (or, for the indigenous dictionaries, its `…0` authority sigla and quoted forms). Two senses are aligned by the Jaccard overlap of their fingerprints. Because the fingerprint is composed entirely of Sanskrit-side material, alignment is **language-agnostic**: it requires no translation of the German, English, French or Sanskrit gloss prose. To suppress spurious matches on short inflectional fragments, we retain only alignments backed by a *strong* shared anchor — a citation, an indigenous siglum, or a content word of at least four characters.

The entire pipeline is deterministic and uses no model or external resource: re-running it on the same source yields byte-identical output.

## Draft — §4 Validation

The alignment behaves correctly at two scales. *Within* a single tradition, the two editions of Apte's Sanskrit-English dictionary align sense-for-sense: for *dharma*, sense 4 of the 1957 edition aligns to sense 4 of the 1890 edition at Jaccard 1.0, the two senses sharing the example *zazWAMSavftterapi Darma* and the citations *Ms.* 1.114 and *Ś.* 5.4. *Across* the language barrier, the method aligns a German sense of the Petersburg dictionary — *"Gesetz, Brauch, Vorschrift, Regel"* — to Apte's English *"Religious or moral merit, virtue"*, on the strength of the shared Sanskrit form *suhfdDarmo* and citation *H.* alone, with no recourse to translation; and for *bodhisattva* it aligns a Western (German) Petersburg sense to an indigenous (Sanskrit) Śabdakalpadruma sense through the shared narrative vocabulary *jImUtavAhanAt*, *kalpadrumaM*. Sanskrit, the object language of every dictionary, thus serves as the alignment interlingua.

## Draft — §5 Results

### 5.1 Sense granularity is a tradition trait, not a function of date (H1)

We measure granularity two independent ways. Over the full corpus of eleven general dictionaries we count sense-units per entry; against publication year the correlation is negligible (Pearson *r* = 0.06). Because that per-entry figure is confounded by headword-splitting policy — Monier-Williams distributes compounds over some 286,000 short entries, diluting its average — we repeat the measurement on a fixed panel of thirty common nouns held constant across every dictionary, aggregating each word's homonym blocks; the year-correlation falls further, to *r* = 0.01. A weak positive correlation (*r* = 0.56) survives only when the comparison is restricted to the five dictionaries that mark senses explicitly, but at *n* = 5 it is not significant and is itself an artefact of marking convention: the earliest dictionary in the set, Wilson (1832), is already among the most finely enumerated (≈ 11 senses per panel word), while the apparently sparse mid-century Petersburg figure reflects only its coarse `<div>`-level marking. What varies across the corpus is therefore not the number of senses a word has but the **convention** by which a tradition exposes them — fine enumeration (Apte, Benfey, Wilson) versus run-on lumping (Monier-Williams, the Petersburg dictionaries, the indigenous lexica) — a categorical, atemporal property of lexicographic school. The naïve expectation that later dictionaries are sense-richer is not supported.

### 5.2 Citation density predicts a sense's survival (H2)

Aligning ancestor to descendant senses along documented inheritance edges, an ancestor sense carrying at least one literary citation survives into its descendant 70% of the time (*n* = 96), against 54% for uncited senses (*n* = 715). Sourcing makes a sense more durable — well-attested meanings are the ones that get carried forward.

### 5.3 Derivatives copy or condense; they do not innovate (H3)

On the three inheritance edges where both ends mark senses, the derivative never systematically adds senses. Yates (1846) condenses Wilson (1832) sharply (mean drift −6.75 senses per panel word; gloss overlap 0.15). The revised Apte (1957) does not expand the 1890 edition. Most strikingly, the Śabda-Sāgara (1900) **reproduces Wilson's sense glosses near-verbatim**: across the panel its sense text is 82% word-identical to Wilson's, sense by sense, with essentially zero net drift. This is a microstructure-level confirmation of the lemma-overlap edge WIL ⊆ SHS ≈ 0.953 reported from headword data alone: the inheritance is visible not only in *which* words the two dictionaries share but in the very wording of their definitions. Sense-level evidence thus corroborates, and sharpens, the computational stemmatics of the CDSL family.

## Reproducibility

All deterministic, stdlib-only, reads sibling `csl-orig`:
`sense_split.py` (splitter + alignment), `h1_analysis.py` (granularity×year), `h2h3_analysis.py`
(survival + drift), `r2_explorer.py` (interactive figure). Data: `data/lexico/`.

## Open before submission

- ✅ **Done** — fixed 30-noun panel de-confounds H1 (panel year-trend *r* = 0.01; `scripts/lexico/h1_panel.py` → `r2_h1_panel.{json,html}`). Methods §3 + Validation/Results §4–5 drafted above.
- Introduction (§1) + Limitations (§7) prose; the two figures (H1 panel scatter, explorer screenshot).
- Finer indigenous (VCP/SKD) splitting + verb grammar for completeness of the cross-tradition claim.
- Co-author (per the PUBLICATIONS Russian-co-author convention) + target venue.
