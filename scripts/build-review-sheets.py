"""Generate csl-atlas's human-gated sheets with the shared csl-pyutil emitter.

Sheets sit on the 19-07-2026 org review-sheet standard (V1-V8), ratified from
the h178_da vote and implemented in csl_pyutil.render_review_sheet v0.3.0.
Which parts of the standard apply here, and why the rest deliberately does not:

* V3 show_ids, V6 note_min_height_px, V8 save_as -- applied to every sheet via
  STANDARD_CONFIG below.
* V4 title_href -- applied per sheet wherever the packet carries a real source
  link (xref edges, SKD units). The H4 and tradition packets have no per-row
  URL, so their headers stay plain text rather than inventing a target.
* V1/V5 rating -- deliberately NOT applied. The rating row scores a judgement
  on a scale; every csl-atlas sheet is a categorical label decision (confirm
  the proposed class, or reject and name the correct one in the note). A 1-5
  score has nothing to measure here, so adding it would ask the reviewer for a
  number that no downstream consumer reads.
* V7 mark_cyrillic -- deliberately NOT applied. It exists to separate the
  Russian text under judgement from surrounding markup and German. In these
  sheets the content under judgement is Sanskrit/IAST lemmas and Latin class
  labels; the only Cyrillic is the instruction chrome, which is the same on
  every card. Verified 19-07-2026: no card content in any of the four packets
  contains Cyrillic. Highlighting the chrome would be pure noise.
"""
import argparse
import csv
import html
import json
import sys
from pathlib import Path

from csl_pyutil import __version__ as CSL_PYUTIL_VERSION
from csl_pyutil import render_review_sheet
from sanskrit_util import from_slp1

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from cdsl_anatomy import highlight as cdsl_highlight, legend_html as cdsl_legend  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review"
DATE = "25-07-2026"  # H1646 xref reviewability: Cologne links, anatomy, taxonomy, sampling
#: Minimum, NOT exact: the V1–V8 standard shipped in csl-pyutil 0.3.0, and the
#: light-mode contrast fix (color-scheme:dark + hardened note textarea) in 0.3.1.
#: A `>=` check expresses "require at least the standard" so future emitter patch
#: releases don't hard-fail this builder (the equality-pin trap PR #5 flagged).
MIN_EMITTER_VERSION = "0.3.1"
REVIEWER = "gasyoun"


def _version_tuple(v):
    """Parse an X.Y.Z version string into an int tuple for ordering comparison."""
    out = []
    for token in str(v).split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)

#: V6 -- the standard's taller note box (the emitter's donor default is 44px,
#: ~2 rows; the standard doubles it). Same value as SanskritLexicography's
#: review_sheet_standard.NOTE_MIN_HEIGHT_PX, so sheets look alike across repos.
NOTE_MIN_HEIGHT_PX = 88

#: V3 + V6 -- applied to every csl-atlas sheet. V8 (save_as) is per-sheet
#: because the banner names that sheet's own destination file.
STANDARD_CONFIG = {"show_ids": True, "note_min_height_px": NOTE_MIN_HEIGHT_PX}


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def first_href(pointers):
    """V4 -- the card header's link target: the first source pointer that
    carries a real URL. Returns None when the packet has none (H4, tradition),
    in which case the header stays plain text."""
    for pointer in pointers or []:
        if pointer.get("href"):
            return pointer["href"]
    return None


def source_panels(pointers):
    if not pointers:
        return []
    rows = []
    for pointer in pointers:
        label = " · ".join(str(v) for v in (pointer.get("dictionary"), f"L{pointer['L']}" if pointer.get("L") else None, pointer.get("role")) if v)
        href = pointer.get("href")
        line = f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{html.escape(label or "источник")}</a>' if href else html.escape(label or "источник")
        excerpt = html.escape(str(pointer.get("bodyExcerpt", "")))
        rows.append(f"<p>{line}{('<br><code>' + excerpt + '</code>') if excerpt else ''}</p>")
    return [("Источник", "".join(rows))]


def emit(stem, title, subtitle, items, filters):
    if _version_tuple(CSL_PYUTIL_VERSION) < _version_tuple(MIN_EMITTER_VERSION):
        raise RuntimeError(
            f"csl-pyutil >= {MIN_EMITTER_VERSION} is required "
            f"(V1–V8 review-sheet standard + light-mode contrast fix); "
            f"found {CSL_PYUTIL_VERSION}. Run `npm run install-review-tools`."
        )
    config = {
        "sheet_id": stem,
        "title": title,
        "subtitle": subtitle,
        "footer": "✅ Подтвердить — принять предложенную классификацию; ❌ Отклонить — не принимать её; ⏸ Отложить — вернуться позже. В примечании укажите корректную альтернативу или частичную правку.",
        "approve_label": "✅ Подтвердить",
        "reject_label": "❌ Отклонить",
        "filters": filters,
        "generated": DATE,
        "strict_review": {
            "reviewer": REVIEWER,
            "require_all_votes": True,
            "require_reject_note": True,
        },
        # V8 -- banner binding the downloaded decisions file to this sheet.
        "save_as": f"csl-atlas\\review\\{stem}_decisions.json",
        **STANDARD_CONFIG,
    }
    OUT.mkdir(exist_ok=True)
    target = OUT / f"{stem}_review.html"
    target.write_text(render_review_sheet(items, config), encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({len(items)} items)")


def _iast(token):
    """Human-facing IAST from SLP1 machine keys (H1621). Empty/None → ''."""
    if not token:
        return ""
    return from_slp1(str(token))


def _humanize_h4_question(row):
    """Replace SLP1 lemma/field tokens in the machine question with IAST."""
    q = str(row.get("reviewQuestion") or "")
    tokens = [
        row.get("lemma"),
        (row.get("field") or {}).get("label"),
        (row.get("field") or {}).get("varga"),
        (row.get("field") or {}).get("kanda"),
        (row.get("field") or {}).get("upavarga"),
    ]
    for token in sorted({t for t in tokens if t}, key=len, reverse=True):
        q = q.replace(str(token), _iast(token))
    return q


def h4_items():
    """H4 sheet is no longer a human vote gate (H1621): show open rows if any,
    else the agent-adjudicated set with IAST titles. Machine keys stay SLP1."""
    packet = read_json("data/lexico/h4_semantic_field_review_packet.json")
    open_rows = [r for r in packet["sampleRows"] if r["reviewStatus"] == "needs-review"]
    rows = open_rows or [r for r in packet["sampleRows"] if r["reviewStatus"] == "reviewed-ok"]
    items = []
    for row in rows:
        options = ", ".join(row["expectedDecisionLabels"])
        lemma_iast = _iast(row["lemma"])
        field_iast = _iast((row.get("field") or {}).get("label") or "")
        agent = row.get("reviewedValue")
        agent_line = (
            f"<p><strong>Agent decision:</strong> <code>{html.escape(str(agent))}</code>"
            f" ({html.escape(str(row.get('reviewer') or ''))}).</p>"
            if agent else ""
        )
        question = (
            f"<p><strong>Предлагаемая метка:</strong> <code>{html.escape(row['proposedLabel'])}</code>.</p>"
            f"<p>{html.escape(_humanize_h4_question(row))}</p>"
            f"{agent_line}"
            f"<p>Допустимые итоговые метки: <code>{html.escape(options)}</code>. "
            "H1621: human vote not required; agent adjudication is the stage of record.</p>"
        )
        items.append({
            "id": row["reviewId"],
            "filt": row["sampleType"],
            "title": f"{row['sampleLabel']}: {lemma_iast} [SLP1 {row['lemma']}]",
            "badges": [row["dictionary"]["label"], field_iast or row["field"]["label"]],
            "question": question,
            "panels": source_panels(row.get("sourcePointers", [])),
            "note_placeholder": "Agent stage closed; optional override note only.",
        })
    return items


#: Muted body text inside the xref reference blocks; the sheet exposes no caller
#: CSS hook, so every colour on this sheet is an inline style.
_MUTED = "#9aa3b2"


def _details(summary, body, open_by_default=False):
    """A collapsed reference block. Cards carry their own copy rather than pointing
    at the sticky sheet header — that header would cover the viewport when expanded,
    and a reviewer on card 27 should not have to scroll back to card 1 for a definition."""
    attr = " open" if open_by_default else ""
    return (
        f'<details{attr} style="margin:8px 0 0"><summary style="cursor:pointer;color:{_MUTED};'
        f'font-size:12.5px">{html.escape(summary)}</summary>'
        f'<div style="margin:8px 0 0;font-size:12.5px;line-height:1.65">{body}</div></details>'
    )


def _label_vocabulary_html(vocabulary):
    """Fix 1 (H1646): the closed label set, each with what it does and does not assert
    plus two worked examples from this packet. Previously the sheet named three reject
    options and defined none of them."""
    blocks = []
    for entry in vocabulary:
        if not entry.get("appliesToSheet"):
            continue
        examples = "".join(
            f'<li><code>{html.escape(ex["sampleId"])}</code> — {html.escape(ex["edge"])}<br>'
            f'<span style="color:{_MUTED}">{html.escape(ex["why"])}</span></li>'
            for ex in entry.get("examples", [])
        )
        blocks.append(
            f'<p style="margin:10px 0 4px"><code>{html.escape(entry["label"])}</code> — '
            f'{html.escape(entry["meaning"])}</p>'
            f'<p style="margin:0 0 4px"><strong>Утверждает:</strong> {html.escape(entry.get("asserts", ""))}</p>'
            f'<p style="margin:0 0 4px"><strong>НЕ утверждает:</strong> {html.escape(entry.get("doesNotAssert", ""))}</p>'
            f'<ul style="margin:0 0 6px;padding-left:20px">{examples}</ul>'
        )
    return "".join(blocks)


def _selection_policy_html(packet):
    """Fix 4 (H1646): how these 40 rows were chosen — "I do not see the list of methods
    used for sampling these words". The packet has always carried selectionPolicy and
    limitations; nothing rendered them."""
    steps = "".join(f"<li>{html.escape(step)}</li>" for step in packet.get("selectionPolicy", []))
    limits = "".join(f"<li>{html.escape(item)}</li>" for item in packet.get("limitations", []))
    counts = packet.get("counts", {})
    artifact = packet.get("sourceArtifact", {})
    return (
        f"<p><strong>Отбор</strong></p><ol style='margin:0 0 8px;padding-left:20px'>{steps}</ol>"
        f"<p><strong>Счётчики:</strong> {counts.get('sharedCoreRows')} строк shared-core, "
        f"{counts.get('exactSharedCorePointers')} записей-источников, "
        f"{counts.get('sharedCoreRowsWithMissingExactEdge')} строк только с одним словарём; "
        f"{counts.get('prefixControlRows')} prefix-control автоматически разрешены "
        f"(<code>{html.escape(str(list(counts.get('byAutoDecision', {}).keys())))}</code>).</p>"
        f"<p><strong>Источник выборки:</strong> <code>{html.escape(str(artifact.get('path')))}</code>, "
        f"построен <code>{html.escape(str(artifact.get('generatedBy')))}</code>.</p>"
        f"<p><strong>Ограничения</strong></p><ul style='margin:0;padding-left:20px'>{limits}</ul>"
    )


def _link_row(links):
    """Render the (label, href) pairs that survive as a single separated line."""
    parts = [
        f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{html.escape(label)}</a>'
        for label, href in links if href
    ]
    return " · ".join(parts)


def xref_source_panels(row):
    """One panel per dictionary record: Cologne + csl-orig links, then the record
    itself with its markup colour-coded (fixes 2 and 3 of H1646).

    Fix 2 — the card used to link only the csl-orig blob line. A reviewer asked to
    judge whether an edge is real needs to read the entry as the dictionary shows it,
    so each record now also links its Cologne entry display and its printed scan page.
    Fix 3 — the raw record was dumped into a bare <code> block; it is now segmented by
    part class, with the cross-reference target outlined where it occurs.
    """
    panels = []
    for pointer in row.get("sourcePointers", []):
        heading = f"Источник · {pointer.get('dictionary')} · L{pointer.get('L')}"
        links = _link_row([
            ("Кёльн: статья", pointer.get("cologneEntryHref")),
            (f"скан {pointer.get('pc')}" if pointer.get("pc") else "скан", pointer.get("cologneScanHref")),
            ("csl-orig", pointer.get("href")),
        ])
        excerpt = pointer.get("bodyExcerpt", "")
        body = cdsl_highlight(excerpt, target=row.get("target")) if excerpt else ""
        panels.append((heading, f'<p style="margin:0 0 8px">{links}</p>{body}'))

    target_links = row.get("targetLinks", [])
    if target_links:
        target_iast = _iast(row["target"])
        heading = f"Цель ссылки · {target_iast} [SLP1 {row['target']}]"
        links = _link_row([
            (f"Кёльн: {link['dictionary']}", link.get("cologneEntryHref")) for link in target_links
        ])
        panels.append((heading, (
            f'<p style="margin:0 0 6px">{links}</p>'
            f'<p style="margin:0;color:{_MUTED}">Другой конец ребра. Ссылка ведёт на статью-заголовок; '
            f'при омонимах Кёльн покажет все статьи под этим заголовком.</p>'
        )))
    return panels


def xref_items():
    packet = read_json("data/lexico/xref_source_check_packet.json")
    vocabulary_html = _label_vocabulary_html(packet.get("packetLabelVocabulary", []))
    policy_html = _selection_policy_html(packet)
    legend = cdsl_legend()
    items = []
    for row in packet["sharedCoreRows"]:
        source_iast, target_iast = _iast(row["sourceLemma"]), _iast(row["target"])
        # Same H1621 rule as the H4 sheet: the machine question is written in SLP1;
        # show the reviewer IAST, keeping the SLP1 key alongside it.
        question_text = row["reviewQuestion"]
        for slp1, iast in sorted(
            {row["sourceLemma"]: source_iast, row["target"]: target_iast}.items(),
            key=lambda kv: len(kv[0]), reverse=True,
        ):
            question_text = question_text.replace(slp1, f"{iast} [{slp1}]")
        missing = row.get("missingExactEdgeDictionaries", [])
        # A row with only one dictionary attached cannot demonstrate the "shared" in
        # shared-core. Say so on the card instead of letting the reviewer discover it
        # by counting panels — this is precisely the `too-sparse` case.
        sparse_note = (
            f'<p style="margin:6px 0 0;color:#e6c07b">⚠ Приложена запись только одного словаря '
            f'({", ".join(html.escape(d) for d in row.get("matchedDictionaries", []))}); '
            f'{", ".join(html.escape(d) for d in missing)} — точного ребра нет. Общность здесь '
            f'не показана, поэтому <code>too-sparse</code> — законный ответ.</p>'
        ) if missing else ""
        question = (
            f'<p><strong>Предложение:</strong> <code>lexical-shared-core</code>.</p>'
            f"<p>{html.escape(question_text)}</p>"
            f"{sparse_note}"
            "<p>Подтвердите значимое общее лексическое ребро либо отклоните и укажите в примечании "
            "<code>prefix-convention</code>, <code>normalization-risk</code> или <code>too-sparse</code>. "
            "Определения и по два разобранных примера — ниже.</p>"
            + _details("Словарь меток: что означает каждая и когда её выбирать", vocabulary_html)
            + _details("Как отобраны эти 40 рёбер (метод выборки и его ограничения)", policy_html)
            + _details("Легенда разметки статьи", legend)
        )
        item = {
            "id": row["sampleId"],
            "filt": "shared-core",
            # H1621 display rule: IAST for the human, SLP1 kept visible as the machine key.
            "title": f"{source_iast} → {target_iast}",
            "badges": row.get("matchedDictionaries", ["MW", "PWG"])
                      + [f"SLP1 {row['sourceLemma']} → {row['target']}"],
            "question": question,
            "panels": xref_source_panels(row),
            "note_placeholder": "Если отклоняете: corrected-label: краткое основание.",
        }
        # V4 — the header now opens the Cologne entry, the thing a reviewer wants to
        # read, rather than the csl-orig source line.
        pointers = row.get("sourcePointers", [])
        href = next((p.get("cologneEntryHref") for p in pointers if p.get("cologneEntryHref")), None)
        if href or first_href(pointers):
            item["title_href"] = href or first_href(pointers)
        items.append(item)
    return items


def tradition_items():
    rows = list(csv.DictReader((ROOT / "data/citations/tradition_tags.tsv").open(encoding="utf-8"), delimiter="\t"))
    items = []
    for row in rows:
        if row.get("reviewed") == "yes":
            continue
        proposed = row["tradition"]
        items.append({"id": row["canonical_text"], "filt": proposed,
                      "title": row["canonical_text"], "badges": [proposed, row.get("confidence", "")],
                      "question": f"<p>Машинная/редакционная гипотеза: <code>{html.escape(proposed)}</code>.</p>"
                                  "<p>Подтвердите её либо отклоните и укажите в примечании одну метку из закрытого словаря традиций.</p>",
                      "panels": [("Контекст", html.escape(row.get("note", "Нет дополнительного комментария.")))],
                      "note_placeholder": "Если отклоняете: corrected-label: краткое основание."})
    return items


def skd_items():
    sample = read_json("data/lexico/r2_kosa_fusion_sample.json")
    items = []
    for row in sample["rows"]:
        item_id = f"skd-iti:{row['L']}:{row['unitIndex']}"
        href = f"https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L{row['L']}"
        question = (
            f"<p><strong>Классификатор предлагает:</strong> <code>{html.escape(row['klass'])}</code>.</p>"
            "<p>Подтвердите классификацию единицы <em>iti</em> как цитатной/грамматической границы либо отклоните "
            "и укажите в примечании <code>authority-terminal</code>, <code>separable</code> или <code>other-no-authority</code>.</p>"
        )
        panel = [("Источник", f'<p><a href="{href}" target="_blank" rel="noopener">SKD L{row["L"]}</a></p><code>{html.escape(row["text"])}</code>')]
        items.append({"id": item_id, "filt": row["klass"], "title": f"{row['k1']} · единица {row['unitIndex']}",
                      "title_href": href,  # V4
                      "badges": [row["klass"]], "question": question, "panels": panel,
                      "note_placeholder": "Если отклоняете: corrected-label: краткое основание."})
    return items


BUILDERS = {
    "h4": (
        "csl-atlas-h4-semantic-field_89rows",
        "H4: семантические поля (IAST display; agent stage H1621)",
        "Пакет H4; леммы/поля в IAST; ключи SLP1. Human vote not required after agent adjudication.",
        h4_items,
        [("skd-false-low", "SKD"), ("vcp-high-coverage", "VCP"), ("ap-ap90-delta", "AP/AP90"), ("specialized-baseline", "специализированные"), ("index-reverse-control", "контроль")],
    ),
    "xref": (
        "csl-atlas-xref-shared-core_40edges",
        "Xref: общие MW/PWG рёбра — 40 строк",
        "Первые 40 из 642 общих рёбер в порядке заголовков (не случайная выборка); "
        "prefix-control разрешены автоматически. На каждой карточке: ссылки в Кёльн на оба конца ребра, "
        "разметка статьи с подсветкой, словарь меток и метод отбора.",
        xref_items,
        [("shared-core", "общие рёбра")],
    ),
    "tradition": ("csl-atlas-tradition-tags_119texts", "Теги традиций — 119 текстов", "Неавтоматизированная проверка, разблокирующая A50.", tradition_items, []),
    # Keep the historical 100units stem: it is part of the download filename,
    # sheet ID, and localStorage key contract. The corrected visible count is 102.
    "skd-iti": ("csl-atlas-skd-iti_100units", "SKD iti: 102 единицы для адъюдикации", "Общая доказательная очередь A02/A08/A30.", skd_items, [("authority-terminal", "authority-terminal"), ("separable", "separable"), ("other-no-authority", "other-no-authority")]),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=BUILDERS.keys())
    choice = parser.parse_args().only
    for key, (stem, title, subtitle, builder, filters) in BUILDERS.items():
        if choice and key != choice:
            continue
        emit(stem, title, subtitle, builder(), filters)


if __name__ == "__main__":
    main()
