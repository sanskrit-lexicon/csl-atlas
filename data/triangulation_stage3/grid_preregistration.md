_Created: 30-10-2026 · Last updated: 30-10-2026_

# Stage 3 pre-registered interpretation grid — PD/PWG/NWS triangulation (H7484)

Committed **before** the Stage-3 triangulation runs and not retuned after.
Provenance: every branch condition and reading below operationalizes the
programme protocol already committed before Stage 1 — report
`research/notes/final_report_pwg-nws-pd-dcs-8294e5.md` §8 (grid +
hypotheses, "written before any join"), §12 (per-conclusion outcome table,
"stated before any join is run"), §13 (Stage-3 definition and kill-exits).
Stage 3 adds no new measurement of its own: it reads the committed Stage-1
and Stage-2 substrates and combines them under the rules below. The fenced
JSON block is machine-read by
[`scripts/triangulation_stage3_join.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/triangulation_stage3_join.py);
its sha256 is pinned in
[`tests/forensic/test_triangulation_stage3.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_triangulation_stage3.py),
so any post-hoc edit to this grid fails the drift gate.

The three apparatus types (protocol §8, verbatim roles):

- **PD** — primary-text apparatus, **partial** (letter a; late-20th-century,
  encyclopaedic, breadth-heavy).
- **PWG** — primary-text apparatus, **complete** (1855–1875, edition-anchored,
  densest citation apparatus in the Cologne collection).
- **NWS** — **secondary-literature meta-apparatus** (attestations transferred
  from ~150 secondary publications, Petersburg inventory).

Diagnostic rule (§13): convergence across apparatus types upgrades a finding
to corpus-structural; divergence along type lines quantifies editorial
artefact; contradiction localizes the finding to one programme.

## Branch rules

All inputs are committed quantities; the conditions fix how they combine into
Stage-3 verdicts. Band width = PD work-bootstrap band top − bottom
(31.52 − 19.15 = 12.37 pp), a PD-side dispersion yardstick committed at
Stage 1 from PD's own substrate.

- **BR1 — contradiction localisation.** Fires iff
  `coverage(PWG_Ω, stratum-excluded) > 31.52` **and**
  `PWG bootstrap p2.5 > 31.52` (point **and** 95 % work-bootstrap interval
  entirely above PD's band top). If fired: the "three-quarters of citation
  practice outside DCS" residue claim is a property of PD's late-20th-century
  breadth-heavy programme, not of citation apparatuses as a class — the A68
  headline **localizes to PD's programme** (§8 Contradiction; §13 stage-3
  kill-exit). If not fired: the residue claim stands as an apparatus-class
  fact pending further apparatuses.
- **BR2 — within-type programme gap.** Fires iff
  `|coverage(PWG_α, stratum-excluded) − coverage(PD_α)| > 12.37 pp` on the
  shared letter-a frontier. If fired: the coverage **level** is
  programme-relative *within* the primary-text type — programme dominates
  type as the explanatory axis for coverage level (divergence (a) sharpened:
  two same-type apparatuses differ by more than PD's own band width). If not
  fired: the programme axis fails at level and coverage differences revert to
  type/scope explanations.
- **BR3 — scope artefact.** Fires iff
  `|coverage(PWG_α, stratum-excluded) − coverage(PWG_Ω, stratum-excluded)|
  > 12.37 pp`. If fired: divergence (b) — letter-a anchoring distorts pooled
  levels (§8). If not fired: the alphabetical-scope artefact is **not real at
  the level dimension** in a completed dictionary; letter-a anchoring is
  level-safe (while H2's letter-pooling ban stands independently).
- **BR4 — type-line reality (NWS).** Fires iff
  `NWS key1 containment in PWG ≥ 80 %` **and**
  `headword-level attestation ρ(NWS, PWG) < 0.40` (the Stage-2 declared
  H5 thresholds). If fired: inventory containment without attestation
  convergence — the secondary/primary **type line carries information**;
  divergence along type lines measures the transfer-vs-excerption editorial
  artefact; NWS corroborates nothing at coverage level (its inventory join
  stays pre-registered out) and its three delimited roles stand. If not
  fired: NWS's mass either tracks PW's (transfer noise) or its containment
  is too weak to speak — readings per Stage-2 H5.
- **BR5 — dispersion convergence.** Fires iff
  `PWG per-letter dispersion (32.19 pp) > PD fascicle span (19.99 pp)`
  (both Stage-1 committed). If fired: letter-volatility of citation-weighted
  coverage replicates across **both** primary-text apparatuses — the
  dispersion structure is corpus-side; letter-level pooling is banned for
  the class, and PD's fascicle heterogeneity is not a PD idiosyncrasy.
- **BR6 — token-level convergence.** Fires iff
  `PWG-cited share of the 118-text DCS anchor (93.98 %) ≥ PD token-weighted
  2026 coverage (77.88 %)` and both `> 50 %`. If fired: at token level both
  apparatuses point into the same anchored corpus core — the corpus-side
  concentration structure converges across programmes (depth differs, level
  does not), corroborating the token-weighted row of §12. If not fired: the
  token-level structure is programme-relative too.

## §12-row outcome space (allowed verdicts, fixed before the run)

| §12 row (A68 conclusion) | Allowed Stage-3 verdicts | Decided by |
|---|---|---|
| Citation-weighted 25.16 % (88,929/353,512) | corroborate · qualify (divergence a) · **localize to PD** (contradiction) | BR1 ∧ BR2 |
| "Three-quarters of citation practice outside DCS" (264,583/353,512) | stand as class fact · **overturn / apparatus-specific** | BR1 |
| Residue four-cluster structure | corroborate · overturn · **not triangulable at row level here** | committed substrates (genre rows absent for PWG residue) |
| Declared-canon 8.0 % (118/1,476, band 7.78–8.32) | corroborate the declared-vs-exercised distinction · not testable | NWS H6 (82/174); PWG 527/2,665 analogue not row-committed |
| Token-weighted 77.88 %/74.06 % and growth concentration | corroborate via PWG-cited anchor share · qualify (edition-era) · diverge | BR6 |
| Density multiple (8.55×; median 4×) | already corroborated and bounded (Stage 1) — not re-measured | — |
| Chronological sense/citation order | H4 not executed in Stages 1–2 — **open**, no Stage-3 claim | — |
| "Deep, not broad" characterization | survives **for PD** · dies **as a class claim** | BR1 ∧ BR2 |

Unconditional (§12): the kośa reframing stands regardless; **no** Stage-3
result upgrades genre-level certification into task adequacy. Kill-exits
respected (§13): a stage-3 contradiction localizes the headline to PD's
programme; the H5 confirmation that would have reduced NWS to transfer noise
did not fire; the NWS↔DCS inventory join stays out; the H5 upgrade stays
H5940-gated.

## Machine block

```json
{
  "stage": 3,
  "handoff": "H7484",
  "protocol": "research/notes/final_report_pwg-nws-pd-dcs-8294e5.md §8+§12+§13 (committed before Stage 1)",
  "committed_before_run": true,
  "inputs": {
    "pd_alpha_pct":                  {"file": "data/pd/pd_dcs_metrics.json", "key": "metric_pd_citation_weighted_pct"},
    "pd_covered_mass":               {"file": "data/pd/pd_dcs_metrics.json", "key": "covered_mass"},
    "pd_primary_work_mass":          {"file": "data/pd/pd_dcs_metrics.json", "key": "primary_work_mass"},
    "pd_residue_mass":               {"file": "data/pd/pd_dcs_metrics.json", "key": "residue_mass"},
    "pd_token_2026_pct":             {"file": "data/pd/pd_dcs_metrics.json", "key": "metric_dcs_token_weighted_2026_pct"},
    "pd_token_2021_pct":             {"file": "data/pd/pd_dcs_metrics.json", "key": "metric_dcs_token_weighted_2021_pct"},
    "pwg_omega_se_pct":              {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "coverage.stratum_excluded_omega"},
    "pwg_alpha_se_pct":              {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "coverage.stratum_excluded_alpha"},
    "pwg_pooled_omega_pct":          {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "coverage.pooled_omega"},
    "pwg_bootstrap_p2_5":            {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "g5_battery.bootstrap_p2_5"},
    "pwg_bootstrap_p97_5":           {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "g5_battery.bootstrap_p97_5"},
    "pwg_h2_dispersion_pp":          {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "h2.dispersion_pp"},
    "pd_fascicle_span_pp":           {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "h2.pd_fascicle_span_pp"},
    "pd_band":                       {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "grid.PD_bootstrap_band"},
    "pwg_anchor_cited_pct":          {"file": "data/pwg_dcs/pwg_dcs_join_metrics.json", "key": "token_view.anchor_share_pct"},
    "nws_rho_total":                 {"file": "data/nws_layer/nws_layer_metrics.json", "key": "h5.rho_total"},
    "nws_letter_aggregate_rho":      {"file": "data/nws_layer/nws_layer_metrics.json", "key": "role1_attestation_mass.letter_aggregate_rho"},
    "nws_containment_pct":           {"file": "data/nws_layer/nws_layer_metrics.json", "key": "role1_attestation_mass.containment_pct"},
    "nws_attested_works":            {"file": "data/nws_layer/nws_layer_metrics.json", "key": "role2_declared_vs_exercised.attested_works"},
    "nws_declared_works":            {"file": "data/nws_layer/nws_layer_metrics.json", "key": "role2_declared_vs_exercised.declared_works"},
    "nws_pure_mw_mediated":          {"file": "data/nws_layer/nws_layer_metrics.json", "key": "role3_dependence_tracer.pure_mw_mediated_entries"},
    "nws_lex_mw_markers":            {"file": "data/nws_layer/nws_layer_metrics.json", "key": "role3_dependence_tracer.lex_mw_markers"}
  },
  "thresholds": {
    "nws_containment_min_pct": 80.0,
    "nws_rho_divergent_max": 0.40,
    "token_convergence_min_pct": 50.0
  },
  "branches": ["BR1", "BR2", "BR3", "BR4", "BR5", "BR6"],
  "kill_exits_respected": [
    "stage-3 contradiction localizes the A68 headline to PD's programme",
    "H5 confirmation (NWS = transfer noise) did not fire; NWS stays in its three delimited roles, upgrade H5940-gated",
    "NWS<->DCS inventory join stays pre-registered out",
    "no stage-3 verdict upgrades genre certification into task adequacy"
  ]
}
```

_Dr. Mārcis Gasūns_
