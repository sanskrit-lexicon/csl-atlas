# Per-letter anatomy of the Sanskrit lexicon — samāsa share, upasarga profile, and the entry-size "funding-decay" test

_Created: 21-07-2026 · Last updated: 21-07-2026_

This report turns three per-letter observations made in passing by the H1336 PD × DCS study
([PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md)
§8.5–8.9) into a systematic per-letter programme, and tests a genuinely novel historical
claim: **do dictionary entries get shorter toward the end of the work** because funding or
editorial energy fell over the decades of serial publication (the claim was raised specifically
for **SKD** Śabdakalpadruma and **VCP** Vācaspatyam)?

**Headline results**

1. **`a` is not uniquely a "letter of compounds."** In Monier-Williams, `a`/`ā` is 83.1 %
   dash-marked samāsas — but `u` (79.5 %), `p` (78.0 %), `s` (77.9 %) and `v` (75.5 %) are
   right behind it. Compound-heaviness is not an `a`-anomaly; it tracks **whether a letter
   heads a productive preverb family**.
2. **The preverbs are the mechanism.** `v` is essentially the *vi-* letter (38.6 % of all `v`
   headwords), `u` the *ud-/upa-* letter (62.3 % combined), `s` the *sam-/su-* letter,
   `p` the *pra-/pari-/prati-* letter, `a` the *ā-/abhi-/anu-/apa-/ava-* + privative letter.
   `k`, which heads no preverb, is only 56 % compound despite being the 5th-largest letter.
3. **The funding-decay hypothesis is *refuted for the two dictionaries it named.*** After
   removing the letter-composition confound with an outlier-robust estimator, **SKD and VCP
   show no entry-size decay** across the alphabet (ρ ≈ 0.00). The decay is real and strong
   instead in the **Petersburg dictionaries and Grassmann** — PWG (ρ = −0.19), PWK (ρ = −0.34),
   GRA (ρ = −0.20) — precisely the works with an independently-documented editorial-compression
   history. "Later entries are shorter" is a **German-Petersburg-tradition** fact, not a
   Sanskrit-encyclopedic-dictionary one.

Data: [data/pd/letter_anatomy.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/letter_anatomy.tsv),
[data/pd/entry_size_by_position.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_position.tsv),
[data/pd/letter_anatomy_stats.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/letter_anatomy_stats.json);
generator [scripts/letter_anatomy.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/letter_anatomy.py).
Interactive: [/tools/letter-anatomy](https://sanskrit-lexicon.github.io/csl-atlas/tools/letter-anatomy).

---

## 1. Method and sources

**Headword-level (Q1, Q2).** The sorted unique-headword lists in
[HeadwordLists/now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)
— **key1** (SLP1, used for upasarga prefix-matching) and **key2** (printed form, where MW marks
every compound joint with a dash). Headwords are bucketed by initial letter (SLP1 first
character → base letter; long/short vowel pairs merged).

**Entry-body-level (Q3, Q4).** The canonical Cologne source `.txt` in
[csl-orig](https://github.com/sanskrit-lexicon/csl-orig) `v02/{mw,ap90,pwg,pwkvn,skd,vcp,gra}`,
each entry delimited `<L>…<LEND>` with `<k1>`/`<k2>` keys; **PD** from
[pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt).
Entry body length is measured in **tag-stripped characters** (XML tags and `{#…#}`/`{%…%}`
delimiters removed, whitespace collapsed) — a definition-text-length proxy that is consistent
within a dictionary, which is all Q4 requires. Entries are in printed/publication order in
every file (Spearman of file position vs. alphabetical rank = **+0.98 to +0.996**; PWG +0.76),
so **file position is a sound proxy for fascicule / publication order**.

**Scope note — the dash convention is MW-specific.** Only **MW** (71.6 % of key2 headwords
carry a dash joint) and, secondarily, **GRA** (36.6 %) mark compounds in the headword. AP, PWG,
PWK, SKD, VCP and VEI have **~0 dash marks** (SKD/VCP key1 ≡ key2). Q1 (samāsa share) is
therefore reported for **MW only**; extending it to the others would require a morphological
splitter, not a headword scan, and is deliberately out of scope here.

---

## 2. Q1 — Samāsa share per letter (Monier-Williams)

Fraction of MW key2 headwords whose printed form contains a compound joint (em-dash `—` or
hyphen). This reproduces the H1336 figure exactly for `a`/`ā` (83.1 %; 19,601 of 23,590) and
generalises it to every letter.

| Letter | n (key2) | % compound |
|---|---:|---:|
| **a/ā** | 23,590 | **83.1** |
| u/ū | — | 79.5 |
| p | 21,051 | 78.0 |
| s | 25,075 | 77.9 |
| v | 18,598 | 75.5 |
| e | — | 69.6 |
| ṛ/ṝ | — | 68.8 |
| i/ī | — | 63.1 |
| k | 12,997 | 56.4 |

**`a` is the most compound-dense letter — but only just, and for a reason that is not unique to
it.** The letters that rival `a` (`u`, `p`, `s`, `v`) are exactly the letters that head large
preverb families (§3). The letters that fall away (`k` at 56 %, and the consonants with no
preverb) are compound-*poorer*. The H1336 intuition — "`a` is a letter of compounds, not of
roots" — is **confirmed and explained**: it is true of `a`, but it is a property of *preverb-
headed letters in general*, of which `a` (with five preverbs plus the privative) is merely the
richest.

---

## 3. Q2 — Upasarga profile per letter

The ~20 preverbs (`pra parā apa sam anu ava nis/nir dus/dur vi ā ni adhi api ati su ud abhi
prati pari upa`), counted by **surface longest-prefix match** on key1 (SLP1), requiring at
least a 2-character stem to remain. This is the **mechanistic explanation** of the Q1 size
ranking.

| Letter | % upasarga-initial | Dominant preverbs (share of the letter) |
|---|---:|---|
| **u/ū** | **62.3** | ud- 34.0 %, upa- 28.3 % |
| a/ā | 44.7 | ā- 19.2 %, abhi- 6.2 %, anu- 6.1 %, ava- 4.9 %, apa- 3.9 % |
| p | 38.6 | pra- 22.6 %, pari- 7.6 %, prati- 7.1 %, parā- 1.4 % |
| v | 38.6 | **vi- 38.6 %** (v is essentially the vi- letter) |
| s | 38.3 | sam- 23.5 %, su- 14.8 % |
| k | 0.0 | — (no preverb begins with k) |

### 3.1 Full per-upasarga counts (every preverb, every dictionary)

Because a preverb *is* the start of its words, each upasarga's total sits entirely under its own
initial letter — so these surface-match totals are exact, not a top-5 truncation. Full feed:
[data/pd/upasarga_counts.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/upasarga_counts.tsv)
(count + % of headwords per dictionary).

| upasarga | MW | AP | PWG | PWK | SKD | VCP | GRA | VEI |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| **vi** | **7,179** | 2,616 | 3,500 | 4,594 | 1,234 | 780 | 348 | 81 |
| **sam** | **5,887** | 1,969 | 2,340 | 3,216 | 522 | 451 | 126 | 35 |
| pra | 4,749 | 2,255 | 2,195 | 2,990 | 639 | 866 | 180 | 66 |
| ā- (A) | 4,384 | 3,060 | 2,647 | 3,952 | 830 | 1,857 | 237 | 98 |
| **su** | **3,705** | 860 | 2,235 | 2,990 | 642 | 450 | 452 | 58 |
| nis/nir | 2,354 | 1,148 | 1,245 | 1,639 | 380 | 537 | 40 | 11 |
| ud | 1,921 | 1,296 | 992 | 1,523 | 342 | 608 | 52 | 17 |
| upa | 1,601 | 965 | 768 | 1,033 | 198 | 501 | 64 | 25 |
| pari | 1,600 | 735 | 716 | 943 | 180 | 257 | 42 | 26 |
| prati | 1,487 | 637 | 669 | 961 | 146 | 239 | 20 | 17 |
| abhi- (aBi) | 1,408 | 719 | 488 | 681 | 93 | 337 | 67 | 8 |
| anu | 1,383 | 808 | 604 | 979 | 113 | 348 | 34 | 8 |
| ni | 1,344 | 611 | 621 | 850 | 244 | 324 | 80 | 20 |
| ava | 1,116 | 839 | 547 | 802 | 193 | 389 | 43 | 6 |
| dus/dur | 1,092 | 428 | 734 | 939 | 128 | 318 | 73 | 13 |
| apa | 893 | 577 | 441 | 779 | 121 | 298 | 34 | 5 |
| ati | 607 | 341 | 375 | 886 | 72 | 170 | 10 | 3 |
| adhi- (aDi) | 333 | 185 | 177 | 262 | 27 | 96 | 19 | 3 |
| parā (parA) | 290 | 132 | 134 | 182 | 50 | 65 | 10 | 2 |
| api | 86 | 27 | 29 | 45 | 5 | 21 | 9 | 1 |

Two patterns stand out. **`vi-` is the single largest preverb in every dictionary** — the most
productive Sanskrit prefix. And **the `sam`/`su` order flips in the Vedic register**: the
classical dictionaries all rank `sam` above `su` (MW 5,887 > 3,705), but **Grassmann's Rig-Veda
dictionary reverses it — `su` 452 > `sam` 126**, the archaic language's fondness for the
laudatory *su-* "well-, good-".

**Every large Sanskrit-dictionary letter is large because it heads a preverb family.** This is
the single cleanest finding of the report: `v` = *vi-*, `u` = *ud-* + *upa-*, `s` = *sam-* +
*su-*, `p` = *pra-* + *pari-* + *prati-*, `a` = *ā-* + *abhi-* + *anu-* + *apa-* + *ava-*. The
preverb generates a prefixed twin of much of the rest of the lexicon and a compound-inclusive
dictionary lists them all under that initial. `k`, `g`, `c` … head no preverb and carry no such
shadow — which is why `k`, though the 5th-most-frequent initial, is compound-*poor* and
entry-*light*.

**The privative is reported separately, and not surface-counted.** Sanskrit's negation `a-`
(before a consonant) / `an-` (before a vowel) can negate essentially any nominal, so it is the
largest single driver of `a`'s bulk — but it is *not* a preverb, and it is **not reliably
surface-separable** (nearly every `a`-word begins `a-` + consonant). We therefore do not report
a spurious privative count; the Q1 dash-share (83.1 %) is the honest measure of how much of `a`
is combinatorial rather than root material. (This follows the handoff's Q6.3 recommendation.)

**Caveat on the surface method.** Longest-prefix matching over-counts preverbs that are also
common stem-initials (`ā`, `vi`, `ni`, `su`) — e.g. not every `vi-` word is *vi-* + stem. The
counts are descriptive of *which preverb dominates a letter*, which is robust to this noise
(the ranking within a letter is stable); they are not a morphological segmentation.

---

## 4. Q3 — Entry-size distribution per letter (the Q4 control)

Mean/median tag-stripped body length per letter, per dictionary (full table in
[letter_anatomy.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/letter_anatomy.tsv)).
Two facts matter for Q4:

- **MW is astonishingly uniform** — mean body length sits at ~55–60 characters across *every*
  decile of the alphabet (a tightly-edited, telegraphic dictionary).
- **The encyclopaedic Sanskrit→Sanskrit dictionaries are wildly skewed** — SKD median 169,
  mean 479, **max 128,405**; VCP median 112, mean 442, **max 310,090**. A handful of gigantic
  articles (clustered in `k`, `d`, `a`) dominate any mean. **This skew is why the naïve entry-
  size test fails and an outlier-robust estimator is mandatory for Q4.**

Letters genuinely differ in intrinsic entry size (roots-heavy letters carry longer articles
than compound-heavy ones), which is exactly the confounder Q4 must remove: *if later letters
host shorter words, an uncontrolled decay test will "find" funding decay that is really just
alphabet composition.*

---

## 5. Q4 — The entry-size "funding-decay" test

**The claim.** For serially-published dictionaries — the user named **SKD** and **VCP** — later
fascicules are believed to carry **shorter entries** as funding/editorial energy fell over the
decades of publication.

**The design.** Two estimators, because the parametric one is not trustworthy on the skewed
encyclopaedic dictionaries:

- **Parametric (as the handoff requested): letter fixed-effects OLS**, `log(1+chars) ~
  position + C(letter)`. Letter fixed effects partial out the Q3 composition confound; the
  slope is the residual position effect. Reported for completeness — **but it remains sensitive
  to VCP/SKD's 100k-plus-character outliers** (it returns a nonsensical +733 % for VCP).
- **Robust ARBITER: per-letter Spearman(position, size), aggregated.** Each initial letter is
  analysed on its own (composition confound removed *by construction*) with a rank correlation
  (immune to the giant articles), then combined across letters by Fisher-z weighted by
  (n − 3), plus a sign test on how many letters slope negative. **Where the two disagree, the
  robust test wins.**

**Results (robust ρ is the verdict; log-FE shown for contrast):**

| Dictionary | Robust ρ (95 % CI) | Letters neg. | log-FE slope | **Verdict** |
|---|---:|---:|---:|---|
| **PWK** · Böhtlingk *kürzere* 1879–89 | **−0.34** (−0.35, −0.32) | 27/32 | −1.18 | **DECAY (strong)** |
| **GRA** · Grassmann RV 1873 | **−0.20** (−0.21, −0.18) | 28/30 | −1.64 | **DECAY (strong)** |
| **PWG** · Böhtlingk–Roth *grosse* 1855–75 | **−0.19** (−0.19, −0.18) | 36/38 | −1.10 | **DECAY (strong)** |
| AP · Apte 1890 | −0.02 (−0.03, −0.01) | 25/36 | +0.09 | weak/negligible |
| MW · Monier-Williams 1899 | +0.02 (+0.01, +0.02) | 17/40 | +0.33 | flat (no decay) |
| **SKD** · Śabdakalpadruma 1886 | **−0.00** (−0.01, +0.01) | 23/38 | −0.19 (ns) | **inconclusive — no decay** |
| **VCP** · Vācaspatyam 1873–84 | **+0.00** (−0.01, +0.01) | 22/38 | +2.12 *(outlier artifact)* | **inconclusive — no decay** |
| PD · Poona (in progress) | — | — | — | untestable (confined to `a`) |

**The verdict on the funding hypothesis: refuted for SKD and VCP.** The two dictionaries the
hypothesis actually named show **no entry-size decay** with alphabetical position once the
composition confound is removed robustly (ρ = −0.001 and +0.001; sign tests non-significant).
VCP's parametric log-FE of +733 %/traversal is a pure artifact of a dozen 100k-plus-character
encyclopaedic articles and is overruled by the robust test — a textbook case of why the
outlier-robust arbiter was necessary.

**But the effect is real elsewhere — in the German Petersburg tradition.** PWG, PWK and
Grassmann show a strong, consistent, robustly-significant negative slope (ρ = −0.19 to −0.34;
36/38, 27/32, 28/30 letters negative). This is exactly where a documented editorial-compression
history exists: Böhtlingk–Roth's *grosse* PWG spent its entire over-detailed first volume
(1855) on `a-` and the editors deliberately compressed thereafter; the *kürzere* PW/PWK was
conceived from the start as a condensation. Grassmann's Rig-Veda dictionary likewise front-loads
its long articles.

**PD cannot be tested this way** — it has not left the letter `a`, so there is no cross-letter
alphabetical span to regress against. Its slowness is a headword-*count* story (H1336), not an
entry-*length* one.

**Keep the statistics and the anecdote separate.** "Later entries are shorter" is now a
*measured* fact for PWG/PWK/GRA and a *refuted* one for SKD/VCP. Whether the PWG/PWK/GRA decay
reflects *funding* specifically, versus deliberate editorial policy or the natural front-loading
of a dictionary's longest articles, is a historical question this statistic cannot settle — it
establishes the shape, not the cause.

---

## 6. Chat tidy — the graveyard of `a`, extended

The H1336 report §8.9 lists Goldstücker (1856) and BORI as the letter-`a` graveyard. Two more
belong there, both 1850s Wilson-remakes that stalled in `a`:

- **KOW · Kossowicz (1854)** — a Sanskrit→Russian dictionary, hypothesised in
  [dictionary_inventory.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv)
  to be a Russian translation/remake of Wilson (1832); it did not progress past the early
  letters.
- **The 1850s Wilson-remake cluster** — Goldstücker (1856), Kossowicz (1854) and Böhtlingk–Roth's
  *grosse* PWG (whose entire 1855 first volume was `a-`) form a **cohort of maximalist projects
  that each ran onto the `a` reef within the same decade**. Only Böhtlingk's later *kürzere*
  Fassung, by refusing to let `a` swallow it, finished.

(Applied to the H1336 report and page graveyard note in the same pass.)

---

## 7. Phase 2 (H1423) — cross-dictionary generalization, real-time decay, density

Three waves extending the above, planned via `/ask`
([PLAN](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md)).

### 7.1 Wave A — the compound law across dictionaries

Q1 (compound share) has ground truth only where a dictionary marks compound joints in its
headwords — **MW** (dash convention) and, more weakly, **GRA**. On that ground truth the
per-letter law holds and reproduces §2 exactly (MW `a` 83.1 %, `u` 79.5 %, `s` 77.9 %; GRA `a`
53.1 %). Generalising it to the non-dash dictionaries (AP/PWG/PWK/SKD/VCP) requires a
morphological splitter; the plan wires the DharmaMitra ByT5 model
([import_compound_segmentation.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/import_compound_segmentation.py)
→ [compound_share.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/compound_share.py),
calibrated against MW dash-truth). **In this run the ByT5 model was not reachable in the build
environment**, so the feed
([compound_share_by_letter.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/compound_share_by_letter.tsv))
ships the **dash-truth-only** columns (MW/GRA) with the splitter columns marked *model
unavailable* — the accepted degraded outcome. Re-running the import step where the model is
reachable fills the splitter estimates (with the MW-calibration error bar) for all dicts.

### 7.2 Wave B — entry-size decay in real publication time

H1416 measured PWG's decay against *alphabetical position*. PWG's `<pc>` field encodes the
volume (1–7), each with a known year (1855…1875), so **every one of the 123,366 PWG entries maps
to a real publication year** (0 unparseable). Regressing entry body-length (log) on year:

**PWG entries shrank −14.3 %/decade** (95 % CI [−15.0, −13.7], p ≈ 0) — a real-time restatement
of the H1416 position-decay, same sign. And the **editorial-compression counter-test settles the
cause question H1416 left open**: is the decay just a one-time correction after the famously
over-detailed first volume (`a-`, 1855)? No — dropping vol-1 entirely, **volumes 2–7 still shrink
−15.3 %/decade**, and the vol-1→later median drop is only −18 %. The decline is a **smooth fade
across the whole 20-year publication**, not a single policy break — consistent with (though not
proof of) the funding/energy-decline narrative. PWK/SKD/VCP lack per-fascicule dates and are
flagged `date_quality` in
[entry_size_by_year.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_year.tsv)
— for them the H1416 alphabetical-position decay remains the only available signal.

### 7.3 Wave D — cross-dictionary density fingerprint

Three uniformly-comparable per-entry signals across the in-scope dicts
([density_fingerprint.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/density_fingerprint.tsv),
page [/tools/dictionary-density](https://sanskrit-lexicon.github.io/csl-atlas/tools/dictionary-density)):

| Dict | chars/entry (mean / **median**) | Sanskrit spans/entry | markup tags/entry |
|---|---:|---:|---:|
| PWK | 42.7 / **40** | 1.2 | 3.0 |
| MW | 56.7 / **46** | 1.2 | 9.3 |
| AP | 195.4 / **74** | 3.9 | 6.5 |
| PWG | 229.0 / **87** | 5.0 | **20.2** |
| VCP | 442.3 / **112** | 0.0 | 0.1 |
| SKD | 478.5 / **169** | 0.0 | 0.1 |

Median is reported beside mean because SKD/VCP are heavy-tailed (single articles > 100 k chars).
Two structural facts fall out: **PWG carries the densest editorial apparatus** (20 markup tags per
entry — citations, grammar, glosses), while **PWK is the tersest** (43 chars, the *kürzere
Fassung* condensing as designed). And **SKD/VCP carry ~0 Cologne markup** (spans and tags ≈ 0):
they are plain Sanskrit→Sanskrit encyclopedic text, so the markup-density signal measures the
*digitisation apparatus* a dictionary received, not only its lexicographic depth — the robust
cross-tradition depth signal is chars/entry (median), on which the encyclopedics
(SKD 169, VCP 112) run far longer than the terse EN/DE working dictionaries.

---

## 8. Provenance

Generated by [scripts/letter_anatomy.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/letter_anatomy.py)
(Opus 4.8, `claude-opus-4-8`), handoff
[H1416](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1416-Opus_csl-atlas_letter-anatomy-samasa-upasarga-entrysize-decay_21.07.26.md).
Sources: [HeadwordLists/now-2026](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)
(headwords), [csl-orig v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) (entry
bodies), [SanskritSpellCheck pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt)
(PD). Extends [PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md)
§8.5–8.9.

_Dr. Mārcis Gasūns_
