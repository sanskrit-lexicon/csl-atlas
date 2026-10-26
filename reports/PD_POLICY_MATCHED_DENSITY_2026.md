# PD policy-matched density: simplex, derivative, compound (H7297)

_Created: 26-10-2026 · Last updated: 26-10-2026_

_Source data: Cologne PDScan 2020 `txt/pd.txt` (55,122,076 B, SHA-256 `4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442`), read-only · PWG: `csl-orig/v02/pwg/pwg.txt`, read-only · Raw ledgers: [pd_attestation_decomposition.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_attestation_decomposition.tsv) (H7095) and [pd_quotations_vs_pwg.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_vs_pwg.tsv) (H6949), unchanged._

## Question

The committed raw comparison reports **8.55× attestations** and **9.53× quotations** over the 4,093 lemmas both dictionaries treat, with a median of **4.0×** and **340** below-parity lemmas. PD's lemmatisation policy gives a headword to nearly every compound (70.7 % of its classified headwords), so the question this pass asks is narrow: **does the multiple survive when the comparison is stratified by the lemma's own morphological class, and what is the pooled ratio under a policy-neutral standard?**

This changes the comparison policy only. The quotation unit, the attestation count and the entry-family rule are the frozen H6949, H7095 and H7110 definitions; no raw number is rebuilt or replaced.

## Raw ledgers retained (not replaced)

| Measure | PD | PWG | ratio |
|---|---:|---:|---:|
| Attestations | 157,480 | 18,423 | **8.55×** |
| Quotations | 97,413 | 10,225 | **9.53×** |
| Median per-lemma attestation ratio | — | — | **4.0×** |
| Below-parity lemmas (PD < PWG) | — | — | **340** |

These are the H6949/H7095 values, re-read from their committed files by `--check`; the new table sits beside them.

## Homograph grouping and class rule

- **Homographs.** Both machine texts use a bare `k1`: homographs are separate `<L>` entries with the same `k1`, never numbered variants. A row is therefore the union of every homograph entry of that `k1` on each side; PD contributes up to 15 entries and PWG up to 9 for one shared lemma. The grouping is fixed before any result is read and is not revisited.
- **Class rule** (H7110, `scripts/lib/pd_family_rule.py`): the first `( … )` after the `¦` separator on the entry's first body line is split on hyphen, en-dash, em-dash and whitespace after stripping Vedic accents; one member is a **simplex**, a last member in the 15-suffix set is a **derivative**, otherwise a **compound**. 4,059 of the 4,093 shared lemmas classify; the 34 that do not (no analysis parenthesis, or a CORRECTIONS block) form an explicit `unclassified` stratum and are excluded from the standardised pool.

## Strata

| Stratum | lemmas | with PWG attestation | PD att. | PWG att. | ratio | 95 % CI | median | below parity |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| simplex | 773 | 624 | 46,236 | 6,144 | **7.53×** | 6.22–9.09 | 3.0× | 110 |
| derivative | 357 | 314 | 12,276 | 1,434 | **8.56×** | 6.95–10.65 | 5.0× | 17 |
| compound | 2,929 | 2,635 | 97,674 | 10,699 | **9.13×** | 8.64–9.65 | 4.5× | 209 |
| unclassified | 34 | 30 | 1,294 | 146 | **8.86×** | — | 3.0× | 4 |

The strata are close together: **7.53× simplex, 8.56× derivative, 9.13× compound**. The compound stratum is the largest (2,929 of 4,093 lemmas) and the densest, but it does not create the aggregate.

## Standardised pooled result

| Estimator | value | 95 % CI | meaning |
|---|---:|---|---|
| **Standardised, equal weights** | **8.41×** | 7.68–9.27 | each policy class counts 1/3; the policy-neutral headline |
| Raw ratio of sums | 8.55× | 7.99–9.15 | the H7095 value, unchanged |
| PD-mix mean of stratum ratios | 8.77× | — | weights the strata by their shared-lemma shares; a mean of ratios, not a ratio of sums |
| Simplex only | 7.53× | 6.22–9.09 | the most policy-matched subset |

**Answer: 8.41× under equal policy weights, against the raw 8.55×.** The standardisation moves the pooled ratio by 0.14×, i.e. the aggregate is *not* an artefact of the shared lemmas' family mix: PD is 7.5–9.1 times denser inside every class, and no weighting of the classes pushes the figure outside that band. Denominators are the 4,093 shared lemmas, 4,059 of them classified; the 95 % intervals are a stratified lemma bootstrap (2,000 replicates, seed 7297, ratio of sums per stratum, percentile interval), which resamples lemmas and therefore carries the heavy-tailed entries' influence.

## Below-parity set (frozen)

340 lemmas have PD attestations below PWG's — the 191 lemmas with zero PD attestations and a defined PWG denominator, plus 149 with a positive but insufficient count. By stratum: simplex 110, derivative 17, compound 209, unclassified 4. Membership is frozen by SHA-256 `e454ffb557beda394b79e97c1548cf621e1405ef6f8a171856afbba9b17000df` and re-checked on every `--check`.

## Inventory policy (PD-only entries) — a separate result

PD-only headwords are the 100,866 keys that have no PWG counterpart; they are published here and nowhere else in this pass. A PD-only headword is **thin** when its entry carries at most 1 attestation.

| Scope | headwords | zero att. | at most one | share | median att. | mean att. | attestation mass |
|---|---:|---:|---:|---:|---:|---:|---:|
| PD-only | 100,866 | 1,175 | 66,036 (65.5 %) | 100 % | 1.0 | 2.60 | 262,410 |
| Shared (4,093) | 4,093 | 264 | 703 | 100 % | 8.0 | 38.48 | 157,480 |

The inventory contrast itself — **23.2×** (PD 104,959 unique key1 against PWG's 4,519 lines to the *apaca* frontier) — is a **lemmatisation-choice ratio**. It is not a citation measure, not a density multiple, and never a typical per-headword claim: the extra headwords carry a median of 1 attestation each, against 8.0 in the shared set. PD's inventory policy multiplies headwords, not citations.

## What this does not claim

- PD is measured on the published letter-*a* fascicules only; the shared set is the 4,093 lemmas both dictionaries treat.
- PWG prints no analysis parenthesis, so its own class mix is not measurable; the standardised pool is a PD-class standardisation, not a two-sided one.
- The class rule is a published heuristic: a compound whose last member is a suffix word counts as a derivative, and 34 shared lemmas stay unclassified.
- No row here is a typical per-headword claim: every ratio is an aggregate with its own PD and PWG denominator, and the inventory contrast is never restated as a density multiple.
- No A68 prose, table, figure or canary value changes in this pass.

## Reproduction

```sh
python3 scripts/pd_policy_matched_density.py --check
python3 -m pytest tests/forensic/test_pd_policy_matched_density.py -q
```

`--check` re-derives the class join, every stratum denominator, the standardised pool, the bootstrap intervals and the canaries from the committed inputs and exits 2 with `STOP_CANARY_MISMATCH` on any drift. `--build --pd txt/pd.txt` re-derives the class ledger from the pinned source.

_Dr. Mārcis Gasūns_
