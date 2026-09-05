_Created: 09-06-2026 · Last updated: 05-09-2026_

# R2 Page Regeneration Spec

Date: 2026-06-09 | Completed: 2026-06-10

Status: **COMPLETED**. The three R2 tool pages (`/tools/r2-explorer`,
`/tools/r2-h1`, and `/tools/r2-h2h3`) are now **data-driven** from live JSON under
`data/lexico/`. The page-wiring script `scripts/build-r2-pages.mjs` regenerates
the pages from that JSON, replacing static archived snapshots with computed output.
All acceptance gates met; 140 tests pass.

**Boundary:** this is presentation only. Do **not** change any parser rule,
generator heuristic, or the JSON schemas. Read the committed JSON, emit
SVG/HTML. Archive parity is a regression signal, not a target.

## Deliverable

A generator `scripts/build-r2-pages.mjs` (`npm run build-r2-pages`) plus a new
page `src/tools/r2-h2h3.md`, plus unit tests. It reads:

| Reads | Writes (between markers, see below) |
|---|---|
| `data/lexico/r2_h1.json` | the scatter SVG in `src/tools/r2-h1.md` |
| `data/lexico/r2_align_<lemma>.json`, `senses_<dict>.jsonl` | the cards/table in `src/tools/r2-explorer.md` |
| `data/lexico/r2_h2h3.json` | the two charts + table in the **new** `src/tools/r2-h2h3.md` |

### Marker-injection mechanism (idempotent)

In each page, wrap the generated block in HTML comment markers:

```html
<!-- R2-GEN:START h1-scatter -->
…generated SVG…
<!-- R2-GEN:END h1-scatter -->
```

The generator replaces only the text between matching `START`/`END` markers,
leaving prose, the trust block, and the `<style>` untouched. If a page has no
markers yet (h1, explorer), add them around the existing SVG/HTML first, then
let the generator overwrite. Re-running the generator must produce no diff when
the JSON is unchanged (idempotent). Files are UTF-8, **no BOM**
(`open … 'w'`-equivalent; Node `fs.writeFileSync` default is fine).

## Shared conventions (match the existing pages)

- Header `<style>`: `font-family:system-ui,sans-serif`. Reuse the `.note` class
  (`color:#555/#666;font-size:~13px`) for captions.
- **Family/cluster palette** (already used in both pages — do not invent new
  colors): western/Apte `#1f77b4`, Benfey `#ff7f0e`, Cappeller `#2ca02c`,
  Monier-Williams `#d62728`, Petersburg `#9467bd`, Wilson `#8c564b`,
  indigenous `#e377c2`, reverse `#9467bd`. Neutral text `#333`, axis `#999`,
  gridline `#eee`, muted label `#555`.
- Every page keeps a **Trust Block** paragraph (see h1's) naming: evidence
  (this page + the live JSON file), the restored generator command, the headline
  number vs archived, and "121/134 unit tests pass". Update wording to say the
  page is **now generated from** the JSON (not "still archived").
- Keep the existing archived numbers visible as a faded/secondary comparison
  where the spec calls for it; the **restored** numbers are primary.

## Page 1 — `r2-h1.md` (data-drive the existing scatter)

The current SVG is the visual target. Keep its 720×440 frame, axes, and family
legend. Replace the hand-placed `<circle>`/`<text>` points with points computed
from `r2_h1.json.rows`:

- X = publication year. The existing axis runs 1820→1960 across x∈[60,550]:
  `x = 60 + (year - 1820) / (1960 - 1820) * (550 - 60)`.
- Y = `senseUnitsPerEntry`. Axis 0→3 across y∈[390,52] (390=0, ~52=3):
  `y = 390 - (units / 3) * (390 - 52)`. Clamp units>3 to the top.
- Point color = family via the palette map. Radius 6, `fill-opacity 0.85`.
- `<title>` tooltip: `"{dict} ({year}, {family}): {units} units/entry, {entries} entries"`.
- Keep the family-mean legend (right side) and the Pearson-r caption, pulling
  `r` from `r2_h1.json.stats.pearsonYearVsUnits` and the family means from
  `.families`.

This page should look ~identical to today's; it is now reproducible.

## Page 2 — `r2-explorer.md` (data-drive the existing cards/table)

Keep the existing CSS, the headword `<select>`, the cluster pills, and the
alignment table. Generate, per anchor lemma in
`r2_align_<lemma>.json` (`gam, dharma, rama, iti, bodhisattva`):

- One `.dict` card per dictionary in `senses`, listing each sense
  (`.num` = localId, text = clipped gloss). Card `.pill` class from the
  dictionary's cluster (`western`/`indigenous`/`reverse`).
- The alignment table from `alignments[]`: columns `a`, `b`, `j` (Jaccard),
  `shared` (as `.chip`/`.chip.cite`/`.chip.sig` by prefix `s:`/`ls:`/`sig:`),
  and a `.cross` highlight when `cross` is true.
- Default the `<select>` to `dharma` (its `ap#4~ap90#4` J=1 row is the headline).

Keep behavior identical to the archived page; it is now reproducible.

## Page 3 — `r2-h2h3.md` (NEW — full layout below)

Create `src/tools/r2-h2h3.md` from scratch. Source: `data/lexico/r2_h2h3.json`
(`.h2`, `.h3r[3]`, `.panel`, `.panelSize`). Structure: `<style>` → `<h1>` →
intro `.note` → Trust Block → **Chart A** → **Chart B** → **data table** →
finding paragraph. All numbers come from the JSON — no hardcoding.

### Chart A — H2 citation-survival (grouped vertical bars)

> Question: do ancestor senses that carry a citation survive into the descendant
> more often than uncited ones? Encodes `h2.cited.rate` vs `h2.uncited.rate`,
> each with its archived counterpart.

- SVG `width="720" height="300"`, `font-family system-ui`, `font-size 12`.
- Plot area: baseline `y=250`, top `y=40` → 210px spans rate 0..1.
  **Rate→y:** `y = 250 - rate*210`; **bar height** `= rate*210`.
- Y gridlines + labels at 0/25/50/75/100 %: `y = 250 - p*210` for p in
  {0,.25,.5,.75,1}; gridline stroke `#eee` from x=80 to x=660; label at x=70,
  `text-anchor=end`, fill `#555`.
- Two groups: **Cited** centered x≈250, **Uncited** centered x≈470. Each group
  has two bars, width 56, 8px gap:
  - restored bar (left): `x=groupCx-60`, fill = group hue, opacity 1.
  - archived bar (right): `x=groupCx+4`, fill = group hue, opacity 0.4.
  - **Group hue:** Cited = `#2ca02c` (green = well-sourced/sticky),
    Uncited = `#888` (neutral gray).
- Above each bar: the percentage label (`Math.round(rate*100)+"%"`), `text-anchor=middle`, fill `#333`.
- Below baseline (y=268): group label (`"Cited"` / `"Uncited"`) and the n
  (`"n="+cited.n`), fill `#555`.
- Legend (top-right, ~x=520,y=40): "■ restored (csl-orig)" solid, "■ archived"
  faded — one swatch pair, gray.
- Y axis title (rotated -90 at x=20): "sense-survival rate".
- Annotate the gap: a thin bracket/label between the two restored bars' tops
  reading `"+"+(cited.rate-uncited.rate).toFixed(2)+" gap"`.

### Chart B — H3R sense-drift dumbbell (3 edges)

> Question: along each measured inheritance edge, does the descendant add,
> copy, or condense senses? Encodes `meanAncSenses → meanDesSenses` per edge,
> colored by `pattern`, annotated with `meanGlossOverlap`.

- SVG `width="720" height="300"`.
- X = mean sense-units per lemma. Domain 0..`maxS` where
  `maxS = Math.ceil(max over edges of max(meanAncSenses, meanDesSenses)) + 2`
  (with the current data that's ~13; compute it, don't hardcode). Range
  x∈[150,620]: `x(s) = 150 + (s/maxS)*(620-150)`.
- One row per edge in JSON order (`wil→shs`, `wil→yat`, `ap90→ap`) at
  `y = 70 + i*70` (rows at 70, 140, 210).
- Each row draws a **dumbbell**:
  - line from `x(meanAncSenses)` to `x(meanDesSenses)` at yRow, stroke =
    pattern color, width 3, with a small arrowhead (a `<path>` triangle) at the
    descendant end.
  - ancestor circle at `(x(meanAncSenses), yRow)`, r=7, fill `#999` (gray =
    "the older dictionary").
  - descendant circle at `(x(meanDesSenses), yRow)`, r=7, fill = pattern color.
  - faded archived ghost (optional but preferred): small circles (r=4,
    opacity 0.3, gray) at `x(archived.meanAncSenses)` and
    `x(archived.meanDesSenses)`.
- **Pattern→color** (map on the `pattern` string, case-insensitive substring):
  `copy`/`verbatim` → `#2ca02c` (green); `condens` → `#d62728` (red);
  `revision` → `#ff7f0e` (orange). Provide a default `#1f77b4` if no match.
- Left label (x=8, yRow, font-size 11): a human edge name. Map dict codes to
  display names: `wil→shs` = "Wilson 1832 → Śabda-Sāgara 1900",
  `wil→yat` = "Wilson 1832 → Yates 1846",
  `ap90→ap` = "Apte 1890 → Apte 1957". (Derive from `ancDict`/`desDict`; keep a
  small code→label map.)
- Right annotation (x=632, yRow, text-anchor=start): `"overlap "+overlap.toFixed(2)`.
- X axis at y=255: line x∈[150,620], ticks + labels at 0,4,8,12,16 (only those
  ≤ maxS): `x(t)`; axis title "mean sense-units per lemma" centered under it.
- Legend (top-right): three swatches — green "copy", red "condensation",
  orange "revision".

### Data table (below the charts)

Reuse the explorer table CSS (`table/td/th`). One row per edge:

| Edge | Senses (anc → des) | Drift | Gloss overlap | Pattern | Archived (anc→des, overlap) |
|---|---|---|---|---|---|

Then a one-line H2 summary under it:
`"H2: cited senses survive at {cited.rate}, uncited at {uncited.rate} (n {cited.n}/{uncited.n}); archived {archivedCited.rate}/{archivedUncited.rate}."`

### Intro + finding text (h2h3 page)

- Intro `.note`: explain the 28-noun panel (`panelSize`), the three edges, and
  that survival uses gloss-word overlap (Wilson-line glosses are English with
  few per-sense Sanskrit anchors). State `survivedThreshold`.
- Finding paragraph: **H2 supported** (citation density predicts survival);
  **H3R**: no edge adds senses — Wilson→Śabda-Sāgara is near-verbatim copy
  (overlap ~0.91), Wilson→Yates is drastic condensation, Apte 1890→1957 is
  revision. Pull all numbers from the JSON.

### Trust Block (h2h3 page)

Mirror h1's trust block. Evidence: this page generated from
`data/lexico/r2_h2h3.json`; generator `npm run build-r2-h2h3` (data) +
`npm run build-r2-pages` (page). Headline: H2 cited > uncited reproduced
(0.762 vs 0.591; archived 0.70/0.54); H3R copy/condense reproduced. Limitations:
SHS/YAT senses split by inline `N.` markers; panel reconstructed (drift vs the
deleted original panel documented in `R2_REBUILD_CONTRACT.md`). Validation:
`npm test` (134 tests). Owner: `csl-atlas`.

## Navigation

Add `/tools/r2-h2h3` to navigation next to `r2-h1` and `r2-explorer`, following
the exact pattern those two use (check `observablehq.config.js` and/or the tools
index page; mirror, don't invent).

## Tests (append to `test/orchestrators.test.mjs`)

Export the pure rendering helpers from `build-r2-pages.mjs` (e.g.
`h1Points(json)`, `h2Bars(json)`, `h3rDumbbells(json)`, `patternColor(str)`,
`yearToX`, `rateToY`) and assert:

1. `patternColor` maps copy→green, condensation→red, revision→orange, else default.
2. `h2Bars` returns 4 bars; cited restored bar height > uncited restored bar
   height (0.762 > 0.591); each bar's `rate` matches the JSON.
3. `h3rDumbbells` returns 3 rows; the `wil→yat` row has `meanDesSenses` ≈ 1 and
   the largest negative drift; `wil→shs` drift ≈ 0.
4. `yearToX(1832)` and `rateToY(0)`/`rateToY(1)` hit the documented axis anchors.
5. Generator is **idempotent**: running it twice on the committed JSON yields the
   same file bytes (snapshot the marker block).

Keep the existing 134 tests green. Do not modify the R2 data generators or their
JSON.

## Acceptance

- `npm run build-r2-pages` regenerates all three pages with no manual edits.
- Re-running produces no git diff (idempotent).
- The h2h3 SVG contains the live numbers (`0.762`, `0.591`, `0.906`) and the
  correct mark counts (4 H2 bars, 3 H3R dumbbells).
- All pages keep their Trust Block, now worded as "generated from JSON".
- `npm test` passes; no parser/JSON-schema change in the diff.

_Dr. Mārcis Gasūns_
