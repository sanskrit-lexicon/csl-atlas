"""H7467 acceptance matrix — changelog_queue producer→consumer contract.

Executes the REAL toolchain end-to-end against a throwaway fixture repo:

  * producer  — the sanctioned writer ``Uprava/tools/changelog_queue_consume.py
    --append`` (the real fragment-creation route),
  * consumer  — the actual release parser's dry run ``Uprava/tools/cut_release.py
    <repo>`` (no flags = plan only, never mutates),
  * gate      — this repo's ``scripts/changelog_queue_shape_gate.py``, which
    imports ``validate_entry(strict=True)`` from that same canonical Uprava
    parser (consume, not copy).

Every expected count below is a literal pinned by hand from one observed run
of the real tools — none is derived from the tools at assertion time.

Cross-repo gap (recorded in the H7467 receipt): csl-atlas is public, Uprava is
org-private, so CI has no sibling Uprava checkout and these contract tests
SKIP there; they run on estate machines where ``../Uprava`` (or
``$UPRAVA_TOOLS``) exists. The degraded-mode test runs everywhere — it pins
the fail-open WARNING the public clones see instead.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / "scripts" / "changelog_queue_shape_gate.py"
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import changelog_queue_shape_gate as gate  # noqa: E402

UPRAVA_TOOLS = gate.resolve_uprava_tools(REPO_ROOT)
CONSUME = UPRAVA_TOOLS / "changelog_queue_consume.py" if UPRAVA_TOOLS else None
CUT_RELEASE = UPRAVA_TOOLS / "cut_release.py" if UPRAVA_TOOLS else None

requires_uprava = pytest.mark.skipif(
    UPRAVA_TOOLS is None,
    reason="canonical Uprava parser not present (sibling ../Uprava or $UPRAVA_TOOLS) "
           "— CI skips the contract matrix; see the H7467 cross-repo gap note",
)

CHANGELOG_HEAD = (
    "# Changelog\n\n"
    "## [Unreleased]\n"
    "<!-- entries land in changelog_queue/ -- appended via\n"
    "tools/changelog_queue_consume.py, consumed by cut_release.py at\n"
    "release-cut (H3355); direct bullets here are hook-blocked -->\n"
    "- baseline unreleased bullet\n\n"
    "## [0.21.6] - 2026-10-28\n- baseline bullet\n"
)


def run(cmd: list[str], cwd: Path | None = None,
        env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env)


@pytest.fixture()
def fx(tmp_path: Path) -> Path:
    """Throwaway git repo shaped like csl-atlas's changelog head."""
    repo = tmp_path / "repo"
    repo.mkdir()
    run(["git", "init", "-q", "."], repo)
    run(["git", "config", "user.email", "fixture@example.invalid"], repo)
    run(["git", "config", "user.name", "fixture"], repo)
    (repo / "CHANGELOG.md").write_text(CHANGELOG_HEAD, encoding="utf-8")
    run(["git", "add", "CHANGELOG.md"], repo)
    run(["git", "commit", "-qm", "init"], repo)
    return repo


def append_entry(repo: Path, bullet: str, slug: str) -> Path:
    """The real fragment-creation route: the sanctioned Uprava writer."""
    r = run([sys.executable, str(CONSUME), "--repo", str(repo),
             "--append", bullet, "--slug", slug])
    assert r.returncode == 0, r.stderr
    created = sorted((repo / "changelog_queue").glob("*.md"))
    assert len(created) == 1, created
    return created[0]


@requires_uprava
def test_writer_creates_valid_fragment_via_real_route(fx: Path):
    frag = append_entry(fx, "- H7467: contract probe entry via the real writer",
                        "h7467-probe")
    assert frag.name.endswith("-h7467-probe.md")
    assert frag.read_text(encoding="utf-8").startswith("- H7467:")


@requires_uprava
def test_dry_run_consumes_generated_fragment_exactly_once(fx: Path):
    append_entry(fx, "- H7467: contract probe entry via the real writer",
                 "h7467-probe")
    r = run([sys.executable, str(CUT_RELEASE), str(fx)])
    assert r.returncode == 0, r.stderr
    # the fragment is inventoried for consumption exactly once
    assert "changelog_queue entries to consume: 1" in r.stdout
    frag_lines = [ln for ln in r.stdout.splitlines()
                  if ln.strip().startswith("changelog_queue/")]
    assert len(frag_lines) == 1, r.stdout
    # no tracked-file mutation and no apply happened (dry-run banner present)
    assert "# dry-run only" in r.stdout


@requires_uprava
def test_two_dry_runs_identical_zero_tracked_changes(fx: Path):
    append_entry(fx, "- H7467: contract probe entry via the real writer",
                 "h7467-probe")
    r1 = run([sys.executable, str(CUT_RELEASE), str(fx)])
    s1 = run(["git", "status", "--porcelain"], fx)
    r2 = run([sys.executable, str(CUT_RELEASE), str(fx)])
    s2 = run(["git", "status", "--porcelain"], fx)
    assert r1.returncode == r2.returncode == 0
    assert r1.stdout == r2.stdout and r1.stderr == r2.stderr
    assert s1.stdout == s2.stdout
    tracked = [ln for ln in s1.stdout.splitlines()
               if ln and not ln.startswith("??")]
    assert tracked == [], tracked  # only the new untracked fragment may exist


@requires_uprava
def test_empty_queue_is_valid(fx: Path):
    # no changelog_queue/ dir at all: the dry-run plans a normal release
    r = run([sys.executable, str(CUT_RELEASE), str(fx)])
    assert r.returncode == 0, r.stderr
    assert "entries to consume" not in r.stdout
    # and the gate finds nothing to refuse on an empty queue
    g = run([sys.executable, str(GATE), "--repo", str(fx), "--staged"])
    assert g.returncode == 0, g.stderr
    # an empty queue DIRECTORY (not just a missing one) is equally valid
    (fx / "changelog_queue").mkdir()
    g2 = run([sys.executable, str(GATE), "--repo", str(fx), "--staged"])
    assert g2.returncode == 0, g2.stderr


@requires_uprava
def test_gate_accepts_generated_valid_fragment(fx: Path):
    frag = append_entry(fx, "- H7467: contract probe entry via the real writer",
                        "h7467-probe")
    g = run([sys.executable, str(GATE), "--repo", str(fx),
             "--paths", str(frag)])
    assert g.returncode == 0, g.stderr


@requires_uprava
def test_mutation_removing_bullet_prefix_fails_gate(fx: Path):
    """Named negative control: strip the required '- ' prefix from the
    generated fragment; the gate must refuse with file-specific guidance."""
    frag = append_entry(fx, "- H7467: contract probe entry via the real writer",
                        "h7467-probe")
    mutated = frag.read_text(encoding="utf-8").replace(
        "- H7467: contract probe entry via the real writer",
        "H7467: contract probe entry via the real writer", 1)
    frag.write_text(mutated, encoding="utf-8")
    g = run([sys.executable, str(GATE), "--repo", str(fx),
             "--paths", str(frag)])
    assert g.returncode == 1, (g.stdout, g.stderr)
    # file-specific guidance: names THIS file, the canonical error, the fix
    assert "h7467-probe.md" in g.stderr
    assert "must contain at least one line starting with '- '" in g.stderr
    assert "Fold the title into the bullet" in g.stderr


@requires_uprava
def test_gate_flags_frontmatter_shape_and_names_every_offender(fx: Path):
    """The live defect class from the current queue (YAML front-matter passes
    the lenient consume-time check but corrupts the released section) plus the
    every-offender contract: both files are named in one refusal."""
    q = fx / "changelog_queue"
    q.mkdir()
    (q / "a-frontmatter.md").write_text(
        "---\ntitle: \"C3: links\"\ndate: 2026-10-30\n---\n- Add links.\n",
        encoding="utf-8")
    (q / "b-heading.md").write_text(
        "# H2: shipped\n\nProse with no bullet.\n", encoding="utf-8")
    g = run([sys.executable, str(GATE), "--repo", str(fx),
             "--paths", str(q / "a-frontmatter.md"), str(q / "b-heading.md")])
    assert g.returncode == 1, (g.stdout, g.stderr)
    assert "2 malformed fragment(s)" in g.stderr
    assert "a-frontmatter.md" in g.stderr and "b-heading.md" in g.stderr


@requires_uprava
def test_gate_selftest():
    g = run([sys.executable, str(GATE), "--selftest"])
    assert g.returncode == 0, g.stderr
    assert "selftest: OK" in g.stdout


def test_degraded_mode_warns_and_passes_without_uprava(tmp_path: Path):
    """Public clones (and CI) have no sibling Uprava: the gate must fail OPEN
    with a loud WARNING naming the resolution order — never crash, never
    silently copy the parser in. Simulated by running a COPY of the gate from
    a tree whose sibling/main-worktree chain has no Uprava anywhere."""
    fake = tmp_path / "fake-estate"
    (fake / "scripts").mkdir(parents=True)
    gate_copy = fake / "scripts" / "changelog_queue_shape_gate.py"
    gate_copy.write_bytes(GATE.read_bytes())
    probe = fake / "probe.md"
    probe.write_text("- fine\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "UPRAVA_TOOLS"}
    g = run([sys.executable, str(gate_copy), "--repo", str(fake),
             "--paths", str(probe)], env=env)
    assert g.returncode == 0, (g.stdout, g.stderr)
    assert "SKIPPED" in g.stderr and "canonical parser not found" in g.stderr
    assert "Uprava" in g.stderr


def test_hook_wiring_syntax():
    """The two wired hooks must stay valid bash."""
    bash = shutil.which("bash")
    if not bash:
        pytest.skip("no bash on PATH")
    for hook in (REPO_ROOT / ".githooks" / "pre-commit",
                 REPO_ROOT / ".githooks" / "pre-push"):
        r = run([bash, "-n", str(hook)])
        assert r.returncode == 0, (hook.name, r.stderr)
