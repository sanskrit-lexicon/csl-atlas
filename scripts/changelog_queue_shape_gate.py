#!/usr/bin/env python3
"""changelog_queue/ fragment shape gate (H7467) — refuse a malformed queue
fragment at the commit/push chokepoint, while its author is still present.

CONSUMER, NOT A COPY. This script deliberately contains no fragment grammar of
its own: the validator is ``validate_entry(strict=True)`` imported from the
canonical Uprava parser ``tools/changelog_queue_consume.py`` (H3355/H4466) —
the same validator the sanctioned writer (``--append``) and the release
consumer ``tools/cut_release.py`` call at release-cut. The staging/ref/paths
plumbing and every-offender reporting mirror Uprava's
``scripts/changelog_queue_shape_gate.py``; if the two drift apart, fix both.

Why this repo needs its own chokepoint: PRs #670 and #674 repaired eight
hand-written malformed fragments days AFTER they landed — the authors were
gone and the shape error surfaced in somebody else's repair PR. The consumer
only WARNs and skips malformed fragments at cut time (H4466 / FINDINGS §744),
so without a commit-time gate nothing rejects a bad fragment while the fix is
still one keystroke.

Cross-repo gap (recorded in the H7467 receipt): csl-atlas is public, Uprava is
org-private, so the canonical parser cannot ship inside this repo and CI
cannot run this gate. Resolution order: ``$UPRAVA_TOOLS``, then the sibling
checkout ``<repo>/../Uprava/tools``, then the MAIN worktree's sibling (estate
edits land in linked worktrees under ``GitHub-worktrees/`` whose own parent
has no Uprava — same sibling convention as ``../csl-orig`` and
``../SanskritLexicography``, resolved through ``git worktree list``). When
none is present the gate degrades to a loud WARNING + exit 0 — the same
fail-open contract the other missing-checker hook gates in this repo use.

    python scripts/changelog_queue_shape_gate.py --staged
    python scripts/changelog_queue_shape_gate.py --ref <sha> [--base <sha>]
    python scripts/changelog_queue_shape_gate.py --paths a.md [b.md ...]
    python scripts/changelog_queue_shape_gate.py --selftest

Exit 0 clean (or degraded skip), 1 on a refusal, 2 on a usage error.
Escape hatch (deliberate, named loudly — never silent):
    ALLOW_CHANGELOG_QUEUE_SHAPE=1
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

QUEUE_PREFIX = "changelog_queue/"
ESCAPE = "ALLOW_CHANGELOG_QUEUE_SHAPE"


def resolve_uprava_tools(repo: Path) -> Path | None:
    """Locate the canonical parser's home. Resolution order:

    1. ``$UPRAVA_TOOLS`` (explicit override),
    2. the sibling checkout ``<repo>/../Uprava/tools`` (the estate convention
       for main checkouts laid out as ``GitHub/<repo>`` beside ``GitHub/Uprava``),
    3. the MAIN worktree's sibling — estate edits happen in linked worktrees
       (``GitHub-worktrees/<repo>/<name>-*``) whose own parent has no Uprava;
       ``git worktree list`` names the main checkout that does.

    Returns None when none of these carries the parser.
    """
    candidates: list[Path] = []
    env = os.environ.get("UPRAVA_TOOLS")
    if env:
        candidates.append(Path(env))
    candidates.append(repo.parent / "Uprava" / "tools")
    main_tree = _main_worktree(repo)
    if main_tree is not None:
        candidates.append(main_tree.parent / "Uprava" / "tools")
    for cand in candidates:
        if (cand / "changelog_queue_consume.py").is_file():
            return cand
    return None


def _main_worktree(repo: Path) -> Path | None:
    """Path of the main working tree this repo/worktree belongs to."""
    r = _run(["git", "worktree", "list", "--porcelain"], repo)
    if r.returncode != 0:
        return None
    for ln in r.stdout.splitlines():
        if ln.startswith("worktree "):
            return Path(ln[len("worktree "):].strip())
    return None


def load_strict_validator(repo: Path):
    """Return validate_entry bound to strict=True from the canonical parser,
    or None when the parser cannot be located (degraded mode)."""
    tools = resolve_uprava_tools(repo)
    if tools is None:
        return None
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    from changelog_queue_consume import validate_entry  # noqa: PLC0415

    def strict(text: str) -> None:
        validate_entry(text, strict=True)

    return strict


def _run(cmd: list[str], repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def staged_queue_files(repo: Path) -> list[str]:
    """Queue fragments Added/Copied/Modified/Renamed in the INDEX."""
    r = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR",
              "-z", "--", QUEUE_PREFIX], repo)
    if r.returncode != 0:
        return []
    return [p for p in r.stdout.split("\0") if p.endswith(".md")]


def ref_queue_files(repo: Path, ref: str, base: str | None) -> list[str]:
    """Queue fragments touched between base and ref (whole ref when base is
    unresolvable — a first push has no merge-base to compare against)."""
    if base:
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR", "-z",
               base, ref, "--", QUEUE_PREFIX]
    else:
        cmd = ["git", "show", "--pretty=format:", "--name-only",
               "--diff-filter=ACMR", "-z", ref, "--", QUEUE_PREFIX]
    r = _run(cmd, repo)
    if r.returncode != 0:
        return []
    return sorted({p for p in r.stdout.split("\0") if p.endswith(".md")})


def blob_at(repo: Path, ref: str, path: str) -> str | None:
    r = _run(["git", "show", f"{ref}:{path}"], repo)
    return None if r.returncode != 0 else r.stdout


def check(pairs: list[tuple[str, str]], validate) -> list[tuple[str, str]]:
    """[(path, text)] -> [(path, error)] for EVERY offender, never just the
    first (FINDINGS §744: one-offender-at-a-time hid four of five)."""
    bad: list[tuple[str, str]] = []
    for path, text in pairs:
        try:
            validate(text)
        except ValueError as e:
            bad.append((path, str(e)))
    return bad


def report(bad: list[tuple[str, str]], tools_hint: Path | None) -> int:
    if not bad:
        return 0
    print("", file=sys.stderr)
    print(f"changelog_queue shape gate: {len(bad)} malformed fragment(s).",
          file=sys.stderr)
    print("", file=sys.stderr)
    for path, err in bad:
        print(f"  {path}", file=sys.stderr)
        print(f"      {err}", file=sys.stderr)
    print("", file=sys.stderr)
    print("A queue fragment is a list of CHANGELOG bullets, not a document: every",
          file=sys.stderr)
    print("line is copied verbatim under ## [Unreleased] at the next release cut",
          file=sys.stderr)
    print("(tools/cut_release.py), so a heading, YAML front-matter or a byline",
          file=sys.stderr)
    print("ends up INSIDE a released section. Fold the title into the bullet:",
          file=sys.stderr)
    print("", file=sys.stderr)
    print("  - **H1234: what shipped, one sentence.** The prose, links and the",
          file=sys.stderr)
    print("    trailing attribution all live inside this one bullet.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Convention: Uprava docs/CONVENTION_CHANGELOG_QUEUE_2026-08.md",
          file=sys.stderr)
    print(f"Override (say so out loud when you use it): {ESCAPE}=1", file=sys.stderr)
    if tools_hint is not None:
        print(f"(validator: canonical parser at {tools_hint})", file=sys.stderr)
    return 1


def degraded_skip(repo: Path) -> int:
    looked = [repo.parent / "Uprava" / "tools"]
    main_tree = _main_worktree(repo)
    if main_tree is not None:
        looked.append(main_tree.parent / "Uprava" / "tools")
    print("changelog_queue shape gate: SKIPPED — canonical parser not found.",
          file=sys.stderr)
    print("  looked for $UPRAVA_TOOLS and the sibling checkout(s): "
          + ", ".join(str(p) for p in looked), file=sys.stderr)
    print("  csl-atlas is public and Uprava is org-private, so the parser is",
          file=sys.stderr)
    print("  consumed from a sibling checkout, never copied (H7467).", file=sys.stderr)
    return 0


def selftest() -> int:
    repo = Path(__file__).resolve().parent.parent
    validate = load_strict_validator(repo)
    if validate is None:
        print("selftest: [FATAL] canonical parser not found "
              "(see resolution order in the module docstring)", file=sys.stderr)
        return 2
    good = "- **H1: shipped.** Prose.\n  continuation line\n"
    assert not check([("x.md", good)], validate), good
    bads = {
        "heading": "# H1: shipped\n\nProse with no bullet.\n",
        "byline": "- **H1: shipped.** Prose.\n_Dr. Mārcis Gasūns_\n",
        "frontmatter": "---\ntitle: \"x\"\ndate: 2026-10-30\n---\n- shipped\n",
        "empty": "\n\n",
    }
    for label, text in bads.items():
        assert check([(f"{label}.md", text)], validate), label
    # every offender is named, not just the first
    assert len(check([("a.md", bads["heading"]), ("b.md", bads["byline"])],
                     validate)) == 2
    print("selftest: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staged", action="store_true")
    g.add_argument("--ref")
    g.add_argument("--paths", nargs="+")
    g.add_argument("--selftest", action="store_true")
    ap.add_argument("--base", default=None, help="merge-base for --ref")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if os.environ.get(ESCAPE) == "1":
        print(f"changelog_queue shape gate: SKIPPED via {ESCAPE}=1", file=sys.stderr)
        return 0

    repo = Path(args.repo).resolve()
    # Parser resolution anchors on the gate script's OWN repo (its sibling /
    # main-worktree chain is where the estate keeps Uprava), never on --repo:
    # --repo may be a throwaway fixture whose parent has no Uprava checkout.
    anchor = Path(__file__).resolve().parent.parent
    validate = load_strict_validator(anchor)
    if validate is None:
        return degraded_skip(anchor)

    pairs: list[tuple[str, str]] = []

    if args.paths:
        for p in args.paths:
            fp = Path(p)
            if not fp.is_file():
                print(f"[FATAL] no such file: {p}", file=sys.stderr)
                return 2
            pairs.append((p, fp.read_text(encoding="utf-8")))
    elif args.staged:
        for path in staged_queue_files(repo):
            # read the STAGED blob, not the worktree — they can differ
            r = _run(["git", "show", f":{path}"], repo)
            text = r.stdout if r.returncode == 0 else None
            if text is None:
                fp = repo / path
                if not fp.is_file():
                    continue
                text = fp.read_text(encoding="utf-8")
            pairs.append((path, text))
    else:
        for path in ref_queue_files(repo, args.ref, args.base):
            text = blob_at(repo, args.ref, path)
            if text is not None:
                pairs.append((path, text))

    return report(check(pairs, validate), resolve_uprava_tools(repo))


if __name__ == "__main__":
    raise SystemExit(main())
