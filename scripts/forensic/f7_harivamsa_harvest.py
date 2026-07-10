"""Phase F7a — harvest the Kinjawadekar (Chitrashala 1936) Harivaṃśa *vulgate* e-text.

Why (H488). A10 (`article_21_apparatus_not_errors.md` §6) needs to test a *shared erroneous
citation* — a HARIV. verse number wrong against the actual text, present in both PWG and MW.
A prior pass resolved 1 of 587 shared refs against DCS, because DCS carries the *critical*
edition (118 adhyāyas, ≈6,073 ślokas) while the Petersburg dictionaries cite the *Calcutta
vulgate* continuous śloka space (≈16,374). The vulgate e-text at mahabharata-resources.org
(Kinjawadekar, transcribed by K. S. Ramachandran & G. Schaufelberger) is the edition the
dictionaries actually cite; this script harvests it so the citations can be resolved directly.

What it does. Walks the CS index, fetches both page series (plain `hv_<p>_<c>.html` and the
fuller mūla-pāṭha `_mpr` series), extracts ITRANS verse text keyed by (parvan, adhyāya, verse),
and transcodes ITRANS → SLP1 with the CANONICAL indic_transliteration.sanscript library (NOT a
hand-rolled transcoder — SHARED_CODE.md rule). Prefers `_mpr` (root text, no interleaved
translation) where present.

Rights. The 1936 text is a volunteer transcription. Deriving *measurements* from it is fine;
republishing the bytes is not — so the harvested verse file is written to a GITIGNORED local
path (`data/forensic/_harivamsa_verses.jsonl`) and is never committed. Only downstream
*measurements* (offsets, resolution categories) are committed, by f7_harivamsa_resolve.py.

Host note. The site's TLS certificate is expired (Uprava/FINDINGS.md) — requests use an
unverified SSL context; WebFetch fails, this does not. Pages cache under the gitignored
`data/forensic/_hv_cache/`, so re-runs are offline and cheap.

Run from repo root:  python scripts/forensic/f7_harivamsa_harvest.py
Deps: pip install indic_transliteration
"""
import sys, os, re, ssl, time, json, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

BASE = "https://mahabharata-resources.org/harivamsa/"
CACHE = "data/forensic/_hv_cache"
OUT = "data/forensic/_harivamsa_verses.jsonl"   # gitignored (rights: derived text, not redistributed)
CEILING = {1: 55, 2: 128, 3: 135}               # real Kinjawadekar chapter counts; drop stray markers
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

MARKER = re.compile(r"\|\|\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)")
# only unambiguous page furniture — keep real verse words that mention harivaṃśa/parva
NOISE = re.compile(r"(uv[Aa]ch?a\s*[-:]?\s*$|shrImahAbhArata|iti\s+shrImahAbhArate"
                   r"|itiharivaMshe|adhyAyaH\s*$|dvaipayana|Chitrashala|continued\s*:?\s*$)", re.I)


def fetch(url, cache_name):
    os.makedirs(CACHE, exist_ok=True)
    cpath = os.path.join(CACHE, cache_name)
    if os.path.exists(cpath):
        return open(cpath, encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research; harivamsa harvest)"})
    for attempt in range(3):
        try:
            html = urllib.request.urlopen(req, context=CTX, timeout=45).read().decode("utf-8", "replace")
            open(cpath, "w", encoding="utf-8").write(html)
            time.sleep(0.25)
            return html
        except Exception as e:
            if attempt == 2:
                print(f"  FETCH-FAIL {url}: {e}", file=sys.stderr)
                return None
            time.sleep(1.5)


def strip_html(html):
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", html).replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"&[a-zA-Z#0-9]+;", " ", text)


def extract(text, exp_parvan):
    out, last = [], 0
    for m in MARKER.finditer(text):
        p, a, v = int(m.group(1)), int(m.group(2)), int(m.group(3))
        chunk = text[last:m.start()]
        last = m.end()
        if p != exp_parvan:
            continue
        keep = [ln.strip() for ln in re.split(r"[\r\n]+", chunk)
                if ln.strip() and not NOISE.search(ln.strip())]
        verse = re.sub(r"\s+", " ", " ".join(keep)).strip(" |").strip()
        verse = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", verse)
        verse = re.sub(r"\s+", " ", verse).strip()
        if verse:
            out.append((p, a, v, verse))
    return out


def index_urls():
    html = fetch(BASE + "harivamsa-cs-index.html", "index.html")
    urls, seen = [], set()
    for h in re.findall(r'href="([^"]+)"', html):
        m = re.search(r"hv_(\d+)_0*(\d+)(_mpr)?\.html$", h)
        if not m:
            continue
        p, a = int(m.group(1)), int(m.group(2))
        series = "mpr" if m.group(3) else "plain"
        if h.startswith("http"):
            if "mahabharata-resources.org" not in h:
                continue
            url = h
        else:
            url = BASE + h
        key = (p, a, series)
        if key in seen:
            continue
        seen.add(key)
        cache_name = re.sub(r"[^A-Za-z0-9_.]", "_", url.replace(BASE, ""))
        urls.append((p, a, series, url, cache_name))
    return urls


def main():
    urls = index_urls()
    print(f"chapter pages listed: {len(urls)}")
    verses = {}
    for i, (p, a, series, url, cn) in enumerate(urls):
        html = fetch(url, cn)
        if html is None:
            continue
        for (pp, aa, vv, itrans) in extract(strip_html(html), p):
            verses.setdefault((pp, aa, vv), {})[series] = itrans
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(urls)} pages, {len(verses)} verses")
    rows = []
    for (p, a, v), d in verses.items():
        if a > CEILING.get(p, 999):        # stray out-of-range marker
            continue
        itrans = d.get("mpr") or d.get("plain")
        if not itrans:
            continue
        rows.append({"parvan": p, "adhyaya": a, "verse": v,
                     "series": "mpr" if "mpr" in d else "plain",
                     "itrans": itrans,
                     "slp1": transliterate(itrans, sanscript.ITRANS, sanscript.SLP1)})
    rows.sort(key=lambda r: (r["parvan"], r["adhyaya"], r["verse"]))
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    byp = Counter(r["parvan"] for r in rows)
    print(f"wrote {len(rows)} verses -> {OUT}  ({len(rows)/16374*100:.1f}% of 16,374 vulgate ślokas)")
    for p in sorted(byp):
        print(f"  parvan {p}: {byp[p]} verses")


if __name__ == "__main__":
    main()
