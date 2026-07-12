#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parallel pre-translator for f10_sense_order.py's DE->EN gloss cache.

f10 translates ~38.9k PWG German sense-glosses single-threaded (~4/s); this fills the
SAME cache (data/forensic/_f10_sense_tcache.json) with a process Pool so the scoring run
finds every gloss already cached and does zero live MT. Idempotent + resumable: only
untranslated glosses are dispatched, and the cache is re-saved every CHUNK results, so a
kill loses at most CHUNK translations. Run repeatedly until it prints ALL_CACHED.

    python scripts/forensic/_f10_pretranslate.py [workers]   # default 6
"""
import os
import sys
import json
import multiprocessing as mp

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CACHE = "data/forensic/_f10_sense_tcache.json"
NEEDFILE = "data/forensic/_f10_need.json"
CHUNK = 200


def _worker(de):
    import argostranslate.translate as tr
    try:
        return de, tr.translate(de[:1500], "de", "en")
    except Exception:
        return de, ""


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6

    # The full universe of German glosses to translate is deterministic; parse the
    # (large) dictionaries ONCE and memoise it to NEEDFILE so chunked reruns start fast.
    if os.path.exists(NEEDFILE):
        with open(NEEDFILE, encoding="utf-8") as f:
            universe = json.load(f)
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import f10_sense_order as f10
        print("parsing MW+PWG once to build the gloss universe...")
        pwg_rec = f10.group_by_k1(os.path.join(f10.CSL_ORIG, "pwg", "pwg.txt"))
        mw_rec = f10.group_by_k1(os.path.join(f10.CSL_ORIG, "mw", "mw.txt"))
        pwg_s = {k: f10.senses_pwg(v) for k, v in pwg_rec.items()}
        mw_s = {k: f10.senses_mw(v) for k, v in mw_rec.items()}
        cand_pwg = sorted(h for h in (mw_s.keys() & pwg_s.keys())
                          if len(mw_s[h]) >= f10.MIN_SENSES and len(pwg_s[h]) >= f10.MIN_SENSES)
        universe = sorted({s["de"] for h in cand_pwg for s in pwg_s[h]})
        with open(NEEDFILE, "w", encoding="utf-8") as f:
            json.dump(universe, f, ensure_ascii=False)
        print(f"gloss universe = {len(universe):,} (memoised to {NEEDFILE})")

    tcache = {}
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            tcache = json.load(f)

    need = [de for de in universe if de not in tcache]
    print(f"universe={len(universe):,}  cached={len(tcache):,}  to-translate={len(need):,}")
    if not need:
        print("ALL_CACHED")
        return

    done = 0
    with mp.Pool(workers) as pool:
        for de, en in pool.imap_unordered(_worker, need, chunksize=8):
            tcache[de] = en
            done += 1
            if done % CHUNK == 0:
                with open(CACHE, "w", encoding="utf-8") as f:
                    json.dump(tcache, f, ensure_ascii=False)
                print(f"  {done:,}/{len(need):,} (+cache saved)")
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(tcache, f, ensure_ascii=False)
    print(f"done: translated {done:,}; cache now {len(tcache):,}")
    if done >= len(need):
        print("ALL_CACHED")


if __name__ == "__main__":
    main()
