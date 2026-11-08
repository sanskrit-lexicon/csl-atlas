# -*- coding: utf-8 -*-
"""Typographic PD ``(siglum, locus)`` extraction for H7458/C2."""
from __future__ import annotations

import re

import pd_quotation_units as pqu

NUMBER = r"(?:[A-Za-z]?\d+[A-Za-z]?|[IVXLCDMivxlcdm]+)(?![^\W\d_])"
LOCUS_QUALIFIER = r"(?:\s*\((?:\d+|[A-Za-z]+\.?(?:\s+[IVXLCDMivxlcdm]+)?)\))?"
LOCUS_ATOM = rf"(?!v\.\s*l\.){NUMBER}{LOCUS_QUALIFIER}\.?{LOCUS_QUALIFIER}"
LOCUS_RE = re.compile(
    rf"\s*(?P<locus>{LOCUS_ATOM}"
    rf"(?:(?:\s*[.,:/-]\s*|\s+){LOCUS_ATOM})*\.?)"
)
RE_PAGE = re.compile(r"\[Page[^\]]*\]")


def candidate_siglum(token, known_sigla):
    """Reject lowercase prose unless the independent PD census knows the token."""
    if token in known_sigla:
        return True
    bare = re.sub(r"\([^)]*\)", "", token).rstrip(".").strip()
    return bool(bare) and not bare[0].islower()


def normalized_siglum(segment, match, known_sigla):
    """Return (siglum, raw_start), repairing a census-confirmed line-wrap hyphen."""
    token = match.group(1) + match.group(2)
    raw_start = match.start()
    prefix = re.search(r"([^\W\d_]+)-\s*$", segment[:match.start()])
    if prefix:
        joined = prefix.group(1) + token
        if joined in known_sigla:
            token = joined
            raw_start = prefix.start(1)
    return token, raw_start


def iter_raw_sigla(segment):
    """Yield the same raw token shapes as H6949, with their character spans."""
    pos = 0
    while True:
        match = pqu.RE_SIG.search(segment, pos)
        if not match:
            return
        pos = match.end()
        sep = match.group(2)
        if sep != "." and not sep.endswith(".)"):
            continue
        token = match.group(1) + sep
        if pqu.is_siglum(token):
            yield match, token


def clean_locus(value):
    return re.sub(r"\s+", " ", value.strip())


def parse_citation_tail(tail, known_sigla):
    """Extract well-formed pairs and explicit rejects from one H6949 tail.

    Returns ``(records, diagnostics)``. Each record carries siglum, locus, kind
    and the exact raw citation. Diagnostics are (siglum, reason, example).
    """
    tail = tail.split("{@", 1)[0]
    source_plain = pqu.RE_ITAL.sub(" ", pqu.RE_TAG.sub(" ", tail))
    plain = RE_PAGE.sub(" ", source_plain)
    records = []
    diagnostics = []
    previous = None
    for source_segment, segment in zip(source_plain.split(";"), plain.split(";")):
        source_hits = sum(1 for _match, _token in iter_raw_sigla(source_segment))
        raw_hits = sum(1 for _match, _token in iter_raw_sigla(segment))
        for _ in range(max(0, source_hits - raw_hits)):
            diagnostics.append(("__PAGE_QUALIFIER__", "page_separated_qualifier", source_segment.strip()[:120]))
        for _ in range(max(0, raw_hits - source_hits)):
            diagnostics.append(("__PAGE_JOIN__", "page_joined_marker", source_segment.strip()[:120]))
        source_continuation = source_hits == 0 and bool(re.search(r"\d", source_segment))
        clean_continuation = raw_hits == 0 and bool(re.search(r"\d", segment))
        if source_continuation and not clean_continuation:
            diagnostics.append(("__PAGE_NUMBER__", "page_marker_only_continuation", source_segment.strip()[:120]))
        examined_hits = 0
        pos = 0
        while True:
            match = pqu.RE_SIG.search(segment, pos)
            if not match:
                break
            pos = match.end()
            sep = match.group(2)
            if sep != "." and not sep.endswith(".)"):
                continue
            raw_token = match.group(1) + sep
            if not pqu.is_siglum(raw_token):
                continue
            examined_hits += 1
            siglum, raw_start = normalized_siglum(segment, match, known_sigla)
            if not candidate_siglum(siglum, known_sigla):
                diagnostics.append((siglum, "discourse_not_siglum", segment[raw_start:match.end()].strip()))
                continue
            previous = siglum
            located = LOCUS_RE.match(segment, match.end())
            if not located:
                diagnostics.append((siglum, "siglum_without_locus", segment[raw_start:match.end()].strip()))
                continue
            locus = clean_locus(located.group("locus"))
            records.append({
                "siglum": siglum,
                "locus": locus,
                "kind": "siglum",
                "raw_citation": clean_locus(segment[raw_start:located.end()]),
            })
            # Roman numerals inside this locus must not become fresh sigla.
            pos = located.end()
        for _ in range(raw_hits - examined_hits):
            diagnostics.append(("__LOCUS_TOKEN__", "marker_consumed_by_locus", segment.strip()[:120]))
        if clean_continuation:
            located = LOCUS_RE.match(segment)
            if located:
                locus = clean_locus(located.group("locus"))
                if previous:
                    records.append({
                        "siglum": previous,
                        "locus": locus,
                        "kind": "continuation",
                        "raw_citation": clean_locus(segment[:located.end()]),
                    })
                else:
                    diagnostics.append(("__UNASSIGNED_CONTINUATION__", "unassigned_continuation", locus))
            else:
                diagnostics.append(("__CONTINUATION__", "continuation_without_locus", segment.strip()[:120]))
    return records, diagnostics
