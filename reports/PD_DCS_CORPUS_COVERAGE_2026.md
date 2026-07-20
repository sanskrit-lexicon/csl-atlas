# What share of the Poona Dictionary's source canon does DCS cover? (2026)

_Created: 20-07-2026 · Last updated: 20-07-2026_

**Handoff:** [H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md)
· **Model:** Opus 4.8 (`claude-opus-4-8`) · **Scope:** Poona Dictionary letter **a-** only (see §6).

---

## TL;DR

The **Poona Dictionary** (PD, *An Encyclopaedic Dictionary of Sanskrit on Historical
Principles*, Deccan College) cites its sources by siglum. Its siglum inventory is a de-facto
declaration of the Sanskrit literary canon as ruled by the most source-exhaustive
lexicographic project ever attempted for the language. The **Digital Corpus of Sanskrit**
(DCS) is the largest lemmatised Sanskrit corpus. **Nobody in this org — and, as far as the
scoping sweep found, nobody in the field — has measured the two against each other.**

Restricted to PD's published **a-** volumes (≈108k entries, 398,359 citation occurrences),
the answer is a study in two numbers that point in opposite directions:

| # | Metric | Value | What it answers |
|---|---|---|---|
| 1 | **PD-citation-weighted coverage** | **25.2 %** | Of what PD actually cites, how much is in DCS? |
| 2 | **Title-level coverage** | **~2.4–4.8 %** (118 of ~2,445 works) | How many of PD's works exist in DCS at all? |
| 3 | **DCS-token-weighted coverage** | **77.9 %** (2026) · 74.1 % (2021) | Of DCS's own text mass, how much does PD also cite? |
| 4 | **Partial-coverage grade** | mostly `present`; 2 partial | Is "covered" a whole work or a fragment? |

**Reading:** DCS is representative of the archaic/classical **core** (its own bulk — the
Mahābhārata, Rāmāyaṇa, Vedas — is 78 % PD-cited) but covers only a **quarter** of PD's
actual citation practice and a **twentieth** of its distinct source canon. What DCS misses is
PD's **encyclopedic breadth**: the purāṇas, the lexicographic tradition, classical kāvya, and
the grammatical/śāstric commentary layer. That gap **is** the finding.

---

## 1. Method

Full provenance and the don't-rebuild sweep are in
[H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md).
Three scripts, all in
[scripts/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/scripts):

1. **Extract** — [scripts/pd_extract_sigla.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py)
   harvests every citation-siglum candidate from
   [pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt)
   (external, read-only; 55 MB, 107,630 `<L>` entries), stripping `{#…#}` SLP1 payloads,
   `{%…%}` italic gloss, markup tags and page brackets first. Output:
   [data/pd/pd_siglum_raw.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_raw.tsv)
   — 5,106 distinct sigla, 398,359 occurrences.
2. **Classify + join** — [scripts/pd_dcs_crosswalk.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_dcs_crosswalk.py)
   assigns every siglum a `match_type` and joins to DCS. Outputs
   [pd_siglum_families.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_families.tsv),
   [pd_dcs_text_crosswalk.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_text_crosswalk.tsv)
   and [pd_dcs_metrics.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_metrics.json).

**The design crux — anchor on DCS, not on PD.** PD's citation mass is a very long tail: the
top 300 sigla are only ~74 % of it, so hand-expanding every siglum to reach 95 % coverage is
infeasible. But DCS is a **bounded** set — 276 token-bearing texts. So the join maps each DCS
text to its PD siglum(s), making *covered* mass exact at any frequency rank; everything
primary-but-not-in-DCS falls out as the **residue**. Every one of the 398,359 occurrences
carries an adjudicated `match_type` (structural / secondary / covered / residue) — 100 % of
occurrence mass is adjudicated, clearing the handoff's ≥95 % stop condition.

**DCS side:** [per_text_token_delta.csv](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv)
(276 texts, tokens for DCS 2021 and DCS 2026),
[Files.csv](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2021/Files.csv),
[capters.csv](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2021/capters.csv)
(chapter counts) and the
[DCS abbreviation list](https://github.com/sanskrit-lexicon/DCS/blob/master/DCS-abbreviation-list.txt).

---

## 2. Mass breakdown

Of 398,359 siglum occurrences under PD's a- volumes:

| Class | Occurrences | Share | Notes |
|---|---:|---:|---|
| **primary** (a Sanskrit work) | 353,512 | 88.7 % | the denominator for metric 1 |
| — covered by DCS | 88,929 | 22.3 % of all | 118 distinct DCS texts |
| — residue (not in DCS) | 264,583 | 66.4 % of all | the §4 finding |
| **structural** | 39,987 | 10.0 % | grammatical case labels (`Acc.`, `Abl.`, `Loc.`…), locus sub-parts (`A.`, `B.`), Roman-numeral book/volume numbers, editorial markers (`Ed.`, `App.`) |
| **secondary** | 4,860 | 1.2 % | modern scholarship — `EI.` (Epigraphia Indica), `MW.`/`PW.`/`APTE.` (dictionaries), `POK.`/`MAYR.`/`DEBRU.`/`AltGr.` (IE etymology), `VIŚVA.` (Vedic concordance) |

The "books **in** Sanskrit, not books **on** Sanskrit" framing from H1336 §1 survives the data:
secondary scholarship is a real but small (1.2 %) minority, now quantified and excluded from
the coverage denominator.

---

## 3. The four metrics in detail

### Metric 1 — PD-citation-weighted coverage: **25.2 %**

Of PD's 353,512 primary-work citation occurrences, **88,929 (25.2 %)** go to works DCS
contains. Three-quarters of PD's citation practice points at texts DCS does not hold.

### Metric 2 — title-level coverage: **~2.4 – 4.8 %**

DCS contains **118** of the distinct works PD cites. The denominator — how many distinct
works PD cites — is inherently fuzzy because unmerged spelling variants inflate a raw
siglum count:

- **Lower bound:** 118 / 4,986 distinct primary sigla = **2.37 %** (denominator over-counts).
- **Estimate:** merging sigla by consonant skeleton (so `PadmP.`/`PadmaP.` collapse) gives
  ~2,445 distinct works → 118 / 2,445 = **4.83 %**.

Either way the order of magnitude is robust: **even under the single letter a-, PD's source
canon runs to roughly 2,400 distinct works, of which DCS holds about one in twenty.**

### Metric 3 — DCS-token-weighted coverage: **77.9 %** (2026), **74.1 %** (2021)

Weighting by DCS's *own* token mass inverts the picture. Of DCS 2026's 5.69 M tokens,
**4.43 M (77.9 %)** sit in texts PD cites. DCS's bulk is the Mahābhārata (1.15 M tokens
alone), Rāmāyaṇa, the Vedas and the big medical saṃhitās — all squarely in PD's canon. DCS is
not a random sample of Sanskrit; it is a deep sample of exactly the archaic/classical core PD
leans on hardest.

**The 2021 → 2026 delta is itself a finding.** Token-weighted coverage rose **+3.8 pp**
(74.1 → 77.9 %) because DCS's 2021 → 2026 expansion was concentrated in PD-core texts — and
overwhelmingly in the **Vedic** layer:

| Text | DCS tok 2021 | DCS tok 2026 | Δ |
|---|---:|---:|---:|
| Śatapathabrāhmaṇa | 3,718 | 144,139 | +140,421 |
| Harivaṃśa | 0 | 85,975 | +85,975 |
| Maitrāyaṇīsaṃhitā | 5,664 | 65,375 | +59,711 |
| Jaiminīyabrāhmaṇa | 2,531 | 53,735 | +51,204 |
| Taittirīyasaṃhitā | 1,941 | 47,989 | +46,048 |
| Kāṭhakasaṃhitā | 0 | 38,894 | +38,894 |
| Baudhāyanaśrautasūtra | 938 | 39,205 | +38,267 |
| Āpastambaśrautasūtra | 861 | 33,857 | +32,996 |

Covered-text tokens grew **+30.7 %** (3.39 M → 4.43 M) over the two snapshots. DCS is
actively closing the gap with PD's canon from the Vedic end first.

### Metric 4 — partial-coverage grade

Most covered texts are graded `present`. Two carry an explicit partial flag:

- **Skandapurāṇa** — PD cites it 3,335× but DCS holds only ~16.5 k tokens (≈ the Revākhaṇḍa /
  fragments), against a full text of hundreds of thousands of ślokas. "Covered" here is a
  sliver.
- **Kāśikāvṛtti** — DCS holds ~2.9 k tokens, a fragment of the full grammar commentary.

The crosswalk carries `dcs_tok_2026` and `dcs_chapters` per text so any "covered" claim can
be sized against the work's real extent.

---

## 4. The residue — PD's canon that DCS does not hold

This is the most interesting output of the study (H1336 §4). The highest-frequency works PD
cites that are **absent from DCS**, by PD citation count:

| PD cites | Work | Class |
|---:|---|---|
| 3,506 | Padmapurāṇa | purāṇa |
| 1,934 | Mahābhāṣya (Patañjali) | grammar |
| 1,857 | Brahmāṇḍapurāṇa | purāṇa |
| 1,840 | Rājataraṅgiṇī | kāvya/history |
| 1,558 | Bhaviṣyapurāṇa | purāṇa |
| 1,333 | Prasāda (grammatical comm.) | grammar |
| 1,249 | Brahmapurāṇa | purāṇa |
| 1,155 | Vaijayantī | kośa |
| 1,014 | Mārkaṇḍeyapurāṇa | purāṇa |
| 961 | Vāyupurāṇa | purāṇa |
| 916 | Śiśupālavadha (Māgha) | kāvya |
| 915 | Gaṇeśapurāṇa | purāṇa |
| 912 | Viṣṇudharmottarapurāṇa | purāṇa |
| 884 | Kādambarī (Bāṇa) | kāvya |
| 798 | Vārttika (Kātyāyana) | grammar |
| 762 | Nānārthasaṃgraha | kośa |
| 757 | Sāhityadarpaṇa | poetics |
| 640 | Medinīkośa | kośa |
| 626 | Anekārthasaṃgraha | kośa |
| 616 | **Raghuvaṃśa** (Kālidāsa) | kāvya |

Four clusters account for nearly all the high-frequency residue, and they name what DCS is
structurally missing relative to a historical dictionary's canon:

1. **Purāṇas.** DCS holds ~12 purāṇas; PD cites at least a dozen more it lacks — Padma,
   Brahmāṇḍa, Bhaviṣya, Brahma, Mārkaṇḍeya, Vāyu, Gaṇeśa, Viṣṇudharmottara, Devībhāgavata,
   Vāmana, Brahmavaivarta… The single largest residue item (Padmapurāṇa, 3,506) outweighs all
   but three *covered* texts.
2. **The lexicographic tradition (kośa).** Vaijayantī, Medinī, Nānārtha, Anekārtha,
   Viśvaprakāśa, Abhidhānaratnamālā — a dictionary naturally cites other dictionaries; DCS,
   being a corpus, holds almost none.
3. **Classical kāvya & nāṭaka.** DCS has *no Raghuvaṃśa, no Kādambarī, no Śiśupālavadha, no
   Naiṣadhīyacarita, no Mṛcchakaṭika, no Mudrārākṣasa.* The mahākāvya/nāṭaka backbone of
   classical literature is largely outside DCS.
4. **The grammatical/śāstric commentary layer.** Mahābhāṣya, the Vārttikas, and a dense
   commentary apparatus (bhāṣyas, ṭīkās) PD leans on for its historical-principles method.

---

## 5. Why the two headline numbers diverge

Metric 1 (25 %) and metric 3 (78 %) are not in tension — they answer different questions:

- **"Of what PD cites, how much is in DCS?"** → 25 %. PD's citation practice is spread across
  a ~2,400-work encyclopedic canon; DCS holds the frequent core but not the tail.
- **"Of what DCS holds, how much does PD cite?"** → 78 %. DCS is a deep, non-random sample of
  the archaic/classical core, and that core is precisely PD's most-cited material.

The one-line synthesis: **DCS is representative of the *core* of the Sanskrit canon but not of
its *breadth*.** For a corpus-linguistics task grounded in the high-frequency classical core,
DCS is well-aligned with the lexicographic gold standard. For a task needing the purāṇic,
lexicographic or classical-kāvya breadth a historical dictionary documents, DCS covers a
quarter of the ground and must be supplemented.

---

## 6. Limitations

- **Letter a- only.** PD is published a– to ~`apaca-` (6 of 37+ planned volumes, ~105 k
  lemmas). Every number here is **PD's canon as exercised under the letter a-**, not its full
  declared canon. This is the single biggest caveat; the printed PD front-matter "List of
  Works and Abbreviations" would remove it (see follow-up below). Whether the a- sample is
  representative of PD's whole is itself untested.
- **No sourced siglum→title expansion.** H1336 §4 expected
  [citation-apparatus.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/citation-apparatus.json)
  to supply a resolved MW abbreviation→title table; on inspection it is a coverage manifest,
  **not** an expansion dictionary. Siglum→title expansion here is therefore Opus-adjudicated
  by hand for the covered set (anchored on DCS's bounded inventory), not sourced from a
  printed list. Covered-set identifications are high-confidence; the exact residue
  denominator is an estimate (§3, metric 2).
- **One material ambiguous merge.** `Kāśi.` (1,380) is read as Kāśikāvṛtti (its 2-volume
  pagination `Kāśi.(Su.) i. 172. 16` matches the grammar commentary, not Kāśīkhaṇḍa). If it
  were instead a Skandapurāṇa khaṇḍa it would move to residue, dropping metric 1 from 25.2 %
  to ~24.8 % — immaterial to the finding.
- **`Loc.` (646) is genuinely ambiguous** between *Locana* (a text, cited with page numbers)
  and the *locative* case label; it is classed structural (conservative — it affects neither
  covered mass nor the finding).
- **Coverage ≠ alignment of citation loci.** This measures whether DCS *holds* a work PD
  cites, not whether DCS's edition matches PD's cited edition line-for-line.

---

## 7. Follow-up (parked, not blocking)

- **Locate the printed PD front-matter "List of Works and Abbreviations"** (Deccan College /
  Sanskrit Library / Cologne mirrors) to convert the inferred expansion into a sourced one and
  adjudicate the residue properly. Worth a separate handoff now that the residue size is known.
- **Both H1336 §8 open questions ratified (MG, 20-07-2026):** `EI.` (Epigraphia Indica,
  inscriptions) counts as **secondary** scholarship — as classified here; and the >200-work
  residue is reported **in full** (§4) rather than treated as a stop-and-report moment —
  as done here. No change to the numbers; the classification stands as ruled.
- **Extend to the rest of PD** when further volumes are digitised, to test whether the a-
  sample is representative.

---

_Data: [data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) · derived from PD
([drdhaval2785/SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck)) and DCS 2021/2026
([gasyoun/VisualDCS](https://github.com/gasyoun/VisualDCS))._

_Dr. Mārcis Gasūns_
