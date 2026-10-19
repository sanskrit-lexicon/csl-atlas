# Dataset card — de/ru historical normalization benchmark (H7103)

_Created: 19-10-2026 · Schema 1.0.0_

## What this is

A frozen **200-token** gold set for historical orthographic normalization of the
dictionary meta-language: **100 German** pre-reform gloss tokens (PWG, PWK, CCS,
SCH) and **100 Russian** pre-1918 gloss tokens (Kossovich). Each gold row gives a
source file, line, short context, historical token and modern target.

Files:

- `data/ortho/normalization_benchmark.gold.tsv` — the gold rows
  (sha256 `9250066a44f8f8799db2b9ea9a7e55a46dcb338abcae661d1630d2e5c1ab9bf4`, 200 rows).
- `data/ortho/normalization_benchmark.json` — this card's machine-readable
  envelope: counts, splits, baselines, caveats, rights.
- `data/ortho/normalization_benchmark.card.md` — this file.
- `scripts/build-ortho-benchmark.mjs` — reproducible builder (needs the
  sibling csl-orig/SanskritSpellCheck/SamudraManthanam inputs; the committed
  files are the CI-safe artifact).
- `scripts/score-ortho-benchmark.mjs` — scorer (accuracy + CER, overall and
  by language/dictionary/split; `--predictions id<TAB>prediction`).

## Provenance and grounding

- German: `csl-orig/v02/{pwg,pw,ccs,sch}`, CC-BY-SA-4.0.
- Russian: `SamudraManthanam/web/corpus_builder/jsonl/kossovich.jsonl`.
- Targets: frozen `SanskritSpellCheck/ortho_drift/{de,ru}_reform_map.tsv`,
  consumed read-only; the maps are not redistributed.
- Grounding: **source-text-grounded, not scan-image verified.** Every token is
  an actual occurrence in the digitised transcription at the named line; no page
  image was re-opened. Do not describe this as a diplomatic scan edition.

## Splits

| split | rows |
|---|---:|
| train | 120 |
| dev | 40 |
| test | 40 |

Per German dictionary: 15 train / 5 dev / 5 test. Kossovich: 60 / 20 / 20.

## Baselines

| baseline | accuracy | CER | n |
|---|---:|---:|---:|
| rule-map rewrite baseline | 84.5% | 0.0193 | 200 |
| identity (no-op) baseline | 0.0% | 0.1457 | 200 |
| frozen reform-map lookup (ceiling) | 100.0% | 0.0000 | 200 |

The **rule-map** baseline applies generic reform rules (`th→t`, final
`iren→ieren`, `ß→ss`; Russian `ѣ→е`, `і→и`, `ѳ→ф`, `ѵ→и`, final `ъ` dropped).
The **identity** baseline is the no-op floor. The **map-oracle** row copies the
gold target and is a ceiling by construction, not a model.

## Metrics

Token accuracy = exact match after lowercasing/NFC. CER = character Levenshtein
distance on lowercased Unicode code points, summed over the set and divided by
the summed target length. Framing follows Bollmann (2019), NAACL, N19-1389;
this is a token-level adaptation, not the paper's sentence-level corpus CER.

## Rights

The benchmark is **CC-BY-SA-4.0** (csl-orig source excerpts are CC-BY-SA-4.0).
SanskritSpellCheck **declares no license**; the reform maps are used read-only to
derive modern targets and are not redistributed. Only 200 short token/target
pairs plus brief contexts are published. Kossovich excerpts are from the
SamudraManthanam corpus build; check that repository for its rights statement.

## Known limitations

- SOURCE-TEXT-GROUNDED, NOT SCAN-IMAGE VERIFIED: each row is grounded in a named csl-orig/SamudraManthanam source line, but no page image was re-opened. This is not a scan-level diplomatic edition.
- Targets are the frozen SanskritSpellCheck reform-map modern forms. The rule-map baseline is therefore an agreement-with-the-map lower bound, not an independent historical judgement; the map's provenance and limits are upstream.
- The reform maps are not redistributed: no map TSV is committed. Only the 200 sampled token/target pairs are published, with upstream attribution; SanskritSpellCheck declares no license.
- The German roster is the Petersburg line plus CCS and SCH as specified by the handoff (PWG, PWK, CCS, SCH). GRA and PWKVN are outside this benchmark.
- Russian is KOW (Kossovich, 1854) only: csl-orig v02 exposes no second Russian-gloss dictionary locally, so the Russian half is single-dictionary and single-date.
- The 'map oracle' row is a ceiling by construction (it copies the gold target) and exists only to bound the metric; the substantive baseline is the rule-map rewriter.
- CER uses lowercased Unicode code points and target-length normalization; it is a token-level CER, not Bollmann's sentence-level corpus CER.
- The Kossovich source is a corpus JSONL, not a csl-orig v02 file; its 'line' is the 1-based JSONL record index.

## Regeneration

```
DE_MAP=…/de_reform_map.tsv RU_MAP=…/ru_reform_map.tsv \
CSL_ORIG_ROOT=…/csl-orig/v02 KOSSOVICH_JSONL=…/kossovich.jsonl \
npm run build-ortho-benchmark
npm run score-ortho-benchmark
npm test
```
