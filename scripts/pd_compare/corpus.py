"""csl-orig record and sense segmentation, in the per-dictionary conventions.

PWG/PW numbered Bedeutungen are the sense unit (lettered sub-senses fold into
their parent), MW splits senses across numbered sub-records plus a root record's
`<div n="to">` glosses, AP separates them with the U+2219 bullet.
"""
from __future__ import annotations

import re
from pathlib import Path

from .core import AP_BULLET, LS, MW_DIV, NUMBERED_SENSE, REC_HEADER

# ------------------------------------------------------------------ records / senses
def iter_records(path: Path):
    """Yield (header dict, body string) per <L>…<LEND> record, preserving file order."""
    header: dict[str, str] = {}
    body: list[str] = []
    inside = False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("<LEND>"):
                if inside:
                    yield header, "".join(body)
                inside = False
                body = []
            elif line.startswith("<L>") and not line.startswith("<LEND>"):
                header = dict(REC_HEADER.findall(line))
                inside = True
                body = []
            elif inside:
                body.append(line)


def _leading_text(chunk: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", chunk[:80])).strip()


def sense_chunks(code: str, body: str) -> list[str]:
    """The entry's sense divisions in document order, per the validated per-dict markers.

    PWG/PW: `<div>` Bedeutungen.  PWG numbers a sense ("— 1〉") and then subdivides it
            with lettered sub-senses ("a〉", "— b〉", "— β〉"); the unit that compares
            with PD's numbered `{@n@}` divisions is the NUMBERED sense, so a lettered
            chunk is folded into its parent — its quotations still count towards the
            parent's earliest date, exactly as a nested division does in PD.  The
            pre-first-`<div>` grammar/etymology head drops out.
    MW    : one numbered sub-record per sense, plus a root record's `<div n="to">` senses.
    AP    : the U+2219 bullet, which separates the numbered senses ("²1", "²2", …).
    """
    if code == "mw":
        return [c for c in MW_DIV.split(body) if c.strip()]
    if code == "ap":
        parts = body.split(AP_BULLET)
        return [c for c in (parts[1:] if len(parts) > 1 else parts) if c.strip()]
    segs = re.split(r"(?=<div\b)", body)
    segs = segs[1:] if len(segs) > 1 and "<div" not in segs[0] else segs
    out: list[str] = []
    for seg in segs:
        if not seg.strip():
            continue
        if not out or NUMBERED_SENSE.match(_leading_text(seg)):
            out.append(seg)
        else:
            out[-1] += seg          # lettered sub-sense: quotations join the parent sense
    return out


def entry_key(code: str, header: dict[str, str]) -> tuple[str, str]:
    """One entry = one headword+homonym; MW/AP split senses across numbered sub-records."""
    k1 = (header.get("k1") or "").strip()
    if code == "mw":
        return k1, (header.get("e") or header.get("h") or "1").strip()
    if code == "ap":
        return k1, (header.get("e") or "1").strip()
    return k1, (header.get("h") or "1").strip()

