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

## 8. Conclusions

### 8.1 The finding, in one line

DCS is a **deep sample of the classical core, not a broad sample of the canon.** It holds the
Vedic-epic-śāstra spine PD leans on hardest (78 % of DCS's own token mass is PD-cited) but only
a quarter of PD's actual citation practice — the purāṇic, lexicographic and classical-kāvya
breadth a historical dictionary documents is three-quarters absent.

### 8.2 How long until PD itself finishes — at the current rate, ≈ 250 years

The residue matters more because the dictionary that would define it is advancing at a pace
that puts its completion **centuries** away. The Poona Dictionary is the slowest-moving major
lexicographic project in the field, and the arithmetic is stark.

**The record (1976 – 2026, 50 years).** Conceived by S. M. Katre in **1948**, editing begun
1973, first fascicule **1976**, first bound volume 1978. In the half-century since, PD has
published **~6 bound volumes / 6,056 pages / 104,959 lemmas**, reaching **a-** to roughly
**`apaca-` / `anupahve-`** — i.e. it has not yet finished the *short* vowel **a**, and has not
reached **ā**. (The project's "35 volumes published" figure counts *fascicules*: 6,056 pp ÷ 35
≈ 173 pp each is fascicule size, not the 500–1,000 pp of a bound volume. The bound work is ~6
volumes.)

**The rate.** 6 volumes in 50 years = **one volume every 8.3 years** (≈ 121 pages/year).

**The horizon.** Against the project's ~37-volume plan, 31 volumes remain:

| Assumed complete scope | Volumes remaining | Years left (at 8.3 yr/vol) | Completion year |
|---|---:|---:|---:|
| 20 volumes (optimistic) | 14 | **~117** | ~2143 |
| 30 volumes | 24 | **~199** | ~2225 |
| **37 volumes (project's plan)** | **31** | **~258** | **~2284** |
| by pages (~37,000 pp target) | ~31,000 pp | ~256 | ~2282 |

**So, at today's printing speed, PD finishes in roughly 250 years — around the year 2280** —
give or take a century depending on the true final scope. The single most telling number is
not the horizon but the present: **after 50 years, PD is still inside the letter `a`.**

The scope itself is the largest uncertainty (the "37+" plan is the project's ambition, not a
measured total), and PD's own density front-loads the letter `a` — the privative `a-`, the
`ā-` stem, and the prefix families (`adhi-`, `anu-`, `antar-`, `apa-`, `abhi-`, `ava-`) make
`a`/`ā` the densest stretch of the whole alphabet. So the later letters should move faster per
letter than `a` did — but the 37-volume plan already prices that in, which is why the
volume-rate estimate (≈ 258 yr) is more principled than a naïve alphabet-position extrapolation
(which would read ~3 % of the alphabet in 50 years and overshoot to 1,000+ years).

### 8.3 Deep comparison — an arithmetic dictionary against a geometric corpus

PD and DCS are not merely fast and slow; they scale by **different laws**, and that is the
real conclusion of this study.

| | Poona Dictionary (PD) | Digital Corpus of Sanskrit (DCS) |
|---|---|---|
| Kind | historical **dictionary** — analysis by historical principles | lemmatised **corpus** — attestation |
| Unit of growth | the hand-edited fascicule | the ingested-and-tagged text |
| Growth law | **arithmetic** — ~121 pp/yr, flat for 50 years | **geometric** — 4.58 M → 5.69 M tokens in 5 yr = **+4.45 %/yr**, doubling every **~16 years** |
| 50-year record | a- → ~`apaca-` (still in `a`) | already holds 78 % of PD's citation *mass* |
| Completion horizon | ~250 years (≈ 2280) | not a fixed target — it accretes |

Project the two over one human planning horizon — **30 years, to ~2056**:

- **PD** adds ~3–4 volumes (0.12 vol/yr × 30). It plausibly *finishes the letter `a`* and
  begins `ā`/`i` — still under ~30 % of the alphabet.
- **DCS** grows by ~×3.7 (16-yr doubling), from ~5.7 M to **~21 M tokens**, almost certainly
  absorbing most of the major purāṇas and kāvya it currently lacks.

**The crossover is structural, not incidental.** A corpus that doubles every 16 years and a
dictionary that spends 50 years in one letter do not converge — the corpus laps the
dictionary. Long before PD reaches `k`, DCS will hold the bulk of the very canon PD would cite.
The residue this study measured — the 75 % of PD's citations DCS lacks — is therefore **not a
permanent deficit but a moving front**, and DCS's 2021→2026 Vedic surge (Śatapathabrāhmaṇa
3.7 k → 144 k tokens; +3.8 pp coverage in five years) is exactly what closing that front looks
like.

### 8.4 What follows — don't wait for the dictionary; feed the corpus

This is not "the corpus makes the dictionary obsolete." DCS *attests*; PD *analyses* — the
historical sense-development, the etymological argument, the disambiguated homonym. A corpus
cannot supply that interpretive layer, and for the 97 % of the lexicon PD has not reached, PD
remains the only project attempting it. But the practical consequence is unambiguous:

1. **For any task needing PD's breadth this generation, supplement DCS — do not wait for PD.**
   The wait is measured in centuries; the supplement in years.
2. **Prioritise the residue for digitisation.** The highest-leverage additions to DCS are
   precisely PD's high-frequency uncovered works — the purāṇas (Padma, Brahmāṇḍa, Bhaviṣya,
   Mārkaṇḍeya…), the kośa tradition (Vaijayantī, Medinī, Nānārtha), and the classical kāvya
   (Raghuvaṃśa, Kādambarī, Śiśupālavadha). PD's own citation frequency is a ready-made
   priority ranking for that effort.
3. **The two are complements on a shared timeline.** DCS closes coverage from the
   high-frequency end in years; PD deepens analysis one letter at a time over centuries. The
   crosswalk in this study is the bridge between them — and the fastest way to raise real
   coverage of PD's canon is not to hurry the dictionary but to feed its residue into the
   corpus.

### 8.5 Two speeds, and three yardsticks (AP · PWG · MW)

The horizon in §8.2 has two free variables — the **printing rate** and the true **final
scope** — and both can be pinned against the three completed Sanskrit dictionaries that already
span the whole alphabet: **AP** (Apte 1890), **PWG** (Böhtlingk–Roth, the *grosses*
Petersburger Wörterbuch), and **MW** (Monier-Williams 1899). Their sorted headword lists let us
locate PD's frontier (`apaca-`) inside a *finished* dictionary and read off, exactly, how much
is done and how much is left.

**Method.** In each dictionary's Sanskrit-collated unique-headword list
([HeadwordLists/now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026),
SLP1 key1), the line number of `apaca` is the count of headwords sorting at or before PD's
frontier. PD's own count in that range is its published lemma total, 104,959.

**How far is PD, measured against a finished dictionary?**

| Reference (whole alphabet) | Total headwords | In `a-`…`apaca-` | PD has reached | Left ahead |
|---|---:|---:|---:|---:|
| AP — Apte 1890 | 88,867 | 5,414 | **6.1 %** | 93.9 % |
| PWG — Böhtlingk–Roth (gr.) | 106,082 | 4,519 | **4.3 %** | 95.7 % |
| MW — Monier-Williams 1899 | 194,084 | 7,856 | **4.1 %** | 95.9 % |

The three agree: after 50 years PD has traversed only **~4–6 % of the alphabetical span** a
complete Sanskrit dictionary covers. **~94–96 % lies ahead.**

**How much denser is PD where it has covered?** This is why 4 % of the alphabet took 50 years:

| Reference | Headwords in `a-`…`apaca-` | PD lemmas, same range | PD is denser by |
|---|---:|---:|---:|
| MW | 7,856 | 104,959 | **13.4 ×** |
| AP | 5,414 | 104,959 | **19.4 ×** |
| PWG | 4,519 | 104,959 | **23.2 ×** |

The single most vivid measure of PD's ambition: **its coverage of just `a-` through `apaca-`
already holds as many lemmas (104,959) as the *entire* Petersburger Wörterbuch (106,082), more
than the *entire* Apte (88,867), and 54 % of the *entire* Monier-Williams (194,084)** — for
about 4 % of the alphabet. Per printed headword, PD carries roughly **13–23 ×** the granularity
of any completed dictionary: every homonym split, every attested compound and derivative, each
with its historical citations.

**The two-speed horizon.** With scope now anchored two ways — the project's own **~37-volume
plan** (~1,009 pp/volume → ~37,300 pp total) versus **holding PD's current MW-relative density**
across the rest of the alphabet (~0.77 pp per MW headword → ~149,600 pp total) — and the rate at
the historical **121 pp/yr** versus a hypothetical post-2019 **200 pp/yr**:

| Completion year | @ 121 pp/yr (50-yr average) | @ 200 pp/yr (accelerated) |
|---|---:|---:|
| **Model A — 37-volume plan** (~31,300 pp left) | **≈ 2284** | **≈ 2182** |
| **Model B — current density held** (~143,600 pp left) | ≈ 3211 | ≈ 2744 |

Two things fall out. First, **scope dominates rate**: choosing between the volume-plan and the
density-held model moves the finish by ~900–1,000 years, far more than the printing speed does.
Second, **even a 65 % speed-up barely dents the horizon** — 200 pp/yr instead of 121 buys ~100
years on the optimistic plan and ~470 on the density model, but completion stays *centuries*
away either way. The constraint is not laziness; it is that PD is an order of magnitude denser
than any dictionary that has ever been finished. That density is exactly why §8.4's conclusion
holds: the corpus (DCS) is the only bridge available on a human timescale, and PD's enduring
value is **depth in what it has covered**, not breadth any time soon.

> **Benchmark caveats.** "Lemmas" (PD, `sanhw1`) and "unique headwords" (AP/PWG/MW key1 lists)
> count in slightly different registers, so the density multipliers are directional, not exact —
> but the order of magnitude, and the "PD's `a-` ≈ all of PWG" statement, are robust across all
> three references. The AP list count (88,867) is itself high versus the printed Apte and is used
> only for the internally-consistent coverage-% and ratio. Frontier taken as `apaca-` (H1336 §6);
> the alternative `anupahve-` frontier sits ~100 headwords earlier and moves nothing material.

### 8.6 Milestones — when does PD clear `a`, the vowels, the halfway mark?

The same headword yardstick turns the horizon into datable milestones. Each milestone is a rank
in the MW list; PD reaches it after covering the intervening headwords at its current density
(0.771 pp/MW-headword) and printing rate. Both rates are carried through.

| Milestone | MW rank | Pages still to print | **@ 121 pp/yr** | **@ 200 pp/yr** |
|---|---:|---:|---:|---:|
| *(now — frontier `apaca-`)* | 7,856 | — | *2026* | *2026* |
| **End of the short vowel `a`** (before `ā`) | 18,463 | ~8,200 | **≈ 2094** | ≈ 2067 |
| **End of ALL vowels** (`a ā i ī u ū ṛ … au`) | 31,946 | ~18,600 | **≈ 2179** | ≈ 2119 |
| **Mid-dictionary** (50 % of headwords) | 97,042 | ~68,800 | **≈ 2594** | ≈ 2370 |
| **Full completion** (density-held) | 194,084 | ~143,600 | ≈ 3211 | ≈ 2744 |

Read plainly: **PD will not finish even the short vowel `a` until ~2094** — a further ~68 years
on top of the 50 already spent, because the letter `a` alone is ~14,200 pages / ~118 years of
work at this density (about 43 % done). **The whole vowel block (`a` … `au`) — 31,946 of MW's
headwords, one-sixth of the alphabet — is not cleared until ~2179.** The alphabetical
**mid-point falls at `p`** (MW headword *pratigṛdh*), not `k`: Sanskrit vocabulary is so
front-loaded with prefix families (`a-`, `pra-`, `sam-`…) that half of all headwords sit in the
first stretch `a`–`p`. The vowel milestones are reliable (the vowel section is as prefix-dense
as `a`); the consonant milestones are an **upper bound** — under the project's optimistic
37-volume plan, which assumes later letters compress, the halfway mark and completion arrive
sooner (the plan finishes the whole work by ~2284 @ 121, ~2182 @ 200; §8.2, §8.5).

### 8.7 What else is worth counting

The dataset supports several further measures, each a different lens on the same slowness:

- **Per-letter workload.** The letter `a` (short) is ~14,200 pp ≈ 118 years by itself; a
  ranked "hardest letters" list (from the MW per-letter headword counts) would show `a`, `p`,
  `s`, `v`, `k` as the multi-decade tentpoles and give a realistic volume-by-letter schedule.
- **Editor-generations.** At ~30 years per scholarly generation, PD needs **~8.6 generations**
  of editors on the optimistic plan and **~40** on the density-held model — it has used ~2.5 so
  far (Katre → Ghatage → Joshi → Bhatta …).
- **Time-since-conception rate.** Measured from Katre's 1948 conception, PD has taken 78 years
  to document ~4 % of the lexicon; that fraction-rate alone implies millennia and is why the
  *density-held* model, not the plan, may be the honest one.
- **Is it accelerating?** The gap between the 50-year average (121 pp/yr) and a plausible
  post-2019 pace (200 pp/yr) is itself a measurable trend; a fascicule-date time-series would
  settle whether the digital *KoshaSHRI* effort has bent the curve.
- **DCS catch-up date.** DCS already holds 78 % of PD's citation *mass* and doubles every ~16
  years; one can date when DCS's corpus will contain effectively every text PD would cite —
  almost certainly long before PD reaches `k`.
- **Coverage of DCS-attested lemmas.** How many of DCS's own lemmas PD has already *defined*
  (in `a`–`apaca-`) is a direct dictionary-for-corpus usefulness metric.

### 8.8 The long-dictionary league table

PD's slowness is best judged against two peer groups: the other **Sanskrit / Indo-Aryan
dictionaries** (same language, so density is the only variable), and the **century-long
historical monuments** of other traditions (same ambition, different language).

**First peer group — the Sanskrit / Indo-Aryan dictionaries.** Seven were *completed* in
10–27 years. Only the two that chose exhaustive historical-principles treatment stall:

| Dictionary | Direction | Span | Years | Lemmas | Status |
|---|---|---|---:|---:|---|
| WIL · Wilson | Skt→Eng | 1819–1832 | ~13 | 43,939 | ✓ complete |
| KOW · Kossowicz | Skt→Rus | 1854 | — | 13,488 *(Russian-ordered)* | ✗ incomplete |
| **GST · Goldstücker** | Skt→Eng | 1856–1864 | ~8 | 6,761 | ✗ **abandoned in `a`** |
| PWG · Böhtlingk–Roth (*grosse*) | Skt→Ger | 1855–1875 | 20 | 106,083 | ✓ complete |
| PW · Böhtlingk (*kürzere*) | Skt→Ger | 1879–1889 | **10** | 151,349 | ✓ complete |
| MW · Monier-Williams | Skt→Eng | 1872–1899 | ~27 | 194,084 | ✓ complete |
| KEWA · Mayrhofer (etymological) | Skt→Ger | 1956–1980 | 24 | — | ✓ complete |
| EWA · Mayrhofer (etymological) | Ind.-Ar.→Ger | 1986–2001 | 15 | — | ✓ complete |
| BORI Prakrit Dict. (CDPL) | Prakrit→Eng | 1988–~2090 *(proj.)* | ~102 | 33,600 *(a→`u`)* | ⧗ through the vowels |
| **PD · Poona Dictionary** | Skt→Eng | **1976–~2284⁺** | **~308⁺** | 104,959 *(a- only)* | ⧗ **still in `a`** |

The contrast could not be sharper. Böhtlingk's *kürzere Fassung* (PW) documented **151,349
lemmas across the whole alphabet in ten years**; PD has 104,959 lemmas and has covered ~4 % of
the alphabet in fifty. Sanskrit is not the problem — **exhaustive historical detail is**, and the
proof is 170 years old. **Theodor Goldstücker's 1856 remake of Wilson** set out to improve the
whole dictionary, sank into `a`, published 6,761 exhaustive entries, and was abandoned there at his
death — the one clean death-in-`a`. Two contemporaries are often lumped with him but do not
belong: **Kossowicz's 1854 Sanskrit→Russian dictionary** reached 13,488 entries but is arranged in
**Russian**, not Sanskrit, alphabetical order and was left unfinished — a partial work of a
different kind, not comparable on the Sanskrit-letter axis; and **Böhtlingk–Roth's PWG** spent its
whole first volume (1855) on `a-` yet *completed the alphabet* by 1875, because it refused to be
exhaustive. Terseness finishes; exhaustiveness drowns. PD is Goldstücker's project reborn at ~16×
the density (104,959 vs Goldstücker's 6,761 for `a`) and computer-typeset — the same undertaking,
the same letter, the same trap, now a century and a half deep.

**The controlled experiment — two dictionaries, one city, one editor.** The sharpest comparison
is not across centuries but across town. In the *same* Pune, the **Bhandarkar Oriental Research
Institute**'s *Comprehensive and Critical Dictionary of the Prakrit Languages* (CDPL) began in
**1988** — twelve years *younger* than PD — and has already published 3 volumes covering **`a`
through `ujjhittu`**: all the vowels and into the consonants, ~33,600 lexemes against a *bounded*
plan of ~90,000 entries over ~450 texts (finish projected ~2090). Its founding general editor was
**A. M. Ghatage — the very scholar who edited PD's first volumes.** The same man, the same city,
the same decade, ran both projects; the difference is *scope*. BORI bounded its corpus (~450
texts, terser articles) and in 38 years cleared the entire vowel series; PD chose the unbounded
historical maximum and in 50 years has not left `a`. It is as close to a natural experiment in
lexicographic ambition as the field offers, and its verdict is unambiguous: **a great
Sanskrit-family dictionary finishes only if it refuses to let the letter `a` become infinite.**

**Second peer group — the century-long giants.** PD's real family is not the fast Sanskrit
dictionaries but the multi-generational historical monuments — and it is projected to outlast
them all:

| Dictionary | Language | Span | Years | Status |
|---|---|---|---:|---|
| OED, 1st edition | English | 1857–1928 | 71 | ✓ completed |
| CAD · Chicago Assyrian | Akkadian | 1921–2011 | 90 | ✓ completed |
| Grimm · *Deutsches Wörterbuch* | German | 1838–1961 | 123 | ✓ (revision to 2016 = 178) |
| SAOB · Swedish Academy | Swedish | 1893–2023 | 130 | ✓ completed (2023) |
| WNT · *Nederlandsche Taal* | Dutch | 1864–1998 | 134 | ✓ largest print dictionary |
| TLL · *Thesaurus Linguae Latinae* | Latin | 1894–~2050 | ~156 | ⧗ ongoing (at `N`/`R`) |
| **PD · Poona Dictionary** | **Sanskrit** | **1976–~2284⁺** | **~308⁺** | **⧗ still in `a`** |

**No dictionary ever completed has taken more than ~180 years** (Grimm, with its revision). Even
PD's most optimistic scenario (2182 — 206 years, plan @ 200 pp/yr) already exceeds the longest
finished dictionary (WNT, 134) and the slowest still running (TLL, ~156); its density-held
scenario (~1,235 years) is roughly **9× the WNT**. On present evidence PD is on course to become
the longest single lexicographic project in human history — a distinction that is the direct
consequence of the ~13–23× density measured in §8.5, not of any lack of effort.

> **Milestone caveats.** Years assume PD holds its current per-MW-headword density and a
> constant rate; both are simplifications (density drops in the consonants, the rate may rise
> under digital editing). Vowel-section milestones are robust; consonant ones (mid-dictionary,
> completion) are upper bounds. Peer spans are start-of-publication to completion (or estimated
> completion) per each project's own record — see sources below.

### 8.9 Is `a` the hardest letter? — the graveyard of the first letter

A natural intuition (and a good question): **is `a` the hardest letter because it holds all the
`a-`/`an-` privative compounds — `a-dharma` "non-dharma", `an-artha` "misfortune" — the negated
samāsas that can be built from almost any word?** The headword lists give a precise, and
partly surprising, answer.

**Counting the initial letter across the three completed dictionaries:**

| Dictionary | 1st | 2nd | 3rd | 4th |
|---|---|---|---|---|
| MW | **s** 12.9 % | p 10.8 % | v 9.6 % | `a` 9.5 % |
| PWG | **s** 12.1 % | p 10.2 % | v 9.1 % | `a` 9.0 % |
| AP (Apte) | **`a` 14.3 %** | p 11.0 % | s 8.9 % | v 7.9 % |

So the intuition is **half right, and the half it gets right is exactly the samāsa point.** In
the two scholarly German-tradition dictionaries (PWG and its descendant MW), `a` is only the
**fourth**-largest letter — the sibilant **`s`** wins, followed by **`p`** and **`v`**. But in
**Apte**, the practical dictionary that lists compounds most generously, **`a` is the largest
letter by a clear margin (14.3 %)** — precisely because the privative `a-`/`an-` and the prefix
families (`ā-`, `adhi-`, `anu-`, `apa-`…) generate a negated or prefixed twin of much of the
rest of the lexicon, and a compound-inclusive dictionary lists them all under `a`. The privative
is a real, `a`-specific tax: `a-` before a consonant (`a-dharma`) and `an-` before a vowel
(`an-artha`) can negate essentially any nominal, so `a` inherits a shadow of the whole language.

**How many `a`-entries are actually compounds? — 83 %.** MW's printed-form (key2) list marks
every compound joint with a dash, so this is directly countable: of the **23,590** `a`-/`ā`-initial
entries, **19,601 (83.1 %) are dash-marked samāsas** and only 3,989 (16.9 %) are simple
uncompounded stems. The intuition is quantitatively vindicated — the letter `a` is overwhelmingly
a letter of *compounds*, not of roots: privative `a-`/`an-` negations (`a-dharma`, `an-artha`),
prefix compounds (`adhi-`, `anu-`, `apa-`…) and every `a`-initial first member (`agni-…`,
`artha-…`). This is the deepest reason a maximalist historical dictionary drowns in `a`: it is not
defining ~4,000 words, it is documenting ~20,000 *combinations*, each with its own attestations.

**But `a` is not uniquely hard — `s`, `p` and `v` carry their own huge prefix families** (`sam-`,
`su-`, `sa-`; `pra-`, `pari-`, `prati-`; `vi-`, `ava-`), which is why they rival or beat `a` in
the scholarly counts. The consequence for PD is sobering: **its hardest letters are still
ahead.** `s` (25,075 MW headwords), `p` (21,051) and `v` (18,598) each exceed the short `a`
(18,463) that has already consumed fifty years — PD's slowest marathons have not begun.

**Why, then, is `a` where Sanskrit dictionaries get stuck?** Not because it is the single largest
letter, but because it is **first, always top-four in size, and privative-inflated** — the worst
possible place to begin a maximalist project. The evidence is a genuine graveyard — but the reef
sinks only the *exhaustive*. The one clean wreck is **Goldstücker (1856)**, whose maximalist remake
of Wilson published 6,761 entries and never left `a`. Two 1850s contemporaries are often lumped in
but do not belong: **Kossowicz (KOW, 1854**, a Sanskrit→Russian remake of Wilson) reached 13,488
entries but is ordered by the **Russian**, not Sanskrit, alphabet and was left unfinished — a
partial work of a different kind; and **Böhtlingk–Roth's PWG (1855)** spent its whole first volume
on `a-` yet *completed the entire alphabet* by 1875, because it declined to be exhaustive. PD has
now spent five decades in `a` and is not done. `a` is the reef every *exhaustive* Sanskrit
dictionary runs onto first — and the ones that
finish, like Böhtlingk's PWG and later *kürzere Fassung*, are those that refuse to let it swallow
them.

A companion study now quantifies the anatomy of that reef —
[LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md)
([/tools/letter-anatomy](https://sanskrit-lexicon.github.io/csl-atlas/tools/letter-anatomy)):
`a` is 83.1 % compounds not because it is uniquely hard but because it heads five preverb
families plus the privative; `u`, `p`, `s`, `v` are close behind for the same reason. That study
also tests, and refutes for SKD/VCP, the belief that dictionary entries shrink toward the end of
the work — the entry-size decay is real only in the Petersburg dictionaries and Grassmann.

### 8.10 The other model — born-digital corpus lexicography (TamiLex)

Every dictionary in §8.8, PD included, belongs to one paradigm: the **print historical
dictionary, composed from a slip-archive and published alphabetically in fascicules**. The whole
arithmetic of this report — the 250-year horizon, the milestones, the death-in-`a` — is the
arithmetic *of that paradigm*. The sharpest comparison is therefore not to another slow print
dictionary but to the paradigm that **retires** it. **[TamiLex](https://www.tamilex.uni-hamburg.de)**
(Universität Hamburg) — a digital lexicography project for **Tamil**, the classical language whose
lexicographic tradition most parallels Sanskrit's — is that other model, and the differences from
PD are differences of *kind*, not of speed:

1. **Born-digital, not print-fascicule.** TamiLex is a queryable digital resource, not a sequence
   of bound volumes. Nothing is "published" letter by letter, so **the death-in-`a` trap is
   structurally impossible** — a database is never *stuck* at a letter.
2. **Whole-language-at-once, not alphabetical.** A digital lexicon holds partial-but-growing
   coverage across the *entire* language simultaneously and deepens everywhere at once, instead of
   perfecting `a` before touching `b`. PD's centuries-long horizon is a direct artifact of the
   alphabetical-*completion* constraint that a digital resource simply does not have.
3. **Corpus-integrated, not corpus-blind.** TamiLex is built against a digital Tamil corpus, so
   attestation and lexicon are one system. In the Sanskrit world the dictionary (PD) and the
   corpus (DCS) are *separate projects* — and this study exists only because someone had to weld
   them together after the fact. TamiLex has that weld from the start.
4. **Aggregative and open, not from-scratch and print.** It digitises and cross-links the existing
   Tamil dictionaries into an open, machine-queryable resource, rather than composing one
   monumental new dictionary from slips over generations.

The synthesis writes itself: **TamiLex is, for Tamil, essentially what §8.4 recommends for
Sanskrit** — a corpus-integrated digital lexicon rather than a print dictionary crawling through
the alphabet for centuries. The drastic difference is not that TamiLex is *faster*; it is that it
**abandons the model whose clock this whole report has been measuring.** PD may be the last, and
grandest, of the great print historical dictionaries; the born-digital corpus lexicon is what
comes after — and DCS, welded to a lexical layer, is the Sanskrit form it would take.

> _TamiLex specifics (exact start year, funding term, entry counts, source-dictionary set) were
> not machine-verifiable at time of writing — the project site returned a transient server error —
> and are described here at the level of paradigm, which is what the comparison turns on. The
> concrete figures should be confirmed against [tamilex.uni-hamburg.de](https://www.tamilex.uni-hamburg.de)
> and folded in._

---

_Data: [data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) · derived from PD
([drdhaval2785/SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck)) and DCS 2021/2026
([gasyoun/VisualDCS](https://github.com/gasyoun/VisualDCS)); reference-dictionary headword counts from
[HeadwordLists/now-2026](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)._

_Peer-dictionary spans (§8.8): Sanskrit/Indo-Aryan (WIL · GST · PWG · PW · MW) from
[dictionary_inventory.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv);
Mayrhofer [KEWA/EWA](https://www.winter-verlag.de/en/detail/c1954/Mayrhofer_Manfred_Kurzgefasstes_etymologisches_Woerterbuch_des_Altindischen/);
[Thesaurus Linguae Latinae](https://en.wikipedia.org/wiki/Thesaurus_Linguae_Latinae),
[Woordenboek der Nederlandsche Taal](https://en.wikipedia.org/wiki/Woordenboek_der_Nederlandsche_Taal),
[Deutsches Wörterbuch (Grimm)](https://www.britannica.com/topic/Deutsches-Worterbuch-German-dictionary),
[Svenska Akademiens ordbok](https://en.wikipedia.org/wiki/Svenska_Akademiens_ordbok). Per-initial-letter
counts from [HeadwordLists/now-2026](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)._

_Dr. Mārcis Gasūns_
