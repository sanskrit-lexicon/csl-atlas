#!/usr/bin/env python3
"""Stage 4 gate-census payload — the ONP<->Menota candidate block (incl. Menota corpus side). Data only; assembled by
scripts/stage4_portability_build.py. Hashes embedded here were computed from
the frozen evidence files at build time and are re-verified independently by
scripts/stage4_portability_check.py."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ONP_CANDIDATE = json.loads(r'''
{
  "candidate": "ONP↔Menota",
  "protocol_rank": "rank 1, conditional on a dated permission/scrape gate",
  "gate_verdict": "closed",
  "gate_arms": {
    "dated_permission": "none exists as of 2026-10-30",
    "reachable_structured_deposit": "closed — CLARIN 11356/1583 metadata-only (see probes)"
  },
  "live_host_refinement": "Refines §9's 'live ONP unreachable from every tested path': the host is UP and answers from external networks, but with a browser-verification interstitial (anti-bot wall); from this LAN the connection is reset at TCP level. Either way no machine-usable structured access exists today. The bot-wall is an access state, not a refusal — the §9 demotion condition ('persistent ONP refusal') is NOT triggered; rank 1 conditional stands.",
  "probes": [
    {
      "ts_utc": "2026-10-30T17:48:45Z",
      "url": "https://hdl.handle.net/11356/1583",
      "effective_url": "https://www.clarin.si/repository/xmlui/handle/11356/1583",
      "network": "executing-host LAN (curl)",
      "http_status": 200,
      "bytes": 34462,
      "sha256": "774886b1182b5178ff8a97321cc660b72fac52c60cfc7096d0024be7cc881c34",
      "body_committed": false,
      "reading": "Metadata record re-read, still metadata-only: Size 65000 entries; Date issued 2021-08-05; Publisher Centre for Language Technology, Dept. of Nordic Research, University of Copenhagen; Project URL https://onp.ku.dk/onp/onp.php. No bitstream/download rows, no licence field on the record (only the repository-wide 'Rights Label' browse menu), no per-work citation rows."
    },
    {
      "ts_utc": "2026-10-30T17:48:46Z",
      "url": "https://onp.ku.dk/",
      "network": "executing-host LAN (curl)",
      "http_status": 0,
      "transport": "curl(35) Recv failure: Connection reset by peer (HTTPS)",
      "reading": "TCP-level reset; DNS itself resolves cleanly to 192.38.114.128."
    },
    {
      "ts_utc": "2026-10-30T17:51:08Z",
      "url": "https://onp.ku.dk/onp/onp.php",
      "network": "executing-host LAN (curl)",
      "http_status": 0,
      "transport": "curl(35) Recv failure: Connection reset by peer"
    },
    {
      "ts_utc": "2026-10-30T17:51:13Z",
      "url": "http://onp.ku.dk/onp/onp.php",
      "network": "executing-host LAN (curl)",
      "http_status": 0,
      "transport": "curl(56) Recv failure: Connection reset by peer"
    },
    {
      "ts_utc": "2026-10-30T17:53:30Z",
      "url": "https://onp.ku.dk/onp/onp.php",
      "network": "harness-hosted fetcher (external to the LAN)",
      "http_status": 0,
      "transport": "read ECONNRESET",
      "reading": "Second network, same connection-reset signature."
    },
    {
      "ts_utc": "2026-10-30T17:54:30Z",
      "url": "https://onp.ku.dk/onp/onp.php",
      "network": "hosted reader service (external to the LAN)",
      "http_status": 200,
      "content": "browser-verification interstitial",
      "evidence": {
        "file": "probe_evidence/onp_interstitial_reader_2026-10-30.md",
        "bytes": 493,
        "sha256": "4d7f67940b0875a7c030ff36e8fc790e5bb668c057dae57ffc39318e5c675113"
      },
      "reading": "Server UP from an external network; serves 'Checking your browser… Security Check'. A JS browser wall, not an outage: live ONP is reachable in principle by a human browser and NOT machine-usable as a structured deposit."
    },
    {
      "ts_utc": "2026-10-30T18:00:30Z",
      "url": "https://onp.ku.dk/onp/onp.php",
      "network": "executing-host LAN (real in-app browser, JS on)",
      "http_status": null,
      "transport": "navigation committed, DOM empty (snapshot length 0)",
      "reading": "The connection commits far enough to set the URL, then the stream stalls; consistent with mid-stream reset toward this LAN. No dictionary interface rendered."
    }
  ],
  "menota_corpus_side": {
    "gate_verdict": "public and structured-accessible (not the binding gate)",
    "reading": "Menota catalogue is public, no login; the binding gate of the ONP↔Menota run is the ONP side. Dated counts below; a 'Download all XML files' button is present on the catalogue page (bulk structured access on the corpus side).",
    "probes": [
      {
        "ts_utc": "2026-10-30T17:48:52Z",
        "url": "https://menota.org/",
        "effective_url": "https://menota.org/forside.xhtml",
        "network": "executing-host LAN (curl)",
        "http_status": 200,
        "bytes": 32931,
        "sha256": "b87530b5e010c586e233947cf7f24c684d3cd4db3cbcd45ad48e9bae560bc6c3",
        "body_committed": false
      },
      {
        "ts_utc": "2026-10-30T17:52:33Z",
        "url": "https://clarino.uib.no/menota/catalogue/menota",
        "network": "executing-host LAN (curl)",
        "http_status": 200,
        "bytes": 2802,
        "sha256": "be3bfb55dc519e6a8d07b65070d05a32bc32c72b2b142b7a837d24a0e345401f",
        "reading": "Identical Korpuskel SPA shell for all four catalogue routes (menota, menota-diploma, menota-lln, menota-rune); app bundle 669,826 B sha256 66982d060e080c48898e5fcedd75e55c04b1de269700607408029df08ad0260a; SPA base '/korpuskel-api/'."
      },
      {
        "ts_utc": "2026-10-30T18:03:00Z",
        "url": "https://clarino.uib.no/menota/catalogue/menota",
        "network": "executing-host LAN (real in-app browser, JS rendered)",
        "http_status": 200,
        "counts": {
          "main_codices": 91,
          "charters": 196,
          "runic_inscriptions": 100,
          "le_lingue_nordiche": 7,
          "total": 394
        },
        "bulk_access": "'Download all XML files' button present",
        "evidence": {
          "file": "probe_evidence/menota_catalogue_rendered_2026-10-30.txt",
          "bytes": 6144,
          "sha256": "3e936f19ecec2478b6b874235c10c75b0c3cb114f6d308b149f360b4e069cfb3"
        }
      }
    ]
  }
}
''')
