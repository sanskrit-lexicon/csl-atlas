# Convention-fingerprint reference — all 30 L0 dimensions (canonical taxonomy)

**Purpose**: the single source of truth for every fingerprint dimension used in
Phase L0 (and reused by L0.5/L0.6 and the typology papers). It enumerates each
dimension's option set, how it is currently obtained, and — for Patel's canonical
7 — the contrastive states we can measure versus the exact codes that live in
Patel 2016 and must be slotted in by M.G. / V. Patel.

**Companion**: [`../L0_DESIGN.md`](../L0_DESIGN.md) §2 (rationale), [`../L0_RESULTS.md`](../L0_RESULTS.md)
(first tree), [`../L0_PATEL_ANNOTATION.md`](../L0_PATEL_ANNOTATION.md) (the fill-in sheet),
[`concordance.md`](concordance.md) (numbering ↔ Patel 2016 ↔ CSV columns; the stability contract).
**Source of truth for code**: `scripts/L0/s2_fingerprint.py` (DIMS), `s2b_patel_auto.py`, `s2c_patel_evidence.py`.

### Status legend

| Tag | Meaning |
|---|---|
| `auto` | mechanically extracted from source XML by `s2_fingerprint.py` |
| `auto-patel` | mechanically extracted by `s2b_patel_auto.py` (a parseable Patel conv.) |
| `gate` | judgement-bound — awaits M.G. co-annotation (`patel_fillin.csv`) |
| `gate+pdf` | needs Patel 2016's exact option enumeration before annotation is final |

> **Convention on option labels.** The pipeline treats every cell value as a free
> categorical string, so canonical Patel codes (e.g. `1.5`) and descriptive labels
> (e.g. `homorganic`) are interchangeable. Where Patel 2016 enumerates N options we
> have left numbered slots `(c.1)…(c.N)` to be filled with his definitions.

---

## A. Patel's canonical 7 (dims 1–7) — exact taxonomy from Patel 2016

Source: **Dhaval Patel, "Normalizing headwords of Cologne digital dictionaries" (2016)**
(`refs/Patel_2016_Normalizing_headwords.pdf`; project repo `sanskrit-lexicon/hwnorm1`).
Patel both defines the options **and assigns every Cologne dictionary** to them — so dims
1–7 are now populated from his ground truth (source `patel2016`), not annotation. The
**Standard** line is Patel's recommended normalization target. Conventions are
multi-valued (a dict may follow several options); cells store the `+`-joined set.
English-headword dicts (BOR, AE, MWE) are excluded by Patel → dims 1–7 N/A.
Status: all `patel2016` ✅ (gate closed) except **LRV, FRI** (not in Patel's 36 → still `gate`).

### dim 1 — Anusvāra before consonants  ·  **6 options**
Before `य र ल व श ष स ह` every dict uses anusvāra uniformly (out of scope). Otherwise:
- **1.1** internal nasal → anusvāra (not when 1st compound-member ends in `m`), e.g. `akuṃṭhita` — *AP90*.
- **1.2** internal nasal → fifth letter of the varga (homorganic), e.g. `cañcala` — *31 dicts (almost all)*.
- **1.3** final anusvāra denotes **neuter gender**, e.g. `akauṭilyaṃ` — *AP90, SKD*.
- **1.4** final anusvāra denotes **avyaya** (where `m` expected), e.g. `anukāmaṃ` — *YAT*.
- **1.5** 1st compound-member ends `m` + 2nd starts with *jhar* → anusvāra, e.g. `saṃgīta` — *ACC,AP,AP90,BEN,BHS,CAE,CCS,MCI,MD,PD,PW,PWG,SCH,STC,VEI,WIL*.
- **1.6** compound-final `m` → fifth letter, e.g. `saṃgīta`→`saṅgīta` — *BOP,BUR,GRA,GST,KRM,IEG,INM,MW72,PGN,PUI,SKD,VCP,YAT*.
- Inconsistent on 1.5/1.6: PE, SHS, MW. KRM: 1.1/1.2 N/A (verbs). **Standard**: internal→anusvāra; final→`m`.

### dim 2 — Duplication of consonants after r  ·  **2 options**
- **2.1** duplication in all cases, e.g. `pūrvva` — *SKD, WIL*.
- **2.2** no duplication, e.g. `pūrva` — *all others*.
- Inconsistent: SHS, YAT (stored `2.1+2.2`); VCP leans 2.2 with a few exceptions. **Standard**: 2.2.

### dim 3 — Words ending with -at (śatṛ + vatup/matup)  ·  **5 options (3+2)**
śatṛ present participles:
- **3.1** → `-at`, e.g. `gacchat` — *AP,AP90,BOP,BUR,GRA,GST,MD,MW,MW72,PD,SHS,VCP,WIL,YAT*.
- **3.2** → `-ant`, e.g. `anāgacchant` — *BEN,BHS,CAE,CCS,PW,PWG,SCH,STC,VEI*.
- **3.3** → `-an`, e.g. `paśyan` — *SKD*.
vatup/matup possessives:
- **3.4** → `-vat/-mat`, e.g. `bhagavat` — *ACC,AP,AP90,BOP,BUR,GRA,GST,IEG,INM,MCI,MD,MW,PD,SHS,VCP,WIL,YAT*.
- **3.5** → `-vant/-mant`, e.g. `bhagavant` — *BEN,BHS,CAE,CCS,PW,PWG,SCH,STC*.
- Insufficient data: ACC,IEG,INM,KRM,MCI,PE,PGN,PUI,SNP (for śatṛ). **Standard**: 3.1 (`-at`).

### dim 4 — Uninflected / inflected headword  ·  **2 options**
- **4.1** inflected (nom. sg., prathamā ekavacana), e.g. `dharmaḥ` — *AP, AP90, SKD*.
- **4.2** uninflected stem, e.g. `dharma` — *all others*.
- ACC inconsistent (`4.1+4.2`); KRM N/A (verbs). **Standard**: 4.2. *(My s2b mechanical agreed exactly: AP/AP90/SKD inflected.)*

### dim 5 — Anusvāra of verb  ·  **3 options**
- **5.1** verbs as in **Dhātupāṭha**, e.g. `stambh` (with anubandhas) — *KRM,PD,SKD,VCP,WIL*.
- **5.2** remove anubandha + convert to fifth letter, e.g. `stambh`→`stambh` — *AP,BEN,BOP,BUR,CAE,CCS,GRA,GST,MD,MW,MW72,PD,PW,PWG,SCH,SHS,STC,YAT*.
- **5.3** remove anubandha, keep anusvāra, e.g. `staṃbh` — *AP90*.
- Insufficient: ACC,BHS,IEG,INM,MCI,PE,PGN,PUI,SNP,VEI. PD in both 5.1 & 5.2. **Standard**: 5.3.

### dim 6 — ṛkārānta words  ·  **3 options**
- **6.1** → `-ar`, e.g. `kartar` (SLP1 `…ar`) — *BHS, CCS, PW, PWG, SCH* (Petersburg school).
- **6.2** → `-ṛ`, e.g. `kartṛ` (SLP1 `…f`) — *ACC,AP,AP90,BEN,BOP,BUR,CAE,GRA,GST,IEG,INM,MD,MW,MW72,PD,SHS,STC,VCP,VEI,WIL,YAT*.
- **6.3** → `-ā` inflected, e.g. `kartā` — *PUI, SKD*.
- Insufficient: KRM,MCI,PE,PGN,SNP. **Standard**: 6.2. *(My s2c mechanical agreed: PWG/PW/CCS/SCH `-ar`.)*

### dim 7 — vas/yas suffixes (kvasu/vasu/īyasun)  ·  **4 options**
- **7.1** → `-vas/-yas`, e.g. `vidvas` — *AP,AP90,BOP,BUR,CCS,GRA,GST,INM,MCI,MD,MW,MW72,PD,PE,SHS,VCP,WIL,YAT*.
- **7.2** → `-vāṃs/-yāṃs`, e.g. `vidvāṃs` — *BHS, STC*.
- **7.3** → `-vān/-yān`, e.g. `vidvān` — *PUI, SKD*.
- **7.4** → `-vaṃs/-yaṃs`, e.g. `vidvaṃs` — *CAE, PW, PWG, SCH*.
- Insufficient: ACC,BEN,IEG,PGN,SNP,VEI; KRM excluded. **Standard**: 7.1.

---

## A′. Patel's open conventions — dims 31–33 (`patel-open`, computed L0.9 2026-06-03)

Patel's paper §TODO left four conventions unfinished. `s2e_patel_open.py` operationalises
three via his own **probe-lemma method** (test which citation form of a diagnostic lemma each
dict lists as a headword). Multi-valued cells (`+`-joined). Contributed back as [hwnorm1#21](https://github.com/sanskrit-lexicon/hwnorm1/issues/21);
data in `data/L0/patel_open_assignments.csv`.

### dim 31 — takārānta (mahat-type) · **4 options** · `patel-open` ✅ (validated 100% vs Patel's महत्)
Probe `mahat`/`bṛhat`. **31.1** `-at` · **31.2** `-ant` · **31.3** `-ān` · **31.4** `-ānt`.
−ant group {BEN,CAE,CCS,FRI,PW,PWG,SCH,STC} ≈ the Petersburg+Cappeller cluster (tracks dim 3).
Reproduces the paper's published महत् split at **23/23 (100%)** on classified dicts.

### dim 32 — sakārānta (s-final stems) · **2–3 options** · `patel-open` *(new — completes §TODO)*
Probe `manas/tejas/payas/yaśas/dhanus/cakṣus`. **32.1** `-as` (near-universal) · **32.2** `-aḥ`
visarga {AP,AP90,BHS,MW,SKD,STC}. Near-constant → low tree signal.

### dim 33 — rephānta (r-final stems) · **2 options** · `patel-open` *(new — completes §TODO)*
Probe `antar/punar/prātar/svar`. **33.1** `-ar/-r` (near-universal) · **33.2** `-aḥ` visarga
{AP,FRI,MW,MW72,SKD,STC}. Near-constant.

### (documented, not yet a dim) ṛ-nipātita
Probe `jāmātṛ/naptṛ/…`; same method, needs a curated nipātita lemma list before it is conclusive.

---

## B. Added dimensions (8–30) — fully defined, mostly `auto`

Grouped as in L0_DESIGN §2.2–2.9. Option sets here are canonical (no PDF needed).

### Sandhi & compound handling
- **8 Sandhi at compound boundary** · `preserved` | `split` | `both` · `gate` (judgement).
- **9 Compound-headword separation** · `hyphen` | `space` | `merged` · `auto`.
- **10 Variant-headword inclusion (`<k2>`)** · `none` | `few` (<5%) | `many` (>5%) · `auto`.

### Polysemy & sense numbering
- **11 Sense numbering style** · `arabic` | `roman` | `alpha` | `sanskrit` | `unnumbered` · `auto`.
- **12 Sense-internal separator** · `semicolon` | `comma` | `period` | `colon` · `auto`.
- **13 Sub-sense indentation** · `present` | `flat` · `auto`.

### Citation conventions
- **14 Citation depth** · `full` (`Rv. 1.22.16`) | `partial` (`Rv. 1.22`) | `minimal` (`RV.`) | `mixed` · `auto`.
- **15 Citation format style** · `abbreviated` | `full` | `sanskrit` · `auto`.
- **16 Mahābhārata edition reference** · `pune` | `critical` · `gate` (judgement; partial auto-signal `MBh. crit.`).

### Grammar / gender markers
- **17 Grammar marker style** · `abbreviated` (`m./f./n.`) | `full` (`masc./fem./neut.`) | `sanskrit` (`puṃ./strī./napuṃ.`) · `auto`.
- **18 Verb-class marker style** · `roman` (`P.IX`) | `arabic` (`9.P`) | `sanskrit` · `auto`.

### Etymology & cross-reference
- **19 Etymology presence** · `none` | `partial` | `full` · `auto`.
- **20 Cross-reference syntax** · `explicit` (`see X`) | `k1` (`<k1>`) | `italic` | `absent` · `auto`.
- **21 Loanword marker** · `tagged` | `untagged` · `auto`.

### Vedic & accent
- **22 Vedic accent preservation** · `present` (`āgnís`) | `absent` · `auto`.
- **23 Vedic-only marker** · `flagged` | `unflagged` · `auto`.

### Loose ends
- **24 Frequency / rarity marker** · `present` (`(rare)`) | `absent` · `auto`.
- **25 Indeclinable marker style** · `ind` | `inv` | `nipata` | `unmarked` · `auto`.
- **26 Pāṇinian sūtra reference** · `cited` | `uncited` · `auto`.
- **27 Source-language identification** · `present` | `absent` · `auto`.

### Etymology / derivation richness (added 2026-05-16)
- **28 Etymology presence rate** · `>5%` | `<=5%` · `auto`.
- **29 Etymology mean-length** · `low` (<30 ch) | `med` (30–80) | `high` (>80) · `auto`.
- **30 Distinct etym-marker patterns** · `0` | `1` | `>1` · `auto`.

---

## C. Methodological taxonomy (encodings · metrics · algorithms · validation)

Locked in L0_DESIGN §3–§6; current implementation in `s3_cladogram.py`.

**Encodings** — A set-membership (one-hot, → Jaccard); B primary categorical (→ Hamming);
C inconsistency-flagged (categorical + confidence weight). *Note*: stage-2 yields a
primary-only cell, so B/C share one value → 4 live (encoding,metric) configs, not 9.

**Distance metrics** — plain Hamming; weighted Hamming (IDF, weight = −log₂ p(option),
rare-option mismatches cost more); confidence-weighted Hamming; Jaccard (encoding A).
All missing-aware (skip dims unknown in either dict).

**Algorithms** — UPGMA (scipy average linkage); Neighbour-Joining (Saitou–Nei);
Bayesian-consensus *approximated* by 1000× dimension-bootstrap majority-consensus UPGMA
(full MCMC deferred, design §9). Canonical config = `B_whamming`, pre-registered.

**Validation** — (a) known-edge recovery (knn-3 cophenetic / clade ≤ 5; target ≥ 70%);
(b) nearest-neighbour LOO (target ≥ 60%); (c) 1000× bootstrap support + Wilson 95% CI
(strong edge ≥ 0.80); (d) Robinson–Foulds across trees; (e) lineage-family cohesion.

---

## D. Known-edge ground truth (validation targets)

Directed parent → child. Tier A = high-confidence (inventory + sanhw1 containment);
Tier B = scholarly hypothesis under test (not assumed true).

| Edge | Tier | Basis |
|---|---|---|
| WIL → YAT | A | sanhw1 containment 0.926 |
| WIL → SHS | A | 0.953; r-duplication shared |
| YAT → SHS | A | Wilson line |
| PWG → PW | A | 0.938 (abridgement) |
| PW → CCS | A | 0.945 |
| CCS → CAE | A | same author Cappeller |
| MW72 → MW | A | self-expansion 0.896 |
| AP90 → AP | A | revised edition, ~2.6× |
| PWG → MW72 | A | MW72 preface cites PWG vols 1–4 |
| PWG → MW | A | 0.893 |
| PWG → SCH | A | Schmidt = continuation of PWG/PWK |
| BOP → MW | B | Bopp-dependence (0 direct citations; cognate-set test) |
| BEN → MW | B | candidate absorption |

*Multi-volume temporal nuance* (L0_DESIGN §13): PWG 1855–1875 (7 vols) → a PWG→MW72 (1872)
edge applies only to lemmas in vols 1–4 (≈ letters a–p). Range columns live in
`data/dictionary_inventory.csv` (`start_year, end_year, n_volumes, letter_coverage`).

---

## E. Future-phase dimension catalogs (pointers, not duplicated here)

- **L0.5 Nirukta** (WIL `.E.`): dhātu / suffix / upasarga token tables + Pāṇinian
  kṛt/taddhita/uṇādi/samāsa classification — L0_DESIGN §17.
- **L0.6 Subentry**: `Caus./Pass./Desid./Inten./Den./Periphr.` density + nesting depth +
  per-verb derivation matrix — L0_DESIGN §20.
- **Microstructure typology**: 24 verb-entry + 10 nominal dimensions — `../MICROSTRUCTURE-MACROSTRUCTURE.md`.
- **Macrostructure typology**: 20 dimensions — same doc.
- **M3-Bopp cognate-set test** (dim-19/BOP↔MW) — L0_DESIGN §18.

> When any future phase needs a fixed option set, add it to this file so there is one
> canonical taxonomy across the programme.
