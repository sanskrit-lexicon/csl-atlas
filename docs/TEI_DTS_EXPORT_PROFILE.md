_Created: 18-11-2026 · Last updated: 18-11-2026_

_Dr. Mārcis Gasūns_

# TEI / DTS export profile — AP page 0001 (H8428)

Adoption move 2 of the [H8426 CLLG comparison](https://github.com/gasyoun/csl-observatory/blob/main/docs/CLLG_VS_SANSKRIT_ESTATE_18-11-2026.md).
The scorecard rates the estate **TRAILS** CLLG on encoding/interoperability:
CLLG ships TEI XML native with `pb`/`lb`, a canonical `citeStructure` and a
planned Biblissima DTS endpoint, while the estate has custom `<L>` markup,
`make_xml.py` TEI exports and **no DTS endpoint**. This profile closes that
specific deficit with a bounded, reproducible sample — it does not claim a
full corpus release.

## What shipped

| Artifact | Purpose |
|---|---|
| [`scripts/build_tei_dts_export_profile.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_tei_dts_export_profile.py) | Deterministic builder: `--emit` / `--check` / `--selftest` (4 controls, 2 positive + 2 negative) |
| [`data/tei_dts/ap_page0001.fixture.txt`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/tei_dts/ap_page0001.fixture.txt) | Verbatim first printed page of AP as a reproducibility fixture (126 lines, 9 entries) |
| [`data/tei_dts/ap-tei-sample.xml`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/tei_dts/ap-tei-sample.xml) | TEI sample: 2 `<pb>` page-column anchors, 9 `<lb>` line anchors, 22 source `<cit>` elements; well-formed XML |
| [`data/tei_dts/ap-dts-manifest.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/tei_dts/ap-dts-manifest.json) | DTS Collection-shaped manifest with a `div → pb → entry → lb` `citeStructure` |
| [`scripts/probe_dts_endpoint.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/probe_dts_endpoint.py) | DTS conformance probe: `--offline` (default) or `--url` for a live endpoint; emits a JSON receipt |
| [`data/tei_dts/dts_probe_receipt.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/tei_dts/dts_probe_receipt.json) | Probe receipt: offline PASS on the committed manifest |
| [`data/tei_dts/build_receipt.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/tei_dts/build_receipt.json) | Builder canary: counts + parity checks, verdict PASS |

## Reuse — what was consumed, not rebuilt

1. **csl-pywork `make_xml.py` conventions.** The fixture keeps the source
   `[Page####-#]` page-column milestones and `<L>…<pc>…<k1>…<k2>…` entry
   markers verbatim from [`csl-orig/v02/ap/ap.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt).
   The builder maps `[Page####-#] → <pb n="####-#"/>` and `<L>n → <lb n="n"/>`;
   this is the same page/line model `make_xml.py` renders, not a new converter.
2. **csl-atlas citation maps.** `<ls>` source citations are resolved against
   [`data/obs/ls_abbreviation_frequency.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/ls_abbreviation_frequency.json)
   (AP: 1,517,609 `<ls>` attestations corpus-wide; 1,541 for `Bg.`) and
   [`data/pd/pd_aob_siglum_title.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_siglum_title.tsv)
   (5,107 sigla). An attested siglum gets `cert="observed"` and its measured
   `n="attestations:N"`; an unattested one gets `cert="unknown"` — never an
   invented expansion.
3. **csl-standards TEI Lex-0 work is the canonical standards home.** The
   archival + Lex-0 exporters, validators and the TEI Lex-0 ODD in
   [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards) were
   read, not duplicated. Per [`ARCHITECTURE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md)
   and [`docs/TEI_ONTOLEX_MIGRATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/TEI_ONTOLEX_MIGRATION.md),
   TEI/OntoLex/FrAC/RDF export validation belongs there. This deliverable
   adds **no npm TEI export command** to csl-atlas; it is a dictionary-evidence
   sample plus a conformance probe, not a second standards pipeline.

## License and provenance

- **Source text:** Apte Sanskrit–English Dictionary (AP), csl-orig `v02/ap/ap.txt`,
  digitisation last updated 11.09.06. The estate distributes CSDL dictionary
  text under **CC BY-SA 4.0**; the csl-atlas [`LICENSE`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/LICENSE)
  and the citation-map `license` field both carry that identifier. The TEI
  `<fileDesc>` repeats it as `<licence target="…by-sa/4.0/">`.
- **Derived artifacts:** generated from the verbatim fixture, so they inherit
  the source licence and attribution. No rights-gated corpus was exported.
- **Provenance chain:** `csl-orig/v02/ap/ap.txt` → (fixture) →
  `csl-pywork make_xml.py` page/line conventions → `csl-atlas` citation maps →
  TEI sample + DTS manifest. Every hop is named in the file headers and in
  the manifest's `provenance` object.

## DTS status — honest scope

No live estate DTS endpoint exists as of 18-11-2026 (H8426, REUSE_INDEX §1).
The committed manifest is **DTS Collection-shaped** and the probe validates
that shape; `--url` is provided so the same check can be pointed at a real
endpoint when one is stood up. A PASS here is a *document conformance* verdict,
not a claim that a DTS service is running. The probe makes no network call in
its default offline mode and never writes to a remote service.

## Reproduce and verify

```bash
python3 scripts/build_tei_dts_export_profile.py --selftest   # 4/4 PASS
python3 scripts/build_tei_dts_export_profile.py --emit        # regenerate
python3 scripts/build_tei_dts_export_profile.py --check       # byte parity OK
python3 scripts/probe_dts_endpoint.py --selftest              # 2/2 PASS
python3 scripts/probe_dts_endpoint.py --offline               # receipt PASS
python3 -c "import xml.etree.ElementTree as ET; ET.parse('data/tei_dts/ap-tei-sample.xml')"
```

Deterministic by construction: no wall-clock timestamp; the provenance date
is fixed in the fixture header. Re-emitting on any host is byte-identical.

## Decision trail

- **Rejected:** rebuilding the csl-standards TEI Exporter in csl-atlas —
  boundary violation; consumed the existing work instead.
- **Rejected:** a full-corpus export — unbounded and out of scope for a
  one-page adoption sample; one printed page is enough to prove the pb/lb
  anchoring and DTS citeStructure.
- **Rejected:** inventing siglum expansions — unattested citations are
  marked `cert="unknown"` rather than guessed.
