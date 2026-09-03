# H3725 — BLOCKED pass, banked evidence + execution plan

_Created: 03-09-2026 · Last updated: 03-09-2026_

**Status:** H3725 NOT done — this session could not execute a single command.
**Executor of this pass:** OxAlpha (`zai-coding-plan/glm-5.3-flash` via opencode), worker 1.
**Why blocked:** the opencode shell harness on this Mac spawns Homebrew `pwsh` 7.6.5
(`/opt/homebrew/Cellar/powershell/7.6.5`), whose apphost requires the .NET 10 runtime
(`osx-arm64`); **no .NET exists anywhere on this disk** (no `/usr/local/share/dotnet`, no
`~/.dotnet`, no `dotnet*` in Cellar, `DOTNET_ROOT` unset, `/etc/dotnet/install_location_arm64`
absent). Every Bash-tool call dies at pwsh startup — verified 4× in this session plus once in
a fresh subagent session. Git/python/node/gh are all unreachable; worktree/commit/PR/census
cannot run. Retry protocol exhausted (3+ retries, deterministic failure, not transient).

**Fix for the human (one line):** `brew install --cask dotnet-sdk` (or point the opencode
shell config at `/bin/zsh`), then re-run `/go H3725` from this worktree.

---

## Banked live evidence (all probes shot 03-09-2026 via WebFetch, api=1 egress-safe route)

Control first (source-health-probe discipline), then ONE sequential probe per dict:

| # | dict | probe URL | result |
|---|------|-----------|--------|
| 0 | (control pwg) | `https://sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/web/webtc/servepdf.php?api=1&page=1-0614` | GO — "PWG Cologne Scan" shell |
| 1 | pui | `…/scans/PUIScan/2020/web/webtc/servepdf.php?api=1&page=2-005` | **GO** — "PUI Cologne Scan" shell |
| 2 | vei | `…/scans/VEIScan/2020/web/webtc/servepdf.php?api=1&page=1-310` | **GO** — "VEI Cologne Scan" shell |
| 3 | acc | `…/scans/ACCScan/2020/web/webtc/servepdf.php?api=1&page=2-004` | **GO** — "ACC Cologne Scan" shell |
| 4 | skd | `…/scans/SKDScan/2020/web/webtc/servepdf.php?api=1&page=3-005` | **GO** — "SKD Cologne Scan" shell |
| 5 | nmmb | `…/scans/NMMBScan/2020/web/webtc/servepdf.php?api=1&page=0001` | **404 — EXCLUDE** (no scan deployment; confirms H3695 "broken probe, A11" residue) |

## `<pc>` shapes, read from csl-orig v02 meta2 + data this pass

| dict | shape | real example (csl-orig) | rule needed |
|------|-------|------------------------|-------------|
| pui | `V-PPP` (3 vols) | `<L>5272<pc>2-002<k1>taqAgaviDi…` | vol-page verbatim (H839 branch) |
| vei | `V-PPP` (2 vols) | `<L>1151<pc>1-310<k1>tiraScarAji…` | vol-page verbatim (H839 branch) |
| acc | `V-PPP,C` (3 vols) | `<L>31448<pc>2-004,1<k1>anumitiparAmarSakAryakAraRaBAvavicAra…` | strip `,C` (MW comma-column class; meta2: C is 'a'/'b', sometimes 'a1'/'b1' — census residual check needed for letter columns) |
| skd | `V-PPP-C` (5 vols) | `<L>19807<pc>3-005-a<k1>paNktiraTaH…` | strip `-C` (matches EXISTING H3695 three-part letter-marker regex as-is) |
| nmmb | bare `PPPP`, NO volume (single vol, kosha-family) | `<L>1<pc>0001` | EXCLUDED — no scan tree (probe 404) |

## Execution plan for the next session (with a working shell)

1. Worktree `../csl-atlas-h3725-drain` (branch `h3725-drain`) — first `git fetch origin && git rebase origin/main`
   (note: handoff's "PR #433 NOT merged" premise is STALE — [#433 merged 30-08-2026](https://github.com/sanskrit-lexicon/csl-atlas/pull/433),
   the U4 method incl. `scanPageFromPc` multi-volume branch is already on origin/main; [#434](https://github.com/sanskrit-lexicon/csl-atlas/pull/434)
   re-ran the census 01-09: 1,506,391 entries, 92.42% resolvable, this five-dict gap = 114,216 entries).
2. `scripts/lib/cologne-links.mjs`:
   - `COLOGNE_SCAN_DIR` += `pui: "PUI", vei: "VEI", acc: "ACC", skd: "SKD"` (40 → 44). No `COLOGNE_SCAN_YEAR` entries (all four serve at 2020 — probes prove it).
   - `MULTI_VOLUME_DICTS` += `pui, vei, acc, skd`.
   - `scanPageFromPc` multi-volume branch: skd's `V-PPP-C` already strips via the existing three-part regex; ADD the acc comma-column class `^(\d+-\d+),[a-zA-Z]?\d?$`-style rule (measure exact residual shapes from census output first — meta2 warns of `a1`/`b1` letter+digit columns). Bare page stays null (H839). Never resolve a bare page to volume 1.
3. Mirror both maps + provenance `rerunBy` in `scripts/metalex/l8_scan_link_census.py`; run census → before/after table (before per #434: five dicts 0% resolvable; after expected ~100% pc-shape coverage for the four).
4. `test/cologne-links.test.mjs`: marker-strip classes per dict + two-part verbatim + bare-page null + 44-dict map. `npm test` (watch the 5 pre-existing failures noted in #433).
5. Roadmap `docs/METALEXICOGRAPHY_ROADMAP.md` L8 bullet numbers.
6. PR: title `feat(metalex): L8 scan-dir map 40 -> 44 + pui/vei/acc/skd vol-page-col rules (H3725)`; body carries the probe table above verbatim + census table; **leave UNMERGED** (handoff stop condition).
7. Close via `handoff_close.py H3725 --pr <url> --tier "OxAlpha (opencode/z-ai/glm-5.3-flash)"`.
   nmmb exclusion one-liner for the census table: `nmmb — no Cologne scan deployment (NMMBScan/2020 servepdf 404 03-09-2026; H3695 A11 broken-probe residue confirmed)`.

_Dr. Mārcis Gasūns_
