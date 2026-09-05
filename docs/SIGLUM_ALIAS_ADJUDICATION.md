_Created: 10-06-2026 · Last updated: 05-09-2026_

# Source-siglum alias adjudication (OBS-C)

Date: 2026-06-10

Review log for the abbreviation-family merge candidates produced by
[`scripts/obs/siglum_families.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/siglum_families.py). Accepted
merges are written to
[`src/data/dict-source-aliases.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dict-source-aliases.json),
which feeds `canonicalSiglum()` in
[`scripts/lib/source-siglum.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/source-siglum.mjs).

**Principle.** Merge a candidate family only when every member is the *same work*
— variants being section/book numerals (`raghxii` = Raghuvaṃśa XII), edition tags
(`pancatedbomb` = ed. Bombay), or trivial spelling. Where a prefix cluster mixes
**distinct works**, split it (accept the single-work subset, keep the rest
separate) or leave it in the queue. Containment of a short ambiguous key (`kath`,
`panc`, `varah`) is not merged.

## Accepted — single-work families (27 canonical works)

Pure accepts (all members one work): Bhāgavata-purāṇa, Mahābhārata (book refs),
Raghuvaṃśa (20 sarga refs), Suśruta-saṃhitā, Aitareya-brāhmaṇa, Dhātupāṭha
(29 adhyāya refs), Yājñavalkya-smṛti, Divyāvadāna, Indische Studien, Gobhila-
gṛhyasūtra, Āśvalāyana-gṛhyasūtra, Lāṭyāyana-śrautasūtra, Naighaṇṭuka,
Naiṣadhacarita, Mṛcchakaṭikā, Chāndogya-upaniṣad, Mārkaṇḍeya-purāṇa, Halāyudha.

`varbrs`/`varbr` were cross-merged into `varahbrhs` — both abbreviation schemes
denote Varāhamihira's **Bṛhatsaṃhitā**.

## Partial accepts — split a mixed cluster, merge only the single-work subset

| Cluster (prefix) | Merged → canonical | Kept SEPARATE (distinct work) |
|---|---|---|
| `kath` | Kathāsaritsāgara (`kathas`, …lxi/xviii/lxxii/vi) | `kathop`/`kathup` = Kaṭha-Upaniṣad; `katharn(ava)` = Kathārṇava; bare `kath` (ambiguous) |
| `raja` | Rājataraṅgiṇī (`rajatar`, `rajat`+roman) | `rajan` = Rājanighaṇṭu (a lexicon — different work) |
| `panc` | Pañcatantra (`pancat`+roman/ed) | `pancavbr` = Pañcaviṃśa-brāhmaṇa; `pancad` = Pañcadaśī; `pancar`, `panci`, bare `panc` |
| `vara` | Bṛhatsaṃhitā (`varahbrhs`, `varahbrh`) | `varahyogay` = Yogayātrā (same author, different work); `varahap`, bare `varah` |
| `katy` | Kātyāyana-śrautasūtra (`katysr`+roman) | bare `katy`/`katyayana` (could be the Vārttika) |
| `mait` | Maitrāyaṇī-saṃhitā (`maitrs`+roman) | `maitryup`/`maitrup` = Maitrī/Maitrāyaṇa-Upaniṣad |
| `sank` | Śāṅkhāyana-gṛhyasūtra (`sankhgr`+i) | `sankhsr` = Śrautasūtra; `sankhbr` = Brāhmaṇa; `sankara` = Śaṅkara |
| `chan` | Chāndogya-upaniṣad (`chandup`, `chandups`) | `chandom` = Chandomañjarī; `chandas`; `chandr` |
| `bala` | Bālarāmāyaṇa (`balar`+roman) | `balab` (Bālabodhinī?); bare `bala` |
| `sabd` | Śabdārthakalpataru (`sabdarthak(alpataru)`) | `sabdar`/`sabdac`/`sabdam`/`sabdak` = distinct lexica (Śabdaratnāvalī, Śabdacandrikā, …) |

## Rejected — left in the queue (no merge)

- **`hari`**: `hariv` = Harivaṃśa vs `harita` = Hārīta (dharmaśāstra author). Distinct.
- **`verz`**: `verzdoxfh` (Oxford), `verzdbh` (Berlin), `verzdcambrh` (Cambridge),
  `verzdtubh` (Tübingen) — these are **different manuscript catalogues** (different
  libraries), not one work; not merged despite the shared "Verzeichniss" prefix.
- **`kaus`**: `kaus` (Kauśika?), `kausup` = Kauṣītaki-upaniṣad, `kausbr` = Kauṣītaki-
  brāhmaṇa. Distinct.
- **`cara`**: `caraka` = Caraka-saṃhitā vs `caran` = Caraṇavyūha. Distinct.
- **`kuma`**: `kumaras` = Kumārasambhava vs `kumarila` = Kumārila (author). Distinct.
- Lower-frequency / len-4-prefix families (`maha`, `samk`, `sarv`, `webe`, `cole`,
  `burn`, `unad`, `dhar`, …) remain `unreviewed` — many are genuine multi-work
  clusters or author-vs-work ambiguities needing source inspection.

## Impact

~150 fold-keys merged into 27 canonical works (the high-frequency head). The
diacritic/case fold already handles the bulk; this adjudication extends the
*reviewed* layer for the most-cited abbreviation families. The long tail stays in
the source-siglum review queue by design — `siglum_families.py` regenerates
candidates, this table records human decisions.

_Dr. Mārcis Gasūns_
