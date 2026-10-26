# PD two-layer validation: letter-a strata and the print-only tail

_Created: 26-10-2026 · Handoff: [H7275](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7275-DeepSeek_csl-atlas_pd-two-layer-validation_26.10.26.md) · Layer-1 verdict: **not stable across fascicles** · Layer-2 verdict: **STOP_NO_PRINT_ACCESS**_

This is the validation pass MG ordered on 26-10-2026, not a new measurement of
PD. It reuses the committed publication ledger (H6947), the H6947 volume
measures, the H6949 quotation unit, the frozen H7110 entry-policy classes and
the A68 PD-to-DCS crosswalk (`data/pd/pd_dcs_text_crosswalk.tsv`, headline
metrics in `data/pd/pd_dcs_metrics.json`). It produces two independent verdicts
and does not merge them: one on the **internal stability** of the 25.2 % headline
across the measured letter-*a* material, and one on the **representativeness of
the machine text for the printed dictionary**, which cannot be assessed without
print access.

## 1. What was rebuilt, with every numerator and denominator

The H6949 quotation unit is re-run over the PDScan 2020 machine text and every
citation tail is resolved through `pd_siglum_families.tsv` (class:
primary / secondary / structural; `match_type`: covered / residue). The recount
reproduces the H6949 pins exactly — 384,217 siglum loci, 35,673 continuation
loci, 419,890 attestations — and lands at **88,363 / 348,430 = 25.36 %** against
the pinned H1336 point 88,929 / 353,512 = 25.16 %. The 0.20 pp difference is the
unmapped-token residue (below), not a revision of the headline.

| Stratum | Entries | Quotations | Attestations | Primary loci | Covered loci | Coverage |
|---|---:|---:|---:|---:|---:|---:|
| simplex | 18,495 | 58,312 | 85,573 | 69,732 | 20,262 | 29.06 % |
| derivative | 13,017 | 33,936 | 44,209 | 37,238 | 6,584 | 17.68 % |
| compound, no privative/preverb prefix | 58,979 | 114,681 | 150,955 | 128,489 | 27,783 | 21.62 % |
| compound, privative *a-* / *an-* | 9,438 | 51,411 | 76,303 | 62,066 | 17,444 | 28.11 % |
| compound, preverb | 7,187 | 43,068 | 61,500 | 49,744 | 16,082 | 32.33 % |
| unclassified (no first-line analysis) | 514 | 1,034 | 1,350 | 1,161 | 208 | 17.92 % |
| **total** | **107,630** | | **419,890** | **348,430** | **88,363** | **25.36 %** |

The five class rows plus the unclassified bucket partition the full 107,630
entry population (no double counting: each compound falls in exactly one of the
three compound buckets). The entry-policy rule is H7110's, frozen:
one analysis member ⇒ simplex; last member in the published suffix set ⇒
derivative; otherwise compound. Privative is the first analysis member `a`/`an`;
preverb is the first member in the 20-upasarga set. The class split is
citation-weighted, not entry-weighted: compound-other and derivative entries
carry fewer covered citations than simplex and privative entries.

Per-fascicle numerators and denominators are in
[`data/pd/pd_two_layer_fascicle.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_two_layer_fascicle.tsv)
(35 ledger rows; the 11 print-only rows carry empty measurement columns and keep
their `in_digital_text=no` marker). The measured 24 rows cover pp. 1–4328,
1976–2008.

## 2. Is 25.2 % stable across the measured letter-*a* material?

**No — not as a fascicle-level constant.** The pooled value is stable to
deletion but heterogeneous across the material it pools.

| Test | Result |
|---|---|
| Per-fascicle coverage, 24 measured rows | **16.91 % – 36.90 %** (min 8.2/2007, max 8.3/2008) |
| Fascicles outside ±2 pp of the pooled 25.36 % | **12 of 24** |
| Full range | **19.98 pp** |
| Leave-one-fascicle-out pooled value | **24.88 % – 25.61 %** (no single fascicle drives the headline) |
| Work-level bootstrap, 5,000 resamples over 5,106 sigla | **19.15 % – 31.52 %** (95 %, seed 7275) |
| Top-20 works | 17.23 % of primary citations; their own coverage 54.08 % |

Read together: the headline is not fragile to dropping any one fascicle, but it
is a pooled average over alphabetical windows whose own coverage differs by up
to 20 pp, and it depends heavily on which works are resampled. Quoting 25.2 %
as a property of "PD's letter *a*" is therefore only defensible with the range
or the fascicle table beside it. The pre-registered verdict rule (in
`pd_two_layer_stability.json`) returns **not stable**: the full range exceeds
8.0 pp.

The result does not contradict A68's use of 25.2 % as a corpus-level contrast
with the 77.9 % token-weighted figure — it bounds that use. It does rule out
treating 25.2 % as a stable per-volume or per-class measurement.

## 3. Layer 2 — the print-only tail: STOP_NO_PRINT_ACCESS

The 11 print-only ledger rows are 9.1–9.3 (2009–2011), 10.1 and 29–32
(2012–2016), and 33–35 (2018–2019): 1,552 of the ledger's 5,880 printed pages
(26.4 % of the page mass). They carry no machine text, and no page images are
available:

- no PDScan page-image directory exists in the estate (searched the GitHub and
  scratch trees on this box);
- `dcpune.ac.in` did not answer a 20-second HTTPS probe from this box (curl
  exit 000), and the Cologne route that serves `pdtxt.zip` serves machine text,
  not page images.

Accordingly the layer-2 artifact is a **frozen sampling manifest, not a
measurement**:
[`data/pd/pd_print_only_sample_manifest.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_print_only_sample_manifest.json)
with its 300 inspectable slots in
[`data/pd/pd_print_only_sample_slots.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_print_only_sample_slots.tsv).

| Freeze | Value |
|---|---|
| Quota | 300 slots, 100 per period (2009–2011, 2012–2016, 2018–2019) |
| Allocation | proportional to printed pages within each period, largest remainder, ties by ledger id |
| Page order | sha256(`seed_text|ledger_id|page`) |
| Seed text | `H7275 print-only sample v1 | 26-10-2026 | ledger rows 9.1-35` |
| Entry rule | first entry that **begins** at or after the page point; else first entry beginning on the next page |
| Status | **STOP_NO_PRINT_ACCESS** — slots are positions, entry identities are unobserved |

The manifest was generated from `pd_publication_ledger.tsv` alone
(`--manifest`), before any layer-1 run; it reads no machine text. Filling a slot
requires the printed page image and records the headword, page and first
citation tail. No machine-text row may be substituted for a print-only entry —
that would silently replace the object being validated. Because the slots are
unobserved, the second verdict is **not assessed**: the representativeness of
the digital text for the printed 2009–2019 fascicles remains an explicit
unknown, not a PASS.

## 4. A68-ready limitations paragraph

> Every figure here is computed on PD's published letter *a-* material only
> (six bound volumes, pp. 1–4328, 1976–2008). The citation-weighted coverage is
> a pooled average over 348,430 mapped primary citations, not a corpus constant:
> across the 24 measured fascicles it ranges from 16.9 % to 36.9 % (12 of 24 lie
> outside ±2 pp of the pooled 25.4 %), though dropping any one fascicle moves the
> pooled value only within 24.9–25.6 %. A work-level bootstrap puts the 95 %
> interval at 19.2–31.5 %, so the headline should be read as the centre of a
> heterogeneous distribution. Coverage is computed over mapped primary sigla;
> 9,535 residual citation-like tokens (2.5 % of siglum loci, mostly
> `comm.`/`cf.`/`e.` and OCR variants) are reported and excluded rather than
> coerced. The 11 print-only ledger rows (2009–2019, 1,552 of 5,880 printed
> pages) are unmeasured; a 300-slot print sample is frozen but unobserved, so
> the machine text's representativeness for the printed dictionary is untested
> and recorded as STOP_NO_PRINT_ACCESS. No claim is made for the unmeasured
> letters, and no extension to them should be planned.

## 5. What is not claimed

- Not a whole-alphabet statement: the measured object is *a-* to ~*apaca-* only.
- Not a print/digital validation: the print sample was not observed.
- Not a revision of A68's 25.2 %/77.9 % contrast; the 0.20 pp extraction
  difference is reported, and the pinned 25.16 % remains the quoted value.
- No future work is minted for other letters: MG's ruling is that such material
  will not arrive in his lifetime.
- H6947's per-volume entry size and source marking are inputs here, not
  deliverables; their numbers are unchanged.

## 6. Reproduce

```bash
# layer 2 only — ledger in, 300 frozen slots out; no machine text
python3 scripts/pd_two_layer_validation.py --manifest

# layer 1 + layer 2 — needs the external PDScan txt (pdtxt.zip → txt/pd.txt)
python3 scripts/pd_two_layer_validation.py --pd /path/to/txt/pd.txt
python3 scripts/pd_two_layer_validation.py --check --pd /path/to/txt/pd.txt

# pins that need no external text
python3 -m pytest tests/forensic/test_pd_two_layer_validation.py -q
```

Inputs and hashes are in `pd_two_layer_stability.json` (`sources`) and the
manifest (`pins`). Exit 3 means the machine text is missing; exit 2 means a
committed artifact differs from a fresh build.

## 7. Files

| File | What it is |
|---|---|
| `scripts/pd_two_layer_validation.py` | builder: strata, stability tests, frozen manifest; `--check` |
| `data/pd/pd_two_layer_fascicle.tsv` | 35 ledger rows × entries, quotations, attestations, primary/covered loci, coverage, Wilson CI |
| `data/pd/pd_two_layer_class.tsv` | 6 entry-policy classes, same measures |
| `data/pd/pd_two_layer_stability.json` | pins, canaries, recount, stability tests, verdicts, input hashes |
| `data/pd/pd_print_only_sample_manifest.json` | frozen 300-slot print-only sample (STOP_NO_PRINT_ACCESS) |
| `data/pd/pd_print_only_sample_slots.tsv` | the 300 slots, one per row, inspectable |
| `tests/forensic/test_pd_two_layer_validation.py` | 5 pins: byte-identical manifest rebuild, quota/frames, arithmetic, verdict shape, frozen classes |
