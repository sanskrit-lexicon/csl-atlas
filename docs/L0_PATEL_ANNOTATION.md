# Phase L0 — Patel co-annotation guide (the 5 judgement-bound conventions)

> **2026-06-03 UPDATE — gate largely CLOSED.** The Patel 2016 PDF
> (`refs/Patel_2016_Normalizing_headwords.pdf`) supplies the convention author's **own
> per-dict assignments** for all 7 conventions across the 36 Cologne-2016 dicts. These were
> ingested as gold (`s2d_patel_gold.py` → `data/L0/patel2016_assignments.csv`) and dims 1–7
> are now filled for **30 of our 32** dicts — no manual annotation needed. The sheet below is
> retained only for the **2 dicts Patel does not cover (LRV, FRI)** and the 3 source-less ones
> (KNA, KOW, AMAR). See [`L0_RESULTS.md`](L0_RESULTS.md) for the resulting tree.

**Date**: 2026-06-03 · **For**: M. Gasūns · **Sheet**: [`data/L0/patel_fillin.csv`](../data/L0/patel_fillin.csv)
**Why this exists**: dims 2 + 4 are auto-filled mechanically; the cladogram recovers all 6
lineage *families* but not fine directed lineage. Patel's other five conventions are the
high-resolution discriminators — filling them closes the gate and produces the final tree.

---

## How to use this

1. Open [`data/L0/patel_fillin.csv`](../data/L0/patel_fillin.csv) (175 rows = 35 dicts × 5 dims).
2. For each row, read the **`evidence`** (a computed rate) and **`examples`** (real headwords of each competing form), then type your call into the **`VALUE`** column. Optional `confidence` (0–1) and `notes`.
3. Push the CSV back (or hand it to me) — I re-run `s2b`→`s3` and the final tree drops out, no code change.

**You do not need the Patel 2016 PDF in front of you** — the evidence columns carry the discriminating signal. Where my candidate option labels differ from Patel's exact taxonomy, just write Patel's label in `VALUE`; the pipeline treats values as free categorical strings.

> The full convention taxonomy (all 30 dims + the numbered slots for Patel's exact
> option codes) lives in [`refs/fingerprint_conventions.md`](refs/fingerprint_conventions.md).
> If you have Patel 2016 to hand, dropping his enumerated options into the `(c.1)…(c.N)`
> slots there lets me pre-map more cells and shrink this sheet further.

Time estimate: ~30–50 cells carry real signal (many dicts share an obvious value); ~1–2 h.

---

## dim 1 — Anusvāra before consonants  ·  *effectively mechanical, please confirm*

**Convention.** When a nasal precedes a stop inside a word, is it written as anusvāra (SLP1 `M`: `akaMpita`, `akAMqa`) or as the homorganic nasal (`akampita`, `aNka`)? The sheet's `anusvāra-share` = M-before-stop ÷ (M-before-stop + homorganic-nasal-before-stop).

**The signal is unusually clean — suggested values (confirm or override):**

| anusvāra-share | suggested VALUE | dicts |
|---|---|---|
| > 0.50 | **anusvara** | **AP90 (0.999)**, **LRV (0.565)** |
| 0.13–0.50 | **mixed** | **FRI (0.235)** |
| < 0.13 | **homorganic** | all 29 others (STC 0.12, BHS 0.12, SCH 0.12, GRA 0.10, MD 0.10, CAE/PUI/CCS/PW/PWG/AP ≈ 0.08, MW 0.04, YAT 0.03, SHS/WIL/SKD ≈ 0.01, GST/MW72/BUR/BOP/BOR/AE/KRM ≈ 0) |

That AP90 (Apte 1890, Indian press) is near-pure anusvāra while the European scholarly editions are homorganic is historically expected — a good sanity check that the measure is sound.

## dim 6 — ṛkārānta words (ṛ-final agent nouns)  ·  *strong lineage signal*

**Convention.** How is an ṛ-stem agent noun (`kartṛ` "doer") cited — as the **bare stem** (SLP1 `kartf`), the **nominative** (`kartA`), or with **`-ar`/`-ṛ`** (`kartar`)? The sheet reports counts of f-stem / nom-A / -ar headwords.

**The discriminating split:**

| pattern | suggested VALUE | dicts (f-stem / -ar counts) |
|---|---|---|
| cites bare ṛ-stems | **stem-f** | WIL 80/1, SHS 80, MW72 228, BEN 210, MD 227, AP90 222/16, CAE 173, MW 157, INM 132, AP 125, BOP 106, VCP 96, STC 259, KRM 186 |
| cites ṛ-stems as **-ar** | **ar** | **PWG 0/134**, **PW 1**, **CCS 6**, **SCH 16** — the Petersburg/German school |
| sparse / index dicts | (judge from examples) | GRA 211/64 (both), ACC 1, BHS 5, PUI 10, MCI 2, SKD 13, FRI 9 |

PWG/PW/CCS/SCH writing `agnihotar` where WIL/MW write `agnihotf` is a clean editorial fingerprint of the Böhtlingk–Roth tradition — exactly the kind of within-family discriminator the tree currently lacks.

## dim 3 — Words ending with -at (śatṛ present participles / vatup-matup possessives)

**Convention.** Patel: 5 options across 3 (-at) + 2 (-vat/-mat) sub-conventions — how present participles in `-at` and possessives in `-vat`/`-mat` are listed/spelled. The sheet gives counts + examples of each ending; **assign from the examples** (Patel's exact 5-way label set needs the 2016 PDF — write the closest Patel label, or describe what you see).

Notable: **GRA -vat 274** (Rigveda possessives dominate), **BOR/AE -vat ≈ 1** (English-headword dicts have almost none), MW72/MW/MD/AP90 rich in `-at`.

## dim 5 — Anusvāra of verbs

**Convention.** Are nasal verbal **roots** cited with anusvāra (`aMS`, `aMh`) or the dental/labial nasal (`aMs`)? The sheet lists short nasal-bearing root headwords of each form. Many dicts list *both* `aMS` and `aMs` as separate root entries (see AP90/PWG/GRA examples) — note that as **both/mixed** if so. Index/reverse dicts (INM, ACC, BOR, AE) have no verb roots → **n.a.**

## dim 7 — vas/yas suffixes (perfect participle -vas, comparative -yas)

**Convention.** Spelling/listing of `-vas` (perfect participle, e.g. `vidvas`) and `-yas` (comparative, e.g. `garīyas`) stems. The sheet gives counts + examples; **assign from examples**. **GRA (-vas 83 / -yas 81)** is the outlier (Vedic forms); BOR/AE/SKD/ACC/BHS ≈ 0 (none in scope → judge n.a.).

---

## After you fill it

- Cells you leave blank stay at `unknown` (the pipeline is missing-aware — partial fills still help).
- The 3 source-less dicts (KNA, KOW, AMAR) are in the sheet marked *NO LOCAL SOURCE*; they need the Cologne text first, so skip unless you want to annotate from the print/scans.
- Hand back the CSV; I run `s2b_patel_auto.py` → `s3_cladogram.py` and update [`L0_RESULTS.md`](L0_RESULTS.md) with the final validated tree + recovery scores.
