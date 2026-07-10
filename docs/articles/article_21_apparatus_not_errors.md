# Article 21 — Apparatus, not errors: how Monier-Williams inherited the Petersburg lexicon

*Draft forensic note. Empirical basis: Phase L3 (forensic suite F0–F4b) + L0.8, building
on the convention-vs-content result of Phase L0
([`paper_H_convention_vs_content_lineage.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_H_convention_vs_content_lineage.md) §5).
Scripts in `scripts/forensic/`, data in `data/forensic/`. Companion to *Redundancy and
Descent* ([`paper_redundancy_and_descent.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md)),
which owns the raw-containment stemma this note de-confounds; the hapax-as-copying and
PWG-backbone companions (internal Articles 17/16) are planned, not yet drafted. Venue: DSH /
*Journal of Cultural Analytics*.*

---

## Abstract

Monier-Williams' *Sanskrit-English Dictionary* (MW, 1899) was built in the shadow of
Böhtlingk & Roth's *Großes Petersburger Wörterbuch* (PWG, 1855–75) and Böhtlingk's
abridgement (PW, 1879–89). *How* it inherited has been asserted but not measured. Using
six language-neutral signals calibrated across 41 digitised dictionaries plus a
scholar-curated error list, we show that MW inherited Böhtlingk's **apparatus** — which words to enter,
which texts to cite **and in what order**, how to divide homonyms — but **not** his
mechanical errors. Where a
PWG headword is misspelled and MW enters the word at all, MW has the correct form in 98%
of curated cases (90/92; it lacks the word in the remaining 31 of 123); MW and PWG
share **zero** documented print errors. The inheritance is of scholarship, not of
typesetting. This resolves the size-confounded "MW absorbed 89–94% of PWG" claim (the
raw-containment reading of the companion redundancy study) into a
precise, defensible statement and supplies a reusable template for separating
content-descent from error-descent in any corpus of related editions.

## 1. The question

"MW copied Böhtlingk" can mean three different things: (i) MW reproduced the *headword
inventory*; (ii) MW reused the *citation apparatus*; (iii) MW carried over Böhtlingk's
*errors*. Only (iii) — a shared mistake — is decisive proof of copying in classical
stemmatics (the Lachmann common-error principle: a correct reading can be reached
independently, but the same error is near-impossible to invent twice; Maas 1958;
West 1973; for its digital extension, Andrews & Macé 2013). The three claims
are routinely conflated. We separate them.

## 2. Method — a ladder of language-neutral signals

MW is English; PWG/PW are German. Gloss prose is therefore a weak, cross-lingual channel;
the load is carried by signals that survive translation: headword sets, citations
(`<ls>` tags), and homonym structure. Each signal is calibrated against a **null** of
demonstrably unrelated dictionaries (e.g. BHS — Buddhist Hybrid Sanskrit, Edgerton 1953;
the indigenous
Śabdakalpadruma/Vācaspatyam are *excluded* from the citation analysis because they cite
in an untagged indigenous style, not for lack of citations — see
`data/forensic/CITATION_TAGGING.md`).

| signal | what it measures | script |
|---|---|---|
| headword containment, size-corrected (L0.8) | shared inventory, de-confounded | `scripts/L0/s6_content_lift.py` |
| **F1** citation overlap | shared apparatus | `scripts/forensic/f1_citations.py` |
| **F2** homonym-split concordance | shared structure | `scripts/forensic/f2_structure.py` |
| **F3** gloss-length tracking | translation of prose | `scripts/forensic/f3_gloss.py` |
| **F5** citation-order agreement | worked *from* the article | `scripts/forensic/f5_entry_comparison.py` |
| **F6** gloss DE→EN (offline MT) | prose translated? | `scripts/forensic/f6_gloss_translation.py` |
| **F4b** shared-error test | copied *mistakes* | `scripts/forensic/f4b_ahlborn_nulltest.py` |

## 3. What MW inherited — the apparatus

**3.1 Headword inventory.** Raw containment is size-confounded (it is *highest*, 0.94, for
the unrelated tiny BOP, because MW's 194k lemmas trivially contain any small dict's common
core). The size-corrected **rare-lemma containment** — the fraction of a source's *rare*
headwords (document-frequency ≤ k across 41 dicts) recurring in MW — inverts that ranking
and isolates descent: PWG→MW 0.70 (df≤3) / 0.82 (df≤5), PW→MW 0.71, MW72→MW 0.57, against
the unrelated BOP→MW at 0.35 (`data/L0/content_lift.csv`). **17,007 headwords occur in
only MW and PW** in the entire corpus (L0.8).

**3.2 Citation apparatus (the strongest signal).** Both traditions tag references with
`<ls>`. MW shares a per-lemma citation **source-Jaccard of 0.16–0.19** with PWG/PW, versus
**0.004 (BHS) – 0.017 (Apte)** for the unrelated nulls — a 9.5–49× separation. Intermediate
values (Benfey 0.10, Grassmann 0.04) sit between lineage and null, consistent with Benfey's
own Petersburg exposure (§3.4). **587 rare exact references are shared for the *same
headword***, each attested at ≤4 lemmas corpus-wide, 203 of them occurring nowhere else in
the corpus at all: e.g. `ullApya → SĀH. 545`, `dAsatA → VEṆĪS. 175`, `granTakAra →
VEDĀNTAS. 1` (all three corpus-unique), and 565
exact Harivaṃśa line-numbers (`HARIV. 9529` …). MW further reduces Böhtlingk's full verse
references to a bare sigil **41,552 times** — a directional PWG→MW compression. The method
self-validates: it ranks known same-apparatus pairs at the top (PW/PWKVN 0.87, SCH/PW 0.62,
AP/AP90 0.76) and the nulls at the floor.

**3.3 Homonym structure.** On the discriminative *deep* (3+) homonym splits, MW matches the
Petersburg divisions 64–77% of the time (MW/PWG 65%, MW/PW 64%, MW/MW72 77%) versus ~32–36%
for index-type nulls (INM, PUI, PE — the PE null rests on only 3 deep splits); the
same-author PW/PWG ceiling is 81.5%. Homonym
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
Petersburg-influenced) > the independent Apte 0.42 (the Apte tail rests on 8 order-bearing
entries and Benfey on 154 — thin, but the gradient is monotone). MW did not merely consult Böhtlingk's
sources; it assembled its entries **following Böhtlingk's entry**. This is the strongest
single copying signal in the suite, and it is structural, not lexical.

## 4. What MW did *not* inherit — the errors

**4.1 The decisive test.** `CORRECTIONS/dictionaries/PWG/ahlborn.txt` is a scholar-curated
list (compiled by M. Ahlborn with P. Scharf and J. Funderburk in 2011; extracted by
Funderburk in 2014) of 123 PWG headword spelling errors, several recording MW's form
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
**recomposed** the definitions rather than translating Böhtlingk's prose. A direct test
confirms it: translating PWG's German gloss to English (offline MT) and measuring token
overlap, MW resembles translated-PWG **no more than the independent Apte does, in any
stratum** — ALL 0.104 vs 0.129, VERB 0.044 vs 0.098, PHIL 0.086 vs 0.086 (against a random-pair floor
of 0.0005–0.0007; F6, up to 1,500 per stratum — VERB n = 1,014, all extant verb roots). The ~0.1 overlap is convergence on the fixed Sanskrit
meaning, not derivation: even **philosophical** terms — where an independent compiler is most
tempted to lean on a predecessor — sit at exact parity (Δ ≈ 0), and MW's terse **verb**-root
glosses track PWG *least*. The prose is MW's own throughout, technical vocabulary included.

## 5. Discussion

The signals converge on one statement: **MW is a structural copycat of Böhtlingk's apparatus
and an independent typesetting.** It worked *from* the Petersburg articles — reproducing not
only the lemma inventory and the textual loci but their **order** within the entry (§3.4),
the surest sign that the German article lay open on the desk — yet it composed its own English
prose and, separately keyed, carried over none of the German edition's mechanical errors.
"Heir of the scholarship, author of the prose." This is the forensic complement to the
Phase-L0 finding that MW absorbed the Petersburg *content* while recoding its *conventions*
(PWG→MW convention bootstrap 0.013 vs formatting-lineage edges 0.58–0.81;
`data/L0/bootstrap_support.csv`): a dictionary can
inherit an apparatus wholesale yet share neither its house style nor its errors.

Methodologically, "did X copy Y" should be decomposed into inventory / apparatus / error
descent and tested separately — the apparatus signal (here, very strong) and the error
signal (here, null) need not agree, and their disagreement is the actual historical fact.

## 6. Limits and the one remaining decisive test

The curated error sample is small (123) and weighted toward scan-era artefacts a
separately-keyed MW could not share in any case. The citation result proves shared
*sources/editions*, not yet a shared *mistake*: independent use of the same edition can
match. The airtight upgrade is a shared **erroneous** citation — a verse number wrong
against the actual text, present in both — verifiable against external
DCS/VisualDCS corpus evidence. That test is outside `csl-atlas`.

**F4-DCS result (10-07-2026, VisualDCS, handoff H203).** The test was run against the DCS
passage corpus and returned **0 adjudicated shared errors — a corpus-availability block, not
a null error signal.** Of the 587 shared rare citations, only **1** resolved to a DCS locus:
96 % are Harivaṃśa, cited by the Petersburg dictionaries in the **Calcutta-vulgate continuous
śloka numbering** (running to 16 291), while DCS carries the **critical edition** (118
chapters, ≈ 6 073 verses). 298 references provably exceed the entire DCS Harivaṃśa and the
remainder have no vulgate↔critical concordance to map a continuous number onto a
(chapter, verse) locus; the single resolvable candidate (CAURAP. (A.) 49) is a recension
artifact, not an editor-independent wrong locus. So the shared-error upgrade stays unavailable
for this dictionary pair until a vulgate Harivaṃśa — the edition Böhtlingk cited — is digitised
and lemmatised. **A10 remains at the "very strong, not airtight" level (F1 apparatus + F5 order);
it is not upgraded.** Summary + full per-candidate classification:
[`VisualDCS …/reports/F4_DCS_SHARED_CITATION_ERRORS_VERDICT.md`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/F4_DCS_SHARED_CITATION_ERRORS_VERDICT.md)
(passage-resolution code stays in VisualDCS per the consumption contract).

**Correction (10-07-2026): a vulgate↔critical concordance would _not_ unblock this test**, and the
sentence above no longer offers it as an alternative. A concordance maps a vulgate address to a
critical one *on the assumption the address is correct* — the very proposition under test. An
erroneous citation maps to a critical verse lacking the headword; a correct citation pointing at
vulgate-only material maps to `ABSENT`. Both emit "not found", so the concordance cannot separate a
wrong number from a verse the critical editor cut, and since the critical text is ≈ ⅓ of the vulgate
the second branch dominates. The test requires the **vulgate itself**. A free vulgate e-text
(Kinjawadekar, Chitrashala 1936) covers 71.1 % of the vulgate and reaches **474 of the 565 shared
Harivaṃśa refs (83.9 %)**, against 1 of 587 via DCS — census in
[`data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md),
executable path in [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md),
negative result in [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8.

## 7. Reproducibility

All figures regenerate from `scripts/forensic/` (run `parse_cslorig.py --all` first) and
`scripts/L0/s6_content_lift.py`, over `../csl-orig`, `../CORRECTIONS`, `../csl-corrections`,
and the sanhw1 snapshot. Datasets: `data/forensic/{citation_pair_overlap,
shared_rare_citations, homonym_concordance, ahlborn_mw_comparison, shared_corrections}.csv`
and the `f*_report.json` files; `data/L0/content_lift.csv`. Per-run provenance in the
`.source.json` sidecars.

## References

Ahlborn, M., Scharf, P. & Funderburk, J. (2011/2014). PWG headword spelling-error notes.
Dataset in the Cologne CDSL corrections corpus,
https://github.com/sanskrit-lexicon/CORRECTIONS/blob/master/dictionaries/PWG/ahlborn.txt

Andrews, T. L. & Macé, C. (2013). Beyond the tree of texts: building an empirical model of
scribal variation through graph analysis of texts and stemmata. *Literary and Linguistic
Computing* 28(4), 504–521.

Apte, V. S. (1890). *The Practical Sanskrit-English Dictionary*. Poona: Shiralkar & Co.

Benfey, T. (1866). *A Sanskrit-English Dictionary*. London: Longmans, Green & Co.

Böhtlingk, O. (1879–1889). *Sanskrit-Wörterbuch in kürzerer Fassung*. 7 parts.
St. Petersburg: Kaiserliche Akademie der Wissenschaften. [PW]

Böhtlingk, O. & Roth, R. (1855–1875). *Sanskrit-Wörterbuch*. 7 vols. St. Petersburg:
Kaiserliche Akademie der Wissenschaften. [PWG]

Cologne Digital Sanskrit Dictionaries (CDSL). Universität zu Köln.
https://www.sanskrit-lexicon.uni-koeln.de/ — digitised source texts (`csl-orig`) and
correction history (`CORRECTIONS`, `csl-corrections`) used throughout.

Edgerton, F. (1953). *Buddhist Hybrid Sanskrit Grammar and Dictionary*. 2 vols.
New Haven: Yale University Press. [BHS]

Gasūns, M. (in preparation). *Redundancy and Descent in a Digitised Dictionary Family: A
Headword-Level Stemma of the Cologne Digital Sanskrit Lexicon.* (The companion redundancy
study; source of the raw-containment "89–94%" reading resolved here.)

Maas, P. (1958). *Textual Criticism*. Trans. B. Flower. Oxford: Clarendon Press.

Monier-Williams, M. (1872). *A Sanskrit-English Dictionary*. Oxford: Clarendon Press. [MW72]

Monier-Williams, M. (1899). *A Sanskrit-English Dictionary, new edition, greatly enlarged
and improved*. Oxford: Clarendon Press. [MW]

West, M. L. (1973). *Textual Criticism and Editorial Technique*. Stuttgart: Teubner.
