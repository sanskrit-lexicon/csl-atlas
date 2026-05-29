# All-Dictionary Coverage And Size Layer

Date: 2026-05-28

## Purpose

Figure 6 in the MW microanalysis paper measures **common-block population**: for each dictionary and block, what percentage of entries contain the structural signal. That is necessary, but not enough. The next atlas layer must also ask:

- How large is each dictionary?
- How long are its entries?
- Which block signals occupy measurable character mass?
- Which entry-type buckets are populated?
- Which CDSL dictionaries fit the MW-derived scheme fully, partially, or only as a boundary case?

The implementation is `npm run build-coverage`, which scans every local `../csl-orig/v02/<code>/<code>.txt` source file and writes:

- `src/data/dictionary-coverage.json` for the Observable atlas.
- `data/dictionary-coverage.json` for repo-level inspection and downstream scripts.

Current scan: **43 dictionaries**, **1,495,461 entries**.

## Volume Corrections To Keep Everywhere

The atlas must not use a simple "single-volume versus multi-volume" explanation for block economy. Four key works are all seven-volume works:

| Dictionary | Volume count | Consequence |
|---|---:|---|
| PWG | 7 | Citation-dense structured bilingual dictionary. |
| PWK | 7 | Compact seven-part Petersburg counterpart, not one-volume; it compresses PWG's apparatus. |
| SKD | 7 | Sanskrit-Sanskrit prose / `iti` lexicon; boundary case for the structured-bilingual block model. |
| VCP | 7 | Sanskrit-Sanskrit prose / `iti` lexicon; confirms the same genre boundary. |

Therefore the explanatory variable is not volume count alone. The better contrast is **editorial structure**: tagged citation slots, compacted citation apparatus, prose citation, and genre.

## Entry-Type Inventory

The first all-dictionary pass uses nine heuristic buckets:

| English | Russian |
|---|---|
| root / verbal lemma | корень / глагольная лемма |
| noun masculine | существительное мужского рода |
| noun feminine | существительное женского рода |
| noun neuter | существительное среднего рода |
| adjective | прилагательное |
| indeclinable / particle | неизменяемое слово / частица |
| compound / continuation | композит / продолженная статья |
| proper / encyclopedic | имя собственное / энциклопедическая статья |
| other / untyped | другое / нетипизированное |

These are research buckets, not final philological categories. Their job is to show where the MW/PWG/PWK/AP style of type detection transfers and where dictionary-specific typology must be built.

## Size Measures

For each dictionary, the coverage layer records:

- records;
- bytes and total characters;
- mean, median, and maximum entry length;
- raw tagged `<ls>` spans per record;
- inline `iti` citations per record;
- block population percentage;
- block character mass;
- type counts and type percentages;
- framework-fit score and fit band.

The key new answer to "how big is each block?" is `blockChars` and `blockCharPct`. These are overlapping signal measurements, not a partition of the entry: the body can contain citation, grammar, and homograph spans that are also counted separately. The first pass is conservative: for tagged blocks it counts actual tag spans; for inline `iti` it counts a short context window after the formula; for body it counts the entry body as a whole. A later philological pass should replace these heuristics with per-dictionary parsers.

## Fit Bands

| Band | Meaning |
|---|---|
| full structured fit | Head/body plus several tagged structural signals transfer well. |
| partial structured fit | Entry shell and some tagged signals transfer. |
| prose / iti fit | Entry shell transfers, but citation lives in prose rather than `<ls>`. |
| entry-shell fit | `<L>` / `<k1>` structure exists, but few MW blocks transfer. |
| weak fit | Some signals exist, but the scheme is not reliable yet. |
| outside scheme | The MW-derived probe is not informative. |

## Research Direction

The all-dictionary layer should become the bridge between the current paper and the future public atlas:

1. Keep the nine narrative chapters as curated interpretation.
2. Use all-dictionary coverage to find candidates beyond the original nine.
3. Promote promising dictionaries into new chapters only after the coverage layer shows real structure.
4. Build a separate Sanskrit-Sanskrit / `iti` parser for SKD, VCP, and related prose lexica.
5. Feed the entry-type and block-size results into TEI archival modeling and OntoLex semantic modeling.

This turns Figure 6 from a structural heatmap into the first panel of a larger atlas: structure, size, type, fit, and model loss.
