#!/usr/bin/env python3
"""ORCID gap census across the four ATLAS repos (H5306).

Reads CITATION.cff and .zenodo.json (at a pinned git rev per repo) and lists
every author/contributor PERSON entry lacking an ORCID iD, with the exact
file and line to fix. Never invents or looks up iDs — it only reports gaps.

Usage:
    python3 scripts/orcid_gap_census.py            # census against pinned revs
    python3 scripts/orcid_gap_census.py --rev HEAD # census against each clone HEAD

Exit code 0 always: a gap is the finding, not an error.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

# repo -> (local clone, rev the H5306 census was taken against)
REPOS = {
    "csl-atlas": "/Users/mac/Documents/GitHub/csl-atlas-h5306-drain",
    "csl-standards": "/Users/mac/Documents/GitHub/csl-standards",
    "VisualDCS": "/Users/mac/Documents/GitHub/VisualDCS",
    "csl-observatory": "/Users/mac/Documents/GitHub/csl-observatory",
}
PINNED = {
    "csl-atlas": "bbca791",
    "csl-standards": "2a0c294",
    "VisualDCS": "6277c8b",
    "csl-observatory": "3f0d700",
}
PERSON_KEY = re.compile(r"(family-names:|given-names:|alias:|\"name\":)")


def show(repo_dir: str, rev: str, path: str) -> str | None:
    r = subprocess.run(
        ["git", "-C", repo_dir, "show", f"{rev}:{path}"],
        capture_output=True, text=True,
    )
    return r.stdout if r.returncode == 0 else None


def cff_person_blocks(text: str):
    """Yield (start_line, name, has_orcid, section) for person-ish CFF blocks.

    Sections keywords/identifiers are skipped; inside references only blocks
    carrying a person key count (skips `- type: data` container lines).
    """
    blocks = []
    section = None
    cur = None
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        m_top = re.match(r"^(\w[\w-]*):\s*$", line)
        if m_top:
            section, cur = m_top.group(1), None
            continue
        if section in ("keywords", "identifiers"):
            continue
        if re.match(r"^\s*-\s+\S", line):
            cur = {"start": i, "lines": [line],
                   "section": section or "?"}
            blocks.append(cur)
        elif cur is not None:
            d = len(line) - len(line.lstrip())
            if stripped and d == 0:
                cur, section = None, None
            elif stripped:
                cur["lines"].append(line)
    out = []
    for b in blocks:
        blk = "\n".join(b["lines"])
        if not PERSON_KEY.search(blk):
            continue
        has_orcid = bool(re.search(r"(?m)^\s*orcid:\s*\S", blk))
        fm = re.search(r"family-names:\s*\"?([^\"\n#]+)", blk)
        gm = re.search(r"given-names:\s*\"?([^\"\n#]+)", blk)
        am = re.search(r"alias:\s*\"?([^\"\n#]+)", blk)
        nm = re.search(r"name:\s*\"?([^\"\n#]+)", blk)
        if fm:
            name = f"{fm.group(1).strip()}, {gm.group(1).strip() if gm else '?'}"
        elif am:
            name = am.group(1).strip()
        elif nm:
            name = nm.group(1).strip()
        else:
            name = b["lines"][0].strip()[:60]
        out.append((b["start"], name, has_orcid, b["section"]))
    return out


def zenodo_person_entries(text: str):
    data = json.loads(text)
    lines = text.splitlines()
    entries = []
    for key in ("creators", "contributors"):
        for item in data.get(key, []):
            name = item.get("name", "?")
            ln = next((i for i, l in enumerate(lines, 1)
                       if f'"name": "{name}"' in l), None)
            entries.append((ln, name, bool(item.get("orcid")), key))
    return entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default=None,
                    help="git rev per repo (default: the H5306 pinned revs)")
    args = ap.parse_args()

    print(f"{'repo':<16} {'file':<14} {'line':>5}  status   who  [section]")
    print("-" * 80)
    missing = 0
    for repo, d in REPOS.items():
        rev = args.rev or PINNED[repo]
        for path in ("CITATION.cff", ".zenodo.json"):
            txt = show(d, rev, path)
            if txt is None:
                print(f"{repo:<16} {path:<14} {'—':>5}  ABSENT   (no file at {rev})")
                continue
            fn = cff_person_blocks if path.endswith(".cff") else zenodo_person_entries
            for start, name, has, section in fn(txt):
                status = "ok     " if has else "MISSING"
                if not has:
                    missing += 1
                    print(f"{repo:<16} {path:<14} {start:>5}  {status}  {name}  [{section}]")
    print("-" * 80)
    print(f"person entries missing an ORCID iD: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
