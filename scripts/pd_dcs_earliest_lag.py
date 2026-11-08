#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H6944 — PD first citation vs DCS earliest dated attestation, per letter-a lemma.

Builds data/pd/pd_dcs_earliest_lag.tsv: one row per PD headword that has (a) a
datable first citation and (b) a datable DCS attestation. Both sides are dated
in the same chronology (the committed Dharmamitra snapshot), so the lag is not
an artefact of mixing two date ladders.

Inputs (external, read-only; pinned by sha256 below):
  * PDScan 2020 pd.txt — 107,630 <L> entries, letter-a volumes.
  * VisualDCS src/DCS-data-2021/0.csv — 246 texts, token-id sentences.
  * VisualDCS src/DCS-data-2021/conllu lookup dictionary.csv — lemma id -> IAST.
Repo inputs:
  * src/data/external/dharmamitra-chronology.json
  * data/pd/pd_siglum_raw.tsv (known PD sigla)
  * data/pd/pd_dcs_text_crosswalk.tsv (DCS title -> PD siglum)
  * data/pd/pd_aob_siglum_title.tsv (PD siglum -> printed title)
  * src/data/review/source-date-anchor-review.json (siglum -> date)

Usage:
  python3 scripts/pd_dcs_earliest_lag.py --inputs /path/to/dir --out-dir data/pd
  python3 scripts/pd_dcs_earliest_lag.py --check

--check re-derives the summary from the committed TSV and compares it with the
committed JSON; it does not need the multi-hundred-MB external inputs.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PINNED = {
    "pd.txt": "4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442",
    "0.csv": "bf0f687ba1bc8272b2bcd709f092c70364709c4b063d178f6fb30529d9291107",
    "dictionary.csv": "95172e5a626ada6322ec67173657b834b7f2bbe1db71250b8b2551c07feb60cd",
}

SLP1 = {
    "ai": "E", "au": "O", "kh": "K", "gh": "G", "ch": "C", "jh": "J",
    "ṭh": "W", "ḍh": "Q", "th": "T", "dh": "D", "ph": "P", "bh": "B",
    "ā": "A", "ī": "I", "ū": "U", "ṛ": "f", "ṝ": "F", "ḷ": "x", "ḹ": "X",
    "ṃ": "M", "ṁ": "M", "ḥ": "H", "ṅ": "N", "ñ": "Y", "ṭ": "w", "ḍ": "q",
    "ṇ": "R", "ś": "S", "ṣ": "z", "ḻ": "L",
    "a": "a", "i": "i", "u": "u", "e": "e", "o": "o", "k": "k", "g": "g",
    "c": "c", "j": "j", "t": "t", "d": "d", "n": "n", "p": "p", "b": "b",
    "m": "m", "y": "y", "r": "r", "l": "l", "v": "v", "s": "s", "h": "h",
}

ALIAS_SIGLUM = {
    "ManuBh.": "Manubhāṣya",
    "BrahmSūBh.": "Brahmasūtra",
    "HarVi.": "Harivaṃśa",
    "BhāṭṭDī.": "Bhāṭṭadīpikā",
    "VīraMi.": "Vīramitrodaya",
    "NyāyMañ.": "Nyāyamañjarī",
    "MīmāKau.": "Mīmāṃsākaustubha",
}

ALIAS_WORK = {
    "Manusmṛti": "Mānava-Dharmaśāstra",
    "Viṣṇusmṛti": "Viṣṇu-Smṛti",
    "Yājñavalkyasmṛti": "Yājñavalkya-Smṛti",
}


def to_slp1(text):
    out, i = [], 0
    while i < len(text):
        two = text[i:i + 2]
        if two in SLP1:
            out.append(SLP1[two])
            i += 2
        else:
            out.append(SLP1.get(text[i], text[i]))
            i += 1
    return "".join(out)


def lemma_key(slp1):
    s = slp1.replace("\\", "").replace("/", "").replace("^", "").replace("~", "")
    return re.sub(r"\d+$", "", s).strip()


def fold(text):
    s = unicodedata.normalize("NFKD", text or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Chronology:
    def __init__(self, path):
        works = json.load(open(path, encoding="utf-8"))["works"]
        self.by_key = defaultdict(list)
        self.all = []
        for work in works:
            key = fold(work["title"])
            self.by_key[key].append(work)
            self.all.append((key, work))

    def lookup(self, title):
        key = fold(ALIAS_WORK.get(title, title))
        if key in self.by_key:
            works = self.by_key[key]
            return (round(statistics.median(w["postMedian"] for w in works), 1),
                    min(works, key=lambda w: w["postMedian"])["title"])
        if len(key) >= 5:
            cand = [(k, w) for k, w in self.all if k.startswith(key)]
            if cand:
                best = min(cand, key=lambda kw: kw[1]["postMedian"])
                return (round(statistics.median(w["postMedian"] for _, w in cand), 1), best[1]["title"])
        return None


def parse_pd_entries(path):
    text = open(path, encoding="utf-8").read()
    header = re.compile(r"<L>(\d+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)")
    re_slp1 = re.compile(r"\{#.*?#\}", re.S)
    re_ital = re.compile(r"\{%.*?%\}", re.S)
    re_tag = re.compile(r"<[^>]*>")
    re_bracket = re.compile(r"\[[^\]]*\]")
    re_siglum = re.compile(r"([^\W\d_][^\W\d_]*)\.(\([^)]*\))?")
    for match in header.finditer(text):
        end = text.find("<LEND>", match.end())
        body = text[match.end():end if end != -1 else match.end() + 4000]
        cleaned = re_bracket.sub(" ", re_tag.sub(" ", re_ital.sub(" ", re_slp1.sub(" ", body))))
        sigla = [m.group(1) + "." for m in re_siglum.finditer(cleaned)]
        yield match.group(1), lemma_key(match.group(3)), sigla


def build(inputs, out_dir, repo):
    pd_txt = os.path.join(inputs, "pd.txt")
    tokens_csv = os.path.join(inputs, "0.csv")
    dictionary_csv = os.path.join(inputs, "dictionary.csv")
    for name, path in (("pd.txt", pd_txt), ("0.csv", tokens_csv), ("dictionary.csv", dictionary_csv)):
        if not os.path.exists(path):
            sys.exit("missing input: %s" % path)
        digest = sha256(path)
        if digest != PINNED[name]:
            sys.exit("input hash mismatch for %s: %s" % (path, digest))

    chronology = Chronology(os.path.join(repo, "src/data/external/dharmamitra-chronology.json"))

    known_sigla = {row["siglum"] for row in csv.DictReader(
        open(os.path.join(repo, "data/pd/pd_siglum_raw.tsv"), encoding="utf-8"), delimiter="\t")}

    crosswalk = defaultdict(list)
    for row in csv.DictReader(open(os.path.join(repo, "data/pd/pd_dcs_text_crosswalk.tsv"),
                                   encoding="utf-8"), delimiter="\t"):
        for siglum in row["pd_sigla"].split("|"):
            crosswalk[siglum.strip()].append(row["dcs_title"])

    printed = defaultdict(list)
    for row in csv.DictReader(open(os.path.join(repo, "data/pd/pd_aob_siglum_title.tsv"),
                                   encoding="utf-8"), delimiter="\t"):
        printed[row["siglum"]].append(row["title"])

    anchored = {}
    for item in json.load(open(os.path.join(repo, "src/data/review/source-date-anchor-review.json"),
                               encoding="utf-8"))["items"]:
        machine = item["machineValue"]
        anchored[machine["siglum"]] = (machine.get("dateMedian"), machine.get("matchedWork"))

    def resolve(siglum):
        if anchored.get(siglum, (None, None))[0] is not None:
            return "source-date-anchor", anchored[siglum][1], anchored[siglum][0]
        if siglum in ALIAS_SIGLUM:
            found = chronology.lookup(ALIAS_SIGLUM[siglum])
            if found:
                return "siglum-alias", found[1], found[0]
        for title in crosswalk.get(siglum, []):
            found = chronology.lookup(title)
            if found:
                return "dcs-crosswalk", found[1], found[0]
        for title in printed.get(siglum, []):
            found = chronology.lookup(title)
            if found:
                return "aob-title", found[1], found[0]
        return None

    entries = 0
    unique = set()
    loss = Counter()
    pd_rows = {}
    for entry_id, key, sigla in parse_pd_entries(pd_txt):
        entries += 1
        if key in unique:
            continue
        unique.add(key)
        candidates = [s for s in sigla if s in known_sigla]
        if not candidates:
            loss["pd_entry_no_known_siglum"] += 1
            continue
        resolved = resolve(candidates[0])
        if not resolved:
            loss["pd_first_siglum_undated"] += 1
            continue
        pd_rows[key] = (entry_id, candidates[0], resolved[0], resolved[1], resolved[2])

    dictionary = {}
    for row in csv.DictReader(open(dictionary_csv, encoding="utf-8"), delimiter="\t"):
        dictionary[row["id"]] = lemma_key(to_slp1(row["word"]))

    dcs_texts = set()
    for line in open(tokens_csv, encoding="utf-8"):
        dcs_texts.add(line.split(";", 1)[0].strip('"'))
    dated_texts = {}
    for title in dcs_texts:
        found = chronology.lookup(title)
        if found:
            dated_texts[title] = found

    wanted = {lemma_key(to_slp1(row["word"])) for row in csv.DictReader(open(dictionary_csv, encoding="utf-8"),
                                                                   delimiter="\t")}
    wanted &= set(pd_rows)
    wanted_ids = {node for node, lemma in dictionary.items() if lemma in wanted}

    earliest = {}
    tokens = 0
    for line in open(tokens_csv, encoding="utf-8"):
        parts = line.rstrip("\n").split(";")
        if len(parts) < 4:
            continue
        title = parts[0].strip('"')
        dated = dated_texts.get(title)
        if not dated:
            continue
        date_estimate, work_title = dated
        ids = parts[3].split(",")
        tokens += len(ids)
        for node in ids:
            lemma = dictionary.get(node)
            if lemma not in wanted:
                continue
            current = earliest.get(lemma)
            if current is None or date_estimate < current[0]:
                earliest[lemma] = (date_estimate, title, work_title)

    dcs_inventory = {lemma_key(to_slp1(row["word"])) for row in csv.DictReader(
        open(dictionary_csv, encoding="utf-8"), delimiter="\t")}
    in_dcs = set(pd_rows) & dcs_inventory
    in_dump = {lemma for lemma in in_dcs if lemma in earliest or lemma in wanted}
    loss["pd_headword_not_in_dcs_inventory"] = len(pd_rows) - len(in_dcs)
    loss["pd_headword_in_dcs_without_datable_attestation"] = len(in_dcs) - len(earliest)

    rows = []
    for lemma in sorted(earliest):
        entry_id, siglum, source, work, pd_date = pd_rows[lemma]
        dcs_date, dcs_title, _ = earliest[lemma]
        rows.append({
            "lemma_slp1": lemma,
            "pd_entry_id": entry_id,
            "pd_first_siglum": siglum,
            "pd_first_work": work,
            "pd_date_estimate": pd_date,
            "pd_date_source": source,
            "dcs_earliest_text": dcs_title,
            "dcs_earliest_date_estimate": dcs_date,
            "lag_years": pd_date - dcs_date,
        })

    lags = sorted(row["lag_years"] for row in rows)
    def quartile_of(values, p):
        if not values:
            return 0
        pos = (len(values) - 1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (pos - lo)
    def quartile(p):
        pos = (len(lags) - 1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        return lags[lo] if lo == hi else lags[lo] + (lags[hi] - lags[lo]) * (pos - lo)

    summary = {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/pd_dcs_earliest_lag.py",
        "handoff": "H6944",
        "inputs": {
            "pd.txt": PINNED["pd.txt"],
            "0.csv": PINNED["0.csv"],
            "dictionary.csv": PINNED["dictionary.csv"],
            "dharmamitra-chronology.json": sha256(
                os.path.join(repo, "src/data/external/dharmamitra-chronology.json")),
        },
        "method": (
            "PD first citation: the first known source siglum in the entry body, resolved to a "
            "Dharmamitra chronology work (source-date-anchor first, then the DCS crosswalk, then "
            "the printed AOB title). DCS earliest: the earliest Dharmamitra-dated DCS text in the "
            "VisualDCS token dump that contains the lemma. Both dates are posterior medians from "
            "the same Dharmamitra model snapshot, not historical dates."
        ),
        "counts": {
            "pd_entries_scanned": entries,
            "pd_unique_headwords": len(unique),
            "pd_headwords_with_dated_first_citation": len(pd_rows),
            "dcs_texts_in_token_dump": len(dcs_texts),
            "dcs_texts_with_dharmamitra_date": len(dated_texts),
            "dcs_tokens_scanned": tokens,
            "joined_lemmas": len(rows),
        },
        "join_loss": dict(sorted(loss.items())),
        "distribution": {
            "n": len(rows),
            "median_years": statistics.median(lags),
            "q1_years": quartile(0.25),
            "q3_years": quartile(0.75),
            "mean_years": round(statistics.mean(lags), 2),
            "min_years": min(lags),
            "max_years": max(lags),
            "share_dcs_earlier": round(sum(1 for x in lags if x > 0) / len(lags), 4),
            "share_tie": round(sum(1 for x in lags if x == 0) / len(lags), 4),
            "share_pd_earlier": round(sum(1 for x in lags if x < 0) / len(lags), 4),
            "share_dcs_earlier_non_tie": round(
                sum(1 for x in lags if x > 0) / max(1, sum(1 for x in lags if x != 0)), 4),
            "non_tie_n": sum(1 for x in lags if x != 0),
            "non_tie_median_years": statistics.median([x for x in lags if x != 0]) if any(x != 0 for x in lags) else 0,
            "non_tie_q1_years": quartile_of([x for x in lags if x != 0], 0.25),
            "non_tie_q3_years": quartile_of([x for x in lags if x != 0], 0.75),
        },
        "pd_date_sources": dict(sorted(Counter(row["pd_date_source"] for row in rows).items())),
        "caveats": [
            "Only 246 of the 271 DCS text directories appear in the VisualDCS token dump.",
            "A DCS text without a Dharmamitra date is skipped; the row therefore records the "
            "earliest DATABLE attestation, which can only push the DCS side later, never earlier.",
            "PD first-citation resolution covers 31,217 of 104,950 unique headwords; the "
            "unresolved majority is dominated by post-classical commentaries and the Padmapurāṇa, "
            "which the Dharmamitra snapshot does not date.",
            "Both dates are model posterior medians; the lag is an offset between two estimates, "
            "not an interval between two historical events.",
        ],
    }

    fieldnames = ["lemma_slp1", "pd_entry_id", "pd_first_siglum", "pd_first_work",
                  "pd_date_estimate", "pd_date_source", "dcs_earliest_text",
                  "dcs_earliest_date_estimate", "lag_years"]
    tsv_path = os.path.join(out_dir, "pd_dcs_earliest_lag.tsv")
    with open(tsv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    json_path = os.path.join(out_dir, "pd_dcs_earliest_lag.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


def check(repo):
    out_dir = os.path.join(repo, "data/pd")
    tsv_path = os.path.join(out_dir, "pd_dcs_earliest_lag.tsv")
    json_path = os.path.join(out_dir, "pd_dcs_earliest_lag.json")
    expected = json.load(open(json_path, encoding="utf-8"))
    rows = list(csv.DictReader(open(tsv_path, encoding="utf-8"), delimiter="\t"))
    lags = sorted(float(row["lag_years"]) for row in rows)
    def quartile_of(values, p):
        if not values:
            return 0
        pos = (len(values) - 1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (pos - lo)
    def quartile(p):
        pos = (len(lags) - 1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        return lags[lo] if lo == hi else lags[lo] + (lags[hi] - lags[lo]) * (pos - lo)
    actual = {
        "n": len(rows),
        "median_years": statistics.median(lags),
        "q1_years": quartile(0.25),
        "q3_years": quartile(0.75),
        "mean_years": round(statistics.mean(lags), 2),
        "min_years": min(lags),
        "max_years": max(lags),
        "share_dcs_earlier": round(sum(1 for x in lags if x > 0) / len(lags), 4),
        "share_tie": round(sum(1 for x in lags if x == 0) / len(lags), 4),
        "share_pd_earlier": round(sum(1 for x in lags if x < 0) / len(lags), 4),
        "share_dcs_earlier_non_tie": round(
            sum(1 for x in lags if x > 0) / max(1, sum(1 for x in lags if x != 0)), 4),
        "non_tie_n": sum(1 for x in lags if x != 0),
        "non_tie_median_years": statistics.median([x for x in lags if x != 0]) if any(x != 0 for x in lags) else 0,
        "non_tie_q1_years": quartile_of([x for x in lags if x != 0], 0.25),
        "non_tie_q3_years": quartile_of([x for x in lags if x != 0], 0.75),
    }
    expected_dist = expected["distribution"]
    ok = all(abs(float(actual[k]) - float(expected_dist[k])) < 1e-6 for k in actual)
    print(json.dumps({"check": "PASS" if ok else "FAIL", "actual": actual,
                      "expected": expected["distribution"]}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", help="directory with pd.txt, 0.csv, dictionary.csv")
    parser.add_argument("--out-dir", default=os.path.join(HERE, "data/pd"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        sys.exit(check(HERE))
    if not args.inputs:
        parser.error("--inputs is required unless --check is used")
    build(args.inputs, args.out_dir, HERE)


if __name__ == "__main__":
    main()
