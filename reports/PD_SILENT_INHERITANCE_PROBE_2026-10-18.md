# PD silent inheritance — inventory, citation and gloss overlap, calibrated on the bracket class (18-10-2026)

_Created: 18-10-2026 · Executor: DeepSeek (`deepseek-flash`) via DSH · Handoff: [H6948](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6948-DeepSeek_csl-atlas_pd-silent-inheritance-probe_18.10.26.md) · Complements [H6942 / PD preface measurements M1](https://github.com/gasyoun/Uprava/blob/main/PD_PREFACE_MEASUREMENTS_2026-10-18.md) and [PD_AOB_SIGLA_RECONCILIATION_2026-10-17.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_AOB_SIGLA_RECONCILIATION_2026-10-17.md)_

The Poona Dictionary brackets a dictionary source on **1.61–2.11 %** of its letter-*a*
entries (H6942, narrower convention: 1,801 entries = 1.67 %). That mark is the only
machine-visible trace of inheritance — a word or sense taken over silently leaves
nothing behind — so the published percentage is a **floor** whose ceiling was unknown.
This probe asks whether the floor can be *calibrated*: do the entries PD marks itself
behave measurably differently from the ones it does not?

**Short answer — the citation proxy fails, the gloss proxy survives, and what the
bracket marks is acknowledged *gloss* borrowing, not entry-level derivation.**

| axis | instrument runs? | calibrates the bracket? | sentence |
|---|---|---|---|
| inventory (macro) | yes | — | 92.5 % of PD's 104,773 letter-*a* headwords are absent from both PWG and MW; 98.3 % of those PD-only headwords are not DCS lemmas, against 59.7 % of the shared ones (40.3 % attested — the check works). |
| citation subsumption | yes (8–12× over null) | **no** — wrong direction | entries PD marks are *less* covered by the target's citations than unmarked ones (−7.9 pp against PWG, −13.4 pp against MW), and the abbreviation crosswalk reaches only 3.1–4.0 % of PD's citation mass. |
| gloss overlap | yes (63× over null, PD–MW) | **yes, for the named source** | entries marked `[MW]` reach Jaccard **0.262** against MW versus **0.198** unmarked (+0.064, 95 % CI 0.043–0.085; size-weighted +0.019). The `[PW]` mark does the same against PWG (+0.022, CI 0.013–0.032). |
| within PD, crosswalk-free | yes | yes, same direction | a marked entry is *gloss-only* far more often — no citation at all in **30.8 %** (strict mark: 37.2 %) against **1.3 %** unmarked — at the same median length (258 vs 266 chars). |

What follows from that: the mark is honest about *where a gloss came from* and says
nothing about wholesale entry derivation, **and the 1.61–2.11 % cannot be ranked**, only
read as a floor of *acknowledged* borrowing. A dictionary that inherited silently would
still look exactly like this.

---

## Control text and inputs

| input | identity | pinned |
|---|---|---|
| PD text | Cologne PDScan 2020 `pdtxt.zip` → `txt/pd.txt`, 55,122,076 B, header `Last_update_14.10.11`, **107,630 `<L>` records** (reproduced) | SHA-256 `b3b9c9ffc82219e204ce83143acd30cd6b5343593dcb3bc7649e8cea1cda30cc` (identical to H6924 and H6942) |
| PWG | `csl-orig/v02/pwg/pwg.txt`, 123,366 records | hashed into the JSON |
| MW | `csl-orig/v02/mw/mw.txt`, 286,525 records | hashed into the JSON |
| corpus attestation | `data/dcs/dcs_lemma_summary.json` — DCS 2021, 83,239 lemmas with `freqBand` | committed in-repo |
| PD siglum vocabulary | `data/pd/pd_siglum_families.tsv`, 4,988 primary sigla (353,512 occurrences) | committed in-repo |

Cologne refused direct connections from the Mac (three failure modes, as recorded in
H6924); the archive was fetched on prod `.92` and copied back. The array of record is the
**2020 scan of the 2009 text** — not a fresh upstream pull.

## Design

**Macro (full population, no sample).** Every PD letter-*a* headword (`<k1>`, house
`slp1_form_key`) against the letter-*a* headwords of PWG and MW:

- overlap: PD∩PWG, PD∩MW, PD∩both, PD-only;
- the PD-only residue against the DCS lemma table (attested / `freqBand`), with the
  shared headwords as the **control** (if the shared set also looked unattested, the DCS
  join would be the thing failing, not PD's vocabulary).

**Marks (full population).** Two conventions, both defined before the run:

- **broad** — every dictionary-source token anywhere in a bracket
  (`[infamous, MW., APTE]` counts 2). Vocabulary: DBHS · PW · APTE · MW · VIŚVA · NT ·
  VĀC, in the observed orthographic variants (`[DBHS]`/`[DBHS.]`, `[pw]`/`[PW.]`, …).
- **strict** — only brackets whose every comma/semicolon segment is a source token;
  this is the convention behind H6942's 1,801 / 1,956.

**Micro (shared headwords).** For every headword PD shares with a target:

- *citation set* — PD: curated-siglum matches in the roman prose (the
  `pd_extract_sigla.py` strip order: `{#…#}`, `{%…%}`, tags, page brackets, then a
  siglum token). PWG/MW: `<ls>` content, using the `n` attribute when the content is a
  bare locus;
- *gloss string* — PD: italic `{%…%}` plus running prose, minus Sanskrit payloads,
  brackets and sigla. MW: minus `<s>`, `<ls>`, `<gk>`, `<hom>`. PWG: italic (German
  gloss) plus prose, minus `<ls>`;
- *metrics* — citation Jaccard **on the shared abbreviation vocabulary only**,
  strict-subset flag (PD's mapped set ⊆ target's), **target coverage** (how much of the
  target's citation set PD reproduces — the direction-correct companion, because PD cites
  more distinct works per headword: median 6 vs 1 against PWG, 3 vs 0 against MW), and
  gloss-token Jaccard;
- *mappable share* — the fraction of PD citation mass the shared vocabulary can
  express. It is reported wherever a citation figure appears, because it caps what that
  figure can say: **3.11 % against PWG (72 shared abbreviations), 4.03 % against MW (55)**.

**Sampling frame (written before the run, implemented in the script).**

- *frame*: all PD letter-*a* headwords also present in the target's letter-*a* headwords;
- *strata*: `marked × PD entry-size class` (0 / 1–10 / 11–50 / 51–200 / 200+ chars);
- *sample*: `min(2,000, stratum size)` per stratum, `random.Random(20261018)`;
  3,050 rows against PWG (652 marked), 3,816 against MW (1,020 marked);
- *null*: each sampled PD headword re-paired with a target entry of the **same** PD
  size class, never its own form key. A metric with no lift over this null is not
  evidence, whatever its absolute value;
- *robustness*: every marked-vs-unmarked delta is also computed **within** each size
  class (pooled deltas mix classes whose metrics differ by an order of magnitude).

**Decision rule (written before the run).**

- **D1** — Δsubset rate (marked − unmarked) ≥ **10 pp** with the 95 % bootstrap CI lower
  bound > 0, on entries whose mapped citation set is non-empty;
- **D2** — Δgloss Jaccard ≥ **0.02**, same CI condition, on the PD–MW pair only (PD–PWG
  is a language-mismatch control: English against German);
- the bracket survives as a proxy only if **both** hold for at least one target.

Bootstrap: 2,000 resamples, seeded. Machine verdict is written into the JSON by the
script, not typed by hand.

## Macro — the inventory is PD's own

| measure | value |
|---|---:|
| PD letter-*a* entries | 107,630 |
| PD distinct letter-*a* headwords | **104,773** |
| PWG letter-*a* distinct | 9,483 |
| MW letter-*a* distinct | 18,430 |
| PD ∩ PWG | 4,086 |
| PD ∩ MW | 7,267 |
| PD ∩ both | 3,534 |
| **PD-only (absent from both)** | **96,954 = 92.5 %** |
| PD-only headwords that are DCS lemmas | 1,623 = **1.67 %** |
| shared headwords that are DCS lemmas (control) | 3,149 of 7,819 = **40.3 %** |

DCS band profile of the PD-only residue: absent 95,331 · band 1 (hapax) 938 · band 2
(2–9) 633 · band 3 (10–99) 51 · band 4 (100–999) 1.

**Reading.** PD's letter-*a* is not a superset of the older dictionaries' vocabulary
with some additions; it is 5.7× the size of MW's letter-*a* section (104,773 vs 18,430) and 11× PWG's
and 92.5 % of it is shared with neither PWG nor MW. The PD-only residue is also *not*
corpus vocabulary: two thirds of it (98.3 %) never appears as a DCS lemma, while the
shared headwords are attested at 40.3 %. Hand-reading a random sample of the residue
shows what it is — transparent compositional and technical formations
(`agnikāryaparityakta-`, `akṣarabāhulya-`, `ananyādhīnamahiman-`) — i.e. exactly the
material an encyclopaedic dictionary builds for itself. This is the strongest evidence
in the probe that PD's inventory is not silently inherited: a dictionary that copied
PWG/MW would share its headwords, not invent 92.5 % of them.

## Marks — PD against itself

| convention | entries | share | marks | by source |
|---|---:|---:|---:|---|
| broad | 2,269 | 2.11 % | 2,717 | DBHS 880 · MW 548 · APTE 526 · PW 485 · NT 145 · VIŚVA 126 · VĀC 7 |
| strict | 1,729 | 1.61 % | 2,007 | DBHS 844 · PW 377 · APTE 330 · MW 288 · VIŚVA 90 · NT 71 · VĀC 7 |
| H6942 (reference) | 1,801 | 1.67 % | 1,956 | DBHS 852 · PW 399 · APTE 264 · MW 245 · VIŚVA 101 · NT 84 · VĀC 11 |

The strict convention reproduces H6942's headline to within 0.06 pp; the difference is
the parser's treatment of multi-source brackets, not a different text. The broad channel
adds the gloss-prefixed brackets (`[infamous, MW., APTE]`), which H6942 did not count.
**Both figures keep the "marked inheritance" wording**: the mark is a printed act by the
editor, not a measurement of derivation.

**Within PD, no crosswalk involved:**

| group | n | citations/entry (mean) | entries with **zero** citations | median chars |
|---|---:|---:|---:|---:|
| unmarked | 105,351 | 2.63 | **1.29 %** | 266 |
| marked (broad) | 2,269 | 7.49 | **30.8 %** | 258 |
| marked (strict) | 1,729 | 5.57 | **37.2 %** | 229 |

A marked entry is the same length as an unmarked one but **24× more likely to carry no
citation at all**. That is the signature of a borrowed *gloss*: PD prints the meaning and
names the dictionary it took it from, instead of building its own citational apparatus.
The high mean (7.49) is a tail effect from a handful of long marked entries.

## Micro — citation sets

Shared-vocabulary slice only; `mappable_share` 3.11 % (PWG) / 4.03 % (MW) travels with
every figure below.

| measure | PD–PWG | PD–MW | shuffled null (PWG / MW) |
|---|---:|---:|---:|
| citation Jaccard (mapped), mean [95 % CI] | 0.124 [0.114–0.134] | 0.101 [0.092–0.109] | 0.010 / 0.009 |
| strict-subset rate, applicable rows | 0.269 [0.242–0.295] (n = 1,098) | 0.249 [0.225–0.273] (n = 1,292) | 0.023 / 0.020 |
| target coverage, mean [95 % CI] | 0.157 [0.145–0.168] | 0.133 [0.123–0.144] | 0.019 / 0.014 |

**The instrument runs** — every figure is 8–12× its own shuffled null. **The calibration
does not:**

| delta (marked − unmarked) | PD–PWG | PD–MW |
|---|---:|---:|
| Δ subset rate (applicable) | **−0.079** [−0.139, −0.021] n = 237/861 | **−0.134** [−0.180, −0.083] n = 333/959 |
| Δ target coverage | −0.014 [−0.043, +0.016] | **−0.041** [−0.063, −0.018] |
| Δ coverage, *named-source* marked | −0.064 [−0.098, −0.027] (n = 273) | −0.056 [−0.084, −0.028] (n = 489) |
| size-stratified weighted Δ subset | −0.030 | −0.073 |
| size-stratified weighted Δ coverage | −0.005 | −0.043 |

Marked entries are **less** subsumed by the target's citation set than unmarked ones, and
the sign does not go away when the comparison is made inside a single size class. The
direction is the opposite of the inheritance hypothesis, with CIs that exclude zero on
the MW pair.

Two structural reasons why the strict-subset test was the wrong instrument here, both
measured rather than asserted:

1. **PD cites more works per headword** — median 6 distinct works against PWG's 1, and 3
   against MW's 0 — so `PD ⊆ target` is biased against PD wherever PD is the larger set.
   That is why coverage is reported beside it; coverage fails in the same direction.
2. **The abbreviation crosswalk is not there.** PD prints its sigla in a **mixed
   SLP1/IAST convention** — `MahāBhā.`, `ṚV.` beside `AbhinBhā. i. 31. 11`, `ArthSaṃ. 10. 4`,
   `AnekaTi. 3. 9` — while PWG/MW use their own abbreviation stock. After the house
   diacritic fold, 55–72 abbreviations are shared and they carry 3.1–4.0 % of PD's
   citation mass. A work-level abbreviation crosswalk (PD siglum ↔ PWG/MW abbreviation ↔
   title) does not exist in the estate and is the prerequisite for a real citation test.

## Micro — gloss strings

| measure | PD–PWG (control) | PD–MW | shuffled null (PWG / MW) |
|---|---:|---:|---:|
| gloss Jaccard, mean [95 % CI] | 0.019 [0.017–0.020] | **0.202** [0.196–0.208] | 0.0004 / 0.0032 |
| median / p75 / p90 | 0 / 0 / 0.067 | 0.143 / 0.286 / 0.500 | 0 / 0 / 0 |

| delta (marked − unmarked) | PD–PWG | PD–MW |
|---|---:|---:|
| Δ gloss Jaccard, aggregate marked class | +0.010 [+0.004, +0.015] | +0.013 [−0.001, +0.027] |
| Δ gloss Jaccard, **named-source** marked | **+0.022** [+0.013, +0.032] (n = 273) | **+0.064** [+0.043, +0.085] (n = 489) |
| size-stratified weighted Δ | +0.008 | +0.019 |

The aggregate marked class does **not** clear D2 on the English–English pair (CI touches
zero); the **named** class does, decisively, in both targets: an entry that PD marks
`[MW]` overlaps MW's gloss vocabulary by 0.262 against 0.198 for an unmarked entry, and
an entry marked `[PW]` overlaps PWG by 0.039 against 0.017. The PD–PWG absolute level is
the expected cross-language floor (English glosses against German), and the instrument
still separates marked from unmarked there — which is itself evidence the `[PW]` mark
carries information independent of language.

**Disclosure.** The named-source test was added *after* the aggregate test failed, in the
same session; it is motivated by the marks' own vocabulary (the mark names MW or PW, so
the natural test is against the dictionary it names), but it is a secondary test and is
reported as such. The pre-registered verdict below uses the aggregate rule and stands.

## Verdict

| rule | result |
|---|---|
| **D1** Δ subset ≥ 10 pp, CI > 0 | **fails both targets** — and with the sign reversed |
| D1 on named-source marked | fails both targets |
| D2 Δ gloss ≥ 0.02, CI > 0 (PD–MW, aggregate) | **fails** (+0.013, CI −0.001…+0.027) |
| D2 on named-source marked | **passes** (+0.064, CI +0.043…+0.085) |
| **bracket proxy survives (script verdict)** | **false** |

**Which proxy survives.** The **gloss-token overlap against the dictionary the bracket
names**. It has instrument validity (63× its shuffled null), it responds to the mark in
the expected direction on both targets (+0.064 and +0.022 over unmarked), it survives
size stratification, and it needs no crosswalk. The **citation-subsumption / coverage
proxy does not survive**: it is crosswalk-limited to 3–4 % of PD's citation mass, it is
biased against PD's larger citation sets, and where it can be measured it points the
other way.

**What that makes the 1.67 %.** A floor of *acknowledged* borrowing — of a gloss, from a
named dictionary — and explicitly **not** a ranking of derived entries. The bracket
convention is not a proxy for inheritance; it is a proxy for explicit gloss attribution.
Any sentence built on it must say "marked inheritance" and must not claim that the
unmarked 98 % is PD's own work.

## Limitations (each one a place the next probe can break this)

1. **Mappable share 3.1–4.0 %.** The citation axis is a slice, not the whole. A
   work-level abbreviation crosswalk would be the single largest gain available here.
2. **PD's mixed sigla convention** is an obstacle, not an artefact of this parser:
   `AbhinBhā.`, `ArthSaṃ.`, `AnekaTi.` really are printed that way.
3. **DCS absence is not "unattested in Sanskrit".** DCS 2021 carries 83,239 lemmas; a
   word absent from it may be attested in a text DCS does not hold. 1.67 % is "not a DCS
   lemma", nothing stronger. The 40.3 % control is what makes it interpretable.
4. **Mark definition matters at the 0.5 pp level** (broad 2.11 % vs strict 1.61 %); both
   are reported, and the H6942 headline sits on the strict convention.
5. **Gloss overlap is lexical overlap**, not derivation. A shared gloss vocabulary can
   come from a shared English idiom for Sanskrit technical terms; the shuffled null and
   the size stratification bound that risk but do not remove it.
6. **The `nfold`-style nasal fold was rejected** for both citations and glosses after a
   hand check showed it turning *pumpkin* into *punpkin* and *MED.* into *ned.*; `norm`
   (diacritic strip + lowercase) is used instead. Roman numerals after a work title
   (`iv.`) are rejected as sigla. Four entries were hand-read end-to-end before the final
   run; the extraction defects they exposed (SLP1 residue in gloss tokens, roman-numeral
   sigla, nasal fold) are fixed in the committed script.
7. **Homograph structure is flattened** per headword: PD's 107,630 entries collapse to
   104,773 keys, PWG's 123,366 letter-*a* records to 9,483. Per-headword unions are what
   the calibration compares; a per-homograph test is a separate design.

## Reproduction

```sh
# PD text (Cologne refuses the Mac; fetch on .92 and copy back)
ssh root@193.232.229.92 'curl -sS -o /tmp/pdtxt.zip https://www.sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip && sha256sum /tmp/pdtxt.zip'
scp root@193.232.229.92:/tmp/pdtxt.zip /tmp/ && unzip -o /tmp/pdtxt.zip -d /tmp/pd

python3 scripts/pd_inheritance_probe.py --pd /tmp/pd/txt/pd.txt          # ~2 min
# writes data/pd/pd_inheritance_distributions.json + data/pd/pd_inheritance_metrics.tsv
# and prints the marks / macro / mappable_share / verdict blocks
```

The script is deterministic (seed 20261018) and pins every input by SHA-256 in the JSON.

## Landing

| artefact | what it is |
|---|---|
| [scripts/pd_inheritance_probe.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_inheritance_probe.py) | the probe: parse → marks → macro → micro → calibration → verdict |
| [data/pd/pd_inheritance_distributions.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_inheritance_distributions.json) | sampling frame, input hashes, marks census, macro, mappable share, calibration, **the three distributions with bootstrap CIs and quantiles**, verdict |
| [data/pd/pd_inheritance_metrics.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_inheritance_metrics.tsv) | 6,866 sampled headword rows × 21 fields — the per-headword metrics |
| this memo | which proxy survives, and the floor's interpretation |

No dictionary source, generated page or review packet was touched.

_Dr. Mārcis Gasūns_
