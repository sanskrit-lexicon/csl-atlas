"""KoshaSHRI vocable response to PD source/citation records.

Stdlib only. This adapter does not fetch, bulk-import, transliterate, or create
work identities. Work resolution belongs to the H7296 shared registry.
"""
import json
from collections.abc import Callable

SOURCE = "koshashri"
VALIDATION = "unvalidated_pending_double_annotation"


def parse_response(text):
    outer = json.loads(text)
    if not isinstance(outer, dict) or not isinstance(outer.get("object"), str):
        raise ValueError("expected an outer object containing a JSON string")
    vocable = json.loads(outer["object"])
    nested = [json.loads(row["object"]) for row in outer.get("nestedVocables") or []]
    return outer, vocable, nested


def entry_record(outer, vocable, nested):
    entry_id = f"{SOURCE}:{outer['id']}"
    return {
        "source": SOURCE,
        "source_entry_id": entry_id,
        "headword_devanagari": vocable.get("entryWord", ""),
        "headword_iast": vocable.get("transliteration", ""),
        "lemma_slp1": None,
        "normalization_status": "pending_canonical_slp1",
        "source_volume": vocable.get("volume"),
        "grammar_raw": vocable.get("grammaticalCategory", ""),
        "grammar_label": vocable.get("grammaticalCategoryFullName", ""),
        "subcategory": vocable.get("subCategory", ""),
        "grammatical_note_raw_html": vocable.get("grammaticalNote", ""),
        "etymology_raw_html": vocable.get("etymology", ""),
        "sandhi": vocable.get("sandhi") or [],
        "nested_vocables": nested,
        "validation_state": VALIDATION,
    }


def _walk_meanings(items, parent=""):
    for item in items or []:
        key = str(
            item.get("meaningKey")
            or item.get("shadeKey")
            or item.get("subShadeKey")
            or ""
        ).replace(" ", "").strip()
        path = parent + key
        yield item, path
        for child in item.get("shades") or []:
            yield from _walk_meanings([child], path)
        for child in item.get("subShades") or []:
            yield from _walk_meanings([child], path)


def citation_records(outer, vocable, work_resolver: Callable | None = None):
    entry_id = f"{SOURCE}:{outer['id']}"
    records = []
    for meaning, sense_path in _walk_meanings(vocable.get("meaning")):
        for citation_index, citation in enumerate(meaning.get("citations") or [], 1):
            for reference_index, reference in enumerate(citation.get("references") or [], 1):
                siglum = reference.get("referenceBook", "")
                work_id = work_resolver(siglum) if work_resolver else None
                records.append({
                    "source": SOURCE,
                    "source_entry_id": entry_id,
                    "sense_id": f"{entry_id}:{sense_path}",
                    "source_citation_id": f"{entry_id}:{sense_path}:{citation_index}:{reference_index}",
                    "quotation_text": citation.get("citationText", ""),
                    "source_siglum": siglum,
                    "work_title_candidate": reference.get("referenceBookFullName", ""),
                    "work_id": work_id,
                    "work_resolution_status": "resolved" if work_id else "unresolved",
                    "locus": reference.get("referenceMode") or [],
                    "locus_scheme": reference.get("referenceModeDesc", ""),
                    "work_date_raw": reference.get("year", ""),
                    "reference_author": reference.get("author", ""),
                    "validation_state": VALIDATION,
                })
    return records
