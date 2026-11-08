_Created: 30-10-2026 · Last updated: 30-10-2026_

# Stage 4 external-portability gate census (H7507) — data dictionary

Dated, multi-network probe census of the four §9 external-replication
candidates of the PWG–NWS–PD–DCS programme (protocol
`research/notes/final_report_pwg-nws-pd-dcs-8294e5.md` §9/§13 — hyperresearch
run 8294e5 workspace, cited the same way as the Stage 1–3 reports).
Every verdict carries its own UTC timestamp; every successful fetch carries a
sha256 of the content the verdict rests on (committed body, or evidence
transcript, or hash-of-record for uncommitted bodies).

## Files

| File | What it is |
|---|---|
| `stage4_gate_census.json` | The census: four candidates, gate verdicts, per-probe records (ts, url, network, transport, status, bytes, sha256, reading), Menota corpus-side block, reversal-condition re-check, P1–P5 carried verbatim (unexecuted), §9 reading printed alongside. |
| `probe_evidence/*.md`, `probe_evidence/*.txt` | Verbatim transcripts of external-network fetches (hosted reader service) + the JS-rendered Menota catalogue capture. Each has its sha256 pinned in the census and in `tests/forensic/test_stage4_portability.py`. |

## Provenance and hashing basis

- Fetches from the executing-host LAN used `curl -sS -L` with bodies saved and
  hashed at capture time; the two large bodies (CLARIN record 34,462 B, ISAC
  CAD page 231,216 B) are **not committed** — they are recorded by URL +
  timestamp + bytes + sha256-of-record, so a verifier can re-fetch and compare.
- External-network fetches used hosted reader services; the reader returns a
  markdown rendering, and the committed transcripts preserve the returned
  `title`/`content` fields verbatim (transcription basis stated per file).
- The Menota catalogue is a Korpuskel SPA; the four catalogue routes serve one
  identical JS shell (hash pinned). Counts were read from the rendered
  catalogue in a real browser session (combobox per corpus; "N texts." line);
  the main-corpus render is committed and hashed.
- `scripts/stage4_portability_build.py` assembles the census (hashes computed
  from committed evidence); `scripts/stage4_portability_check.py` re-validates
  it independently — `python3 scripts/stage4_portability_check.py` → exit 0.
- Forensic freeze: `tests/forensic/test_stage4_portability.py` pins the census
  sha, the five evidence shas, and the verdict values.

## Licence envelope

`stage4_gate_census.json` carries `license: CC-BY-SA-4.0` (repo-wide value,
[H5303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5303-OxAlpha_csl-atlas_dataset-licence-field-backfill-validator_23.09.26.md)
gate). Evidence transcripts are factual captures of public web interfaces
(interface labels, counts); `copied_from` provenance is inside each file.

_Dr. Mārcis Gasūns_
