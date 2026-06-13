# Order Is the Dictionary: A Macrostructural Model of the Versified Synonymic *Kośa*

*Draft manuscript for a metalexicography venue (target: International Journal of
Lexicography; the World Sanskrit Conference 2027 as an indological alternate). The
**macrostructural** companion to* Grammar Without Tags
([`paper_indigenous_microstructure.md`](paper_indigenous_microstructure.md), P4): where
P4 recovered the indigenous *micro*structure of the verbal-root lexica, this paper
recovers the *macro*structure of the synonymic *kośa*s — works that carry no
European entry apparatus at all, and whose entire lexicographic content is their
arrangement. Empirical basis: the four CDSL koshas (ARMH, ABCH, ACPH, ACSJ), measured
by [`scripts/lexico/m6_kosha_macrostructure.py`](../../scripts/lexico/m6_kosha_macrostructure.py)
→ [`data/lexico/kosha_macrostructure.json`](../../data/lexico/kosha_macrostructure.json);
context in the dictionary pages [`armh`](../../src/dicts/armh.md),
[`abch`](../../src/dicts/abch.md) and the structural typology
[`MICROSTRUCTURE-MACROSTRUCTURE.md`](../MICROSTRUCTURE-MACROSTRUCTURE.md). All counts are
the 2026-06 snapshot and reproducible from committed data. Author: M. Gasūns (byline to
finalise).*

---

## Abstract

The versified synonymic *kośa* is the central genre of indigenous Sanskrit
lexicography, yet it is invisible to every structural measure built for a European
dictionary: it has no part-of-speech tags, no source-citation apparatus, no definitional
prose — a microstructure detector scores it zero. We show that the zero is the point.
The *kośa*'s lexicographic work is done entirely by its **macrostructure**: an
onomasiological (concept-ordered) hierarchy of *kāṇḍa* (book) → *varga* (section) →
verse → synonym-set, in which to place a word *is* to define it. Measuring the four
*kośa*s of the Cologne Digital Sanskrit Lexicon — Halāyudha's *Abhidhānaratnamālā*
(ARMH) and Hemacandra's *Abhidhānacintāmaṇi* corpus (ABCH, ACPH, ACSJ) — we recover
that macrostructure quantitatively and report four findings. **(1)** The two koshas
encode two *different* orderings of the same conceptual universe: ARMH runs by cosmic
region (heaven → earth → nether-world → general → homonyms), ABCH by a hierarchy of
beings (supreme-Jina → gods → mortals → animals → hell → general) — a **Jain**
signature, with the Arhats placed above the Brahmanical gods and the mass of the lexicon
(811 of 1,965 records) in the *human* world. **(2)** The verse is the lexical unit and
the synonym-set its payload: ARMH packs a mean of **9.2 synonyms per verse**, densest in
the heaven-*kāṇḍa* (10.6), peaking at **56 names for Viṣṇu**, 47 for the Sun, 45 for
Śiva — theonyms carry the largest sets. **(3)** The two koshas are digitized by
**opposite** models — ARMH *explodes* one synonym per record (7,907 records), ABCH
*groups* one concept per record (1,965 records / 4,619 lexemes) — so their entry counts
are **incommensurable**, a concrete hazard for any corpus statistic that sums "entries"
across koshas. **(4)** Hemacandra's lexicon carries a full gender apparatus over the
macrostructure (masc. 7,015, neut. 3,110, fem. 2,524 lexeme tags, plus dual-gender
combinations), and the supplementary koshas (ACPH, ACSJ) **inherit the six-*kāṇḍa*
frame** of the parent. The macrostructural model is first-class lexicographic data that
no entry-level measure can see — the same convention-blindness, raised from the
microstructure to the architecture of the work.

**Keywords:** Sanskrit lexicography; *kośa*; macrostructure; onomasiological
dictionary; synonymy; Amarakośa; Hemacandra; digital lexicography; measurement bias.

---

## 1. Introduction

A European dictionary is *semasiological*: it is ordered by the word (alphabetically)
and, at each word, tells you the meanings. The classical Sanskrit *kośa* is the inverse
— *onomasiological*: it is ordered by the concept, and at each concept lists the words.
There is no alphabet, no headword-then-definition entry, no citation apparatus. The
*Amarakośa*, the genre's exemplar, is 1,500 memorisable verses grouped by subject; to
know that *vahni*, *agni* and *pāvaka* are synonyms is simply to find them strung
together in the fire-verse. The lexicographic act is the *placement*.

This makes the *kośa* a stress test for digital metalexicography. Every structural
measure the field has built — and that the companion papers in this series apply across
the Cologne Digital Sanskrit Lexicon (CDSL) — keys on a European convention: a
part-of-speech tag, an `<ls>` source siglum, a `<div>` sense block. The *kośa* has none
of these, and so reads as **empty** under all of them. The project records this as the
*zero-meaning* rule: a zero under a convention-specific detector measures the absence of
that convention, not the absence of content. P4 demonstrated the rule for the indigenous
*micro*structure (the verbal-root apparatus). This paper demonstrates it for the
*macro*structure — and the demonstration is sharper here, because the *kośa* has *no*
microstructure to recover: its entire content is its arrangement.

Our contribution is a quantitative macrostructural model of the four CDSL koshas: the
*kāṇḍa*–verse–synonym-set hierarchy made measurable (§3), the comparative ordering of
two koshas and its theological signature (§4.1), the verse-as-unit and synonym-set
statistics (§4.2), the incommensurability of the two digitization models (§4.3), and the
gender apparatus and macrostructural inheritance across the Hemacandra corpus (§4.4).
The discussion (§5) draws the corpus-statistics moral and ties the koshas to the
sense-division lineage that reached the European dictionaries.

## 2. The genre and the data

### 2.1 The versified synonymic *kośa*

The synonymic *kośa* (*nāmamālā*, "garland of names") arranges the vocabulary by subject
into *kāṇḍa*s (books) and *varga*s (thematic sections), and within each section composes
the synonyms of a concept into metrical verse for memorisation. The *Amarakośa* (not in
CDSL) is the prototype; the CDSL holds four others (Table 1), headed by the two we
analyse: Halāyudha's *Abhidhānaratnamālā* (**ARMH**, ~10th c.) and Hemacandra's
*Abhidhānacintāmaṇi* (**ABCH**, ~12th c.), together with the latter's two supplements,
the *-pariśiṣṭa* (**ACPH**) and the *-śiloñcha* (**ACSJ**).

**Table 1.** The four CDSL koshas.

| Code | Title | Author | Date | Tradition |
|---|---|---|---|---|
| ARMH | *Abhidhānaratnamālā* | Halāyudha | ~10th c. | Brahmanical |
| ABCH | *Abhidhānacintāmaṇi* | Hemacandra | ~12th c. | Jain |
| ACPH | *Abhidhānacintāmaṇi-pariśiṣṭa* | Hemacandra | ~12th c. | Jain |
| ACSJ | *Abhidhānacintāmaṇi-śiloñcha* | Jinadeva (attr.) | ~12th c. | Jain |

These koshas matter to the wider CDSL lineage: the Fort William College pandits built
Wilson's (WIL) English sense-divisions from exactly this kosha tradition, and those
divisions descend into Monier-Williams. The *kośa*'s macrostructure is, in that sense,
an ancestor of the European microstructure — which is one more reason it must be
measured on its own terms rather than scored zero.

### 2.2 Why a microstructure detector scores them zero

The koshas carry none of the European entry apparatus. ARMH's "entry" is a fragment of a
verse; ABCH's is a synonym-list. There is no `<lex>`, no `<ls>`, no definitional prose
to parse. The dictionary pages in this atlas already flag the koshas as
"Common-block framework: **Not applicable** (verse-synonym genre)." The content is real
and dense; it is simply *located in the arrangement*, which is what we now measure.

## 3. Data and method

We measure the macrostructure directly from the canonical `csl-orig` source files with a
stdlib-only extractor ([`m6_kosha_macrostructure.py`](../../scripts/lexico/m6_kosha_macrostructure.py)),
which detects each kosha's encoding model and recovers its hierarchy. The two koshas use
**opposite digitization models**, and recognising this is itself part of the method:

- **ARMH — exploded.** Each synonym is its own `<L>` record carrying a verse locator
  `<vn>` = *kāṇḍa.section.subsection.verse*; the synonym-set is reconstructed by grouping
  all records that share a `<vn>`. (Five synonyms of "heaven" — *svar, svarga,
  surasadman, tridaśāvāsa, triviṣṭapa* — are five records, all tagged `<vn>1.1.1.3` and
  all repeating the same śloka.)
- **ABCH / ACPH / ACSJ — grouped.** A `;k{…kāṇḍaḥ}` header opens each book; one `<L>`
  record holds a whole concept-group in a `<syns>` field of `<eid>`-numbered lexemes,
  each carrying a gender tag (`-puM` masc., `-strI` fem., `-klī` neut., and combinations);
  every record is stamped `<info kvvv="…kāṇḍaḥ"/>`.

From these we count, per kosha: `<L>` records; distinct verses and *kāṇḍa*s (ARMH);
*kāṇḍa* headers and their order, lexeme (`<eid>`) counts, and the gender distribution
(ABCH family); synonym-set sizes (ARMH, by grouping on `<vn>`); and per-*kāṇḍa* record
counts. The numbers below are emitted to
[`kosha_macrostructure.json`](../../data/lexico/kosha_macrostructure.json) and are exact.

## 4. Results

### 4.1 Two orderings of one universe — and a Jain signature

Both koshas are onomasiological, but they order the conceptual universe **differently**
(Table 2). ARMH runs by **cosmic region** — *svarga* (heaven) → *bhūmi* (earth) →
*pātāla* (the nether/oceanic region, opening with *vaḍavāmukha*, the submarine fire) →
*sāmānya* (general) → *anekārtha* (homonyms). Hemacandra's ABCH runs by a **hierarchy of
beings** — *devādhideva* (the supreme Jinas) → *deva* (gods) → *martya* (mortals) →
*tiryak* (animals) → *naraka* (hell-beings) → *sāmānya* (general), closed by an
*avyaya-varga* of indeclinables.

Two things are legible in the ordering. First, it is **Jain**: ABCH places the
*devādhideva-kāṇḍa* — the Arhats and Tīrthaṅkaras — *above* the Brahmanical gods, exactly
inverting the Amarakośa's *svarga*-first cosmology. The macrostructure encodes the
worldview. Second, the *order* is theological but the *mass* is anthropocentric: the
**martya- (human) *kāṇḍa* holds 811 of ABCH's 1,965 records** — more than gods (271+41)
and animals (602) — while the hell-*kāṇḍa* musters only **6**. A *kośa* is a map of what
its culture had the most words for, and that is the human world.

**Table 2.** Macrostructure of the two principal koshas (records per *kāṇḍa*).

| ARMH (cosmic region) | recs | | ABCH (hierarchy of beings) | recs |
|---|---:|---|---|---:|
| 1 *svarga* (heaven) | 1,462 | | 1 *devādhideva* (supreme Jinas) | 41 |
| 2 *bhūmi* (earth) | 3,959 | | 2 *deva* (gods) | 271 |
| 3 *pātāla* (nether) | 597 | | 3 *martya* (mortals) | 811 |
| 4 *sāmānya* (general) | 958 | | 4 *tiryak* (animals) | 602 |
| 5 *anekārtha* (homonyms) | 931 | | 5 *naraka* (hell) | 6 |
| | | | 6 *sāmānya* (general) | 203 |
| | | | *avyaya-varga* (indeclinables) | 31 |
| **total** | **7,907** | | **total** | **1,965** |

### 4.2 The verse is the unit; the synonym-set is the payload

In ARMH the lexical unit is the verse: **860 verse-locators** carry the **7,907**
synonym-records, a mean of **9.2 synonyms per verse** (median 8). Density is highest in
the heaven-*kāṇḍa* (**10.6** per verse) and lowest on earth (8.6) — the gods attract the
most names. The peak is emphatic: the single largest synonym-set is **56 names for
Viṣṇu** (*viṣṇu, kṛṣṇa, keśava, …*), followed by **47 for the Sun** (*āditya, savitṛ,
bhāskara, …*) and **45 for Śiva** (*īśāna, paśupati, śaṅkara, …*). The theonymic richness
of devotional Sanskrit is directly visible as macrostructural density.

One honest qualification: ARMH's fifth *kāṇḍa* is *anekārtha* — **homonymic**, not
synonymic. Its verses use the *…api…* ("X also [means] Y") formula, e.g.
*"rudre'pi khaṇḍaparaśur vaiśravaṇe'py ekakuṇḍalaḥ…"* ("*khaṇḍaparaśu* also denotes Rudra;
*ekakuṇḍala* also denotes Vaiśravaṇa…"). The flat `<vn>` digitization explodes these
word + added-meaning pairs exactly as it explodes a synonym-set, so the per-verse figure
for *kāṇḍa* 5 (9.3) counts lexemes, not synonyms. We therefore report the synonym density
on the synonymic *kāṇḍa*s 1–4 (mean 9.18) and flag *kāṇḍa* 5 separately — the same
convention-awareness the genre demands, applied to its own internal sections.

### 4.3 Two digitization models, incommensurable counts

The headline methodological result is that the **same genre is digitized two opposite
ways** (Table 3). ARMH privileges the *headword* — one synonym, one record, alphabetically
findable — and so reports **7,907 "entries."** ABCH privileges the *concept-group* — one
verse-set, one record, preserving the onomasiological unit — and so reports **1,965
"entries"** holding **4,619 lexemes**. Neither count is wrong; they measure different
things. But it means **a corpus statistic that sums "entries" across koshas is summing
incommensurable units** — ARMH's record is a lexeme, ABCH's is a synonym-set roughly nine
lexemes deep. Any density, coverage, or overlap figure computed over raw kosha
record-counts is therefore an artifact of digitization policy, not of the texts. The unit
must be normalised (to the lexeme, or to the verse) before koshas can be compared.

**Table 3.** Two digitization models.

| Kosha | Model | Records | Lexemes | Verses / *kāṇḍa*s |
|---|---|---:|---:|---|
| ARMH | exploded (1 synonym = 1 record) | 7,907 | 7,907 | 860 v · 5 k |
| ABCH | grouped (1 concept = 1 record) | 1,965 | 4,619 | 6 k + *avyaya* |
| ACPH | grouped | 163 | 383 | 6 k |
| ACSJ | grouped | 240 | 491 | 6 k |

### 4.4 The gender apparatus, and macrostructural inheritance

Hemacandra's koshas carry a full **gender apparatus** layered over the macrostructure:
every lexeme in ABCH is tagged for *liṅga* — masculine (*puM*, 7,015 tags), neuter
(*klī* = *klība*, 3,110) and feminine (*strī*, 2,524), with dual-gender combinations
(*puṃklī* "masc. and neut.", 385; *puṃstrī*, 122) and number (*dvi*, *ba*) where
relevant — 13,284 gendered tags in all. This is grammatical information the European
dictionaries mark inconsistently and that P4 found encoded *indigenously* in the
verbal-root lexica; here it rides on the synonym macrostructure, lexeme by lexeme.

Finally, the macrostructure is **inherited within the Hemacandra corpus**: the
supplementary *-pariśiṣṭa* (ACPH) and *-śiloñcha* (ACSJ) reuse the parent's six-*kāṇḍa*
frame intact (*devādhideva → deva → martya → tiryak → naraka → sāmānya*), adding gleaned
material into the existing books rather than re-ordering. The frame is a stable
intellectual object, transmitted across a textual tradition the way a European
dictionary's alphabetisation is — and just as measurable.

## 5. Discussion

**Order is the lexicographic act.** In a semasiological dictionary the semantic work is
done in the microstructure — the sense divisions, the glosses, the citations. In the
*kośa* it is done in the macrostructure: to place *agni* in the fire-verse of the
*svarga-kāṇḍa* is to assert its meaning, its register and its synonymy in one stroke.
A metalexicography that can only see microstructure cannot see this lexicography at all.
The *zero-meaning* rule, established for the microstructure in P4, therefore reaches its
strongest form here: the synonymic *kośa* is **100 % macrostructure**, and a zero under
any entry-level detector is a statement about the instrument, never the text.

**Incommensurable counts are a corpus hazard.** §4.3 is a caution for the whole CDSL
atlas and for digital historical lexicography generally: when the same genre is digitized
under headword-primary and concept-primary models, raw entry counts cannot be summed or
compared. This is the macrostructural analogue of the citation-register and
edit-type-axis confounds the companion papers identify — convention must be a controlled
variable, here the *digitization* convention.

**A bridge to the lineage.** Because the kosha sense-divisions descend, through the Fort
William pandits and Wilson, into the European Sanskrit-English dictionaries, the
macrostructural model is also the upstream end of the inheritance graph this project
measures elsewhere. The 56-synonym Viṣṇu verse is the ancestor of a column of
near-synonyms in Monier-Williams; modelling the *kośa* is modelling where those English
sense-lists came from.

## 6. Limitations and future work

The CDSL holds four koshas, not the *Amarakośa* itself, so the genre prototype is a
comparandum rather than data; adding a digitized Amara would anchor the model. ARMH's
`<vn>` is not *varga*-subdivided in the digitization (only the *kāṇḍa* and a running
verse number vary), so we model ARMH at *kāṇḍa* granularity and ABCH at *kāṇḍa*/*varga*
granularity — a normalisation the sources permit but do not yet expose uniformly. The
gender figures count combined tags toward each gender admitted, and the *kāṇḍa*-5
synonym density is reported as lexeme-density for the reason given in §4.2. Finally, the
model is structural; aligning the synonym-sets to the European dictionaries' sense
divisions — turning the lineage claim of §5 into a measured edge set — is the natural
next study.

## 7. Conclusion

The versified synonymic *kośa* is not a dictionary without structure; it is a dictionary
that is *only* structure. Its meaning lives in a concept-ordered *kāṇḍa*–verse–synonym
hierarchy that no European entry-measure can read, and that hierarchy is richly
informative once measured: it encodes a cosmology (Brahmanical in Halāyudha, Jain in
Hemacandra), it concentrates its mass in the human world, it peaks at fifty-six names for
a single god, it carries a complete gender apparatus, and it is transmitted intact across
a textual tradition. The two koshas' opposite digitizations make their entry-counts
incommensurable — a warning for any statistic that would sum them. The lesson is the
series' lesson, raised one level: a zero is a question about the instrument, and the
architecture of the word-hoard is data.

---

## References (draft — author to finalise)

*Primary.* Halāyudha, *Abhidhānaratnamālā* (*Halāyudhakośa*), ~10th c.; Hemacandra,
*Abhidhānacintāmaṇi* with *-pariśiṣṭa*, ed. Śivadatta and Parab (Nirṇaya-sāgara Press,
Bombay, 1896); Jinadeva (attr.), *Abhidhānacintāmaṇi-śiloñcha*; Amarasiṃha, *Amarakośa*
(*Nāmaliṅgānuśāsana*), as genre comparandum.

*Resource.* Kapp, D. and Malten, T., *Cologne Digital Sanskrit Dictionaries*, University
of Cologne (sanskrit-lexicon.uni-koeln.de); the *sanskrit-kosha* digitization project
(Patel et al.).

*Secondary (to be completed).* Vogel, C., *Indian Lexicography* (1979); standard
treatments of the *nāmamālā* / *kośa* genre and of onomasiological vs semasiological
dictionary structure; metalexicographic work on macrostructure (Wiegand; Svensén 2009).
[TODO: author to insert specific citations.]
