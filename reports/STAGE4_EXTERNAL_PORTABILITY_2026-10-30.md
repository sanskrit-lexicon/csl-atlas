_Created: 30-10-2026 · Last updated: 30-10-2026_

# Stage 4 external portability: the dated four-candidate gate census — every gate dated, ONP closed, the Russian analogue verified

**Protocol:** `research/notes/final_report_pwg-nws-pd-dcs-8294e5.md` §9/§13
(hyperresearch run 8294e5, committed before Stage 1; cited as in the Stage 1–3 reports).
**Census data:** [data/stage4_portability/stage4_gate_census.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4_portability/stage4_gate_census.json)
— every probe timestamped (UTC), every successful fetch hashed (committed body /
evidence transcript / sha256-of-record).
**Regeneration:** `python3 scripts/stage4_portability_check.py` → exit 0 (81 checks).
**Forensic freeze:** `tests/forensic/test_stage4_portability.py` (census sha, five
evidence shas, verdict pins).
**Substrates:** [Stage 1 PWG↔DCS](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PWG_DCS_JOIN_STAGE1_2026-10-30.md) (H7463) ·
[Stage 2 NWS layer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/NWS_LAYER_STAGE2_2026-10-30.md) (H7476) ·
[Stage 3 triangulation](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/TRIANGULATION_STAGE3_2026-10-30.md) (H7484).

## TL;DR

Stage 4 was executed as its protocol shape demands: Part 1 unconditional
(dated, hashed, multi-network gate census of all four §9 candidates), Part 2
(the ONP↔Menota run under the five pre-registrations) **skipped by design
because the ONP gate stayed closed on both arms**. The census is the
deliverable, and it changes the state of two rows:

1. **ONP↔Menota — gate CLOSED (rank 1 conditional stands).** The permission
   arm: no dated permission exists. The deposit arm: CLARIN handle
   [11356/1583](https://hdl.handle.net/11356/1583) re-read 2026-10-30T17:48Z
   (sha256 `774886b1…`, 34,462 B) is **still metadata-only** — declared 65,000
   entries, no files, no licence row, no citation rows, unchanged since its
   2021-08-05 issue date. One refinement to §9: "live ONP unreachable from
   every tested path" is now over-specific — from external networks the host
   **answers, with a browser-verification interstitial** (anti-bot wall,
   captured and hashed); from this LAN the connection is TCP-reset (curl 35/56,
   ECONNRESET from a second network, and a real local browser commits but
   renders an empty DOM). The wall is an access state, not a refusal, so the
   §9 demotion condition ("persistent ONP refusal") does **not** fire.
2. **Russian Словарь XI–XVII вв. ↔ web-corpora.net — the verification
   precondition FIRED.** §9's verdict was "Unqualified pending one successful
   fetch from a different network". That fetch succeeded on 2026-10-30, twice,
   from hosted services external to this LAN: the platform root (title
   "Corpora :: Home page"; the dictionary listed as «База данных на основе
   словаря») and the dictionary application itself,
   [web-corpora.net/wsgi/oldrus.wsgi](http://web-corpora.net/wsgi/oldrus.wsgi)
   — live, titled «Словарь русского языка XI–XVII веков», with the
   **search-by-source-list structure confirmed**: переводные/непереводные; ten
   genre classes (Библия и апокрифы … Документы); original-language axis
   (греческий, латынь, немецкий, польский, чешский); year/century and
   first-attestation year/century axes. The candidate upgrades from
   Unknown/unqualified to **verified structural analogue**. What it does not
   yet have is an assessed structured-data path: it is a query UI with a
   linked open-code GitHub project, no bulk export or licence row in view —
   executability of a run is successor work (pre-registration first, per the
   programme's own discipline).
3. **CAD↔Oracc/CDLI — gate CLOSED.** ISAC's CAD page re-read
   2026-10-30T17:51Z (sha256 `be18919c…`, 231,216 B; page revision stamp
   2026-05-27) still carries team/history/publications only: no transcribed
   data, no dataset, no open-data row. The reversal condition (ISAC release →
   rank 1) has not fired.
4. **GDLI↔OVI/TLIO — HELD, unchanged.** TLIO re-read 2026-10-30T18:09Z:
   alive (GattoWeb), "Corpus TLIO per il vocabolario", **corpus 3,295 testi —
   9 settembre 2024** — a dated count update against the ~1,960 figure the
   protocol carried, and corpus growth, not a scope change: no post-1375
   independent inventory appeared, so GDLI stays rank 3, held to its medieval
   slice.
5. **Menota (corpus side) — public and structured-accessible, so the binding
   gate really is the ONP side.** Catalogue rendered and counted 2026-10-30:
   Main (codices) **91**, Charters **196**, Runic inscriptions **100**,
   Le lingue nordiche **7** — **394 texts**, with a "Download all XML files"
   button on the catalogue page. Render capture committed and hashed.

**§9's reading, printed alongside the verdict and not absorbed by it:** read
strictly, no external candidate is currently cleanly executable — the
portability claim's true state. CAD remains OCR-gated; GDLI corpus-circular
beyond its medieval slice; ONP bot-walled with its sole structured deposit
metadata-only; the Russian analogue is now verified alive but offers a query
interface, not an assessed data path. The kill-exit is honoured (§13): the
programme records the pending state rather than manufacturing a survival in an
independent tradition.

## 1. Why a census, and what counts as a gate

The mission fixed Part 2's scope before any probing: the ONP↔Menota run
executes only behind "a dated permission or a reachable structured deposit".
Everything else is Part 1 — a dated census whose value is exactly that it is
boring: catalog rot and moving denominators are §11 threats, so every verdict
here carries its own timestamp and content hash, and no "current state" claim
rests on an undated row (GRETIL 384/772 precedent, §11 "Catalogue rot").

Network discipline: the executing host sits on a LAN with documented
resolver/TCP interference (diagnosed 21-10-2026), so **no unreachability
verdict rests on this LAN alone** — every candidate was probed from at least
one network external to it (hosted reader service, harness-hosted fetcher),
and the Russian candidate — the one §9 explicitly gated on a non-LAN fetch —
was verified twice externally.

## 2. Candidate readings (full probe records in the census JSON)

| Candidate | Gate | Dated reading |
|---|---|---|
| ONP↔Menota | **closed** | CLARIN 11356/1583 metadata-only (65,000 entries declared, 2021-08-05, no files/licence/citation rows); live host answers externally with a browser-verification wall; LAN + harness fetcher get connection-reset; local browser commits empty. Menota side: public, 394 texts, bulk-XML button. |
| CAD↔Oracc/CDLI | **closed** | ISAC page (stamp 2026-05-27): no transcribed data, no dataset; announcement-only state persists. |
| Russian Словарь XI–XVII | **verification precondition fired** | Root + oldrus.wsgi verified from external networks; search-by-source-list confirmed (genres, translated/original, languages, dates, first-attestation); query UI + open-code GitHub link; no bulk export/licence in view. |
| GDLI↔OVI/TLIO | **held** | TLIO alive, 3,295 testi (2024-09-09); medieval scope unchanged; reversal unfired. |

## 3. Reversal conditions re-checked (§9), each dated

| Condition | Fired | Dated evidence |
|---|---|---|
| ISAC publishes transcribed CAD → CAD rank 1 | no | 2026-10-30T17:51Z page re-read: nothing published |
| Persistent ONP refusal → demote below CAD | no | 2026-10-30T17:54Z: bot-wall + metadata-only deposit = access state, not refusal |
| Post-1375 independent Italian inventory → revive GDLI | no | 2026-10-30T18:09Z: TLIO scope unchanged |
| Menota absorbed into ONP citations at scale → independence collapse | not assessable | untestable with the ONP gate closed; recorded as unknown, not as pass |

## 4. What Stage 4 does and does not license

- The programme's falsification-first posture survives Stage 4 intact: the
  honest label stays "the overlap of two editorial programmes, reported
  against a population neither enumerates" — Levels 1–3 of the §10 verdict are
  unchanged by this census; Level 2's "no external candidate cleanly
  executable today" is **re-dated and sharpened**, not overturned.
- P1–P5 stand as written (§9), carried verbatim in the census, unexecuted;
  they fire only when the ONP gate opens, under the §8 pre-registrations and
  the §11 bias register.
- The Russian analogue is the census's one genuine state change. Per §13,
  Stage 4 includes "the Russian analogue after one verified fetch" — the
  fetch now exists, so the next programme step is a **pre-registered
  executability assessment** of that candidate (GitHub data, source-list
  export path, licence), not an improvised run. That is minted as the
  programme's successor handoff at this pass's close.

## Verifier

External, different model family from the executor (programme standing rule):
census JSON validated by `python3 scripts/stage4_portability_check.py`
(exit 0, 81 checks) and `python3 -m pytest tests/forensic/test_stage4_portability.py`
(3 pins) — machine gates, not self-attestation; the close-time verifier run
and its verdict are recorded in the H7507 registry row.

_Dr. Mārcis Gasūns_
