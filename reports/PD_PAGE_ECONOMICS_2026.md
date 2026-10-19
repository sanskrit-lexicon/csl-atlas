# PD vs PWG vs OED page economics — what a page contains, and what an entry costs in pages

_Created: 19-10-2026 · Last updated: 19-10-2026_

_Dr. Mārcis Gasūns_

**Handoff:** [H7109](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7109-DeepSeek_csl-atlas_pd-page-economics_19.10.26.md) · **Executor:** DeepSeek Flash (`deepseek-flash`)

The question is not which dictionary is bigger. It is **how much of a page is a decision**: how
many entries a printed page carries, how many printed lines and characters each entry costs, and
how much page area the whole apparatus occupies. Those are the quantities that turn a
lexicographic programme into a schedule.

## Headline

A page is **about 28 entries** in PD, **about 28** in PWG and **about 20** in the OED sample —
across a century and a half, two languages of scholarship and three different page formats. Page
format is not what separates these dictionaries. What separates them is **how much text each
decision carries**: PD and PWG spend ≈380–390 characters per entry, the OED sample ≈1,030. PD is
slow not because its pages are crowded but because its entries are long — which is the same
conclusion §6.2 of A68 reaches from the citation side, and this pass measures the page side of it
for the first time.

| | PD | PWG | OED (sample) |
|---|---:|---:|---:|
| pages in the measured basis | 4,327 | 4,750 (reconstructed) | 3 (random) |
| entries | 107,630 | 123,366 | 50 |
| entries per page (mean) | 24.87 | 25.97 | 16.67 |
| **entries per page (median)** | **28** | **28** | **20** |
| characters per page | 9,764 | 9,823 | 17,231 |
| characters per entry | 393 | 378 | 1,034 |
| columns per page | 2 | 2 | 3 |

## 1. Method, and why the units needed fixing first

The three sources do not encode the same thing, and the whole comparison collapses if that is
waved through.

**PD** (Cologne PDScan 2020 `txt/pd.txt`) encodes a printed line break as `<div n="lb">` — 440,003
of them — but the line that *opens* an entry carries no such tag. So "line-divisions" is not
"printed lines": the printed lines of PD are the 440,003 breaks **plus** the 107,630
entry-opening lines, **547,633**, which is what the machine text's own header asserts
(`…_FINAL.TXT, … 547634Lines`; the extra line is the header itself). Both numbers are reported
below and in the TSV, because the handoff's "line-divisions" figure is the bare `lb` count and it
would be wrong to label it "lines per page".

**PWG** (`csl-orig/v02/pwg/pwg.txt`) encodes **no printed line break at all**. Its body lines are
wrapped at source level — median 115 characters, maximum 15,234 — so they are *machine* lines. PWG
printed lines are not recoverable from the text, and this report does not report them as if they
were. What is recoverable is the character mass and the number of entries.

**Pages are reconstructed, not counted** in both machine texts, because both number a **column**,
not a page. PD's `<pc>` is `volume-page` plus a column letter `a`/`b`; the text's own page markers
(`[Page1-0001a+ 54]`) give 54 lines for that column, 64 at the median, two columns to the page — a
2 × 64 = 128-line grid. PWG's `<pc>` is a page-col reference whose two columns are the **odd
(left)** and **even (right)** numbers of one page, exactly as `pwg-meta2.txt` states. A "page" here
is therefore a printed page *reconstructed* from the column reference; the reconstruction is
stated in every row's `basis` column and the PWG figure is a ceiling, not a count of scanned pages.

**OED is measured on page images**, not on a machine text. Edition: **the 1933 corrected re-issue
of OED1 (1928)**, volume **IV (F–G)**, Clarendon Press — read from the scan's own title page, not
from memory. It is a **three-column** page, which is the re-issue's format and *not* the 1928
two-column folio; anyone quoting "OED pages are two columns" is quoting the first edition.

Page IDs and measurement, per sampled page:

| printed page | leaf | running heads | columns | lines/column | lines/page | entries |
|---:|---:|---|---:|---|---:|---:|
| 242 (**fire**, anchor) | 253 | FIRE. / FIRE. | 3 | 101, 98, 93 | 292 | 1 |
| 78 (random) | 89 | FARMERLY. / FARRAND. | 3 | 99, 93, 92 | 284 | 21 |
| 362 (random) | 373 | FLURTED. / FLUSH. | 3 | 96, 98, 96 | 290 | 9 |
| 154 (random) | 793 | GIBBON. / GIBLET. | 3 | 100, 95, 98 | 293 | 20 |

Random pages were drawn with a seeded pick (seed 7109) from leaves 20–1150, excluding leaves
235–262 (the *fire* entry and its compounds). Columns and printed lines are measured on the image
by column/row projection of the ink mask; characters per column are measured on that page's own
OCR text layer between its two running heads (5,664 chars on p. 362, 5,823 on p. 154). That
per-column figure cross-checks against the volume: 20,157,083 OCR characters / 1,176 leaves =
**17,140 per leaf**, and three columns × 5,664–5,823 = **17,000–17,500**. Entries are a **visual
count** of bold headwords on the image, ±1; no automated bold-headword detector reached a usable
signal on this scan.

The three sources are never mixed inside one average: each TSV row names its own source, and no PD
or PWG number is derived from an OED number.

## 2. The three samples

### PD — 4,327 pages carry 107,630 entries

| measure | value | basis |
|---|---:|---|
| printed pages in the machine text | 4,327 | highest page number reached (`8-4327`) |
| entries | 107,630 | `<L>` headers |
| line-divisions (`<div n="lb">`) | 440,003 | the handoff's figure |
| printed lines | 547,633 | breaks + entry-opening lines |
| characters | 42,247,645 | body characters, lb tags removed |
| entry-bearing columns | 7,684 | distinct `<pc>` incl. `a`/`b` |
| entry-bearing page numbers | 4,055 | distinct `volume-page` |
| columns per page | 2 | `a`/`b` suffixes; 2 markers per physical page |
| lines per column | 64 (median; min 8, max 64) | `[Page…+ N]` markers, n = 6,730 |

Entries per column: **median 15** (min 1, max 28, n = 7,684).
Entries per page: **median 28** (min 1, max 52, n = 4,055).

The **4,327 vs 6,056** distinction matters and is the one place where the handoff's own headline
arithmetic is unsafe. 6,056 is the catalogue extent of the whole printed dictionary (Deccan
College ledger, pp. 1–4,327 in the machine text; the rest of the alphabet is print-only). Dividing
machine-text content by 6,056 gives 17.8 entries/page, 72.6 line-divisions/page and 6,976
characters/page — but those denominators include ~1,700 pages that contribute nothing to the
numerator. Over the pages the text actually spans, PD is **24.87 entries/page, 101.69
line-divisions/page and 9,764 characters/page** (or 126.6 printed lines/page if printed lines are
used, which is within 1.1 % of the 2 × 64 = 128 grid — an independent confirmation that the grid
reading is right).

### PWG — 123,366 entries over ~4,750 pages

| measure | value | basis |
|---|---:|---|
| printed pages (reconstructed) | 4,750 | Σ over 7 volumes of ⌈highest column / 2⌉ |
| entries | 123,366 | `<L>` headers |
| machine lines | 223,497 | body lines — **not** printed lines |
| characters | 46,661,479 | body characters |
| page-col codes | 8,171 | distinct `<pc>`, odd = left column |
| columns per page | 2 | `pwg-meta2.txt`: odd = left, even = right |

Highest column per volume: 1,147 · 1,103 · 1,015 · 1,219 · 1,678 · 1,511 · 1,822.
Entries per column: **median 15** (min 1, max 89, n = 8,171).
Entries per page: **median 28** (min 1, max 89, n = 4,329).

PWG and PD are uncannily alike on the page axis: same two-column format, same median 15 entries
per column, same median 28 per page, and character masses within 0.6 % of each other (9,823 vs
9,764 per page; 46.66 M vs 42.25 M total). The 15 % entry-count difference and the near-identical
character mass is the whole of PWG's advantage: it gets more entries out of the same paper by
writing shorter ones — 378 characters per entry against PD's 393, and far shorter ones on the
long tail.

### OED — the re-issue packs 1.76 × PD's characters into a page

| measure | value | basis |
|---|---:|---|
| sampled pages | 3 (random) | pp. 78, 362, 154 |
| entries | 50 | visual count |
| printed lines per page | 289 (284, 290, 293) | row projection on image |
| lines per column | 96 (min 92, max 100, n = 9) | row projection |
| columns per page | 3 | image |
| characters per column | 5,744 | OCR text layer between running heads |
| characters per page | 17,231 | 3 × 5,744 |
| page size | 13.74 × 18.65 cm | scan's declared 600 dpi × original pixel dimensions |

Entries per page: **median 20** (min 9, max 21). Characters per entry ≈ **1,034**.

The OED page is denser in characters than either Sanskrit dictionary — 3 columns, 96 lines a
column, 17,231 characters a page — yet it carries **fewer** entries than PD or PWG, because an OED
entry at this depth is long. The *fire* anchor page makes the point at its extreme: both running
heads read `FIRE.`, the page is 292 lines of one entry, and one headword owns a whole page.

## 3. What the comparison does and does not license

**It licenses** the statement that entries-per-page is a near-constant of dictionary typography —
20–28 across three dictionaries, three formats and a century — and that the real variable is
entry length (characters per entry). It licenses the arithmetic for scheduling: at PD's measured
24.87 entries per page and 121 pages per year, a finished *a*-to-*z* PD needs the entry count
before the page count is even meaningful.

**It does not license:**

- **Comparing lines/entry across dictionaries.** PD's printed lines and PWG's machine lines are
  different objects; only PD's printed lines are recoverable. The PWG row's `lines` is a text-line
  count and is labelled as such.
- **Treating 4,750 as PWG's page count.** It is a reconstruction from the highest column per
  volume, and columns are only coded where an entry begins, so it is a ceiling on the printed
  extent, not a census of scanned pages. PWG's scans were not opened this pass.
- **Treating the OED sample as the OED.** Three pages, 50 entries. The 16.67 mean is dominated by
  p. 362 (9 entries, because *Flush* is a long entry); the median of 20 is the better central
  figure, and neither is an edition-level statistic.
- **Quoting OED page size as a measurement.** It is derived from the scan's declared 600 dpi and
  its original pixel dimensions. A caliper measurement was not taken.
- **Reading "density" in A68 §6.2 as page density.** §6.2's 13–23× is *per headword*. On the page
  axis PD is the **least** character-dense of the three; its pages are ordinary, its entries are
  not.

## 4. Effect on A68 §6.2

**None — the wording was not changed, deliberately.** §6.2 attributes PD's projected span to
"its density, 13–23 times that of any finished dictionary **per headword**". This pass measures the
*page*, and the page measurement corroborates rather than contradicts: PD's pages carry the same
number of entries as PWG's and fewer characters than the OED's, so the slowness cannot be page
crowding. The existing sentence already says the right thing and needed no paragraph. Recorded
here rather than edited into the paper, per the handoff's "only if the comparison changes the
current wording".

## 5. Artefacts and reproduction

| file | what |
|---|---|
| [`data/pd/page_economics.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/page_economics.tsv) | the three rows: dictionary, edition, pages, entries, lines, characters, entries/page, lines/page, chars/page, columns, page size, plus source/basis/note |
| [`data/pd/oed_page_sample.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/oed_page_sample.json) | the four OED page measurements with page IDs, edition statement and count method |
| [`scripts/pd_page_economics.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_page_economics.py) | parser, OED sample reader, TSV writer, `--check` |
| [`tests/forensic/h7109_page_economics_pins.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/h7109_page_economics_pins.tsv) | 10 pinned rows, each naming where its number comes from |
| [`tests/forensic/test_pd_page_economics.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pd_page_economics.py) | the pins as tests, on miniature fixtures |

```sh
python3 scripts/pd_page_economics.py --pd /path/to/pdtxt/txt/pd.txt \
    --pwg ../csl-orig/v02/pwg/pwg.txt
python3 scripts/pd_page_economics.py --check --pd /path/to/pdtxt/txt/pd.txt \
    --pwg ../csl-orig/v02/pwg/pwg.txt
```

`--check` re-derives the TSV, the 9 acceptance canaries (107,630 / 440,003 / 42,247,645 /
547,633 / 7,684 / 123,366 / 223,497 / 8,171 / 4,750) and the 10 pins. Both texts are external and
read-only; the script exits 3 when either is absent.

### Provenance of the two machine texts (recorded because one path failed)

- **PD**: Cologne PDScan 2020 `pdtxt.zip`. The Cologne host
  (`sanskrit-lexicon.uni-koeln.de`) **refused TLS from this machine on 19-10-2026**
  (`SSL_ERROR_SYSCALL` on 443, empty reply on 80, `--tlsv1.2` no better), so the archive was
  fetched from the Wayback Machine instead. Member `txt/pd.txt`, **55,122,076 B** — byte-for-byte
  the size the dataset README documents, which is the check that the Wayback copy is the same
  artefact.
- **PWG**: local `csl-orig/v02/pwg/pwg.txt` (sibling checkout), read-only; no csl-orig commit.
- **OED**: archive.org item
  [`the-oxford-english-dictionary-1933-all-volumes`](https://archive.org/details/the-oxford-english-dictionary-1933-all-volumes),
  volume 4 `_jp2.zip` members, `_scandata.xml` (dpi, geometry, leaf count) and `_djvu.txt` (OCR
  text layer). Individual JP2 pages were pulled by member path; the BookReader
  `BookReaderImages.php` endpoint answers `Image error: not found` for this item because it has
  no `_jp2.zip` image stack in the form that endpoint expects.
