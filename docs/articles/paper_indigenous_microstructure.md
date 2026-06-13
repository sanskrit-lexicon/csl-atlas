# Grammar Without Tags: The Verbal-Root Microstructure of the Indigenous Sanskrit *Kośa*

*Draft manuscript for submission to a metalexicography venue (target: International
Journal of Lexicography, with the World Sanskrit Conference 2027 as an indological
alternate). Empirical basis: the indigenous-root extraction
([`scripts/lexico/m4_indigenous.py`](../../scripts/lexico/m4_indigenous.py) →
[`data/lexico/indigenous_roots.csv`](../../data/lexico/indigenous_roots.csv),
[`indigenous_by_dict.json`](../../data/lexico/indigenous_by_dict.json)); the
anubandha key ([`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](../MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md));
the cross-dictionary agreement
([`root_agreement.json`](../../data/lexico/root_agreement.json),
[`MICROSTRUCTURE_ROOT_AGREEMENT.md`](../MICROSTRUCTURE_ROOT_AGREEMENT.md)); and the
zero-meaning methodology ([`MICROSTRUCTURE_ZERO_MEANING.md`](../MICROSTRUCTURE_ZERO_MEANING.md)).
Companion to *Two Citation Registers*
([`paper_citation_registers.md`](paper_citation_registers.md)) and *Condensation, Not
Inflation* ([`paper_sense_inheritance.md`](paper_sense_inheritance.md)). All counts
are reproducible from committed data; numbers herein are the 2026-06 snapshot.
Author: M. Gasūns (byline to finalise).*

---

## Abstract

Run any European-style microstructure detector — for part of speech, gender, or a
tagged source apparatus — over the Sanskrit-to-Sanskrit *kośa*s of the Cologne
Digital Sanskrit Lexicon (CDSL) and they score close to zero. We show that this zero
is a measurement artifact, not an absence of content: the indigenous lexica encode a
**rich and recoverable verbal-grammatical apparatus** through conventions of their
own. First, the verbal root is almost exclusively an *indigenous* object in this
corpus — the *Śabdakalpadruma* carries 2,544 root entries, the *Vācaspatya* 2,230,
the *Kṛdantarūpamālā* 1,757, Yates's conjugation tables 1,643 and the *Śabda-Sāgara*
463, against eight or fewer in every European dictionary. Second, the
*Śabdakalpadruma* records each root's verbal class (*gaṇa*), voice (*pada*) and
morphophonemic behaviour not in tags but in a string of *anubandha* indicatory
letters, whose key we recover from Durgādāsa Vidyāvāgīśa's *Dhātudīpikā* (preserved
in SKD's own front matter) and apply at scale: it resolves the *gaṇa* of 1,737 and
the *pada* of 1,498 SKD roots, up from 1,117 and 1,167 by surface markers alone.
Third — and this is the validation — five independent indigenous lexica, using four
different encoding conventions, **agree on the grammar they record**: across 1,526
roots classified by two or more of them, *gaṇa* is compatible in **85.5 %** of cases
(pairwise *Śabdakalpadruma*–*Vācaspatya* 92.8 %, *Śabdakalpadruma*–*Kṛdantarūpamālā*
95.0 %), *pada* in 75.3 %, transitivity in 81.4 %. The indigenous microstructure is
therefore first-class lexicographic data that a tag-keyed measure simply cannot see;
treating a detector's zero as "no content" systematically erases the indigenous
tradition from any corpus-wide statistic.

**Keywords:** Sanskrit lexicography; *kośa*; verbal root; *anubandha*; *dhātupāṭha*;
microstructure; indigenous lexicography; digital lexicography; measurement bias.

---

## 1. Introduction

A digital dictionary corpus invites measurement: count the part-of-speech tags, the
gender markers, the source citations, and you have a microstructural profile of each
dictionary. Applied across the forty-three dictionaries of the Cologne Digital
Sanskrit Lexicon, such measurement produces a striking and recurring result — the two
great Sanskrit-to-Sanskrit *kośa*s, the *Śabdakalpadruma* (SKD) and the *Vācaspatya*
(VCP), score at or near **zero** on almost every European-style detector. They carry
no `<lex>` part-of-speech tags, no `<ls>` source-citation elements, no structural
`<div>` sense markers.

It is tempting, and wrong, to read that zero as thinness. This paper makes the
opposite case with three measurements. The verbal root — the organising object of the
indigenous Sanskrit grammatical tradition — is almost *only* recorded in these
dictionaries (§4.1). What looks like an absence of grammatical tagging is in fact a
different *technology* of grammatical encoding, one we can decode (§4.2–4.3). And the
decode is not a private reading: five indigenous lexica, encoding root grammar four
different ways, agree on it (§4.4). The methodological moral — never read a
convention-specific detector's zero as absence of content — is stated in §5.

## 2. The indigenous lexica and the zero-meaning problem

The European Indological dictionaries tag grammar explicitly: Monier-Williams writes
`<lex>m.</lex>` for a masculine noun, `<ls>Pāṇ. 3,1,86</ls>` for a source. The
indigenous *kośa*s descend instead from the *dhātupāṭha* and *kośa* traditions, in
which a root's grammar is conveyed by **position and convention** — the company a
root keeps, the indicatory letters attached to it, the prose formula that closes a
sense. A detector written for the European apparatus finds none of its expected
markers and returns zero.

The project has recorded this hazard qualitatively as the *zero-meaning* rule: a zero
under a European detector measures the **absence of a European convention**, not the
absence of content. The *Śabdakalpadruma*'s own front matter states the principle for
its root apparatus in so many words — *"the anubandha of each root is determined;
roots that have no anubandha get a dot or a zero"* — so that a `0` in the slot means
"no indicatory letter," never "no verb." This paper turns the rule from a caution into
a measured demonstration.

## 3. Data and method

We extract, from the canonical CDSL source files (`csl-orig/v02`), every entry that
records a verbal root, across the five indigenous root-bearing lexica — SKD, VCP, the
*Kṛdantarūpamālā* (KRM), Yates (YAT) and the *Śabda-Sāgara* (SHS) — and, for control,
the European dictionaries. For each root entry the extractor recovers, where the
dictionary encodes them, the verbal class (*gaṇa*, ten classes), the voice (*pada*:
*parasmai-*, *ātmane-*, *ubhaya-*), and transitivity (*sa-/akarmaka*), together with
the *signal* by which the dictionary conveyed each — a cited authority, a prose
annotation, an *anubandha* slot, or a conjugation paradigm.

The *Śabdakalpadruma* slot is decoded with the key in Durgādāsa Vidyāvāgīśa's
*Dhātudīpikā* — his commentary on Vopadeva's *Kavikalpadruma*, reproduced in SKD's
front matter — which assigns a *phala* (grammatical effect) to each of forty-six
*anubandha* letters: some mark *gaṇa* (`ka`/`ki` → *curādi* class 10, `ga`/`gi` →
*kryādi* class 9, …), two mark *pada* (`ṅ` → *ātmanepada*, `ñ` → *ubhayapada*, with
*parasmaipada* the unmarked default), and the rest mark morphophonemic operations
(*iṭ*/*aniṭ* behaviour, *mit* shortening, and so on). The key was first recovered
empirically from an SKD∩VCP cross-walk and then corrected by the primary source,
which reassigned the gaṇa markers the cross-walk had mistaken for *pada* signals (the
*pada* correlation was a shadow of the *gaṇa*→*pada* tendency); G. B. Palsule's
edition of the *Kavikalpadruma* independently corroborates it.

To test whether the recovered grammar is real rather than an artifact of one decoder,
we measure **cross-dictionary agreement**: grouping all entries by SLP1 root, we ask
whether two or more dictionaries that classify the same root give a compatible label.
*Compatible* tolerates legitimate homonymy (a root spelled alike but belonging to two
classes is not a self-conflict); *unanimous* is the stricter all-agree rate.
Disagreement conflates genuine cross-tradition difference with homonymy, so we report
it as an upper bound on real conflict, not a review queue.

## 4. Results

### 4.1 The verbal root is an indigenous object

The verbal-root apparatus is almost entirely confined to the indigenous lexica
(Table 1). The five indigenous root dictionaries carry hundreds to thousands of root
entries each; every European dictionary in the corpus carries **eight or fewer**.

**Table 1.** Root entries per dictionary (selected).

| Dictionary | Root entries | of total entries |
|---|---:|---:|
| SKD — *Śabdakalpadruma* | 2,544 | 42,531 |
| VCP — *Vācaspatya* | 2,230 | 50,135 |
| KRM — *Kṛdantarūpamālā* | 1,757 | 2,061 |
| YAT — Yates (conjugation) | 1,643 | 45,206 |
| SHS — *Śabda-Sāgara* | 463 | 47,326 |
| PWG — Petersburg (große) | 8 | 123,366 |
| PW — Petersburg (kürzere) | 3 | 170,556 |
| MW72 — Monier-Williams 1872 | 1 | 55,388 |

*Source: [`indigenous_by_dict.json`](../../data/lexico/indigenous_by_dict.json).*

A microstructural census that keyed "verbal grammar" to a European tag would conclude
that the CDSL barely records roots at all. The truth is the reverse: it records them
densely, in the dictionaries the tag cannot read.

### 4.2 The *anubandha* system, decoded at scale

The *Śabdakalpadruma* encodes each root's class and voice in a string of *anubandha*
letters placed in a slot immediately after the headword separator. Applying
Durgādāsa's key resolves the *gaṇa* of **1,737** SKD roots and the *pada* of
**1,498**, up from 1,117 and 1,167 recoverable from surface markers alone — a gain of
55 % and 28 %. Of SKD's 2,544 root entries, 1,925 carry a slot to decode. The
resulting *gaṇa* distribution is linguistically correct: *bhvādi* (class 1, the
largest class) dominates (634 roots), followed by *curādi* (531) and *tudādi* (170),
once the unmarked *parasmaipada/bhvādi* defaults are restored from the visarga prose
rather than read as zero.

### 4.3 Five conventions, one grammar

The indigenous lexica do not share an encoding; they share a *subject*. SKD marks
roots by *anubandha* letters plus cited authority; VCP and SHS by prose annotation;
KRM by a *dhātupāṭha*-style annotation; YAT by a full conjugation paradigm (Table 2).
Yet the *gaṇa* distributions they produce agree in shape — *bhvādi* is the modal class
in every one (SKD 634, VCP 1,152, KRM 944, YAT 1,009, SHS 288), exactly as the
grammatical tradition predicts.

**Table 2.** Encoding convention and resolved-feature counts, indigenous root lexica.

| Dictionary | Primary signal | *gaṇa* resolved | *pada* resolved | transitivity |
|---|---|---:|---:|---:|
| SKD | *anubandha* slot + citation | 1,737 | 1,498 | 1,156 |
| VCP | prose annotation | 1,954 | 1,897 | 2,183 |
| KRM | *dhātupāṭha* annotation | 1,755 | 1,378 | 1,735 |
| YAT | conjugation paradigm | 1,643 | 1,643 | — |
| SHS | prose annotation | 456 | 407 | 454 |

### 4.4 The lexica agree on the grammar they record

Agreement is the test that the decoded grammar is real. Across the 1,526 roots that
two or more indigenous lexica classify for *gaṇa*, a single class is compatible in
**85.5 %** of cases (unanimous in 69.9 %); only 221 roots (14.5 %) conflict, and that
figure still includes homonyms. Pairwise, the closest readers agree even more tightly
— *Śabdakalpadruma*–*Vācaspatya* 92.8 % (948 of 1,022 shared roots),
*Śabdakalpadruma*–*Kṛdantarūpamālā* 95.0 %, *Vācaspatya*–*Kṛdantarūpamālā* 92.7 %.
*Pada* is compatible in **75.3 %** (the lower figure reflects the genuine
*parasmai*-default ambiguity and YAT's bare-stem citation, which undercounts), and
transitivity in **81.4 %**. Five dictionaries, four conventions, one grammatical
tradition, measured.

### 4.5 The sense unit is the *iti*-group, not the gloss

The same convention-specificity governs the *kośa*'s sense structure. Where a European
dictionary separates a sense from its source, the *kośa* fuses them: a synonym run or
definition is closed by the quotative particle *iti* and the name of its authority
(*ity Amaraḥ*, *iti Medinī*), so that the unit of microstructure is the *iti*-closed
group, in which enumeration and attestation are a single construction. A source parser
that segments SKD records on their closing authorities recovers this structure
directly; the consequence for sense counting — that the European sense/apparatus
distinction cannot be imposed on the *kośa* without loss — is developed in the
companion sense-inheritance study.

## 5. Discussion

**The zero-meaning rule, demonstrated.** A convention-specific detector's zero is an
instrument reading, not a property of the dictionary. The indigenous lexica score zero
for European grammar tags and carry, behind that zero, the corpus's densest verbal-root
apparatus — decodable (§4.2), cross-validated (§4.4), and organised on a different
microstructural unit (§4.5). Any cross-dictionary statistic that sums a European-keyed
feature will therefore *systematically erase* the indigenous tradition, reporting it as
empty where it is in fact richest. Register and convention must be controlled variables
in corpus-wide lexicographic measurement, exactly as they must be for the citation
apparatus (companion paper).

**For the history of grammar.** That five independently compiled indigenous lexica
agree on *gaṇa* at 85.5 % is, beyond a data-quality check, a measurement of the
*coherence of the dhātupāṭha tradition* as transmitted into nineteenth-century
lexicography: the *Kavikalpadruma*/*Dhātudīpikā* line (SKD, KRM) and the prose-grammar
line (VCP, SHS) converge on the same classification of the same roots.

**For digital standards.** Encoding this microstructure in an interoperable form
requires treating the *anubandha* slot and the *iti*-unit as first-class structures,
not as untagged prose to be flattened — a requirement a baseline lexicographic schema
(e.g. TEI Lex-0) meets only with a *kośa*-specific customisation.

## 6. Limitations and future work

Disagreement (§4.4) conflates cross-tradition difference with homonymy — same SLP1
spelling, different roots — and so over-states genuine conflict; resolving it needs a
homonym-aware root key. Yates cites bare stems where the others keep the
*uccāraṇārtha* final *-a*, so YAT's cross-dictionary agreement is conservative
(undercounted); a normalising pass is held back because it collides homographs (it
lowers SKD–YAT *gaṇa* agreement from 86.0 % to 81.2 %). SKD and SHS have lower feature
coverage than VCP/KRM and so contribute fewer opinions. The *anubandha* key rests on a
single primary source (Durgādāsa), corroborated by Palsule's edition; a second
manuscript witness would harden the few contested letters. Finally, the decode is at
the level of the root's lexical grammar; aligning it to a corpus of attested verb
forms (a dictionary-to-corpus join) is the natural next step.

## 7. Conclusion

The Sanskrit *kośa* does not lack microstructure; it carries a microstructure no
European-keyed detector can see. The verbal root is an almost exclusively indigenous
object in the CDSL, its grammar encoded by *anubandha* letters and prose convention
rather than tags, decodable at scale from the tradition's own *Dhātudīpikā* key, and
agreed upon at better than five-in-six by five independently compiled lexica. The
practical lesson is a single discipline for corpus lexicography: a zero is a question
about the instrument before it is a fact about the dictionary.

---

## References (draft — author to finalise)

*Primary.* Rādhākānta Deva, *Śabdakalpadruma* (Calcutta, 1822–1858), with the
*Dhātudīpikā* of Durgādāsa Vidyāvāgīśa in the front matter; Vopadeva, *Kavikalpadruma*,
ed. G. B. Palsule (Poona, 1954); Tarkavācaspati, *Vācaspatya* (Calcutta, 1873–1884);
*Kṛdantarūpamālā*; Yates, W., conjugation tables (1846); *Śabda-Sāgara* (1900).

*Resource.* Kapp, D. and Malten, T., *Cologne Digital Sanskrit Dictionaries*,
University of Cologne (sanskrit-lexicon.uni-koeln.de).

*Secondary (to be completed).* Standard treatments of the *dhātupāṭha* and *anubandha*
systems; the *kośa* genre in Sanskrit lexicography (Vogel, *Indian Lexicography*); and
metalexicographic work on microstructure and on measurement bias in dictionary
corpora. [TODO: author to insert specific citations.]
