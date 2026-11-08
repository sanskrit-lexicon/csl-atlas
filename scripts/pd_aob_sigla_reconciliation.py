#!/usr/bin/env python3
"""H6720 -- reconcile the printed AOB authority against the harvested PD sigla.

The PD-sigla harvest (``pd_siglum_families.tsv``, 5,106 sigla from PDScan's
letter-``a-`` text) and the printed ``Abbreviations of Books Quoted`` list
(PD repo ``AOB.md``, 42 pp OCR of the official KoshaSHRI PDF) describe the same
citation universe from two sides. H6707 joined every harvested siglum to an AOB
title (``pd_aob_siglum_title.tsv``: exact / fuzzy / title_* / gt_official_pdf /
census_unmatched). That join answers "is this citation explained by the printed
list?"; it does not answer the two questions this script exists for:

  Q1  What share of the harvested families is present in the printed AOB,
      and how much citation mass do they carry?
  Q2  Which AOB entries were never exercised under letter ``a-`` at all?

Q2 needs the opposite direction: an inventory of printed AOB *entries* (one
printed row each), then a match from entries to harvested sigla. The printed
list is a wrapped table in the OCR: an entry's siglum opens the row in
backticks, and its title/author/publication tail continues on the following
non-backtick lines. The parser below reassembles that tail; without it, tails
are truncated mid-word ("Padmapi" / "urana") and title matching collapses.

Matching (both routes recorded, never blended silently):

  route A  siglum identity -- casefold + diacritic-stripped skeleton equality.
           Skeleton length >= 3 always; shorter keys only on strict
           (punctuation-trimmed, diacritic-preserving) equality, because one-
           and two-letter sigla collide freely ("A." is a real AOB entry).
  route B  title identity -- the harvested siglum's adjudicated AOB title
           (H6707 join, non-``census_unmatched`` rows) against the entry's
           reassembled tail, skeleton, SequenceMatcher ratio >= 0.85 or one
           side contained in the other at length >= 12.

The documented trap (SanskritLexicography FINDINGS 457; H6724) is preserved:
skeletonisation does not merge ``MahāBhā.`` (Mahābhārata) with ``MahāBh.``
(Mahābhāṣya) -- "mahabha" vs "mahabh" -- and the selftest asserts the pair
never lands on the same entry.

Outputs (all deterministic, no network):

  data/pd/pd_aob_entries.tsv            the printed entry inventory + match
  data/pd/pd_aob_sigla_reconciliation.tsv  the discrepancy list
  data/pd/pd_aob_sigla_reconciliation.json aggregates, method, input hashes

H6941: the 681 `join_unconfirmed_at_entry` rows are re-checked against the printed
book's own text witnesses -- the PDF/A text layer of ``AOB.pdf`` (poppler
``pdftotext``) and the second OCR (``AOB_ocr.md``). A row whose adjudicated title
is found there (>=0.85 of the title skeleton) becomes
`join_confirmed_printed_text`: presence in the printed list is confirmed, the
siglum binding is still NOT bound at entry level. ``--check`` needs the same
witness inputs to reproduce the class.

``--check`` verifies the JSON aggregates *and* both row-level TSVs byte for byte.

Run:
  python3 scripts/pd_aob_sigla_reconciliation.py            # measure + write
  python3 scripts/pd_aob_sigla_reconciliation.py --check    # verify committed
  python3 scripts/pd_aob_sigla_reconciliation.py --selftest # trap + parser
  python3 scripts/pd_aob_sigla_reconciliation.py --aob /path/to/AOB.md
  python3 scripts/pd_aob_sigla_reconciliation.py --witness ../PD/AOB_ocr.md

Exit codes: 0 ok / 1 drift under --check or failed selftest / 2 input missing.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from dataset_meta import license_fields  # noqa: E402

ENTRY_MIN_TAIL_LETTERS = 6
#: H7096: the KoshaSHRI scan leaves a zero-width non-joiner (U+200C) after a
#: truncated Devanagari fragment ("... W. Calan — त्<ZWNJ>.").  The character is
#: invisible, breaks literal search/comparison and is an artifact of the scan,
#: not part of the printed title.  It is removed at the source (the tail), so
#: every emitted artifact regenerates byte-for-byte.  U+200D (ZWJ) is NOT
#: removed: it can be orthographically meaningful.
#:
#: The invisibles are written as escapes on purpose: a literal U+200C in the
#: source is itself invisible, and a reader cannot tell a deliberate literal
#: from a stray one (or tell which codepoint it is).
ZWNJ = "\u200c"
#: U+200B ZERO WIDTH SPACE and U+FEFF BOM/ZWNBSP are the other two invisibles
#: this scan is known to emit; all three are artifacts of the same class.
OCR_INVISIBLES = ZWNJ + "\u200b\ufeff"

YEAR_RE = re.compile(r"\b(1[89]\d\d|20[0-2]\d)\b")
LETTER_RE = re.compile(r"[A-Za-z\u00c0-\u024f]")
UPPER_START_RE = re.compile(r"^[A-Z\u00c0-\u024f]")
TOKEN_RE = re.compile(r"^\s*`([^`]*)`(.*)$")
PAGE_RE = re.compile(r"^## Page (\d+)$")
SIGLUM_WORD_RE = re.compile(r"^[A-Z\u00c0-\u024f][^\s]{0,24}$")
TITLE_MIN_RATIO = 0.85
TITLE_MIN_CONTAINED = 12

ROUTE = {"A": "siglum", "B": "title"}
# a deliberately small, auditable stop-list of OCR fragments that are not
# sigla at all -- they are counted, reported and excluded from Q2's denominators
NOT_A_SIGLUM = {
    "abbreviation", "abbreviations", "name", "names", "page", "line", "vol",
    "author", "editor", "editor", "edition", "reference", "book", "books",
    "of", "and", "the",
}

# --- H6960: the wrap-fragment rule -------------------------------------------
#
# H6720 folded *every* dotless backticked token into the previous entry. That
# catches OCR wraps ("Lakshmidha" + "ra Katre.") but also swallows real printed
# entries whose siglum lost its terminal punctuation to the wrap
# ("AtmaU.1", "AnyaS( Ni)", "P. Astadhy", "Kad. Kadam"). H6960 re-adjudicates
# the direction from the tail:
#
#   * a capital-initial bibliographic tail (title/author, publisher+number or
#     a year) proves the token is an entry, not a continuation;
#   * a lowercase / part-word tail ("ra Katre.", "svami", "attagobhakara")
#     proves it is a continuation of the previous row;
#   * a very short terminal token ("N.", "Pt.", "Siv:", "K:") with a lowercase
#     tail is a part-word wrap, not a siglum, even though it ends in
#     ``.,;:*-``.
#
# The promoted/false lists below are the hand adjudication from AOB.md checked
# against the second OCR witness (PD/AOB_ocr.md); --selftest re-derives both
# from the source and fails if the parse stops matching them.
PUBLISHER_RE = re.compile(
    r"\b(?:NSP|GOS|KM|ASS|TSS|HSS|KSS|MUSS|DLJP|YJGM|SJS|VVP|BORI|BI|BSS|"
    r"BSPS|MGOMS|ALS|SKS|PSP|SVS|VSP|VSS|TSWS|IFI|GPP|OUSA|ChSS|CHSS|MLSPS|"
    r"VSGM|BVP|HOS|AOS|BJS|BJSS|BVSM|MDJG)\b[.,]?\s*\d")

#: 29 printed entries H6720 folded as wrap fragments (hand-checked; the second
#: OCR witness shows each as its own siglum). Keyed by the token as printed.
H6960_PROMOTED = (
    "AnyaS( Ni)", "AtmaU.1", "AVP.)", "\u2018BhavU", "BrahmSi", "Chanda",
    "DagavaC, a", "EkaNa. (Vi)", "GitaBh.( Ra.)", "HamsDii.( Ri.)",
    "Kad. Kadam", "Linganu, (Sa.)", "Linganu, (Va.)", "Linganu. (Va.)",
    "Naga. Nagan", "01101)", "P. Astadhy", "PranU.1", "PranU.2",
    "Praudha. ae", "SabdaBhePra.(Pa.)", "SabdaRa.(Su.)", "SabdaRa.(Va.)",
    "SaddarSa.(Ra.)", "SmigaTi.( Ra.)", "TajiNi", "TarkSarh.( A.)",
    "TatpaT.( Va.)", "UnmaRa( Vi.)",
)

#: "recoveries" H6932 counted that are really continuations: the 10 parser-only
#: rows named in the handoff (N., Pt., Siv: x3, K:, Sh:, Par:, Av:, Ram) plus
#: 5 rows R1 also counts (Bh: x2, Ny: x2, Ra,). The first two keep the OCR's
#: leading fragment; the siglum H6720 read off them is the second element.
H6960_FALSE_RECOVERIES = (
    ("and N. G. 8:", "N."),
    ("111, Pt. Siv:", "Pt."),
    ("Siv:", "Siv:"), ("Siv:", "Siv:"), ("Siv:", "Siv:"),
    ("K:", "K:"),
    ("Sh:", "Sh:"),
    ("Par:", "Par:"),
    ("Av:", "Av:"),
    ("Ram Acharya", "Ram"),
    ("Bh:", "Bh:"), ("Bh:", "Bh:"),
    ("Ny:", "Ny:"), ("Ny:", "Ny:"),
    ("Ra,", "Ra,"),
)

#: non-entry reasons that continue the previous row's tail (everything else
#: resets it, exactly as H6720 did for a terminal token with no usable tail)
FOLD_REASONS = {
    "merged_without_title",
    "first_word_punct_fragment",
    "dotless_fragment",
    "short_lowercase_continuation",
    "leading_continuation",
}

#: a small named sample of the 136+ genuine wrap fragments that must stay
#: folded in both directions (start + tail as printed)
H6960_FRAGMENT_SAMPLE = (
    ("Lakshmidha", "ra Katre."),
    ("Gos", "svami Damodara Sastri."),
    ("Pt. Durgapr", "asida and Wasudev Laxman Sastri: Pan"),
    ("Has", "rvard University Press, Cambridge, Mass. 1957"),
    ("Bhi", "arati Series 2-7; Varanasi 1965-67"),
    ("De", "partment 2, University of Madras 1934"),
    ("Vy", "yavaharakanda Pt. 2, 1916, 317-773"),
    ("Sra", "iddhakanda, 1918, 1-452"),
    ("Pas", "dma Prasad Upadhyaya; Samayaprakaga (1935)"),
    ("Bs Sar", "uskrit Vidyamandira, Ahmedabad.1966"),
)


def _first_alpha(s):
    for ch in s:
        if ch.isalpha():
            return ch
    return ""


def _starts_lower(s):
    ch = _first_alpha(s or "")
    return bool(ch) and ch.islower()


def _has_bibliographic_tail(rest):
    """True when the tail reads as ``Title/Author, PUB. N, YEAR``."""
    rest = (rest or "").strip()
    if not rest or _starts_lower(rest):
        return False
    return bool(YEAR_RE.search(rest)) or bool(PUBLISHER_RE.search(rest))


def _has_internal_punct(s):
    return any(ch in ".,;:*-" for ch in (s or ""))


def classify_aob_token(clean, token, rest, merged):
    """H6960: (is_entry, garbled, reason) for one backticked token.

    ``clean`` is the token with OCR quote/bracket prefixes stripped; ``merged``
    is H6720's ``Siglum Title`` token test. The caller still applies the
    tail-length test, so a terminal siglum with no tail is dropped as before.
    """
    words = clean.split()
    first = words[0] if words else ""
    terminal = clean[-1:] in ".,;:*-"
    nonascii = any(ord(ch) > 127 for ch in clean)

    if not terminal and not nonascii:
        # --- dotless ASCII: the repaired rule -------------------------------
        if merged:
            # ``Siglum Title`` tokens already carry their title; only a bare
            # two-word token with no title ("Ram Acharya") is a wrap.
            if rest.strip() or first[-1:] in ".,;:*-":
                return True, False, "merged"
            return False, False, "merged_without_title"
        if UPPER_START_RE.match(clean):
            if first[-1:] in ".,;:*-" and len(words) > 1:
                if YEAR_RE.search(rest) and _has_internal_punct(clean):
                    return True, False, "first_word_punct_year"
                if _has_bibliographic_tail(rest):
                    return True, False, "first_word_punct_bib"
                if (_has_internal_punct(clean) and rest.count(",") >= 2
                        and len(rest) >= 20):
                    return True, False, "punct_and_commas"
                return False, False, "first_word_punct_fragment"
            if _has_bibliographic_tail(rest):
                return True, False, "bibliographic_tail"
            if (_has_internal_punct(clean) and rest.count(",") >= 2
                    and len(rest) >= 20):
                return True, False, "punct_and_commas"
            return False, False, "dotless_fragment"
        # non-uppercase dotless: only a digit-only garble can be a siglum
        if (re.fullmatch(r"[0-9]+\)", clean) and rest.strip()[:1].isupper()
                and rest.count(",") >= 2 and YEAR_RE.search(rest)):
            return True, True, "numeric_garble"
        return False, False, "dotless_fragment"

    # --- terminal punctuation or non-ASCII: H6720 rules + the H6960 guard ---
    if (terminal and not merged and len(words) == 1
            and letters(clean) <= 4 and _starts_lower(rest)):
        # "Siv:" / "K:" / "Bh:" / "Ny:" -- a word split at the wrap, even
        # when the rest of the row carries a year
        return False, False, "short_lowercase_continuation"
    if not UPPER_START_RE.match(clean):
        lead = words[0] if words else ""
        ascii_word = re.fullmatch(r"[A-Za-z]+[.,;:]*", lead) is not None
        ascii_digits = re.fullmatch(r"[0-9]+[.,;:]*", lead) is not None
        if ((ascii_word and lead[:1].islower()) or ascii_digits) and _starts_lower(rest):
            # "and N. G. 8:" / "111, Pt. Siv:" -- the OCR kept a piece of the
            # preceding row in the token; the Devanagari-garbled real entries
            # ("18०8, Naradas") are untouched because their lead is not ASCII
            return False, False, "leading_continuation"
    tail_ok = (
        letters(rest) >= ENTRY_MIN_TAIL_LETTERS
        or bool(YEAR_RE.search(rest))
        or merged
    )
    if UPPER_START_RE.match(clean):
        return (tail_ok, False, "terminal" if terminal else "nonascii_upper")
    latin = [w for w in words if SIGLUM_WORD_RE.match(w)]
    ok = bool(latin) and tail_ok and letters(rest) >= ENTRY_MIN_TAIL_LETTERS
    return (ok, ok, "garbled_start" if ok else "continuation")


# --- normalisation -----------------------------------------------------------

def strip_ocr_invisibles(s):
    """H7096 -- drop the scan's invisible artifacts from a printed string.

    The KoshaSHRI OCR emits a zero-width non-joiner after a truncated
    Devanagari fragment.  It is invisible on screen, absent from the printed
    book, and breaks any literal comparison against the title.  Removing it
    *here*, at the source, is what keeps ``pd_aob_entries.tsv`` regenerable:
    the rule lives in the generator instead of a hand edit to the output
    (which is what made the ``--check`` gate red in #598).

    The characters are removed outright, not replaced by a space: in
    Devanagari a ZWNJ is intra-word, never a word separator, so removing it
    can never glue two words together.
    """
    return (s or "").translate({ord(ch): None for ch in OCR_INVISIBLES})


def strict_key(s):
    """Punctuation-trimmed, whitespace-collapsed, casefolded; diacritics kept."""
    s = (s or "").strip()
    s = re.sub(r"[.,;:*\u2018\u2019\"')\]]+$", "", s)
    s = s.strip("([{")
    s = re.sub(r"\s+", " ", s)
    return s.casefold()


def skeleton(s):
    """Diacritic-free alphanumeric skeleton: 'MahāBhā.' -> 'mahabha'."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.casefold())


def letters(s):
    return len(LETTER_RE.findall(s or ""))


def sha256_of(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# --- AOB parse ---------------------------------------------------------------

def parse_aob(text):
    """One entry per printed row: siglum + the tail reassembled across wraps.

    A printed AOB entry opens with its siglum in backticks. The OCR wraps the
    row, so following lines without a backtick continue the same entry until
    the next siglum line (or a page break). A ``## Page N`` marker is recorded
    but does not break the tail: PD's printed table runs entries across pages.
    """
    entries = []
    page = 0
    cur = None
    for line in text.splitlines():
        m = PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
            continue
        m = TOKEN_RE.match(line)
        if not m:
            if cur is not None and line.strip():
                cur["tail_parts"].append(line.strip())
            continue
        token = m.group(1).strip()
        rest = m.group(2).strip()
        # the OCR sometimes opens the cell with stray quotes/brackets before a
        # perfectly good siglum ("‘“MahaBha, Mahabh | arata, BORI..."), which
        # the upper-case test must not read as a garbled row
        clean = token.lstrip("\u2018\u2019\u201c\u201d\"'`([{*")
        words = clean.split()
        merged = (
            len(words) > 1
            and bool(SIGLUM_WORD_RE.match(words[0]))
            and letters(token) >= 10
        )
        is_entry, garbled, reason = classify_aob_token(
            clean, token, rest, merged)
        if not is_entry:
            if reason in FOLD_REASONS:
                if cur is not None:
                    cur["tail_parts"].append(token)
                    if rest:
                        cur["tail_parts"].append(rest)
            else:
                cur = None
            continue
        tail_ok = (
            letters(rest) >= ENTRY_MIN_TAIL_LETTERS
            or bool(YEAR_RE.search(rest))
            or merged
        )
        if not tail_ok:
            cur = None
            continue
        if garbled:
            latin = [w for w in words if SIGLUM_WORD_RE.match(w)]
            siglum = latin[0] if latin else clean
        else:
            siglum = words[0] if merged else (clean or token)
        cur = {
            "page": page,
            "siglum_raw": siglum,
            "token_raw": token,
            "merged_token": merged,
            "garbled_start": garbled,
            "tail_parts": [rest] if rest else [],
        }
        entries.append(cur)
    for i, e in enumerate(entries, 1):
        e["entry_id"] = "AOB-%04d" % i
        e["tail"] = re.sub(
            r"\s+", " ",
            strip_ocr_invisibles(" ".join(e.pop("tail_parts")))).strip()
        e["strict"] = strict_key(e["siglum_raw"])
        e["skeleton"] = skeleton(e["siglum_raw"])
        # a printed entry may carry an edition suffix -- "RajTa,(Ka.)",
        # "RajTa.(Jo.)" -- while PD cites the work under the bare "RājTa.";
        # the base key groups those editions without merging distinct works
        e["base_skeleton"] = skeleton(re.sub(r"\([^)]*\)", "", e["siglum_raw"]))
        e["junk"] = e["skeleton"] in NOT_A_SIGLUM or e["strict"].split()[0] in NOT_A_SIGLUM
        tail = e["tail"]
        e["wellformed"] = bool(
            len(e["skeleton"]) >= 2
            and not e["junk"]
            and letters(tail) >= 15
            and len(tail.split()) >= 2
            and not re.match(r"^\d", tail.strip())
        )
    return entries


# --- matching ----------------------------------------------------------------

def build_entry_index(entries):
    by_strict = {}
    by_skeleton = {}
    by_base = {}
    for e in entries:
        by_strict.setdefault(e["strict"], []).append(e)
        if e["skeleton"]:
            by_skeleton.setdefault(e["skeleton"], []).append(e)
        if e["base_skeleton"]:
            by_base.setdefault(e["base_skeleton"], []).append(e)
    return by_strict, by_skeleton, by_base


CLEAN_SHORT_RE = re.compile(r"^[A-Za-z]{1,2}[.,]$")


def _short_ok(entry):
    """A one/two-letter siglum may only answer a *clean* printed short form
    whose tail opens a title.  Without this, "A.)  Tantrasara..." (a mangled
    TantraS. siglum) would answer RājTa.-scale nothing -- it would answer the
    harvested "A." and silently absorb 6,451 occurrences."""
    return (CLEAN_SHORT_RE.match(entry.get("siglum_raw", "")) is not None
            and entry.get("tail", "")[:1].isupper())


def match_a(harvest_siglum, by_strict, by_skeleton, by_base):
    """route A -- siglum identity.  Returns (entries, strength); ``entries`` is
    a list because an edition-suffixed group ("RajTa,(Ka.)", "RajTa.(Jo.)")
    legitimately answers one printed work siglum."""
    sk = skeleton(harvest_siglum)
    st = strict_key(harvest_siglum)
    if len(sk) < 3:
        if st and st in by_strict and len(by_strict[st]) == 1 and _short_ok(by_strict[st][0]):
            return by_strict[st], "strict_short"
        return [], None
    if st and st in by_strict and len(by_strict[st]) == 1:
        return by_strict[st], "strict"
    if len(sk) >= 3 and sk in by_skeleton:
        ents = by_skeleton[sk]
        if len(ents) == 1:
            return ents, "skeleton"
    if len(sk) >= 3 and sk in by_base:
        return by_base[sk], "base_skeleton"
    return [], None


class TitleMatcher(object):
    """route B -- harvested-siglum AOB title -> printed entry tail.

    Pre-computes the entry tail skeletons once; a title is looked up at most
    once (the join carries 1,081 distinct titles for 3,224 joined sigla).
    Containment is the cheap first pass (the join's title is normally the head
    of the reassembled tail); a diacritic-free ratio >= 0.85 over same-initial
    entries is the fallback for OCR-damaged heads.
    """

    def __init__(self, entries):
        self.items = [(e, skeleton(e["tail"])[:240])
                      for e in entries if not e["junk"]]
        self.cache = {}

    def find(self, title):
        ts = skeleton(title)[:160]
        if len(ts) < 6:
            return None, None
        if ts in self.cache:
            return self.cache[ts]
        best = None
        best_r = 0.0
        for e, es in self.items:
            if not es:
                continue
            if len(ts) >= TITLE_MIN_CONTAINED and (ts in es or es in ts):
                r = 1.0
            elif ts[:1] == es[:1] and 0.5 <= (len(ts) / float(len(es))) <= 2.0:
                r = difflib.SequenceMatcher(None, ts, es[:len(ts) + 10]).ratio()
            else:
                continue
            if r > best_r:
                best, best_r = e, r
            if best_r == 1.0:
                break
        res = ((best, round(best_r, 3))
               if best is not None and best_r >= TITLE_MIN_RATIO else (None, None))
        self.cache[ts] = res
        return res


# --- printed-book witnesses (H6941) ------------------------------------------

WITNESS_MIN_COVERAGE = 0.85
WITNESS_ANCHOR_OCCURRENCES = 40


def pdf_text(path):
    """The PDF/A text layer, via poppler's pdftotext. None when unavailable."""
    try:
        out = subprocess.run(["pdftotext", str(path), "-"],
                             capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout


def load_witnesses(paths):
    """[(label, text)] for every witness that can be read; [] if none."""
    got = []
    for raw in paths:
        if not raw:
            continue
        path = Path(raw)
        if not path.exists():
            continue
        if path.suffix.lower() == ".pdf":
            text = pdf_text(path)
            if text is None:
                print("[WARN] witness unreadable (pdftotext missing or empty): %s"
                      % path, file=sys.stderr)
                continue
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
        got.append((str(path), text))
    return got


def title_coverage(ts, corpus):
    """How much of a title skeleton is present in a witness skeleton.

    0-1 coverage = longest common substring over a window anchored on the
    title's first 8 chars and on its longest words. Short titles (<8 chars)
    only count on exact containment -- a six-letter skeleton has no room for
    a tolerant match.
    """
    if not ts:
        return 0.0
    if len(ts) < 8:
        return 1.0 if ts in corpus else 0.0
    anchors = {ts[:8]}
    words = [w for w in re.split(r"[^a-z0-9]+", ts) if len(w) >= 6]
    anchors.update(w[:8] for w in sorted(set(words), key=len, reverse=True)[:3])
    best = 0.0
    for a in anchors:
        i = corpus.find(a)
        seen = 0
        while i != -1 and seen < WITNESS_ANCHOR_OCCURRENCES:
            window = corpus[i:i + len(ts) + 12]
            hit = difflib.SequenceMatcher(None, ts, window).find_longest_match(
                0, len(ts), 0, len(window)).size
            best = max(best, hit / float(len(ts)))
            if best >= 0.99:
                return best
            i = corpus.find(a, i + 1)
            seen += 1
    return best


# --- measure -----------------------------------------------------------------

def measure(aob_path, families_path, join_path, witnesses=None):
    text = aob_path.read_text(encoding="utf-8")
    entries = parse_aob(text)
    by_strict, by_skeleton, by_base = build_entry_index(entries)

    with open(families_path, encoding="utf-8", newline="") as fh:
        families = list(csv.DictReader(fh, delimiter="\t"))
    with open(join_path, encoding="utf-8", newline="") as fh:
        join = {r["siglum"]: r for r in csv.DictReader(fh, delimiter="\t")}

    matcher = TitleMatcher(entries)
    exercised = {}          # entry_id -> list of (siglum, route, evidence)
    harvest_rows = []
    for fam in families:
        sig = fam["siglum"]
        count = int(fam["count"] or 0)
        j = join.get(sig, {})
        jtype = j.get("match_type", "")
        title = (j.get("title") or "").strip()
        entries_hit, strength = match_a(sig, by_strict, by_skeleton, by_base)
        route = "A" if entries_hit else None
        evidence = strength if entries_hit else None
        if not entries_hit and title:
            one, ratio = matcher.find(title)
            if one is not None:
                entries_hit, route = [one], "B"
                evidence = "title_%.2f" % (ratio or 0.0)
        for entry in entries_hit:
            if not entry["junk"]:
                exercised.setdefault(entry["entry_id"], []).append(
                    (sig, route, evidence))
        entry = entries_hit[0] if entries_hit else None
        harvest_rows.append({
            "siglum": sig,
            "count": count,
            "class": fam.get("class", ""),
            "harvest_match_type": jtype,
            "aob_title": title,
            "entry": entry,
            "route": route,
            "evidence": evidence,
        })

    # route-A rescue of rows H6707 left unmatched -- a join miss, not a gap
    rescued = [r for r in harvest_rows
               if r["route"] == "A" and r["harvest_match_type"] == "census_unmatched"]
    in_aob = [r for r in harvest_rows if r["entry"] is not None and not r["entry"]["junk"]]
    not_in_aob = [r for r in harvest_rows if r["entry"] is None]

    total_occ = sum(r["count"] for r in harvest_rows)
    in_occ = sum(r["count"] for r in in_aob)
    join_rows = [r for r in harvest_rows
                 if r["harvest_match_type"] and r["harvest_match_type"] != "census_unmatched"]
    join_occ = sum(r["count"] for r in join_rows)
    corrected = [r for r in harvest_rows
                 if (r["harvest_match_type"] and r["harvest_match_type"] != "census_unmatched")
                 or r["route"] == "A"]
    corrected_occ = sum(r["count"] for r in corrected)

    by_class = {}
    for cls in ("primary", "secondary", "structural"):
        rows = [r for r in harvest_rows if r["class"] == cls]
        hit = [r for r in rows if r["entry"] is not None and not r["entry"]["junk"]]
        by_class[cls] = {
            "families": len(rows),
            "in_aob": len(hit),
            "share_pct": round(100.0 * len(hit) / len(rows), 2) if rows else None,
            "occurrences": sum(r["count"] for r in rows),
            "occurrences_in_aob": sum(r["count"] for r in hit),
        }

    entries_out = []
    for e in entries:
        hits = exercised.get(e["entry_id"], [])
        entries_out.append({
            "entry_id": e["entry_id"],
            "page": e["page"],
            "siglum": e["siglum_raw"],
            "siglum_skeleton": e["skeleton"],
            "merged_token": "yes" if e["merged_token"] else "no",
            "garbled_start": "yes" if e["garbled_start"] else "no",
            "junk": "yes" if e["junk"] else "no",
            "wellformed": "yes" if e["wellformed"] else "no",
            "exercised": "yes" if hits else "no",
            "routes": ";".join(sorted({h[1] for h in hits})),
            "harvested_sigla": ";".join(h[0] for h in hits),
            "title_tail": e["tail"],
        })
    usable = [e for e in entries if not e["junk"]]
    wellformed = [e for e in entries if e["wellformed"]]
    never = [e for e in entries_out
             if e["exercised"] == "no" and e["wellformed"] == "yes"]

    # near-miss lookup for never-cited entries: a printed siglum can be OCR-
    # mangled past skeleton identity while the work IS cited. Report the best
    # harvested candidate -- never silently promote it to a match.
    harvest_skel = [(skeleton(r["siglum"]), r["siglum"]) for r in harvest_rows]
    by_prefix = {}
    for sk, sig in harvest_skel:
        if len(sk) >= 3:
            by_prefix.setdefault(sk[:3], []).append(sk)

    discrepancies = []
    near = 0
    for e in entries_out:
        if e["exercised"] == "no":
            if e["junk"] == "yes":
                kind = "junk_ocr"
            elif e["wellformed"] != "yes":
                kind = "aob_fragment_or_garble"
            else:
                kind = "aob_never_cited"
            evidence = "no siglum or title route matched a harvested family"
            if kind == "aob_never_cited" and e["wellformed"] == "yes":
                sk = e["siglum_skeleton"]
                best, best_r = "", 0.0
                for cand in by_prefix.get(sk[:3], []):
                    r = difflib.SequenceMatcher(None, sk, cand).ratio()
                    if r > best_r:
                        best, best_r = cand, r
                if best and best_r >= 0.85:
                    kind = "aob_never_cited_near_miss"
                    evidence = ("nearest harvested siglum %r at %.2f -- likely an OCR "
                                "variant, not a gap" % (best, best_r))
                    near += 1
            discrepancies.append({
                "kind": kind,
                "aob_siglum": e["siglum"],
                "aob_page": e["page"],
                "aob_title": e["title_tail"][:160],
                "harvest_siglum": "",
                "harvest_count": "",
                "harvest_class": "",
                "evidence": evidence,
            })
    unconfirmed = 0
    for r in not_in_aob:
        if r["harvest_match_type"] == "census_unmatched" or not r["harvest_match_type"]:
            kind = "harvest_not_in_aob"
            evidence = r["harvest_match_type"] or "no row in the H6707 join"
        else:
            kind = "join_unconfirmed_at_entry"
            evidence = ("H6707 join=%s (title %r) but no printed entry could be "
                        "re-located for it in this OCR pass"
                        % (r["harvest_match_type"], r["aob_title"][:60]))
            unconfirmed += 1
        discrepancies.append({
            "kind": kind,
            "aob_siglum": "",
            "aob_page": "",
            "aob_title": "",
            "harvest_siglum": r["siglum"],
            "harvest_count": r["count"],
            "harvest_class": r["class"],
            "evidence": evidence,
        })
    # H6941: the printed book's own text witnesses (PDF/A text layer, second
    # OCR) can confirm a join row whose entry the AOB.md OCR mangled. This
    # confirms *presence of the title in the printed list*, never the row's
    # siglum binding -- the class says so.
    witness_summary = None
    if witnesses:
        witness_skel = [(label, skeleton(text)) for label, text in witnesses]
        confirmed = 0
        for row in discrepancies:
            if row["kind"] != "join_unconfirmed_at_entry":
                continue
            title = join.get(row["harvest_siglum"], {}).get("title", "")
            ts = skeleton(title)[:160]
            if not ts:
                continue
            best_cov, best_src = 0.0, ""
            for label, corpus in witness_skel:
                cov = title_coverage(ts, corpus)
                if cov > best_cov:
                    best_cov, best_src = cov, label
            if best_cov >= WITNESS_MIN_COVERAGE:
                row["kind"] = "join_confirmed_printed_text"
                row["evidence"] = ("adjudicated title found in the printed text "
                                   "witness %s at coverage %.2f"
                                   % (Path(best_src).name, best_cov))
                confirmed += 1
        join_entry_rows = sum(1 for r in harvest_rows
                              if r["harvest_match_type"]
                              and r["harvest_match_type"] != "census_unmatched")
        join_entry_located = sum(
            1 for r in harvest_rows
            if r["harvest_match_type"] and r["harvest_match_type"] != "census_unmatched"
            and r["entry"] is not None and not r["entry"]["junk"])
        witness_summary = {
            "sources": [{"path": Path(lbl).name,
                         "sha256": sha256_of(Path(lbl)),
                         "text_sha256": hashlib.sha256(
                             txt.encode("utf-8")).hexdigest(),
                         "chars": len(txt)} for lbl, txt in witnesses],
            "confirmed_rows": confirmed,
            "join_rows": join_entry_rows,
            "join_rows_entry_located": join_entry_located,
            "coverage_before_pct": round(
                100.0 * join_entry_located / join_entry_rows, 2) if join_entry_rows else None,
            "coverage_after_pct": round(
                100.0 * (join_entry_located + confirmed) / join_entry_rows, 2)
                if join_entry_rows else None,
            "min_coverage": WITNESS_MIN_COVERAGE,
        }

    for r in rescued:
        discrepancies.append({
            "kind": "join_miss_siglum_equal",
            "aob_siglum": r["entry"]["siglum_raw"],
            "aob_page": r["entry"]["page"],
            "aob_title": r["entry"]["tail"][:160],
            "harvest_siglum": r["siglum"],
            "harvest_count": r["count"],
            "harvest_class": r["class"],
            "evidence": "H6707 join=census_unmatched; route %s (%s)"
                        % (r["route"], r["evidence"]),
        })

    summary = {
        "generated_by": "H6720/H6960 scripts/pd_aob_sigla_reconciliation.py "
                        "(DeepSeek v4.1 Flash, deepseek-flash)",
        "measured_on": "2026-10-18",
        "method": {
            "aob_universe": "PD/AOB.md OCR entries (siglum opens a backticked row; "
                            "tail reassembled across OCR wraps)",
            "fragment_rule": "H6960: dotless tokens are entries when the tail is a "
                             "capital-initial bibliographic tail (or the first word "
                             "already ends the siglum); lowercase/part-word tails fold",
            "harvest_universe": "data/pd/pd_siglum_families.tsv (PDScan letter-a-)",
            "route_a": "siglum identity: strict key, else diacritic-free skeleton "
                       "(len>=3, unique); shorter sigla require strict equality",
            "route_b": "title identity: H6707 adjudicated title vs entry tail, "
                       "skeleton, ratio>=%.2f or containment>=%d chars"
                       % (TITLE_MIN_RATIO, TITLE_MIN_CONTAINED),
            "trap": "MahāBhā. (Mahābhārata) and MahāBh. (Mahābhāṣya) stay distinct: "
                    "mahabha vs mahabh; asserted in --selftest",
            "witness": "H6941: a join row whose adjudicated title is found in a "
                       "printed-book text witness (PDF/A text layer via pdftotext, or "
                       "the second OCR) at >=%.2f skeleton coverage is reclassified "
                       "join_confirmed_printed_text -- presence confirmed, siglum "
                       "binding still unbound" % WITNESS_MIN_COVERAGE,
            "not_moved": "frozen headline values 25.2% / 77.9% are not touched here",
            "invisibles": "H7096: the scan's invisible artifacts (U+200C ZWNJ, "
                          "U+200B, U+FEFF) are removed from the printed tail at the "
                          "source, so every emitted artifact regenerates "
                          "byte-for-byte; U+200D ZWJ is kept (it can be "
                          "orthographically meaningful)",
        },
        "source_aob": {
            "path": "PD/AOB.md (sanskrit-lexicon/PD, OCR of the official KoshaSHRI PDF)",
            "sha256": sha256_of(aob_path),
            "lines": len(text.splitlines()),
            "entries": len(entries),
            "entries_usable": len(usable),
            "merged_tokens": sum(1 for e in entries if e["merged_token"]),
            "junk_tokens": sum(1 for e in entries if e["junk"]),
        },
        "harvest": {
            "families": len(families),
            "occurrences": total_occ,
            "in_aob": len(in_aob),
            "share_pct": round(100.0 * len(in_aob) / len(families), 2),
            "occurrences_in_aob": in_occ,
            "mass_share_pct": round(100.0 * in_occ / total_occ, 2) if total_occ else None,
            "not_in_aob": len(not_in_aob),
            "join_misses_rescued": len(rescued),
            "by_class": by_class,
            "join_claim": {
                "families": len(join_rows),
                "share_pct": round(100.0 * len(join_rows) / len(families), 2),
                "occurrences": join_occ,
                "mass_share_pct": round(100.0 * join_occ / total_occ, 2) if total_occ else None,
            },
            "join_claim_plus_siglum_identity": {
                "families": len(corrected),
                "share_pct": round(100.0 * len(corrected) / len(families), 2),
                "occurrences": corrected_occ,
                "mass_share_pct": round(100.0 * corrected_occ / total_occ, 2)
                                  if total_occ else None,
            },
            "entry_located": {
                "families": len(in_aob),
                "share_pct": round(100.0 * len(in_aob) / len(families), 2),
                "occurrences": in_occ,
                "mass_share_pct": round(100.0 * in_occ / total_occ, 2) if total_occ else None,
            },
        },
        "aob": {
            "entries_usable": len(usable),
            "entries_wellformed": len(wellformed),
            "exercised": len(wellformed) - len(never),
            "never_cited": len(never),
            "never_cited_pct": round(100.0 * len(never) / len(wellformed), 2)
                                if wellformed else None,
            "fragments_or_garble": sum(1 for e in entries_out
                                       if e["wellformed"] == "no" and e["junk"] == "no"),
        },
        "h6960": {
            "rule": "dotless token = entry when its tail is a capital-initial "
                    "bibliographic tail (title/author + publisher+number or year), "
                    "or when its first word already carries the siglum's terminal "
                    "punctuation; a lowercase/part-word tail folds it back",
            "usable_before": 1423,
            "promoted_entries": len(H6960_PROMOTED),
            "false_recoveries": len(H6960_FALSE_RECOVERIES),
            "usable_after": len(usable),
            "arithmetic": "1423 + %d - %d = %d"
                          % (len(H6960_PROMOTED), len(H6960_FALSE_RECOVERIES),
                             len(usable)),
            "promoted_tokens": list(H6960_PROMOTED),
            "false_recovery_tokens": [tok for tok, _ in H6960_FALSE_RECOVERIES],
            "false_recovery_sigla": sorted({sig for _, sig in H6960_FALSE_RECOVERIES}),
            "residual_known_false": ["both-rows outside the 119 recoveries "
                                     "(e.g. Pt. Durgapr., R.) are not re-adjudicated "
                                     "in this pass; see report Caveats"],
            "headline_absences": {
                "kadambari": "Kad. Kadam -> Kadambari, Bana, BS(P)S. 24, 1885",
                "astadhyayi": "P. Astadhy -> Astadhyayi, Panini, Leipzig, 1887",
            },
            "linganu_editions": 7,
        },
        "inputs": {
            "families_sha256": sha256_of(families_path),
            "join_sha256": sha256_of(join_path),
        },
        "witness": witness_summary,
        "discrepancies": {
            "aob_never_cited": len(never) - near,
            "aob_fragment_or_garble": sum(1 for e in entries_out
                                          if e["exercised"] == "no"
                                          and e["wellformed"] != "yes"
                                          and e["junk"] != "yes"),
            "aob_never_cited_near_miss": near,
            "harvest_not_in_aob": len(not_in_aob) - unconfirmed,
            "join_unconfirmed_at_entry": sum(
                1 for d in discrepancies if d["kind"] == "join_unconfirmed_at_entry"),
            "join_confirmed_printed_text": sum(
                1 for d in discrepancies if d["kind"] == "join_confirmed_printed_text"),
            "join_miss_siglum_equal": len(rescued),
            "junk_ocr": sum(1 for e in entries_out if e["junk"] == "yes"),
        },
    }
    return entries_out, discrepancies, summary


# --- writers / checks --------------------------------------------------------

def render_tsv(cols, rows):
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, delimiter="\t",
                       lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def write_tsv(path, cols, rows):
    path.write_text(render_tsv(cols, rows), encoding="utf-8")


ENTRY_COLS = ["entry_id", "page", "siglum", "siglum_skeleton", "merged_token",
              "garbled_start", "junk", "wellformed", "exercised", "routes",
              "harvested_sigla", "title_tail"]
DISC_COLS = ["kind", "aob_siglum", "aob_page", "aob_title", "harvest_siglum",
             "harvest_count", "harvest_class", "evidence"]


def selftest(aob_path=None):
    ok = True
    # 1. parser: wrapped tail is reassembled, merged siglum split off
    text = ("## Page 1\n"
            "`PadmP.` Padmapi\n"
            "urana, ASS. 1893, Vishvanatha Narayana\n"
            "`AllaU. Allopanisad` Allopanisad, MB, 1970\n")
    ents = parse_aob(text)
    assert len(ents) == 2, ents
    assert ents[0]["siglum_raw"] == "PadmP.", ents[0]
    assert "urana" in ents[0]["tail"], ents[0]
    assert ents[1]["merged_token"] is True and ents[1]["siglum_raw"] == "AllaU.", ents[1]
    print("ok  parser: tails reassembled, merged tokens split (%d entries)" % len(ents))
    # 1b. H6960: both directions of the repaired fragment rule
    text = ("## Page 1\n"
            "`PadmP.` Padmapi\n"
            "urana, ASS. 1893, Vishvanatha Narayana\n"
            "`AllaU. Allopanisad` Allopanisad, MB, 1970\n"
            "`Lakshmidha` ra Katre.\n"
            "`Gos` svami Damodara Sastri.\n"
            "`N.` ardesai.\n"
            "`Siv:` adatta and Kaginath Parab.\n"
            "`Siv:` adatta and Kasinath Pandurang Parab.\n"
            "`K:` aul Shastri; IFI. 1962, Kriyapada (2)\n"
            "`Ram Acharya`\n"
            "`AnyaS( Ni)` Anyapadegasataka, Nilakanthadiksita, BMS. 1929,\n"
            "`AtmaU.1` Atmopanisad, NSP. 1948,\n"
            "`Kad. Kadam` bari, Bana and his son, BS(P)S. 24, 1885,\n"
            "`P. Astadhy` ayi, Panini, Leipzig, 1887,\n"
            "`01101)` Nityotsavanibandha, Umanandanatha, GOS. 23, 1948,\n")
    ents = parse_aob(text)
    got = [e["siglum_raw"] for e in ents]
    expected = ["PadmP.", "AllaU.", "AnyaS( Ni)", "AtmaU.1",
                "Kad. Kadam", "P. Astadhy", "01101)"]
    if got != expected:
        print("FAIL H6960 parser: got %r, expected %r" % (got, expected))
        ok = False
    else:
        print("ok  H6960 parser: 29-entry class promoted, short wrap tokens folded")
    if not ok:
        return 1
    # 1c. H7096: the scan's invisible artifacts never reach an emitted title
    dirty = ("Gopalakelicandrika, Ramakrsna, Amsterdam 1917, "
              "W. Calan — त्\u200c.")
    clean = strip_ocr_invisibles(dirty)
    if clean != "Gopalakelicandrika, Ramakrsna, Amsterdam 1917, W. Calan — त्.":
        print("FAIL H7096 invisibles: ZWNJ survived the strip: %r" % clean)
        ok = False
    elif any(ch in clean for ch in OCR_INVISIBLES):
        print("FAIL H7096 invisibles: an invisible survived the strip")
        ok = False
    elif "\u200d" not in strip_ocr_invisibles("a\u200db"):
        print("FAIL H7096 invisibles: ZWJ must survive (it can be meaningful)")
        ok = False
    else:
        ents = parse_aob("## Page 1\n`GopaKeCan,` " + dirty + "\n")
        if not ents or any(ch in ents[0]["tail"] for ch in OCR_INVISIBLES):
            print("FAIL H7096 invisibles: an invisible reached a parsed tail")
            ok = False
        else:
            print("ok  H7096 invisibles: U+200C/U+200B/U+FEFF stripped at the "
                  "source, U+200D kept")
    if not ok:
        return 1
    # 2. trap: Mahabharata vs Mahabhasya never share a skeleton
    if skeleton("MahāBhā.") == skeleton("MahāBh."):
        print("FAIL trap: MahāBhā. and MahāBh. share a skeleton")
        ok = False
    else:
        print("ok  trap: %s != %s" % (skeleton("MahāBhā."), skeleton("MahāBh.")))
    # 3. one-letter sigla: punctuation is not meaning, a diacritic is
    by_strict = {"a": [{"siglum_raw": "A.", "tail": "Amarakosa, NSP. 1950."}]}
    by_skel = by_strict
    by_base = by_strict
    if not match_a("A.", by_strict, by_skel, by_base)[0]:
        print("FAIL short key: 'A.' did not match its own printed entry 'A.'")
        ok = False
    elif match_a("Ā", by_strict, by_skel, by_base)[0]:
        print("FAIL short key: 'Ā' matched 'A.' on a one-letter skeleton")
        ok = False
    else:
        print("ok  short keys: 'A.' matches, 'Ā' refused")
    # 4. H6960 on the real AOB when it is on disk (the --check input)
    real = Path(aob_path) if aob_path else (ROOT.parent / "PD/AOB.md")
    if real.exists():
        entries = parse_aob(real.read_text(encoding="utf-8"))
        tokens = {e["token_raw"] for e in entries}
        missing = [t for t in H6960_PROMOTED if t not in tokens]
        still = sorted({t for t, _ in H6960_FALSE_RECOVERIES if t in tokens})
        ling = [e for e in entries if e["siglum_raw"].startswith("Linganu")]
        kad = next((e for e in entries if e["siglum_raw"] == "Kad. Kadam"), None)
        ast = next((e for e in entries if e["siglum_raw"] == "P. Astadhy"), None)
        # the 136+ genuine fragments must STAY folded: count R1 entry-like lines
        # (audit rule) whose token the repaired parser did not turn into an entry
        text = real.read_text(encoding="utf-8")
        folded_fragments = 0
        for line in text.splitlines():
            m = TOKEN_RE.match(line)
            if not m:
                continue
            tok = m.group(1).strip()
            tail = m.group(2).strip()
            words = tok.lstrip("\u2018\u2019\u201c\u201d\"'`([{*").split()
            merged_r1 = (len(words) > 1 and bool(SIGLUM_WORD_RE.match(words[0]))
                         and letters(tok) >= 10)
            r1 = bool(UPPER_START_RE.match(tok)) and (
                letters(tail) >= 6 or bool(YEAR_RE.search(tail)) or merged_r1)
            if r1 and tok not in tokens:
                folded_fragments += 1
        sample_still = [tok for tok, _ in H6960_FRAGMENT_SAMPLE
                        if tok in tokens]
        problems = []
        if missing:
            problems.append("not promoted: %r" % missing)
        if sample_still:
            problems.append("fragment sample became entries: %r" % sample_still)
        if still:
            problems.append("still entries: %r" % still)
        if len(ling) != 7:
            problems.append("Linganu rows %d != 7 (witness)" % len(ling))
        if kad is None or "1885" not in kad["tail"]:
            problems.append("Kadambari row missing its year")
        if ast is None or "1887" not in ast["tail"]:
            problems.append("Astadhyayi row missing its year")
        if folded_fragments < 136:
            problems.append("only %d genuine fragments still folded (<136)"
                            % folded_fragments)
        dirty_tails = [e["entry_id"] for e in entries
                       if any(ch in e["tail"] for ch in OCR_INVISIBLES)]
        if dirty_tails:
            problems.append("invisible artifact in %d tails: %r"
                            % (len(dirty_tails), dirty_tails[:5]))
        if problems:
            print("FAIL H6960 real data: %s" % "; ".join(problems))
            ok = False
        else:
            print("ok  H6960 real data: %d promoted, %d folded, %d genuine "
                  "fragments stayed folded, Linganu=7, Kadambari/Astadhyayi own "
                  "dated rows"
                  % (len(H6960_PROMOTED), len(H6960_FALSE_RECOVERIES),
                     folded_fragments))
    else:
        print("skip H6960 real-data assertions (no AOB.md at %s)" % real)
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aob", default=None, help="path to PD/AOB.md")
    ap.add_argument("--witness", action="append", default=None,
                    help="printed-book text witness (.pdf or .txt), repeatable; "
                         "default: ../PD/AOB.pdf + ../PD/AOB_ocr.md when present")
    ap.add_argument("--no-witness", action="store_true",
                    help="skip the printed-text confirmation (H6941 classes)")
    ap.add_argument("--check", action="store_true",
                    help="recompute and compare with the committed artifacts")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(Path(args.aob) if args.aob else None)

    aob = Path(args.aob) if args.aob else (ROOT.parent / "PD/AOB.md")
    families = ROOT / "data/pd/pd_siglum_families.tsv"
    join = ROOT / "data/pd/pd_aob_siglum_title.tsv"
    for p in (aob, families, join):
        if not p.exists():
            print("[FAIL] missing input: %s" % p, file=sys.stderr)
            return 2

    if args.no_witness:
        witness_paths = []
    elif args.witness:
        witness_paths = args.witness
    else:
        witness_paths = [str(p) for p in (ROOT.parent / "PD/AOB.pdf",
                                          ROOT.parent / "PD/AOB_ocr.md")
                         if p.exists()]
    witnesses = load_witnesses(witness_paths) if witness_paths else []

    entries, disc, summary = measure(aob, families, join, witnesses)
    summary = {**license_fields(), **summary}

    if args.check:
        out_dir = ROOT / "data/pd"
        committed_text = (
            out_dir / "pd_aob_sigla_reconciliation.json").read_text(encoding="utf-8")
        committed = json.loads(committed_text)
        # The WHOLE artifact is compared, byte for byte, not a hand-picked
        # list of blocks.  A partial comparison is exactly what let H7107's
        # own `method` edit drift away from the committed JSON unnoticed:
        # the six blocks this loop used to name all matched, and the seventh
        # key (the one H7107 added) did not.  Derive-don't-store means the
        # committed file is the generator's output, in full.
        diffs = []
        fresh_text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
        if committed_text != fresh_text:
            for key in sorted(set(committed) | set(summary)):
                if committed.get(key) != summary.get(key):
                    diffs.append(key)
            if not diffs:
                diffs.append("json formatting/ordering")
        # row-level artifacts are gated too: aggregates can be right while a
        # TSV row is hand-edited or truncated
        for name, cols, rows in (
                ("pd_aob_entries.tsv", ENTRY_COLS, entries),
                ("pd_aob_sigla_reconciliation.tsv", DISC_COLS, disc)):
            path = out_dir / name
            if (path.read_text(encoding="utf-8") if path.exists() else "") != \
                    render_tsv(cols, rows):
                diffs.append(name)
        if diffs:
            print("[FAIL] committed artifacts drifted in: %s" % ", ".join(diffs),
                  file=sys.stderr)
            return 1
        print("ok  committed reconciliation reproduces "
              "(json aggregates + both row-level TSVs)")
        return 0

    out_dir = ROOT / "data/pd"
    write_tsv(out_dir / "pd_aob_entries.tsv", ENTRY_COLS, entries)
    write_tsv(out_dir / "pd_aob_sigla_reconciliation.tsv", DISC_COLS, disc)
    target = Path(args.json_out) if args.json_out else (
        out_dir / "pd_aob_sigla_reconciliation.json")
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")

    print("AOB entries          : %d usable / %d parsed"
          % (summary["aob"]["entries_usable"], summary["source_aob"]["entries"]))
    print("AOB never cited in a-: %d (%.2f %% of well-formed entries)"
          % (summary["aob"]["never_cited"], summary["aob"]["never_cited_pct"]))
    h = summary["harvest"]
    print("harvested families   : %d" % h["families"])
    print("  join claim         : %d (%.2f %%), mass %.2f %%"
          % (h["join_claim"]["families"], h["join_claim"]["share_pct"],
             h["join_claim"]["mass_share_pct"]))
    print("  + siglum identity  : %d (%.2f %%), mass %.2f %%"
          % (h["join_claim_plus_siglum_identity"]["families"],
             h["join_claim_plus_siglum_identity"]["share_pct"],
             h["join_claim_plus_siglum_identity"]["mass_share_pct"]))
    print("  entry-located      : %d (%.2f %%), mass %.2f %%"
          % (h["entry_located"]["families"], h["entry_located"]["share_pct"],
             h["entry_located"]["mass_share_pct"]))
    print("join misses rescued  : %d" % summary["harvest"]["join_misses_rescued"])
    w = summary.get("witness")
    if w:
        print("printed-text witnesses: %s" % ", ".join(x["path"] for x in w["sources"]))
        print("  join confirmed     : %d/%d entry-located (%.2f %%) -> %d/%d (%.2f %%)"
              % (w["join_rows_entry_located"], w["join_rows"],
                 w["coverage_before_pct"], w["join_rows_entry_located"] + w["confirmed_rows"],
                 w["join_rows"], w["coverage_after_pct"]))
        print("  rows reclassified  : %d join_unconfirmed_at_entry -> join_confirmed_printed_text"
              % w["confirmed_rows"])
    print("wrote                : data/pd/pd_aob_entries.tsv, "
          "data/pd/pd_aob_sigla_reconciliation.tsv, "
          "data/pd/pd_aob_sigla_reconciliation.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
