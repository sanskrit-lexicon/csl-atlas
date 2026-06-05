"""H4 / M8 — Amarakośa-native semantic fields.

Builds a dictionary-first semantic-field coverage layer without using corpus
frequency or external passage data. The field taxonomy comes directly from the
local sibling AMAR repo:

    ../AMAR/amar.txt

Each Amarakośa synonym is assigned to its kāṇḍa/varga/upavarga context, then
matched against local csl-orig <k1> headword sets. The output answers:

    Which dictionaries cover which Amarakośa semantic fields?

Run from repo root:
    python scripts/lexico/m8_semantic_fields.py
"""

import collections
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import CSL_ORIG, iter_entries

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT_DIR = "data/lexico"
AMAR_PATH = os.path.abspath(os.path.join("..", "AMAR", "amar.txt"))
GENDER_CODES = {
    "puM", "strI", "klI", "tri", "a",
    "puMklI", "puMstrI", "strIklI", "strIpuM", "klIpuM",
    "puMdvi", "strIdvi", "klIdvi", "puMba", "strIba", "klIa",
}
ACCENTS = re.compile(r"[/\\^~]")
TRAILING_HOM = re.compile(r"\d+$")
S_TAG = re.compile(r"<s>(.*?)</s>")
L_RE = re.compile(r"^<L>([^<]+)")
INFO_RE = re.compile(r'<info\s+kvvv="([^"]+)"')
SYNS_RE = re.compile(r"<eid>([^<]+)<syns><s>(.*?)</s>")


def normalize(k1):
    return TRAILING_HOM.sub("", ACCENTS.sub("", (k1 or "").strip())).strip()


def clean_label(s):
    return " ".join((s or "").replace(",", " ").split()).strip()


def parse_kvvv(line):
    m = INFO_RE.search(line)
    if not m:
        return "", "", ""
    parts = [clean_label(p) for p in S_TAG.findall(m.group(1))]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]


def parse_synonym(token):
    raw = token.strip()
    if not raw:
        return "", "", ""
    lemma, gender = raw, ""
    if "-" in raw:
        head, tail = raw.rsplit("-", 1)
        if tail in GENDER_CODES:
            lemma, gender = head, tail
    norm = normalize(lemma)
    return lemma, norm, gender


def parse_amar():
    if not os.path.exists(AMAR_PATH):
        raise SystemExit(f"Missing AMAR source: {AMAR_PATH}")

    current_l = ""
    current_kanda = current_varga = current_upavarga = ""
    fields = collections.OrderedDict()
    lemma_fields = collections.OrderedDict()

    with open(AMAR_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            lm = L_RE.match(line)
            if lm:
                current_l = lm.group(1)
                continue
            if line.startswith("<info "):
                current_kanda, current_varga, current_upavarga = parse_kvvv(line)
                continue
            sm = SYNS_RE.search(line)
            if not sm:
                continue
            eid, payload = sm.group(1), sm.group(2)
            field_key = "|".join([current_kanda, current_varga, current_upavarga])
            field = fields.setdefault(field_key, {
                "field_key": field_key,
                "kanda": current_kanda,
                "varga": current_varga,
                "upavarga": current_upavarga,
                "field_order": len(fields) + 1,
                "amar_entries": set(),
                "lemmas": collections.OrderedDict(),
            })
            field["amar_entries"].add(current_l)
            syns = [s for s in (p.strip() for p in payload.split(",")) if s]
            for raw in syns:
                lemma_raw, lemma_norm, gender = parse_synonym(raw)
                if not lemma_norm:
                    continue
                rec_key = (lemma_norm, field_key)
                rec = lemma_fields.setdefault(rec_key, {
                    "lemma": lemma_norm,
                    "raw_forms": collections.OrderedDict(),
                    "genders": set(),
                    "field_key": field_key,
                    "kanda": current_kanda,
                    "varga": current_varga,
                    "upavarga": current_upavarga,
                    "first_amar_L": current_l,
                    "first_eid": eid,
                    "occurrences": 0,
                })
                rec["raw_forms"].setdefault(lemma_raw, None)
                if gender:
                    rec["genders"].add(gender)
                rec["occurrences"] += 1
                field["lemmas"].setdefault(lemma_norm, None)

    rows = []
    for rec in lemma_fields.values():
        rows.append({
            "lemma": rec["lemma"],
            "raw_forms": "|".join(rec["raw_forms"].keys()),
            "genders": "|".join(sorted(rec["genders"])),
            "field_key": rec["field_key"],
            "kanda": rec["kanda"],
            "varga": rec["varga"],
            "upavarga": rec["upavarga"],
            "first_amar_L": rec["first_amar_L"],
            "first_eid": rec["first_eid"],
            "occurrences": rec["occurrences"],
        })
    return fields, rows


def discover_dicts():
    return sorted(os.path.basename(os.path.dirname(p))
                  for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                  if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))


def load_headword_sets(codes):
    out = {}
    records = {}
    for code in codes:
        path = os.path.join(CSL_ORIG, code, f"{code}.txt")
        if not os.path.exists(path):
            continue
        lemmas = set()
        n = 0
        for e in iter_entries(path):
            n += 1
            k = normalize(e.get("k1", ""))
            if k:
                lemmas.add(k)
        out[code] = lemmas
        records[code] = n
    return out, records


def pct(n, d):
    return round(n / d, 4) if d else 0.0


def build_coverage(fields, headwords):
    rows = []
    by_dict = {code: {"covered": set(), "field_rows": []} for code in headwords}
    for field in fields.values():
        lemmas = list(field["lemmas"].keys())
        lemma_set = set(lemmas)
        denom = len(lemma_set)
        for code, hws in headwords.items():
            covered = [l for l in lemmas if l in hws]
            missing = [l for l in lemmas if l not in hws]
            row = {
                "dict": code,
                "field_key": field["field_key"],
                "field_order": field["field_order"],
                "kanda": field["kanda"],
                "varga": field["varga"],
                "upavarga": field["upavarga"],
                "amar_lemmas": denom,
                "covered_lemmas": len(covered),
                "coverage_pct": f"{pct(len(covered), denom):.4f}",
                "covered_examples": "|".join(covered[:8]),
                "missing_examples": "|".join(missing[:8]),
            }
            rows.append(row)
            by_dict[code]["covered"].update(covered)
            by_dict[code]["field_rows"].append(row)
    return rows, by_dict


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    fields, lemma_rows = parse_amar()
    codes = discover_dicts()
    headwords, records = load_headword_sets(codes)
    coverage_rows, by_dict = build_coverage(fields, headwords)

    semantic_path = os.path.join(OUT_DIR, "semantic_fields.csv")
    coverage_path = os.path.join(OUT_DIR, "semantic_field_coverage.csv")
    report_path = os.path.join(OUT_DIR, "semantic_field_report.json")

    write_csv(semantic_path, lemma_rows, [
        "lemma", "raw_forms", "genders", "field_key", "kanda", "varga", "upavarga",
        "first_amar_L", "first_eid", "occurrences",
    ])
    write_csv(coverage_path, coverage_rows, [
        "dict", "field_key", "field_order", "kanda", "varga", "upavarga",
        "amar_lemmas", "covered_lemmas", "coverage_pct", "covered_examples",
        "missing_examples",
    ])

    total_lemmas = len({r["lemma"] for r in lemma_rows})
    field_summary = []
    for field in fields.values():
        field_summary.append({
            "field_key": field["field_key"],
            "field_order": field["field_order"],
            "kanda": field["kanda"],
            "varga": field["varga"],
            "upavarga": field["upavarga"],
            "amar_entries": len(field["amar_entries"]),
            "amar_lemmas": len(field["lemmas"]),
        })

    dict_summary = {}
    for code, blk in by_dict.items():
        ranked = sorted(blk["field_rows"],
                        key=lambda r: (-float(r["coverage_pct"]), -int(r["covered_lemmas"]), r["field_order"]))
        dict_summary[code] = {
            "records": records.get(code, 0),
            "distinct_headwords": len(headwords.get(code, set())),
            "covered_amar_lemmas": len(blk["covered"]),
            "coverage_pct": pct(len(blk["covered"]), total_lemmas),
            "top_fields": [
                {
                    "field_key": r["field_key"],
                    "varga": r["varga"],
                    "coverage_pct": float(r["coverage_pct"]),
                    "covered_lemmas": int(r["covered_lemmas"]),
                    "amar_lemmas": int(r["amar_lemmas"]),
                }
                for r in ranked[:8]
            ],
        }

    report = {
        "schema": "h4-semantic-fields-v1",
        "question": "Which dictionaries cover which Amarakośa-native semantic fields?",
        "source": {
            "amar": os.path.relpath(AMAR_PATH, os.getcwd()).replace("\\", "/"),
            "csl_orig": CSL_ORIG,
        },
        "method": ("Parse AMAR <info kvvv> kāṇḍa/varga/upavarga labels and <syns> synonym "
                   "lists, normalize AMAR lemmas and csl-orig <k1> by removing accents and "
                   "trailing homonym digits, then compute dictionary coverage per field."),
        "caveats": ("Dictionary-first headword coverage only. This does not measure corpus "
                    "frequency, passage attestation, sense coverage, or non-headword mentions. "
                    "AMAR is a taxonomy seed, not a claim that every dictionary organises meaning "
                    "by Amarakośa categories."),
        "fields": field_summary,
        "dictionaries": dict_summary,
        "counts": {
            "field_count": len(fields),
            "semantic_field_rows": len(lemma_rows),
            "distinct_amar_lemmas": total_lemmas,
            "coverage_rows": len(coverage_rows),
            "dict_count": len(headwords),
        },
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(semantic_path, "m8_semantic_fields.py", 8)
        write_source(coverage_path, "m8_semantic_fields.py", 8)
    except Exception as e:
        print(f"Provenance error: {e}")

    print("=" * 64)
    print("M8 — Amarakośa-native semantic fields")
    print("=" * 64)
    print(f"  fields: {len(fields):,}")
    print(f"  semantic lemma-field rows: {len(lemma_rows):,}")
    print(f"  distinct AMAR lemmas: {total_lemmas:,}")
    print(f"  dictionary coverage rows: {len(coverage_rows):,} ({len(headwords)} dicts)")
    for code in ("mw", "ap", "pwg", "pw", "wil", "vcp", "skd", "shs", "yat"):
        if code in dict_summary:
            d = dict_summary[code]
            print(f"  {code:5s} AMAR lemmas covered={d['covered_amar_lemmas']:>5,} "
                  f"({d['coverage_pct']:.1%})")
    print(f"Wrote {semantic_path}, {coverage_path}, {report_path}")


if __name__ == "__main__":
    main()
