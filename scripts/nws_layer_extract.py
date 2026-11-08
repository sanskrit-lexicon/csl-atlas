#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7476 — Stage 2 extractor: the NWS layer's committed row-level substrate.

One-shot LOCAL-ONLY extractor (the NWS lemma tar is private, H5939; pwg.txt
lives in csl-orig). Produces the committed row-level TSVs that
scripts/nws_layer_join.py measures and scripts/nws_layer_check.py gates:

  data/nws_layer/nws_headword_mass.tsv     34,101 rows: per-key1 NWS mass
  data/nws_layer/nws_works_attestation.tsv 174 rows: declared-vs-exercised
  data/nws_layer/nws_works_registry.json   the dated scrape (verbatim copy)
  data/nws_layer/pwg_headword_ql.tsv       123,366 rows: per-k1 PWG mass
  data/nws_layer/nws_letter_envelope.tsv   key-space envelope per letter
  data/nws_layer/nws_x_mw_census.tsv       the X(MW) internal-source family
  data/nws_layer/nws_layer_pins.json       substrate pins (sha256 anchors)

Parse truth is IMPORTED from the kosha H6064 pipeline (fail-closed on its
Pinned numbers) — this script never re-implements the nws field grammar.

    python scripts/nws_layer_extract.py [--kosha DIR] [--pwg FILE] [--tar FILE]

Rights: MLU Halle-Wittenberg — texts with attribution (Impressum probe
04-10-2026). Committed rows are derived counts/keys only; the private lemma
tar is NOT committed (H5939).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "nws_layer"

TAR_SHA256_PIN = "054b05da96df2f1af2c95c02b7e15d87f8a616d4eaa339f93e3ed7430e07f00c"
PWG_SHA256_PIN = "430c910f8b0c9229d89ef1580b2385883ce5f4e2ee83dfc6ecb7d6251bb62166"
REGISTRY_HTML_SHA256_PIN = "86c9495e0cbe7824d9d1496974f245fab4d3cfb873cee1ce225defb20bbb8aa7"

# kosha H6064 pinned numbers the extractor must reproduce exactly (fail closed)
PINNED = {
    "tar_lemmas": 167990,
    "nws_content_entries": 34101,
    "page_refs": 8440,
    "lit_refs": 8937,
    "dict_marker_entries": 4941,
    "works_attested": 82,
    "lex_mw": 5873,
    "pwg_entries": 123366,
    "pwg_raw_ls_tags": 801788,
    "pwg_quotation_linked": 729719,
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kosha", default="/Users/mac/Documents/GitHub/kosha")
    ap.add_argument("--pwg", default="/Users/mac/Documents/GitHub/csl-orig/v02/pwg/pwg.txt")
    ap.add_argument("--tar", default="/Users/mac/Documents/GitHub/pwg-ru-data/layers/nws.tar.gz")
    args = ap.parse_args()

    sys.path.insert(0, str(Path(args.kosha) / "scripts"))
    import nws_ingest_pipeline as nip  # noqa: E402  (kosha H6064 parser)

    tar = Path(args.tar)
    pwg_txt = Path(args.pwg)
    fails: list[str] = []

    # --- 1. substrate hashes (fail closed before any parse) ----------------
    if sha256_of(tar) != TAR_SHA256_PIN:
        sys.exit("FAIL: NWS tar sha256 drift — not the pinned 054b05da… artifact")
    if sha256_of(pwg_txt) != PWG_SHA256_PIN:
        sys.exit("FAIL: pwg.txt sha256 drift — not the pinned 430c910f… machine text")

    # --- 2. the dated scrape (verbatim copy + provenance echo) --------------
    src_registry = Path(args.kosha) / "data" / "nws" / "nws_works_registry.json"
    registry_doc = json.loads(src_registry.read_text(encoding="utf-8"))
    prov = registry_doc["provenance"]
    if prov["html_sha256"] != REGISTRY_HTML_SHA256_PIN or prov["fetched"] != "2026-10-06" \
            or len(registry_doc["works"]) != 174:
        sys.exit("FAIL: registry provenance mismatch (need scrape 06-10-2026, "
                 "html sha 86c9495e…, 174 works)")

    OUT.mkdir(parents=True, exist_ok=True)
    # verbatim copy + the H5303 licence envelope (additive top-level keys;
    # works/provenance content untouched — see data/nws_layer/README.md)
    registry_copy = dict(registry_doc)
    registry_copy["license"] = "CC-BY-SA-4.0"
    registry_copy["licenseUrl"] = ("https://creativecommons.org/licenses/"
                                   "by-sa/4.0/")
    registry_copy["copied_from"] = {
        "repo": "gasyoun/kosha", "path": "data/nws/nws_works_registry.json",
        "note": "dated scrape copied verbatim; licence envelope additive "
                "(H5303); rights see provenance.rights",
    }
    (OUT / "nws_works_registry.json").write_text(
        json.dumps(registry_copy, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    index = nip.WorksIndex(registry_doc["works"])

    # --- 3. per-headword NWS mass + per-work attestation -------------------
    hw_rows = []
    per_work: dict[int, dict] = {w["id"]: {"exact": 0, "fuzzy": 0}
                                 for w in registry_doc["works"]}
    got = Counter()
    lex_mw_total = 0
    x_mw_family_total = 0
    x_mw_census: Counter[str] = Counter()
    letter_keys: Counter[str] = Counter()
    letter_prose: Counter[str] = Counter()
    for stem, j in nip.iter_tar_lemmas(tar):
        got["tar_lemmas"] += 1
        k1 = (j.get("key1") or "").strip()
        if k1:
            letter_keys[k1[:1]] += 1
        prose = j.get("nws") or ""
        if not prose.strip():
            continue
        got["nws_content_entries"] += 1
        p = nip.parse_nws_field(prose)
        got["page_refs"] += len(p["page_refs"])
        got["lit_refs"] += len(p["lit_refs"])
        if p["dict_markers"]:
            got["dict_marker_entries"] += 1
        got["dict_markers"] += len(p["dict_markers"])
        fam_toks = [t for t in p["sigla"] if t.endswith("(MW)")]
        for t in fam_toks:
            x_mw_census[t] += 1
        lex_mw = sum(1 for t in fam_toks if t == "Lex(MW)")
        fam = len(fam_toks)
        lex_mw_total += lex_mw
        x_mw_family_total += fam
        if k1:
            letter_prose[k1[:1]] += 1
        hw_rows.append({
            "key1": k1,
            "letter": k1[:1] if k1 else "",
            "senses": p["senses"],
            "sigla": len(p["sigla"]),
            "page_refs": len(p["page_refs"]),
            "lit_refs": len(p["lit_refs"]),
            "dict_markers": len(p["dict_markers"]),
            "lex_mw": lex_mw,
            "x_mw_family": fam,
        })
        for tok in p["sigla"] + p["lit_refs"]:
            w, how = index.match(tok)
            if w:
                per_work[w["id"]]["exact" if how == "exact" else "fuzzy"] += 1

    with open(OUT / "nws_headword_mass.tsv", "w", encoding="utf-8", newline="") as fh:
        cols = ["key1", "letter", "senses", "sigla", "page_refs", "lit_refs",
                "dict_markers", "lex_mw", "x_mw_family"]
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(hw_rows)

    attested = 0
    with open(OUT / "nws_works_attestation.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["work_id", "siglum", "exact", "fuzzy", "attested"])
        for wk in registry_doc["works"]:
            v = per_work[wk["id"]]
            a = 1 if v["exact"] + v["fuzzy"] > 0 else 0
            attested += a
            w.writerow([wk["id"], wk["siglum"], v["exact"], v["fuzzy"], a])

    with open(OUT / "nws_letter_envelope.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["letter", "keys_total", "keys_prose", "prose_pct"])
        for lit in sorted(letter_keys, key=lambda c: (-letter_prose.get(c, 0), c)):
            a, p = letter_keys[lit], letter_prose.get(lit, 0)
            w.writerow([lit, a, p, round(100.0 * p / a, 2) if a else 0.0])

    with open(OUT / "nws_x_mw_census.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["marker", "count"])
        for tok, c in x_mw_census.most_common():
            w.writerow([tok, c])

    # --- 4. PWG per-headword mass (committed reader, sha-verified input) ---
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "scripts" / "lib"))
    import pd_quotations_vs_pwg as pvg  # noqa: E402

    pwg_rows = []
    pw_entries = pw_raw = pw_ql = 0
    for hdr, body in pvg.iter_entries(str(pwg_txt)):
        m = pvg.RE_HDR.match(hdr)
        if not m:
            continue
        k1 = m.group(3)
        text = " ".join(body)
        n_raw = len(pvg.RE_LS.findall(text))
        rec = pvg.pwg_entry(body)
        pw_entries += 1
        pw_raw += n_raw
        pw_ql += rec["attestations"]
        pwg_rows.append({"k1": k1, "raw_tags": n_raw, "ql_tags": rec["attestations"]})
    with open(OUT / "pwg_headword_ql.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["k1", "raw_tags", "ql_tags"],
                           delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(pwg_rows)

    # --- 5. fail-closed verification against every pin ----------------------
    checks = {
        "tar_lemmas": got["tar_lemmas"],
        "nws_content_entries": got["nws_content_entries"],
        "page_refs": got["page_refs"],
        "lit_refs": got["lit_refs"],
        "dict_marker_entries": got["dict_marker_entries"],
        "works_attested": attested,
        "lex_mw": lex_mw_total,
        "pwg_entries": pw_entries,
        "pwg_raw_ls_tags": pw_raw,
        "pwg_quotation_linked": pw_ql,
    }
    for k, v in checks.items():
        if v != PINNED[k]:
            fails.append(f"{k}: {v} != pinned {PINNED[k]}")

    pins = {
        "created": "2026-10-30",
        "dataset": "nws_layer/nws_layer_pins",
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "rights_nws": "MLU Halle-Wittenberg — texts with attribution "
                      "(Impressum probe 04-10-2026); private lemma tar NOT "
                      "committed (H5939); committed rows are derived counts/keys",
        "nws_tar": {"sha256": TAR_SHA256_PIN, "bytes": tar.stat().st_size},
        "pwg_txt": {"sha256": PWG_SHA256_PIN, "bytes": pwg_txt.stat().st_size},
        "works_registry_scrape": {
            "url": prov["url"], "fetched": prov["fetched"],
            "html_sha256": prov["html_sha256"], "works": len(registry_doc["works"]),
        },
        "rows": {
            "nws_headword_mass": len(hw_rows),
            "nws_works_attestation": len(registry_doc["works"]),
            "pwg_headword_ql": len(pwg_rows),
            "nws_letter_envelope": len(letter_keys),
            "nws_x_mw_census": len(x_mw_census),
        },
        "x_mw_family_total": x_mw_family_total,
        "nws_key_space": sum(letter_keys.values()),
        "method_h6": "attested works recomputed ONLY from the dated scrape "
                     "(2026-10-06, html sha 86c9495e…) + parsed sigla match "
                     "— never from filename stems (H6050 retraction)",
    }
    (OUT / "nws_layer_pins.json").write_text(
        json.dumps(pins, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    if fails:
        print("EXTRACT FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"EXTRACT OK: {len(hw_rows)} headword rows, {len(registry_doc['works'])} "
          f"work rows, {len(pwg_rows)} PWG rows; all pins reproduce")
    return 0


if __name__ == "__main__":
    sys.exit(main())
