"""cdsl_anatomy — colour-code the anatomy of a raw CDSL dictionary record.

A CDSL record body is a dense mix of SGML-ish tags (``<s>``, ``<lex>``, ``<ls>``,
``<ab>``) and brace markers (``{#…#}``, ``{%…%}``) whose classes differ per
dictionary. Dumped verbatim into a review card it is a wall of punctuation, and a
reviewer cannot see which clause the cross-reference under judgement rests on
(H1646: "add dictionary entry anatomy markup, the bright colors for different
part of entry").

This module keeps the markup fully VISIBLE — the tags are the anatomy, not noise
to be stripped — but dims the delimiters and colours the payload by part class, so
the shape of the entry reads at a glance. It also accepts the cross-reference
target, and outlines every occurrence of it in the record: that is the exact span
the edge is claimed from.

Prior art it deliberately reuses rather than re-derives:

* Part taxonomy and colour semantics — the ``/entry-anatomy`` skill
  (``entry_anatomy.py``'s ``PARTS`` / ``DICT_MAPS``), which segments a CDSL entry
  into headword · grammar · etymology · sense · citation · cross-reference.
* The raw-markup highlighting approach and dark palette —
  ``SanskritLexicography/EntryAnatomy/build_entry_anatomy.py`` ``raw_highlight()``
  + ``GENERIC_EXTRA_CSS``, whose colours already sit on a dark panel.

The difference from both: those render a whole located record onto their own page
with a stylesheet. Review sheets are emitted by ``csl_pyutil.render_review_sheet``,
which exposes NO caller-CSS hook, so every colour here is an inline ``style=`` on a
self-contained span and the output can be dropped into any panel body.
"""
import html
import re

#: Part class -> (colour, human label, extra CSS). Dark-panel palette, matching the
#: review sheet's own --panel2 (#1e222b). Labels drive the rendered legend.
#: Labels are Russian: the only surface rendering this legend is the review sheet,
#: whose reviewer reads Russian (H1648). Keys stay English machine identifiers.
PARTS = {
    "sanskrit": ("#e6c07b", "санскритская форма", ""),
    "gloss": ("#98c379", "перевод / значение", "font-style:italic"),
    "citation": ("#e06c75", "ссылка на источник", ""),
    "grammar": ("#d19a66", "грамматическая помета", ""),
    "crossref": ("#56b6c2", "маркер перекрёстной ссылки (cf. / Vgl.)", "font-weight:600"),
    "etymology": ("#61afef", "этимология / когнат", ""),
    "language": ("#7aa2c9", "название языка", ""),
    "taxon": ("#c678dd", "ботаническое / зоологическое название", ""),
    "homonym": ("#b57edc", "номер омонима", ""),
    "structure": ("#7f8c9b", "разделитель значения / раздела", ""),
}

#: Paired content tags -> part class. ``<s>``/``<s1>``/``<s2>`` are MW's Sanskrit
#: spans; ``<is>`` is PWG's. ``<ab>`` carries the cf./Vgl. marker that IS the
#: cross-reference evidence, so it gets the brightest treatment.
TAG_PARTS = {
    "s": "sanskrit", "s1": "sanskrit", "s2": "sanskrit", "is": "sanskrit",
    "ns": "gloss",
    "ls": "citation",
    "lex": "grammar",
    "ab": "crossref",
    "etym": "etymology",
    "lang": "language",
    "bot": "taxon", "zoo": "taxon",
    "hom": "homonym",
}

#: Brace markers -> part class. ``{#…#}`` Sanskrit, ``{%…%}`` gloss (PWG/AP90),
#: ``{@…@}`` a sense/section number.
BRACE_PARTS = {"#": "sanskrit", "%": "gloss", "@": "structure"}

_DELIM = "#5c6773"          # tag/brace delimiters — present but receded
_ACCENT = "#ff7b72"         # Vedic accent marks inside a Sanskrit form
_PIPE = "#e06c75"           # the ¦ head/body separator
_PLAIN = "#d8dce2"          # untagged running text

_SCANNER = re.compile(
    r"(?P<pair><(?P<tag>s1|s2|s|is|ns|ls|lex|ab|etym|lang|bot|zoo|hom)\b(?P<attrs>[^>]*)>"
    r"(?P<inner>.*?)</(?P=tag)>)"
    r"|(?P<brace>\{(?P<bk>[#%@])(?P<binner>.*?)(?P=bk)\})"
    r"|(?P<other><[^>]+>)"
    r"|(?P<pipe>¦)",
    re.DOTALL,
)

#: Vedic accent / length marks CDSL writes inside SLP1 forms. Stripped only when
#: comparing a form against the cross-reference target.
_ACCENT_CHARS = "/\\^~"


def _strip_accents(text):
    return "".join(ch for ch in text if ch not in _ACCENT_CHARS)


def _span(text, colour, extra="", title=None, escape=True):
    body = html.escape(text) if escape else text
    style = f"color:{colour}"
    if extra:
        style += ";" + extra
    attrs = f' title="{html.escape(title)}"' if title else ""
    return f'<span style="{style}"{attrs}>{body}</span>'


def _sanskrit_body(inner, target_norm):
    """Colour a Sanskrit payload, marking accents and the cross-reference target."""
    colour, _label, extra = PARTS["sanskrit"]
    pieces = []
    for ch in inner:
        if ch in _ACCENT_CHARS:
            pieces.append(_span(ch, _ACCENT, "font-weight:700"))
        else:
            pieces.append(html.escape(ch))
    body = "".join(pieces)
    if target_norm and _strip_accents(inner).strip() == target_norm:
        # This span IS the cross-reference the card is asking about.
        return (
            '<span style="background:rgba(86,182,194,.22);outline:1px solid #56b6c2;'
            'border-radius:3px;padding:0 2px" title="цель перекрёстной ссылки, о которой спрашивает эта карточка">'
            + _span(body, colour, extra, escape=False)
            + "</span>"
        )
    return _span(body, colour, extra, escape=False)


def highlight(raw, target=None):
    """Return colour-coded HTML for one raw CDSL record body.

    ``target`` is the SLP1 cross-reference target; every Sanskrit form in the
    record equal to it (ignoring accent marks) is outlined.
    """
    text = str(raw or "")
    target_norm = _strip_accents(str(target or "").strip()) or None
    out = []
    pos = 0
    for m in _SCANNER.finditer(text):
        if m.start() > pos:
            out.append(_span(text[pos:m.start()], _PLAIN))
        if m.group("pair"):
            tag, attrs, inner = m.group("tag"), m.group("attrs") or "", m.group("inner")
            part = TAG_PARTS.get(tag, "structure")
            colour, label, extra = PARTS[part]
            out.append(_span(f"<{tag}{attrs}>", _DELIM, title=label))
            if part == "sanskrit":
                out.append(_sanskrit_body(inner, target_norm))
            else:
                out.append(_span(inner, colour, extra, title=label))
            out.append(_span(f"</{tag}>", _DELIM, title=label))
        elif m.group("brace"):
            bk, inner = m.group("bk"), m.group("binner")
            part = BRACE_PARTS.get(bk, "structure")
            colour, label, extra = PARTS[part]
            out.append(_span("{" + bk, _DELIM, title=label))
            if part == "sanskrit":
                out.append(_sanskrit_body(inner, target_norm))
            else:
                out.append(_span(inner, colour, extra, title=label))
            out.append(_span(bk + "}", _DELIM, title=label))
        elif m.group("other"):
            # <div n="v">, <info lex="m"/> and friends: structural, kept visible but quiet.
            out.append(_span(m.group("other"), _DELIM, title="structural markup"))
        else:
            out.append(_span("¦", _PIPE, "font-weight:700", title="headword / body separator"))
        pos = m.end()
    if pos < len(text):
        out.append(_span(text[pos:], _PLAIN))
    return (
        '<div style="background:#20242a;border-radius:6px;padding:12px 14px;'
        'font:12.5px/1.9 Consolas,\'Cascadia Mono\',monospace;white-space:pre-wrap;'
        'word-break:break-word">' + "".join(out) + "</div>"
    )


def legend_html(parts=None):
    """A compact swatch legend for the part classes, for one place on the sheet."""
    keys = list(parts or PARTS)
    chips = []
    for key in keys:
        colour, label, extra = PARTS[key]
        chips.append(
            f'<span style="display:inline-block;margin:0 10px 4px 0;white-space:nowrap">'
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
            f'background:{colour};margin-right:5px;vertical-align:baseline"></span>'
            f'<span style="color:{colour};{extra}">{html.escape(label)}</span></span>'
        )
    chips.append(
        '<span style="display:inline-block;margin:0 10px 4px 0;white-space:nowrap">'
        '<span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
        'background:rgba(86,182,194,.22);outline:1px solid #56b6c2;margin-right:5px"></span>'
        '<span style="color:#56b6c2">цель перекрёстной ссылки</span></span>'
    )
    return '<div style="font-size:12px;line-height:1.9">' + "".join(chips) + "</div>"
