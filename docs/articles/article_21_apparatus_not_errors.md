# Apparatus, not errors: how Monier-Williams inherited the Petersburg lexicon

Mārcis Gasūns · ORCID [0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X) · gasyoun@ya.ru

*Submit-ready draft pending author sign-off
([SIGNOFF_A10_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A10_author_pass.md));
internal Article 21 / paper A10. Empirical basis: the L3 forensic suite (F1–F6) + L0.8,
building on the convention-vs-content result of Phase L0
([`paper_H_convention_vs_content_lineage.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_H_convention_vs_content_lineage.md) §5).
Scripts in `scripts/forensic/`, data in `data/forensic/`. Companion to *Redundancy and
Descent* ([`paper_redundancy_and_descent.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md)),
which owns the raw-containment stemma this note de-confounds; the hapax-as-copying and
PWG-backbone companions (internal Articles 17/16) are planned, not yet drafted. Venue:
*Digital Scholarship in the Humanities* (locked 10-07-2026).*

---

## Abstract

Monier-Williams' *Sanskrit-English Dictionary* (MW, 1899) was built in the shadow of
Böhtlingk & Roth's *Großes Petersburger Wörterbuch* (PWG, 1855–75) and Böhtlingk's
abridgement (PW, 1879–89). *How* it inherited has been asserted but not measured. Using
six language-neutral signals calibrated across 41 digitised dictionaries plus a
scholar-curated error list, I show that MW inherited Böhtlingk's **apparatus** — which words to enter,
which texts to cite **and in what order**, how to divide homonyms — but **not** his
mechanical errors. The inheritance shows even in the *gaps*: on 6,941 real words attested
in both indigenous kośas but which PWG may or may not carry, MW's omissions track PWG's
**≈8× more** than the independent Apte's do (gap-sensitivity 12.3× vs 1.5×), yet MW
independently supplies **55%** of the words PWG omits — it inherited the inventory backbone
without copying the blind spots. Where a
PWG headword is misspelled and MW enters the word at all, MW has the correct form in 98%
of curated cases (90/92; it lacks the word in the remaining 31 of 123); MW and PWG
share **zero** documented print errors. Nor did MW copy the order of the **meanings** —
Böhtlingk's fourth charge: it sequences its senses no more like PWG's (0.767) than like the
independent Apte's (0.751), shared lexicographic convention rather than transcription, with a
copying residue only in the entries whose definitions MW derived most closely. Resolving the 565 shared Harivaṃśa references
directly against the Calcutta vulgate both traditions cite corroborates 206 of them at the
exact cited śloka (≈75× the shuffled null) while turning up no shared mistake. The
inheritance is of scholarship, not of typesetting. This resolves the size-confounded "MW absorbed 89–94% of PWG" claim (the
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
are routinely conflated. I separate them.

These are not abstract categories — they are the very terms of Böhtlingk's own accusation.
In the preface to volume 4 of the abridged *pw* (1883) he charged Monier-Williams with a
"hinter dem Rücken … handwerksmässig betriebene Ausbeutung" of the Petersburg lexicon and
cited **35 passages** in evidence. The contemporaneous Böhtlingk↔Max-Müller correspondence,
edited by Stache-Weiske (2015), itemises the charge precisely: MW reproduces "**Versehen**
mannigfacher Art, **Druckfehler** und falsche **Citate**" (errors of every kind, misprints,
false citations), and — Müller, 11 June 1881 — "**was in Ihrem Werk ausgelaßen** … ist bei
ihm ausgelaßen … u[nd] **die Reihenfolge der Bedeutungen einfach abgeschrieben**" (shared
*omissions*, shared *errors*, copied *sense-order*). Müller's proposed proof was the very
common-error principle used here: under English law "Wiederabdruck von Druckfehlern"
(reprinting of misprints) constituted piracy, and Böhtlingk set the bar at a *single*
demonstrable copied error. Ladislav Zgusta (1988), reviewing the affair, judged it a matter
of insufficient *acknowledgement* rather than theft — "Monier-Williams ought to have been
more explicit in his preface." This note adjudicates the 140-year-old charge on the
digitised editions, clause by clause: apparatus (§3), omission (§3.5), sense-order (§3.6), error (§4, §6).

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
| **F9** shared omission | inventory inheritance, negative-space | `scripts/forensic/f9_shared_omission.py` |
| **F10** sense-order concordance | order of *meanings* copied? | `scripts/forensic/f10_sense_order.py` |
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

**3.5 Shared omission — the inventory backbone, from the negative-space side.** §3.1 shows
shared *presence*; Böhtlingk's item #1 was shared *absence* — "was in Ihrem Werk ausgelaßen
ist, ist bei ihm ausgelaßen." I test it on the negative space of the inventory, restricted to
words that are unambiguously real yet lie **wholly outside the European lineage**: the **6,941**
headwords attested in **both** indigenous kośas, Śabdakalpadruma and Vācaspatyam (SKD ∩ VCP).
Among these, whether MW enters a word is **12.3×** more likely when PWG enters it than when PWG
omits it (MW lacks 3.7% of PWG's holdings but 45.4% of PWG's omissions) — while for the
independent Apte the same coupling is only **1.5×** (F9). Whether MW enters a real word is thus
**≈8× more predicted by Böhtlingk's decision** than it is for an independent compiler — a
negative-space corroboration of §3.1's containment on a set where "MW contains everything"
cannot trivially hold and with an *independent* dictionary, not a size-correction, absorbing
the rarity confound (the mirror of the §4.2 "same hard words" trap). The confound runs the safe
way: MW's Pandit-mediated Indian sources would, if anything, let it share indigenous vocabulary
*independently* of PWG and *fill* the gaps — weakening the coupling — so 8× is a floor. **Yet MW
is no mechanical copy of the gaps:** it independently supplies **54.6%** of the real indigenous
words PWG omits, *more* than the independent Apte's 43.9%. Böhtlingk's rhetorical "what PW omits,
MW omits" therefore *overstates*: MW inherited the inventory backbone and then extended it. And,
exactly as with the shared citations (§6), an omission is not a conjunctive error — two compilers
can independently drop the same rare word — so this corroborates common descent without
delivering the airtight Lachmann proof. It strengthens the **apparatus** side, not the error side
(full census: [`data/forensic/SHARED_OMISSION_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SHARED_OMISSION_TEST.md)).

**3.6 Sense order — the fourth clause, measured directly, and it comes out near-null.** §3.4 measured the
order in which the two works cite their *sources*; Böhtlingk's item #4 was narrower and more literal —
"die Reihenfolge der **Bedeutungen** einfach abgeschrieben," the order of the **meanings** copied out.
For every headword both dictionaries carry with ≥3 senses, I extract MW's ordered sense sequence and
PWG's, align them **cross-lingually by meaning** — each sense reduced to its {English gloss + Sanskrit
referent} token bag, PWG's German rendered `de→en` by the same offline MT channel as §4.3, citations
**excluded** so the test is independent of F5 — and score sequence concordance exactly as §3.4 did for
citations. Over **2,451** shared headwords MW reproduces PWG's sense order at **0.767** concordance
(41.9% of entries in perfectly identical order). But — unlike the citations — this barely clears the
**independent Apte control at 0.751**: a differential of just **+0.016**, against the +0.39 gap that the
citation order showed (§3.4: PWG 0.811 vs Apte 0.42). Both dictionaries order senses far above the 0.50
shuffled-sense floor, so sense order is *structured* — but it is structured by a **shared lexicographic
convention** (literal → figurative → technical), not by transcription: MW sequences its meanings barely
more like Böhtlingk's than like the wholly independent Apte's. Only on the strict "perfectly identical"
metric does a faint Petersburg residue survive (41.9% vs Apte's 34.3%, +7.6 pts), and the cross-lingual
match is noisier for PWG (match-similarity 0.22 vs Apte's 0.40), which if anything **depresses** the
measured MW-vs-PWG value — so 0.767 is a floor and the near-parity with Apte is not a matching artefact.
A paired within-headword test (n = 660: MW-vs-PWG 0.716 vs Apte 0.713, sign-test *n.s.*) confirms the
near-parity is not a subset accident, and a match-quality sweep locates the residue precisely: as the
matches are cleaned up (equalising the noisier PWG arm), the Petersburg excess emerges and grows
(+0.10 at match-similarity > 0.20) **only** in the entries where MW's gloss most closely echoes PWG's —
sense order was copied chiefly where MW derived the definition most directly, and convergently
everywhere else. **On this one clause Böhtlingk largely overreached:** the sense order was not "simply copied" — MW is the author
of its sense-sequencing as it is of its prose (§4), even as it remains the heir of the citation
apparatus (§3.4) and inventory (§3.1, §3.5). Read alone, the F5 citation-order proxy would have
over-attributed this clause; the direct test corrects it (full census:
[`data/forensic/SENSE_ORDER_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SENSE_ORDER_TEST.md)).

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
only the lemma inventory and the textual loci but their **citation order** within the entry (§3.4),
the surest sign that the German article lay open on the desk — yet the finer-grained order of the
**meanings** was *not* transcribed (§3.6: MW-vs-PWG 0.767 barely above the independent Apte's 0.751,
against the +0.39 citation-order gap), it composed its own English prose, and, separately keyed,
carried over none of the German edition's mechanical errors.
"Heir of the scholarship, author of the prose." This is the forensic complement to the
Phase-L0 finding that MW absorbed the Petersburg *content* while recoding its *conventions*
(PWG→MW convention bootstrap 0.013 vs formatting-lineage edges 0.58–0.81;
`data/L0/bootstrap_support.csv`): a dictionary can
inherit an apparatus wholesale yet share neither its house style nor its errors.

Methodologically, "did X copy Y" should be decomposed into inventory / apparatus / error
descent and tested separately — the apparatus signal (here, very strong) and the error
signal (here, null) need not agree, and their disagreement is the actual historical fact.

## 6. Limits — and the decisive test, run to ground

The curated error sample is small (123) and weighted toward scan-era artefacts a
separately-keyed MW could not share in any case. And the citation result, however strong,
proves shared *sources/editions*, not yet a shared *mistake*: independent use of the same
edition can match. The airtight upgrade, in classical stemmatic terms, would be a shared
**erroneous** citation — a verse number wrong against the actual text, present in both
dictionaries. I ran that test twice, against the two corpora available.

**Against the DCS corpus the test is structurally blocked.** Of the 587 shared rare
citations, only **1** resolved to a DCS locus: 96 % are Harivaṃśa references, cited by the
Petersburg dictionaries in the **Calcutta-vulgate continuous śloka numbering** (running to
16 291), while DCS carries the **critical edition** (118 chapters, ≈ 6 073 verses). 298
references provably exceed the entire DCS Harivaṃśa, and the single resolvable candidate
(CAURAP. (A.) 49) is a recension artifact, not an editor-independent wrong locus (full
per-candidate classification:
[`VisualDCS …/reports/F4_DCS_SHARED_CITATION_ERRORS_VERDICT.md`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/F4_DCS_SHARED_CITATION_ERRORS_VERDICT.md);
the passage-resolution code stays in VisualDCS per the consumption contract). Nor would a
vulgate↔critical concordance unblock it: a concordance maps a vulgate address to a critical
one *on the assumption the address is correct* — the very proposition under test. An
erroneous citation maps to a critical verse lacking the headword; a correct citation
pointing at vulgate-only material maps to `ABSENT`. Both emit "not found", so the
concordance cannot separate a wrong number from a verse the critical editor cut, and since
the critical text is ≈ ⅓ of the vulgate the second branch dominates. The test requires the
**vulgate itself**.

**Against the vulgate itself, the shared citations verify as correct.** I therefore resolved
the Harivaṃśa references directly against the **Calcutta vulgate** the Petersburg
dictionaries actually cite, using a free vulgate e-text (Kinjawadekar, Chitrashala 1936;
**15,364 verses = 93.8 %** of the 16,374-śloka vulgate). A per-adhyāya continuous index was
fitted on 14,471 PWG anchors and **validated on 815 held-out MW anchors: 68.4 % land within
±3 of their cited śloka vs a 2.1 % shuffled-N null (≈ 33×)** — the index is trustworthy. Of
the **565** shared rare Harivaṃśa citations, **206 (37.7 %) corroborate at the exact cited
vulgate śloka** (e.g. `kīrtimant` `HARIV. 62` → verse 1-2-9 *…kīrtimantaṃ ca…*) against a
**0.5 % shuffled-N null — a ≈ 75× enrichment, and against 1 of 587 resolvable via DCS.**
This upgrades the citation evidence from *shared editions* to a **shared, verse-level,
verifiably-correct apparatus.** The *airtight* upgrade — a shared **erroneous** citation —
is **not** obtained, and the reason is positive rather than circumstantial: displaced cases
fall *below* their shuffled-N null (79 vs 200) with no clustering, so against the correct
edition the shared citations verify as correct and there is **no shared error to find** in
this pool. The shared-mistake signal is a measured null, not a data-availability block.

The verdict therefore stands at "very strong, not airtight" — F1 apparatus + F5 order +
direct verse-level corroboration — with the common-error coup unavailable precisely because
the shared apparatus is accurate. Census + full per-reference resolution:
[`data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md)
§6 and
[`data/forensic/harivamsa_shared_citation_resolution.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_shared_citation_resolution.csv);
executable path [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md);
dead-end record [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8.

## 7. Reproducibility

All figures regenerate from `scripts/forensic/` (run `parse_cslorig.py --all` first) and
`scripts/L0/s6_content_lift.py`, over `../csl-orig`, `../CORRECTIONS`, `../csl-corrections`,
and the sanhw1 snapshot. Datasets: `data/forensic/{citation_pair_overlap,
shared_rare_citations, homonym_concordance, ahlborn_mw_comparison, shared_corrections,
shared_omission_test, sense_order_test, sense_order_robustness}.csv`
and the `f*_report.json` files; `data/L0/content_lift.csv`. F9 (shared omission) additionally
reads the `now-2026` `key1` headword exports from `../SanskritLexicography/HeadwordLists/`. F10
(sense order) renders PWG's German glosses `de→en` with offline argos-translate (one-time model
install via `scripts/forensic/_setup_argos.py`; cache gitignored + rebuildable, parallel fill via
`_f10_pretranslate.py`) — the only figure not derived purely from the source text. Per-run provenance in the
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

Stache-Weiske, A. (2015). „Man muß zuweilen Insekten mit Kanonen schießen." Max Müllers Rolle
im Streit zwischen Böhtlingk und Monier-Williams. In: A. A. Esposito, H. Oberlin, B. A. Viveka
Rai & K. J. Steiner (eds.), *„In ihrer rechten Hand hielt sie ein silbernes Messer mit
Glöckchen…" — Studies in Indian Culture and Literature*, 323–336. Wiesbaden: Harrassowitz.
(Documentary reconstruction of the 1881–83 plagiarism dispute from the Böhtlingk↔Max-Müller
correspondence; source of the itemised charge tested here.)

West, M. L. (1973). *Textual Criticism and Editorial Technique*. Stuttgart: Teubner.

Zgusta, L. (1988). Copying in lexicography: Monier-Williams, Sanskrit Dictionary and other cases
(Dvaikośyam). *Lexicographica* 4, 145–164.
