"""Diagnostic: dump raw extractor counters + sample entries for a few dicts,
to judge whether a convention-distance pairing is real signal or weak-extraction
collapse toward an 'everything-absent' profile."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from s2_fingerprint import extract, iter_entries, SRC_ROOT, CAP  # noqa

CODES = ["WIL", "YAT", "STC", "PW", "AP90"]
KEYS = ["n", "k2_sep_any", "k2_total", "num_arabic", "num_roman", "num_alpha",
        "sep_semicolon", "sep_comma", "ls_entries", "ls_count", "etym_entries",
        "lang_tag", "xref_explicit", "skt_tokens", "skt_accent", "panini",
        "gram_abbrev", "gram_full", "gram_skt", "ind_ind", "subsense"]


def main():
    print(f"{'metric':16s}" + "".join(f"{c:>9s}" for c in CODES))
    data = {}
    for c in CODES:
        path = os.path.join(SRC_ROOT, c.lower(), c.lower() + ".txt")
        data[c] = extract(path)
    for k in KEYS:
        row = f"{k:16s}"
        for c in CODES:
            v = data[c][k]
            n = max(data[c]["n"], 1)
            # show as rate where it's a per-entry count
            if k in ("n", "k2_total", "ls_count", "skt_tokens"):
                row += f"{v:>9d}"
            else:
                row += f"{v/n:>9.3f}"
        print(row)
    print("\netym marker types per dict:")
    for c in CODES:
        print(f"  {c:5s} {sorted(data[c]['etym_markers'])}")

    print("\n--- first 2 real entries (body) per dict ---")
    for c in CODES:
        path = os.path.join(SRC_ROOT, c.lower(), c.lower() + ".txt")
        print(f"\n===== {c} =====")
        shown = 0
        for k1, k2, body in iter_entries(path, CAP):
            b = body.strip()
            if not b:
                continue
            print(f"[k1={k1} k2={k2}] {b[:220].replace(chr(10), ' ')}")
            shown += 1
            if shown >= 2:
                break


if __name__ == "__main__":
    main()
