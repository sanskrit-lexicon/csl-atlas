# Metalexicography roadmap — measuring digital-edition richness

> Supporting specification. The governing delivery order is
> [`ROADMAP_2026_2027.md`](ROADMAP_2026_2027.md).

_Created: 04-06-2026 · Last updated: 01-09-2026_

**Version**: 1.0 · **Date**: 2026-05-16 · **Owner**: M. Gasūns + Claude Code
**Companion to**: [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md), [`L0_DESIGN.md`](L0_DESIGN.md)

Boundary update 2026-06-04: atlas may measure dictionary markup richness and
dictionary structure. TEI/OntoLex/FrAC/SHACL/RDF export, validation, and
publication pipelines belong in `csl-standards`; GitHub/org dashboards belong in
`csl-observatory`.

This doc plans the measurement of **what each digital edition adds, omits, encodes, and exposes** — distinct from the historical comparison of source contents. It's the meta-layer: the dictionaries-as-software story.

It addresses three large questions:

1. **Are all 35 digital editions equally rich?** No. Quantify the differences.
2. **Has MW received disproportionate attention** in the last 30 years? Prove with markup-richness data.
3. **What features did CDSL ADD** that weren't in the printed originals? Inventory and quantify them.

This stream produces material for **Paper M §4.1.6** (data-richness as KPI), **Paper L §6** (digital edition vs print), and a possible new **Paper E** (engineering/edition) covering the digital-edition history of CDSL.

---

## 1. The data richness typology (10 levels)

A scaled framework. Each digital edition can be placed on this scale.

| Level | Name | What's required | Example dicts at this level |
|---|---|---|---|
| **L0** | **Scan-only** | PDF page images; no text content | Patel-2016 scan-only set (PD, PE, PGN, IEG, MWE, AE, SNP, YAT) |
| **L1** | **Plain text** | OCR'd or keyboarded UTF-8; no markup | early state of all dicts before triage |
| **L2** | **Entry boundaries** | `<L>NNNN` … `<LEND>` markers separate entries | most dicts at minimum |
| **L3** | **Headword / body separation** | `<k1>` for primary, `<k2>` for variants | most well-processed dicts |
| **L4** | **Lexical metadata tags** | `<lex>` (category), `<gen>` (gender) | MW, AP, AP90, PWG, … |
| **L5** | **Citation tagging** | `<ls>` for literary sources, structured | MW (gold), PWG (gold), AP (good), others (partial) |
| **L6** | **Sense structure** | numbered or hierarchical senses; `<sense n="1">` or equivalent | MW (full), PWG (good), most others (partial) |
| **L7** | **Cross-reference tagging** | entry-to-entry pointers as machine-readable links | MW (full), few others |
| **L8** | **Scan-page linking** | each entry → page image of original print | major modern push (Dictionary-to-Book) — MW most complete |
| **L9** | **Cross-dictionary integration** | each headword → corresponding entries in other CDSL dicts | nascent; alternateheadwords, csl-lslink |
| **L10** | **Full structured semantic web** | external TEI/RDF publication via `csl-standards` | aspirational; not yet achieved by any CDSL dict |

**Hypothesis**: MW is the only dict at L8+; most others sit at L4-L6; specialised ones at L3-L5; scan-only ones at L0.

This typology becomes a **single ordinal metric per dict** (the *richness level*) and **multiple component metrics** (presence/absence per feature).

---

## 2. Measurable richness dimensions (~30 KPIs)

Per-dictionary, computed from source XML.

### 2.1 Markup density
| KPI | Method | Why it matters |
|---|---|---|
| Distinct tag count | count `<X>` distinct tag names | richer schema = more semantic distinctions |
| Total tag count | count all `<X>` occurrences | depth of encoding work |
| Tags per entry (mean, median) | total tags / entry count | per-entry markup investment |
| Max tag depth | max nesting level | hierarchical structure presence |
| Tag/text ratio | tag chars / total chars | how "structured" vs "prose" the data is |

### 2.2 Semantic tag presence (binary per dict)
| Tag family | Presence indicates |
|---|---|
| `<lex>` | lexical category encoded |
| `<gen>` | grammatical gender encoded |
| `<num>` | number encoded |
| `<ls>` | literary source citations machine-readable |
| `<ab>` | abbreviation expansions encoded |
| `{#…#}` | SLP1 boundaries marked |
| `{%…%}` | display-italic semantics preserved |
| `<k1>`/`<k2>` | primary/variant headword distinction |
| `<sense>` or numbering | sense structure machine-readable |
| `<bookref>` (or equivalent) | scan-page linking present |
| `<dictlink>` (or equivalent) | cross-dictionary linking present |

### 2.3 Citation richness (the truncation insight, applied at edition level)
| KPI | Method |
|---|---|
| Mean citation depth (text→book→chapter→verse) | parse `<ls>` content, measure components |
| Citation completeness | % of `<ls>` with full hierarchy vs truncated |
| Distinct cited works | count unique text-name strings in `<ls>` content |
| Citation density (per entry) | total `<ls>` / entry count |

### 2.4 Cross-reference richness
| KPI | Method |
|---|---|
| Internal references per entry | count `<k1>` recurrences inside body of other entries |
| External/dict references | count refs that point to other CDSL dicts |
| Bidirectional link count | refs that resolve in both directions |

### 2.5 Print-source linking (the CDSL-added feature)
| KPI | Method |
|---|---|
| Print-page coverage % | % of entries with `<page>` or `<bookref>` to scan |
| Image-link presence | % of entries linked to scan image |
| Pagination granularity | per-page, per-column, per-entry |

### 2.6 Editorial overlay (corrections after digitisation)
| KPI | Method |
|---|---|
| Correction issues filed | count from GitHub issues per dict |
| Correction issues resolved | closed-issue count |
| Editorial notes (`<note>`, `<corr>`) embedded in XML | count tags |
| Patel-fingerprint normalisation conformance | how close to Patel's standard? |

### 2.7 Metadata completeness
| KPI | Method |
|---|---|
| CITATION.cff present + complete | check schema fields |
| README richness | char count + section count |
| Schema/DTD documentation | presence of formal schema file |
| API exposure | does csl-apidev expose this dict? |
| App exposure | does csl-app surface this dict? |

---

## 3. The "MW gets all the attention" hypothesis

**Claim**: Monier-Williams (MW, 1899) has received disproportionate digital-edition attention in the last 30 years.

**Operationalisation** (multiple converging evidence streams):

| Evidence stream | Metric | How to measure |
|---|---|---|
| Markup richness | richness level (L0-L10) per dict | from §1 typology |
| Per-entry markup density | tags per entry (mean) | from §2.1 |
| Citation linking completeness | % of `<ls>` with full text→verse | from §2.3 |
| Cross-reference density | refs per entry | from §2.4 |
| Print-page link coverage % | from §2.5 |
| GitHub issue volume | issues opened (lifetime, normalised by entry count) | from observatory snapshots |
| Commit volume | commits (lifetime, normalised by entry count) | from observatory snapshots |
| Contributor count | distinct contributors per dict | from observatory snapshots |
| Multiple-edition presence | does MW have multiple parallel digital editions in CDSL? | yes: MW72 + MW(1899) + MWS variants |
| Downstream surface area | # of CDSL tools that consume this dict | csl-apidev, csl-app, csl-inflect, csl-devanagari, alternateheadwords, etc. |
| Citation in other CDSL repos | count cross-repo references | grep |

**Visualisation**: a single radar chart per dict on these axes. MW's polygon should dominate. If it doesn't, we revise the hypothesis.

**Counter-hypothesis to test**: maybe PWG or PWK has equal or greater digital investment, just less visible. Worth showing in the same chart.

---

## 4. CDSL-added features inventory (post-print enhancements)

The user's insight: "We are adding features, like Dictionary to Book links, that were not present in the original dictionary."

### 4.1 Catalogue of added features

| Feature | What it does | When added | Coverage |
|---|---|---|---|
| **Dictionary→Book linking** | Entry → scan page of printed source | ongoing 2014-now | uneven (MW high, others lower) |
| **Cross-dictionary lookup** | Same lemma → entries in other CDSL dicts | ongoing | partial via alternateheadwords |
| **Devanagari rendering at runtime** | SLP1 → Devanagari display | mature | universal via csl-devanagari |
| **Inflected-form lookup** | Surface forms → lemma | partial | csl-inflect (MW only mostly) |
| **API access** | RESTful query over all dicts | mature | csl-apidev |
| **Mobile/desktop app** | Native UI surfacing dicts | newer | csl-app (Flutter) |
| **Search across dicts** | One query → many results | mature | csl-websanlexicon (web), csl-app (mobile) |
| **Per-issue correction workflow** | Track + fix errors via GitHub issues | mature, formalised by runbook | universal across 35 dicts |
| **Roundtrip-encoding validation** | SLP1 ↔ IAST ↔ Devanagari | partial | implemented for some dicts |
| **JSON export** | Machine-readable dict export | mature | csl-json |
| **SQLite distribution** | Compiled queryable DB | mature | csl-sqlite |
| **Stardict / Babylon export** | Conversion for offline dict apps | mature | cologne-stardict |
| **Lemma normalisation index** | Patel-style normalised headword index | new | hwnorm1, hwnorm2 |
| **Headword variant index** | All known spelling variants per lemma | new | alternateheadwords |
| **Literary-source link resolver** | `<ls>` → external scan of cited text | new | csl-lslink |
| **Atharvaveda / Rigveda hymn pages** | Display individual hymns linked from dict citations | new | avlinks, rvlinks |
| **Pipeline DAG** | Orchestrated data-flow for builds | mature | csl-pywork |
| **Tooling-runbook** | Standardised issue taxonomy across all repos | new (2026, this project) | universal |
| **Live observatory** | Cross-repo metrics dashboard | external sibling project | csl-observatory |

### 4.2 Per-dict feature coverage matrix

35 dicts × ~20 features = a presence/absence matrix. Compute coverage % per dict and per feature.

**Expected patterns**:
- MW = highest feature coverage (everything)
- PWG/PWK/MD/AP = high coverage (most features)
- Specialised dicts = lower (scope-limited)
- Russian dicts (KNA, KOW) = currently lowest (recent additions, less integrated)

This becomes a heatmap chart on the dashboard.

---

## 5. Roadmap for data-structure evolution

**Where we are**: most dicts at L4-L6; 44 dicts (mw, pwg, ap90, wil, cae, bor, fri, ieg, armh, krm, abch, pgn, snp, acsj, acph, bur, stc, vcp, ae, bhs, gra, ben, gst, inm, lan, mci, mw72, mwe, nybj, pe, shs, yat, bop, ap, ccs, lrv, md, sch, pw, pwkvn, pui, vei, acc, skd) at entry-level L8 under the atlas scan URL builder (H2368 census, A11 + A12 + A07 + A08 + A08 follow-up + H3695 + H3725; 99.97% of all entries atlas-resolvable as of 03-09-2026).
**Where we want to be**: all dicts at L8+ minimum; flagship dicts at L9-L10.

### 5.1 Target end-state (5-year horizon)

For every CDSL dictionary:

- [ ] **L8 minimum**: every entry linked to scan page — **measured 07-08-2026, re-measured 24-08-2026 (H2368, A10 ap90 letter-marker fix; A11 12-dict scan-dir extension; A11 follow-up ap90 digit-marker fix), re-measured 28-08-2026 twice (A12 6-dict scan-dir extension; A07 11-dict scan-dir extension + gra unseparated-column fix):** local csl-orig **1,506,391** entries (A12 measured 1,496,157 — acc/ap/ben landed in csl-orig between the measurements) · **1,506,390** with non-empty `<pc>` (**99.9999%**) · **963,510** atlas-resolvable Cologne scan URLs (**63.96%**, up from 48.11%; **32** dicts in `COLOGNE_SCAN_DIR`: mw, pwg, ap90, wil, cae, bor, fri, ieg, armh, krm, abch, pgn, snp, acsj, acph, bur, stc, vcp, ae, bhs, gra, **ben, gst, inm, lan, mci, mw72, mwe, nybj, pe, shs, yat**). ap90 reached 100% in two steps: A10 taught `scanPageFromPc` its page-column-letter `NNNN-a/b/c` shape, then the follow-up taught it the page-column-digit `NNNN-N` shape (e.g. `0220-1`, `0351-2`) seen at new-letter section breaks — same reasoning, the trailing chunk is a column marker, not a volume. A11 extended `COLOGNE_SCAN_DIR` 3 → 15 via bare-integer `<pc>` dicts; **A12 (`/drain` bucket A, OxAlpha `x-preview-f-free`, 28-08-2026) extended 15 → 21 with bur/stc/vcp/ae/bhs/gra (~136k entries):** each dict's own `<dict>-meta2.txt` in csl-orig documents `<pc>` as a page-col reference with continuous page numbering and **no volume component** (only PWG carries vol-Spalte — kosha `scan_resolver.MULTI_VOLUME_DICTS = {pwg}`, H839), so the existing single-volume `scanPageFromPc` paths apply verbatim (page = first comma-field; vcp's dash-letter variant strips the same way); `csl-websanlexicon/v02/redo_cologne_all.sh` maps all six to `{DICT}Scan/2020`; each was live spot-checked with one `servepdf.php` fetch on a real mid-dict `<pc>` page, sequential WebFetch (ae and gra needed one retry each after transient transport errors — endpoint answered on the second attempt). `nmmb` still out (broken probe, A11). **A07 (roadmap-drain bucket A, OxAlpha opencode glm-5.3-flash, 28-08-2026) extended 21 → 32 with ben/gst/inm/lan/mci/mw72/mwe/nybj/pe/shs/yat (~244k entries) and resolved gra's 23 `NNNa` stragglers — gra now 100%:** each dict's `<pc>` first comma-field grows like a real continuous page number (hundreds of distinct values per dict) and its `-meta2.txt` documents a page-col reference with no volume component, so the existing single-volume `scanPageFromPc` paths apply verbatim; `csl-websanlexicon/v02/redo_cologne_all.sh` maps all eleven to `{DIR}Scan/2020`; one sequential `servepdf.php` live spot-check per dict on a real mid-dict `<pc>` page — every endpoint answered with the working scan-viewer shell embedding the real PDF path (a raw PDF-binary fetch 429s on the host's documented burst limiter; the servepdf bar is the A11/A12 precedent). `nybj` required `COLOGNE_SCAN_YEAR` 2026 per `csl-websanlexicon/v02/dictparms.py` `dictyear` — its redo-script "2020" path 404s live. The gra rule handles the unseparated page-column shape (`0307a` → page `0307`, live-verified; a census of every local dict confirmed that shape exists in no other dictionary). **Three candidates were deliberately excluded**: `pui`, `vei`, `acc` — their `<pc>` leads with a volume-like field (first field ∈ {1,2,3} / {1,2} / {1,2,3}), structurally PWG's vol-Spalte (H839); the single-volume rule would emit `?page=1..3` for every entry, and emitting no link beats emitting a silently-wrong one — each needs its own multi-volume rule + spot-check. Residuals: **ae** 99.99% (its single missing-`<pc>` entry). Dominant gap now **542,880** entries across the remaining **13** dicts with `<pc>` but no verified Cologne scan-dir map (`acc`, `ap`, `bop`, `ccs`, `lrv`, `md`, `nmmb`, `pui`, `pw`, `pwkvn`, `sch`, `skd`, `vei`) — most carry non-trivial `<pc>` shapes (volume-prefixed trio pui/vei/acc needing a multi-volume rule per the H839 reasoning; mixed-marker `N-aN` shapes in ap/bop/ccs/md; three-part vol-page-col in pw/pwkvn/skd; `lrv` `N-N.N`; `sch` `Na-N`) each needing its own `scanPageFromPc` rule plus a live spot-check before trusting it, per-dict work out of scope per pass. **A08 (`/roadmap-item-exec` bucket A, 29-08-2026, PR [#429](https://github.com/sanskrit-lexicon/csl-atlas/pull/429)) extended 32 → 33 with `bop` (~9k entries) — this pass's local csl-orig re-measured at **1,496,157** entries (matches the A12 snapshot, not the later acc/ap/ben-landed A07 snapshot of 1,506,391 — the sibling `../csl-orig` checkout used here predates that landing) · **1,496,156** with non-empty `<pc>` (**99.9999%**) · **962,240** atlas-resolvable Cologne scan URLs (**64.31%**, up from 64.31%-basis 63.96%/32-dict at the A07 snapshot's own entry count): `bop-meta2.txt` documents `<pc>` as a page-col reference with no volume component (same single-volume family, H839), and `csl-websanlexicon/v02/redo_cologne_all.sh` maps it to `BOPScan/2020`; 97.1% of its `<pc>` values already matched the existing dash-marker rule (`NNN-a`/`NNN-b`) and the remaining 2.9% are `bop-meta2.txt`'s documented "letter break" shape `[PagePPP-zC+ NN]` (digitised as `NNN-1a`/`NNN-2a`), handled by a new `scanPageFromPc` alternative — **`bop` now 100% resolvable**; live spot-check: one `servepdf.php` fetch at `page=322` returned the working scan-viewer shell embedding `bop-322.pdf`. Dominant gap now **12** dicts (`acc`, `ap`, `ccs`, `lrv`, `md`, `nmmb`, `pui`, `pw`, `pwkvn`, `sch`, `skd`, `vei`), **533,916** entries at this pass's snapshot. **A08 follow-up (`/roadmap-item-exec` bucket A, Grok 4.5 `grok-4.5`, 29-08-2026, PR [#430](https://github.com/sanskrit-lexicon/csl-atlas/pull/430)) extended 33 → 38 with `ap`/`ccs`/`lrv`/`md`/`sch` (~224k entries) — all five now 100% resolvable:** each `<pc>` first-field grows like a real continuous page number (ap 1–1768, ccs 1–541, lrv 1–839, md 1–384, sch 1–396) with no volume component; `redo_cologne_all.sh` maps ap/ccs/md/sch to `{DIR}Scan/2020` and lrv to `LRVScan/2022` (`dictparms.py` still says 2020 for lrv — nybj-class year mismatch; the live 2022 path is the one that answers). Three new `scanPageFromPc` alternatives, each live-verified: ap/md letter-then-digit (`0379-a1` / `036-a1`), sch unseparated-page-then-column (`104a-1`), lrv dotted-column (`120-12.1`); ccs's `038-1a` already matched the A08 bop letter-break rule. One sequential `servepdf.php` mid-dict probe per dict (ap `page=0923`, ccs `264`, lrv `425`, md `137`, sch `198`) plus one residual-shape probe each, all returned the working scan-viewer shell. Re-measured: local csl-orig **1,496,157** entries · **1,496,156** with non-empty `<pc>` (**99.9999%**) · **1,186,408** atlas-resolvable Cologne scan URLs (**79.30%**, up from 64.31%). Dominant gap now **7** dicts (`acc`, `nmmb`, `pui`, `pw`, `pwkvn`, `skd`, `vei`), **309,748** entries — volume-prefixed pui/vei/acc and three-part vol-page-col pw/pwkvn/skd still need their own multi-volume rule (H839); nmmb stays out (broken probe, A11). **H3695 (Atlas L8 bounded slice, OxAlpha opencode `glm-5.3-flash`, 29-08-2026, PR [#433](https://github.com/sanskrit-lexicon/csl-atlas/pull/433)) extended 38 → 40 with `pw`/`pwkvn` (~195.5k entries) — both now 100% resolvable:** the three-part vol-page-col family — `<pc>` is PWG's vol-Spalte (H839) plus a trailing column marker on the same page (`N-N-a/b/c/d` dominant; per dict 19 letter-break stragglers `7-384-1a`..`-1d` — the bop digit-then-letters class — and 1 digit-only marker `7-366-1` — the ap90 digit-marker class; vol ∈ 1..7; 100% of both dicts' `<pc>` values are that one shape family). `redo_cologne_all.sh` maps pw → `PWScan/2020` and pwkvn → `PWKVNScan/2020` (`dictparms.py` dictyear 2020 for both). servepdf.php still has no vol= parameter, so `scanPageFromPc`'s multi-volume branch now strips the trailing marker and returns `{vol}-{page}` verbatim (H839's bare-page refusal untouched; pw/pwkvn join pwg in `MULTI_VOLUME_DICTS`). Cologne was source-health-probed up (200 GO) before the fetches; live evidence, one sequential `servepdf.php` probe per dict plus one residual-marker probe: pw `page=7-385` → working scan-viewer shell embedding `pw7-385.pdf` (marker page `7-384` → `pw7-384.pdf`), pwkvn `page=2-288` → working shell embedding `pw2-288N.png`. Re-measured at this pass's sibling-csl-orig snapshot: **1,506,391** entries (the acc/ap/ben-landed snapshot, +10,234 rows of upstream drift vs the A08-follow-up run's 1,496,157) · **1,506,390** with non-empty `<pc>` (**99.9999%**) · **1,392,174** atlas-resolvable Cologne scan URLs (**92.42%**, up from 79.30%). Dominant gap now **5** dicts (`acc`, `nmmb`, `pui`, `skd`, `vei`), **114,216** entries — volume-prefixed pui/vei/acc and skd (same vol-page-col family as pw/pwkvn) still need their own multi-volume rule + live spot-check (H839); nmmb stays out (broken probe, A11). Residual: **ae** 11,358/11,359 (its single missing-`<pc>` entry). **Not L8-complete.** **Re-measured 01-09-2026 (H3779, Sonnet 5 `claude-sonnet-5`):** fresh `csl-orig` sibling checkout (pulled to `origin/main`, was 6 commits/8 weeks stale locally) re-ran `scripts/metalex/l8_scan_link_census.py` — **1,506,391** entries · **1,506,390** with non-empty `<pc>` (**99.9999%**) · **1,392,174** atlas-resolvable Cologne scan URLs (**92.42%**) — identical to the H3695 snapshot: **stable, no drift**, same **5**-dict gap (`acc`, `nmmb`, `pui`, `skd`, `vei`, 114,216 entries). Those five are the scope of [H3725 (Grok 4.6, 🟡2 medium) — Atlas L8 next multivolume dicts nmmb/pui/vei/acc/skd](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3725-Grok_csl-atlas_l8-nmmb-pui-vei-acc-skd-scan_30.08.26.md), not this re-measurement pass. **H3725 (Atlas L8 next multivolume dicts, OxAlpha opencode `glm-5.3-flash`, 03-09-2026) extended 40 → 44 with `pui`/`vei`/`acc`/`skd` (113,710 entries) — all four now 100% resolvable:** all four join the multi-volume family (`MULTI_VOLUME_DICTS`, H839). `redo_cologne_all.sh` maps all four to `{DICT}Scan/2020` (`dictparms.py` dictyear 2020 — no `COLOGNE_SCAN_YEAR` entry). `<pc>` shape-pure per dict: pui 17,512 values all `{vol}-{page}` (vol 1..3, pages 1–786) and vei 3,834 all `{vol}-{page}` (vol 1..2, pages 1–543) — the pwg verbatim path unchanged; acc 49,833 all `{vol}-{page},{col}` (vol 1..3, pages 1–795) — new MV comma-column alternative strips the trailing chunk (`1-618,1` → `1-618`); note the H839 trap acc would have walked into under the single-volume rule: its first comma-field `1-618` matches the page-column-marker regex and would return `1` — volume-as-page for every entry — the `MULTI_VOLUME` gate is what makes acc resolvable at all; skd 42,531 all three-part vol-page-col (vol 1..5, pages 1–937) — pw/pwkvn's family with 30 letter-break stragglers `2-486-a1`..`-b1`/`-c1` whose tail is letters-then-digit (the ap/md letterThenDigit class on the MV tail, new alternative → `2-486`). Cologne live evidence 03-09-2026, one sequential probe per dict plus the embedded-pdf HTTP check and one residual-shape probe: pui `page=2-444` → viewer shell embedding `pg2_444.pdf` (HTTP 200), vei `page=2-015` → `pg2_015.pdf` (200), acc `page=1-618` → `pg1_618.pdf` (200), skd `page=3-122` → `pg3_122.pdf` (200) + straggler page `2-486` → `pg2_486.pdf`. `nmmb` re-tried and stays out with a deeper breakage: the `NMMBScan/2026` servepdf.php shell now answers 200 (A11's flat failure has healed) but **every embedded pdf it names 404s** (`pdfpages/pg0001/0020/0100.pdf` and the `NMMBScanpdf/` variant) — the scan images behind the tree are absent, and a shell-only pass would be the silently-wrong-link failure mode; needs upstream scan images, not an atlas rule. Re-measured at the current sibling-csl-orig `origin/main` snapshot: **1,506,391** entries · **1,506,390** with non-empty `<pc>` (**99.9999%**) · **1,505,884** atlas-resolvable Cologne scan URLs (**99.97%**, up from 92.42%). Dominant gap now **1** dict: `nmmb`, **506** entries (missing scan images). Residual: **ae** 11,358/11,359 (its single missing-`<pc>` entry) plus one other missing-`<pc>` row elsewhere. **L9/L10 unchanged (0%, no infra) — neither box clears.** Report: [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md).
- [ ] **L9 stretch**: cross-dict linking active for every shared lemma
- [ ] **L10 aspirational**: external `csl-standards` export available; queryable via SPARQL

### 5.2 Per-level uplift recipes

| From → To | Required work | Effort estimate |
|---|---|---|
| L0 → L1 | OCR or keyboard the text | weeks per dict |
| L1 → L2 | Add `<L>NNNN` boundaries via regex on source | hours per dict |
| L2 → L3 | Identify and tag `<k1>` and `<k2>` headwords | days per dict |
| L3 → L4 | Tag lexical categories (often present in source as abbreviations like `m.`, `f.`, `n.`) | days |
| L4 → L5 | Identify literary-source citations and wrap in `<ls>` | weeks |
| L5 → L6 | Detect and structure senses (often by `1.`, `;`, `2.` patterns) | weeks |
| L6 → L7 | Detect cross-references and mark | days-weeks |
| L7 → L8 | Match each entry to scan-page coordinates | months — **coordinates almost done** (`<pc>` ≈100% per H2368); **ap90 at 100% resolvable (A10 + A11 follow-up, 24-08-2026)**; **12 more dicts (wil/cae/bor/fri/ieg/armh/krm/abch/pgn/snp/acsj/acph) verified + live-spot-checked (A11, 24-08-2026)**; **6 more (bur/stc/vcp/ae/bhs/gra) verified + live-spot-checked (A12, 28-08-2026 — 21 dicts, 48.11% of entries)**; **A07 (28-08-2026) added 11 more (ben/gst/inm/lan/mci/mw72/mwe/nybj/pe/shs/yat, live-spot-checked) and fixed gra's 23 unseparated-`NNNa` stragglers — 32 dicts, 63.96% of entries**; **A08 (29-08-2026) added `bop` and a new letter-break-marker rule, `bop` now 100% resolvable — 33 dicts, 64.31% of this pass's entries**; **A08 follow-up (29-08-2026) added `ap`/`ccs`/`lrv`/`md`/`sch` (letter-then-digit, sch unseparated-then-col, lrv dotted-column; lrv year 2022) — 38 dicts, 79.30% of this pass's entries**; **H3695 (29-08-2026) added `pw`/`pwkvn` (three-part vol-page-col, trailing marker stripped to `{vol}-{page}` per H839; live-probed `pw7-385.pdf` / `pw2-288N.png`) — 40 dicts, 92.42% of entries**; **H3725 (03-09-2026) added `pui`/`vei`/`acc`/`skd` to the multi-volume family (pui/vei vol-page verbatim; acc comma-column `1-618,1` → `1-618`; skd three-part incl. 30 letters-then-digit stragglers `2-486-a1` → `2-486`; all live-probed with embedded-pdf HTTP checks) — 44 dicts, 99.97% of entries**; remaining work is the upstream scan images for `nmmb` (506 entries; viewer shell live but every pdf 404s — not an atlas-rule gap) |
| L8 → L9 | Build cross-dict lemma matching | new infrastructure |
| L9 → L10 | external TEI/RDF conversion + SPARQL endpoint | `csl-standards` infrastructure |

### 5.3 Recommended priority by dict family

1. **First wave** (already at L7-L8): finish L8 for AP, AP90, PWG, PWK
2. **Second wave** (at L4-L6): bring SCH, CCS, CAE, MD, WIL, BHS up to L7
3. **Third wave** (at L2-L4): bring specialised dicts (VEI, INM, MCI) to L5
4. **Fourth wave** (at L0-L1): ingest scan-only dicts (PD, MWE, etc.) and bring to L3

### 5.4 Engineering investments needed

- **Standard schema**: hand off atlas evidence to `csl-standards` for unified TEI/OntoLex profile work
- **Migration scripts**: per-source-dict converters to the unified schema
- **Validation harness**: continuous integration that flags schema violations
- **Cross-dict link infrastructure**: new tooling for L9 (extending alternateheadwords + csl-lslink)
- **SPARQL endpoint**: new infrastructure for L10
- **Editorial UI**: more accessible than git+text for non-engineer contributors

---

## 6. Hypothesis: KOW = Russian translation of WIL

**Claim** (M.G. domain knowledge): KOW (Kossowich, ~1854) is a Russian translation/adaptation of WIL (Wilson, 1832).

**Temporal plausibility**: WIL 1832 → KOW ~1854 = 22-year gap. Plausible.

### 6.1 Convergent evidence to gather

| Evidence | Method | Strength |
|---|---|---|
| Lemma-set Jaccard (WIL ∩ KOW) | set comparison after Patel normalisation | strong if >0.95 |
| Lemma-set order preservation | per-letter ordering | medium |
| Sense-count parallelism | for shared lemmas, do KOW glosses match WIL sense-count? | strong if matches |
| Translation correspondence | machine-translate WIL English → Russian, compare to KOW Russian | strong if >0.7 cosine |
| Citation set similarity (language-neutral) | compare `<ls>` sets | medium |
| Citation order preservation | `<ls>` sequence per entry | strong if matches |
| Forensic typo / OCR-error sharing | rare cross-dict error pairs | strongest if found |
| Page-correspondence | KOW's page numbering related to WIL's? | medium |
| Editorial preface evidence | does KOW preface mention Wilson? | check Cologne scan |

### 6.2 Phase L1.5 (KOW⇄WIL focused study)

A targeted mini-study to test the WIL→KOW hypothesis:
1. Parse both dicts to lemma → glosses → citations
2. Compute the 8 evidence metrics above
3. Bayesian combine into single posterior P(WIL → KOW | evidence)
4. Publish: dashboard chart + paper paragraph in Paper L §6
5. If confirmed: KOW becomes the test-case for cross-language inheritance methodology — applicable to other unknown pairs (e.g. is BUR a French translation of any specific source?)

**Output**: `data/wil_kow_evidence.csv` + a side-by-side display widget on the dashboard.

---

## 7. The "MW gets all the attention" study (parallel to L0)

A specific cross-cutting analysis using all the metalexicography KPIs from §2-§4.

### 7.1 Charts to produce

1. **Single radar chart per dict** with normalised KPIs (markup density, citation richness, cross-ref count, Dictionary-to-Book coverage, downstream surface area). MW's polygon should encompass others.
2. **30-year attention timeline** for MW vs PWG vs AP: commits + issues per year, side-by-side
3. **Feature coverage heatmap**: 35 dicts × 20 added-by-CDSL features
4. **Investment-equivalent chart**: each dict's volunteer-hours estimate (from Phase A) divided by entry count → "minutes invested per entry"

### 7.2 Expected paper findings

- MW's per-entry investment is 5-10× the median dict
- MW is the ONLY dict at L8 (full Dictionary→Book linking) — **superseded H2368, re-measured A10+A11 24-08-2026, A12 + A07 28-08-2026:** 32 dicts (mw, pwg, wil, cae, bor, fri, ieg, armh, krm, abch, pgn, snp, acsj, acph, bur, stc, vcp, ae, bhs, gra, ben, gst, inm, lan, mci, mw72, mwe, nybj, pe, shs, yat; all at ~100% except ae 99.99%) are atlas-resolvable; print coordinates are near-universal; working scan URLs for the remaining 13 dicts are the bottleneck (63.96% overall)
- MW has the deepest XML markup
- MW is referenced in the most other CDSL repos
- BUT: PWG has comparable per-entry investment when normalised (it's foundational)

This becomes the **opening paragraph of Paper L §6** — empirically substantiating an oft-stated but never-quantified claim.

---

## 8. Implementation phases (added to lexicography stream)

| Phase | Name | Effort | Output |
|---|---|---|---|
| **L0** | Convention fingerprint cladogram | ~5d | first phylogenetic tree (already designed) |
| **L1.5** | KOW⇄WIL focused study | ~3d | proof of WIL→KOW + cross-language methodology validation |
| **M1** | Data-richness typology assignment | ~3d | every dict placed on L0-L10 scale |
| **M2** | Markup density KPIs | ~3d | the 30 KPIs in §2 |
| **M3** | "MW gets all the attention" study | ~2d | radar charts + investment timeline |
| **M4** | Added-features inventory matrix | ~2d | 35×20 coverage heatmap |
| **M5** | Data-structure evolution roadmap recommendations per dict | ~3d | actionable per-dict uplift plan |
| **M6** | External standards handoff | ~5d | compact atlas evidence for `csl-standards` |

Total metalexicography stream: ~21 days (3 weeks active work, spread across 6 months).

---

## 9. New paper opportunity: Paper E

**Paper E** — *Engineering an open digital lexicographic infrastructure: the CDSL data-richness story*

Audience: digital infrastructure venues (Dlib Magazine, IJDL, JCDL), TEI consortium, lexicography community.

Contribution: Documenting the technical evolution of 35 dictionaries from scan-only PDFs to integrated digital infrastructure, with the data-richness typology as the measurement framework.

Sections:
1. Introduction — digital editions as data infrastructure (not just text)
2. Related work — TEI Lex-0, FAIR principles for lexical data
3. The 10-level data-richness typology (proposed)
4. Application to CDSL: which dicts are at which level and why
5. The MW exception: why one dict received disproportionate investment
6. Added features inventory: what CDSL added beyond the printed originals
7. The roadmap: where each dict should be in 5 years
8. Discussion: lessons for other DH infrastructure projects
9. Conclusion

Length: 15-20 pages, fits IJDL well.

---

## 10. Decisions locked (2026-05-16 round 3)

| Question | Decision |
|---|---|
| L10 target schema | Atlas keeps native dictionary evidence; `csl-standards` owns TEI Lex-0 and OntoLex-Lemon exports. |
| L0 vs L1.5 ordering | **Parallel**: L0 (convention fingerprint, no XML needed) and L1.5 (KOW⇄WIL focused study, needs XML) run on independent code paths simultaneously |
| Paper E status | **Merged into Paper M** as the data-quality treatment. Paper M expands to: KPI catalog + measurement framework + data-quality typology. One stronger methodological paper instead of two competing ones |
| CDSL-added features inventory | **Augment via Cologne-site scrape**: GitHub repos miss runtime/UI-only features. New phase **M0a** (web scrape of sanskrit-lexicon.uni-koeln.de pages) feeds the §4 inventory |

## 11. New Phase M0a — Cologne web feature scrape (~1 day)

Discover runtime / UI / display-layer features not visible from GitHub source alone.

### What to fetch
- Top-level `https://www.sanskrit-lexicon.uni-koeln.de/`
- Per-dict display URLs (e.g. `/scans/MWScan/2014/web/`, `/monier/indexcaller.php`)
- API endpoints (`/scans/csl-apidev/...`)
- Display-tool URLs (transcoder, search, simple-search)
- Documentation pages (csldoc, where reachable)

### What to extract
- List of distinct dictionary display interfaces (each = one CDSL-added "display-layer feature")
- Search-tool variants (simple-search, advanced, fuzzy, glob, etc.)
- Mobile/desktop integration mentions
- Acknowledged contributor list (for `people.yaml` enrichment)
- Any documentation of dictionary derivation (lineage ground truth)

### Output
- `data/cologne_features.csv` — feature presence per dict from the live site
- `data/cologne_acknowledgments.csv` — credited people from the site
- Updates to §4.1 features inventory

## 12. Updated Paper M outline (now incorporating Paper E content)

**Paper M (revised)**: *A measurement framework for digital lexicography: KPI catalog, data-quality typology, and the CDSL case*

The framework has now **two contributions** rolled into one paper:
1. The KPI catalog (4 dimensions × 30+ metrics, original Paper M scope)
2. The data-richness typology (L0-L10, originally Paper E scope) with worked example

Total length: ~25 pages (longer than original M, but more substantive). Sections:
- §1 Introduction (rolled hooks: measurement gap + data-richness story)
- §2 Related work (added: TEI Lex-0, OntoLex-Lemon, CHAOSS, GHOST)
- §3 Method part A — KPI catalog (the original Paper M)
- §4 Method part B — Data richness typology L0-L10 (the original Paper E)
- §5 Worked example: CDSL — KPIs + richness levels
- §6 The MW exception (the §3 hypothesis from this doc)
- §7 Discussion: how data quality conditions all measurement
- §8 Recommendations + future work
- §9 Conclusion

## 13. Updated phase plan (parallel L0 + L1.5 + M0a)

Three phases run in parallel from session 1:

| Phase | Code path | Effort | Output |
|---|---|---|---|
| **L0** | `lexico/conventions.py` | ~5d | 27-tree cladogram + validation |
| **L1.5** | `lexico/wil_kow.py` | ~3d | KOW⇄WIL evidence matrix + posterior |
| **M0a** | `lexico/cologne_scrape.py` | ~1d | Cologne site features inventory |

After all three complete:
- **M1-M5** (richness KPIs, MW study, evolution roadmap) draw on L0 and M0a outputs
- **L1-L9** (full corpus mining) is the next major branch
- **Paper M** drafting begins after L0 + M1 + M3 produce data

## 13b. Locked execution details (2026-05-16 round 4)

| Question | Decision |
|---|---|
| L1.5 Russian-text handling | **All three signals combined** in Bayesian posterior: (a) lemma + citation set overlap (language-neutral); (b) machine-translate WIL English→Russian, cosine vs KOW; (c) machine-translate KOW Russian→English, cosine vs WIL |
| Annotation provenance | **File-level metadata header** in each CSV: annotators (name + ORCID), date created, dimensions covered. No per-cell tracking |
| First-cladogram sharing | **Commit + GH Actions redeploy + dashboard link**. Full pipeline, public viewing at `/lexicography/conventions/` |
| Execution start | **HOLD** — more design pending |

## 14. Dictionary-Schema Handoff Strategy (per decision §10)

Atlas owns the native dictionary-evidence side only. External publication
schemas are handoff targets for `csl-standards`, not atlas deliverables.

### Native schema, external exports

#### Native CDSL schema (`csl-schema/v1.xsd`)
- Captures everything: Patel-normalised headwords, citation tags, sense structure, scan-page links, cross-dict refs, all CDSL-specific features
- Authoritative; XML source files convert to this
- Validation harness in CI

#### TEI Lex-0 handoff (`csl-standards`)
- Atlas may provide dictionary evidence and mapping notes.
- `csl-standards` owns any TEI generator, validation profile, and publication
  decision.

#### OntoLex-Lemon handoff (`csl-standards`)
- Atlas may provide dictionary evidence and loss-case examples.
- `csl-standards` owns RDF/JSON-LD stress tests, SHACL validation, and any
  future RDF publication.

### Phase plan for atlas-side schema work (post-L0/L1.5)

| Phase | Output |
|---|---|
| **M6a** — Native schema design | XSD + documentation + per-dict mapping notes |
| **M6b** — Standards handoff notes | Dictionary evidence and known loss cases for `csl-standards` |
| **M6c** — Boundary check | Confirm no TEI/OntoLex/RDF generation is added to atlas scripts |

_Dr. Mārcis Gasūns_
