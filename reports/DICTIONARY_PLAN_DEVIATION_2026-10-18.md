# The ~3× plan-deviation rule, tested across Sanskrit and non-Sanskrit dictionaries

_Created: 18-10-2026 · H6984 · DeepSeek Flash (deepseek-flash)_

**Status: measurement note, not manuscript text.** This tests one claim — *"great dictionaries miss
their plans by ~3×"* — against every dictionary in the §8.8 corpus whose **plan was actually
documented at the start**. It is the plan-side companion to
[§8.8](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md#88-the-long-dictionary-league-table)
(the delivery-side league table) and to Uprava
[A68 §5](https://github.com/gasyoun/Uprava/blob/main/papers/A68/PD_FINISHABILITY_AND_THE_OED_STALL_2026-10-18.md),
which tests a *different* 3× claim (PD vs OED **size**). Nothing here enters the A68 canon until the
voice pass closes.

**Headline.** The rule is **true of size and false of time**. Across the completed plans we can
measure, a dictionary overshoots its planned *size* by a median **2.50×** (n=3) and its planned
*schedule* by a median **8.90×** (n=4). "~3×" is a fair summary of the first family and a
three-fold understatement of the second. Reporting one number for both is the same category error
that [H6985](https://github.com/gasyoun/Uprava/commit/f43d25acf6) caught when pages and entries
were mixed in a single ratio.

---

## 1. The claim, and what would falsify it

The claim under test is not §8.8's "PD's plan is ~3× the OED" and not A68 §5's volume/pages/entries
decomposition. It is a **behavioural** claim about plan-keeping in general: *a great dictionary
overshoots whatever it planned by a factor of about three.*

It is falsifiable in two ways, and this note tests both:

1. **If documented plans cluster near 3× on every axis**, the rule is real and useful.
2. **If the ratios do not cluster — if the answer depends on which axis you read or which
   dictionary you count — then "~3×" is an artefact of the counting rule, not a property of the
   craft.**

## 2. Method

**Three axes, measured separately** (the handoff's core requirement): **volumes** (or a volume
count), **pages**, and **elapsed years**. A dictionary can hit one and miss another, so each ratio
is computed and classified on its own axis.

**Ratio** = `delivered / planned`, per axis. For a completed work the numerator is the final
figure. For an unfinished work there is no final figure, so:

- on the **size** axes (volumes/pages/entries) the ratio is **progress** (`delivered ÷ plan`) and
  is classified `IN-PROGRESS`, never as a deviation;
- on the **duration** axis, where a planned *rate* exists, the ratio is a **projection**
  (`projected years ÷ planned years`) at the observed rate, labelled `basis=projection`.

**Four deviation classes**, as specified: `PLAN-KEPT` (< 1.5×), `PLAN-MISSED` (1.5–4×),
`PLAN-BROKEN` (> 4×), `NO-DOCUMENTED-PLAN`. `IN-PROGRESS` is added **only** for unfinished size
axes, because a 0.16 progress figure is not a 0.16 deviation and must never be averaged as one.

**Two source classes**, as specified: `[literature]` = the founding institution's own record, read
directly; `[secondary]` = an encyclopaedic summary, press witness, or third-party transcription.
**Each row carries the source that declares the plan**, and no plan is inferred: a dictionary with
no documented plan gets `NO-DOCUMENTED-PLAN`, not a guess.

## 3. What the corpus can actually support — 6 of 17

The §8.8 corpus is 17 dictionaries (9 Sanskrit/Indo-Aryan, 6 century-long monuments, 2 Eastern).
**Only 6 of them have a numeric plan documented at the start on any axis; 11 have none.**

| Dictionary | Plan documented at start | Source class | Delivered | Verdict |
|---|---|---|---|---|
| **OED**, 1st ed. | 4 vols · 6,400 pp · 10 yr (1879 contract) | [secondary] | 10 vols · ~15,500 pp · 49 yr | all three axes measurable |
| **Grimm**, DWB | 6–7 vols · 10 yr (1838) | [secondary] | 32 vols · 67,744 cols · 123 yr | volumes + years measurable |
| **TLL** | **15 years** for the whole (1894) | **[literature]** | 132 yr, still at N/R, ~2/3 done | years measurable (floor) |
| **CAD** | **10 years** (1921) | [secondary] | 26 vols · 90 yr (1921–2011) | years measurable |
| **PD** | 37 vols · 37,333 pp · 200 pp/yr (2017 plan) | [secondary] | 35 fascicles / ~6 vols · 6,056 pp · 50 yr | progress + projection |
| **CDPL** | ~90,000 entries over ~450 texts — entry axis only | [secondary] | 33,600 lexemes · 38 yr | progress only; no volumes/pages/years plan |
| WIL · GST · PWG · PWK · MW · KEWA · EWA | **none documented** | — | spans and counts in §8.8 | `NO-DOCUMENTED-PLAN` |
| WNT · SAOB · HDC · Nikkoku, 1st ed. | **none documented** | — | spans and counts in §8.8 | `NO-DOCUMENTED-PLAN` |

Two consequences follow immediately and constrain everything below.

**The evidence base is almost entirely secondary.** Only the TLL's 15-year estimate is
`[literature]` — read from the Bavarian Academy's own project history. The OED contract is the
publisher's own account read in a third-party transcription; Grimm, CAD and the rest are
encyclopaedic summaries. **No paper sentence may be built on these ratios until that is upgraded**
— the same discipline §8.8 already applies to its `[secondary]` Eastern rows.

**The denominator exists for a third of the corpus.** 41 of 52 dictionary-axis cells are
`NO-DOCUMENTED-PLAN`. The Sanskrit side is where the gap is widest: **not one of the seven
finished Sanskrit dictionaries has a documented numeric plan.** §8.8 can rank them by delivered
entries per year precisely because delivery is countable; it cannot say whether any of them hit a
plan, because no plan is in the record. That is an absence **in our source base**, not proof that
Böhtlingk or Monier-Williams planned nothing — a prospectus or publisher's announcement may still
exist, and finding one is a named open item (§7).

## 4. The measured distribution

### 4.1 Size axes — volumes and pages

| Dictionary | Axis | Plan | Delivered | Ratio | Class |
|---|---|---:|---:|---:|---|
| OED, 1st ed. | volumes | 4 | 10 | **2.50×** | PLAN-MISSED |
| OED, 1st ed. | pages | 6,400 | ~15,500 | **2.42×** | PLAN-MISSED |
| Grimm, DWB | volumes | 6–7 | 32 | **4.92×** | PLAN-BROKEN |

**Median 2.50× · mean 3.28× (n=3).**

This is where "~3×" lives. Three of the four size observations sit at 2.4–2.5×, and the mean lands
at 3.28× — close enough that a round "about three times" is a defensible summary **of size**.

Two caveats keep this from being stronger than it is. **The OED1 page count is not re-verified**
(A68 §5 carries the same warning): the 2.42× row is provisional. The only fully sourced OED size is
**OED2 (1989): 20 volumes · 21,730 pp · 291,500 entries**, from OUP's *OED editions* page (accessed
18-10-2026); against the same 6,400-page plan it gives **3.40×**. That is a different edition, so it
is printed beside the OED1 outcome, never substituted for it, and §8.8 shows both. And **a volume is
not a unit of size** — the OED's volumes average ~1,290 pp, PD's plan averages ~1,009 — so a volume
ratio is a count ratio, exactly the trap H6985 identified in a different pair of units.

### 4.2 Duration axis — elapsed years

| Dictionary | Plan | Delivered | Ratio | Class |
|---|---:|---:|---:|---|
| OED, 1st ed. | 10 yr | 49 yr (1879–1928) | **4.90×** | PLAN-BROKEN |
| TLL | 15 yr | 132 yr and counting (1894–2026) | **8.80×** (floor) | PLAN-BROKEN |
| CAD | 10 yr | 90 yr (1921–2011) | **9.00×** | PLAN-BROKEN |
| Grimm, DWB | 10 yr | 123 yr (1838–1961) | **12.30×** | PLAN-BROKEN |

**Median 8.90× · mean 8.75× (n=4).**

OED's 4.90× is **plan-anchored**: the ten-year plan was made in 1879. Measured from the 1857
Philological Society conception, as §8.8 also prints it, the 71 years to April 1928 give **7.10×**.
Both are stated per axis and neither is averaged with the other; the median above uses the
plan-anchored figure because no ten-year plan existed before 1879.

Not one documented schedule was kept, and **every one is PLAN-BROKEN by the handoff's own >4×
threshold**. The TLL's ratio is a floor, not a final figure: the 15-year estimate was made in 1894
and had reached only half of the letter D when it expired; the work is still at N/R after 132 years
and projects to ~156 by 2050 (10.4×). The OED is the *best* schedule-keeper in the set at 4.9× —
and it is the only one whose plan came with a publisher's contract and a deadline.

**5 of the 7 completed deviations are PLAN-BROKEN. None is PLAN-KEPT.**

### 4.3 The two unfinished plans

| Dictionary | Axis | Plan | Delivered | Ratio | Basis |
|---|---|---:|---:|---:|---|
| PD | pages | 37,333 | 6,056 | 0.16 | progress |
| PD | volumes | 37 | ~6 bound (35 fascicles) | 0.16 | progress |
| PD | years | 186.7 (at 200 pp/yr) | 308.2 (at realized 121 pp/yr) | **1.65×** | projection |
| CDPL | entries | ~90,000 | 33,600 | 0.37 | progress |

PD's **projected** duration ratio is 1.65× — the mildest duration number in the whole set, and
still PLAN-MISSED. It is mild because PD's plan is *already enormous* (187 years at its own stated
rate), not because PD is keeping it. Its binding constraint is scope, not schedule: §8.8's
density-held model needs ~149,600 pages, four times the 37,333-volume plan — a **scope deviation**
that no plan-deviation ratio captures. That is the honest limit of this table: it can test whether a
dictionary hit the plan it wrote, not whether the plan was right.

## 5. Verdict

**The ~3× rule is a description of size, not of plan-keeping, and it does not survive as a single
number.** Three findings:

1. **Axis mixing manufactures it.** Size medians at 2.50×, duration at 8.90×. Averaged together the
   two families give roughly 6×; reported as one figure they give "about three" only if the size
   observations are over-weighted. The correct report is **two numbers, on two axes**, exactly as
   the handoff anticipated when it refused a single ratio.
2. **Denominator selection manufactures it too.** Only 6 of 17 dictionaries have any documented
   plan, and 4 of those 6 are the monuments *famous for missing theirs*. The documented-plan set is
   the notorious set — nobody writes a history of the dictionary that finished on time. So the
   8.90× duration median is an **upper bound** on the true population value: the 11 undocumented
   dictionaries might have kept plans we cannot see. "~3×" and "~9×" are both claims about a
   **self-selected 35 %** of the corpus.
3. **What is robust is the shape, not the centre.** Every documented schedule was missed, and every
   miss is >4×. Every documented size was missed too — but by 2.4–4.9×. **Great dictionaries miss
   their plans; they miss the calendar far worse than the paper.**

## 6. Why this matters for §8.8

§8.8's argument is that scope, not speed, is PD's binding constraint. This note sharpens it from
the other side: **the peer monuments that finished did so by breaking their schedules by an order
of magnitude, and they finished anyway.** Grimm planned ten years and took 123; CAD planned ten and
took ninety; TLL planned fifteen and has taken 132 so far. Finishing is not evidence of good
planning — it is evidence that the scope was survivable. PD's distinguishing feature is therefore
not that it is late. **Everybody was late. PD is the one whose scope is unbounded.**

That is a cleaner statement for A68 than "dictionaries run ~3× over", which would understate the
schedule failure by a factor of three and would invite the reply that PD's 1.65× projected
deviation is mild.

## 7. Limitations and open items

1. **Source upgrade.** Every plan except the TLL's is `[secondary]`. The OED contract should be read
   against the OED's own history page and Murray's 1879 appeal; the Grimm figures against the
   Weidmann contract or the *Allgemeine Zeitung* announcement of 1838.
2. **Sanskrit plans.** Seven finished Sanskrit dictionaries carry none in the record. A prospectus
   search (Böhtlingk–Roth's 1855 announcement; Monier-Williams's 1872 preface) could move several
   rows out of `NO-DOCUMENTED-PLAN` — the single highest-value extension of this table.
3. **Unverified OED1 page count.** ~15,500 pp is commonly cited and was not re-verified on
   17-10-2026; the 2.42× row is provisional until it is.
4. **Unit homogeneity.** Volume counts are not sizes when volumes differ in thickness; the TSV
   flags this on PD and OED. A page-based table would be the stronger instrument, but page plans
   exist for only one dictionary.
5. **`IN-PROGRESS` is an extension, not a fifth deviation class.** It exists so unfinished plans
   are never averaged as if they were deviations; the four classes the handoff names still cover
   every completed plan.

## 8. Data and reproduction

- Machine-readable table: [`data/plan_deviation.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/plan_deviation.tsv)
  — 52 rows, one per (dictionary, axis), 18 columns, with `plan_source`, `outcome_source`,
  `plan_source_class`, `ratio`, `classification`, `status`, `basis` and `caveat`.
- Validator: `npm run validate-plan-deviation` — recomputes every ratio from its own plan/delivered
  pair, re-checks each classification against its ratio band, refuses an undocumented plan that
  carries a value or a source class, and pins the aggregates this report quotes (so a data edit
  that moves a figure fails CI rather than leaving the prose stale).

_Plan sources: [TLL Geschichte](https://thesaurus.badw.de/ueber-den-tll/geschichte.html)
([literature], the 15-year estimate and the "half of D" outcome); [OUP, History of the
OED](https://public.oed.com/history/) (accessed 18-10-2026; the 1857 Philological Society call, the
1879 agreement and the 4-volume / 6,400-page / 10-year plan); [OUP, OED
editions](https://public.oed.com/history/oed-editions/) (accessed 18-10-2026; OED2, 20 vols /
21,730 pp / 291,500 entries); [Deutsches Wörterbuch](https://en.wikipedia.org/wiki/Deutsches_W%C3%B6rterbuch)
([secondary], 6–7 volumes and ten years); [Chicago Assyrian
Dictionary](https://en.wikipedia.org/wiki/Chicago_Assyrian_Dictionary) ([secondary], "initially
expected to take 10 years"); PD from [PD_KNOWLEDGE_INDEX §2/§4](https://github.com/gasyoun/Uprava/blob/main/papers/A68/PD_KNOWLEDGE_INDEX.md)
([secondary], the 37-volume plan and the 2017 200 pp/yr plan, both press-mediated); CDPL from §8.8
([secondary], the BORI bounded plan). Delivery figures from
[csl-atlas §8.2/§8.8](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md)
and the encyclopaedic records above._

_Dr. Mārcis Gasūns_
