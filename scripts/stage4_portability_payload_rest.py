#!/usr/bin/env python3
"""Stage 4 gate-census payload — the other three candidates, statics, reversals, P1-P5, s9 reading, verdicts. Data only; assembled by
scripts/stage4_portability_build.py. Hashes embedded here were computed from
the frozen evidence files at build time and are re-verified independently by
scripts/stage4_portability_check.py."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REST = json.loads(r'''
{
  "statics": {
    "license": "CC-BY-SA-4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
    "schema": "stage4-gate-census/1",
    "handoff": "H7507",
    "stage": "PWG-NWS-PD-DCS Stage 4 — external portability (protocol §9+§13)",
    "protocol": "research/notes/final_report_pwg-nws-pd-dcs-8294e5.md (hyperresearch run 8294e5, committed before Stage 1)",
    "census_window_utc": "2026-10-30T17:48:45Z/2026-10-30T18:10:00Z",
    "executor": "GLM-5.3 (account:zai-individual-coding-plan/GLM-5.3), effort hard",
    "network_context": "The executing host sits on a LAN with documented resolver/TCP interference (poisoned nets 8.6.112.x / 8.47.69.x, diagnosed 21-10-2026, global fix applied 22-10-2026; residue still observable for some hosts). Protocol §9 therefore demands the Russian analogue be verified from a network other than this LAN; every other candidate was additionally probed from at least one external network (hosted reader service, harness-hosted fetcher, Spider cloud) so that no 'unreachable' verdict rests on this LAN alone.",
    "part2_onp_menota_executed": false,
    "part2_skip_reason": "ONP gate closed on both arms: (a) dated permission — none exists as of 2026-10-30; (b) reachable structured deposit — the sole structured deposit (CLARIN handle 11356/1583) re-read 2026-10-30T17:48Z is still metadata-only (declared 65,000 entries; no files, no licence row, no citation rows). Per the mission, the dated census IS the Stage 4 deliverable."
  },
  "rest_candidates": [
    {
      "candidate": "CAD↔Oracc/CDLI",
      "protocol_rank": "rank 1 the day ISAC publishes transcribed data (date-stamped)",
      "gate_verdict": "closed",
      "gate_arms": {
        "isac_transcribed_data_publication": "not published as of 2026-10-30 — page revision stamp 2026-05-27; team/history/publications content only; the two .pdf references are publication items, not datasets"
      },
      "live_host_refinement": "The 'digital CAD exists as announcement only' state persists; the reversal condition (ISAC release promotes CAD to rank 1) has NOT fired.",
      "probes": [
        {
          "ts_utc": "2026-10-30T17:51:19Z",
          "url": "https://isac.uchicago.edu/research/publications/chicago-assyrian-dictionary",
          "effective_url": "https://isac.uchicago.edu/research-projects/chicago-assyrian-dictionary",
          "network": "executing-host LAN (curl)",
          "http_status": 200,
          "bytes": 231216,
          "sha256": "be18919c073a32b976e56d0dca30e0c1928e0f8200690d1de623f5fe4ee02ea0",
          "body_committed": false,
          "page_published_time_meta": "2026-05-27T09:18:59-0500",
          "reading": "Page content: CAD team (Reculeau; Borgen; Ray; former Editors-in-Charge Gelb/Oppenheim/Reiner/Roth), history, select publications. No dataset, no transcribed-data download, no open-data statement."
        }
      ]
    },
    {
      "candidate": "Russian Словарь XI–XVII вв.↔web-corpora.net",
      "protocol_rank": "unqualified pending one successful fetch from a different network (§9)",
      "gate_verdict": "verification precondition now satisfied — host and dictionary interface VERIFIED from an external network",
      "gate_arms": {
        "verified_external_fetch": "satisfied 2026-10-30 (twice, independent services): platform root and the dictionary app http://web-corpora.net/wsgi/oldrus.wsgi",
        "structured_data_access": "unassessed beyond the search UI — a wsgi query application with headword/mask/example/source/genre/language/date axes and a linked open-code GitHub project; no bulk export or licence row seen on the interface. Executability of a run is a separate assessment (successor)."
      },
      "live_host_refinement": "§9's row read 'Host timed out under every probe from this perimeter' — still true from this LAN (root and app time out; browser navigation never commits), but FALSE as a property of the host: from external networks the platform serves normally. Verdict column upgrades from Unknown/unqualified to verified-alive structural analogue; the 'searchable by source list' claim is CONFIRMED (переводные/непереводные; genre axis: Библия и апокрифы, Богословие, Гомилетика, Агиография, Повести и беллетристика, Литургика, Эпистолография, Летопись, Хроника и хронография, Документы; original-language axis for translated sources; year/century and first-attestation year/century axes).",
      "probes": [
        {
          "ts_utc": "2026-10-30T17:56:57Z",
          "url": "https://web-corpora.net/slovar11-17/",
          "network": "executing-host LAN (curl)",
          "http_status": 0,
          "transport": "curl timeout after 30.0s (no answer)",
          "note": "path was a guess, abandoned; the real app URL comes from search + external fetch below"
        },
        {
          "ts_utc": "2026-10-30T17:55:30Z",
          "url": "https://web-corpora.net/",
          "network": "hosted reader service (external to the LAN)",
          "http_status": 200,
          "title": "Corpora :: Home page",
          "evidence": {
            "file": "probe_evidence/webcorpora_root_reader_2026-10-30.md",
            "bytes": 4380,
            "sha256": "5c16c2b3b001d7d741ed777d1a024210a02fba6679f97c093d1545682a0e396b"
          },
          "reading": "Platform verified alive from an external network; resource list includes 'Словарь русского языка XI–XVII веков — База данных на основе словаря'."
        },
        {
          "ts_utc": "2026-10-30T18:06:30Z",
          "url": "http://web-corpora.net/wsgi/oldrus.wsgi",
          "url_source": "web search result naming the beta database of the academic Словарь русского языка XI–XVII вв. (ИРЯ РАН, изд. с 1975)",
          "network": "harness-hosted fetcher (external to the LAN)",
          "http_status": 0,
          "transport": "Connect Timeout (443, 10s) — one external service slow to this host"
        },
        {
          "ts_utc": "2026-10-30T18:07:00Z",
          "url": "http://web-corpora.net/wsgi/oldrus.wsgi",
          "network": "hosted reader service (external to the LAN)",
          "http_status": 200,
          "title": "Словарь русского языка XI–XVII веков",
          "evidence": {
            "file": "probe_evidence/oldrus_wsgi_reader_2026-10-30.md",
            "bytes": 2043,
            "sha256": "669dd5b53c10e1b7b756cc4671e31b752580ca67ce2d9a3ab9775b09cb630b6e"
          },
          "reading": "Dictionary interface confirmed live: поиск по заголовочному слову / по маске / по примерам; часть речи (11 категорий); ПОИСК ПО ИСТОЧНИКАМ (переводные/не переводные); жанр источника (10 жанров); язык оригинала (греческий, латынь, немецкий, польский, чешский); год/век; год/век первого упоминания."
        }
      ]
    },
    {
      "candidate": "GDLI↔OVI/TLIO",
      "protocol_rank": "rank 3, held to its medieval slice",
      "gate_verdict": "held (unchanged) — no post-1375 independent Italian inventory appeared",
      "gate_arms": {
        "post_1375_independent_inventory": "not fired as of 2026-10-30 — TLIO remains the medieval corpus 'per il vocabolario' (GattoWeb); dated corpus count now 3,295 testi (9 settembre 2024), up from the ~1,960 figure the protocol carried — corpus growth, not a scope change"
      },
      "probes": [
        {
          "ts_utc": "2026-10-30T17:51:20Z",
          "url": "https://tlioweb.ovi.cnr.it/",
          "network": "executing-host LAN (curl)",
          "http_status": 0,
          "transport": "curl(35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL"
        },
        {
          "ts_utc": "2026-10-30T18:09:30Z",
          "url": "https://tlioweb.ovi.cnr.it/",
          "network": "hosted reader service (external to the LAN)",
          "http_status": 200,
          "title": "GattoWeb",
          "evidence": {
            "file": "probe_evidence/tlio_gattoweb_reader_2026-10-30.md",
            "bytes": 1019,
            "sha256": "829babb386231a5ac1cd04457dd16425ccff1cf279df24d8b7a2e2f26e7607f1"
          },
          "reading": "'Corpus TLIO per il vocabolario', corpus 3295 testi - 9 settembre 2024; ISSN 2281-5058; first publication 15.10.2005; Direttori Larson/Artale/Dotto. Alive; medieval scope unchanged; GDLI stays held to its medieval slice."
        }
      ]
    }
  ],
  "reversal_conditions_recheck": [
    {
      "condition": "ISAC publishing the transcribed CAD promotes CAD to rank 1",
      "fired": false,
      "ts_utc": "2026-10-30T17:51:19Z",
      "dated_evidence": "ISAC CAD page 2026-10-30T17:51Z: no transcribed data; page stamp 2026-05-27"
    },
    {
      "condition": "a persistent ONP refusal drops it below CAD",
      "fired": false,
      "ts_utc": "2026-10-30T17:54:30Z",
      "dated_evidence": "2026-10-30: no refusal event exists — the live host answers with a browser-verification wall and the deposit stays metadata-only; an access state is not an administrative refusal"
    },
    {
      "condition": "a post-1375 independent Italian inventory revives GDLI",
      "fired": false,
      "ts_utc": "2026-10-30T18:09:30Z",
      "dated_evidence": "TLIO 2026-10-30T18:09Z: medieval corpus, 3,295 testi, no scope change"
    },
    {
      "condition": "Menota already absorbed into ONP citations at scale collapses the independence premise",
      "fired": null,
      "ts_utc": "2026-10-30T18:10:00Z",
      "dated_evidence": "untestable with the ONP gate closed; no evidence either way as of 2026-10-30 (None = not assessable, not a pass)"
    }
  ],
  "preregistrations_onp_menota_p1_p5": {
    "status": "fixed in advance (protocol §9), UNEXECUTED — the run never fired because the ONP gate stayed closed",
    "bias_register": "protocol §11 applies to the run when it fires; this census itself used multi-network probing to counter the catalog-rot threat ('Catalogue rot / moving denominators': every verdict carries its own timestamp and content hash)",
    "P1": "citation mass per cited work is extreme-right-skewed, with Menota overlap concentrating in the top decile and near-zero tail overlap — uniform overlap falsifies A68's coverage structure",
    "P2": "completely excerpted works show an order-of-magnitude citation-density advantage over same-genre selective works — uniform density falsifies the editorial-artefact hypothesis",
    "P3": "print-only coverage underestimates archive coverage by ≈2.6× (1/0.38) for a–em — instability of that ratio shows partial-apparatus results are apparatus artefacts",
    "P4": "work-, citation- and manuscript-weighted metrics diverge materially — coincidence overturns the claim that metric choice carries information",
    "P5": "Menota absences are predictable from genre/date/charters profile, not random"
  },
  "section9_reading_printed_alongside": "Read strictly, no external candidate is currently cleanly executable — which is the portability claim's true state: CAD remains OCR-gated (and ISAC has published no transcribed data as of 2026-10-30), GDLI corpus-circular beyond its medieval slice (TLIO scope unchanged), ONP bot-walled with its sole structured deposit still metadata-only, and the Russian analogue — verified alive today with its search-by-source-list structure confirmed — offers a query interface, not yet an assessed structured-data path. This qualifier is printed alongside the §9 recommendation, never absorbed by it. Kill-exit honoured (§13): the programme records the pending state rather than manufacturing a survival.",
  "verdict_summary": {
    "onp_menota": "gate closed (permission arm: none; deposit arm: metadata-only); Part 2 unexecuted by design",
    "cad_isac": "gate closed (no transcribed data published)",
    "russian_slovar": "verification precondition FIRED — verified alive externally, structural analogue confirmed; executability assessment is successor work",
    "gdli_tlio": "held to medieval slice (reversal unfired); corpus count updated 3,295 testi (2024-09-09)",
    "menota_corpus_side": "public, 394 texts dated across four archives, bulk-XML button present"
  }
}
''')
