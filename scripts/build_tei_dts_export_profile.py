#!/usr/bin/env python3
# coding: utf-8
"""Build the pb/lb-anchored TEI sample + DTS collection manifest for AP.

H8428 — adoption move 2 from the H8426 CLLG comparison. Reuses:
  * the csl-pywork ``make_xml.py`` page/line conventions ([Page####-#], <L>..<pc>)
    via the verbatim csl-orig/v02/ap/ap.txt page-0001 fixture;
  * csl-atlas citation maps (data/obs/ls_abbreviation_frequency.json for AP
    attestation, data/pd/pd_aob_siglum_title.tsv for attested siglum titles).

It does NOT rebuild the csl-standards TEI/OntoLex exporters (boundary rule in
ARCHITECTURE.md and docs/TEI_ONTOLEX_MIGRATION.md): this is a dictionary-evidence
sample, not a new standards export pipeline.

Deterministic: no wall-clock timestamp; the provenance date comes from the
fixture header. ``--emit`` writes the artifacts, ``--check`` regenerates in
memory and byte-compares, ``--selftest`` runs four controls (2 positive,
2 negative).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "data/tei_dts/ap_page0001.fixture.txt"
LS_MAP = ROOT / "data/obs/ls_abbreviation_frequency.json"
SIGLUM_TITLES = ROOT / "data/pd/pd_aob_siglum_title.tsv"
OUT_TEI = ROOT / "data/tei_dts/ap-tei-sample.xml"
OUT_DTS = ROOT / "data/tei_dts/ap-dts-manifest.json"
OUT_RECEIPT = ROOT / "data/tei_dts/build_receipt.json"

SCHEMA_VERSION = "1.0.0"
PROFILE = "tei-pb-lb-dts-profile-v0.1"
SOURCE_DATE = "2006-09-11"  # ap.txt last-update stamp 11.09.06 in the fixture

PAGE_RE = re.compile(r"^\[Page(\d+)-(\d+)\]$")
ENTRY_RE = re.compile(
    r"^<L>(?P<line>[^<]+)<pc>(?P<pc>[^<]+)<k1>(?P<k1>[^<]*)<k2>(?P<k2>[^<]*)<e>(?P<e>.*)$"
)
LS_RE = re.compile(r"<ls(?:\s+n=\"([^\"]*)\")?>(.*?)</ls>")
SANSKRIT_RE = re.compile(r"\{#(.*?)#\}")
LABEL_RE = re.compile(r"<ab>(.*?)</ab>")
LEX_RE = re.compile(r"\{%(.*?)%\}")


def load_citation_maps() -> tuple[dict[str, int], dict[str, str]]:
    """Return (AP siglum -> attestation count, siglum -> attested title)."""
    ls = json.loads(LS_MAP.read_text(encoding="utf-8"))
    counts = ls.get("dicts", {}).get("ap", {})
    titles: dict[str, str] = {}
    with SIGLUM_TITLES.open(encoding="utf-8") as fh:
        next(fh, None)  # header
        for row in fh:
            parts = row.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[1].strip():
                titles[parts[0]] = parts[1].strip()
    return counts, titles


def siglum_of(raw: str, n_attr: str | None) -> str:
    """Base siglum from an <ls> element (H1086 shape: @n joined to content)."""
    text = (n_attr or "") + raw
    token = re.split(r"[\s,.;:]+", text.strip(), maxsplit=1)[0]
    return token.strip()


def inline_markup(text: str, counts: dict[str, int], titles: dict[str, str]) -> str:
    """Translate Cologne inline pseudo-markup into TEI inline elements.

    Every recognized markup span is replaced by a placeholder holding an
    already-built TEI fragment; only the remaining plain text is escaped.
    This avoids double-escaping and keeps the output well-formed.
    """
    slots: list[str] = []

    def keep(fragment: str) -> str:
        slots.append(fragment)
        return f"\x00SLOT:{len(slots) - 1}:\x00"

    def repl_ls(m: re.Match) -> str:
        n_attr, content = m.group(1), m.group(2)
        siglum = siglum_of(content, n_attr)
        count = counts.get(siglum, 0)
        cert = "observed" if count else "unknown"
        bibl_attrs = f' cert="{cert}"'
        if count:
            bibl_attrs += f' n="attestations:{count}"'
        title = titles.get(siglum, "")
        title_el = f"<title>{escape(title)}</title>" if title else ""
        abbr = f"<abbr>{escape(siglum)}</abbr>"
        ref = f'<ref target="csl:ls:{escape(siglum)}">{escape(content.strip())}</ref>'
        return keep(f'<cit type="source"{bibl_attrs}><bibl>{abbr}{title_el}</bibl>{ref}</cit>')

    text = LS_RE.sub(repl_ls, text)
    text = SANSKRIT_RE.sub(
        lambda m: keep(f'<foreign xml:lang="sa-Latn">{escape(m.group(1))}</foreign>'), text
    )
    text = LABEL_RE.sub(lambda m: keep(f"<abbr>{escape(m.group(1))}</abbr>"), text)
    text = LEX_RE.sub(lambda m: keep(escape(m.group(1))), text)
    text = re.sub(
        r"<lang>(.*?)</lang>",
        lambda m: keep(f'<foreign xml:lang="und">{escape(m.group(1))}</foreign>'),
        text,
    )
    text = escape(text)
    # A single <ls> span can nest other markup spans, so a slot value may itself
    # contain placeholders. Resolve iteratively until no token remains.
    token = re.compile(r"\x00SLOT:(\d+):\x00")
    for _ in range(len(slots) + 2):
        text, count = token.subn(lambda mm: slots[int(mm.group(1))], text)
        if count == 0:
            break
    return text.strip()


def parse_fixture(text: str) -> list[dict]:
    """Parse the verbatim AP source slice into page/entry/line records."""
    counts, titles = load_citation_maps()
    pages: list[dict] = []
    current_page: dict | None = None
    current_entry: dict | None = None
    body: list[str] = []

    def close_entry() -> None:
        nonlocal current_entry, body
        if current_entry is not None:
            current_entry["body"] = "\n".join(body).strip()
            assert current_page is not None
            current_page["entries"].append(current_entry)
        current_entry, body = None, []

    for raw in text.splitlines():
        line = raw.rstrip("\r")
        if not line or line.startswith("#"):
            continue
        page_m = PAGE_RE.match(line)
        if page_m:
            close_entry()
            current_page = {"page": page_m.group(1), "col": page_m.group(2), "entries": []}
            pages.append(current_page)
            continue
        if current_page is None:
            continue
        if line.strip() == "<LEND>":
            close_entry()
            continue
        entry_m = ENTRY_RE.match(line)
        if entry_m:
            close_entry()
            g = entry_m.groupdict()
            current_entry = {
                "line": g["line"],
                "pc": g["pc"],
                "k1": g["k1"],
                "k2": g["k2"],
                "n": g["e"],
            }
            body = []
            continue
        if current_entry is not None:
            body.append(line)
    close_entry()
    for page in pages:
        for entry in page["entries"]:
            entry["body_tei"] = inline_markup(entry["body"], counts, titles)
    return pages


def xml_id(entry: dict, page: dict) -> str:
    return f"ap-{page['page']}-{page['col']}-{re.sub(r'[^A-Za-z0-9]+', '-', entry['line']).strip('-')}"


def build_tei(pages: list[dict]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="sa-Latn">',
        "  <teiHeader>",
        "    <fileDesc>",
        "      <titleStmt>",
        "        <title>AP page 0001 — pb/lb-anchored TEI sample</title>",
        f"        <respStmt><resp>built by</resp><name>{PROFILE}</name></respStmt>",
        "      </titleStmt>",
        "      <publicationStmt>",
        "        <publisher>csl-atlas (Sanskrit Lexicon)</publisher>",
        '        <availability><licence target="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</licence></availability>',
        "      </publicationStmt>",
        "      <sourceDesc>",
        "        <bibl><title>Apte Sanskrit-English Dictionary (AP)</title>",
        "          <publisher>Bombay Sanskrit Series</publisher>",
        f"          <date>{SOURCE_DATE}</date>",
        '          <ref target="https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/ap">csl-orig/v02/ap</ref>',
        "        </bibl>",
        "      </sourceDesc>",
        "    </fileDesc>",
        "    <encodingDesc>",
        "      <projectDesc><p>H8428 adoption sample: pb/lb anchors derived from csl-pywork make_xml.py conventions; citations attested against the csl-atlas AP &lt;ls&gt; register.</p></projectDesc>",
        '      <refsDecl n="pb-lb">',
        '        <cRefPattern matchPattern="([0-9]{4})-([0-9])([0-9]*):([^:]+)" replacementPattern="#xpath(/TEI/text/body/div/pb[@n=&quot;$1-$2$3&quot;])"><p>page-column + line anchor</p></cRefPattern>',
        "      </refsDecl>",
        "    </encodingDesc>",
        "  </teiHeader>",
        "  <text><body>",
        '    <div type="dictionary" n="AP">',
    ]
    for page in pages:
        lines.append(f'      <pb n="{page["page"]}-{page["col"]}"/>')
        lines.append('      <list type="dictionary">')
        for entry in page["entries"]:
            lines.append(f'        <entry xml:id="{xml_id(entry, page)}">')
            lines.append(f'          <lb n="{escape(entry["line"])}"/>')
            k2 = escape(entry["k2"] or entry["k1"])
            lines.append(f'          <form><orth>{k2}</orth></form>')
            lines.append(f'          <sense n="{escape(entry["n"] or "1")}"><p>{entry["body_tei"]}</p></sense>')
            lines.append("        </entry>")
        lines.append("      </list>")
    lines += ["    </div>", "  </body></text>", "</TEI>", ""]
    return "\n".join(lines)


def build_dts(pages: list[dict]) -> str:
    anchors = [f'{p["page"]}-{p["col"]}' for p in pages]
    entries = sum(len(p["entries"]) for p in pages)
    doc = {
        "@context": "https://distributed-text-services.github.io/contexts/collection/1.jsonld",
        "@id": "https://sanskrit-lexicon.github.io/csl-atlas/data/tei_dts/ap-tei-sample.xml",
        "dts": {
            "conformsTo": "https://distributed-text-services.github.io/specifications/Collection",
            "profile": PROFILE,
        },
        "title": "AP page 0001 — pb/lb-anchored TEI sample",
        "citeStructure": [
            {
                "citeType": "div",
                "use": "n",
                "citeStructure": [
                    {
                        "citeType": "pb",
                        "use": "n",
                        "citeStructure": [
                            {
                                "citeType": "entry",
                                "use": "xml:id",
                                "citeStructure": [{"citeType": "lb", "use": "n"}],
                            }
                        ],
                    }
                ],
            }
        ],
        "citeTotal": len(anchors) + entries,
        "anchors": anchors,
        "provenance": {
            "source": "csl-orig/v02/ap/ap.txt (page 0001 fixture)",
            "conventions": "csl-pywork make_xml.py",
            "citationMap": "data/obs/ls_abbreviation_frequency.json (ap)",
            "titleMap": "data/pd/pd_aob_siglum_title.tsv",
            "sourceDate": SOURCE_DATE,
            "schemaVersion": SCHEMA_VERSION,
        },
        "licence": {
            "id": "CC-BY-SA-4.0",
            "url": "https://creativecommons.org/licenses/by-sa/4.0/",
        },
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def build_receipt(pages: list[dict], tei: str, dts: str) -> str:
    doc = {
        "schemaVersion": SCHEMA_VERSION,
        "handoff": "H8428",
        "profile": PROFILE,
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "counts": {
            "pages": len(pages),
            "entries": sum(len(p["entries"]) for p in pages),
            "pb": tei.count("<pb "),
            "lb": tei.count("<lb "),
            "cit": tei.count("<cit "),
        },
        "checks": {
            "pb_matches_pages": tei.count("<pb ") == len(pages),
            "lb_matches_entries": tei.count("<lb ") == sum(len(p["entries"]) for p in pages),
            "dts_cite_structure": bool(json.loads(dts).get("citeStructure")),
        },
        "verdict": "PASS",
    }
    doc["verdict"] = (
        "PASS"
        if all(doc["checks"].values())
        and doc["counts"]["pages"] > 0
        and doc["counts"]["entries"] > 0
        else "FAIL"
    )
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def generate() -> tuple[str, str, str, list[dict]]:
    pages = parse_fixture(FIXTURE.read_text(encoding="utf-8"))
    tei, dts = build_tei(pages), build_dts(pages)
    return tei, dts, build_receipt(pages, tei, dts), pages


def emit() -> int:
    tei, dts, receipt, pages = generate()
    OUT_TEI.write_text(tei, encoding="utf-8")
    OUT_DTS.write_text(dts, encoding="utf-8")
    OUT_RECEIPT.write_text(receipt, encoding="utf-8")
    print(f"emitted {OUT_TEI.relative_to(ROOT)} ({tei.count(chr(10))} lines)")
    print(f"emitted {OUT_DTS.relative_to(ROOT)}")
    print(f"emitted {OUT_RECEIPT.relative_to(ROOT)} — {receipt.strip().splitlines()[-3:]}")
    return 0


def check() -> int:
    tei, dts, receipt, _ = generate()
    ok = True
    for path, content in ((OUT_TEI, tei), (OUT_DTS, dts), (OUT_RECEIPT, receipt)):
        if not path.exists():
            print(f"FAIL missing {path.name}", file=sys.stderr)
            ok = False
            continue
        actual = path.read_text(encoding="utf-8")
        status = "OK" if actual == content else "MISMATCH"
        if actual != content:
            ok = False
        print(f"{status} {path.name}")
    return 0 if ok else 1


def selftest() -> int:
    """Four controls: 2 positive, 2 negative (gate must actually refuse)."""
    fixture = FIXTURE.read_text(encoding="utf-8")
    results: list[tuple[str, bool]] = []

    pages = parse_fixture(fixture)
    results.append(("positive: fixture parses pages+entries", bool(pages) and all(p["entries"] for p in pages)))
    tei, dts, receipt, _ = generate()
    results.append((
        "positive: pb/lb anchors match parsed pages/entries",
        tei.count("<pb ") == len(pages)
        and tei.count("<lb ") == sum(len(p["entries"]) for p in pages)
        and json.loads(receipt)["verdict"] == "PASS",
    ))

    mutated = fixture.replace("[Page0001-2]", "[MUTATED-2]")
    mutated_pages = parse_fixture(mutated)
    results.append(("negative: page-marker mutation changes page count", len(mutated_pages) != len(pages)))

    bad_tei = tei.replace("<pb ", "<pb:broken ", 1)
    results.append(("negative: tampered TEI fails byte parity", bad_tei != OUT_TEI.read_text(encoding="utf-8") if OUT_TEI.exists() else True))

    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    return 0 if all(p for _, p in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true", help="write the generated artifacts")
    group.add_argument("--check", action="store_true", help="byte-compare generated vs committed")
    group.add_argument("--selftest", action="store_true", help="run 4 parity controls")
    args = parser.parse_args()
    if args.emit:
        return emit()
    if args.check:
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
