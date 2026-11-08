_Created: 30-10-2026 · Last updated: 30-10-2026_

# data/nws_layer — the NWS-layer Stage 2 dataset (H7476)

Row-level substrate of [NWS_LAYER_STAGE2_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/NWS_LAYER_STAGE2_2026-10-30.md).
Every published number regenerates from these files under
[nws_layer_check.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/nws_layer_check.py)
(exit non-zero on drift); pins in
[test_nws_layer_join.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_nws_layer_join.py).

| File | Contents |
|---|---|
| `nws_headword_mass.tsv` | 34,101 rows: per-key1 senses/sigla/page-precise/literature refs + X(MW) tracer counts |
| `nws_works_attestation.tsv` | 174 rows: the declared-vs-exercised test (exact/fuzzy citations, attested flag) |
| `nws_works_registry.json` | the dated scrape (fetched 2026-10-06, html sha `86c9495e…`): works/provenance verbatim, licence envelope additive (H5303) |
| `pwg_headword_ql.tsv` | 123,366 rows: per-k1 PWG raw/quotation-linked mass (entry-family sums at join) |
| `nws_letter_envelope.tsv` | key-space envelope per letter (48 letters, full-alphabet digitization) |
| `nws_x_mw_census.tsv` | the X(MW) internal-source family (41 kinds) |
| `nws_layer_metrics.json` | every published number incl. H5/H6 verdicts |
| `nws_layer_pins.json` | tar/pwg/scrape sha pins + rights |

Denominators: prose entries 34,101 of the 167,990-key index (20.3 %);
page-precise refs 8,440; literature refs 8,937; attestation vs PW on 28,158
shared headwords; PW mass = quotation-linked tags (729,719), entry-family
grouped. The attested fraction is recomputed ONLY from the dated scrape with
its hash — never from filename stems (the retracted 82.7 % figure is barred
by the gate). Rights: MLU Halle-Wittenberg — texts with attribution
(Impressum probe 04-10-2026); the private lemma tar is NOT committed
(H5939); these rows are derived counts/keys. Rebuild (local-only):
`python3 scripts/nws_layer_extract.py`.

_Dr. Mārcis Gasūns_
