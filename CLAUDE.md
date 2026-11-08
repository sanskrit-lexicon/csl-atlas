# CLAUDE.md

_Created: 03-07-2026 · Last updated: 05-11-2026 (H7746 orientation backfill: PWG-DCS / NWS / triangulation registration, changelog-queue shape gate, CI paragraph truth-pass)_

Recent state (09-10-2026): `v0.19.11` released; vendored
`sanskrit-util` re-pinned to **v0.12.0** (#542 — H3975 medial-anusvāra
`form_key` fold); `ci: paper-priv-guard` blocks manuscript-shape files
outside the allowlist and the P1–P6 manuscripts were removed
(STANDING_POLICY_PAPER_WORK_PRIVATE_REPOS_ONLY, MG 06-10); nightly
bughunt findings reports are committed (latest #541); the mechanical lint
sweep took UP031/ISC004/I001 to 0 in scope (#534); the atlas concept DOI
`10.5281/zenodo.21419691` is pinned in `CITATION.cff`, the README citation
block, and A50 data-availability (#528).

`csl-atlas` is the public **dictionary-evidence** microsite for the Cologne
Digital Sanskrit Dictionaries — a static Observable Framework site for
reader-facing chapters, cross-dictionary comparisons, genealogy views, and
review queues over nine narrative dictionaries (MW, PWG, PWK, AP, WIL, SKD,
VCP, ARMH, ABCH) plus an all-dictionary coverage layer. No backend, no
database, no runtime LLM, no full-text search engine. Companion to the MW
microanalysis papers in [`sanskrit-lexicon/MWS`](https://github.com/sanskrit-lexicon/MWS).

Org conventions live in [`../CLAUDE.md`](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md).
Before encodings or corpus data, read the
[Sanskrit context primer](https://github.com/gasyoun/github-spine/blob/main/SANSKRIT_CONTEXT_PRIMER.md).

## How to run

```sh
npm run dev                       # Observable preview (predev runs sync-site-data)
npm run build                     # → dist/ (prebuild syncs data)
npm run deploy                    # Observable deploy (predeploy syncs)
npm test                          # node --test
npm run validate-review-reports   # required before any CI build
```

Data pipelines are one `npm run build-*` script per dataset (~70 in
[`package.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/package.json)),
each backed by `scripts/build-*.mjs` (or `.py`). Grep `package.json` `scripts`
for the name — do not guess. Pair `build-*` with `validate-*` when a validator
exists (`build-mw-depth` / `validate-mw-depth`, `build-dict-comparison` /
`validate-dict-comparison`).

The forensic data-stage pipelines are the deliberate exception: the H7463 /
H7476 / H7484 substrates under `data/pwg_dcs/`, `data/nws_layer/` and
`data/triangulation_stage3/` are bare `python3` scripts invoked directly (no
npm wrapper) — `scripts/pwg_dcs_join.py`, `scripts/nws_layer_extract.py` +
`scripts/nws_layer_join.py`, `scripts/triangulation_stage3_join.py` — each
with a `*_check.py` gate that exits non-zero on drift. Invoke them directly;
do not hunt for a `build-*` name that does not exist.

## Key paths

| Path | Purpose |
|---|---|
| [`src/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src) | Observable pages (`.md`), generated `src/data/*.json`, `src/lib/`, tool pages, dict chapters |
| [`scripts/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/scripts) | Build/import/validate; shared parsers in `scripts/lib/` |
| [`docs/ARCHITECTURE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md) · [`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md) | Scope — read first |
| [`data/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data) | Raw/intermediate inputs (not the generated `src/data/` copies) |
| `dist/` | Build output — generated, gitignored |

CI: `test.yml` (PR/push `main`) runs `npm ci` → `npm run verify` — the full
production acceptance gate (unit tests, validators, both regeneration passes,
the production dependency audit, `npm run build`, and the clean-tree assert
before and after), not a plain `npm test` → build. A second job runs the
offline forensic claim pins (`python -m pytest tests/forensic -q`), and two
negative-control jobs (H4613 generator-owned docs, H7096 PD regeneration
gate) hand-edit a generated file and prove the gate actually goes RED.
`build-and-deploy.yml` then publishes `dist/` to GitHub Pages.

## Conventions

- **Display Sanskrit in IAST, never raw SLP1** on any human-facing page. Convert
  with `slp1ToIast` from
  [`src/lib/lookup-normalize.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/lookup-normalize.js).
  Keep SLP1 only as a muted secondary / search key.
- **Every table or list gets a CSV download** via
  [`src/lib/csv-download.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/csv-download.js).
- **Source links must open the exact line.** GitHub will not render large
  `csl-orig` `.txt` files; use the [`/tools/source`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/source.md)
  viewer and render raw SLP1-inside-markup with
  [`sourceLineToIast` / `sourceTextToIast`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/source-iast.js).
- Scope is gated by `docs/BOUNDARY_RULES.md`: a page belongs here only if its
  primary object is a dictionary, edition, headword/entry, citation/siglum, or
  dictionary-to-dictionary comparison. TEI/OntoLex/FrAC/SHACL/RDF →
  `csl-standards`. DCS/corpus dashboards → `VisualDCS`. Org/CI metrics →
  `csl-observatory`.
- Generated `src/data/**` JSON from `sync-site-data` is gitignored — regenerate,
  do not hand-edit.
- **Citation-graph re-freeze chain (H5407).** `data/citations/ls_citation_*.tsv` are frozen
  at the revision pair in `ls_citation_graph.source.json`; regenerate them only with the
  siblings at that pair (or record the new pair). A change to the TSVs or to `CANON_ALIAS`
  regenerates, in the same PR: `build-citation-canon` + `validate-citation-canon`,
  `build-tradition-tags`, `scripts/forensic/f12_a50_claim_ledger.py` +
  `f12_a50_topology_arms.mjs` (~15 min) with the pins in
  `tests/forensic/test_f12_a50_claim_ledger.py`, `build-four-axis-independence`, and the
  tradition review-sheet count in `scripts/test_validate_review_decisions.py`; then the
  A50 figures and the claim ledger §P. CI red on any of these = a step skipped.
- **PD quotation-level unit (H6949).** `data/pd/pd_quotations_by_entry.tsv`,
  `pd_quotations_vs_pwg.tsv` and `pd_quotations_summary.json` are generated, not hand-kept:
  `python scripts/pd_quotation_units.py --pd <staged pd.txt>` then
  `python scripts/pd_quotations_vs_pwg.py --pd <pd.txt> --pwg ../csl-orig/v02/pwg/pwg.txt`.
  The rule lives in `scripts/lib/quotation_units.py` and **both** dictionaries import it —
  that identity is the whole reason the PD/PWG comparison is like-for-like, so a change to
  the rule regenerates both artifacts in the same PR. The counts in
  `reports/PD_QUOTATION_UNIT_2026-10-18.md` and the `data/pd/README.md` row must move with
  them. `tests/forensic/test_quotation_units.py` holds the rule with **hand-derived**
  expectations — never regenerate those pins from the script they check.
- **PD locus fields (H7458/C2).** `data/pd/pd_locus_fields.tsv`,
  `pd_locus_coverage_by_entry.tsv`, `pd_locus_rejections.tsv` and
  `pd_locus_fields_summary.json` are generated together by
  `python3.13 scripts/pd_locus_fields.py --pd <staged pd.txt>`. Reuse H6949's traversal and
  C1's continuation inheritance; never rewrite their frozen aggregates. Any parser change
  reruns `--check` plus `tests/forensic/test_pd_locus_fields.py` in the same PR, and every
  H6949 siglum/continuation marker must remain accounted for in the summary reconciliation.
  Method and current coverage: `reports/PD_LOCUS_FIELDS_C2_2026-10-29.md`.
- **PD AOB scan links (C3).** `data/pd/pd_aob_scan_targets.tsv`,
  `pd_aob_locus_scan_resolution.tsv` and `pd_aob_scan_links_summary.json` are rebuilt together
  by `python3.13 scripts/pd_aob_scan_links.py`; the committed page map and probe receipts make
  ordinary builds and `--check` offline. Only `--fetch-archive` refreshes Archive.org evidence.
  Keep work identity, AOB edition identity, Index scan URLs and locus-level page resolution
  separate. Emit a locus link only for a page-bearing AOB scheme and a unique printed-page
  label in an accepted main-pagination run or a multiply anchored visual range in
  `pd_aob_scan_ranges.tsv`; two-page scans carry two page numbers per leaf. Late resets,
  multipart resets and unanchored gaps stay unresolved.
  Method: `reports/PD_AOB_SCAN_LINKS_C3_2026-10-30.md`.
- **PD KoshaSHRI fixture (H7316).** `data/pd/pd_koshashri_entries.tsv` and
  `data/pd/pd_koshashri_citations.tsv` are generated together by
  `scripts/pd_koshashri_fixture_export.py` from the restricted local response through
  `scripts/pd_koshashri_vocable.py`. Changing the adapter, exporter or canonical input regenerates
  both TSVs and runs `python3 scripts/pd_koshashri_fixture_export.py --check` plus
  `python3.13 -m pytest tests/forensic/test_pd_koshashri_fixture_export.py -q` in the same PR.
  Never commit the full `data/pd/koshashri_vocable.json` response: KoshaSHRI is all rights reserved.
- **PWG↔DCS Stage 1 join (H7463).** Everything in `data/pwg_dcs/` regenerates by
  `python3 scripts/pwg_dcs_join.py` (register: `scripts/pwg_work_register.py`; catalogue:
  `scripts/dcs_catalogue_parse.py` over the sha-pinned snapshot). `python3 scripts/pwg_dcs_check.py`
  exits non-zero on drift; pins in `tests/forensic/test_pwg_dcs_join.py`. The denominators are
  pre-registered (quotation-linked 729,719 / raw 801,788 / α-frontier `k1 ≤ apacaya`) and strata
  are never pooled. Method: `reports/PWG_DCS_JOIN_STAGE1_2026-10-30.md`.
- **NWS layer (H7476).** `data/nws_layer/` rebuilds local-only via
  `python3 scripts/nws_layer_extract.py` + `python3 scripts/nws_layer_join.py` — the private
  lemma tar is NOT committed (H5939). `python3 scripts/nws_layer_check.py` gates drift; pins in
  `tests/forensic/test_nws_layer_join.py`. The attested fraction is recomputed only from the
  dated, hash-pinned scrape (`nws_works_registry.json`, fetched 2026-10-06); the retracted
  82.7 % figure is structurally barred. Method: `reports/NWS_LAYER_STAGE2_2026-10-30.md`.
- **PD/PWG/NWS Stage-3 triangulation (H7484).** `data/triangulation_stage3/` is rebuilt by
  `python3 scripts/triangulation_stage3_join.py` — deterministic and read-only over the
  committed Stage-1/Stage-2 substrates; it adds no new measurement. The interpretation grid
  (`grid_preregistration.md`, commit `b531f96`, sha-pinned) was committed before the run and
  is never retuned. `python3 scripts/triangulation_stage3_check.py` exits non-zero on drift;
  pins in `tests/forensic/test_triangulation_stage3.py`. Method:
  `reports/TRIANGULATION_STAGE3_2026-10-30.md`.
- **PD edition availability (C1).** `data/pd/pd_edition_availability_by_aob.tsv`,
  `pd_edition_availability_by_siglum.tsv`, `pd_edition_availability_evidence.tsv` and
  `pd_edition_availability_summary.json` regenerate by
  `python3 scripts/pd_edition_availability.py`; pins in
  `tests/forensic/test_pd_edition_availability.py`. Method:
  `reports/PD_EDITION_AVAILABILITY_C1_2026-10-29.md`.

## Do not touch

- `dist/`, `node_modules/`, `*.log` — generated/local.
- `src/data/dcs/**`, `src/data/lexico/sense_divergence.json`,
  `src/data/external/{langdetect-candidates,dharmamitra-langdetect}.json`,
  `data/forensic/_f6_tcache.json` — `npm run sync-site-data` outputs.
- TEI/OntoLex/SHACL/RDF work — `csl-standards`, not this repo.
- `csl-orig` — never commit or push dictionary source there.
- **Review-pool student guide** — [`docs/REVIEW_POOL_STUDENT_GUIDE.ru.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_STUDENT_GUIDE.ru.md)
  teaches a student to key the R2 / H4 / xref packets from the source line. Sync rule:
  a change to a label set (`R2_CHECKPOINT_LABEL_TAXONOMY*`, `H4_*LABEL*`,
  `XREF_SHARED_CORE_LABEL_TAXONOMY*`) or to a packet's row count updates the guide's
  matching table in the same PR (H5310).
- **Xref key normaliser twin** — [`scripts/lib/xref-normalize.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/xref-normalize.mjs)
  mirrors `normalize()` in `scripts/lexico/m6_xref_lineage.py` (strip `/ \ ^` accents,
  `°`, whitespace, edge hyphens). `xref_edges.csv` targets are RAW; the packet builder
  compares them through this normaliser. Sync rule: change one normaliser ⇒ change the
  other + `test/xref-normalize.test.mjs` in the same PR (H5408).
- **Generator-owned review docs** — every `docs/*.md` whose second line is
  `_Generated by \`node scripts/…\` — do not hand-edit…_` (R2 checkpoint/drift,
  H5 maker QA/correction, three-axis, H4 samples, xref source-check, both
  worksheets) and `test/fixtures/R2_DRIFT_EXPLANATION.machine-only.md`.
  `node --test` and `npm run verify` diff them byte-for-byte against their
  generator, so a hand edit (header, byline, link rewrite) turns CI red —
  change the generator, then `npm run regen-review-artifacts`
  (`npm run build-three-axis-comparison` for the three-axis packet).

Issues use the Cologne tooling taxonomy — see
[`/cologne-issue-runbook`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-issue-runbook.md).
Do not recopy type/severity/milestone tables into this file.

Danger facts:
[Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)
(org-private) and the generated block of
[AGENTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/AGENTS.md).

## Repo guards

The shared main tree is guarded: `.githooks/pre-commit` blocks main-tree commits
(escape `ALLOW_MAIN_TREE_COMMIT=1`, solo only) and `.githooks/post-checkout`
auto-reverts a foreign branch-switch back to `main` (shared-tree branch-switch guard,
03-10-2026, PR #532; escape `ALLOW_MAIN_TREE_CHECKOUT=1`). Work in a session-unique
worktree; `core.hooksPath=.githooks`.

The changelog-queue shape gate (H7467, PR #680) runs from the same hooks:
`.githooks/pre-commit` (staged fragments) and the pre-push gate validate every
staged `changelog_queue/*.md` fragment against the canonical Uprava parser
(`validate_entry` strict), consumed from the sibling `../Uprava` checkout or
`UPRAVA_TOOLS` — the parser is never copied into this repo. A malformed fragment
blocks commit and push; escape `ALLOW_CHANGELOG_QUEUE_SHAPE=1`. Where Uprava is
absent (public or cold clones, CI), or the sibling parser exists but fails to
import, the gate degrades to a loud WARNING-only fail-open instead of
tracebacking at the commit chokepoint.

_Dr. Mārcis Gasūns_
