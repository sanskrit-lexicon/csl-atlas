# Article 21 — Apparatus, not errors: how Monier-Williams inherited the Petersburg lexicon

*Draft forensic note. Empirical basis: Phase L3 (forensic suite F0–F4b) + L0.8, building
on the convention-vs-content result of Phase L0 (Paper H §5 / Article 20). Scripts in
`scripts/forensic/`, data in `data/forensic/`. Companion to Article 17 (hapax-as-copying
method) and Article 16 (PWG as the European-Sanskrit backbone). Venue: DSH /
*Journal of Cultural Analytics*.*

---

## Abstract

Monier-Williams' *Sanskrit-English Dictionary* (MW, 1899) was built in the shadow of
Böhtlingk & Roth's *Großes Petersburger Wörterbuch* (PWG, 1855–75) and Böhtlingk's
abridgement (PW, 1879–89). *How* it inherited has been asserted but not measured. Using
five language-neutral signals across 43 digitised dictionaries plus a scholar-curated
error list, we show that MW inherited Böhtlingk's **apparatus** — which words to enter,
which texts to cite **and in what order**, how to divide homonyms — but **not** his
mechanical errors. Where a
PWG headword is misspelled, MW has the correct form in ~98% of curated cases; MW and PWG
share **zero** documented print errors. The inheritance is of scholarship, not of
typesetting. This resolves the size-confounded "MW absorbed 89–94% of PWG" claim into a
precise, defensible statement and supplies a reusable template for separating
content-descent from error-descent in any corpus of related editions.

## 1. The question

"MW copied Böhtlingk" can mean three different things: (i) MW reproduced the *headword
inventory*; (ii) MW reused the *citation apparatus*; (iii) MW carried over Böhtlingk's
*errors*. Only (iii) — a shared mistake — is decisive proof of copying in classical
stemmatics (the Lachmann common-error principle: a correct reading can be reached
independently, but the same error is near-impossible to invent twice). The three claims
are routinely conflated. We separate them.

## 2. Method — a ladder of language-neutral signals

MW is English; PWG/PW are German. Gloss prose is therefore a weak, cross-lingual channel;
the load is carried by signals that survive translation: headword sets, citations
(`<ls>` tags), and homonym structure. Each signal is calibrated against a **null** of
demonstrably unrelated dictionaries (e.g. BHS — Buddhist Hybrid Sanskrit; the indigenous
Śabdakalpadruma/Vācaspatyam are *excluded* from the citation analysis because they cite
in an untagged indigenous style, not for lack of citations — see
`data/forensic/CITATION_TAGGING.md`).

| signal | what it measures | script |
|---|---|---|
| headword containment, size-corrected (L0.8) | shared inventory, de-confounded | `scripts/L0/s6_content_lift.py` |
| **F1** citation overlap | shared apparatus | `scripts/forensic/f1_citations.py` |
| **F2** homonym-split concordance | shared structure | `scripts/forensic/f2_structure.py` |
| **F3** gloss-length tracking | translation of prose | `scripts/forensic/f3_gloss.py` |
| **F4b** shared-error test | copied *mistakes* | `scripts/forensic/f4b_ahlborn_nulltest.py` |

## 3. What MW inherited — the apparatus

**3.1 Headword inventory.** Raw containment is size-confounded (it is *highest*, 0.94, for
the unrelated tiny BOP, because MW's 194k lemmas trivially contain any small dict's common
core). The size-corrected **rare-lemma containment** — the fraction of a source's *rare*
headwords (document-frequency ≤ k across 41 dicts) recurring in MW — inverts that ranking
and isolates descent: PWG→MW 0.70 (df≤3) / 0.82 (df≤5), PW→MW 0.71, MW72→MW 0.57, against
the unrelated BOP→MW at 0.35. **17,007 headwords occur in only MW and PW** in the entire
corpus (L0.8).

**3.2 Citation apparatus (the strongest signal).** Both traditions tag references with
`<ls>`. MW shares a per-lemma citation **source-Jaccard of 0.16–0.19** with PWG/PW, versus
**0.004–0.017** with unrelated dictionaries — a 10–40× separation. **587 rare exact
references are shared for the *same headword* and occur nowhere else in the corpus**:
e.g. `ullApya → SĀH. 545`, `dAsatA → VEṆĪS. 175`, `granTakAra → VEDĀNTAS. 1`, and 565
exact Harivaṃśa line-numbers (`HARIV. 9529` …). MW further reduces Böhtlingk's full verse
references to a bare sigil **41,552 times** — a directional PWG→MW compression. The method
self-validates: it ranks known same-apparatus pairs at the top (PW/PWKVN 0.87, SCH/PW 0.63,
AP/AP90 0.77) and the nulls at the floor.

**3.3 Homonym structure.** On the discriminative *deep* (3+) homonym splits, MW matches the
Petersburg divisions 64–77% of the time (MW/PWG 65%, MW/PW 64%, MW/MW72 77%) versus ~32–36%
for index-type nulls (INM, PUI, PE); the same-author PW/PWG ceiling is 81.5%. Homonym
division is partly linguistically forced, so this corroborates rather than proves.

**3.4 Citation order — MW worked *from* PWG's articles.** Sharing *which* texts to cite
(§3.2) is consistent with merely using the same sources; sharing their *order* is not.
Over 3,593 shared headwords for which both works cite ≥3 common sources, MW reproduces
PWG's citation **sequence** at **0.811** concordance, with **47.8% of entries in perfectly
identical order** — against a random baseline of 0.50 concordance and only ~5–17%
chance-identical for k≥3 sources (a 3–10× excess). For example *droṇa*: both cite
MBH · YĀJÑ · SUŚR · HARIV · VP in that order; *pratikartavya*: MBH · HARIV · ŚAṂK · R ·
PRAB · SUŚR (six sources, identical sequence — random odds 1/720). The effect is
Petersburg-*specific*, not a shared scholarly ordering convention: agreement falls
monotonically with distance from the tradition — PWG 0.81 > PW 0.73 > Benfey 0.68 (itself
Petersburg-influenced) > the independent Apte 0.42. MW did not merely consult Böhtlingk's
sources; it assembled its entries **following Böhtlingk's entry**. This is the strongest
single copying signal in the suite, and it is structural, not lexical.

## 4. What MW did *not* inherit — the errors

**4.1 The decisive test.** `CORRECTIONS/dictionaries/PWG/ahlborn.txt` is a scholar-curated
list (M. Ahlborn, 2011) of 123 PWG headword spelling errors, several recording MW's form
for the same word. **MW carries the PWG error in 2 of 123 cases (1.6%)** — and both
(`asUya/asUy`, `vara/var`) are root-vs-stem citation conventions, not misspellings, so the
genuine figure is ≈ **0%**. Where PWG erred, MW has the *correct* form (90 cases) or simply
lacks the word (31). Independent of typesetting accidents.

**4.2 The null-test trap.** A naïve corpus null is misleading here: headwords corrected in
*both* a Petersburg dict and MW number 256 against 102.8 expected by chance — a lift of
**2.49** (hypergeometric p ≈ 4×10⁻⁴¹). Taken alone this *looks* like shared errors. It is
not: it is the *same hard words* attracting corrections in both works, with **different**
errors in each — convergence on difficult vocabulary, compounded by editorial coupling
(the Cologne `pwgissues` bundles correct one word across several dictionaries by design).
The direct test (4.1) settles what the null cannot.

**4.3 Corroboration.** MW and PWG share **zero** documented print errors (24 PWG / 122 MW
printchange records; F4a). And MW's English gloss *length* tracks PWG's German no more than
it tracks Apte's independent English (Spearman 0.564 vs 0.576; differential −0.01; F3) — MW
**recomposed** the definitions rather than translating Böhtlingk's prose.

## 5. Discussion

The signals converge on one statement: **MW is a structural copycat of Böhtlingk's apparatus
and an independent typesetting.** It worked *from* the Petersburg articles — reproducing not
only the lemma inventory and the textual loci but their **order** within the entry (§3.4),
the surest sign that the German article lay open on the desk — yet it composed its own English
prose and, separately keyed, carried over none of the German edition's mechanical errors.
"Heir of the scholarship, author of the prose." This is the forensic complement to the
Phase-L0 finding that MW absorbed the Petersburg *content* while recoding its *conventions*
(PWG→MW convention bootstrap 0.02 vs formatting-lineage edges 0.70–0.81): a dictionary can
inherit an apparatus wholesale yet share neither its house style nor its errors.

Methodologically, "did X copy Y" should be decomposed into inventory / apparatus / error
descent and tested separately — the apparatus signal (here, very strong) and the error
signal (here, null) need not agree, and their disagreement is the actual historical fact.

## 6. Limits and the one remaining decisive test

The curated error sample is small (123) and weighted toward scan-era artefacts a
separately-keyed MW could not share in any case. The citation result proves shared
*sources/editions*, not yet a shared *mistake*: independent use of the same edition can
match. The airtight upgrade is a shared **erroneous** citation — a verse number wrong
against the actual text, present in both — verifiable against a digital corpus
(Digital Corpus of Sanskrit). That is the deferred Phase F4.

## 7. Reproducibility

All figures regenerate from `scripts/forensic/` (run `parse_cslorig.py --all` first) and
`scripts/L0/s6_content_lift.py`, over `../csl-orig`, `../CORRECTIONS`, `../csl-corrections`,
and the sanhw1 snapshot. Datasets: `data/forensic/{citation_pair_overlap,
shared_rare_citations, homonym_concordance, ahlborn_mw_comparison, shared_corrections}.csv`
and the `f*_report.json` files; `data/L0/content_lift.csv`. Per-run provenance in the
`.source.json` sidecars.
