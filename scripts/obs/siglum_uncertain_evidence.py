#!/usr/bin/env python3
"""OBS-C — per-dict raw-form evidence for the quarantined ("uncertain") sigla.

SPEC-4 step 5: the curated table (src/data/dicts/dict-source-aliases.json,
"uncertain" section) quarantines a handful of high-frequency fold-keys whose
correct merge target can't be decided without seeing which dictionary cites
which raw spelling how often (e.g. "Ratnam." could be several different
Ratnamalas depending on the dictionary). This script is EVIDENCE ONLY — it
does not merge or rule on anything; the August planning session reads this
table and rules.

Outputs
-------
* `data/obs/siglum_uncertain_evidence.csv` — quarantined_key, dict, raw_form, count

Usage:  python scripts/obs/siglum_uncertain_evidence.py
"""
import csv, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siglum_families import fold_siglum  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))          # csl-atlas
V02 = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUT_CSV = os.path.join(ROOT, 'data', 'obs', 'siglum_uncertain_evidence.csv')

LS = re.compile(r'<ls>([^<]*)</ls>')
PRE_DIGIT = re.compile(r'[0-9].*')

# Highest-frequency quarantined keys named in SPEC-4 step 5 (see the
# "uncertain" section of src/data/dicts/dict-source-aliases.json for the
# adjudication notes that quarantined each one).
QUARANTINED_KEYS = {"ratnam", "samk", "burn", "mahav", "bhar", "maitr"}


def collect_evidence():
    # (quarantined_key, dict, raw_form) -> count
    evidence = Counter()
    for name in sorted(os.listdir(V02)):
        f = os.path.join(V02, name, name + '.txt')
        if not os.path.isfile(f):
            continue
        with open(f, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                for c in LS.findall(line):
                    sig = PRE_DIGIT.sub('', c).strip(' .,')
                    if not sig:
                        continue
                    k = fold_siglum(sig)
                    if k in QUARANTINED_KEYS:
                        evidence[(k, name, sig)] += 1
    return evidence


def main():
    if not os.path.isdir(V02):
        sys.exit(f'csl-orig sources not found at {V02}')

    evidence = collect_evidence()

    rows = [
        {'quarantined_key': k, 'dict': d, 'raw_form': raw, 'count': n}
        for (k, d, raw), n in evidence.items()
    ]
    rows.sort(key=lambda r: (r['quarantined_key'], -r['count'], r['dict']))

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['quarantined_key', 'dict', 'raw_form', 'count'])
        w.writeheader(); w.writerows(rows)

    print(f'wrote {OUT_CSV}')
    print(f'  {len(rows):,} (quarantined_key, dict, raw_form) rows across {len(QUARANTINED_KEYS)} quarantined keys')
    totals = Counter()
    for r in rows:
        totals[r['quarantined_key']] += r['count']
    for k in sorted(QUARANTINED_KEYS):
        print(f'  {k:<8} total cites: {totals.get(k, 0):,}')


if __name__ == '__main__':
    main()
