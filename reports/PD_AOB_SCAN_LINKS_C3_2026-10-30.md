# PD siglum → AOB edition → scan-page targets — C3, 30-10-2026

_Created: 30-10-2026 · Scope: all 1,622 siglum-bearing Index rows and all 391,444 C2 `(siglum, locus)` pairs · Status: **landed as a bounded, reproducible lower-bound link layer** · Evidence: identities and aggregates **derived**, Archive.org probes **observed**, no human `reviewed` claim._

## 1. Result — three different measures

| Measure | Numerator / denominator | Share | What it establishes |
|---|---:|---:|---|
| Work identity | **1,615 / 1,622** | **99.57 %** | Index row has an H7296 `PDW-…` work identity |
| AOB edition identity | **815 / 1,622** | **50.25 %** | H7296 edition edge, or C1's explicit AOB-exact entry |
| AOB-exact scan target | **14 / 1,622 rows** | **0.86 %** | Live image URL for a C1-confirmed AOB edition |
| Locus → unique scan page | **5,639 / 23,491 AOB-exact C2 pairs** | **24.00 %** | Printed-page image resolved without a part/page ambiguity |

The 14 scan-bearing Index rows represent **13 distinct works**: `VīraMi.` occupies two printed
Index rows. The AOB-exact locus population is **23,491 of all 391,444 C2 pairs (6.00 %)**;
the 5,639 resolved pairs are **1.44 % of all C2 pairs**. This is a lower bound bounded by
C1's exact-edition evidence and by the quality of Archive.org page labels, not an absence census.

The table also retains a separate `index_scan_url` for **all 1,622 rows**. That URL opens the
printed Index row on which the siglum is transcribed; it is **not** an AOB-edition target and
is never included in the 14-row numerator.

## 2. Why edition identity is 815, not the older 981

C3 uses the conservative H7296 registry rather than the older siglum-fold delta:

- **814** rows have an H7296 `edition_of_declared_work` edge;
- **1** further row, `RasGaṅ.`, has C1's explicit `AOB-0952` exact-edition witness although the
  conservative registry has no edition edge;
- **807** rows remain unresolved.

Thus work-level availability is never silently promoted to edition identity. Conversely, the
`RasGaṅ.` row does not show the contradictory pair “edition unresolved / exact scan resolved”:
its edition basis is labelled `resolved_c1_exact` separately from the 814 registry joins.

## 3. What a scan target means

All **14 Archive.org items** behind the 13 exact-edition works returned a live
`page/n0.jpg` image probe on 30-10-2026. These are page-image URLs, not item-details pages.
Prasāda has two part items; the other works have one item each in this bounded evidence set.

For locus resolution, a URL is emitted only when all four conditions hold:

1. C2 supplies a well-formed `(siglum, locus)` pair.
2. C1 identifies the edition as `aob_exact`.
3. The AOB locus scheme contains a printed page (`Page, Line`, `Page, Śloka`, or
   `Volume, Page, Line`).
4. Either Archive.org scandata maps that page to one unambiguous leaf inside a run of at least
   three consecutive labels, or a committed visual range maps it inside a multiply anchored
   printed-page sequence.

A resolved target is a **page-level** link. It does not claim line-level placement, quotation
fidelity, or that PD's reading matches the scan. Three scandata spot checks matched
`VīraMi. n5 → 386`, `SmṛtiCan. n7 → 3`, and `RasGaṅ. n67 → 6`.

The visual extension adds eight ranges over four works. Every range has repeated image anchors;
unstable transitions and later resets stay outside the map.

| Siglum / part | Accepted leaves | Printed pages | Pages per leaf |
|---|---:|---:|---:|
| `Prasā.` part I, opening | 60–175 | 6–121 | 1 |
| `Prasā.` part I, main | 200–977 | 148–925 | 1 |
| `Prasā.` part II, opening | 10–175 | 4–169 | 1 |
| `Prasā.` part II, main | 305–805 | 297–797 | 1 |
| `Bhām.` | 5–650 | 97–742 | 1 |
| `Aparā.` | 10–575 | 11–576 | 1 |
| `Vaija.` | 5–150 | 2–293 | 2 |

`Vaija.` is explicitly a two-page scan: left and right pages receive separate numbers but share
the leaf URL. Its range stops at leaf 150; a later two-page gap is not bridged. `Aparā.` is
confirmed through page 576. The `Prasā.` openings and main ranges are deliberately disjoint:
the insertion-heavy transitions between them remain unresolved.

## 4. Locus resolution by work

| Principal siglum | AOB-exact C2 pairs | Unique scan page | Share within work |
|---|---:|---:|---:|
| `Vaija.` | 1,175 | **1,169** | 99.49 % |
| `Prasā.` | 1,487 | **1,371** | 92.20 % |
| `RasGaṅ.` | 1,235 | **1,166** | 94.41 % |
| `Bhām.` | 1,475 | **1,016** | 68.88 % |
| `Aparā.` | 1,293 | **423** | 32.71 % |
| `VīraMi.` | 3,590 | **357** | 9.94 % |
| `SmṛtiCan.` | 1,794 | **137** | 7.64 % |
| Other six exact-edition works | 11,442 | **0** | 0 % |
| **Total** | **23,491** | **5,639** | **24.00 %** |

The zeroes are explained, not treated as missing works. `HarVi.` uses sarga/śloka and
`Subhāṣi.` śloka alone, so their loci carry no page coordinate.

Two initially tempting classes remain excluded after range inspection:

- **`BālamBha.`** — leaves 1072–1126 restart at pages 2–56. That late reset cannot be equated
  with the main pagination, so no links are emitted from it.
- **`VedāntKa.`** — the combined parts repeat and incompletely label pagination, while PD's
  locus has no part coordinate. Even a locally unique label cannot prove the correct part.

The committed page map contains **4,032 candidates**: **3,986 unique** and **46 ambiguous
duplicates**. Only the unique class is eligible, inside either the three scandata maps or the
eight visually anchored ranges above.

## 5. Complete unresolved-locus accounting

| Reason | C2 pairs |
|---|---:|
| Printed page not mapped / excluded / absent from the scanned portion | 7,338 |
| Required volume not present in the verified scan set | 7,806 |
| Non-page locus scheme (`sarga/śloka`, śloka only) | 2,499 |
| Locus syntax outside the bounded page parser | 118 |
| Ambiguous duplicate printed page | 53 |
| Volume required but absent in the PD locus | 38 |
| **Unique printed-page target** | **5,639** |
| **Total AOB-exact C2 pairs** | **23,491** |

“Unresolved” therefore names the failed link stage. It does not mean that the work or edition
is unavailable, and it does not convert missing scandata labels into an absence verdict.

## 6. Artifacts

- [`pd_aob_scan_targets.tsv`](../data/pd/pd_aob_scan_targets.tsv) — all 1,622 Index rows, with separate work, edition, exact-scan and Index-scan fields.
- [`pd_aob_locus_scan_resolution.tsv`](../data/pd/pd_aob_locus_scan_resolution.tsv) — all 23,491 AOB-exact C2 pairs, target or explicit unresolved reason.
- [`pd_aob_scan_page_map.tsv`](../data/pd/pd_aob_scan_page_map.tsv) — 4,032 printed-page candidates, unique and duplicate status preserved.
- [`pd_aob_scan_ranges.tsv`](../data/pd/pd_aob_scan_ranges.tsv) — eight bounded visual ranges, including `Vaija.`'s two-page scans.
- [`pd_aob_scan_range_anchors.tsv`](../data/pd/pd_aob_scan_range_anchors.tsv) — the repeated image observations supporting those ranges.
- [`pd_aob_scan_editions.tsv`](../data/pd/pd_aob_scan_editions.tsv) — 14 curated C1-exact Archive.org items, volume, locus scheme and map-scope decision.
- [`pd_aob_scan_probes_2026-10-30.json`](../data/pd/pd_aob_scan_probes_2026-10-30.json) — metadata/scandata hashes, visual range anchors and live image receipts.
- [`pd_aob_scan_links_summary.json`](../data/pd/pd_aob_scan_links_summary.json) — protocol, all headline measures, per-work and per-reason aggregates, input hashes.
- [`scripts/pd_aob_scan_links.py`](../scripts/pd_aob_scan_links.py) — deterministic builder/checker; Archive.org refresh is a separate explicit mode.
- [`tests/forensic/test_pd_aob_scan_links.py`](../tests/forensic/test_pd_aob_scan_links.py) — hand-derived parser/map controls and full-population reconciliation.

## 7. Reproduce

```sh
# Offline rebuild from committed evidence and page map
python3.13 scripts/pd_aob_scan_links.py
python3.13 scripts/pd_aob_scan_links.py --check
python3.13 -m pytest tests/forensic/test_pd_aob_scan_links.py -q

# Explicit network refresh: metadata, scandata and live image probes
python3.13 scripts/pd_aob_scan_links.py --fetch-archive
```

Expected check:

```text
PASS C3 Index work 1615/1,622; edition 815/1,622; scan 14/1,622; loci 5639/23491 = 24.00% AOB-exact
```

## 8. Limits and next increment

- **Lower bound only.** Raising the 14-row scan figure requires more AOB-exact evidence, not
  looser promotion of C1's work-level witnesses.
- **Identity is not yet human-reviewed.** H7296's `unvalidated_pending_double_annotation`
  status is inherited; C3 claims no κ and no independent precision estimate.
- **Visual ranges remain bounded.** The remaining `Prasā.` transition gaps need their own
  anchors; no interpolation joins the opening and main ranges.
- **No content match is claimed.** Comparing PD's quoted reading with the scan is a later
  quotation-alignment task, not part of the 5,639-link numerator.

_30-10-2026 — Kimi Work; C3 full-population identity projection, live Archive.org scan probes, and conservative printed-page resolution._
