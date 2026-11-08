#!/usr/bin/env python3
"""A72 pedagogy (H6465): student label-reading guide, computed from the census payload.

Every guide row is derived from data/abbrev/abbrev_census.json (H6409) — never
hand-assigned and never paraphrased from memory. A label the payload does not
carry is emitted with an explicit «not in census» verdict (the handoff's fail
condition), never silently glossed.

Outputs:
  docs/A72_LABEL_READING_GUIDE.ru.md   — RU-primary student guide (generated)
  data/abbrev/label_guide_rows.tsv     — machine-readable twin (label -> payload row)

`--check` regenerates into a temp dir and byte-compares against the committed
files: derive-don't-store parity gate.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAYLOAD = REPO / "data" / "abbrev" / "abbrev_census.json"
GUIDE_OUT = REPO / "docs" / "A72_LABEL_READING_GUIDE.ru.md"
TSV_OUT = REPO / "data" / "abbrev" / "label_guide_rows.tsv"
TSV_HEADER = ["section", "label", "in_census", "distinct_expansions", "expansion", "legend_dicts", "corpus_tag_dicts"]

# The teaching set, ordered as the guide reads. (section_key, label, ru_heading)
GUIDE_LABELS = [
    ("gender", "m.", "Мужской род"),
    ("gender", "f.", "Женский род"),
    ("gender", "n.", "Средний род"),
    ("gender", "mfn.", "Все три рода / прилагательное"),
    ("pada", "P.", "Парасмайпада (актив)"),
    ("pada", "A.", "Атманепада (медиум)"),
    ("pada", "U.", "Оба пады"),
    ("verbclass", "c.", "Каузатив / падеж"),
    ("verbclass", "D.", "Деноминатив / дезидератив / дат. / дэва"),
    ("verbclass", "med.", "Медиум (лат. medium)"),
    ("participle", "p.", "Стр. / прич. / мн. ч. и др."),
    ("participle", "pp.", "Причастие прошедшего времени"),
    ("titles", "V.", "Веда / глагол / изд. Бардвана"),
    ("titles", "P.", "Панини / парасмайпада"),
    ("titles", "N.", "Имя / Найшадха / налa"),
    ("titles", "M.", "Ману / маскулин / медиум"),
    ("titles", "S.", "Сутра / простое / см. (siehe)"),
    ("titles", "R.", "Рамаяна / корень / река"),
    ("titles", "K.", "Царь / Кадамбари / кинара"),
    ("titles", "H.", "Хитопадеша / небо / Хемачандра"),
    ("register", "inj.", "Инъюнктив (вне ценза — см. реестр E3)"),
]

SECTIONS = [
    ("gender", "Родовые пометы", "Одна буква — но словари пишут её по-разному (латынь, французский, немецкий)."),
    ("pada", "Залог/пада: P., A., U.", "Большие буквы — грамматика глагола: парасмайпада, атманепада, убхаяпада."),
    ("verbclass", "Каузатив, падеж и класс глагола", "Малые буквы, где самое опасное — перепутать грамматику с падежом."),
    ("participle", "Причастия: p., pp.", "p. и pp. — пять-шесть разных смыслов, считанных из легенд."),
    ("titles", "Однобуквенные титулы: V., N., M., S., R., K., H.", "Главная ловушка: заглавная буква может быть названием произведения, а не грамматикой."),
    ("register", "Что не входит в ценз", "Метка «нет в цензе» = у нас нет вычисленной строки; мы не пересказываем по памяти."),
]


def load_payload() -> dict:
    with PAYLOAD.open(encoding="utf-8") as f:
        return json.load(f)


def label_rows(payload: dict):
    """Yield one evidence row per (label, expansion) pair, computed from the payload."""
    lt = payload["labelTable"]
    rows = []
    for section, label, _heading in GUIDE_LABELS:
        row = lt.get(label)
        if not row:
            rows.append(
                {"section": section, "label": label, "in_census": False,
                 "distinct_expansions": 0, "expansion": "", "legend_dicts": "", "corpus_tag_dicts": ""}
            )
            continue
        exps: dict[str, list[str]] = {}
        for lg in row.get("legends", []):
            exps.setdefault(lg["expansion"], [])
            if lg["dict"] not in exps[lg["expansion"]]:
                exps[lg["expansion"]].append(lg["dict"])
        tag_dicts = ",".join(sorted(row.get("tags", {}).keys()))
        census_senses = payload["polysemy"].get(label, {}).get("nExpansions", 0)
        for expansion, dicts in exps.items():
            rows.append(
                {"section": section, "label": label, "in_census": True,
                 "distinct_expansions": census_senses, "expansion": expansion,
                 "legend_dicts": ";".join(sorted(dicts)), "corpus_tag_dicts": tag_dicts}
            )
    return rows


def _md_escape(s: str) -> str:
    return s.replace("|", "\\|")


def render_guide(payload: dict, rows) -> str:
    n_strings = payload["denominators"]["distinctLabelsInTable"]
    polysemy = payload["polysemy"]
    legend_carrying = len(polysemy)
    polysemous = sum(1 for v in polysemy.values() if v["nExpansions"] >= 2)
    generated_at = payload["generatedAt"]
    by_label: dict[str, list[dict]] = {}
    for r in rows:
        by_label.setdefault(r["label"], []).append(r)

    out = []
    out.append("# A72 pedagogy — как читать словарные пометы (m./f./n./mfn., P./A./U., c., V./N./M./S.: вычисленный путеводитель)")
    out.append("")
    out.append("_Created: 13-10-2026 · Last updated: 13-10-2026_")
    out.append("")
    out.append(f"Сгенерировано [`scripts/build_abbrev_label_guide.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_abbrev_label_guide.py) "
               f"(handoff [H6465](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6465-OxAlpha_csl-atlas_a72-label-reading-student-guide_11.10.26.md)) "
               f"из ценза грамматических сокращений [data/abbrev/abbrev_census.json](../data/abbrev/abbrev_census.json) "
               f"(H6409, снапшот от {generated_at}). **Каждая строка — это вычисленная строка ценза, а не пересказ по памяти**: "
               "расшифровка приводится дословно из слоя легенд, а помета, которой нет в цензе, помечается «нет в цензе» "
               "и не толкуется. Машинный двойник таблицы — [data/abbrev/label_guide_rows.tsv](../data/abbrev/label_guide_rows.tsv).")
    out.append("")
    out.append("## Зачем это студенту")
    out.append("")
    out.append(f"В цифровизированном каноне CSDL {n_strings} разных сокращений; у {legend_carrying} из них есть расшифровка в слоях легенд, "
               f"и **{polysemous} из них многозначны** (≥2 разных расшифровок в разных словарях — вычислено, не по памяти). "
               "Одна и та же помета в Мономье (MW) и в Апте (AP90) может означать разное: ниже — как читать её не гадая.")
    out.append("")
    out.append("## Правило чтения (3 шага)")
    out.append("")
    out.append("1. **Определи словарь.** Помета живёт внутри конкретного словаря: сначала посмотри, чья статья перед тобой (MW, PWG, AP90…), потом читай пометы этого словаря.")
    out.append("2. **Не угадывай по букве.** У одних и тех же строк ниже — от 1 до 12 разных расшифровок (столбец «смыслов» посчитан по легендам ценза).")
    out.append("3. **Если пометы нет в таблице — считай, что ты её не знаешь.** Мы не пересказываем по памяти: «нет в цензе» значит «не вычислено».")
    out.append("")

    for section_key, section_title, section_intro in SECTIONS:
        out.append(f"## {section_title}")
        out.append("")
        out.append(section_intro)
        out.append("")
        sec_rows = [r for r in rows if r["section"] == section_key]
        labels = list(dict.fromkeys(r["label"] for r in sec_rows))
        for label in labels:
            lab_rows = by_label[label]
            heading = next(h for s, l, h in GUIDE_LABELS if s == section_key and l == label)
            if not lab_rows[0]["in_census"]:
                out.append(f"### `{label}` — {heading}")
                out.append("")
                out.append(f"**Нет в цензе.** В `labelTable` ценза (H6409, снапшот {generated_at}) строки `{label}` нет: "
                           "расшифровка не вычислена, и мы её не толкуем. Для `inj.` это подтверждено независимо: реестр малых классов E3 "
                           "(csl-standards v1.5.0, §2) держит форму декларативно-неразрешённой — attested-легенды в каноне нет.")
                out.append("")
                continue
            distinct = payload["polysemy"][label]["nExpansions"]
            raw_rows = len(lab_rows)
            tagd = lab_rows[0]["corpus_tag_dicts"]
            out.append(f"### `{label}` — {heading}")
            out.append("")
            out.append(f"Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **{distinct}**; "
                       f"строк легенд дословно: {raw_rows}. Встречается в статьях словарей: {tagd}.")
            out.append("")
            out.append("| Строка легенды (дословно) | Словари легенды |")
            out.append("|---|---|")
            for r in lab_rows:
                out.append(f"| `{_md_escape(r['expansion'])}` | {r['legend_dicts'].replace(';', ', ')} |")
            out.append("")

    out.append("## Если помету прочитал неверно — скажите об этом (обратная связь)")
    out.append("")
    out.append("Гид — это тест на удобство регистра: **какие пометы студенты читают неверно — это сигнал**, который "
               "возвращается в реестр малых классов E3 (csl-standards v1.5.0). Одна строка обратной связи — одна ошибка чтения, "
               "схема поля: [data/schema/label-misread-feedback.schema.json](../data/schema/label-misread-feedback.schema.json). "
               "Правила: анонимный псевдоним пула (`pool-aNN`, никаких имён и контактов), дата в UTC без времени, "
               "поле `note` проходит ту же зачистку контактов, что и экспорт пула (§4.5 дизайн-документа пула), "
               "сырые строки живут в gitignored `review/` и в репозиторий не попадают; в репозиторий попадает только "
               "агрегат. Маршрут: строка → `review/` → агрегат → примечание в реестр E3 "
               "([SMALL_CLASS_ABBREV_REGISTER_NOTE](https://github.com/gasyoun/csl-standards/blob/main/docs/SMALL_CLASS_ABBREV_REGISTER_NOTE.md)).")
    out.append("")
    out.append("## Откуда взяты все числа (происхождение чисел)")
    out.append("")
    out.append("| Число в гиде | Строка ценза |")
    out.append("|---|---|")
    out.append(f"| Всего сокращений в таблице: {n_strings} | `denominators.distinctLabelsInTable` |")
    out.append(f"| Строк с легендой: {legend_carrying} | `len(polysemy)` |")
    out.append(f"| Многозначных: {polysemous} | `polysemy[*].nExpansions >= 2` (casefold-сравнение ценза) |")
    out.append(f"| Число смыслов у пометы (например, у `c.` — 4) | `polysemy[\"<label>\"].nExpansions` |")
    out.append("| Расшифровки дословно | `labelTable[\"<label>\"].legends[*].expansion` + `.dict` |")
    out.append(f"| Словари, где помета встречается в статьях | `labelTable[\"<label>\"].tags` |")
    out.append("")
    out.append("Снапшот ценза: " + generated_at + " (H6409). Регенерация: "
               "`npm run build-abbrev-label-guide`; проверка байт-идентичности: `npm run build-abbrev-label-guide -- --check`.")
    out.append("")
    return "\n".join(out) + "\n"


def render_tsv(rows) -> str:
    lines = ["\t".join(TSV_HEADER)]
    for r in rows:
        lines.append("\t".join(
            str(r[k]).replace("\t", " ").replace("\n", " ") for k in TSV_HEADER
        ))
    return "\n".join(lines) + "\n"


def write_outputs(payload: dict, dest_guide: Path, dest_tsv: Path) -> None:
    rows = label_rows(payload)
    dest_guide.write_text(render_guide(payload, rows), encoding="utf-8")
    dest_tsv.write_text(render_tsv(rows), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate into a temp dir and byte-compare with committed outputs; exit 1 on drift")
    args = ap.parse_args(argv)

    payload = load_payload()
    if args.check:
        ok = True
        with tempfile.TemporaryDirectory() as td:
            tmp_guide = Path(td) / GUIDE_OUT.name
            tmp_tsv = Path(td) / TSV_OUT.name
            write_outputs(payload, tmp_guide, tmp_tsv)
            for committed, regenerated in ((GUIDE_OUT, tmp_guide), (TSV_OUT, tmp_tsv)):
                if not committed.exists():
                    print(f"DRIFT: committed {committed} missing")
                    ok = False
                elif committed.read_bytes() != regenerated.read_bytes():
                    print(f"DRIFT: {committed} does not match regeneration (payload or template changed)")
                    ok = False
        print("CHECK PASS" if ok else "CHECK FAIL")
        return 0 if ok else 1

    write_outputs(payload, GUIDE_OUT, TSV_OUT)
    print(f"wrote {GUIDE_OUT} and {TSV_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
