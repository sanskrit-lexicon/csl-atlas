"""Shared helpers for the H5325 fill scripts (seven narrative dictionaries).

Same record shape as the H5324 pilots (mw_components.py / skd_components.py);
see data/schema/megastructure-component.schema.json (schemaVersion 1.0.0,
unchanged) and docs/MEGASTRUCTURE_CATALOGUE.md.
"""
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "megastructure"


def comp(cid, seq, position, ctype, fn, title, extent, scan, disposition, evidence,
         level="observed", decodes=(), transcriptions=(), parent=None, notes=None,
         secondary=(), langs=("eng",)):
    return {"id": cid, "sequence": seq, "position": position, "componentType": ctype,
            "componentTypeNote": None, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition,
            "transcriptions": list(transcriptions), "parent": parent, "evidenceLevel": level,
            "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, english, iast=None):
    return {"asPrinted": as_printed, "iast": iast, "english": english}


def locus(scan_set, ref, image=None, printed=None):
    return {"scanSet": scan_set, "ref": ref, "image": image, "printedPage": printed}


def loci(scan_set, first, last, images, printed=None):
    """One locus per page ref first..last (inclusive, zero-padded ints) with image names."""
    n = len(images)
    out = []
    for i, r in enumerate(range(first, last + 1)):
        out.append(locus(scan_set, f"{r:02d}", images[i], printed))
    assert len(out) == n, (first, last, n)
    return out


def write(dict_obj):
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"{dict_obj['dict']}.json"
    path.write_text(json.dumps(dict_obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {path} ({len(dict_obj['components'])} components)")
