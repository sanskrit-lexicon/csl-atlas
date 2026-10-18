# Compound-depth evidence — corrected distribution, intervals, bounds, join, loose frame, GRA

_Generated 2026-10-18 for H6963 (rulings Q6–Q11 in [COMPOUND_DEPTH_CORRECTION_DECISIONS_2026-10-18](https://github.com/gasyoun/Uprava/blob/main/papers/A68/COMPOUND_DEPTH_CORRECTION_DECISIONS_2026-10-18.md))._

This note makes every new compound-depth number reproducible from committed inputs and gives each quoted cell an `n` plus an interval or a bound. It does **not** replace the 2026-10-17 probe report; it extends it under the 18-10-2026 rulings.

Builders (all deterministic — run twice, compare `sha256sum`):

```bash
python3 scripts/build-compound-depth-evidence.py --csl-orig /path/to/csl-orig
python3 scripts/build-compound-depth-loose-frame.py --csl-orig /path/to/csl-orig --source pypi
python3 scripts/pilot-gra-compound-depth.py --csl-orig /path/to/csl-orig --audit-only
python3 scripts/pilot-gra-compound-depth.py --csl-orig /path/to/csl-orig --source local --limit 500
```

`--csl-orig` is read-only; this repository never vendors the dictionaries. The evidence builder has no wall-clock field, so a second run is byte-identical.

## 1. Corrected distribution, markup depths 3–8 (Q6)

Source: the committed snapshot `data/compound-depth/typography-probe-2026-10-17.json` (sha256 `c902dd99b422…`), no new model calls. Record counts are recomputed from MW because the snapshot stores distinct surfaces only; their sum reproduces the census exactly (27,174 + 2,974 + 434 + 95 + 15 + 9 + 1 + 1 = **30,703** marker-3+ records). Output: `data/compound-depth/depth-distribution-2026-10-18.json`.

**Joints (MW markup) → immediate constituents (model read), valid rows only**

| markup depth | records | surfaces | valid | valid rate | model = 1 | model = 2 | model ≥ 3 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 27,174 | 6,946 | 4,488 | 64.6 % | 745 (16.6 %) | 2,121 (47.3 %) | 1,622 (36.1 %) |
| 4 | 2,974 | 1,190 | 821 | 69.0 % | 71 (8.6 %) | 186 (22.7 %) | 564 (68.7 %) |
| 5 | 434 | 196 | 140 | 71.4 % | 5 (3.6 %) | 12 (8.6 %) | 123 (87.9 %) |
| 6 | 95 | 47 | 32 | 68.1 % | 0 | 0 | 32 (100.0 %) |
| 7 | 15 | 8 | 6 | 75.0 % | 0 | 0 | 6 (100.0 %) |
| 8 | 9 | 5 | 2 | 40.0 % | 0 | 0 | 2 (100.0 %) |

The compression is monotone: the model reads 47.3 % of markup-3 rows as two members, but only 22.7 % of markup-4 and 8.6 % of markup-5. Above markup-5 the sample is too small to support a share (n = 32 / 6 / 2 valid; see the intervals in the JSON), so the tail is reported as a count, not a percentage headline.

**The corrected (IC) series over all 3+ surfaces** (`n` = 5,489 valid of 8,394 surfaces):

| model read | n | share of valid | Wilson 95 % CI (valid) | share of all surfaces |
|---:|---:|---:|---|---:|
| 1 | 821 | 15.0 % | 14.0–15.9 % | 9.8 % |
| 2 | 2,319 | 42.3 % | 41.0–43.6 % | 27.6 % |
| 3 | 1,920 | 35.0 % | 33.7–36.3 % | 22.9 % |
| 4 | 331 | 6.0 % | 5.4–6.7 % | 3.9 % |
| 5 | 70 | 1.3 % | 1.0–1.6 % | 0.8 % |
| 6 | 22 | 0.4 % | 0.3–0.6 % | 0.3 % |
| 7 | 4 | 0.07 % | 0.03–0.19 % | 0.05 % |
| 8 | 2 | 0.04 % | 0.01–0.13 % | 0.02 % |

Model-read IC-3+ = **2,349 of 5,489 valid (42.8 %, CI 41.5–44.1 %)**. Scaling that rate to all 8,394 surfaces gives ≈3,592 (the ≈3,560 in the ruling), but that scaling assumes the 34.6 % missing rows are missing-at-random; the next section states what can move if they are not.

## 2. p2 interval and censoring bounds (Q10)

Output: `data/compound-depth/ci-bounds-2026-10-18.json`. `p2` is the share of valid rows read as exactly two members; intervals are Wilson 95 %.

The snapshot's missing rows are not exchangeable: `truncated` means the model dropped the first member, so the true depth is **at least** the returned token count + 1. Only truncated rows that returned ≤ 1 token can still be a 2-read. Empty and garbage rows carry no such restriction and are bounded adversarially (Manski).

| markup depth | valid | reads 2 | p2 of valid (95 % CI) | lower bound, all rows | upper bound, all rows | truncated still eligible for 2 |
|---:|---:|---:|---|---:|---:|---:|
| 3 | 4,488 | 2,121 | **47.3 % (45.8–48.7)** | 30.5 % | 52.3 % | 120 |
| 4 | 821 | 186 | 22.7 % (19.9–25.6) | 15.6 % | 32.8 % | 9 |
| 5 | 140 | 12 | 8.6 % (5.0–14.4) | 6.1 % | 21.4 % | 1 |
| 6 | 32 | 0 | 0.0 % (0.0–10.7) | 0.0 % | 17.0 % | 0 |
| 7 | 6 | 0 | 0.0 % (0.0–39.0) | 0.0 % | 25.0 % | 0 |
| 8 | 2 | 0 | 0.0 % (0.0–65.8) | 0.0 % | 60.0 % | 0 |

The headline cell is the markup-3 p2: **47.3 % (CI 45.8–48.7)**. Even under the worst case for the missing rows it cannot exceed **52.3 %**, and under the all-missing-are-not-2 case it cannot fall below **30.5 %**. The interval is therefore not the whole story; the bound is what licenses "about half", not "47 % exactly".

## 3. Deterministic headword join (Q11)

Output: `data/compound-depth/headword-join-2026-10-18.tsv` (2,121 rows) and `.json` summary. For every markup-3 row the model read as 2, the first two markup members are concatenated in SLP1 (plain concatenation, no sandhi rewrite) and looked up in the MW and PWG `<k1>` inventories:

| test | rows | share | Wilson 95 % CI |
|---|---:|---:|---|
| first two members = an MW or PWG headword | 2,101 | **99.1 %** | 98.6–99.4 % |
| — in both MW and PWG | 1,856 | 87.5 % | — |
| — MW only | 245 | 11.6 % | — |
| — residual (neither) | 20 | 0.9 % | — |

The join is reproducible byte-for-byte (sorted by `k2`, then `surface`; input hashes and TSV hash in the JSON). The 20 residuals are listed in the TSV with `residual=no_mw_or_pwg_headword`; they are genuine non-matches (`BUyo'kzara`, `anyonyaspar`, `indrajid`, …), not lookup failures. This is non-ML corroboration that the model's "read 2" is usually a lexicalised first member — `agni—zwoma—yAj/in` → `agniṣṭoma`, `agni—hotra—sTAlI` → `agnihotra` — and it is a much stronger result than the probe could state: 99 % of the 47.3 % cell has an independent dictionary headword for the pair.

## 4. Full loose frame (Q7)

Frame: every MW record whose `<k2>` has 3+ marker-separated members (em dash, hyphen or plus). **30,703 records → 28,977 distinct surfaces**; the census total is reproduced exactly. The frame is deterministic and committed beside the run (`data/compound-depth/loose-frame-2026-10-18.tsv`).

**Run: remote API cross-check** (`18,545` valid of `28,977`, `64.0 %`, Wilson CI `63.4–64.6 %`). The pinned local run is the canonical path under Q9 but is not this snapshot: on a 1-vCPU host the model generates ~0.45 rows/s, so the local full frame is ~18 h. The frame and runner are committed; this section reports what the cross-check measured, with the caveat made explicit.

| read | n | share of valid |
|---|---:|---:|
| 1 | 5,034 | 27.1 % |
| 2 | 7,310 | **39.4 %** (CI 38.7–40.1 %) |
| 3+ | 6,201 | **33.4 %** (CI 32.8–34.1 %) |

**Verdict: the loose frame is not the privative class.** Population B (single-hyphen privatives) read 3+ at **1.5 %** (CI 1.1–2.0 %); the full marker-3+ frame reads 3+ at **33.4 %** (CI 32.8–34.1 %), 22× higher. The preverb-joint class population A never sampled is therefore genuinely deep, not a typographic artefact; the loose numerator cannot be dismissed on the privative evidence.

Frame composition: 25,481 records at marker depth 3, 2,941 at 4, 434 at 5, 95 at 6, 15 at 7, 9 at 8, and 2 beyond. Marker types: 6,964 em-dash-only, 3,858 hyphen-containing, and 18,155 mixed. The frame TSV and JSON record every surface, status and returned token count; the API status mix is 2,714 empty, 3,258 garbage, 4,460 truncated, 18,545 ok — the same endpoint failure mode as the 2026-10-17 snapshot, which is exactly why Q9 moved the canonical path local.



## 5. GRA marker convention, then the pilot (Q8)

**Convention is stated before the number.** Output: `data/compound-depth/gra-marker-audit-2026-10-18.json`.

| fact | count |
|---|---:|
| GRA headwords | 12,785 |
| `<k2>` containing a hyphen | 4,356 |
| `<k2>` containing an em dash | **0** |
| hyphen characters in `<k2>` | 4,360 |
| em dashes in `<k2>` | **0** |
| hyphen characters in the whole file | 47,042 |
| em dashes in the whole file | 14,938 |

GRA's compound-member marker is the **hyphen**; `/` separates spelling variants, not members. The 14,938 em dashes are running-text punctuation (phrase brackets, ellipses), never headword segmentation. The cited "5,497 hyphens vs 1,045 em dashes" is therefore not a `<k2>` contrast: GRA `<k2>` has no em dash at all. Any GRA depth figure that reads em dashes as members is measuring the wrong layer.

GRA is shallow by construction: 8,432 unchained headwords, 4,349 with one hyphen, and only 4 with two or more. The pilot therefore samples the 4,356 hyphenated headwords and asks whether the model reproduces GRA's marked split.

**Pilot (500 sampled hyphenated headwords, seed 20261018; recorded cross-check, `data/compound-depth/gra-pilot-2026-10-18.json`):**

| statistic | value | 95 % CI |
|---|---:|---|
| valid reads | 304 / 500 (60.8 %) | 56.5–65.0 % |
| model reads 1 | 171 (56.3 %) | — |
| model reads 2 | 128 (**42.1 %**) | 36.7–47.7 % |
| model reads 3+ | 5 (**1.6 %**) | 0.7–3.8 % |
| exact agreement with GRA's hyphen split | 127 (**41.8 %**) | 36.4–47.4 % |
| model reads a compound at all (≥ 2) | 133 (43.8 %) | 38.3–49.4 % |

The convention is stated before the number: GRA marks a two-member compound with one hyphen, and the model reproduces that split in **41.8 %** of valid rows (CI 36.4–47.4 %), reading a single token in 56.3 %. GRA's hyphen therefore marks a *spelling/compound boundary* that the segmenter frequently treats as a bound prefix, not an immediate-constituent boundary; a GRA depth count must not be read as IC depth. The 3+ rate (1.6 %, CI 0.7–3.8 %) is statistically indistinguishable from the MW privative branch (1.5 %, CI 1.1–2.0 %), which is the cross-dictionary replication Q8 asked for.

This pilot is a **remote API cross-check**, not the canonical local run: the local 500-row run was started on the pinned revision but did not finish inside this unit's budget on a shared 1-vCPU host. The audit, sample selection and runner are committed; re-running with `--source local` is one command. No GRA number should be promoted to a paper cell until that local run lands.

## 6. What is still not canonical

- The 2026-10-17 snapshot (and therefore §§1–2) is a **remote API** run. Q9 makes the pinned local model canonical for new runs; §§1–2 add no new model calls, which Q6 explicitly permits, but the underlying reads remain API evidence. The local replication on 160 rows (92.5 % / 100 % valid, 79.3 % agreement) bounds the endpoint artefact; it does not replace the snapshot.
- The loose frame run above is the **recorded cross-check**, not the canonical local run. On this unit's box (1 vCPU) the pinned model generates ≈0.45 rows/s, i.e. ≈18 h for 28,977 surfaces; a local full-frame run needs a GPU or a multi-core host and is the remaining Q7 task. The frame, its hash and the runner are committed so that run is a single command, not a rebuild.
- Model output stays review evidence, never an input to `compoundSegmentCount` (docs/DHARMAMITRA_INTEGRATION.md).

## Provenance

| artefact | path |
|---|---|
| snapshot (input) | `data/compound-depth/typography-probe-2026-10-17.json` |
| corrected distribution | `data/compound-depth/depth-distribution-2026-10-18.json` |
| CI + bounds | `data/compound-depth/ci-bounds-2026-10-18.json` |
| headword join | `data/compound-depth/headword-join-2026-10-18.tsv` / `.json` |
| loose frame | `data/compound-depth/loose-frame-2026-10-18.tsv` / `.json` |
| GRA audit + pilot | `data/compound-depth/gra-marker-audit-2026-10-18.json`, `data/compound-depth/gra-pilot-2026-10-18.json` |

Model: Dharmamitra ByT5-Sanskrit (unsandhied); pinned local revision `chronbmm/sanskrit5-multitask@c0d2ada54f3d19903149425aa888a203601423f8`. Headword inventories: `csl-orig/v02/mw/mw.txt`, `csl-orig/v02/pwg/pwg.txt`, `csl-orig/v02/gra/gra.txt` (hashes recorded in the JSON artefacts).
