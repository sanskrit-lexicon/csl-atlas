"""Phase F8d — stage the two rights-gated MBh e-text witnesses locally (H2845).

The MBh presence lane needs TEXT, not just numbering. csl-atlas holds the numbering
(`mbh_vulgate_concordance.csv`, 83,971 verses) but deliberately holds no verse bytes: the
Nilakantha vulgate (sanatana.in, third-party volunteer transcription) and the BORI critical
e-text ((C) BORI 1999, John D. Smith's terms: "please do not provide copies of the text to
others") are both **gitignored, never committed, never published**.

Both witnesses were already harvested by the sibling repo `CommentaryStrategies` and preserved
on its LOCAL-ONLY branch `mahabharata-nilakantha-local-only-do-not-push` (H921 / H784):

  mahabharata-nilakantha/nilakantha_vulgate_full.jsonl   83,971 verses, mula_dev + tika_dev
  mahabharata-nilakantha/bori-critical/MBh{01..18}.txt   ISO-15919 "UR" critical text

This script reads those blobs straight out of that branch's git object store (no checkout, no
re-scrape, no network) and writes the two gitignored caches csl-atlas' presence lane consumes:

  data/forensic/_mbh_vulgate_verses.jsonl   {parvan, upaparva, adhyaya, shloka, id, slp1, C}
  data/forensic/_mbh_bori_halfverse.jsonl   {parvan, adhyaya, shloka, half, loc, folded}

(The name deliberately differs from f8_mbh_verify.py's `_mbh_bori_folded.jsonl`: that cache is
built from the GRETIL mirror at WHOLE-verse granularity, this one from the Tokunaga/Smith "UR"
text at HALF-verse granularity. Two files, two lanes, no silent cross-consumption.)

**ISO-15919 trap, measured 16-08-2026:** the "UR" text is ISO-15919, not IAST. `r̥`/`l̥`
(NFD r + combining ring U+0325) survive `indic_transliteration`'s IAST->SLP1 unharmed, but
anusvara `ṁ` (U+1E41) does **not** — it passes straight through as a literal `ṁ` and every
folded key carrying an anusvara silently fails to match the vulgate. Normalising ISO-15919 to
IAST before transliteration is therefore load-bearing, not cosmetic.

If the sibling branch is missing, the fallback is the original acquisition path — re-run
`scripts/forensic/f8_mbh_harvest.py` for the vulgate (NOTE 16-08-2026: the sanatana.in AJAX
endpoint `listing/getParvaByPage/` now returns an empty body — the site was rebuilt around
`listing/parva/<slug>?id=P..._U..._A..._S...`, so that harvester needs a rewrite before it
works again) and the `curl` loop in CommentaryStrategies'
`mahabharata-nilakantha/BORI_CRITICAL_SOURCE.md` for the critical text.

Run from repo root:  python scripts/forensic/f8_mbh_witnesses.py
Deps: indic_transliteration; ../sanskrit-util/py (slp1_simplify).
"""
import sys, os, re, json, subprocess, unicodedata

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sanskrit_util import slp1_simplify

SIBLING = "../CommentaryStrategies"
BRANCH = "mahabharata-nilakantha-local-only-do-not-push"
VULGATE_BLOB = "mahabharata-nilakantha/nilakantha_vulgate_full.jsonl"
BORI_BLOB = "mahabharata-nilakantha/bori-critical/MBh%02d.txt"

VULGATE_OUT = "data/forensic/_mbh_vulgate_verses.jsonl"   # gitignored (rights)
BORI_OUT = "data/forensic/_mbh_bori_halfverse.jsonl"      # gitignored (rights)

DEV = re.compile(r"[ऀ-ॿ]")
# BORI "UR" line: PPAAASSS + half-verse letter, then a tab or spaces, then the text.
BORI_LINE = re.compile(r"^(\d{2})(\d{3})(\d{3})([a-zA-Z]?)\s+(.+?)\s*$")


def fold(s):
    """SLP1 -> length/retroflex/sibilant-folded, letters only: the fuzzy match key.

    f8_mbh_verify.py's fold only drops spaces; this one also drops avagraha/punctuation, so a
    vulgate `yajamAno 'nuparyagAH` and a critical `yajamāno 'nuparyagāḥ` fold identically."""
    return re.sub(r"[^a-z]", "", slp1_simplify(s or "").lower())


def iso15919_to_iast(s):
    """ISO-15919 (the BORI "UR" encoding) -> IAST. See the module docstring's anusvara trap."""
    s = unicodedata.normalize("NFD", s)
    s = s.replace("r̥", "ṛ").replace("R̥", "Ṛ")
    s = s.replace("l̥", "ḷ").replace("L̥", "Ḷ")
    s = unicodedata.normalize("NFC", s)
    return s.replace("ṁ", "ṃ").replace("Ṁ", "Ṃ")   # ṁ -> ṃ


def git_show(path):
    """Stream one blob out of the sibling repo's local-only branch. Bytes never touch its
    working tree, so the sibling main checkout stays clean."""
    return subprocess.run(["git", "-C", SIBLING, "show", f"{BRANCH}:{path}"],
                          capture_output=True, encoding="utf-8", errors="replace")


def have_branch():
    r = subprocess.run(["git", "-C", SIBLING, "rev-parse", "--verify", BRANCH],
                       capture_output=True, encoding="utf-8", errors="replace")
    return r.returncode == 0


def clean_mula(dev):
    """Strip the danda/verse-number furniture from a sanatana.in mula field."""
    dev = re.sub(r"[०-९]+", " ", dev or "")
    dev = re.sub(r"[।॥\s]+", " ", dev)
    return dev.strip()


def stage_vulgate():
    r = git_show(VULGATE_BLOB)
    if r.returncode != 0:
        print(f"  MISSING {VULGATE_BLOB} on {BRANCH}", file=sys.stderr)
        return 0
    rows, empty = [], 0
    per_parvan = {}
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        dev = clean_mula(d.get("mula_dev"))
        if not DEV.search(dev):
            empty += 1
            dev = ""
        p = int(d["parva_no"])
        per_parvan[p] = per_parvan.get(p, 0) + 1
        rows.append({
            "parvan": p, "upaparva": int(d.get("upaparva") or 0),
            "adhyaya": int(d["adhyaya"]), "shloka": int(d["shloka"]),
            "id": d.get("id", ""),
            "slp1": transliterate(dev, sanscript.DEVANAGARI, sanscript.SLP1) if dev else "",
        })
    rows.sort(key=lambda x: (x["parvan"], x["adhyaya"], x["shloka"]))
    running = {}
    for x in rows:
        running[x["parvan"]] = running.get(x["parvan"], 0) + 1
        x["C"] = running[x["parvan"]]
    with open(VULGATE_OUT, "w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"  vulgate: {len(rows)} verses ({empty} with empty mula) -> {VULGATE_OUT}")
    return len(rows)


def stage_bori():
    out, missing = [], []
    for p in range(1, 19):
        r = git_show(BORI_BLOB % p)
        if r.returncode != 0:
            missing.append(p)
            continue
        for raw in r.stdout.splitlines():
            if not raw or raw.startswith("%"):
                continue
            m = BORI_LINE.match(raw)
            if not m:
                continue
            pp, aa, ss, half, text = m.groups()
            if int(pp) != p:
                continue
            slp = transliterate(iso15919_to_iast(text), sanscript.IAST, sanscript.SLP1)
            folded = fold(slp)
            if len(folded) < 4:
                continue
            out.append({"parvan": p, "adhyaya": int(aa), "shloka": int(ss), "half": half,
                        "loc": f"{p:02d},{int(aa)}.{int(ss)}{half}", "folded": folded})
    if missing:
        print(f"  MISSING BORI parvans: {missing}", file=sys.stderr)
    with open(BORI_OUT, "w", encoding="utf-8") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"  BORI critical: {len(out)} half-verse lines -> {BORI_OUT}")
    return len(out)


def main():
    print("F8d — stage the rights-gated MBh witnesses (H2845)")
    if not have_branch():
        print(f"FATAL: {SIBLING} has no branch {BRANCH}.\n"
              "  Vulgate fallback: scripts/forensic/f8_mbh_harvest.py (endpoint currently dead —\n"
              "  see this file's docstring).\n"
              "  BORI fallback: the curl loop in CommentaryStrategies'\n"
              "  mahabharata-nilakantha/BORI_CRITICAL_SOURCE.md.", file=sys.stderr)
        return 2
    os.makedirs("data/forensic", exist_ok=True)
    nv = stage_vulgate()
    nb = stage_bori()
    print(f"\nstaged: vulgate={nv} verses, BORI={nb} half-verses")
    print("Both outputs are GITIGNORED. Never commit, never publish verse bytes; only "
          "measurements and de-minimis single-verse quotations leave this repo.")
    return 0 if (nv and nb) else 1


if __name__ == "__main__":
    sys.exit(main())
