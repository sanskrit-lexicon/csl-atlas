#!/usr/bin/env python3
"""METALEX L8 census — entry-level scan-page link coverage (H2368).

Measures how many csl-orig entries carry a print-page coordinate and how many
of those currently resolve to a Cologne scan URL under the atlas's own
``scripts/lib/cologne-links.mjs`` rules (mw / pwg / ap90 only).

Does **not** invent link targets or fill missing links. Stdlib only.

Writes:
  data/metalex/L8_SCAN_LINK_CENSUS.json
  data/metalex/L8_SCAN_LINK_CENSUS.md

Re-run:
  python scripts/metalex/l8_scan_link_census.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
CSL_ORIG = (REPO.parent / "csl-orig" / "v02").resolve()
OUT_DIR = REPO / "data" / "metalex"
OUT_JSON = OUT_DIR / "L8_SCAN_LINK_CENSUS.json"
OUT_MD = OUT_DIR / "L8_SCAN_LINK_CENSUS.md"

# Mirror of scripts/lib/cologne-links.mjs COLOGNE_SCAN_DIR + MULTI_VOLUME_DICTS.
# Keep in sync; this census deliberately does not invent new dict→scan-dir maps.
COLOGNE_SCAN_DIR = {
    "mw": "MW",
    "pwg": "PWG",
    "ap90": "AP90",
    "wil": "WIL",
    "cae": "CAE",
    "bor": "BOR",
    "fri": "FRI",
    "ieg": "IEG",
    "armh": "ARMH",
    "krm": "KRM",
    "abch": "ABCH",
    "pgn": "PGN",
    "snp": "SNP",
    "acsj": "ACSJ",
    "acph": "ACPH",
}
MULTI_VOLUME_DICTS = {"pwg"}

_ATTR_PC = re.compile(r"<pc>([^<]*)")
_ATTR_K1 = re.compile(r"<k1>([^<]*)")
_ATTR_L = re.compile(r"<L>([0-9.]+)")
_GAP_SAMPLE_PER_BUCKET = 8
_GAP_SAMPLE_PER_DICT = 3


_PC_COLUMN_MARKER = re.compile(r"^(\d+)-([a-zA-Z]+|\d+)$")


def scan_page_from_pc(dict_code: str, pc: str | None) -> str | None:
    """Port of cologne-links.mjs scanPageFromPc — exact contract."""
    raw = (pc or "").strip()
    if not raw:
        return None
    code = (dict_code or "").lower()
    if code in MULTI_VOLUME_DICTS:
        return raw if re.fullmatch(r"\d+-\d+", raw) else None
    page = raw.split(",")[0].strip()
    if re.fullmatch(r"\d+", page):
        return page
    # Single-volume "page-<column marker>" shape (ap90: "0001-a", or at a
    # new-letter section break "0351-1" — H2368-A11 follow-up). Marker is
    # all-letters or all-digits, never mixed.
    m = _PC_COLUMN_MARKER.match(page)
    return m.group(1) if m else None


def atlas_resolvable(dict_code: str, pc: str | None) -> bool:
    """True iff cologne-links.mjs scanUrl() would emit a non-null URL."""
    if (dict_code or "").lower() not in COLOGNE_SCAN_DIR:
        return False
    return scan_page_from_pc(dict_code, pc) is not None


def discover_dicts() -> list[tuple[str, Path]]:
    if not CSL_ORIG.is_dir():
        raise SystemExit(f"csl-orig not found at {CSL_ORIG}")
    found: list[tuple[str, Path]] = []
    for d in sorted(CSL_ORIG.iterdir()):
        if not d.is_dir():
            continue
        src = d / f"{d.name}.txt"
        if src.is_file():
            found.append((d.name.lower(), src))
    return found


def census_dict(code: str, path: Path) -> dict:
    n = 0
    with_pc = 0
    resolvable = 0
    missing_pc: list[dict] = []
    unparseable: list[dict] = []
    pc_shapes: Counter[str] = Counter()
    gap_reason: Counter[str] = Counter()

    has_scan_dir = code in COLOGNE_SCAN_DIR

    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.startswith("<L>"):
                continue
            n += 1
            pc_m = _ATTR_PC.search(line)
            pc = pc_m.group(1).strip() if pc_m else ""
            k1_m = _ATTR_K1.search(line)
            k1 = k1_m.group(1).strip() if k1_m else ""
            L_m = _ATTR_L.search(line)
            L = L_m.group(1) if L_m else ""

            if not pc:
                gap_reason["missing_pc"] += 1
                if len(missing_pc) < _GAP_SAMPLE_PER_DICT:
                    missing_pc.append({"L": L, "k1": k1, "pc": pc})
                continue

            with_pc += 1
            shape = re.sub(r"\d+", "N", pc)
            pc_shapes[shape] += 1

            if atlas_resolvable(code, pc):
                resolvable += 1
            else:
                if not has_scan_dir:
                    gap_reason["pc_present_no_cologne_scan_dir"] += 1
                else:
                    gap_reason["pc_unparseable_for_atlas_scan_url"] += 1
                    if len(unparseable) < _GAP_SAMPLE_PER_DICT:
                        unparseable.append({"L": L, "k1": k1, "pc": pc})

    return {
        "code": code,
        "sourcePath": str(path.relative_to(CSL_ORIG.parent.parent) if path.is_relative_to(CSL_ORIG.parent.parent) else path),
        "entries": n,
        "with_pc": with_pc,
        "missing_pc": n - with_pc,
        "pc_pct": round(100.0 * with_pc / n, 4) if n else 0.0,
        "atlas_resolvable_scan": resolvable,
        "atlas_resolvable_pct": round(100.0 * resolvable / n, 4) if n else 0.0,
        "in_cologne_scan_dir": has_scan_dir,
        "cologne_scan_dir": COLOGNE_SCAN_DIR.get(code),
        "gap_reason_counts": dict(gap_reason),
        "pc_shape_top": pc_shapes.most_common(6),
        "sample_missing_pc": missing_pc,
        "sample_unparseable_pc": unparseable,
    }


def build_report(rows: list[dict]) -> dict:
    total = sum(r["entries"] for r in rows)
    with_pc = sum(r["with_pc"] for r in rows)
    resolvable = sum(r["atlas_resolvable_scan"] for r in rows)
    missing_pc = total - with_pc

    gap_buckets = Counter()
    for r in rows:
        for k, v in r["gap_reason_counts"].items():
            gap_buckets[k] += v

    # Dict-level gap buckets for the roadmap table
    dicts_100_pc = [r["code"] for r in rows if r["entries"] and r["pc_pct"] >= 100.0]
    dicts_lt_100_pc = [r["code"] for r in rows if r["entries"] and r["pc_pct"] < 100.0]
    dicts_atlas_100 = [
        r["code"] for r in rows if r["entries"] and r["atlas_resolvable_pct"] >= 100.0
    ]
    dicts_in_scan_dir = [r["code"] for r in rows if r["in_cologne_scan_dir"]]
    dicts_scan_dir_not_100 = [
        r["code"]
        for r in rows
        if r["in_cologne_scan_dir"] and r["atlas_resolvable_pct"] < 100.0
    ]

    gap_samples: list[dict] = []
    for r in rows:
        for s in r["sample_missing_pc"]:
            gap_samples.append(
                {
                    "bucket": "missing_pc",
                    "code": r["code"],
                    **s,
                }
            )
        for s in r["sample_unparseable_pc"]:
            gap_samples.append(
                {
                    "bucket": "pc_unparseable_for_atlas_scan_url",
                    "code": r["code"],
                    **s,
                }
            )
    # Cap sample size for the report
    gap_samples = gap_samples[:40]

    # Representative "no scan dir" dict samples (codes only — mass list not invent)
    no_scan_dir_codes = [r["code"] for r in rows if not r["in_cologne_scan_dir"] and r["entries"]]

    return {
        "schemaVersion": "1.0.0",
        "handoff": "H2368",
        "title": "METALEX L8 — entry-level scan-page link census",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generatedDate": date.today().isoformat(),
        "model": "Grok 4.5 (grok-4.5)",
        "rerunBy": "Sonnet 5 (claude-sonnet-5), A10 (H2368 ap90 pc-shape fix), A11 (12-dict COLOGNE_SCAN_DIR extension), A11-followup (ap90 digit-marker fix)",
        "cslOrigRoot": str(CSL_ORIG),
        "method": {
            "denominator": "Every <L>… header line in each local csl-orig/v02/<code>/<code>.txt",
            "numerator_pc": "Entry header contains non-empty <pc>… (print page/column coordinate)",
            "numerator_atlas_scan": (
                "Entry would get a non-null cologne-links.mjs scanUrl(dict, pc) — "
                "dict ∈ COLOGNE_SCAN_DIR (15 dicts as of A11) AND pc passes scanPageFromPc "
                r"(PWG: /^\d+-\d+$/; others: first comma-field is digits-only)"
            ),
            "scan_link_field": "<pc> in csl-orig entry header (not <bookref>; roadmap alias)",
            "non_goals": [
                "No mass link invention",
                "No extension of COLOGNE_SCAN_DIR without live spot-check confirmation (A11: single sequential WebFetch probes per candidate dict, not a bulk crawl)",
                "L9/L10 out of scope",
            ],
            "relation_to_richness_typology": (
                "scripts/build-richness-typology.mjs L8 is DICT-level "
                "(sourceCode ∈ COLOGNE_SCAN_DIR). This census is ENTRY-level "
                "coverage. A dict can be typology L8=true while atlas_resolvable_pct < 100% "
                "if pc shapes fail scanPageFromPc (observed for ap90)."
            ),
            "cologne_scan_dir_map": dict(COLOGNE_SCAN_DIR),
        },
        "totals": {
            "dicts": len(rows),
            "entries": total,
            "with_pc": with_pc,
            "missing_pc": missing_pc,
            "pc_pct": round(100.0 * with_pc / total, 4) if total else 0.0,
            "atlas_resolvable_scan": resolvable,
            "atlas_resolvable_pct": round(100.0 * resolvable / total, 4) if total else 0.0,
        },
        "gap_buckets": dict(gap_buckets),
        "dict_buckets": {
            "pc_coverage_100": dicts_100_pc,
            "pc_coverage_lt_100": dicts_lt_100_pc,
            "in_cologne_scan_dir": dicts_in_scan_dir,
            "atlas_resolvable_100": dicts_atlas_100,
            "in_scan_dir_but_not_100_resolvable": dicts_scan_dir_not_100,
            "not_in_cologne_scan_dir": no_scan_dir_codes,
        },
        "l8_verdict": {
            "roadmap_target": "L8 minimum: every entry linked to scan page",
            "pc_substrate_complete": missing_pc == 0,
            "atlas_scan_url_complete": resolvable == total and total > 0,
            "claim_l8_done": False,
            "note": (
                "Do not claim L8 complete: print coordinates are nearly universal, "
                "but a working Cologne scan URL is only resolvable for a minority of "
                "entries under the atlas's verified dict→scan-dir map."
            ),
        },
        "gap_samples": gap_samples,
        "rows": rows,
    }


def render_md(report: dict) -> str:
    t = report["totals"]
    m = report["method"]
    v = report["l8_verdict"]
    gb = report["gap_buckets"]
    db = report["dict_buckets"]

    lines: list[str] = []
    lines.append("# METALEX L8 — entry-level scan-page link census")
    lines.append("")
    lines.append(f"_Created: 07-08-2026 · Last updated: 24-08-2026_")
    lines.append("")
    lines.append(
        f"**Handoff:** [H2368](https://github.com/gasyoun/Uprava/blob/main/handoffs/"
        f"H2368-Grok_csl-atlas_metalex-l8-scan-link-census_07.08.26.md) · "
        f"**Model:** {report['model']} · **Generated:** {report['generatedAt']} · "
        f"**Rerun:** {report['rerunBy']}"
    )
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(
        f"| Metric | n | of total | % |"
    )
    lines.append("|---|---:|---:|---:|")
    lines.append(
        f"| Entries in scope (local csl-orig) | {t['entries']:,} | — | 100 |"
    )
    lines.append(
        f"| With non-empty `<pc>` (print coordinate) | {t['with_pc']:,} | {t['entries']:,} | **{t['pc_pct']:.2f}** |"
    )
    lines.append(
        f"| Atlas-resolvable Cologne scan URL | {t['atlas_resolvable_scan']:,} | {t['entries']:,} | **{t['atlas_resolvable_pct']:.2f}** |"
    )
    lines.append("")
    lines.append(
        f"**L8 complete?** **No.** {v['note']}"
    )
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(f"- **Denominator:** {m['denominator']}")
    lines.append(f"- **Numerator A (`with_pc`):** {m['numerator_pc']}")
    lines.append(f"- **Numerator B (`atlas_resolvable_scan`):** {m['numerator_atlas_scan']}")
    lines.append(f"- **Scan-link field:** {m['scan_link_field']}")
    lines.append(
        f"- **Verified `COLOGNE_SCAN_DIR`:** `{m['cologne_scan_dir_map']}` "
        f"(from [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs))"
    )
    lines.append(f"- **vs richness typology L8:** {m['relation_to_richness_typology']}")
    lines.append("")
    lines.append("### Non-goals")
    lines.append("")
    for ng in m["non_goals"]:
        lines.append(f"- {ng}")
    lines.append("")
    lines.append("## Gap buckets")
    lines.append("")
    lines.append("| Bucket | Entries | Meaning |")
    lines.append("|---|---:|---|")
    bucket_help = {
        "missing_pc": "Header has no non-empty `<pc>`",
        "pc_present_no_cologne_scan_dir": (
            "`<pc>` present but dict not in atlas `COLOGNE_SCAN_DIR` "
            "(no verified Cologne scan URL builder)"
        ),
        "pc_unparseable_for_atlas_scan_url": (
            "Dict is in `COLOGNE_SCAN_DIR` but `scanPageFromPc` returns null "
            "(pc shape not trusted by the atlas builder)"
        ),
    }
    for key in (
        "missing_pc",
        "pc_present_no_cologne_scan_dir",
        "pc_unparseable_for_atlas_scan_url",
    ):
        n = gb.get(key, 0)
        lines.append(f"| `{key}` | {n:,} | {bucket_help[key]} |")
    lines.append("")
    lines.append("### Dict-level sets")
    lines.append("")
    lines.append(
        f"- **`<pc>` coverage 100%:** {len(db['pc_coverage_100'])} dicts"
        + (f" (not 100%: `{', '.join(db['pc_coverage_lt_100']) or '—'}`)" )
    )
    lines.append(
        f"- **In atlas `COLOGNE_SCAN_DIR`:** `{', '.join(db['in_cologne_scan_dir']) or '—'}`"
    )
    lines.append(
        f"- **Atlas-resolvable 100%:** `{', '.join(db['atlas_resolvable_100']) or '—'}` "
        f"(ap90 reached 100% in two steps: page-column-letter shape `NNNN-a/b/c` "
        f"stripped to the page — H2368-A10 fix; then the page-column-digit shape "
        f"`NNNN-N` seen at new-letter section breaks, e.g. `0220-1`, `0351-2` — "
        f"H2368-A11 follow-up, same reasoning: the trailing chunk is a column "
        f"marker, not a volume)"
    )
    lines.append(
        f"- **In scan-dir map but not 100% resolvable:** "
        f"`{', '.join(db['in_scan_dir_but_not_100_resolvable']) or '—'}`"
    )
    lines.append(
        f"- **Not in scan-dir map:** {len(db['not_in_cologne_scan_dir'])} dicts "
        f"(dominant gap — coordinates exist; atlas has no verified servepdf map)"
    )
    lines.append("")
    lines.append("## Per-dictionary table")
    lines.append("")
    lines.append(
        "| code | entries | with_pc | pc% | atlas_scan | atlas% | in_scan_dir | top pc shapes |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|:---:|---|")
    for r in sorted(report["rows"], key=lambda x: (-x["entries"], x["code"])):
        shapes = ", ".join(f"`{s}`×{c}" for s, c in r["pc_shape_top"][:3]) or "—"
        flag = "yes" if r["in_cologne_scan_dir"] else "no"
        lines.append(
            f"| {r['code']} | {r['entries']:,} | {r['with_pc']:,} | {r['pc_pct']:.2f} | "
            f"{r['atlas_resolvable_scan']:,} | {r['atlas_resolvable_pct']:.2f} | {flag} | {shapes} |"
        )
    lines.append("")
    lines.append("## Gap list sample")
    lines.append("")
    if not report["gap_samples"]:
        lines.append("_No per-entry gap samples (missing_pc / unparseable only)._")
    else:
        lines.append("| bucket | code | L | k1 | pc |")
        lines.append("|---|---|---|---|---|")
        for g in report["gap_samples"]:
            lines.append(
                f"| `{g['bucket']}` | {g['code']} | {g.get('L','')} | "
                f"`{g.get('k1','')}` | `{g.get('pc','')}` |"
            )
    lines.append("")
    lines.append(
        "The mass of the gap is **dict not in `COLOGNE_SCAN_DIR`**, not missing `<pc>`. "
        "Those rows are not expanded entry-by-entry (would be ~1.2M rows and invent nothing useful)."
    )
    lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```sh")
    lines.append("# requires sibling ../csl-orig/v02")
    lines.append("python scripts/metalex/l8_scan_link_census.py")
    lines.append("```")
    lines.append("")
    lines.append(
        "Machine-readable twin: "
        "[data/metalex/L8_SCAN_LINK_CENSUS.json]"
        "(https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.json)"
    )
    lines.append("")
    lines.append("_Dr. Mārcis Gasūns_")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    dicts = discover_dicts()
    print(f"csl-orig: {CSL_ORIG}  dicts={len(dicts)}", flush=True)
    rows: list[dict] = []
    for code, path in dicts:
        row = census_dict(code, path)
        rows.append(row)
        print(
            f"  {code:8s} entries={row['entries']:>8,}  pc={row['pc_pct']:7.2f}%  "
            f"atlas_scan={row['atlas_resolvable_pct']:7.2f}%  "
            f"scan_dir={'Y' if row['in_cologne_scan_dir'] else 'n'}",
            flush=True,
        )

    report = build_report(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(render_md(report), encoding="utf-8")

    t = report["totals"]
    print(
        f"\nTOTAL entries={t['entries']:,}  with_pc={t['with_pc']:,} ({t['pc_pct']:.2f}%)  "
        f"atlas_resolvable={t['atlas_resolvable_scan']:,} ({t['atlas_resolvable_pct']:.2f}%)",
        flush=True,
    )
    print(f"Wrote {OUT_JSON.relative_to(REPO)}", flush=True)
    print(f"Wrote {OUT_MD.relative_to(REPO)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
