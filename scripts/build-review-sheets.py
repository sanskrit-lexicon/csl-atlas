"""Generate csl-atlas's human-gated sheets with the shared csl-pyutil emitter."""
import argparse
import csv
import html
import json
import sys
from pathlib import Path

from csl_pyutil import __version__ as CSL_PYUTIL_VERSION
from csl_pyutil import render_review_sheet

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review"
DATE = "17-07-2026"  # explicit for reproducible artifacts
REQUIRED_EMITTER_VERSION = "0.2.0"
REVIEWER = "gasyoun"


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


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
    if CSL_PYUTIL_VERSION != REQUIRED_EMITTER_VERSION:
        raise RuntimeError(
            f"csl-pyutil {REQUIRED_EMITTER_VERSION} is required; "
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
    }
    OUT.mkdir(exist_ok=True)
    target = OUT / f"{stem}_review.html"
    target.write_text(render_review_sheet(items, config), encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({len(items)} items)")


def h4_items():
    packet = read_json("data/lexico/h4_semantic_field_review_packet.json")
    items = []
    for row in packet["sampleRows"]:
        if row["reviewStatus"] != "needs-review":
            continue
        options = ", ".join(row["expectedDecisionLabels"])
        question = (
            f"<p><strong>Предлагаемая метка:</strong> <code>{html.escape(row['proposedLabel'])}</code>.</p>"
            f"<p>{html.escape(row['reviewQuestion'])}</p>"
            f"<p>Допустимые итоговые метки: <code>{html.escape(options)}</code>. "
            "Подтвердите предложенную оценку либо отклоните и укажите итоговую метку в примечании.</p>"
        )
        items.append({"id": row["reviewId"], "filt": row["sampleType"],
                      "title": f"{row['sampleLabel']}: {row['lemma']}",
                      "badges": [row["dictionary"]["label"], row["field"]["label"]],
                      "question": question, "panels": source_panels(row.get("sourcePointers", [])),
                      "note_placeholder": "Если отклоняете: corrected-label: краткое основание."})
    return items


def xref_items():
    packet = read_json("data/lexico/xref_source_check_packet.json")
    items = []
    for row in packet["sharedCoreRows"]:
        question = (
            f"<p><strong>Предложение:</strong> <code>lexical-shared-core</code>.</p>"
            f"<p>{html.escape(row['reviewQuestion'])}</p>"
            "<p>Подтвердите значимое общее лексическое ребро либо отклоните и укажите в примечании "
            "<code>prefix-convention</code>, <code>normalization-risk</code> или <code>too-sparse</code>.</p>"
        )
        items.append({"id": row["sampleId"], "filt": "shared-core",
                      "title": f"{row['sourceLemma']} → {row['target']}",
                      "badges": row.get("matchedDictionaries", ["MW", "PWG"]), "question": question,
                      "panels": source_panels(row.get("sourcePointers", [])),
                      "note_placeholder": "Если отклоняете: corrected-label: краткое основание."})
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
                      "badges": [row["klass"]], "question": question, "panels": panel,
                      "note_placeholder": "Если отклоняете: corrected-label: краткое основание."})
    return items


BUILDERS = {
    "h4": ("csl-atlas-h4-semantic-field_89rows", "H4: семантические поля — 89 строк", "Пакет H4; авторазрешённые строки исключены.", h4_items, [("skd-false-low", "SKD"), ("vcp-high-coverage", "VCP"), ("ap-ap90-delta", "AP/AP90"), ("specialized-baseline", "специализированные"), ("index-reverse-control", "контроль")]),
    "xref": ("csl-atlas-xref-shared-core_40edges", "Xref: общие MW/PWG рёбра — 40 строк", "Пакет xref; prefix-control уже разрешены автоматически.", xref_items, [("shared-core", "общие рёбра")]),
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
