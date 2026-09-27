_Created: 24-09-2026 · Last updated: 24-09-2026_

# Usage and register labels — comparative census across the nine narrative dictionaries

Handoff H5333 (epic E014), OxAlpha `opencode/z-ai/glm-5.3-flash`. Data: `csl-orig@f4c08c57`.

Every dictionary tells the reader *where a word is used* — that it is Vedic, epic, classical, poetic, liturgical, figurative, literal, or that it exists only in the lexicographers (a word no text ever attests). This page asks, for each of the nine narrative dictionaries, *how is that information encoded, how often does each label occur, and how do the dictionaries compare?* The lexicographers-only label has been studied for MW alone; this census extracts every usage/register label per dictionary from the tagged markup, normalises the raw strings to one published vocabulary, and reports counts and per-thousand-records rates.

Outputs:

1. [`data/lexico/usage_register_labels.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/usage_register_labels.json) — envelope (mapping, csl-orig pin, denominators) plus per-dictionary counts, rates and the untagged residue.
2. [`data/lexico/usage_register_labels_map.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/usage_register_labels_map.csv) — the published mapping table: raw string × surface × dictionaries × total.
3. [`data/lexico/usage_register_labels_counts.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/usage_register_labels_counts.csv) — dictionary × normalised label × surface counts with the per-1,000-records rate.
4. The generator is [`scripts/lexico/m12_usage_register_labels.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m12_usage_register_labels.py) (`npm run build-usage-register-labels`, stdlib only, ~40 s, deterministic). Hand-derived pins are in [`tests/forensic/test_m12_usage_register_labels.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_m12_usage_register_labels.py).

## 1. Where the labels live

Two Cologne tags carry usage/register information, and the dictionaries split by which one they file their labels in:

- **`<lang>…</lang>`** — MW files `Ved.` (612) and `ep.` (328) here; PWG files `ved.` (543), `klass.` (89), `nachved.` (9); PW files `ved.` (52), `klass.` (5), `ep.` (2). A `<lang>` token absent from the mapping is a true language name (`Lat.`, `Gk.`, `Mar.` …) — 4,532 such tags across the estate, counted in the envelope, never in the register table.
- **`<ab>…</ab>`** — AP files `Ved.` here (**1,916**, the estate's largest single cell), and its `fig.` (416) / `lit.` (98) / `epic.` (9); PWG files the estate's only tagged **lexicographers-only** family — `Lexicogrr.` (38), `Lexicogr.` (2), `Lexicc.` (1); MW files `fig.` (245), `lit.` (217), `poet.` (3).

The same mapping table also carries the middle-Indo-Aryan ascriptions found in `<lang>` — `Prākṛt`/`Prākrit` (398), `Pāli` (63), `Apabhraṃśa` (7) — as a separate `kind`, since they ascribe a word to a speech layer rather than a genre.

## 2. Published mapping and per-dictionary rates

Normalisation: the raw tag content is whitespace-trimmed and stripped of paired bracket punctuation (`().,:;`), then matched against the exact mapping keys — `(Ved.` → VEDIC, `Fig.` and `fig.` → two raw rows of one FIGURATIVE label, `Lexicogrr.`/`Lexicogr.`/`Lexicc.` → LEXICOGRAPHERS_ONLY. Full table: the map CSV above.

Tagged occurrences and rates (per 1,000 csl-orig records):

| Label (kind) | MW | PWG | PW | AP | WIL | SKD | VCP | ARMH | ABCH | Estate |
|---|---|---|---|---|---|---|---|---|---|---|
| VEDIC (register) | 612 · 2.14 | 543 · 4.40 | 52 · 0.30 | **1,916 · 21.09** | 0 | 0 | 0 | 0 | 0 | 3,123 |
| EPIC (register) | 328 · 1.14 | 97 · 0.79 | 2 · 0.01 | 9 · 0.10 | 0 | 0 | 0 | 0 | 0 | 436 |
| CLASSICAL (register) | 0 | 89 · 0.72 | 5 · 0.03 | 0 | 0 | 0 | 0 | 0 | 0 | 94 |
| POST_VEDIC (register) | 0 | 9 · 0.07 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| POETIC (register) | 3 · 0.01 | 2 · 0.02 | 0 | 1 · 0.01 | 0 | 0 | 0 | 0 | 0 | 6 |
| LEXICOGRAPHERS_ONLY (register) | 0 | **41 · 0.33** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 41 |
| LITURGICAL (register) | 0 | 11 · 0.09 | 4 · 0.02 | 0 | 0 | 0 | 0 | 0 | 0 | 15 |
| FIGURATIVE (register) | 245 · 0.86 | 1 · 0.01 | 1 · 0.01 | 416 · 4.58 | 15 · 0.34 | 0 | 0 | 0 | 0 | 678 |
| LITERAL (register) | 236 · 0.82 | 6 · 0.05 | 0 | 98 · 1.08 | 13 · 0.29 | 0 | 0 | 0 | 0 | 353 |
| PRAKRIT (middle_indic) | 227 · 0.79 | 10 · 0.08 | 161 · 0.94 | 0 | 0 | 0 | 0 | 0 | 0 | 398 |
| PALI (middle_indic) | 31 · 0.11 | 0 | 31 · 0.18 | 1 · 0.01 | 0 | 0 | 0 | 0 | 0 | 63 |
| APABHRAMSA (middle_indic) | 6 · 0.02 | 0 | 1 · 0.01 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| **All tagged** | **1,688** | **809** | **257** | **2,441** | **28** | 0 | 0 | 0 | 0 | **5,223** |

Records (denominator): MW 286,525 · PWG 123,366 · PW 170,556 · AP 90,847 · WIL 44,577 · SKD 42,531 · VCP 50,135 · ARMH 7,907 · ABCH 1,965.

## 3. Findings

1. **The tagged layer is a European-medium phenomenon.** Five dictionaries carry every one of the 5,223 tagged labels; the four Sanskrit-medium dictionaries (SKD, VCP, ARMH, ABCH) carry none. Their usage markers live in Devanāgarī prose (सं. for "in the lexicographers" and the like), outside this tag census — zeros are findings, not defects.
2. **Vedic dominates but the tag surface differs.** VEDIC is 59.8 % of all tagged labels, yet MW/PWG/PW file it in `<lang>` while AP files it in `<ab>` — and AP's Vedic rate (21.09/1k) is ten times MW's (2.14/1k). Apte flags Vedic tenure on the word itself; MW flags it per-sense inside the grammar apparatus.
3. **Lexicographers-only marking is PWG's alone.** All 41 tagged LEXICOGRAPHERS_ONLY occurrences are PWG `<ab>` cells. MW — whose lexicographers-only stock is the famous one — carries no tagged marker at all in this census; its hedge lives in prose. Any cross-dictionary lexicographers-only study must normalise through this table or it will mistake tagging convention for lexicographic practice.
4. **The tag layer captures nearly everything.** Net-untagged residue (tag-stripped text minus tagged occurrences) is tiny: MW 44 (43 `poet.` + 1 `Ved.`), AP 24, WIL 14, PW 4, PWG 1 — 87 across the estate against 5,223 tagged. MW's `Ved.` is 99.8 % tagged; its `poet.` is the one label it habitually leaves in plain text.
5. **PWG alone marks chronological fine-grain.** `klass.` (classical), `nachved.` (post-Vedic) and `liturg.` (liturgical) exist only in the Petersburg dictionaries, PWG overwhelmingly — a period axis MW and AP never tag.

## 4. Limits

1. Only the two tagged surfaces are censused; Devanāgarī prose markers (SKD/VCP/ARMH/ABCH) and any label conventions outside `<ab>`/`<lang>` are out of scope.
2. The mapping is an exact-string table — a raw variant not in the table is silently a `language_name_tags` row (for `<lang>`) or ignored (for `<ab>`). The map CSV lists every raw string actually matched, so additions are auditable.
3. Rates use csl-orig `<L>` records as denominator; alias records and run-on sub-entries are not separated (unlike M11's views).
4. `<ab>` also carries ~200 grammatical abbreviations (`cf.`, `fr.`, `P.`, `Ā.` …); only mapping keys were counted, so grammar noise cannot enter the register table.

## 5. Reproduce

```sh
npm run build-usage-register-labels   # writes the three data/lexico files
python -m pytest tests/forensic/test_m12_usage_register_labels.py -q
```

Refutation conditions: a register-bearing tag surface other than `<ab>`/`<lang>` in a European-medium dictionary, or a raw usage-label string in those tags absent from the published mapping, refutes the census's completeness claim for that dictionary.

_Гасунс_
