# Paper (methods) — Sanskrit-Anchored Cross-Language Sense Alignment

_Created: 04-06-2026 · Last updated: 06-09-2026_

**Status**: Methods (§3) + Validation/Results (§4–5) drafted 2026-05-31; §1 + §7 +
figures added 2026-07-04 · author-voice pass 06-09-2026
([SIGNOFF_A09_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/SIGNOFF_A09_author_pass.md)) · feeds Paper L.
**Type**: short computational-lexicography / digital-humanities methods paper.
**Owner**: M. Gasūns + Claude. **Evidence base**:
[R2_FINDINGS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_FINDINGS.md),
the restored R2 generator outputs in `data/lexico/`, and the atlas pages
`/tools/r2-h1`, `/tools/r2-h2h3` and `/tools/r2-explorer`.

Artifact note, updated 2026-07-04 (supersedes the 2026-06-05 "scripts not
present" note): the R2 generator package **was restored 2026-06-09** and
re-verified 2026-07-04 against current `csl-orig` — `npm run build-r2-explorer`,
`build-r2-h1`, `build-r2-h1-panel`, `build-r2-h2h3` regenerate every output
named below deterministically (re-runs are byte-identical), and
`npm run build-r2-paper-figures` regenerates the two paper figures. The
acceptance-gate record and documented archived-vs-restored drift live in
[`R2_REBUILD_CONTRACT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md).
The archive fixtures `data/lexico/r2_archive_explorer.json` and
`data/lexico/r2_archive_h1.json` remain comparison targets only. Result numbers
in §4–5 below are the **restored, committed** values, with the archived values
kept in parentheses as regression baselines.

## Working title

*Anchoring on Sanskrit: deterministic cross-language sense alignment across 15 historical Sanskrit dictionaries.*

Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru

## Thesis / abstract

Historical Sanskrit dictionaries gloss the same Sanskrit headwords into different metalanguages — German (Petersburg, Schmidt), English (Wilson, Monier-Williams, Apte, Benfey), French (Stchoupak), and Sanskrit itself (Vācaspatya, Śabdakalpadruma). Comparing their senses has therefore required translation. We show this is unnecessary: because every tradition exposes Sanskrit material *inside* each sense — cited forms, synonyms, cognates, and citation sigla — senses can be aligned deterministically, with no translation, by the Sanskrit they share ("anchor on Sanskrit"). We split each dictionary's entries into senses with per-tradition heuristic grammars, fingerprint each sense by its Sanskrit tokens + `<ls>` citations, and align by fingerprint overlap. Applied to 15 CDSL dictionaries (1822–1957), the method aligns German↔English↔Sanskrit senses and yields three results on dictionary genealogy.

## Contributions

1. **A deterministic, translation-free sense-alignment method** for multilingual historical lexicography (reproducible; no LLM), with per-tradition sense-splitter grammars (Western / indigenous-quotation / reverse English→Sanskrit).
2. **H1** — sense granularity is a **lexicographic-tradition trait, not temporal** (full corpus, 11 dicts; year-trend r = 0.035). A covariate to control for, correcting the "later = finer" intuition.
3. **H2** — **citation density co-varies with a sense's survival** into descendant dictionaries (cited 76.8% vs uncited 70.5%), but under controls the effect is threshold-dependent and edge-concentrated — reported as suggestive, not established (§5.2).
4. **H3** — derivatives **copy or condense, they do not net-add** senses; forensic centerpiece: Śabda-Sāgara (1900) reproduces Wilson (1832) sense glosses **90.6% word-identical**, a microstructure-level confirmation of the lemma-overlap edge (WIL ⊆ SHS ≈ 0.953).

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

## Draft — §1 Introduction

The Cologne Digital Sanskrit Dictionaries (CDSL) corpus preserves, in one
machine-readable family, the whole nineteenth- and early twentieth-century
effort to gloss Sanskrit: Wilson (1832) and its English descendants, the
Petersburg dictionaries in German (1855–1889), Benfey, Monier-Williams,
Cappeller, Apte, Schmidt, Stchoupak's French, and — older than any of them —
the indigenous Sanskrit-to-Sanskrit lexica Śabdakalpadruma and Vācaspatya.
These works describe the *same* headwords, and questions about how they relate
— who copied whom, whether later lexicographers discriminated senses more
finely, which meanings survived from one generation to the next — are
questions about senses, not headwords. Headword-overlap stemmatics for
this family already exists; what it cannot see is the microstructure: whether
a shared lemma carries the same meanings, the same evidence, the same wording.

The obstacle is the metalanguage. A sense of *dharma* is stated in German in
the Petersburg dictionary, in English in Apte, in scholastic Sanskrit in the
Śabdakalpadruma. Comparing them has therefore seemed to require translation —
either a human reading all the languages at once, or, recently, a multilingual
embedding model. Both are expensive; the second is also unstable: embeddings
drift with model version, offer no audit trail, and hallucinate similarity
precisely where vocabularies are thin. For a corpus whose value is
philological, a comparison method whose evidence cannot be inspected is a poor
fit.

This paper's observation is that translation is unnecessary. Every tradition,
whatever its metalanguage, exposes *Sanskrit* material inside each sense: the
forms it cites, the synonyms it lists, the passages it quotes, the sigla of
the authorities it invokes. A sense of *dharma* glossed "Duty, prescribed
course of conduct" quotes *ṣaṣṭhāṃśavṛtterapi dharma eṣaḥ* and cites *Ms.*
1.114; the German sense facing it quotes the same Sanskrit and cites the same
passage. That shared Sanskrit residue is a fingerprint, and matching
fingerprints is a set-overlap computation — deterministic, auditable, and
blind to the gloss language. We call the approach **anchoring on Sanskrit**:
the object language of every dictionary in the family serves as the alignment
interlingua, and no dictionary ever needs to be translated to be compared.

We contribute (i) the method — per-tradition sense splitting plus
Sanskrit-fingerprint alignment (§3); (ii) its validation within and across
languages and traditions (§4); and (iii) three corpus-scale results on
dictionary genealogy that the method makes cheap to ask (§5): sense
granularity is a trait of lexicographic school, not of date (H1); citation
density co-varies with a sense's survival into descendant dictionaries,
though on evidence concentrated on a single edge (H2); and
derivative dictionaries copy or condense their ancestors' senses rather than
adding new ones (H3), to the point of 90% word-identical gloss reuse on the
Wilson → Śabda-Sāgara edge. Everything is computed by a deterministic,
stdlib-only pipeline over the canonical CDSL sources, with no LLM and no
external resource (§6); its limitations, and the parser decisions still held
open for expert review, are stated in §7.

## Draft — §2 Related work

Cross-dictionary sense alignment has a published ACL Anthology analogue:
**Monolingual Word Sense Alignment (MWSA)**, run as a GlobaLex/GWC shared task
(2020 edition: [2020.globalex-1.12](https://aclanthology.org/2020.globalex-1.12/),
[2020.globalex-1.14](https://aclanthology.org/2020.globalex-1.14/)) and framed
methodologically as a supervised classification problem over gloss-pair
features (Ahmadi & McCrae, GWC 2021, [2021.gwc-1.9](https://aclanthology.org/2021.gwc-1.9/)).
That literature aligns senses *within* a language across dictionary editions
using gloss-text features and embeddings; this paper's Sanskrit-fingerprint
method is a complementary, translation-free alternative for a family where
the dictionaries are in *different* metalanguages (German, English, Sanskrit)
and a shared gloss-embedding space is unavailable or unreliable. The two
approaches could be benchmarked against each other on an English/German pair
where both are applicable (e.g. PWG↔Apte); that benchmark is flagged as an
open validation idea for §7/§8 rather than attempted here. The MWSA shared task's
labeled-relation framing (exact/broader/narrower/related, not just a binary
match) is also a candidate refinement for this paper's own agreement
statistic, currently binary Sanskrit-fingerprint overlap. The closest
Sanskrit-specific precedent is Patel & Kulkarni's "Word Sense Alignment of
Sanskrit Lexica" (ISCLS 2024, [2024.iscls-1.1](https://aclanthology.org/2024.iscls-1.1/)),
which cross-aligns senses between Wilson and Yates' dictionaries by a different (non-Sanskrit-anchoring) method. It deserves direct comparison
in a revision pass, and it is the paper this one should most explicitly
position itself against for an ISCLS submission.

### Technique-adoption assessment (internal note, not manuscript prose)

**Question.** §2 flags the MWSA shared task's labeled-relation framing
(exact/broader/narrower/related, Ahmadi & McCrae GWC 2021,
[2021.gwc-1.9](https://aclanthology.org/2021.gwc-1.9/)) as "a candidate
refinement" for this paper's own agreement statistic, currently binary
Sanskrit-fingerprint overlap. Is it actually worth prototyping now?

**Where a validation pair already exists.** §4 names the two live examples:
the *within-tradition* Apte 1957↔1890 *dharma* pair (Jaccard 1.0, reproduced)
and the *cross-tradition* PWG↔Śabdakalpadruma *bodhisattva* pair (reproduced).
The genuinely **cross-language** case — the archived German↔English
*"Gesetz, Brauch, Vorschrift, Regel"* (PWG) ↔ *"Religious or moral merit,
virtue"* (Apte) pair on shared form *suhṛddharmo* / citation *H.* — is the one
that would actually test MWSA's framing against this paper's fingerprint
overlap, since MWSA itself is a cross-*edition*, same-language task and the
labeled-relation idea only earns its keep where alignment quality is
contestable enough to need finer-grained labels than match/no-match. **That
pair is currently unreproduced** by the restored splitter (§7, packet 1:
PWG/PWK `<div n>` scope) — the restored pipeline only aligns PWG to Apte at
preface level on a single shared form for *dharma*, not at the sub-sense
level the archived German↔English example used.

**Verdict: not now — defer until §7 packet 1 lands.** Labeling a handful of
alignment pairs (exact/broader/narrower/related instead of binary overlap) is
itself cheap once pairs exist to label — a few hours of manual annotation
against the existing `r2_align_*.json` fixtures, not a pipeline redesign: the
fingerprint-overlap score would stay the mechanism, with the four-way label
applied as a post-hoc human read of what kind of overlap each aligned pair
represents. But at n=2–3 reproduced pairs today (both same-lemma
identity/near-identity cases, not the genuinely divergent German↔English
example MWSA's finer labels would actually discriminate), there is nothing to
prototype the refinement *against* — a labeled scheme needs cases where
exact/broader/narrower actually differ, and the one pair that would supply
that is exactly the one blocked on the parser fix. Once packet 1 lands and the
German↔English pair reproduces, revisit: hand-labeling the resulting set
(dharma identity, bodhisattva cross-tradition, PWG↔Apte cross-language) with
MWSA's four relations is a ~2–4 hour exercise appropriate for §7/§8 as a
robustness note, not a redesign of §3.3's alignment statistic.

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

The alignment behaves correctly at two scales (Figure 2). *Within* a single tradition, the two editions of Apte's Sanskrit-English dictionary align sense-for-sense: for *dharma*, sense 4 of the 1957 edition aligns to sense 4 of the 1890 edition at Jaccard 1.0, the two senses sharing the example *ṣaṣṭhāṃśavṛtterapi dharma* and the citations *Ms.* 1.114 and *Ś.* 5.4 (reproduced in the restored data: `r2_align_dharma.json`, `ap#4 ~ ap90#4`). *Across* the language barrier and the tradition boundary at once, for *bodhisattva* the method aligns a Western (German) Petersburg sense to an indigenous (Sanskrit) Śabdakalpadruma sense through the shared narrative vocabulary *jīmūtavāhanāt*, *kalpadrumam* (reproduced: `r2_align_bodhisattva.json`, `pwg#preface ~ skd#2`). The archived run additionally aligned a German Petersburg sense — *"Gesetz, Brauch, Vorschrift, Regel"* — to Apte's English *"Religious or moral merit, virtue"* on the shared form *suhṛddharmo* and citation *H.*; that German↔English pair is preserved in the archive fixture but not yet reproduced by the restored splitter, because the restored PWG parser does not yet split `<div>`-level sub-senses the same way — exactly the open `div-source-scope` parser decision of §7 (the restored data still aligns PWG to Apte for *dharma*, but only at preface level on a single shared form). Sanskrit, the object language of every dictionary, thus serves as the alignment interlingua.

## Draft — §5 Results

### 5.1 Sense granularity is a tradition trait, not a function of date (H1)

We measure granularity two independent ways (Figure 1). Over the full corpus of eleven general dictionaries we count sense-units per entry; against publication year the correlation is negligible (Pearson *r* = 0.035; archived run 0.06). Because that per-entry figure is confounded by headword-splitting policy — Monier-Williams distributes compounds over some 286,000 short entries, diluting its per-entry average to 1.15 while its fixed-panel mean is 14.9 once a lemma's `<L>` blocks are aggregated — we repeat the measurement on a fixed panel of thirty common nouns held constant across every dictionary, aggregating each word's homonym blocks; the year-correlation stays effectively zero (*r* = 0.093; archived 0.01). The archived run had reported a weak positive correlation (*r* = 0.56) when the comparison was restricted to the five dictionaries that mark senses explicitly; in the restored data even that vanishes (*r* = −0.035), and at *n* = 5 neither value was ever significant — the apparent trend was an artefact of marking convention: the earliest dictionary in the set, Wilson (1832), is already among the most finely enumerated (8 senses per panel word), while the apparently sparse mid-century Petersburg figure reflects only its coarse `<div>`-level marking. What varies across the corpus is therefore not the number of senses a word has but the convention by which a tradition exposes them — fine enumeration (Apte, Benfey, Wilson) versus run-on lumping (Monier-Williams, the Petersburg dictionaries, the indigenous lexica) — a categorical, atemporal property of lexicographic school. The naïve expectation that later dictionaries are sense-richer is not supported.

### 5.2 Citation density co-varies with a sense's survival (H2, suggestive)

Aligning ancestor to descendant senses along documented inheritance edges (28-noun panel, 807 ancestor senses), an ancestor sense carrying at least one literary citation survives into its descendant 76.8% of the time (*n* = 82), against 70.5% for uncited senses (*n* = 725); the archived run had reported 70% vs 54%, a gap that narrowed once a semicolon-aware counter credited the uncited Yates senses the archived splitter had missed. The restored pipeline also subjects H2 to controls the archived run lacked, and they downgrade the claim; this section is therefore written as *co-varies*, not *predicts*. In a logistic regression with sense-position, gloss-length, cross-dictionary-attestation and edge fixed effects, and lemma-cluster-robust standard errors, the citation coefficient is nominally significant at the reference threshold (OR 3.30, 95% CI 1.34–8.09, *p* = 0.009), but two committed diagnostics undercut it: (i) the estimate is **threshold-dependent** — stable in magnitude (OR 2.2–3.3) but not in significance (*p* = 0.05 at the loosest cutoff) across survival thresholds 0.1–0.25; and (ii) it is **edge-concentrated** — every one of the 82 cited senses sits on the single Apte 1890→1957 edge (Wilson carries almost no `<ls>` citations), and the clean unclustered two-proportion test within that one edge gives 76.8% vs 66.1%, *z* = 1.80, *p* = 0.072: not significant. The defensible statement is that citation density and survival co-vary in the expected direction on the only edge that can test it, with the pooled "significance" an artifact of edge composition — report the sensitivity table and the within-edge test, not a single star. (The companion inheritance manuscript already adopts this framing; keep the two in lockstep.)

### 5.3 Derivatives copy or condense; they do not innovate (H3)

On the three inheritance edges where both ends mark senses, the derivative never systematically adds senses. Yates (1846) condenses Wilson (1832) sharply (mean drift −3.3 senses per panel word, 9 → 5.7, with gloss overlap 0.26; the archived run's −6.75 was partly an artifact of undercounting Yates's unmarked senses, corrected by the same semicolon-aware counter as in §5.2). The revised Apte (1957) does not expand the 1890 edition (drift −3.07, overlap 0.57); this is revision, not expansion. The Śabda-Sāgara (1900) reproduces Wilson's sense glosses near-verbatim: across the panel its sense text is 90.6% word-identical to Wilson's (archived 82%), sense by sense, with exactly zero net drift (9 senses in, 9 senses out). This is a microstructure-level confirmation of the lemma-overlap edge WIL ⊆ SHS ≈ 0.953 reported from headword data alone: the inheritance is visible not only in *which* words the two dictionaries share but in the very wording of their definitions. Sense-level evidence thus corroborates, and sharpens, the computational stemmatics of the CDSL family.

## Draft — §7 Limitations

Because the pipeline is deterministic, every weakness below is visible in the
committed outputs rather than averaged away, and none is silently patched.

**Splitter grammars are heuristic, and parser-rule promotion is gated by an
expert-reviewed decision queue.** The per-tradition grammars of §3.2 were
promoted only where they reproduce the archived results; where they do not,
the divergence is parked in a machine-generated decision queue
([`R2_PARSER_DIAGNOSTICS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_PARSER_DIAGNOSTICS.md),
70 classified diagnostics; the 10 checkpoint rows in
[`R2_CHECKPOINT_DECISIONS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_CHECKPOINT_DECISIONS.md)
carry human rulings, reviewed 2026-06-12) spanning five packets:
(1) PWG/PWK `<div n>` and source-record scope — the ruled-but-not-yet-applied
packet whose splitter changes are needed to re-reproduce the archived
German↔English *dharma* alignment of §4;
(2) BEN/AP90/BHS marker-run scope; (3) rank bands for the reverse
English→Sanskrit dictionary, whose common lemmas (e.g. *gam*) over-match;
(4) indigenous SKD/VCP *iti* segmentation, which is useful but coarse — an
*iti*-closed quotation unit is not necessarily one sense; and (5) source-gap
controls. Of these, only the Yates semicolon counter has been applied so far
(through its own reviewed 26-row packet); the rest of the rulings await
implementation, so the numbers reported here are conservative with respect to
rule tuning.

**Lumped traditions are counted by a proxy.** Monier-Williams and the
Petersburg dictionaries mark no senses; their granularity figures rest on
semicolon-clause counting with citation lists stripped (§3.2), a
lower-confidence proxy that suffices for H1's categorical claim but should not
be read as a true sense inventory. Verb entries additionally need parser rules
distinct from nominal ones and are under-served by the current grammars.

**The fixed panel is a reconstruction.** The original 30-noun panel list was
lost with the archived scripts; the restored panel is rebuilt from the
documented selection criteria (28 nouns attested in all five sense-marking
dictionaries for H2/H3). Headline conclusions reproduce across the
reconstruction (H1 panel *r*: 0.093 vs 0.01; H2 direction; H3 patterns), and
the residual archived-vs-restored drift is tabulated per figure in
[`R2_REBUILD_CONTRACT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md).

**H2's evidence is threshold-dependent and edge-concentrated.** Survival is
operationalised as fingerprint alignment above a Jaccard threshold; the
citation effect's odds ratio is stable across thresholds 0.1–0.25 but its
*p*-value spans 0.05–0.009, and all 82 cited senses sit on the single
Apte 1890→1957 edge, where the clean within-edge test is not significant
(*p* = 0.072; §5.2) — so H2 is reported as suggestive co-variation with its
sensitivity table, not as a single significance claim. Survival-by-alignment also inherits the fingerprint's
blind spot: a sense inherited by *translation without any shared Sanskrit*
(gloss reworded, citations dropped) is invisible to the method and counted as
non-surviving.

**Coverage claims need one trim.** The restored package covers fourteen
dictionaries in the explorer slice plus Yates and Śabda-Sāgara on the
inheritance edges; the French dictionary (Stchoupak) named in the abstract was
touched only by the archived run. Before submission either restore Stchoupak
to the corpus or trim the metalanguage list — a scholarly-scope decision left
to the authors, not silently resolved here.

## Figures

| Figure | File | Generator |
|---|---|---|
| Figure 1 — H1 fixed-panel scatter (panel sense-units vs year, family-colored) | [`docs/figures/r2_fig1_h1_panel.svg`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/figures/r2_fig1_h1_panel.svg) | `npm run build-r2-paper-figures` (from `r2_h1_panel.json`) |
| Figure 2 — anchor-alignment examples: Apte 1957↔1890 identity pair and PWG↔ŚKD cross-tradition pair, with shared IAST anchors | [`docs/figures/r2_fig2_alignment_anchor.svg`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/figures/r2_fig2_alignment_anchor.svg) | `npm run build-r2-paper-figures` (from `r2_align_{dharma,bodhisattva}.json`; pinned rows fail loudly if a data refresh breaks a §4 example) |

Both figures regenerate byte-identically from the committed JSON; the
generator replaces the archived run's explorer screenshot with a
data-traceable equivalent.

## Reproducibility

Deterministic, stdlib-only, reading sibling `csl-orig`. The archived Python
package (`sense_split.py`, `h1_analysis.py`, `h2h3_analysis.py`,
`r2_explorer.py`) was lost with its branch; its restored Node successor has
been the package of record since 2026-06-09
([`R2_REBUILD_CONTRACT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md)):

```sh
npm run build-r2-explorer      # senses_<dict>.jsonl, r2_align_<lemma>.json, r2_summary.json
npm run build-r2-h1            # r2_h1.json (granularity × year)
npm run build-r2-h1-panel      # r2_h1_panel.json (fixed-panel deconfounding)
npm run build-r2-h2h3          # r2_h2h3.json (survival + drift on inheritance edges)
npm run build-r2-pages         # regenerate /tools/r2-h1, /tools/r2-h2h3, /tools/r2-explorer
npm run build-r2-paper-figures # docs/figures/r2_fig{1,2}_*.svg
```

Re-verified 2026-07-04 against current `csl-orig`: re-runs are byte-identical
(determinism), and the refresh moved only third-decimal values (documented in
the PR that committed it). Archive fixtures can be refreshed with
`npm run recover-r2-archive`, `build-r2-source-anchors`,
`build-r2-parser-diagnostics`.

## Open before submission

- ~~R2 generator package missing~~ ✅ restored 2026-06-09, re-verified + figures 2026-07-04.
- ~~Introduction (§1) + Limitations (§7) prose; the two figures~~ ✅ drafted/generated 2026-07-04
  (`npm run build-r2-paper-figures`).
- ~~Human checkpoint review (10 rows)~~ ✅ reviewed 2026-06-12
  ([`R2_CHECKPOINT_DECISIONS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_CHECKPOINT_DECISIONS.md),
  all rows `reviewed-ok`). **Still open (agent-doable):** APPLY the ruled parser labels
  to the splitter — PWG/PWK div scope first (re-reproduces the archived German↔English
  §4 example), then BEN/AP90/BHS marker scope, AE reverse rank bands, VCP/SKD `iti` —
  before broadening the cross-tradition claim. Only the YAT semicolon counter is
  applied so far.
- ⚠️ Scope decision (§7): restore Stchoupak (French) to the corpus or trim the
  abstract's metalanguage list.
- ⚠️ §2 Data and §6 Explorer sections are still outline-only; §8 conclusion unwritten.
- Co-author (per the PUBLICATIONS Russian-co-author convention) + target venue — MG @DECIDE.

_Dr. Mārcis Gasūns_
