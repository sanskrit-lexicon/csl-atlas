# PD × DCS residue status queue (H7298)

_Created: 27-10-2026 · Executor: Kimi K3.1 Pro (`kimi-code-plan-global/k3.1-pro`) — filename tier DeepSeek retained as provenance (H3688)_

## 1. What this is

H6722 crossed the A68 PD residue against GRETIL and emitted the missing-everywhere
acquisition queue (6 works / 9,229 PD citations). This pass makes that queue
**status-aware**: every one of the 44 named-residue works now carries its DCS, GRETIL,
wisdomlib-portal and wisdomlib-estate state plus rights, annotation and fragment
status, and is routed into one of three action lanes; uncrossed rows are retained as
`unverified`, never dropped.

| Lane | Works | PD cites | Expected citation-mass gain |
|---|---:|---:|---:|
| `ingest-annotate` (machine-readable, not in DCS) | 9 | 10,262 | 10,262 |
| `acquire-digitise` (H6722 missing-everywhere, unchanged membership) | 6 | 9,229 | 9,229 |
| `fragment-completion` (partial witnesses + Skandapurāṇa context) | 6 | 8,683 | 5,348 |
| `unverified` (H6722 rows 21–44, GRETIL-uncrossed) | 24 | 9,685 | 9,685 |

Data: `data/pd/pd_dcs_residue_status_queue.tsv` / `.json`; frozen evidence input
`data/pd/pd_residue_source_status.tsv`; builder `scripts/pd_dcs_residue_status_queue.py`
(`--check` byte-parity + hand-computed lane invariants); pins
`tests/forensic/test_pd_dcs_residue_status_queue.py` (8 tests, green).

The missing-everywhere class is kept **distinct** from machine-readable-but-not-ingested
works: its six members are exactly H6722's, but two of them (Padmapurāṇa, Bhaviṣyapurāṇa)
now carry a located source — wisdomlib.org lists Sanskrit editions and the estate store
holds their link indexes (§3). Two `unverified` rows gain estate manifest hits the same
way (Naiṣadhīyacarita 2,860 chapters; Bṛhatsaṃhitā 107 chapters — link indexes only).

## 2. Method (bounded, dated)

- Residue source re-derived from `data/pd/pd_siglum_families.tsv`: 44 named rows,
  top-20 mass 24,839, tail mass 9,685 — exact parity with H6722/C5 enforced as a
  build-time gate.
- GRETIL verdicts inherited from C5 §2 (live census 14-10-2026; name-level, edition
  identity not asserted) — **no fresh GRETIL re-probe**.
- Wisdomlib estate probed live on the MSI box (`msi`/100.69.208.63, DESKTOP-8N57E9U,
  27-10-2026 ~06:00–06:15 UTC, 8 bounded SSH probes): the registered
  `ext:wisdomlib-sanskrit-layers` store is at `E:\Tools\wisdomlib-scrape`
  (canonical `D:\Tools\…` path is gone — D: holds 366 MB total), manifest
  `out/meta/books.json` = **75 books**, text layer per book = `sitemap.txt` only.
- Live wisdomlib.org meta probe from this Mac: **Cloudflare HTTP 403** (27-10-2026) —
  consistent with the store's own `stats.json` (23-07-2026: "Chapter bodies
  CF-blocked", 569,084 chapter URLs blocked).

## 3. Skandapurāṇa verdict (evidence-linked)

| Axis | Verdict | Evidence |
|---|---|---|
| Identity | wisdomlib.org book `skanda-purana-sanskrit` (`/hinduism/book/…`, discovered from `/sanskrit`) | MSI `out/meta/books.json` (27-10-2026) |
| Edition | **INCONCLUSIVE** — the store holds no book-page HTML for it (empty dir), and the live meta probe is CF-blocked; which print edition the portal digitized is not determinable from a link index | MSI `out/html/hinduism/book/skanda-purana-sanskrit` (empty); curl 403 "Just a moment…" (27-10-2026) |
| Completeness | Estate = **link-index only**: `text/…/skanda-purana-sanskrit/sitemap.txt` is a 40 B marker ("[link-index only; html_bytes=23838303]"); 0 chapter bodies. Manifest claims 95,556 chapters. Not a usable text. | MSI file census 27-10-2026 (files=1, bytes=40); `stats.json` CF-block |
| Rights | Derived layers **CC BY 4.0** (`LICENSE-DATA`, Zenodo 10.5281/zenodo.22117833); bulk-public GO per `RIGHTS_RULING_BULK_PUBLIC_28.07.2026` R1; underlying edition unverified | MSI store files (27-10-2026) |
| Annotation | none — no text layer exists for this book | MSI file census |
| DCS side | covered via **fragments only**: SkPuR (Revākhaṇḍa) 113,333 tok + SkPu 16,479 tok (2026); the full work is far larger | `data/pd/dcs_text_inventory.tsv` rows 9/282 |

Reading: DCS absence is not global absence (the portal holds a Sanskrit edition), and
fragments are not complete (both DCS witnesses are partial against the vulgate). The
lead is **verified as a lead and verified as not-yet-text**: the acquisition action is a
CF-blocked scrape, not an estate ingestion. `SkandP.`'s 3,335 PD citations stay distinct
from the DCS fragment mass — the queue row carries `expected_pd_citation_gain = 0`
(covered mass already attributed) and the verdict above.

## 4. Five-row source spot checks

| Row | Queue claim | Source record | Result |
|---|---|---|---|
| SkandP. (3,335) | covered-fragment; estate link-index only | MSI `books.json` 95,556 ch; `sitemap.txt` 40 B; DCS inv. 113,333+16,479 tok | PASS (27-10-2026) |
| PadmP. (3,506) | acquire; portal Sanskrit ed.; estate link index | MSI `books.json` `padma-purana-sanskrit` 700 ch; text = sitemap 38 B; C5 §2 #1 "0 hits" | PASS |
| MahāBh. (1,934) | ingest; GRETIL `vyakaranamahabhasya` (Cardona) | C5 §2 #2 evidence string; C6 404 probes; absent from 75-book manifest | PASS |
| NaiṣC. (694) | unverified (GRETIL uncrossed) + estate manifest hit | MSI `books.json` `naishadha-charita-sanskrit` 2,860 ch; text = sitemap 38 B | PASS |
| VāyuP. (961) | fragment-completion; Revākhaṇḍa only | C5 §2 #10 `sa_revAkhANDa-of-the-vAyupurANa-rkv.xml`; DCS classes Revākhaṇḍa under Skandapurāṇa (inv. rows 9/282) | PASS |

## 5. Risks / explicit unknowns

- The mint-time **"Q11"** label was ambiguous: no artefact literally named Q11 was
  found (A68 grill Q11 is the Mahābhārata-signal ruling; PD_OUTLOOK Q11 is staffing).
  Resolved 28-10-2026 by naming the actual anchors in H7298: `iscls.tex` §6 residue
  agenda + C5/C6 sweeps. The operational content is unchanged.
- GRETIL verdicts are as of 14-10-2026 and name-level; no fresh re-probe (network
  hygiene, H6722's own caveat).
- Wisdomlib portal state is as of the 2026 scrape manifest; live verification is
  CF-blocked from this host. Portal additions since the scrape are not visible.
- Print-edition identity of every wisdomlib book is unverified; rights fields say so.
- BṛĀraUBh: if the unnamed commentary is not Śaṅkara's, 891 cites flip
  present→absent (H6722 §5 risk carried forward).
- `unverified` rows can move lanes only after a GRETIL cross; NaiṣC./BṛSaṃ. already
  have estate link indexes, which makes them the cheapest first re-cross candidates.
- MSI store drift resolved 28-10-2026: the `wisdomlib-sanskrit-layers` registry row
  and H6073 now name the live store at `E:\Tools\wisdomlib-scrape` (former `D:\`
  path gone). Chapter-body acquisition remains CF-blocked.
