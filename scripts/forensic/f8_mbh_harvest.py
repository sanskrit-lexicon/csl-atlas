"""Phase F8c — harvest the Nīlakaṇṭha (Bhāvadīpa) *vulgate* Mahābhārata mūla from sanatana.in.

Provides the vulgate adjudicator for the ALL-18-parvan fitted-index census
(f8_mbh_resolve.py). The Nīlakaṇṭha vulgate is the edition family PWG/MW cite by per-parvan
continuous śloka number; sanatana.in/mahabharata serves the complete text. (H761 harvested the
same source via CommentaryStrategies' nilakantha_parser.py for the book-7 Droṇa census
MBH_DRONA_FITTED_INDEX_CENSUS.md; this is the self-contained csl-atlas harvester covering all 18
parvans — the two agree exactly on book 7, 9,641 verses.)

Data endpoint (from the site's own common.js `.get(url,…,"json")` call): `listing/getParvaByPage/
<parva-slug>?page=<n>` with `X-Requested-With: XMLHttpRequest` + Referer, page 1-indexed. Returns
an HTML fragment: `<article class="adhyaya" id="Ppp_Uuu_Aaaa">` → `<div class="shloka text-center"
id="…_Saaa">` → `<p class="shloka_text">` (mūla, ending ॥N॥) + `<p class="bhavadeepa">` (ṭīkā,
skipped). The id carries parva/adhyāya/verse directly. Continuous per-parvan C = running verse
count ordered by (adhyāya, shloka).

Rights: third-party volunteer transcription — only measurements are redistributed; verse bytes go
to a GITIGNORED local jsonl, never committed.

Run from repo root:  python scripts/forensic/f8_mbh_harvest.py
Deps: indic_transliteration.
"""
import sys, os, re, ssl, time, json, html, urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

BASE = "https://sanatana.in/mahabharata/listing/getParvaByPage/"
REFBASE = "https://sanatana.in/mahabharata/listing/parva/"
CACHE = "data/forensic/_mbh_vulgate_cache"
OUT = "data/forensic/_mbh_vulgate_verses.jsonl"          # gitignored (rights)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

PARVAS = [
    ("adiparva", 1, 19), ("sabhaparva", 2, 10), ("vanaparva", 3, 22), ("virataparva", 4, 5),
    ("udyogaparva", 5, 10), ("bhishmaparva", 6, 4), ("dronaparva", 7, 8), ("karnaparva", 8, 1),
    ("shalyaparva", 9, 3), ("sauptikaparva", 10, 2), ("striparva", 11, 3), ("shantiparva", 12, 3),
    ("anushasanaparva", 13, 2), ("ashwamedhikaparva", 14, 2), ("ashramavasikaparva", 15, 3),
    ("mausalaparva", 16, 1), ("mahaprasthanikaparva", 17, 1), ("swargarohanaparva", 18, 2),
]
SHLOKA = re.compile(r'<div class="shloka text-center" id="P(\d+)_U\d+_A(\d+)_S(\d+)">(.*?)</div>', re.S)
SHLOKA_TEXT = re.compile(r'<p class="shloka_text[^"]*">(.*?)</p>', re.S)
DEV = re.compile(r'[ऀ-ॿ]')


def fetch(slug, page):
    os.makedirs(CACHE, exist_ok=True)
    cpath = os.path.join(CACHE, f"{slug}_{page}.html")
    if os.path.exists(cpath):
        return open(cpath, encoding="utf-8").read()
    url = f"{BASE}{slug}?page={page}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (research; mbh vulgate harvest)",
        "X-Requested-With": "XMLHttpRequest", "Referer": REFBASE + slug})
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, context=CTX, timeout=60).read().decode("utf-8", "replace")
            open(cpath, "w", encoding="utf-8").write(data)
            time.sleep(0.3)
            return data
        except Exception as e:
            if attempt == 2:
                print(f"  FETCH-FAIL {url}: {e}", file=sys.stderr)
                return ""
            time.sleep(2)


def clean_verse(frag):
    m = SHLOKA_TEXT.search(frag)
    body = m.group(1) if m else frag
    body = re.sub(r'<span class="uvacha">.*?</span>', " ", body, flags=re.S)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    body = re.sub(r"[०-९]+", " ", body)
    body = re.sub(r"[।॥\s]+", " ", body).strip()
    return body


def main():
    print("F8c — Nīlakaṇṭha vulgate MBH harvest (sanatana.in) — H610")
    rows = []
    for slug, pnum, maxpage in PARVAS:
        got = 0
        for page in range(1, maxpage + 1):
            frag_html = fetch(slug, page)
            for m in SHLOKA.finditer(frag_html):
                p, adh, sh = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if p != pnum:
                    continue
                dev = clean_verse(m.group(4))
                if not DEV.search(dev):
                    continue
                slp = transliterate(dev, sanscript.DEVANAGARI, sanscript.SLP1)
                rows.append({"parvan": pnum, "adhyaya": adh, "shloka": sh, "slp1": slp})
                got += 1
        print(f"  {slug:22s} P{pnum:02d}: {got} verses")
    rows.sort(key=lambda r: (r["parvan"], r["adhyaya"], r["shloka"]))
    cby = Counter()
    for r in rows:
        cby[r["parvan"]] += 1
        r["C"] = cby[r["parvan"]]
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nwrote {len(rows)} verses -> {OUT}")
    for p in sorted(cby):
        print(f"  parvan {p:2d}: {cby[p]} verses")


if __name__ == "__main__":
    main()
