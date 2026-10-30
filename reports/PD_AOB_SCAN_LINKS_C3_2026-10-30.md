# PD siglum → AOB edition → scan-page targets — C3, 30-10-2026

_Created: 30-10-2026 · Scope: all 1,622 siglum-bearing Index rows and all 391,444 C2 `(siglum, locus)` pairs · Status: **landed as a bounded, reproducible lower-bound link layer** · Evidence: identities and aggregates **derived**, Archive.org probes **observed**, no human `reviewed` claim._

## 1. Result — three different measures

| Measure | Numerator / denominator | Share | What it establishes |
|---|---:|---:|---|
| Work identity | **1,615 / 1,622** | **99.57 %** | Index row has an H7296 `PDW-…` work identity |
| AOB edition identity | **815 / 1,622** | **50.25 %** | H7296 edition edge, or C1's explicit AOB-exact entry |
| AOB-exact scan target | **14 / 1,622 rows** | **0.86 %** | Live image URL for a C1-confirmed AOB edition |
| Locus → unique scan page | **1,660 / 23,491 AOB-exact C2 pairs** | **7.07 %** | Printed-page image resolved without a part/page ambiguity |

The 14 scan-bearing Index rows represent **13 distinct works**: `VīraMi.` occupies two printed
Index rows. The AOB-exact locus population is **23,491 of all 391,444 C2 pairs (6.00 %)**;
the 1,660 resolved pairs are **0.42 % of all C2 pairs**. This is a lower bound bounded by
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
4. Archive.org scandata maps that page to one unambiguous leaf inside a run of at least three
   consecutive printed-page labels.

A resolved target is a **page-level** link. It does not claim line-level placement, quotation
fidelity, or that PD's reading matches the scan. Three image-level spot checks also matched
the printed numerals on the pages: `VīraMi. n5 → 386`, `SmṛtiCan. n7 → 3`, and
`RasGaṅ. n67 → 6`.

## 4. Locus resolution by work

| Principal siglum | AOB-exact C2 pairs | Unique scan page | Share within work |
|---|---:|---:|---:|
| `RasGaṅ.` | 1,235 | **1,166** | 94.41 % |
| `VīraMi.` | 3,590 | **357** | 9.94 % |
| `SmṛtiCan.` | 1,794 | **137** | 7.64 % |
| Other ten exact-edition works | 16,872 | **0** | 0 % |
| **Total** | **23,491** | **1,660** | **7.07 %** |

The zeroes are explained, not treated as missing works. `HarVi.` uses sarga/śloka and
`Subhāṣi.` śloka alone, so their loci carry no page coordinate. Several other witnesses have
no numeric printed-page labels in scandata.

Two initially tempting classes were deliberately excluded after range inspection:

- **`BālamBha.`** — leaves 1072–1126 restart at pages 2–56. That late reset cannot be equated
  with the main pagination, so no links are emitted from it.
- **`VedāntKa.`** — the combined parts repeat and incompletely label pagination, while PD's
  locus has no part coordinate. Even a locally unique label cannot prove the correct part.

The committed page map contains **967 candidates**: **921 unique** and **46 ambiguous
duplicates**. Only the unique class is eligible, and only inside the three accepted
main-pagination maps above.

## 5. Complete unresolved-locus accounting

| Reason | C2 pairs |
|---|---:|
| Printed page not mapped / excluded / absent from the scanned portion | 11,317 |
| Required volume not present in the verified scan set | 7,806 |
| Non-page locus scheme (`sarga/śloka`, śloka only) | 2,499 |
| Locus syntax outside the bounded page parser | 118 |
| Ambiguous duplicate printed page | 53 |
| Volume required but absent in the PD locus | 38 |
| **Unique printed-page target** | **1,660** |
| **Total AOB-exact C2 pairs** | **23,491** |

“Unresolved” therefore names the failed link stage. It does not mean that the work or edition
is unavailable, and it does not convert missing scandata labels into an absence verdict.

## 6. Artifacts

- [`pd_aob_scan_targets.tsv`](../data/pd/pd_aob_scan_targets.tsv) — all 1,622 Index rows, with separate work, edition, exact-scan and Index-scan fields.
- [`pd_aob_locus_scan_resolution.tsv`](../data/pd/pd_aob_locus_scan_resolution.tsv) — all 23,491 AOB-exact C2 pairs, target or explicit unresolved reason.
- [`pd_aob_scan_page_map.tsv`](../data/pd/pd_aob_scan_page_map.tsv) — 967 printed-page candidates, unique and duplicate status preserved.
- [`pd_aob_scan_editions.tsv`](../data/pd/pd_aob_scan_editions.tsv) — 14 curated C1-exact Archive.org items, volume, locus scheme and map-scope decision.
- [`pd_aob_scan_probes_2026-10-30.json`](../data/pd/pd_aob_scan_probes_2026-10-30.json) — metadata/scandata hashes and live image receipts.
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
PASS C3 Index work 1615/1,622; edition 815/1,622; scan 14/1,622; loci 1660/23491 = 7.07% AOB-exact
```

## 8. Limits and next increment

- **Lower bound only.** Raising the 14-row scan figure requires more AOB-exact evidence, not
  looser promotion of C1's work-level witnesses.
- **Identity is not yet human-reviewed.** H7296's `unvalidated_pending_double_annotation`
  status is inherited; C3 claims no κ and no independent precision estimate.
- **Page labels are not uniform.** A useful next acquisition pass is printed-page verification
  for the no-label witnesses, beginning with `Prasā.`, `Bhām.`, `Aparā.` and `Vaija.`.
- **No content match is claimed.** Comparing PD's quoted reading with the scan is a later
  quotation-alignment task, not part of the 1,660-link numerator.

_30-10-2026 — Kimi Work; C3 full-population identity projection, live Archive.org scan probes, and conservative printed-page resolution._
