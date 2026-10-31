"""Build the A68 review gallery (single self-contained HTML, inline SVGs).

Usage:  python -m a68_figures.gallery <figures_dir> <out_html>

The gallery is a SESSION/REVIEW artifact, not a paper deliverable: it wraps
the deterministic SVGs written by the builder with headings and notes so a
human review pass sees everything on one page. Sections are declared below;
files not listed land in a trailing 'unchanged' section.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SECTIONS = [
    ("fig5 · cat #1 — citation-mass flow — <b>FIX: colour legend added</b>",
     ["a68_fig5_citation_flow.svg"],
     "Four swatches under the flow: primary/covered, residue, structural, "
     "secondary scholarship."),
    ("fig7 · cat #12 — denominator ladder — current style",
     ["a68_fig7_denominator_ladder.svg"], ""),
    ("fig7 — style study A · Tufte (minimal ink, no fills)",
     ["style_studies/a68_fig7_styleA_tufte.svg"],
     "Dots + dotted connectors; the axis is implied, numerals carry the "
     "message."),
    ("fig7 — style study B · Economist idiom",
     ["style_studies/a68_fig7_styleB_economist.svg"],
     "Sans-serif, red accent rule, horizontal bars, value at bar end, "
     "source line."),
    ("fig7 — style study C · FT idiom",
     ["style_studies/a68_fig7_styleC_ft.svg"],
     "Salmon field, kicker, teal/claret rounded bars, inline white "
     "numerals."),
    ("fig7 — style study D · engraved plate (monochrome)",
     ["style_studies/a68_fig7_styleD_engraving.svg"],
     "Double-rule frame, hatched bars, rung-to-rung deltas, plate caption."),
    ("fig10 · cat #24 — DCS-276 token mass by Renou layer — current style",
     ["a68_fig10_dcs276_layers.svg"], ""),
    ("fig10 — style study A · Tufte (two 100 %-strips + drift connectors)",
     ["style_studies/a68_fig10_styleA_tufte.svg"],
     "Grey tones only; connector fan traces each layer's drift all → "
     "covered; key column shows all % → covered %."),
    ("fig10 — style study B · Economist idiom",
     ["style_studies/a68_fig10_styleB_economist.svg"], ""),
    ("fig10 — style study C · FT idiom",
     ["style_studies/a68_fig10_styleC_ft.svg"], ""),
    ("fig10 — style study D · engraved stratigraphic columns",
     ["style_studies/a68_fig10_styleD_engraving.svg"],
     "Two columns to one absolute scale; six hatch textures instead of "
     "hues."),
    ("fig14 · cat #9 — corpus size vs attention — original (for reference)",
     ["a68_fig14_corpus_attention.svg"], ""),
    ("fig14b · cat #9 — <b>ZOOM: 4 median quadrants at ~2× axis scale</b>",
     ["a68_fig14b_corpus_attention_zoom.svg"],
     "Overview top-left; panels A–D each carry every title labelled "
     "(20/39/39/20). Panel edges ARE the median crosshair."),
    ("fig15 · cat #19 — class-coverage forest (PD side, for reference)",
     ["a68_fig15_class_forest.svg"], ""),
    ("fig16 · <b>NEW: PWG vs PD per stratum — the companion forest</b>",
     ["a68_fig16_pwg_vs_pd_forest.svg"],
     "What fig15 shows for PD coverage, fig16 shows for the PWG-vs-PD "
     "inheritance: paired attestation dots per stratum + committed "
     "ratio CIs."),
]


def build(figures_dir: Path, out_path: Path, title: str) -> None:
    parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title></head><body "
        "style='font-family:Georgia,serif;max-width:1720px;margin:24px auto;"
        "padding:0 16px'>",
        f"<h1 style='font:700 22px/1.3 Georgia,serif'>{title}</h1>",
        "<p style='color:#555;font-size:13px'>Deterministic SVGs from the "
        "csl-atlas builder, cross-check gate green. Fixed/new material is "
        "marked in bold; the rest repeat for side-by-side comparison.</p>",
    ]
    seen = set()
    for heading, files, note in SECTIONS:
        body = []
        for rel in files:
            p = figures_dir / rel
            if not p.exists():
                body.append(f"<p style='color:#b2182b'>MISSING: {rel}</p>")
                continue
            seen.add(rel)
            body.append(p.read_text(encoding="utf-8"))
        parts.append(
            f"<section style='margin:0 0 36px 0'>"
            f"<h2 style='font:600 16px/1.4 Georgia,serif;margin:0 0 8px 0'>"
            f"{heading}</h2>"
            + (f"<p style='color:#555;font-size:12.5px;margin:0 0 8px 0'>"
               f"{note}</p>" if note else "")
            + "<div style='border:1px solid #e4e4e4;border-radius:6px;"
              "padding:8px;background:#fff;overflow-x:auto'>"
            + "".join(body) + "</div></section>")
    others = sorted(
        str(p.relative_to(figures_dir))
        for p in figures_dir.rglob("*.svg")
        if str(p.relative_to(figures_dir)) not in seen)
    if others:
        body = "".join((figures_dir / o).read_text(encoding="utf-8")
                       for o in others)
        parts.append(
            "<section style='margin:0 0 36px 0'>"
            "<h2 style='font:600 16px/1.4 Georgia,serif;margin:0 0 8px 0'>"
            "Unchanged in this pass (for completeness)</h2>"
            "<div style='border:1px solid #e4e4e4;border-radius:6px;"
            "padding:8px;background:#fff;overflow-x:auto'>" + body
            + "</div></section>")
    parts.append("</body></html>\n")
    out_path.write_text("".join(parts), encoding="utf-8", newline="\n")
    print(f"gallery: {out_path} ({len(seen) + len(others)} SVGs inlined)")


def main():
    if len(sys.argv) != 3:
        print("usage: python -m a68_figures.gallery <figures_dir> <out_html>")
        return 2
    build(Path(sys.argv[1]), Path(sys.argv[2]),
          "A68 figures — MG review pass 2 (31-10-2026)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
