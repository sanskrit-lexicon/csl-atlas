_Created: 04-06-2026 · Last updated: 05-09-2026_

# hwnorm1 contribution — completing the §TODO conventions

*Body of the issue opened on [`sanskrit-lexicon/hwnorm1`](https://github.com/sanskrit-lexicon/hwnorm1) as part of Phase L0.9. Kept here for the record. Computed by `scripts/L0/s2e_patel_open.py`; data in `data/L0/patel_open_assignments.csv`.*

---

**Title:** Completing the paper's §TODO conventions — takārānta (validated vs your महत् split), sakārānta, rephānta: computed per-dict assignments

The 2016 *Normalizing headwords* paper lists four conventions under §TODO that were left for a sequel: **takārānta** (mahat-type), **sakārānta**, **rephānta**, and **ṛ-nipātita**. As part of a computational genealogy of the CDSL dictionaries ([csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas), Phase L0), we operationalised the first three using your own **probe-lemma method** — for each dictionary, test which citation form of a small set of diagnostic lemmas appears as a `<k1>` headword — and offer the per-dict assignments back here.

### 1. takārānta (mahat-type) — reproduces your महत् split at 100%

Probing `mahat`/`bṛhat` forms and comparing to the महत् split published in the paper's §TODO: **agreement 23/23 (100%)** on the dictionaries you classified. (FRI, LRV are not in the paper's set; the method assigns them 31.2 and 31.1 respectively.)

| option | form | dictionaries |
|---|---|---|
| 31.1 | `-at` (mahat) | AP, AP90, BHS, BOP, BUR, GRA, INM, LRV, MD, MW, MW72, PUI, PW, SHS, SKD, VCP, WIL, YAT |
| 31.2 | `-ant` (mahant) | BEN, CAE, CCS, FRI, PW, PWG, SCH, STC |
| 31.3 | `-ān` (mahān) | PUI, SKD |
| 31.4 | `-ānt` (mahānt) | STC |

(PW, PUI, SKD, STC list more than one form — the inconsistency you flagged for PUI/PW/SKD.)

### 2. sakārānta (s-final stems) — *new*

Probing `manas, tejas, payas, yaśas, dhanus, cakṣus`:

| option | form | dictionaries |
|---|---|---|
| 32.1 | `-as` (manas) | AP, AP90, BEN, BHS, BOP, BUR, CAE, CCS, FRI, GRA, INM, LRV, MD, MW, MW72, PUI, PW, PWG, SCH, SHS, STC, VCP, VEI, WIL, YAT |
| 32.2 | `-aḥ` (manaḥ, visarga) | AP, AP90, BHS, MW, SKD, STC |

Near-uniform on `-as`; the visarga form co-occurs only in a handful (and aligns with the inflected-headword dicts of convention 4).

### 3. rephānta (r-final stems) — *new*

Probing `antar, punar, prātar, svar`:

| option | form | dictionaries |
|---|---|---|
| 33.1 | `-ar/-r` (antar) | AP, AP90, BEN, BOP, BUR, CAE, CCS, FRI, GRA, GST, INM, LRV, MD, MW, MW72, PW, PWG, SHS, SKD, STC, VCP, VEI, WIL, YAT |
| 33.2 | `-aḥ` (antaḥ, visarga) | AP, FRI, MW, MW72, SKD, STC |

Also near-uniform on `-ar`.

### 4. ṛ-nipātita — method ready, needs a curated list

The same probe approach applies (`jāmātṛ, naptṛ, …`) but needs a vetted nipātita lemma list to be conclusive; not run at scale yet.

### Method & caveats

- One membership test per (dictionary, lemma-variant) over the full `<k1>` headword set — identical in spirit to your महत् probe, just over a few diagnostic lemmas per convention.
- Probe-based, so a dictionary not listing a probe lemma is simply absent (not "no convention"). A full pass over *all* takārānta/sakārānta/rephānta lemmas would sharpen the multi-form dicts (PW, SKD, STC).
- Reproducible: [`scripts/L0/s2e_patel_open.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/s2e_patel_open.py); assignments CSV [`data/L0/patel_open_assignments.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/patel_open_assignments.csv).

Happy to open a PR adding these as conventions 8–10 (+ the validation harness) to hwnorm1 if useful, or to adjust the probe sets to forms you prefer.

_Dr. Mārcis Gasūns_
