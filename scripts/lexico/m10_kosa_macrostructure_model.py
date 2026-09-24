"""M10 — the kośa macrostructure model (H5328): the versified synonymic dictionary
as a macrostructural type.

M6 (m6_kosha_macrostructure.py) *measured* the koshas' kāṇḍa/verse/synonym-set
hierarchy. This script turns that into a *model*: every kośa is emitted as an
instance of one schema (data/schema/kosa-macrostructure.schema.json) whose levels
are the ordering devices of the genre —

    kāṇḍa → varga → (upavarga) → verse-group → set (synonym-set | homonym-sense |
    indeclinable-set | unsegmented-verse) → member (form + parsed gender tag)

— plus an `orderingDevices` table that labels each device OBSERVED (stated in the
source text, or encoded in the digitization markup) or INFERRED (our measurement).

Three instances are built, one per digitization shape of the genre:

  AMAR  Amarakośa, sanskrit-kosha/kosha format (sibling repo ../AMAR/amar.txt):
        grouped, kāṇḍa+varga headers, <eid> synsets with gender tags, a nānārtha
        (homonym) and an avyaya (indeclinable) varga.     ← the validation target
  ABCH  Hemacandra, same format in csl-orig; kāṇḍa-level plus a tiryak upavarga tier.
  ARMH  Halāyudha, csl-orig "exploded" format (one synonym = one <L>, grouped by <vn>);
        synset boundaries and gender are NOT encoded.

Samples keep every kāṇḍa/varga with its full counts but only a few verse-groups
per selected varga (the schema-validation fixtures). Whole-text measurements go to
kosa_model_measures.json: verse-numbering integrity, set sizes, the gender-tag
vocabulary, gender-run contiguity against its exact permutation baseline, the
nānārtha final-consonant (a tergo) order, and alphabetical adjacency against MW.

Stdlib only. Run from the repo root:
    python scripts/lexico/m10_kosa_macrostructure_model.py
"""
import math
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict, defaultdict
import json

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GH = os.path.abspath(os.path.join(ROOT, ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
from dataset_meta import license_fields, generated_at_for_payload, read_json_if_exists  # noqa: E402
from dharmamitra_infer import slp1_to_iast  # noqa: E402

AMAR_REPO = os.path.join(GH, "AMAR")
CSL_REPO = os.path.join(GH, "csl-orig")
SOURCES = {
    "AMAR": {"repo": AMAR_REPO, "path": "amar.txt", "upstream": "sanskrit-kosha/kosha (mirrored as ../AMAR)",
             "licence": "GPL-3.0", "title": "Nāmaliṅgānuśāsana (Amarakośa)", "author": "Amarasiṃha",
             "tradition": "Buddhist (attr.)", "date": "~6th c. (trad.)"},
    "ABCH": {"repo": CSL_REPO, "path": "v02/abch/abch.txt", "upstream": "sanskrit-lexicon/csl-orig",
             "licence": "CC-BY-SA-4.0", "title": "Abhidhānacintāmaṇi", "author": "Hemacandra",
             "tradition": "Jain", "date": "~12th c."},
    "ARMH": {"repo": CSL_REPO, "path": "v02/armh/armh.txt", "upstream": "sanskrit-lexicon/csl-orig",
             "licence": "CC-BY-SA-4.0", "title": "Abhidhānaratnamālā", "author": "Halāyudha",
             "tradition": "Brahmanical", "date": "~10th c."},
}
MW_PATH = os.path.join(CSL_REPO, "v02", "mw", "mw.txt")
OUT_DIR = os.path.join(ROOT, "data", "lexico")

# Which verse-groups each sample keeps: (varga-or-kāṇḍa label SLP1, how many groups).
SAMPLE_PLAN = {
    "AMAR": [("svargavargaH", 12), ("manuzyavargaH", 6), ("viSezyaniGnavargaH", 4),
             ("nAnArTavargaH", 10), ("avyayavargaH", 8)],
    "ABCH": [("devADidevakARqaH", 4), ("tiryakkARqaH", 6), ("avyayavargaH", 4)],
    "ARMH": [("1", 6), ("5", 4)],
}

# Sanskrit (varṇa) collation of SLP1: vowels, anusvāra/visarga, then the vargas.
VARNA = "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh"
RANK = {c: i for i, c in enumerate(VARNA)}
VOWELS = set("aAiIuUfFxXeEoO")
CONSONANTS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh")
# Letter equivalences the tradition allows in ordering: l counts as ḍ (SLP1 q), v as b.
EQUIV = {"l": "q", "v": "b"}
EQUIV_NAME = {"l": "ḍ=l", "q": "ḍ=l", "v": "b=v", "b": "b=v", "B": "b=v"}

L_RE = re.compile(r"^<L>([^<]+)")
KVVV_RE = re.compile(r'<info kvvv="([^"]+)"')
S_TAG = re.compile(r"<s>(.*?)</s>")
EID_RE = re.compile(r"^<eid>(\d+)<syns>(?:<s>)?(.*?)(?:</s>)?\s*$")
VERSE_LINE_RE = re.compile(r"^<s>(.*)</s>\s*$")
FULL_VERSE_RE = re.compile(r"\.\.\s*(\d+)\s*\.\.")
HALF_VERSE_RE = re.compile(r"\((\d+)\)")
VN_RE = re.compile(r"<vn>([0-9.]+)")
K1_RE = re.compile(r"<k1>([^<]*)")
TAG_TOKEN_RE = re.compile(r"puM|strI|klI|tri|dvi|ba|vA|a")
OPEN_COLOPHON_RE = re.compile(r"^;c\{<s>aTa \S*vargaH")
CLOSE_COLOPHON_RE = re.compile(r"^;c\{<s>iti \S*vargaH")
VARGA_HEAD_RE = re.compile(r"^;v\{<s>(\S*vargaH)</s>\}")


# ---------------------------------------------------------------- helpers

def git_rev(repo):
    try:
        out = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True,
                             text=True, encoding="utf-8", check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def iast(s):
    return slp1_to_iast(s) if s else s


def section_type(label):
    lab = (label or "")
    if "nAnArTa" in lab or "anekArTa" in lab:
        return "homonymic"
    if "avyaya" in lab:
        return "indeclinable"
    return "synonymic"


def parse_tag(raw):
    """Hemacandra/Amara liṅga tag -> structured gender. Unknown residue is kept."""
    if raw is None:
        return None
    toks, pos, residue = [], 0, ""
    while pos < len(raw):
        m = TAG_TOKEN_RE.match(raw, pos)
        if not m:
            residue = raw[pos:]
            break
        toks.append(m.group(0))
        pos = m.end()
    genders = []
    for t, g in (("puM", "m"), ("strI", "f"), ("klI", "n")):
        if t in toks:
            genders.append(g)
    tri = "tri" in toks
    if tri:
        genders = ["m", "f", "n"]
    number = "du" if "dvi" in toks else ("pl" if "ba" in toks else None)
    return OrderedDict([
        ("tag", raw),
        ("genders", genders),
        ("indeclinable", "a" in toks and not genders),
        ("triLinga", tri),
        ("optional", "vA" in toks),
        ("number", number),
        ("parsed", residue == ""),
    ])


def split_member(tok):
    tok = tok.strip()
    if "-" in tok:
        form, tag = tok.rsplit("-", 1)
        if re.fullmatch(r"(?:puM|strI|klI|tri|dvi|ba|vA|a)+", tag):
            return form, tag
    return tok, None


def collate_key(word):
    return [RANK.get(c, len(VARNA)) for c in word if c in RANK]


def final_consonant(word):
    for c in reversed(word):
        if c in CONSONANTS:
            return c
    return None


def syllables(word):
    return sum(1 for c in word if c in VOWELS)


def nondecreasing_share(keys):
    pairs = [(a, b) for a, b in zip(keys, keys[1:]) if a is not None and b is not None]
    if not pairs:
        return None
    return round(sum(1 for a, b in pairs if a <= b) / len(pairs), 4)


def runs(keys):
    return 1 + sum(1 for a, b in zip(keys, keys[1:]) if a != b) if keys else 0


# ---------------------------------------------------------------- grouped parser (AMAR, ABCH)

def parse_grouped(lines, code):
    """Yield the grouped-format kośa as divisions -> groups, preserving source line numbers."""
    groups = []
    cur = None
    for i, ln in enumerate(lines, start=1):
        m = L_RE.match(ln)
        if m:
            cur = {"L": m.group(1).strip(), "line": i, "path": None, "sets": [], "verseLines": []}
            groups.append(cur)
            continue
        if cur is None:
            continue
        if ln.startswith("<LEND>"):
            cur = None
            continue
        mk = KVVV_RE.search(ln)
        if mk:
            cur["path"] = [p.strip().rstrip(",").strip() for p in S_TAG.findall(mk.group(1))]
            continue
        me = EID_RE.match(ln)
        if me:
            body = me.group(2).replace("</s>", "").replace("<s>", "")
            members = []
            for tok in body.split(","):
                if not tok.strip():
                    continue
                form, tag = split_member(tok)
                members.append((form, tag))
            cur["sets"].append({"eid": int(me.group(1)), "members": members})
            continue
        mv = VERSE_LINE_RE.match(ln)
        if mv:
            cur["verseLines"].append(mv.group(1))
    return groups


def division_of(group, code):
    """(kanda_label, varga_label, upavarga_label) from the kvvv path."""
    path = group["path"] or []
    if code == "AMAR":
        return (path[0] if path else None, path[1] if len(path) > 1 else None, None)
    # ABCH: first part is the kāṇḍa (or the free-standing avyayavarga); deeper parts are
    # a varga and an upavarga tier (tiryakkāṇḍa only).
    return (path[0] if path else None, path[1] if len(path) > 1 else None,
            path[2] if len(path) > 2 else None)


def build_set(raw_set, sect):
    tagged = [m for m in raw_set["members"] if m[1] is not None]
    members = []
    if sect == "homonymic":
        kind = "homonym-sense"
    elif sect == "indeclinable":
        kind = "indeclinable-set"
    else:
        kind = "synonym-set"
    for idx, (form, tag) in enumerate(raw_set["members"]):
        if kind == "homonym-sense":
            role = "headword" if idx == 0 else "gloss"
        elif tag is None and tagged:
            role = "gloss"
        else:
            role = "synonym"
        members.append(OrderedDict([
            ("form", form), ("formIast", iast(form)), ("role", role), ("gender", parse_tag(tag)),
        ]))
    return OrderedDict([("eid", raw_set["eid"]), ("kind", kind), ("members", members)])


def verse_refs(verse_lines):
    refs = []
    for vl in verse_lines:
        for m in FULL_VERSE_RE.finditer(vl):
            refs.append({"n": int(m.group(1)), "half": False})
        for m in HALF_VERSE_RE.finditer(vl):
            refs.append({"n": int(m.group(1)), "half": True})
    return refs


def model_grouped(code, lines):
    groups = parse_grouped(lines, code)
    kandas = OrderedDict()
    for g in groups:
        k, v, u = division_of(g, code)
        kd = kandas.setdefault(k, OrderedDict())
        kd.setdefault(v, []).append((u, g))
    return kandas


# ---------------------------------------------------------------- exploded parser (ARMH)

def model_exploded(lines):
    by_vn = OrderedDict()
    cur = None
    for i, ln in enumerate(lines, start=1):
        m = L_RE.match(ln)
        if m:
            mvn, mk = VN_RE.search(ln), K1_RE.search(ln)
            if not mvn:
                cur = None
                continue
            vn = mvn.group(1)
            g = by_vn.get(vn)
            if g is None:
                g = {"L": m.group(1).strip(), "line": i, "vn": vn, "k1": [], "verseLines": [], "Ls": []}
                by_vn[vn] = g
            g["k1"].append(mk.group(1) if mk else "")
            g["Ls"].append(m.group(1).strip())
            cur = g
            continue
        if cur is None:
            continue
        if ln.startswith("<LEND>"):
            cur = None
        # records of one locator repeat its verse block (kāṇḍas 1–4) or carry the half-line
        # their word stands in (kāṇḍa 5): keep the ordered union of distinct verse lines
        elif ln.strip() and ln.strip() != cur["vn"] and not ln.rstrip().endswith(";") \
                and ln.strip() not in cur["verseLines"]:
            cur["verseLines"].append(ln.strip())
    kandas = OrderedDict()
    for vn, g in by_vn.items():
        kandas.setdefault(vn.split(".")[0], []).append(g)
    return kandas


# ---------------------------------------------------------------- instance builders

def src_block(code):
    s = SOURCES[code]
    return OrderedDict([
        ("upstream", s["upstream"]), ("path", s["path"]), ("revision", git_rev(s["repo"])),
        ("licence", s["licence"]),
    ])


def device(name, evidence, layer, level, note):
    return OrderedDict([("device", name), ("evidence", evidence), ("layer", layer),
                        ("level", level), ("note", note)])


def grouped_instance(code, kandas, measures):
    plan = dict(SAMPLE_PLAN[code])
    out_kandas = []
    for kn, (klabel, vargas) in enumerate(kandas.items(), start=1):
        out_vargas = []
        for vn, (vlabel, members) in enumerate(vargas.items(), start=1):
            unit_label = vlabel if vlabel is not None else klabel
            sect = section_type(unit_label)
            keep = plan.get(vlabel if code == "AMAR" else klabel, 0)
            if code == "ABCH" and klabel == "tiryakkARqaH" and vn > 1:
                keep = 0          # sample only the first tiryak varga
            n_sets = sum(len(g["sets"]) for _, g in members)
            n_members = sum(len(s["members"]) for _, g in members for s in g["sets"])
            full_verses = sorted({r["n"] for _, g in members for r in verse_refs(g["verseLines"]) if not r["half"]})
            groups_out = []
            for upa, g in members[:keep]:
                groups_out.append(OrderedDict([
                    ("L", g["L"]), ("sourceLine", g["line"]),
                    ("upavarga", upa), ("upavargaIast", iast(upa)),
                    ("verseRefs", verse_refs(g["verseLines"])),
                    ("verseLines", g["verseLines"]),
                    ("sets", [build_set(s, sect) for s in g["sets"]]),
                ]))
            out_vargas.append(OrderedDict([
                ("n", vn), ("label", vlabel), ("labelIast", iast(vlabel)),
                ("labelStatus", "stated-in-text" if vlabel else "not-divided-in-source"),
                ("sectionType", sect), ("sectionTypeBasis", "section-label"),
                ("counts", OrderedDict([("groups", len(members)), ("sets", n_sets), ("members", n_members),
                                        ("fullVerses", len(full_verses))])),
                ("groups", groups_out),
            ]))
        out_kandas.append(OrderedDict([
            ("n", kn), ("label", klabel), ("labelIast", iast(klabel)),
            ("labelStatus", "stated-in-text" if klabel else "absent"), ("vargas", out_vargas),
        ]))
    return out_kandas


def exploded_instance(kandas):
    plan = dict(SAMPLE_PLAN["ARMH"])
    out = []
    for kn, (klabel, groups) in enumerate(kandas.items(), start=1):
        sect = "homonymic" if klabel == "5" else "synonymic"
        keep = plan.get(klabel, 0)
        groups_out = []
        for g in groups[:keep]:
            vr = [{"n": int(m.group(1)), "half": False} for vl in g["verseLines"]
                  for m in FULL_VERSE_RE.finditer(vl)]
            groups_out.append(OrderedDict([
                ("L", g["L"]), ("sourceLine", g["line"]), ("upavarga", None), ("upavargaIast", None),
                ("locator", g["vn"]), ("verseRefs", vr), ("verseLines", g["verseLines"]),
                ("sets", [OrderedDict([
                    ("eid", None), ("kind", "unsegmented-verse"),
                    ("members", [OrderedDict([("form", k), ("formIast", iast(k)), ("role", "synonym"),
                                              ("gender", None)]) for k in g["k1"]]),
                ])]),
            ]))
        out.append(OrderedDict([
            ("n", kn), ("label", None), ("labelIast", None), ("labelStatus", "numeric-locator-only"),
            ("vargas", [OrderedDict([
                ("n", 1), ("label", None), ("labelIast", None), ("labelStatus", "not-divided-in-source"),
                ("sectionType", sect),
                ("sectionTypeBasis", "content" if sect == "homonymic" else "default"),
                ("counts", OrderedDict([("groups", len(groups)), ("sets", len(groups)),
                                        ("members", sum(len(g["k1"]) for g in groups)),
                                        ("fullVerses", len({int(m.group(1)) for g in groups
                                                            for vl in g["verseLines"]
                                                            for m in FULL_VERSE_RE.finditer(vl)}))])),
                ("groups", groups_out),
            ])]),
        ]))
    return out


# ---------------------------------------------------------------- measurements

def gender_class(m):
    g = m["gender"]
    if g is None:
        return None
    if g["indeclinable"]:
        return "avy"
    if g["triLinga"]:
        return "tri"
    return "".join(g["genders"]) or "?"


def contiguity(sets):
    """Share of multi-gender synonym-sets whose gender classes each form ONE run,
    against the exact permutation baseline P = k!·Πc_i! / n! per set."""
    observed, expected, n_sets, masc_first, masc_share = 0, 0.0, 0, 0, 0.0
    for s in sets:
        seq = [gender_class(m) for m in s["members"] if m["role"] == "synonym"]
        seq = [c for c in seq if c is not None]
        counts = Counter(seq)
        if len(counts) < 2:
            continue
        n_sets += 1
        k, n = len(counts), len(seq)
        p = math.factorial(k) * math.prod(math.factorial(c) for c in counts.values()) / math.factorial(n)
        expected += p
        run_count = runs(seq)
        if run_count == k:
            observed += 1
        if seq[0] == "m":
            masc_first += 1
        masc_share += counts.get("m", 0) / n
    if not n_sets:
        return None
    return OrderedDict([
        ("multiGenderSets", n_sets),
        ("contiguousObserved", round(observed / n_sets, 4)),
        ("contiguousExpectedUnderPermutation", round(expected / n_sets, 4)),
        ("mascFirstObserved", round(masc_first / n_sets, 4)),
        ("mascFirstExpected", round(masc_share / n_sets, 4)),
    ])


def all_sets(kandas_full, code):
    """Every set in the whole text, with its section type (built un-sampled)."""
    out = []
    for klabel, vargas in kandas_full.items():
        for vlabel, members in vargas.items():
            sect = section_type(vlabel if vlabel is not None else klabel)
            for _, g in members:
                for s in g["sets"]:
                    out.append((sect, vlabel or klabel, build_set(s, sect)))
    return out


def verse_integrity(kandas_full):
    """Full-verse numbers per section: they should run in steps of one (restarting or not)."""
    rows = []
    for klabel, vargas in kandas_full.items():
        for vlabel, members in vargas.items():
            nums = [r["n"] for _, g in members for r in verse_refs(g["verseLines"]) if not r["half"]]
            if not nums:
                continue
            steps = list(zip(nums, nums[1:]))
            rows.append(OrderedDict([
                ("varga", vlabel or klabel), ("vargaIast", iast(vlabel or klabel)),
                ("first", nums[0]), ("last", nums[-1]), ("fullVerses", len(nums)),
                ("stepsOfOne", sum(1 for a, b in steps if b == a + 1)),
                ("otherSteps", [[a, b] for a, b in steps if b != a + 1][:5]),
            ]))
    return rows


def numbering_scope(rows):
    """Does the verse count restart at a section boundary, or run on through the work?"""
    boundaries = list(zip(rows, rows[1:]))
    restarts = sum(1 for a, b in boundaries if b["first"] <= a["last"])
    return OrderedDict([("sectionBoundaries", len(boundaries)), ("restarts", restarts),
                        ("scope", "per-section" if restarts > len(boundaries) / 2 else "continuous")])


def colophons(lines):
    """Section headings (;v) against opening 'atha … vargaḥ' and closing 'iti … vargaḥ' colophons."""
    heads = [m.group(1) for ln in lines for m in [VARGA_HEAD_RE.match(ln)] if m]
    opening = {ln.split()[1].rstrip(".<") for ln in lines if OPEN_COLOPHON_RE.match(ln)}
    closing = {ln.split()[1].rstrip(".<") for ln in lines if CLOSE_COLOPHON_RE.match(ln)}
    opening = {re.sub(r"<.*$", "", o) for o in opening}
    closing = {re.sub(r"<.*$", "", c) for c in closing}
    return OrderedDict([
        ("sections", len(heads)),
        ("withOpeningAtha", sum(1 for h in heads if h in opening)),
        ("withClosingIti", sum(1 for h in heads if h in closing)),
        ("withoutOpening", [iast(h) for h in heads if h not in opening]),
        ("withoutClosing", [iast(h) for h in heads if h not in closing]),
    ])


def nanartha_order(sets):
    heads = [s["members"][0]["form"] for sect, _, s in sets if sect == "homonymic"]
    # collapse consecutive senses of one headword to the headword sequence
    seq = [h for i, h in enumerate(heads) if i == 0 or heads[i - 1] != h]
    finals = [RANK.get(final_consonant(h)) for h in seq]          # None = vowel-only headword
    initials = [RANK.get(h[0], len(VARNA)) if h else len(VARNA) for h in seq]
    fc_runs = []
    for h in seq:
        fc = final_consonant(h)
        if fc_runs and fc_runs[-1][0] == fc:
            fc_runs[-1][1] += 1
        else:
            fc_runs.append([fc, 1])
    # syllable order inside each final-consonant block
    syl_nd, syl_pairs, i = 0, 0, 0
    for fc, n in fc_runs:
        block = [syllables(h) for h in seq[i:i + n]]
        syl_pairs += max(0, len(block) - 1)
        syl_nd += sum(1 for a, b in zip(block, block[1:]) if a <= b)
        i += n
    # Series: a drop of more than half the alphabet restarts the a-tergo cycle. Each
    # descending step inside a series is checked against the traditional letter
    # equivalences ḍ = l (ḍalayor abhedaḥ) and b = v (bavayor abhedaḥ).
    tags = {}
    for sect, _, s in sets:
        if sect == "homonymic":
            g = s["members"][0]["gender"]
            tags.setdefault(s["members"][0]["form"], g["tag"] if g else None)
    series, violations, start, last = [], [], 0, finals[0] if finals else None
    for i in range(1, len(seq) + 1):
        restart = (i < len(seq) and finals[i] is not None and last is not None
                   and finals[i] < last - len(VARNA) // 2)
        if i < len(seq) and finals[i] is not None:
            last = finals[i]
        if i == len(seq) or restart:
            block = seq[start:i]
            tag_counts = Counter(tags.get(h) for h in block)
            series.append(OrderedDict([
                ("startIast", iast(block[0])), ("headwords", len(block)),
                ("indeclinableShare", round(tag_counts.get("a", 0) / len(block), 4)),
                ("finalConsonantNondecreasing", nondecreasing_share(finals[start:i])),
            ]))
            for a, b in zip(block, block[1:]):
                fa, fb = final_consonant(a), final_consonant(b)
                if fa is not None and fb is not None and RANK[fb] < RANK[fa]:
                    ea, eb = EQUIV.get(fa, fa), EQUIV.get(fb, fb)
                    explained = RANK.get(eb, len(VARNA)) >= RANK.get(ea, len(VARNA))
                    violations.append(OrderedDict([
                        ("series", len(series)), ("from", a), ("fromIast", iast(a)), ("to", b), ("toIast", iast(b)),
                        ("explainedBy", EQUIV_NAME.get(fa if fa in EQUIV else fb) if explained else None),
                    ]))
            start = i
    return OrderedDict([
        ("headwords", len(seq)), ("senses", len(heads)),
        ("series", series), ("violations", violations),
        ("finalConsonantNondecreasing", nondecreasing_share(finals)),
        ("initialLetterNondecreasing", nondecreasing_share(initials)),
        ("finalConsonantBlocks", len(fc_runs)),
        ("distinctFinalConsonants", len({fc for fc, _ in fc_runs})),
        ("blockSequence", [OrderedDict([("final", fc), ("finalIast", iast(fc)), ("headwords", n)])
                           for fc, n in fc_runs][:60]),
        ("syllableNondecreasingWithinBlocks", round(syl_nd / syl_pairs, 4) if syl_pairs else None),
    ])


def alpha_adjacency(forms):
    keys = [collate_key(f) for f in forms if f]
    return OrderedDict([("pairs", max(0, len(keys) - 1)), ("nondecreasing", nondecreasing_share(keys))])


def mw_forms():
    forms = []
    if not os.path.exists(MW_PATH):
        return forms
    with open(MW_PATH, encoding="utf-8") as fh:
        for ln in fh:
            if ln.startswith("<L>"):
                m = K1_RE.search(ln)
                if m:
                    forms.append(m.group(1))
    return forms


def measure(code, kandas_full=None, exploded=None, lines=None):
    res = OrderedDict()
    if exploded is not None:
        forms = [k for groups in exploded.values() for g in groups for k in g["k1"]]
        res["digitizationModel"] = "exploded"
        res["alphabeticalAdjacency"] = alpha_adjacency(forms)
        res["genderMarking"] = "absent-in-markup"
        return res
    sets = all_sets(kandas_full, code)
    res["digitizationModel"] = "grouped"
    res["verseNumbering"] = verse_integrity(kandas_full)
    res["verseNumberingScope"] = numbering_scope(res["verseNumbering"])
    in_groups = sum(r["fullVerses"] for r in res["verseNumbering"])
    in_file = sum(len(FULL_VERSE_RE.findall(ln)) for ln in lines) if lines else None
    res["fullVerseCount"] = OrderedDict([("inVerseGroups", in_groups), ("inFile", in_file)])
    if lines and code == "AMAR":
        res["sectionColophons"] = colophons(lines)
    size = defaultdict(list)
    for sect, _, s in sets:
        size[s["kind"]].append(len([m for m in s["members"] if m["role"] != "gloss"]))
    res["setSizes"] = OrderedDict(
        (k, OrderedDict([("sets", len(v)), ("mean", round(sum(v) / len(v), 2)), ("max", max(v)),
                         ("singletons", sum(1 for x in v if x == 1))]))
        for k, v in sorted(size.items()))
    tags = Counter(m["gender"]["tag"] for _, _, s in sets for m in s["members"] if m["gender"])
    unparsed = sorted({m["gender"]["tag"] for _, _, s in sets for m in s["members"]
                       if m["gender"] and not m["gender"]["parsed"]})
    untagged = Counter(m["role"] for _, _, s in sets for m in s["members"] if not m["gender"])
    res["genderTags"] = OrderedDict([("distinctTags", len(tags)), ("top", dict(tags.most_common(12))),
                                     ("unparsed", unparsed), ("untaggedByRole", dict(untagged))])
    res["genderContiguity"] = contiguity([s for sect, _, s in sets if sect == "synonymic"])
    if any(sect == "homonymic" for sect, _, _ in sets):
        res["nanarthaOrder"] = nanartha_order(sets)
    forms = [m["form"] for sect, _, s in sets if sect == "synonymic" for m in s["members"]
             if m["role"] == "synonym"]
    res["alphabeticalAdjacency"] = alpha_adjacency(forms)
    return res


# ---------------------------------------------------------------- devices (observed vs inferred)

def devices_for(code, meas):
    if code == "ARMH":
        return [
            device("kanda", "observed", "digitization-markup", "division",
                   "Only as the first field of the <vn> locator; no kāṇḍa headings in the digitization."),
            device("varga", "absent", "digitization-markup", "division",
                   "The <vn> locator does not vary below the kāṇḍa (A06 §6)."),
            device("verse", "observed", "source-text", "group",
                   "Verse-end numbers in the text; the <vn> groups the exploded records."),
            device("synonym-set", "absent", "digitization-markup", "set",
                   "Exploded model: one record per synonym, set boundaries inside a verse not encoded."),
            device("homonym-section", "inferred", "measurement", "division",
                   "kāṇḍa 5 identified as anekārtha from its '…api…' formula (A06 §4.2), not from a heading."),
            device("gender-marking", "absent", "digitization-markup", "member", "No liṅga tags in the digitization."),
            device("alphabetical-order", "inferred", "measurement", "member",
                   f"Adjacent-headword non-decreasing share {meas['alphabeticalAdjacency']['nondecreasing']} — chance level."),
        ]
    col = meas.get("sectionColophons")
    if col:
        varga_note = (f"Section headings name all {col['sections']} vargas; {col['withOpeningAtha']} open with "
                      f"atha … vargaḥ and {col['withClosingIti']} close with iti … vargaḥ (no opening colophon: "
                      f"{', '.join(col['withoutOpening'])}; no closing one: {', '.join(col['withoutClosing'])}).")
    else:
        varga_note = ("ABCH is divided by kāṇḍa; varga-level labels occur only in the tiryak-kāṇḍa "
                      "and the avyaya-varga.")
    scope = meas["verseNumberingScope"]
    verse_note = ("Verse-end numbers '.. N ..' (half-verse '(N)'); "
                  + (f"numbering restarts at {scope['restarts']} of {scope['sectionBoundaries']} section boundaries."
                     if scope["scope"] == "per-section" else
                     f"numbering runs on continuously across all {scope['sectionBoundaries']} section boundaries."))
    if code == "AMAR":
        avyaya_note = ("avyaya-varga is the last varga in this digitization; kāṇḍa 3 v. 1 names a "
                       "liṅgādisaṅgraha-varga after it, which the digitization does not contain.")
    else:
        avyaya_note = "avyaya-varga is the last section of the digitization, a top-level division after the sāmānya-kāṇḍa."
    devs = [
        device("kanda", "observed", "source-text", "division",
               "Book headings/colophons are part of the text (e.g. prathamaṃ kāṇḍam)."),
        device("varga", "observed", "source-text", "division", varga_note),
        device("upavarga", "absent" if code == "AMAR" else "observed", "digitization-markup", "division",
               "No third kvvv tier in AMAR (every record carries kāṇḍa + varga only)."
               if code == "AMAR" else "tiryak-kāṇḍa carries a third kvvv tier (e.g. pañcendriya → sthalacara)."),
        device("verse", "observed", "source-text", "group", verse_note),
        device("synonym-set", "observed", "digitization-markup", "set",
               "<eid> segmentation of a verse into sets is editorial annotation, not marked in the verse itself."),
        device("gender-marking", "observed", "digitization-markup", "member",
               "Per-lexeme liṅga tags are annotator-supplied; the text marks gender by form, association and explicit statement"
               + (" (paribhāṣā vv. 3–5)." if code == "AMAR" else ".")),
    ]
    gc = meas.get("genderContiguity")
    if gc:
        devs.append(device("gender-contiguity", "inferred", "measurement", "member",
                           f"{gc['contiguousObserved']} of multi-gender sets keep each gender in one run "
                           f"vs {gc['contiguousExpectedUnderPermutation']} expected by chance."))
    if "nanarthaOrder" in meas:
        no = meas["nanarthaOrder"]
        devs.append(device("homonym-section", "observed", "source-text", "division",
                           "nānārtha-varga; its opening verse states the arrangement by final sound (kāntādi)."))
        explained = sum(1 for v in no["violations"] if v["explainedBy"])
        devs.append(device("final-sound-order", "inferred", "measurement", "member",
                           "The kāntādi verse states the principle; measured here is how strictly it holds. "
                           f"Final-consonant rank non-decreasing on {no['finalConsonantNondecreasing']} of adjacent "
                           f"headwords vs {no['initialLetterNondecreasing']} for the initial letter; "
                           f"{len(no['series'])} a-tergo series (the second almost wholly indeclinable); "
                           f"{explained} of {len(no['violations'])} descending steps fall under the ḍ=l / b=v equivalences."))
    devs.append(device("indeclinable-section", "observed", "source-text", "division", avyaya_note))
    devs.append(device("alphabetical-order", "inferred", "measurement", "member",
                       f"Adjacent-headword non-decreasing share {meas['alphabeticalAdjacency']['nondecreasing']} "
                       "in synonymic sections — chance level, i.e. no alphabetical device."))
    return devs


# ---------------------------------------------------------------- main

def write(path, payload):
    prev = read_json_if_exists(path)
    payload["generatedAt"] = None
    payload["generatedAt"] = generated_at_for_payload(prev, payload)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("wrote", os.path.relpath(path, ROOT))


def read_lines(code):
    s = SOURCES[code]
    with open(os.path.join(s["repo"], s["path"]), encoding="utf-8") as fh:
        return fh.read().split("\n")


def envelope(code, model, kandas, devices, meas):
    s = SOURCES[code]
    env = OrderedDict()
    env["schemaVersion"] = "1.0"
    env["schema"] = "data/schema/kosa-macrostructure.schema.json"
    env["generatedBy"] = "scripts/lexico/m10_kosa_macrostructure_model.py"
    env["generatedAt"] = None
    env.update(license_fields())
    env["kosha"] = OrderedDict([
        ("code", code), ("title", s["title"]), ("author", s["author"]), ("tradition", s["tradition"]),
        ("date", s["date"]), ("source", src_block(code)),
    ])
    env["macrostructureType"] = "onomasiological-versified"
    env["digitizationModel"] = model
    env["genderMarking"] = model == "grouped"
    env["sample"] = OrderedDict([
        ("isSample", True),
        ("plan", [OrderedDict([("unit", u), ("unitIast", iast(u) if not u.isdigit() else u), ("groups", n)])
                  for u, n in SAMPLE_PLAN[code]]),
        ("note", "Every division is listed with its full-text counts; only the planned verse-groups are expanded."),
    ])
    env["orderingDevices"] = devices
    env["kandas"] = kandas
    return env


def main():
    measures = OrderedDict()
    instances = {}
    for code in ("AMAR", "ABCH"):
        lines = read_lines(code)
        full = model_grouped(code, lines)
        meas = measure(code, kandas_full=full, lines=lines)
        measures[code] = meas
        instances[code] = envelope(code, "grouped", grouped_instance(code, full, meas), devices_for(code, meas), meas)
    lines = read_lines("ARMH")
    exp = model_exploded(lines)
    meas = measure("ARMH", exploded=exp)
    measures["ARMH"] = meas
    instances["ARMH"] = envelope("ARMH", "exploded", exploded_instance(exp), devices_for("ARMH", meas), meas)
    measures["MW"] = OrderedDict([("digitizationModel", "alphabetical-entry"),
                                  ("alphabeticalAdjacency", alpha_adjacency(mw_forms()))])

    for code, inst in instances.items():
        write(os.path.join(OUT_DIR, f"kosa_model_{code.lower()}_sample.json"), inst)

    payload = OrderedDict()
    payload["schemaVersion"] = "1.0"
    payload["generatedBy"] = "scripts/lexico/m10_kosa_macrostructure_model.py"
    payload["generatedAt"] = None
    payload.update(license_fields())
    payload["sources"] = OrderedDict((c, src_block(c)) for c in SOURCES)
    payload["sources"]["MW"] = OrderedDict([("upstream", "sanskrit-lexicon/csl-orig"), ("path", "v02/mw/mw.txt"),
                                            ("revision", git_rev(CSL_REPO)), ("licence", "CC-BY-SA-4.0")])
    payload["collation"] = "SLP1 varṇa order: " + VARNA
    payload["devices"] = OrderedDict((c, instances[c]["orderingDevices"]) for c in instances)
    payload["measures"] = measures
    write(os.path.join(OUT_DIR, "kosa_model_measures.json"), payload)
    summary = {c: {k: v for k, v in m.items() if k in ("genderContiguity", "alphabeticalAdjacency", "setSizes")}
               for c, m in measures.items()}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if "nanarthaOrder" in measures["AMAR"]:
        no = dict(measures["AMAR"]["nanarthaOrder"])
        no.pop("blockSequence", None)
        print(json.dumps(no, ensure_ascii=False))


if __name__ == "__main__":
    main()
