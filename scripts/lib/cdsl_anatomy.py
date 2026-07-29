"""cdsl_anatomy — re-export shim over ``csl_pyutil.anatomy``.

The implementation used to live here (H1646: "add dictionary entry anatomy
markup, the bright colors for different part of entry"). It moved into the
shared emitter package under H1808, when SanskritLexicography's G5 sheet needed
the same treatment and could not reach it — MG, voting that sheet: "why entry
anatomy is missing again? It must be a hook". Two hand-synced copies of one
highlighter is exactly the fork-drift SHARED_CODE exists to prevent, so this
file keeps the import path and this repo's *semantics*, and owns no logic.

The one semantic this repo does own: ``<ab>``. In PWG it wraps EVERY
abbreviation (``caus.``, ``gerund.``, ``v. a.``), which is why the shared module
defaults it to the quieter ``abbreviation`` class. This sheet judges
cross-references, where the ``cf.``/``Vgl.`` marker IS the evidence, so it keeps
the bright ``crossref`` treatment — and its legend keeps the original ten
classes rather than gaining the new one.

Requires csl-pyutil >= 0.6.0 (see requirements-review.txt).
"""
from csl_pyutil import anatomy

#: This sheet's tag semantics — see the module docstring.
XREF_TAG_PARTS = {"ab": "crossref"}

#: The legend as it stood before the shared module gained an `abbreviation`
#: class, so the rendered legend is unchanged for this repo's sheets.
XREF_LEGEND_PARTS = [k for k in anatomy.PARTS if k != "abbreviation"]

PARTS = anatomy.PARTS
TAG_PARTS = dict(anatomy.TAG_PARTS, **XREF_TAG_PARTS)
BRACE_PARTS = anatomy.BRACE_PARTS


def highlight(raw, target=None, **kwargs):
    """Colour-code one raw CDSL record body with this repo's xref semantics."""
    kwargs.setdefault("tag_parts", XREF_TAG_PARTS)
    return anatomy.highlight(raw, target, **kwargs)


def legend_html(parts=None, **kwargs):
    """The swatch legend, defaulting to this repo's part set."""
    return anatomy.legend_html(parts if parts is not None else XREF_LEGEND_PARTS, **kwargs)
