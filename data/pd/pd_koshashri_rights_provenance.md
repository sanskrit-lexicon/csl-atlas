# PD × KoshaSHRI staleness audit — rights and provenance note

_Created: 27-10-2026 · Handoff: H7300 · Executor: Kimi Work (Kimi)_

## Sources touched

| Source | Rights | What was taken | Where it landed |
|---|---|---|---|
| KoshaSHRI portal (koshashri-dc.ac.in, Deccan College / C-DAC) | **All rights reserved** (permission by email; Terms + Copyright Policy, C7 14-10-2026) | 35 GETs of the public per-volume JSON metadata endpoint (`/search/fetchVolumeInfo/<id>`), browser User-Agent, no login, no socket subscription, no POST; root page, one login-walled preview page (gate check only), robots.txt/sitemap.xml (404 check) | `pd_koshashri_volume_snapshot_2026-10-27.json` — volume ids, years, editors, page ranges, opening/closing headwords only. **No entry text fetched or committed.** |
| Cologne PDScan 2020 (sanskrit-lexicon.uni-koeln.de) | **CC BY-NC-SA 3.0** | `pdtxt.zip` re-downloaded for the tag census; one public entry HTML page; four scan-page PDFs of vols 7–8 for the bracket-mark control | Derived counts only (`pd_cologne_tag_census_2026-10-27.json`); the scan PDFs and pd.txt were **not committed**; the control TSV records presence/absence verdicts, not page content |
| H7275 publication ledger | this repo | read-only join substrate | — |
| C7 audit (14-10-2026) and two-digitisations audit (25-10-2026) | Uprava papers/A68/sweeps | verdicts and probe facts carried with per-row evidence dates | quoted as evidence refs in the panels |

## Decisions

- **No circumvention.** KoshaSHRI answers 403 to a bare curl UA; the probes use
  a normal browser UA string on public GET routes — the same surface a browser
  user sees. The login wall was not passed, no account was made or requested,
  the SockJS/STOMP data channel was not subscribed.
- **`total_vocables` trap documented, not used.** Every volume record carries
  `total_vocables: 100` — a constant, not a count (canary K4). No entry census
  is derived from the portal.
- **Unicode.** The portal serves NFD; snapshot strings are NFC-normalized at
  ingest (noted in the snapshot).
- **Scan pages stay off-git.** The four Cologne scan PDFs (vols 7–8) were
  rendered and eyeballed for the control, then discarded; only the per-mark
  consistency verdicts are committed.
- **Missing print evidence is STOP, not PASS.** The 2009–2019 print record is
  unreachable in the estate (H7275 layer-2 precedent); the fidelity panel for
  it is `STOP_NO_PRINT_ACCESS` and no editorial claim is made from tags alone.

## Repro

`scripts/pd_koshashri_staleness_audit.py` (build / `--check`) plus the exact
curl surface in `reports/PD_KOSHASHRI_STALENESS_AUDIT_2026.md` §Repro.

## H7316 addendum — one fixture, 29-10-2026

A separate public single-entry GET (`/search/vocable/<uuid>`) supplied the
`agni` response for the fixture export. No login, POST, socket subscription or
bulk crawl was used. The full 2,768,644-byte response remains a restricted
local input and is **not committed**. Only H7316's one entry and its 1,400
citation-reference rows are committed, with per-row provenance and
`unvalidated_pending_double_annotation`; this is not a bulk publication or an
independent-witness claim. The response's malformed source strings and all
unresolved works are preserved rather than silently normalized. See
`reports/PD_KOSHASHRI_FIXTURE_EXPORT_2026.md`.
