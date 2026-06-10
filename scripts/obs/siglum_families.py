#!/usr/bin/env python3
"""OBS-C — abbreviation-family merge candidates for `<ls>` source sigla.

The diacritic/case fold in `scripts/lib/source-siglum.mjs` (`foldSiglum`) already
aligns MBh/MBH and RV/ṚV. What it cannot catch is **abbreviation-length**
variants of the same work — `R.` / `Rām.` / `Rāmāy.` all denote the Rāmāyaṇa.
Collapsing those is the central OBS-C contribution (`docs/CITATION_REGISTERS.md`).

Merging sigla is error-prone (e.g. `R.` could be Rāmāyaṇa or, via the bare fold,
collide with other short keys), so the atlas keeps merges **human-reviewed**:
the curated table is `src/data/dict-source-aliases.json`, grown from the
source-siglum review queue. This tool therefore **generates candidates**, it does
not auto-merge: it folds every `<ls>` siglum with the same `foldSiglum` logic,
clusters fold-keys that share a prefix (one abbreviation expanding another), and
emits a review worklist plus the *achievable* collapse if the candidates are
accepted.

Outputs
-------
* `data/obs/siglum_family_candidates.csv` — prefix, members, frequency (review worklist)
* prints: raw sigla → fold-keys → achievable families

Usage:  python scripts/obs/siglum_families.py [--prefix-len 4] [--min-freq 20]
"""
import argparse, csv, os, re, sys, unicodedata
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # csl-atlas
V02 = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUT_CSV = os.path.join(ROOT, 'data', 'obs', 'siglum_family_candidates.csv')

LS = re.compile(r'<ls>([^<]*)</ls>')
PRE_DIGIT = re.compile(r'[0-9].*')


def fold_siglum(s):
    """Port of foldSiglum() in scripts/lib/source-siglum.mjs."""
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())


def collect_sigla():
    raw = Counter()
    fold = Counter()
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
                    raw[sig] += 1
                    k = fold_siglum(sig)
                    if k:
                        fold[k] += 1
    return raw, fold


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefix-len', type=int, default=4,
                    help='shared leading characters that define a candidate family')
    ap.add_argument('--min-freq', type=int, default=20,
                    help='minimum citations for a fold-key to be a family member')
    args = ap.parse_args()

    if not os.path.isdir(V02):
        sys.exit(f'csl-orig sources not found at {V02}')

    raw, fold = collect_sigla()

    # Cluster fold-keys that share the first `prefix-len` characters. A cluster
    # with >=2 distinct keys is a candidate abbreviation family for review.
    groups = defaultdict(list)
    for key, n in fold.items():
        if n < args.min_freq or len(key) < args.prefix_len:
            continue
        groups[key[:args.prefix_len]].append((key, n))

    families = []
    for prefix, members in groups.items():
        if len(members) < 2:
            continue
        members.sort(key=lambda kv: -kv[1])
        rep = members[0][0]                 # most-cited member = provisional canonical
        families.append({
            'prefix': prefix,
            'n_members': len(members),
            'total_freq': sum(n for _, n in members),
            'representative': rep,
            'members': ' | '.join(f'{k}:{n}' for k, n in members),
            'status': 'unreviewed',
        })
    families.sort(key=lambda r: -r['total_freq'])

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['prefix', 'n_members', 'total_freq',
                                           'representative', 'members', 'status'])
        w.writeheader(); w.writerows(families)

    fold_keys = len(fold)
    merged_members = sum(r['n_members'] for r in families)
    achievable = fold_keys - merged_members + len(families)  # each family -> 1 key

    print(f'wrote {OUT_CSV}')
    print(f'  raw distinct sigla:        {len(raw):,}')
    print(f'  after foldSiglum:          {fold_keys:,}  (diacritic/case layer — already in source-siglum.mjs)')
    print(f'  candidate families (prefix-len {args.prefix_len}, min-freq {args.min_freq}): '
          f'{len(families):,}  covering {merged_members:,} fold-keys')
    print(f'  achievable fold-keys if all accepted: {achievable:,}  '
          f'(−{fold_keys-achievable:,})')
    print('  top families (review these first):')
    for r in families[:10]:
        print(f'    {r["representative"]:<12} ×{r["total_freq"]:<6} '
              f'[{r["members"][:70]}]')
    print('  → review-accept rows then add them to src/data/dict-source-aliases.json '
          '(feeds canonicalSiglum()).')


if __name__ == '__main__':
    main()
