# PD policy-matched density: the 8.55× survives simplex/derivative/compound stratification; the 23.2× inventory contrast is a policy artefact (H7297)

The raw H6949/H7095 comparison is unchanged — 157,480 : 18,423 attestations (8.55×),
97,413 : 10,225 quotations (9.53×), median 4.0×, 340 below-parity lemmas over the
4,093 shared lemmas. This pass changes the **comparison policy** only: each shared
lemma is assigned the frozen H7110 class from PD's printed analysis, and the ratio is
recomputed inside each stratum with its own PD and PWG denominator. PD is denser in
every stratum — **7.53× simplex** (773 lemmas), **8.56× derivative** (357), **9.13×
compound** (2,929) — and the equal-weight standardised pool is **8.41×** (95 % CI
7.68–9.27, 2,000-replicate stratified lemma bootstrap, seed 7297), against the raw
8.55×. The aggregate is therefore not an artefact of the shared lemmas' family mix;
the PD-mix mean of stratum ratios (8.77×) and the simplex-only subset (7.53×) bracket
the same answer. The 34 unclassified lemmas form an explicit stratum and stay out of
the standardised pool. Below-parity membership is frozen by SHA-256 (simplex 110,
derivative 17, compound 209, unclassified 4).

PD-only headwords are published separately as an inventory-policy result: 100,866
headwords with no PWG counterpart carry 262,410 attestations between them (median
**1**, mean 2.60; 66,036 at most one), against a median of 8 and a mean of 38.48 in
the shared set. The **23.2×** headword-inventory contrast therefore stays a
lemmatisation-choice ratio: never a citation measure, never a density multiple, never
a typical per-headword claim. Canaries: *akāmataḥ* (`akAmatas`: 31/75 against 2/6 =
12.5×), the compound stratum (2,929 / 97,674 / 10,699) and the 340-row below-parity
set. New `scripts/pd_policy_matched_density.py` (`--build --pd` / `--check`, the check
needs no external text), `data/pd/pd_policy_matched_{class,density,inventory}` artifacts,
`reports/PD_POLICY_MATCHED_DENSITY_2026.md`, 18 gold rows and 9 pins in
`tests/forensic/test_pd_policy_matched_density.py`. No A68 prose, table, figure or
canary value moves; the raw ledgers are read, not rebuilt.
