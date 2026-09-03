# METALEX L8 — entry-level scan-page link census

_Created: 07-08-2026 · Last updated: 03-09-2026_

**Handoff:** [H2368](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2368-Grok_csl-atlas_metalex-l8-scan-link-census_07.08.26.md) · **Model:** Grok 4.5 (grok-4.5) · **Generated:** 2026-09-03T12:46:38Z · **Rerun:** Sonnet 5 (claude-sonnet-5), A10 (H2368 ap90 pc-shape fix), A11 (12-dict COLOGNE_SCAN_DIR extension), A11-followup (ap90 digit-marker fix), A12 (bur/stc/vcp/ae/bhs/gra 6-dict extension, OxAlpha x-preview-f-free), A07 (ben/gst/inm/lan/mci/mw72/mwe/nybj/pe/shs/yat 11-dict extension + gra unseparated-column fix, OxAlpha opencode glm-5.3-flash), A08 (bop 1-dict extension + letter-break-marker fix), A08 follow-up (ap/ccs/lrv/md/sch 5-dict extension + letter-then-digit / sch unseparated-then-col / lrv dotted-column rules, Grok 4.5 grok-4.5), H3695 (pw/pwkvn three-part vol-page-col extension, OxAlpha opencode glm-5.3-flash), H3725 (pui/vei/acc/skd multi-volume extension + acc comma-column / skd letters-then-digit-tail rules, OxAlpha opencode glm-5.3-flash)

## Headline

| Metric | n | of total | % |
|---|---:|---:|---:|
| Entries in scope (local csl-orig) | 1,506,391 | — | 100 |
| With non-empty `<pc>` (print coordinate) | 1,506,390 | 1,506,391 | **100.00** |
| Atlas-resolvable Cologne scan URL | 1,505,884 | 1,506,391 | **99.97** |

**L8 complete?** **No.** Do not claim L8 complete: print coordinates are nearly universal, but 1 dicts with <pc> data still have no verified Cologne scan-dir map (506 entries), so a working scan URL resolves for 99.97% of entries under the atlas's verified dict→scan-dir map.

## Method

- **Denominator:** Every <L>… header line in each local csl-orig/v02/<code>/<code>.txt
- **Numerator A (`with_pc`):** Entry header contains non-empty <pc>… (print page/column coordinate)
- **Numerator B (`atlas_resolvable_scan`):** Entry would get a non-null cologne-links.mjs scanUrl(dict, pc) — dict ∈ COLOGNE_SCAN_DIR (44 dicts as of H3725) AND pc passes scanPageFromPc (PWG/pui/vei: /^\d+-\d+$/ verbatim; pw/pwkvn/skd: three-part vol-page-col marker-stripped to vol-page, skd tail may be letters-then-digit; acc: vol-page,col comma-column stripped to vol-page; others: first comma-field is digits-only, page-marker, unseparated page+column-letters, letter-then-digit, unseparated-page-then-column, or dotted-column)
- **Scan-link field:** <pc> in csl-orig entry header (not <bookref>; roadmap alias)
- **Verified `COLOGNE_SCAN_DIR`:** `{'mw': 'MW', 'pwg': 'PWG', 'ap90': 'AP90', 'wil': 'WIL', 'cae': 'CAE', 'bor': 'BOR', 'fri': 'FRI', 'ieg': 'IEG', 'armh': 'ARMH', 'krm': 'KRM', 'abch': 'ABCH', 'pgn': 'PGN', 'snp': 'SNP', 'acsj': 'ACSJ', 'acph': 'ACPH', 'bur': 'BUR', 'stc': 'STC', 'vcp': 'VCP', 'ae': 'AE', 'bhs': 'BHS', 'gra': 'GRA', 'ben': 'BEN', 'gst': 'GST', 'inm': 'INM', 'lan': 'LAN', 'mci': 'MCI', 'mw72': 'MW72', 'mwe': 'MWE', 'nybj': 'NYBJ', 'pe': 'PE', 'shs': 'SHS', 'yat': 'YAT', 'bop': 'BOP', 'ap': 'AP', 'ccs': 'CCS', 'lrv': 'LRV', 'md': 'MD', 'sch': 'SCH', 'pw': 'PW', 'pwkvn': 'PWKVN', 'pui': 'PUI', 'vei': 'VEI', 'acc': 'ACC', 'skd': 'SKD'}` (from [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs))
- **vs richness typology L8:** scripts/build-richness-typology.mjs L8 is DICT-level (sourceCode ∈ COLOGNE_SCAN_DIR). This census is ENTRY-level coverage. A dict can be typology L8=true while atlas_resolvable_pct < 100% if pc shapes fail scanPageFromPc (observed for ap90).

### Non-goals

- No mass link invention
- No extension of COLOGNE_SCAN_DIR without live spot-check confirmation (A11: single sequential WebFetch probes per candidate dict, not a bulk crawl)
- L9/L10 out of scope

## Gap buckets

| Bucket | Entries | Meaning |
|---|---:|---|
| `missing_pc` | 1 | Header has no non-empty `<pc>` |
| `pc_present_no_cologne_scan_dir` | 506 | `<pc>` present but dict not in atlas `COLOGNE_SCAN_DIR` (no verified Cologne scan URL builder) |
| `pc_unparseable_for_atlas_scan_url` | 0 | Dict is in `COLOGNE_SCAN_DIR` but `scanPageFromPc` returns null (pc shape not trusted by the atlas builder) |

### Dict-level sets

- **`<pc>` coverage 100%:** 44 dicts (not 100%: `ae`)
- **In atlas `COLOGNE_SCAN_DIR`:** `abch, acc, acph, acsj, ae, ap, ap90, armh, ben, bhs, bop, bor, bur, cae, ccs, fri, gra, gst, ieg, inm, krm, lan, lrv, mci, md, mw, mw72, mwe, nybj, pe, pgn, pui, pw, pwg, pwkvn, sch, shs, skd, snp, stc, vcp, vei, wil, yat`
- **Atlas-resolvable 100%:** `abch, acc, acph, acsj, ap, ap90, armh, ben, bhs, bop, bor, bur, cae, ccs, fri, gra, gst, ieg, inm, krm, lan, lrv, mci, md, mw, mw72, mwe, nybj, pe, pgn, pui, pw, pwg, pwkvn, sch, shs, skd, snp, stc, vcp, vei, wil, yat` (ap90 reached 100% in two steps: page-column-letter shape `NNNN-a/b/c` stripped to the page — H2368-A10 fix; then the page-column-digit shape `NNNN-N` seen at new-letter section breaks, e.g. `0220-1`, `0351-2` — H2368-A11 follow-up, same reasoning: the trailing chunk is a column marker, not a volume)
- **In scan-dir map but not 100% resolvable:** `ae`
- **Not in scan-dir map:** 1 dicts (dominant gap — coordinates exist; atlas has no verified servepdf map)

## Per-dictionary table

| code | entries | with_pc | pc% | atlas_scan | atlas% | in_scan_dir | top pc shapes |
|---|---:|---:|---:|---:|---:|:---:|---|
| mw | 286,525 | 286,525 | 100.00 | 286,525 | 100.00 | yes | `N,N`×286524, `N,Nx`×1 |
| pw | 170,556 | 170,556 | 100.00 | 170,556 | 100.00 | yes | `N-N-b`×55765, `N-N-a`×55627, `N-N-c`×55445 |
| pwg | 123,366 | 123,366 | 100.00 | 123,366 | 100.00 | yes | `N-N`×123366 |
| ap | 90,847 | 90,847 | 100.00 | 90,847 | 100.00 | yes | `N-N`×90098, `N-aN`×693, `N-bN`×50 |
| mw72 | 55,390 | 55,390 | 100.00 | 55,390 | 100.00 | yes | `N-a`×18569, `N-c`×18519, `N-b`×18302 |
| lrv | 53,440 | 53,440 | 100.00 | 53,440 | 100.00 | yes | `N-N`×53220, `N-N.N`×220 |
| vcp | 50,135 | 50,135 | 100.00 | 50,135 | 100.00 | yes | `N,b`×25267, `N,a`×24868 |
| acc | 49,833 | 49,833 | 100.00 | 49,833 | 100.00 | yes | `N-N,N`×49833 |
| shs | 47,326 | 47,326 | 100.00 | 47,326 | 100.00 | yes | `N-a`×23988, `N-b`×23338 |
| yat | 45,206 | 45,206 | 100.00 | 45,206 | 100.00 | yes | `N-b`×22652, `N-a`×22554 |
| wil | 44,577 | 44,577 | 100.00 | 44,577 | 100.00 | yes | `N`×44577 |
| skd | 42,531 | 42,531 | 100.00 | 42,531 | 100.00 | yes | `N-N-a`×14334, `N-N-c`×14321, `N-N-b`×13841 |
| cae | 40,069 | 40,069 | 100.00 | 40,069 | 100.00 | yes | `N`×40069 |
| ap90 | 34,882 | 34,882 | 100.00 | 34,882 | 100.00 | yes | `N-b`×11574, `N-c`×11532, `N-a`×11530 |
| mwe | 32,378 | 32,378 | 100.00 | 32,378 | 100.00 | yes | `N-b`×16389, `N-a`×15989 |
| ccs | 30,010 | 30,010 | 100.00 | 30,010 | 100.00 | yes | `N-N`×29099, `N-Na`×844, `N-Nc`×32 |
| sch | 29,125 | 29,125 | 100.00 | 29,125 | 100.00 | yes | `N-N`×28610, `Na-N`×515 |
| ben | 25,062 | 25,062 | 100.00 | 25,062 | 100.00 | yes | `N-a`×12619, `N-b`×12443 |
| pwkvn | 24,976 | 24,976 | 100.00 | 24,976 | 100.00 | yes | `N-N-b`×7119, `N-N-a`×7110, `N-N-c`×7034 |
| bor | 24,609 | 24,609 | 100.00 | 24,609 | 100.00 | yes | `N`×24609 |
| stc | 24,574 | 24,574 | 100.00 | 24,574 | 100.00 | yes | `N,N`×24574 |
| md | 20,749 | 20,749 | 100.00 | 20,749 | 100.00 | yes | `N-N`×19954, `N-aN`×750, `N-cN`×28 |
| bur | 19,776 | 19,776 | 100.00 | 19,776 | 100.00 | yes | `N,N`×19776 |
| bhs | 17,839 | 17,839 | 100.00 | 17,839 | 100.00 | yes | `N,N`×17839 |
| pui | 17,512 | 17,512 | 100.00 | 17,512 | 100.00 | yes | `N-N`×17512 |
| gra | 12,785 | 12,785 | 100.00 | 12,785 | 100.00 | yes | `N`×12493, `N-b`×138, `N-a`×131 |
| inm | 12,647 | 12,647 | 100.00 | 12,647 | 100.00 | yes | `N-N`×12647 |
| ae | 11,359 | 11,358 | 99.99 | 11,358 | 99.99 | yes | `N`×11358 |
| bop | 8,961 | 8,961 | 100.00 | 8,961 | 100.00 | yes | `N-a`×4433, `N-b`×4269, `N-Na`×139 |
| pe | 8,799 | 8,799 | 100.00 | 8,799 | 100.00 | yes | `N-a`×4444, `N-b`×4355 |
| fri | 8,155 | 8,155 | 100.00 | 8,155 | 100.00 | yes | `N`×8155 |
| ieg | 7,932 | 7,932 | 100.00 | 7,932 | 100.00 | yes | `N`×7932 |
| armh | 7,907 | 7,907 | 100.00 | 7,907 | 100.00 | yes | `N`×7907 |
| gst | 6,780 | 6,780 | 100.00 | 6,780 | 100.00 | yes | `N-b`×3406, `N-a`×3374 |
| lan | 4,944 | 4,944 | 100.00 | 4,944 | 100.00 | yes | `N-a`×2511, `N-b`×2433 |
| vei | 3,834 | 3,834 | 100.00 | 3,834 | 100.00 | yes | `N-N`×3834 |
| mci | 2,643 | 2,643 | 100.00 | 2,643 | 100.00 | yes | `N-a`×1324, `N-b`×1319 |
| nybj | 2,479 | 2,479 | 100.00 | 2,479 | 100.00 | yes | `N`×2479 |
| krm | 2,061 | 2,061 | 100.00 | 2,061 | 100.00 | yes | `N`×2061 |
| abch | 1,965 | 1,965 | 100.00 | 1,965 | 100.00 | yes | `N`×1965 |
| nmmb | 506 | 506 | 100.00 | 0 | 0.00 | no | `N`×506 |
| pgn | 485 | 485 | 100.00 | 485 | 100.00 | yes | `N`×485 |
| snp | 453 | 453 | 100.00 | 453 | 100.00 | yes | `N`×453 |
| acsj | 240 | 240 | 100.00 | 240 | 100.00 | yes | `N`×240 |
| acph | 163 | 163 | 100.00 | 163 | 100.00 | yes | `N`×163 |

## Gap list sample

| bucket | code | L | k1 | pc |
|---|---|---|---|---|
| `missing_pc` | ae | 9035.1 | `ruffian` | `` |

The mass of the gap is **dict not in `COLOGNE_SCAN_DIR`**, not missing `<pc>`. Those rows are not expanded entry-by-entry (would be ~1.2M rows and invent nothing useful).

## Reproduce

```sh
# requires sibling ../csl-orig/v02
python scripts/metalex/l8_scan_link_census.py
```

Machine-readable twin: [data/metalex/L8_SCAN_LINK_CENSUS.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.json)

_Dr. Mārcis Gasūns_
