#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PD bracketed dictionary-source rule (H6942), shared by H6947.

The Cologne PDScan 2020 text marks a minority of entries with a source
dictionary in square brackets, e.g. ``baby [DBHS]`` or ``[MW, APTE]``.  The
rule here is a direct transcription of the H6942 measurement
(Uprava ``papers/A68/sweeps/scripts-h6942/measure_pd_marked_inheritance.py``);
it reproduces that script's locked baseline exactly:

    107,630 entries, 1,801 entries with >=1 mark (1.67 %), 1,956 marks
    DBHS 852, PW 399, APTE 264, MW 245, VISVA 101, NT 84, VAC 11

The capped class (used for "marked entries") ignores brackets longer than 40
characters, including long MW brackets.  The uncapped mark total keeps long MW
brackets and counts an embedded VAC in a concrete source list; it is used only
for the mark counts, never for the entry class.  See H6942 for the two DBHS
gloss exclusions and the VAC rule.
"""
from __future__ import annotations

import re

SOURCES = (
    ("DBHS", r"dbhs"),
    ("PW", r"pw"),
    ("APTE", r"apte"),
    ("MW", r"mw"),
    ("VISVA", r"vi[śs]va"),
    ("NT", r"nt"),
    ("VAC", r"v[āa]cas"),
)
SOURCE_NAMES = tuple(name for name, _ in SOURCES)
MAX_BRACKET_CONTENT = 40

DBHS_POINTER = re.compile(r"^dbhs\.?\s+(?:q\.|s\.|under|cf\.|v\.?)", re.I)
DBHS_GLOSS = re.compile(r"^dbhs\.?\s+[a-z]", re.I)
LIST_FIRST = {"dbhs", "pw", "apte", "mw", "viśva", "visva", "nt"}


def leading_source(token: str) -> str | None:
    body = token.lstrip()
    for name, pattern in SOURCES:
        if re.match(pattern, body, re.I):
            return name
    return None


def entry_marks(entry: str, capped: bool = False) -> list[str]:
    marks: list[str] = []
    tokens = re.findall(r"\[([^\]]*)\]", entry)
    for token in tokens:
        name = leading_source(token)
        if name is None:
            continue
        if len(token) > MAX_BRACKET_CONTENT and (capped or name != "MW"):
            continue
        body = token.lstrip()
        if name == "DBHS" and DBHS_GLOSS.match(body) and not DBHS_POINTER.match(body):
            continue
        marks.append(name)
    if not capped:
        for token in tokens:
            parts = [p.strip().strip(".").lower() for p in re.split(r"[,;]", token)]
            if len(parts) > 1 and parts[0] in LIST_FIRST and "vācas" in parts:
                marks.append("VAC")
    return marks


def marked_entry(entry: str) -> bool:
    """True when the entry belongs to the H6942 1,801-entry capped class."""
    return bool(entry_marks(entry, capped=True))
