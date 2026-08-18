"""H1684 — build the stratified BLIND spot-check sheet for the reduced human ask.

The agent stage (adjudicate-h1684-skd-iti.mjs + adjudicate-h1684-tradition-tags.mjs)
rules on all 221 rows of the two В2 sheets. This script turns that into the only
thing still owed to a human:

  1. FORKS — every row the agent could not decide, shown WITH its analysis. The
     reviewer rules; these are not part of any statistical gate.
  2. BLIND SAMPLE — a stratified sample of the rows the agent DID decide, shown
     WITHOUT the agent's verdict. The reviewer sees exactly what the original
     sheet showed (the machine/seed proposal) and votes independently. Agreement
     between that vote and the hidden agent verdict is what the promotion gate
     measures.

Blindness is the point: a reviewer shown "the agent says authority-terminal"
cannot produce an independent measurement of whether the agent is right.

── Sample size derivation (NOT hardcoded) ─────────────────────────────────────
Per stratum, promotion requires the Wilson 95% LOWER bound on the agreement
proportion to reach PROMOTION_FLOOR. Sizing solves for the smallest n at which
unanimous agreement would clear that floor, under a finite-population correction
(the strata are small and sampled without replacement, so the infinite-population
Wilson interval overstates the required n):

    lower(n of n) = n / (n + z^2 * f),  f = (N - n) / (N - 1)
    => n >= pi0 * z^2 * N / ((1 - pi0) * (N - 1) + pi0 * z^2)

Wilson form matches scripts/compound_share.py (the repo's existing implementation).

Usage: python scripts/build_h1684_spotcheck_sheet.py
Writes: review/csl-atlas-h1684-spotcheck_<n>rows_review.html
        review/csl-atlas-h1684-spotcheck_manifest.json
"""
import html
import json
import math
import sys
from pathlib import Path

from csl_pyutil import __version__ as CSL_PYUTIL_VERSION
from csl_pyutil import render_review_sheet

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review"
HANDOFF = "H1684"
DATE = "27-07-2026"

#: Wilson z for a 95% interval, and the agreement floor a stratum must clear
#: before its agent verdicts may be promoted to reviewed=yes.
Z = 1.96
PROMOTION_FLOOR = 0.80

SKD_PACKET = ROOT / "data/lexico/h1684_skd_iti_adjudication_packet.json"
TRAD_PACKET = ROOT / "data/citations/h1684_tradition_adjudication_packet.json"

SKD_CLASSES = ["authority-terminal", "separable", "other-no-authority"]

UI_STRINGS_RU = {
    "download_button": "Скачать decisions.json",
    "save_button": "Сохранять в папку…",
    "footer_hint": (
        "Клавиши: <kbd>a</kbd> — подтвердить &middot; <kbd>r</kbd> — отклонить &middot; "
        "<kbd>d</kbd> — отложить &middot; <kbd>&darr;</kbd>/<kbd>&uarr;</kbd> — следующая/предыдущая "
        "карточка. Голоса сохраняются в localStorage этого браузера; когда закончите, "
        "нажмите «Скачать decisions.json»."
    ),
    "legend": (
        "<b>Подтвердить</b> — согласиться с предложением на карточке. <b>Отклонить</b> — не "
        "согласиться; в примечании укажите верную метку. <b>Отложить</b> — вернуться позже. "
        "В группе «выборка» вердикт агента намеренно скрыт: ваш голос — независимое измерение, "
        "по нему считается доверительная граница Уилсона."
    ),
    # H3103: chrome keys added in csl-pyutil v0.18.0/v0.20.0, absent from
    # this dict since it predates them — see build-review-sheets.py's H3103
    # comment for the full "%(n)d items"/"Generated"/lang="en" backstory.
    "count_suffix": "карточек",
    "generated_label": "Собрано",
    "doc_lang": "ru",
    "filter_all": "все",
    "filter_unvoted": "только непроголосованные",
}


def wilson_lower(k, n, z=Z, population=None):
    """Wilson 95% lower bound, with an optional finite-population correction.

    Same algebra as scripts/compound_share.py:wilson(), returned as a
    proportion rather than a percentage, plus the (N-n)/(N-1) variance scale
    when the stratum is a finite population sampled without replacement.
    """
    if n == 0:
        return 0.0
    p = k / n
    f = 1.0
    if population and population > 1:
        f = max(0.0, (population - n) / (population - 1))
    d = 1 + z * z * f / n
    c = p + z * z * f / (2 * n)
    h = z * math.sqrt(f * p * (1 - p) / n + z * z * f * f / (4 * n * n))
    return (c - h) / d


def required_n(population, pi0=PROMOTION_FLOOR, z=Z):
    """Smallest n whose unanimous agreement clears pi0 (finite-population)."""
    if population <= 1:
        return population
    zz = z * z
    n = pi0 * zz * population / ((1 - pi0) * (population - 1) + pi0 * zz)
    return min(population, max(1, math.ceil(n - 1e-9)))


def systematic(rows, n):
    """Deterministic stratified pick: sort by id, take every k-th.

    Systematic rather than random so the sample is reproducible from the
    committed packets alone — the same idiom as build-r2-kosa-fusion.mjs's
    buildSample(), and it needs no seeded RNG.
    """
    ordered = sorted(rows, key=lambda r: str(r["reviewId"]))
    if n >= len(ordered):
        return ordered
    step = len(ordered) / n
    return [ordered[min(len(ordered) - 1, int(i * step))] for i in range(n)]


def esc(value):
    return html.escape(str(value if value is not None else ""))


def skd_card(row, blind):
    """Card for one SKD iti-unit. In blind mode the agent verdict is omitted and
    the card shows exactly what the original sheet showed."""
    href = row["sourceHref"]
    proposed = row["proposedClass"]
    vocab = " · ".join("<code>%s</code>" % c for c in SKD_CLASSES)
    question = (
        "<p><strong>Классификатор предлагает:</strong> <code>%s</code>.</p>"
        "<p>Единица <em>iti</em> — цитатная граница (заканчивается формулой авторитета) "
        "или грамматическая? Подтвердите предложенный класс либо отклоните и укажите в "
        "примечании один из: %s.</p>" % (esc(proposed), vocab)
    )
    if not blind:
        question += (
            '<p style="margin-top:10px;color:#e6c07b"><strong>Агент не смог решить.</strong> %s</p>'
            % esc(row["evidence"])
        )
    panels = [(
        "Источник",
        '<p><a href="%s" target="_blank" rel="noopener">SKD L%s</a> · единица %s · %s знаков</p><code>%s</code>'
        % (esc(href), esc(row["L"]), esc(row["unitIndex"]), esc(row["fullUnitChars"]), esc(row["unitText"]))
    )]
    return {
        "id": row["reviewId"],
        "title": "%s · единица %s" % (esc(row["k1"]), esc(row["unitIndex"])),
        "title_href": href,
        "badges": [proposed, "SKD"],
        "question": question,
        "panels": panels,
        "note_placeholder": "Если отклоняете: corrected-label: краткое основание.",
    }


def trad_card(row, blind):
    proposed = row["proposedTradition"]
    question = (
        "<p>Машинная/редакционная гипотеза: <code>%s</code>.</p>"
        "<p>Подтвердите её либо отклоните и укажите в примечании одну метку из закрытого "
        "словаря традиций.</p>" % esc(proposed)
    )
    if not blind:
        question += (
            '<p style="margin-top:10px;color:#e6c07b"><strong>Агент не смог решить (%s).</strong> %s</p>'
            % (esc(row["rule"]), esc(row["why"]))
        )
    panels = []
    if row.get("seedNote"):
        panels.append(("Комментарий из таблицы", esc(row["seedNote"])))
    entries = row.get("crosswalkPairs") or []
    if entries:
        body = "".join(
            "<p><b>%s</b> ↔ <b>%s</b> (Tier %s)<br><code>%s</code><br><code>%s</code></p>"
            % (esc(p["accId"]), esc(p["nccId"]), esc(p["tier"]), esc(p["accExcerpt"]), esc(p["nccExcerpt"]))
            for p in entries[:3]
        )
        panels.append(("Каталог ACC↔NCC (сшитые пары)", body))
    else:
        cat = row.get("catalogueEntries") or []
        if cat:
            body = "".join(
                "<p><b>%s</b>%s<br><code>%s</code></p>"
                % (esc(e["id"]), (" · sigla: %s" % esc(", ".join(e["sigla"]))) if e["sigla"] else "", esc(e["excerpt"]))
                for e in cat[:4]
            )
            panels.append(("Каталог ACC/NCC (совпадения по заглавию)", body))
        else:
            panels.append(("Каталог ACC/NCC", "Записи под свёрнутым ключом не найдены."))
    return {
        "id": row["reviewId"],
        "title": esc(row["canonicalText"]),
        "badges": [proposed, row.get("seedConfidence", "")],
        "question": question,
        "panels": panels,
        "note_placeholder": "Если отклоняете: corrected-label: краткое основание.",
    }


def main():
    skd = json.loads(SKD_PACKET.read_text(encoding="utf-8"))
    trad = json.loads(TRAD_PACKET.read_text(encoding="utf-8"))

    skd_rows = skd["rows"]
    trad_rows = trad["rows"]

    forks = (
        [("skd-iti", r) for r in skd_rows if r["verdict"] == "uncertain"]
        + [("tradition", r) for r in trad_rows if r["verdict"] == "uncertain"]
    )

    strata = [
        {
            "key": "skd-iti/agent-confirmed",
            "sheet": "skd-iti",
            "description": "Единицы SKD, где агент подтвердил класс классификатора.",
            "rows": [r for r in skd_rows if r["verdict"] == "confirm"],
        },
        {
            "key": "skd-iti/agent-corrected",
            "sheet": "skd-iti",
            "description": "Единицы SKD, где агент ИЗМЕНИЛ класс классификатора (наибольший риск).",
            "rows": [r for r in skd_rows if r["verdict"] == "correct"],
        },
        {
            "key": "tradition/canonical-attribution",
            "sheet": "tradition",
            "description": "Тексты, где традиция бесспорна и правило по умолчанию подтвердило тег.",
            "rows": [r for r in trad_rows if r["verdict"] == "confirm" and r["rule"] == "canonical-attribution"],
        },
        {
            "key": "tradition/ruled-override",
            "sheet": "tradition",
            "description": "Тексты, решённые явным правилом (омоним, вариант OCR, не-произведение, комментатор…).",
            "rows": [r for r in trad_rows if r["verdict"] == "confirm" and r["rule"] != "canonical-attribution"],
        },
    ]

    items = []
    manifest_strata = []
    filters = [("fork", "решение (форк)"), ("sample", "выборка (вслепую)")]

    for sheet, row in forks:
        card = skd_card(row, blind=False) if sheet == "skd-iti" else trad_card(row, blind=False)
        card["filt"] = "fork"
        card["id"] = "%s::%s" % (sheet, card["id"])
        items.append(card)

    for st in strata:
        population = len(st["rows"])
        n = required_n(population)
        picked = systematic(st["rows"], n)
        for row in picked:
            card = skd_card(row, blind=True) if st["sheet"] == "skd-iti" else trad_card(row, blind=True)
            card["filt"] = "sample"
            card["id"] = "%s::%s" % (st["sheet"], card["id"])
            items.append(card)
        manifest_strata.append({
            "key": st["key"],
            "sheet": st["sheet"],
            "description": st["description"],
            "population": population,
            "sampled": len(picked),
            "requiredN": n,
            "unanimousLowerBound": round(wilson_lower(len(picked), len(picked), population=population), 4),
            "members": [
                {
                    "reviewId": "%s::%s" % (st["sheet"], r["reviewId"]),
                    # The hidden half of the comparison. Present in the manifest
                    # (a machine artefact) but never rendered on the sheet.
                    "agentLabel": r["agentClass"] if st["sheet"] == "skd-iti" else r["agentTradition"],
                    "proposedLabel": r["proposedClass"] if st["sheet"] == "skd-iti" else r["proposedTradition"],
                }
                for r in picked
            ],
        })

    total_sampled = sum(s["sampled"] for s in manifest_strata)
    stem = "csl-atlas-h1684-spotcheck_%drows" % len(items)
    save_as = "review/%s_decisions.json" % stem
    subtitle = (
        "Сокращённый человеческий запрос по H1684: %d форк(ов), где агент воздержался, "
        "плюс слепая стратифицированная выборка из %d строк (из 207 решённых агентом). "
        "Порог продвижения: нижняя граница Уилсона 95%% ≥ %.2f по каждому слою. "
        "Всего к проверке %d строк вместо исходных 221."
        % (len(forks), total_sampled, PROMOTION_FLOOR, len(items))
    )

    config = {
        "sheet_id": stem,
        "generated": DATE,
        "title": "H1684: форки + слепая выборка (SKD iti + теги традиций)",
        "subtitle": subtitle,
        "footer": (
            "✅ Подтвердить — принять предложение карточки; ❌ Отклонить — указать верную метку "
            "в примечании; ⏸ Отложить — вернуться позже. Группа «выборка» намеренно не показывает "
            "вердикт агента."
        ),
        "approve_label": "✅ Подтвердить",
        "reject_label": "❌ Отклонить",
        "filters": filters,
        "show_ids": True,
        "note_min_height_px": 88,
        "save_as": save_as,
        "ui_strings": {
            **UI_STRINGS_RU,
            "save_banner": (
                "&#128229; Экспорт скачается файлом <code>%s_decisions.json</code> &rarr; "
                "сохраните его в <code>%s</code>, затем запустите "
                "<code>python scripts/apply_h1684_spotcheck.py</code>." % (stem, html.escape(save_as))
            ),
        },
    }

    OUT.mkdir(exist_ok=True)
    target = OUT / ("%s_review.html" % stem)
    target.write_text(render_review_sheet(items, config), encoding="utf-8")

    manifest = {
        "schemaVersion": "1.0.0",
        "handoff": HANDOFF,
        "sheetId": stem,
        "generated": DATE,
        "emitter": "csl_pyutil %s" % CSL_PYUTIL_VERSION,
        "gate": {
            "z": Z,
            "promotionFloor": PROMOTION_FLOOR,
            "rule": (
                "Per stratum: promote its agent verdicts to reviewed=yes only if the Wilson 95%% "
                "lower bound of human-agent agreement reaches %.2f. Strata are gated "
                "independently; a stratum that fails stays unpromoted and its rows return to the "
                "human queue." % PROMOTION_FLOOR
            ),
            "sizing": "n >= pi0*z^2*N / ((1-pi0)*(N-1) + pi0*z^2)  [finite-population corrected]",
            "blind": "Sample cards omit the agent verdict; agentLabel lives only in this manifest.",
        },
        "forks": [
            {"reviewId": "%s::%s" % (sheet, r["reviewId"]), "sheet": sheet, "rule": r["rule"]}
            for sheet, r in forks
        ],
        "strata": manifest_strata,
        "counts": {
            "originalHumanAsk": len(skd_rows) + len(trad_rows),
            "agentDecided": len(skd_rows) + len(trad_rows) - len(forks),
            "forks": len(forks),
            "blindSampled": total_sampled,
            "reducedHumanAsk": len(items),
        },
    }
    (OUT / ("%s_manifest.json" % stem)).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Wrote %s" % target.relative_to(ROOT))
    print("Wrote %s" % (OUT / ("%s_manifest.json" % stem)).relative_to(ROOT))
    print("forks=%d blind-sampled=%d total=%d (was %d)"
          % (len(forks), total_sampled, len(items), manifest["counts"]["originalHumanAsk"]))
    for s in manifest_strata:
        print("  %-36s N=%-4d n=%-3d unanimous-lower=%.3f"
              % (s["key"], s["population"], s["sampled"], s["unanimousLowerBound"]))


if __name__ == "__main__":
    main()
