_Created: 08-09-2026 · Last updated: 08-09-2026_

# Forensic claim pins — coverage, expected-vs-actual, unpinned residue (H4352)

Executor: Claude Code Fable 5.1 (`claude-fable-5-1`), 08-09-2026. Handoff: Uprava
[H4352](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4352-Fable_csl-atlas_forensic-claim-arithmetic-null-pins_08.09.26.md)
(rank 3 of [TEST_GAP_CENSUS_ORGWIDE_08-09-2026.md](https://github.com/gasyoun/Uprava/blob/main/reports/TEST_GAP_CENSUS_ORGWIDE_08-09-2026.md)).

## What this suite is for

The 24 scripts under [scripts/forensic/](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic)
produce publishable claims about which lexicographer copied whom. The failure
mode is not a red build but a wrong number about a named scholar found by a
reader — this repo has already retracted an independent-witnesses claim and
corrected a pool count from 642 to 641. These tests pin the ARITHMETIC of the
nine highest-claim scripts against miniature fixtures whose expected counts were
worked out by hand and written into each test module's docstring.

## How to run

```bash
npm run test-forensic-pins
```

Equivalent: `python -m pytest tests/forensic -q -p no:cacheprovider`. CI job
`forensic-pins` in [test.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/test.yml)
(Python 3.11, `pytest` + `scipy`; the suite needs only the stdlib otherwise).

## Discipline (locked before the first test was written)

1. **Expected values are hand-derived**, never produced by running the script
   under test. Each module's docstring shows the derivation.
2. **Fixtures are written by the test**, in real csl-orig shapes (`<L>…<LEND>`
   records, `<ls>`/`<ls n="…">` citations, `{%…%}` German spans, `{#…#}` /
   `<s>` Sanskrit tokens, `<div>` sense markers, the `L k1 k2 h e n_cit cites`
   parsed-cache columns, pwgissues change files, ahlborn lines, key1 exports).
3. **Every script gets a null fixture** where the correct answer is zero shared
   items, and the pin asserts exactly zero — never merely `> 0`.
4. **Off-by-one guards** on every population count a script prints (lemma
   totals, shared-headword counts, pair-row counts, CSV row counts, contingency
   cells, margins).
5. **Offline, proven**: an autouse fixture in
   [conftest.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/conftest.py)
   replaces `socket.socket` for every test;
   [test_offline_guard.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_offline_guard.py)
   proves the guard is live. No test reads `../csl-orig`, `../CORRECTIONS`,
   `../csl-corrections`, `../PWG` or `SanskritLexicography/` — every path
   constant is repointed at a `tmp_path` corpus.
6. **main()-only scripts** get a dry-run-surface pin: main() runs in a tmp cwd
   against the fixture and its `f*_report.json` / CSV outputs are read back.
   Each such limitation (a lowered threshold constant, a hard-coded floor) is
   named in the module docstring and in the table below.

## Per-script coverage

| Script | Pure-function pins | main() surface pin | Null fixture | Limitations documented |
|---|---|---|---|---|
| `parse_cslorig` (foundation) | `iter_entries`, `clean_citation`, `build_cache`, `load_entries` | — | unterminated entry, empty file | — |
| `f0_shared_headword_typos` | `within_ed1`, `deletes1`, `load_snapshot` | `f0_report.json` + 2 CSVs | rare lemmas ≥2 edits from every real lemma → 0 anomalies | snapshot resolved at import (`$SANHW1` placeholder); `MIN_PAIR_SIZE` 5000→1 |
| `f4_shared_corrections` | `norm_hw`, `norm_cit`, `dict_of`, `side`, `parse_change_file`, `parse_correctionform`, `parse_printchange`, `collect` | `f4_report.json` + CSV | disjoint headwords and citations on the two sides → 0 | — |
| `f4b_ahlborn_nulltest` | `parse_ahlborn`, `corrected_headwords` | `f4b_report.json` (hypergeometric null) | MW correct every time; corrections disjoint → 0 observed | main() needs scipy (see quirks) |
| `f9_shared_omission` | `contingency` | `shared_omission_test.csv` + sidecar | probe fills every PWG gap → 0 shared omissions | stdout wrapper at import handled by the fixture |
| `f1_citations` | `norm_ref`, `source_of`, `build` | `f1_report.json` + 2 CSVs | shared lemmas, disjoint apparatus → 0 exact, 0 guns | `MIN_CIT` 500→1; a `pw` cache must exist (see quirks) |
| `f10_sense_order` | `toks_en`, `toks_skt`, `strip_markup_en`, `group_by_k1`, `senses_mw/pwg/ap`, `jaccard`, `greedy_match`, `concordant_fraction`, `score_headword`, `score_floor`, `null_concordance` | `--census` branch via captured stdout | PWG with 2 senses → 0 candidates | full main() needs argos MT — not run |
| `f3_gloss` | `corr`, `gloss_len_map` | `f3_report.json` + CSV | no shared lemmas → 0 shared, 0.0 correlations | — |
| `f2_structure` | `hcount_map` | `f2_report.json` + 2 CSVs | MW never splits what PWG splits → 0 agreement, empty pool | `MIN_HOM` 1000→1; the `len(split) < 20` floor is hard-coded in main(), so the fixture carries 24 split headwords |
| `f5_entry_comparison` | `sigil`, `dedup`, `concordant_fraction`, `spearman`, `build` | `f5_report.json` + 2 CSVs | shared headwords citing disjoint sources → no order verdict anywhere | Petersburg-mean truthiness quirk pinned as observed |

## Expected vs actual — runner output, 08-09-2026, offline

`python -m pytest tests/forensic -q -p no:cacheprovider` → **48 passed in 0.76s**
(Python 3.13.15, pytest 9.1.1, scipy 1.18.1; socket guard live). The table is
the suite's own terminal summary; the `expected` column is the hand-derived
value written in the test, `actual` is what the script returned.

| script | metric | expected | actual | ok |
|---|---|---|---|---|
| f0 | load_snapshot.lemmas | 1 | 1 | yes |
| f0 | load_snapshot.agni_dicts | {'PWG', 'MW'} | {'PWG', 'MW'} | yes |
| f0 | load_snapshot.agni_df | 2 | 2 | yes |
| f0 | n_lemmas | 8 | 8 | yes |
| f0 | n_real | 3 | 3 | yes |
| f0 | n_rare | 4 | 4 | yes |
| f0 | n_candidate_anomalies | 3 | 3 | yes |
| f0 | anomalies.csv_rows | 3 | 3 | yes |
| f0 | pairs.csv_rows | 3 | 3 | yes |
| f0 | probe.PWG/MW | (3, 2, 2) | (3, 2, 2) | yes |
| f0 | probe.PW/MW | (1, 1, 0) | (1, 1, 0) | yes |
| f0 | probe.PWG/PW | (1, 1, 0) | (1, 1, 0) | yes |
| f0 | probe.BOP/MW | (0, 0, 0) | (0, 0, 0) | yes |
| f0 | top_doublet_pair | {'pair': 'MW/PWG', 'doublets': 2, 'shared': 3, 'per_1k': 600.0} | {'pair': 'MW/PWG', 'doublets': 2, 'shared': 3, 'per_1k': 600.0} | yes |
| f0 | mw_pwg_doublet_examples | ['agnl~agni', 'agn~agni'] | ['agnl~agni', 'agn~agni'] | yes |
| f0 | csv.MW/PWG.sizes | ('6', '5') | ('6', '5') | yes |
| f0 | csv.MW/PWG.both_in_L0 | 'True' | 'True' | yes |
| f0 | csv.MW/PW.both_in_L0 | 'False' | 'False' | yes |
| f0 | anomalies.last_row | ('agn', 'agni', '3') | ('agn', 'agni', '3') | yes |
| f0 | null.n_real | 2 | 2 | yes |
| f0 | null.n_rare | 2 | 2 | yes |
| f0 | null.n_candidate_anomalies | 0 | 0 | yes |
| f0 | null.anomalies.csv_rows | 0 | 0 | yes |
| f0 | null.pairs.csv_rows | 0 | 0 | yes |
| f0 | null.probe.PWG/MW.shared | 0 | 0 | yes |
| f0 | null.top_doublet_pairs | [] | [] | yes |
| f0 | null.mw_pwg_doublet_examples | [] | [] | yes |
| f10 | group_by_k1.mw | {'go': 2, 'deva': 1} | {'go': 2, 'deva': 1} | yes |
| f10 | senses_mw.go | 4 | 4 | yes |
| f10 | senses_mw.go.en | [{'cow', 'bull'}, {'ray', 'beam', 'light'}, {'ground', 'earth'}, {'language', 'words', 'speech'}] | [{'cow', 'bull'}, {'ray', 'beam', 'light'}, {'ground', 'earth'}, {'language', 'words', 'speech'}] | yes |
| f10 | senses_mw.deva | 1 | 1 | yes |
| f10 | senses_pwg.go | 3 | 3 | yes |
| f10 | senses_pwg.go.de | ['Rind, Kuh', 'Strahl', 'Erde'] | ['Rind, Kuh', 'Strahl', 'Erde'] | yes |
| f10 | senses_pwg.deva | 1 | 1 | yes |
| f10 | senses_ap.go | 4 | 4 | yes |
| f10 | senses_ap.go.en | [{'cow', 'bull'}, {'ray', 'beam'}, {'ground', 'earth'}, {'words', 'speech'}] | [{'cow', 'bull'}, {'ray', 'beam'}, {'ground', 'earth'}, {'words', 'speech'}] | yes |
| f10 | concordant.identity | 1.0 | 1.0 | yes |
| f10 | concordant.reversed | 0.0 | 0.0 | yes |
| f10 | concordant.one_swap | 0.6666666666666666 ± 6.7e-07 | 0.6666666666666666 | yes |
| f10 | concordant.too_few | None | None | yes |
| f10 | concordant.shared_index_only | None | None | yes |
| f10 | greedy_match | [(0, 0), (1, 1)] | [(0, 0), (1, 1)] | yes |
| f10 | greedy_match.empty | [] | [] | yes |
| f10 | score.concordance | 1.0 | 1.0 | yes |
| f10 | score.matches | 4 | 4 | yes |
| f10 | score.n_other | 4 | 4 | yes |
| f10 | score.mean_sim | 0.8333333333333333 ± 8.3e-07 | 0.8333333333333333 | yes |
| f10 | score.reversed.concordance | 0.0 | 0.0 | yes |
| f10 | score.reversed.matches | 4 | 4 | yes |
| f10 | score.too_few | None | None | yes |
| f10 | score_floor.0.7_drops_two | None | None | yes |
| f10 | score_floor.0.5_keeps_all | 1.0 | 1.0 | yes |
| f10 | null_concordance.reversed | 0.0 | 0.0 | yes |
| f10 | null_concordance.identity | 1.0 | 1.0 | yes |
| f10 | null_concordance.too_few | None | None | yes |
| f10 | census.k1_counts | True | True | yes |
| f10 | census.MW_vs_PWG | True | True | yes |
| f10 | census.MW_vs_AP | True | True | yes |
| f10 | census.pwg_glosses_to_translate | True | True | yes |
| f10 | census.null.MW_vs_PWG | True | True | yes |
| f10 | census.null.MW_vs_AP | True | True | yes |
| f1 | build.pwg.cited_lemmas | 3 | 3 | yes |
| f1 | build.pwg.agni.full | {'P. 1,1,14', 'MBH. 3,45'} | {'P. 1,1,14', 'MBH. 3,45'} | yes |
| f1 | build.pwg.agni.src | {'P', 'MBH'} | {'P', 'MBH'} | yes |
| f1 | build.mw.agni.full | {'P', 'MBH. 3,45'} | {'P', 'MBH. 3,45'} | yes |
| f1 | citation_dicts | ['AP', 'MW', 'PW', 'PWG'] | ['AP', 'MW', 'PW', 'PWG'] | yes |
| f1 | n_pairs | 4 | 4 | yes |
| f1 | csv.pairs_rows | 4 | 4 | yes |
| f1 | MW/PWG.shared_cited_lemmas | '2' | '2' | yes |
| f1 | MW/PWG.mean_source_jaccard | '0.5' | '0.5' | yes |
| f1 | MW/PWG.shared_exact_refs | '1' | '1' | yes |
| f1 | MW/PWG.truncation(a=MW trunc b, b trunc a) | ('1', '0') | ('1', '0') | yes |
| f1 | MW/PWG.comparable_sources | '2' | '2' | yes |
| f1 | MW/PW.row | ('1', '1.0', '1', '0', '0', '1') | ('1', '1.0', '1', '0', '0', '1') | yes |
| f1 | AP/MW.row | ('1', '0.5', '1', '0', '0', '1') | ('1', '0.5', '1', '0', '0', '1') | yes |
| f1 | csv.first_row_is_top_jaccard | ('MW', 'PW') | ('MW', 'PW') | yes |
| f1 | n_smoking_guns | 2 | 2 | yes |
| f1 | guns | [('agni', 'MBH. 3,45', 'PWG', 'MW', '1'), ('soma', 'R. 5,5', 'PW', 'MW', '1')] | [('agni', 'MBH. 3,45', 'PWG', 'MW', '1'), ('soma', 'R. 5,5', 'PW', 'MW', '1')] | yes |
| f1 | smoking_gun_sources | {'MBH': 1, 'R': 1} | {'MBH': 1, 'R': 1} | yes |
| f1 | lineage.PWG/MW.exact | 1 | 1 | yes |
| f1 | lineage.keys | ['PWG/MW', 'PW/MW'] | ['PWG/MW', 'PW/MW'] | yes |
| f1 | nulls.keys | ['AP/MW'] | ['AP/MW'] | yes |
| f1 | top_pairs(>=500 shared) | [] | [] | yes |
| f1 | null.n_pairs | 1 | 1 | yes |
| f1 | null.pair | ('MW', 'PWG') | ('MW', 'PWG') | yes |
| f1 | null.shared_cited_lemmas | '1' | '1' | yes |
| f1 | null.mean_source_jaccard | '0.0' | '0.0' | yes |
| f1 | null.shared_exact_refs | '0' | '0' | yes |
| f1 | null.comparable_sources | '0' | '0' | yes |
| f1 | null.n_smoking_guns | 0 | 0 | yes |
| f1 | null.csv.guns_rows | 0 | 0 | yes |
| f1 | null.smoking_gun_sources | {} | {} | yes |
| f2 | hcount_map | {'a': 3, 'b': 1, 'c': 2} | {'c': 2, 'a': 3, 'b': 1} | yes |
| f2 | homonym_dicts | ['MW', 'PWG'] | ['MW', 'PWG'] | yes |
| f2 | n_pairs | 1 | 1 | yes |
| f2 | pair | ('MW', 'PWG') | ('MW', 'PWG') | yes |
| f2 | shared_headwords | '27' | '27' | yes |
| f2 | split_in_either | '24' | '24' | yes |
| f2 | agree_on_count | '21' | '21' | yes |
| f2 | agreement_rate | '0.875' | '0.875' | yes |
| f2 | deep_split_both_3plus | '2' | '2' | yes |
| f2 | deep_agree | '1' | '1' | yes |
| f2 | deep_agreement_rate | '0.5' | '0.5' | yes |
| f2 | raw_pool | (2, 1, 1) | (2, 1, 1) | yes |
| f2 | raw_pool.csv | [('zz2', 'PW'), ('zz1', 'PWG')] | [('zz2', 'PW'), ('zz1', 'PWG')] | yes |
| f2 | lineage.PWG/MW.agree | 21 | 21 | yes |
| f2 | nulls | {} | {} | yes |
| f2 | null.shared_headwords | '20' | '20' | yes |
| f2 | null.split_in_either | '20' | '20' | yes |
| f2 | null.agree_on_count | '0' | '0' | yes |
| f2 | null.agreement_rate | '0.0' | '0.0' | yes |
| f2 | null.deep | ('0', '0', '0.0') | ('0', '0', '0.0') | yes |
| f2 | null.raw_pool_total | 0 | 0 | yes |
| f2 | null.raw_pool.csv_rows | 0 | 0 | yes |
| f3 | corr.proportional | (1.0, 1.0) | (1.0, 1.0) | yes |
| f3 | corr.reversed | (-1.0, -1.0) | (-1.0, -1.0) | yes |
| f3 | corr.too_few | (0.0, 0.0) | (0.0, 0.0) | yes |
| f3 | corr.constant | (0.0, 0.0) | (0.0, 0.0) | yes |
| f3 | corr.tied_ranks | (0.866025 ± 1.0e-06, 0.866025 ± 1.0e-06) | (0.8660254037844387, 0.8660254037844387) | yes |
| f3 | gloss_len.de.agni | 14 | 14 | yes |
| f3 | gloss_len.de.deva | 0 | 0 | yes |
| f3 | gloss_len.en.agni | 18 | 18 | yes |
| f3 | rows | 4 | 4 | yes |
| f3 | PWG.shared_glossed_lemmas | '3' | '3' | yes |
| f3 | PWG.corr | ('1.0', '1.0') | ('1.0', '1.0') | yes |
| f3 | PW.shared_glossed_lemmas | '2' | '2' | yes |
| f3 | PW.corr(<3 -> 0) | ('0.0', '0.0') | ('0.0', '0.0') | yes |
| f3 | AP.corr | ('-1.0', '-1.0') | ('-1.0', '-1.0') | yes |
| f3 | BEN.corr(constant) | ('0.0', '0.0') | ('0.0', '0.0') | yes |
| f3 | differential_pwg_minus_ap_spearman | 2.0 | 2.0 | yes |
| f3 | report.pairs.source_lang | ['de', 'de', 'en', 'de'] | ['de', 'de', 'en', 'de'] | yes |
| f3 | null.shared | ['0', '0', '0', '0'] | ['0', '0', '0', '0'] | yes |
| f3 | null.PWG.corr | ('0.0', '0.0') | ('0.0', '0.0') | yes |
| f3 | null.differential | 0.0 | 0.0 | yes |
| f4 | parse_change_file.records | 3 | 3 | yes |
| f4 | parse_change_file.first | ('agni', '10', 'fire', 'flame') | ('agni', '10', 'fire', 'flame') | yes |
| f4 | parse_change_file.ins | ('deva', '20', '', 'added line') | ('deva', '20', '', 'added line') | yes |
| f4 | parse_change_file.del | ('deva', '21', '', 'gone') | ('deva', '21', '', 'gone') | yes |
| f4 | parse_correctionform | [('deva', 'alt', 'neu'), ('vala', '', 'only')] | [('deva', 'alt', 'neu'), ('vala', '', 'only')] | yes |
| f4 | parse_printchange.tabular | [('agni', 'agnl', 'agni')] | [('agni', 'agnl', 'agni')] | yes |
| f4 | parse_printchange.prose | [('agni', '', ''), ('vala', '', '')] | [('agni', '', ''), ('vala', '', '')] | yes |
| f4 | collect.hw | ({'agni'}, {'agni'}) | ({'agni'}, {'agni'}) | yes |
| f4 | collect.cit | ({'MBH. 1,2'}, {'MBH. 1,2', 'R. 3'}) | ({'MBH. 1,2'}, {'MBH. 1,2', 'R. 3'}) | yes |
| f4 | source1_cross_issues | 2 | 2 | yes |
| f4 | issue_breakdown | [('issue001fix', 1, 1), ('issue003fix', 0, 1)] | [('issue001fix', 1, 1), ('issue003fix', 0, 1)] | yes |
| f4 | shared_headwords_issue | ['agni', 'deva'] | ['agni', 'deva'] | yes |
| f4 | shared_citations_issue | ['MBH. 1,2', 'R. 3,4'] | ['MBH. 1,2', 'R. 3,4'] | yes |
| f4 | source2_pet_corrected_hw | 3 | 3 | yes |
| f4 | source2_mw_corrected_hw | 3 | 3 | yes |
| f4 | shared_headwords_corpus | 3 | 3 | yes |
| f4 | shared_citations_corpus | 0 | 0 | yes |
| f4 | print_errors | (1, 2) | (1, 2) | yes |
| f4 | shared_print_error_headwords | ['agni'] | ['agni'] | yes |
| f4 | n_shared_correction_rows | 3 | 3 | yes |
| f4 | csv.rows | 3 | 3 | yes |
| f4 | csv.in_pwgissues | [('agni', 'True'), ('deva', 'True'), ('vala', 'False')] | [('agni', 'True'), ('deva', 'True'), ('vala', 'False')] | yes |
| f4 | csv.agni.pet_dict | 'pwg' | 'pwg' | yes |
| f4 | null.source1_cross_issues | 1 | 1 | yes |
| f4 | null.issue_breakdown | [('issue001fix', 0, 0)] | [('issue001fix', 0, 0)] | yes |
| f4 | null.shared_headwords_issue | [] | [] | yes |
| f4 | null.shared_citations_issue | [] | [] | yes |
| f4 | null.shared_headwords_corpus | 0 | 0 | yes |
| f4 | null.shared_citations_corpus | 0 | 0 | yes |
| f4 | null.print_errors | (1, 1) | (1, 1) | yes |
| f4 | null.shared_print_error_headwords | [] | [] | yes |
| f4 | null.n_shared_correction_rows | 0 | 0 | yes |
| f4 | null.csv.rows | 0 | 0 | yes |
| f4b | ahlborn.rows | 8 | 8 | yes |
| f4b | ahlborn.statuses | ['mw_correct', 'shares_error', 'mw_absent_recorded', 'mw_other', 'mw_correct', 'shares_error', 'mw_absent', 'mw_correct'] | ['mw_correct', 'shares_error', 'mw_absent_recorded', 'mw_other', 'mw_correct', 'shares_error', 'mw_absent', 'mw_correct'] | yes |
| f4b | ahlborn.shares_error | 2 | 2 | yes |
| f4b | ahlborn.err_type.first | 'typo' | 'typo' | yes |
| f4b | ahlborn.err_type.lookup_form | '?' | '?' | yes |
| f4b | ahlborn.mw_recorded.empty | '' | '' | yes |
| f4b | ahlborn.mw_has_error.tuv | True | True | yes |
| f4b | corrected_headwords.PET | {'a', 'x', 'b'} | {'a', 'x', 'b'} | yes |
| f4b | corrected_headwords.mw_none | set() | set() | yes |
| f4b | main.ahlborn_total | 4 | 4 | yes |
| f4b | main.ahlborn_status | {'mw_correct': 2, 'shares_error': 1, 'mw_absent': 1} | {'mw_correct': 2, 'shares_error': 1, 'mw_absent': 1} | yes |
| f4b | main.ahlborn_shares_error_pct | 25.0 | 25.0 | yes |
| f4b | main.null_U | 4 | 4 | yes |
| f4b | main.null_pet_corrected | 2 | 2 | yes |
| f4b | main.null_mw_corrected | 2 | 2 | yes |
| f4b | main.null_observed | 1 | 1 | yes |
| f4b | main.null_expected | 1.0 | 1.0 | yes |
| f4b | main.null_lift | 1.0 | 1.0 | yes |
| f4b | main.null_p | 0.8333333333333334 ± 1.0e-09 | 0.8333333333333334 | yes |
| f4b | main.null_verdict | 'AT chance — independent errors' | 'AT chance — independent errors' | yes |
| f4b | main.shared_corrected_examples | ['a'] | ['a'] | yes |
| f4b | null.ahlborn_total | 3 | 3 | yes |
| f4b | null.ahlborn_shares_error | 0 | 0 | yes |
| f4b | null.ahlborn_shares_error_pct | 0.0 | 0.0 | yes |
| f4b | null.null_observed | 0 | 0 | yes |
| f4b | null.null_expected | 1.0 | 1.0 | yes |
| f4b | null.null_lift | 0.0 | 0.0 | yes |
| f4b | null.null_p | 1.0 | 1.0 | yes |
| f4b | null.shared_corrected_examples | [] | [] | yes |
| f5 | concordant.identity | 1.0 | 1.0 | yes |
| f5 | concordant.reversed | 0.0 | 0.0 | yes |
| f5 | concordant.one_swap_of_4 | 0.8333333333333334 ± 8.3e-07 | 0.8333333333333334 | yes |
| f5 | concordant.two_shared_only | None | None | yes |
| f5 | concordant.repeats_deduped | 1.0 | 1.0 | yes |
| f5 | spearman.too_few | 0.0 | 0.0 | yes |
| f5 | spearman.monotone | 1.0 | 1.0 | yes |
| f5 | spearman.reversed | -1.0 | -1.0 | yes |
| f5 | build.mw.headwords | 3 | 3 | yes |
| f5 | build.mw.agni.cites | ['MBH', 'R', 'AV', 'P'] | ['MBH', 'R', 'AV', 'P'] | yes |
| f5 | build.mw.agni.ncit | 4 | 4 | yes |
| f5 | build.mw.agni.sktoks | {'indra', 'deva'} | {'indra', 'deva'} | yes |
| f5 | build.mw.agni.nsense(2 records, no {%) | 2 | 2 | yes |
| f5 | build.mw.deva | ([], 0, set(), 1) | ([], 0, set(), 1) | yes |
| f5 | build.pwg.agni.sktoks | {'agni', 'agnI', 'deva'} | {'agni', 'agnI', 'deva'} | yes |
| f5 | build.pwg.agni.nsense(1 {%) | 1 | 1 | yes |
| f5 | rows | 6 | 6 | yes |
| f5 | row_order | ['PWG', 'PW', 'PWKVN', 'SCH', 'AP', 'BEN'] | ['PWG', 'PW', 'PWKVN', 'SCH', 'AP', 'BEN'] | yes |
| f5 | PWG.shared_headwords | '2' | '2' | yes |
| f5 | PWG.entries_with_order_signal | '1' | '1' | yes |
| f5 | PWG.order | ('1.0', '100.0') | ('1.0', '100.0') | yes |
| f5 | PWG.content_jaccard | '0.25' | '0.25' | yes |
| f5 | PWG.apparatus_spearman(n<5) | '0.0' | '0.0' | yes |
| f5 | PW.order | ('0.0', '0.0') | ('0.0', '0.0') | yes |
| f5 | PW.content_jaccard | '0.5' | '0.5' | yes |
| f5 | PWKVN.no_order_verdict | ('0', '', '') | ('0', '', '') | yes |
| f5 | SCH.shared_headwords | '0' | '0' | yes |
| f5 | AP.order | '0.8333' | '0.8333' | yes |
| f5 | AP.is_null | 'True' | 'True' | yes |
| f5 | null_mean_order | 0.8333 | 0.8333 | yes |
| f5 | n_order_examples_identical | 1 | 1 | yes |
| f5 | examples | [('PWG', 'agni', 'MBH R AV P')] | [('PWG', 'agni', 'MBH R AV P')] | yes |
| f5 | petersburg_mean_order(QUIRK: 0.0 dropped) | 1.0 | 1.0 | yes |
| f5 | null.shared_headwords | ['1', '1', '1', '1', '1', '1'] | ['1', '1', '1', '1', '1', '1'] | yes |
| f5 | null.entries_with_order_signal | ['0', '0', '0', '0', '0', '0'] | ['0', '0', '0', '0', '0', '0'] | yes |
| f5 | null.mean_order_all_empty | ['', '', '', '', '', ''] | ['', '', '', '', '', ''] | yes |
| f5 | null.content_all_empty | ['', '', '', '', '', ''] | ['', '', '', '', '', ''] | yes |
| f5 | null.petersburg_mean_order | 0 | 0 | yes |
| f5 | null.null_mean_order | 0 | 0 | yes |
| f5 | null.n_order_examples_identical | 0 | 0 | yes |
| f5 | null.examples_rows | 0 | 0 | yes |
| f9 | anchor | 6 | 6 | yes |
| f9 | MW.cells | (3, 1, 1, 1) | (3, 1, 1, 1) | yes |
| f9 | MW.margins | (4, 2) | (4, 2) | yes |
| f9 | MW.rates | (0.25, 0.5) | (0.25, 0.5) | yes |
| f9 | MW.gap_sensitivity | 2.0 | 2.0 | yes |
| f9 | AP.cells | (1, 3, 2, 0) | (1, 3, 2, 0) | yes |
| f9 | AP.rates | (0.75, 0.0) | (0.75, 0.0) | yes |
| f9 | AP.gap_sensitivity | 0.0 | 0.0 | yes |
| f9 | edge.ratio_undefined | None | None | yes |
| f9 | edge.shared_omission | 2 | 2 | yes |
| f9 | edge.ratio_one | 1.0 | 1.0 | yes |
| f9 | edge.empty_anchor | (0, 0, None) | (0, 0, None) | yes |
| f9 | main.rows | 2 | 2 | yes |
| f9 | main.anchor_n | 6 | 6 | yes |
| f9 | main.MW.cells | ('3', '1', '1', '1') | ('3', '1', '1', '1') | yes |
| f9 | main.MW.gap_sensitivity | '2.0' | '2.0' | yes |
| f9 | main.AP.cells | ('1', '3', '2', '0') | ('1', '3', '2', '0') | yes |
| f9 | main.AP.gap_sensitivity | '0.0' | '0.0' | yes |
| f9 | main.sidecar.MW.gap_sensitivity | 2.0 | 2.0 | yes |
| f9 | null.MW.shared_omission | '0' | '0' | yes |
| f9 | null.MW.gap_sensitivity | '0.0' | '0.0' | yes |
| f9 | null.AP.shared_omission | '0' | '0' | yes |
| f9 | null.AP.rates | ('1.0', '0.0') | ('1.0', '0.0') | yes |
| f9 | null.sidecar.MW.lacks_lacks | 0 | 0 | yes |
| parse_cslorig | entries | 3 | 3 | yes |
| parse_cslorig | a.L | '1' | '1' | yes |
| parse_cslorig | a.h | '1' | '1' | yes |
| parse_cslorig | a.citations | ['P. 1,1,14', 'RV. vii, 96, 3'] | ['P. 1,1,14', 'RV. vii, 96, 3'] | yes |
| parse_cslorig | agni.h | None | None | yes |
| parse_cslorig | agni.citations | ['MBh. 1, 2', '>Dhātup. iii, 4'] | ['MBh. 1, 2', '>Dhātup. iii, 4'] | yes |
| parse_cslorig | soma.citations | [] | [] | yes |
| parse_cslorig | total_ls | 4 | 4 | yes |
| parse_cslorig | null.unterminated | 0 | 0 | yes |
| parse_cslorig | null.empty_file | 0 | 0 | yes |
| parse_cslorig | cache.entries | 3 | 3 | yes |
| parse_cslorig | cache.citations | 4 | 4 | yes |
| parse_cslorig | cache.with_homonym | 1 | 1 | yes |
| parse_cslorig | roundtrip.rows | 3 | 3 | yes |
| parse_cslorig | roundtrip.agni.n_cit | '2' | '2' | yes |
| parse_cslorig | roundtrip.agni.citations | ['MBh. 1, 2', '>Dhātup. iii, 4'] | ['MBh. 1, 2', '>Dhātup. iii, 4'] | yes |
| parse_cslorig | roundtrip.soma.citations | [] | [] | yes |

## Script quirks surfaced by the pins (recorded, not patched)

The handoff scope is pins, not script changes; each item below is a candidate
follow-up in its own PR so the published numbers do not move unreviewed.

1. **f4b crashes without scipy.** `main()` formats `p={pval:.3g}` inside its
   `finding` string; when scipy is absent `pval` is `None` and the format raises
   `TypeError` after the console report but before `f4b_report.json` is written.
   The two main()-surface tests `importorskip("scipy")`; CI installs scipy so
   they run there.
2. **f5 drops a 0.0 Petersburg row from its mean.** `pet_ord` keeps only truthy
   per-dict means, so a Petersburg dict whose citation-order agreement is exactly
   0.0 falls out of `petersburg_mean_order`. With PWG = 1.0 and PW = 0.0 scored the
   hand mean is 0.5; the script reports 1.0. Pinned as observed in
   `test_petersburg_mean_drops_zero_rows_QUIRK` with instructions to update the
   pin (not revert) when the fix lands. On the live corpus every Petersburg row is
   far from 0.0, so the published 0.811 is unaffected — but the estimator is wrong
   in the limit the null tests exist to guard.
3. **f1 hard-codes `smoking("PW","MW")`.** If the parsed cache lacks `pw.tsv`
   (or PW falls under `MIN_CIT`) main() raises `KeyError` after writing the pair
   CSV. Every fixture therefore carries a `pw` cache.
4. **f9 rebinds `sys.stdout`/`sys.stderr` at import** to fresh UTF-8 wrappers over
   the current `.buffer`; under pytest that wraps the capture tmpfile and closes it
   on garbage collection, poisoning every later test in the session. The module
   fixture imports f9 behind throwaway streams. The other eight scripts use
   `sys.stdout.reconfigure(...)`, which is safe.

## The 14 forensic scripts left unpinned, and why

24 files under `scripts/forensic/`. Nine are pinned by the handoff list, plus
`parse_cslorig` (pinned here as the foundation every parsed-cache fixture
depends on) — so 14 remain, not 15:

| Script | Why unpinned | Owner of the seam |
|---|---|---|
| `_setup_argos.py` | one-time installer: `pip` + argos model download via `subprocess`; nothing to pin offline | — |
| `_f10_pretranslate.py` | process-pool driver around argos MT for f10's cache; no arithmetic of its own | pin with f10's full main() once an argos-free stub exists |
| `f6_gloss_translation.py` | DE→EN gloss test; every score depends on argos MT output (offline model, but a 2 GB dependency the CI runner does not carry) | mock-translator seam: inject a `translate` callable, then pin the resemblance arithmetic |
| `f7_harivamsa_harvest.py` | web harvest of the Kinjawadekar vulgate e-text (`urllib`); network by design | — (rights-gated source) |
| `f7_harivamsa_resolve.py` | resolves citations against the harvested `_harivamsa_verses.jsonl` (gitignored, rights-gated); the fitted-index calibration is pinnable once a 30-verse fixture is hand-built | next test-gap wave: hand-build the fixture, pin anchor extraction + index fit |
| `f8_mbh_census.py` | MBH citation-form census over the full PWG/MW parse plus Böhtlingk correction notes; large stdlib script, pinnable with a mini corpus — deferred for time | next wave |
| `f8_mbh_harvest.py` | web harvest of the Nīlakaṇṭha vulgate from sanatana.in; network by design | — (rights-gated source) |
| `f8_mbh_witnesses.py` | stages two rights-gated e-text witnesses locally (`subprocess`, downloads); network by design | — |
| `f8_mbh_resolve.py` | per-parvan fitted index against the harvested vulgate (gitignored input); same seam as f7 resolve | next wave, after the f7 fixture pattern |
| `f8_mbh_drona_fitted_index.py` | book-7 census against the same gitignored vulgate | next wave |
| `f8_mbh_verify.py` | verifies correction notes against BORI reading evidence (`_mbh_bori_folded.jsonl`, rights-gated, gitignored) | next wave |
| `f8_mbh_presence.py` | four-state presence verdict over the two rights-gated e-texts (`urllib` for the critical-edition lookups) | next wave, with the witness fixtures |
| `f8_mbh_quote_lane.py` | text-side resolution of PWG's quoted pratīkas against the vulgate; input gitignored | next wave |
| `f8_mbh_specimen.py` | single-specimen answer script (MBH. 12,8081); reads the presence lane's outputs; nothing population-level to pin | — |

Reading of the residue: five scripts are network or installer scripts by
design and stay unpinned on purpose; eight depend on rights-gated, gitignored
e-text harvests and need a hand-built 20–30-verse fixture each — the f7/f8
resolve family shares one method, so one fixture pattern unlocks all of them;
one (f6) needs a translator seam. None of the 14 carries the copy-lineage
headline numbers (F1 0.16–0.19 Jaccard, F5 0.811, F2 64–77 %, F9 ~8×, F4b ~0 %)
— those all sit in the nine pinned here.

_Dr. Mārcis Gasūns_
