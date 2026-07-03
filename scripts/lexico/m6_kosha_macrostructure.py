"""M6 — macrostructure of the versified synonymic kośa (ARMH/ABCH/ACPH/ACSJ).

The macrostructural counterpart to m4 (which recovered indigenous *micro*structure).
The four CDSL koshas are onomasiological (concept-ordered) verse texts, not
alphabetical dictionaries: their structure is the kāṇḍa→varga→verse→synonym-set
hierarchy, and they carry ZERO European block apparatus (no <lex>/<ls>/<div>; see
MICROSTRUCTURE_ZERO_MEANING.md). This script measures that macrostructure from the
csl-orig sources, and — the headline finding — shows the two digitization models
(ARMH explodes one-synonym-per-record; ABCH groups one-concept-per-record) put the
same genre at incommensurable record granularities.

Two source formats:
  ARMH  — "exploded": each synonym is its own <L> record carrying <vn>K.V.S.verse;
          the synonym-set is reconstructed by grouping records on <vn>.
  ABCH/ACPH/ACSJ — "grouped": ;k{...kARqaH} kāṇḍa headers; one <L> record holds a
          whole concept-group in <syns>/<eid> fields with per-lexeme gender tags
          (-puM/-strI/-na/-avy). Each record is tagged <info kvvv="...kARqaH"/>.

Stdlib only; UTF-8, no BOM. Output: data/lexico/kosha_macrostructure.json (envelope).
Run:  python scripts/lexico/m6_kosha_macrostructure.py
"""
import sys, os, re, json, statistics
from collections import Counter, defaultdict, OrderedDict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GH = os.path.abspath(os.path.join(ROOT, ".."))            # GitHub/ parent
CSL = os.path.join(GH, "csl-orig", "v02")
OUT = os.path.join(ROOT, "data", "lexico", "kosha_macrostructure.json")

KOSHAS = ["armh", "abch", "acph", "acsj"]

L_RE = re.compile(r"^<L>")
VN_RE = re.compile(r"<vn>([0-9.]+)")
K1_RE = re.compile(r"<k1>([^<]*)")
KHEAD_RE = re.compile(r"^;k\{<s>([^<}]+)</s>\}")
EID_RE = re.compile(r"<eid>")
# Hemacandra's liṅga apparatus: a lexeme tag is -<morph> before , or < ; the gender
# component is one or more of puM (masc.), strI (fem.), klI (klība = neut.), possibly
# combined (puMklI = "masc. and neut."), with number tags (dvi/ba) appended.
MORPHTAG_RE = re.compile(r"-([A-Za-z]+)(?=[,<])")
KVVV_RE = re.compile(r'<info kvvv="<s>([^<"]+)</s>"')
S_RE = re.compile(r"<s>([^<]*)</s>")          # a <syns> synonym-form string (may be a comma list)
POS_RE = re.compile(r"-[A-Za-z]+$")            # trailing gender/number tag on a form


def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().split("\n")


def measure_exploded(lines):
    """ARMH-style: one synonym per <L>, grouped by <vn>."""
    records = 0
    by_vn = defaultdict(list)          # vn -> [headwords]
    kanda_records = Counter()
    first_of_kanda = OrderedDict()     # kanda -> (vn, first headword)
    for ln in lines:
        if not L_RE.match(ln):
            continue
        records += 1
        mvn = VN_RE.search(ln)
        mk1 = K1_RE.search(ln)
        hw = mk1.group(1) if mk1 else ""
        if not mvn:
            continue
        vn = mvn.group(1)
        kanda = vn.split(".")[0]
        by_vn[vn].append(hw)
        kanda_records[kanda] += 1
        if kanda not in first_of_kanda:
            first_of_kanda[kanda] = (vn, hw)
    set_sizes = [len(v) for v in by_vn.values()]
    # Per-kāṇḍa set-size: kāṇḍas 1–4 are synonymic (true synonym-sets); kāṇḍa 5 is
    # the anekārtha (homonym) section, where the "api" formula pairs a word with an
    # ADDED meaning — so its records are word+gloss pairs, not synonyms. Reporting the
    # synonym density separately keeps the flat <vn> digitization from over-counting.
    vn_by_kanda = defaultdict(list)
    for vn, hw in by_vn.items():
        vn_by_kanda[vn.split(".")[0]].append(len(hw))
    per_kanda_setsize = {
        k: {"verses": len(v), "mean_set": round(statistics.mean(v), 2)}
        for k, v in sorted(vn_by_kanda.items())
    }
    synonymic = [n for k, v in vn_by_kanda.items() if k != "5" for n in v]
    return {
        "model": "exploded (one synonym = one record)",
        "records": records,
        "verses": len(by_vn),
        "kandas": len(kanda_records),
        "synonyms_per_verse_mean_all": round(statistics.mean(set_sizes), 2),
        "synonyms_per_verse_mean_synonymic_k1to4": round(statistics.mean(synonymic), 2),
        "per_kanda_setsize": per_kanda_setsize,
        "synonyms_per_verse_median": statistics.median(set_sizes),
        "synonyms_per_verse_max": max(set_sizes),
        "largest_verses": [
            {"vn": vn, "n": len(hw), "headwords": hw[:6]}
            for vn, hw in sorted(by_vn.items(), key=lambda kv: -len(kv[1]))[:5]
        ],
        "kanda_records": dict(sorted(kanda_records.items())),
        "kanda_first_headword": {k: {"vn": v[0], "k1": v[1]} for k, v in first_of_kanda.items()},
    }


def measure_grouped(lines):
    """ABCH-style: one concept-group per <L>; <syns>/<eid>; ;k{} kāṇḍa headers."""
    records = 0
    eids = 0
    morphtags = Counter()              # raw -<morph> tokens
    gender = Counter()                 # masc/fem/neut by substring membership
    kanda_headers = []                 # order of ;k{} headers
    kanda_records = Counter()          # <L> records attributed to running ;k{} header
    cur_kanda = None
    form_total = 0                     # comma-split <s> members (the SYNONYM-FORM unit)
    form_distinct = set()              # distinct POS-stripped forms
    for ln in lines:
        mkh = KHEAD_RE.match(ln)
        if mkh:
            cur_kanda = mkh.group(1)
            if cur_kanda not in kanda_headers:
                kanda_headers.append(cur_kanda)
        if L_RE.match(ln):
            records += 1
            if cur_kanda is not None:
                kanda_records[cur_kanda] += 1
        eids += len(EID_RE.findall(ln))
        for syn in S_RE.findall(ln):
            for member in syn.split(","):
                lex = POS_RE.sub("", member.strip())
                if lex:
                    form_total += 1
                    form_distinct.add(lex)
        for t in MORPHTAG_RE.findall(ln):
            if "puM" in t or "strI" in t or "klI" in t:
                morphtags[t] += 1
                if "puM" in t:
                    gender["masculine"] += 1
                if "strI" in t:
                    gender["feminine"] += 1
                if "klI" in t:
                    gender["neuter"] += 1
    return {
        "model": "grouped (one concept-group = one record, internal <syns>/<eid>)",
        "records": records,
        # THREE distinct size granularities — do not conflate (see assumptions):
        "lexeme_eids": eids,                       # <eid> concept-slots (Table-3 "lexemes")
        "synonym_forms_total": form_total,         # comma-split <s> members (the unit gender tags ride on)
        "synonym_forms_distinct": len(form_distinct),
        "kandas": len(kanda_headers),
        "kanda_order": kanda_headers,
        "gendered_lexeme_tags": int(sum(morphtags.values())),  # per synonym-FORM, not per eid
        "gender_admissions": dict(gender),     # a combined tag counts toward each gender it admits
        "top_morphtags": dict(morphtags.most_common(8)),
        "records_per_kanda": dict(kanda_records),
    }


def main():
    result = OrderedDict()
    for code in KOSHAS:
        path = os.path.join(CSL, code, code + ".txt")
        if not os.path.exists(path):
            result[code] = {"error": "source not found", "path": path}
            continue
        lines = read_lines(path)
        # Format detection: <vn> on L-lines ⟹ exploded; else grouped.
        has_vn = any(L_RE.match(ln) and VN_RE.search(ln) for ln in lines[:200])
        result[code] = measure_exploded(lines) if has_vn else measure_grouped(lines)

    payload = OrderedDict()
    payload["schemaVersion"] = "1.0"
    payload["generatedBy"] = "scripts/lexico/m6_kosha_macrostructure.py"
    payload["sourcePath"] = "csl-orig/v02/<kosha>/<kosha>.txt"
    payload["assumptions"] = [
        "ARMH <vn> = kāṇḍa.section.subsection.verse; the synonym-set is the group of records sharing one <vn>.",
        "ABCH/ACPH/ACSJ kāṇḍa membership is read from ;k{} headers and <info kvvv=> tags; lexemes counted as <eid>.",
        "Gender tokens counted as -puM/-strI/-na/-avy suffixes in the <syns> field (Hemacandra's liṅga apparatus).",
        "Record counts are NOT cross-comparable: the two digitization models grain the same genre differently.",
        "THREE grouped-kosha granularities are reported separately and MUST NOT be conflated as 'lexeme': "
        "records (<L> concept-groups) < lexeme_eids (<eid> concept-slots) < synonym_forms_total "
        "(comma-split <s> members). Gender tags ride on synonym-forms, so gendered_lexeme_tags is per-form, "
        "not per-eid. The OBS-R redundancy census (headword_multiplicity.csv) counts the first <s> per line "
        "comma-split, a fourth slice again — e.g. ABCH is 1,965 records / 4,619 eids / 14,735 distinct forms "
        "(19,511 total) / 11,584 OBS-R keys; cite the unit explicitly in any kosha size claim.",
    ]
    payload["koshas"] = result
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("wrote", os.path.relpath(OUT, ROOT))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
