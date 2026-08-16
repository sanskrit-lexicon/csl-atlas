"""Throwaway probe (H2845): how BORI ISO-15919 survives IAST->SLP1."""
import sys, os, json, unicodedata, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sanskrit_util import slp1_simplify

r = subprocess.run(["git", "-C", "../CommentaryStrategies", "show",
                    "mahabharata-nilakantha-local-only-do-not-push:mahabharata-nilakantha/bori-critical/MBh12.txt"],
                   capture_output=True, encoding="utf-8", errors="replace")
lines = [l for l in r.stdout.splitlines() if l.startswith("12223") or l.startswith("12226")][:8]
for l in lines[:6]:
    print(repr(l[:70]))
    body = l.split(None, 1)[1] if len(l.split(None, 1)) > 1 else ""
    print("   NFD codepoints:", [hex(ord(c)) for c in unicodedata.normalize("NFD", body)[:14]])
    print("   SLP1 raw    :", transliterate(body, sanscript.IAST, sanscript.SLP1)[:60])
    n = unicodedata.normalize("NFD", body).replace("r̥", "ṛ").replace("l̥", "ḷ")
    n = unicodedata.normalize("NFC", n).replace("ṁ", "ṃ")
    print("   SLP1 normed :", transliterate(n, sanscript.IAST, sanscript.SLP1)[:60])
    print("   folded      :", slp1_simplify(transliterate(n, sanscript.IAST, sanscript.SLP1)).replace(" ", "")[:60])
