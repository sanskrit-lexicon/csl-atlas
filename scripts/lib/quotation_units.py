# -*- coding: utf-8 -*-
"""The PD quotation-level unit, as one reusable rule.

H6949. Full definition and rationale: reports/PD_QUOTATION_UNIT_2026-10-18.md.

Three units, nested, and only the middle one is the measurement unit:

  * **block** — one ``{#...#}`` SLP1 payload. Not the unit: it counts the
    headword, the morphemes of an etymology, and cross-referenced forms, and a
    single printed quotation is routinely split across two or more blocks at a
    line wrap.
  * **quotation** — a maximal run of consecutive blocks separated only by
    whitespace, immediately followed by a citation marker (PD: an inline
    siglum; PWG: an ``<ls>…</ls>`` tag). This is the unit.
  * **locus / attestation** — one citation marker, plus (PD only) each further
    reference carried by a bare locus after a ``;`` in the same citation tail
    (Reader's Guide X.v: only a limited number of citations is given from a
    book, further references are added). This is what PWG's ``<ls>`` counts.

Block 1 of every PD entry is the printed headword (99.87 % literally equal to
``<k1>``/``<k2>``; the residue are OCR and variant forms such as
``agnikarzu, agnikarzU``). It is never a quotation, and a boundary is forced
after it.
"""
from __future__ import annotations

import re

RE_SLP1 = re.compile(r"\{#(.*?)#\}")


def split_blocks(body):
    """Split a joined entry body into alternating text/block segments.

    Returns ``(segments, nblocks)`` where ``segments[0]`` is the text before
    block 1, ``segments[1]`` block 1, ``segments[2]`` the text after block 1,
    and so on — so the text following block *i* is ``segments[2 * i]``.
    """
    segs = RE_SLP1.split(body)
    return segs, (len(segs) - 1) // 2


def count_units(body, marker):
    """Count quotation units in one entry body.

    ``marker(tail)`` inspects the text following a block run and returns
    ``(n_loci, n_continuation_loci, tokens)``; a return with ``n_loci`` 0 means
    "not a citation", so the run is not a quotation.
    """
    segs, nblocks = split_blocks(body)
    quotations = 0
    blocks_in_quotations = 0
    loci = 0
    cont_loci = 0
    tokens = []

    i = 2                                   # block 1 is the headword
    while i <= nblocks:
        run = 1
        # a run continues across whitespace-only gaps, i.e. line wraps inside
        # one printed quotation
        while i + run <= nblocks and segs[2 * (i + run - 1)].strip() == "":
            run += 1
        n_loci, n_cont, found = marker(segs[2 * (i + run - 1)])
        if n_loci:
            quotations += 1
            blocks_in_quotations += run
            loci += n_loci
            cont_loci += n_cont
            tokens.extend(found)
        i += run

    return {
        "slp1_blocks": nblocks,
        "quotations": quotations,
        "blocks_in_quotations": blocks_in_quotations,
        "headword_block": 1 if nblocks else 0,
        "loci": loci,
        "continuation_loci": cont_loci,
        "attestations": loci + cont_loci,
        "tokens": tokens,
    }
