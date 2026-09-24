"""Pins for M11 — access-structures census (H5331, 24-09-2026).

Hand derivations (base order a ā i ī u ū ṛ ṝ ḷ ḹ e ai o au ṃ ḥ k kh g gh ṅ … m y r l v ś ṣ s h):

* anusvāra: `saMkara` → `pos` keeps M; `nasal`/`nasal_m` → `saNkara` (k's class nasal ṅ);
  `m` → `samkara`. `saMyama` → `nasal` keeps M (y has no class nasal), `nasal_m` → m.
  `saMmata` → `nasal` gives `sammata` (m's class nasal is m itself).
* visarga: `niHsAra` internal `sib` → `nissAra`; `duHKa` `sib` keeps ḥ (kh is no sibilant),
  `s` → `dusKa`. Final `kaviH`: `slot` keeps, `s` → `kavis`, `drop` → `kavi`.
* gemination: `karRRa` `degem` → `karRa`; `vardDa` (r+d+dh) → `varDa`; `sarva` unchanged.
* lnds([1, 3, 2, 4]) = 3 (1, 2, 4), the 3 is off the path.
* restarts: `ba bb bc | aa ab ac` — initial b→a drops and max(after)=`ac` < min(before)=`ba`
  → restart at index 2. `ba bb bc | aa bd be` fails (be > ba); `bx by bz | ba bb bc` fails
  (the initial letter does not drop).

Fixture dictionary (`wil`, 19 records): segment 1 = a, aṃkura, [alias āta], aka, ka¹, ka²,
kaṭhā, kara, kala, kā, kāka, kila, kuśa, kha, gha (sorted under M-pos: ṃ < k); segment 2
(a supplement) = aja, ita, āta, ucca.
  - records 19, alias 1, print 18, units 17 (ka¹ ka² collapse).
  - gha → aja is a restart (a < gh; the last 10 of segment 1 all start with k/kh/gh, all of
    segment 2's 4 units sort below them) → 2 segments.
  - within-segment descents under M-pos: only ita → āta (1 of 17−1−1 = 15 pairs = 0.066667);
    segment 2's LNDS is 3 of 4 → displaced 1 / 17 = 0.058824.
  - M-nasal turns aṃkura into aṅkura, which sorts after aka → 2 descents, so M-pos wins; no ḥ
    and no r+geminate, so all 3×3×2 = 18 M-pos rules tie and grid order picks
    M-pos/Hi-pos/Hf-slot/G-keep. Every contrast has < 30 pairs → all four factors undetermined.
  - `all` view keeps the alias āta between aṃkura and aka → one more descent (2).
  - homonyms: ka h1, h2 — 1 group, contiguous, numbered, ascending, gapless.
"""

import json
import pathlib
import sys
from collections import OrderedDict

LEXICO = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "lexico"
if str(LEXICO) not in sys.path:
    sys.path.insert(0, str(LEXICO))

import m11_access_structures as m11  # noqa: E402

S = "m11_access_structures"


def test_anusvara_policies(pin):
    pin(S, "apply_m(saMkara,pos)", "saMkara", m11.apply_m("saMkara", "pos"))
    pin(S, "apply_m(saMkara,nasal)", "saNkara", m11.apply_m("saMkara", "nasal"))
    pin(S, "apply_m(saMkara,nasal_m)", "saNkara", m11.apply_m("saMkara", "nasal_m"))
    pin(S, "apply_m(saMkara,m)", "samkara", m11.apply_m("saMkara", "m"))
    pin(S, "apply_m(saMyama,nasal)", "saMyama", m11.apply_m("saMyama", "nasal"))
    pin(S, "apply_m(saMyama,nasal_m)", "samyama", m11.apply_m("saMyama", "nasal_m"))
    pin(S, "apply_m(saMmata,nasal)", "sammata", m11.apply_m("saMmata", "nasal"))


def test_visarga_policies(pin):
    pin(S, "apply_h(niHsAra,sib)", "nissAra", m11.apply_h("niHsAra", "sib", "slot"))
    pin(S, "apply_h(niHsAra,pos)", "niHsAra", m11.apply_h("niHsAra", "pos", "slot"))
    pin(S, "apply_h(duHKa,sib)", "duHKa", m11.apply_h("duHKa", "sib", "slot"))
    pin(S, "apply_h(duHKa,s)", "dusKa", m11.apply_h("duHKa", "s", "slot"))
    pin(S, "apply_h(kaviH,final slot)", "kaviH", m11.apply_h("kaviH", "pos", "slot"))
    pin(S, "apply_h(kaviH,final s)", "kavis", m11.apply_h("kaviH", "pos", "s"))
    pin(S, "apply_h(kaviH,final drop)", "kavi", m11.apply_h("kaviH", "pos", "drop"))


def test_gemination_after_r(pin):
    pin(S, "apply_g(karRRa,degem)", "karRa", m11.apply_g("karRRa", "degem"))
    pin(S, "apply_g(vardDa,degem)", "varDa", m11.apply_g("vardDa", "degem"))
    pin(S, "apply_g(sarva,degem)", "sarva", m11.apply_g("sarva", "degem"))
    pin(S, "apply_g(karRRa,keep)", "karRRa", m11.apply_g("karRRa", "keep"))


def test_lnds_and_restarts(pin):
    length, on = m11.lnds([1, 3, 2, 4])
    pin(S, "lnds length", 3, length)
    pin(S, "lnds path", [True, False, True, True], on)
    for keys, expected in ((["ba", "bb", "bc", "aa", "ab", "ac"], [2]),
                           (["ba", "bb", "bc", "aa", "bd", "be"], []),
                           (["bx", "by", "bz", "ba", "bb", "bc"], [])):
        pin(S, f"restarts {' '.join(keys)}", expected, m11.restarts(keys, m11.descents(keys)))


def test_factor_status_and_profile(pin):
    block = {"pairwise": [
        {"contrast": "pos|nasal", "verdict": "clear", "winner": "pos", "disagreeing_pairs": 40},
        {"contrast": "pos|m", "verdict": "undetermined", "winner": None, "disagreeing_pairs": 5},
        {"contrast": "nasal|m", "verdict": "clear", "winner": "nasal", "disagreeing_pairs": 50},
    ]}
    st = m11.factor_status(block, "pos")
    pin(S, "factor_status status", "partial", st["status"])
    pin(S, "factor_status rejects", ["nasal"], list(st["rejects"]))
    pin(S, "factor_status indistinguishable", ["m"], st["indistinguishable_from"])
    us = [{"k1": k} for k in ("agrataH", "agra", "kara", "kAla", "tapas", "Ga")]
    prof = m11.descent_profile(us, [0, 2, 4])
    # pair agrataH/agra: common prefix 4 = len(agra) → ending_variant; kara/kAla: prefix 1
    # → prefix_0_1; tapas/Ga: prefix 0 → prefix_0_1. (The bins only read the prefix length.)
    pin(S, "descent_profile", {"ending_variant": 1, "prefix_4plus": 0, "prefix_2_3": 0, "prefix_0_1": 2},
        dict(prof))


def test_heads_filter(pin):
    recs = [{"L": "1", "k1": "gam", "root": True}, {"L": "2", "k1": "gamana", "root": False},
            {"L": "2.1", "k1": "gamya", "root": False}, {"L": "3", "k1": "gaja", "root": False}]
    kept, st = m11.heads_filter(recs)
    pin(S, "heads_filter kept", ["gam", "gaja"], [r["k1"] for r in kept])
    pin(S, "heads_filter stats", {"roots": 1, "paragraph_runons_dropped": 1,
                                  "root_nest_derivatives_dropped": 1}, st)


FIXTURE = [
    ("1", "001", "a", ""), ("2", "001", "aMkura", ""), ("2.1", "001", "Ata", "alias"),
    ("3", "001", "aka", ""), ("4", "002", "ka", "1"), ("5", "002", "ka", "2"),
    ("6", "002", "kaWA", ""), ("7", "002", "kara", ""), ("8", "003", "kala", ""),
    ("9", "003", "kA", ""), ("10", "003", "kAka", ""), ("11", "003", "kila", ""),
    ("12", "004", "kuSa", ""), ("13", "004", "Ka", ""), ("14", "004", "Ga", ""),
    ("15", "101", "aja", ""), ("16", "101", "ita", ""), ("17", "101", "Ata", ""),
    ("18", "102", "ucca", ""),
]


def _write_fixture(tmp_path):
    csl = tmp_path / "v02"
    (csl / "wil").mkdir(parents=True)
    lines = []
    for L, pc, k1, h in FIXTURE:
        head = f"<L>{L}<pc>{pc}<k1>{k1}<k2>{k1}"
        if h.isdigit():
            head += f"<h>{h}"
        lines += [head, "{{Lbody=17}}" if h == "alias" else f"¦ entry {k1}", "<LEND>"]
    (csl / "wil" / "wil.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csl


def test_fixture_run(pin, tmp_path):
    csl = _write_fixture(tmp_path)
    out = tmp_path / "out"
    m11.main(["--dicts", "wil", "--csl", str(csl), "--out-dir", str(out)])
    d = json.loads((out / "access_structures.json").read_text(encoding="utf-8"))["dicts"][0]
    b = d["best_fit"]
    pin(S, "records", 19, d["records"])
    pin(S, "alias_records", 1, d["alias_records"])
    pin(S, "print_records", 18, d["print_records"])
    pin(S, "primary_units", 17, d["primary_units"])
    pin(S, "best rule", "M-pos/Hi-pos/Hf-slot/G-keep", b["rule"])
    pin(S, "tied rules", 18, len(b["tied_rules"]))
    pin(S, "segments", 2, b["segments"])
    pin(S, "descents", 1, b["descents"])
    pin(S, "descent_rate", 0.066667, b["descent_rate"])
    pin(S, "displaced_rate", 0.058824, b["displaced_rate"])
    pin(S, "M-nasal descents", 2, d["rates"]["main"]["M-nasal/Hi-pos/Hf-slot/G-keep"]["descents"])
    pin(S, "all-view descents", 2, d["rates"]["all"][b["rule"]]["descents"])
    pin(S, "factor statuses", ["undetermined"] * 4, [v["status"] for v in d["factor_status"].values()])
    h = d["homonyms"]
    pin(S, "homonym groups/contiguous/asc/gapless", (1, 1, 1, 1),
        (h["groups"], h["contiguous"], h["h_ascending"], h["h_gapless_from_1"]))
    cex = (out / "access_structures_counterexamples.csv").read_text(encoding="utf-8").splitlines()
    pin(S, "counterexample rows", 1, len(cex) - 1)
    row = cex[1].split(",")
    pin(S, "counterexample pair (iast)", ("ita", "āta"), (row[9], row[13]))
    pin(S, "counterexample kind", "isolated", row[3])
