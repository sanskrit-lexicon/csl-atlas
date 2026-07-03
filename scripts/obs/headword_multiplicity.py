#!/usr/bin/env python3
"""OBS-R — format-aware headword multiplicity across all 43 csl-orig dicts.

Fixes the parser gap noted in `docs/CORPUS_REDUNDANCY_GENEALOGY.md`: three
Hemacandra kośas (abch, acph, acsj) carry **no `<k1>`** — they use the
sanskrit-kosha `<syns><s>lemma-POS,…</s>` synonym format. This extractor detects
the format per dictionary and uses the right key source, so every dictionary is
included in the redundancy / novelty numbers.

Headword key per dictionary:
* standard CDSL  — `<k1>` value on each `<L>` line (40 dicts)
* kośa (no `<k1>`) — lemmas inside `<syns><s>…</s>` (abch, acph, acsj) or a
  bare `<syns>lemma-POS,…` list without the `<s>` wrapper (nmmb), comma-split,
  POS suffix (`-puM`, `-strI`, `-na`, `-tri`, `-klI`, …) stripped

Validated: kośa extraction reproduces the sanhw1 lemma counts exactly
(abch 11,584 · acph 1,453 · acsj 634).

Outputs
-------
* `data/obs/headword_multiplicity.csv` — per-dict entries / distinct lemmas /
  unique-to-dict / unique%
* `data/obs/headword_collapse.json` — the enveloped corpus headline
  (entry→lemma collapse, redundancy, independence, fold-sensitivity bound);
  this is the committed anchor for P1 §3.2 (was print-only before)
* prints the corpus headline (entry→lemma collapse, redundancy, independence)

Usage:  python scripts/obs/headword_multiplicity.py
        (reads ../csl-orig/v02 — the sibling source repo)
"""
import csv, json, os, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # csl-atlas
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'lib'))
from dataset_meta import license_fields, generated_at_for_payload, read_json_if_exists  # noqa: E402
V02 = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUT_CSV = os.path.join(ROOT, 'data', 'obs', 'headword_multiplicity.csv')
OUT_JSON = os.path.join(ROOT, 'data', 'obs', 'headword_collapse.json')

K1 = re.compile(r'<k1>([^<]*)')
SYNS = re.compile(r'<syns><s>([^<]*)</s>')
# nmmb variant: <eid>N<syns>lemma-puM,lemma-klI,…  (no <s> wrapper; [^<\n]+
# requires a non-tag char, so <syns><s>… lines never double-match here)
SYNS_BARE = re.compile(r'<syns>([^<\n]+)')
POS = re.compile(r'-[a-zA-Z]+$')

# Final anusvara/visarga fold (OBS-R referee M-M3 / A02 R2 sensitivity bound):
# a trailing SLP1 M (anusvara) or H (visarga) is stripped so that e.g. devaM /
# devaH / deva collapse to one key. This is a sensitivity bound, not a
# replacement for the canonical <k1>/synonym keys used everywhere else in
# this script -- it is applied only inside fold_sensitivity() below.
FINAL_ANUSVARA_VISARGA = re.compile(r'[MH]$')


def folded(key):
    return FINAL_ANUSVARA_VISARGA.sub('', key)


def dict_files():
    for name in sorted(os.listdir(V02)):
        f = os.path.join(V02, name, name + '.txt')
        if os.path.isfile(f):
            yield name, f


def extract(path):
    """Return (format, entry_count, set_of_distinct_lemmas) for one dict file."""
    entries, k1_keys, syns_keys = 0, set(), set()
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('<L>'):
                entries += 1
                m = K1.search(line)
                if m and m.group(1):
                    k1_keys.add(m.group(1))
            for s in SYNS.findall(line) + SYNS_BARE.findall(line):
                for tok in s.split(','):
                    tok = POS.sub('', tok.strip())
                    if tok:
                        syns_keys.add(tok)
    if k1_keys:                       # standard CDSL dict
        return 'k1', entries, k1_keys
    return 'kosa', entries, syns_keys  # kośa fallback


def fold_sensitivity(per_dict):
    """Recompute the independence figure with a final anusvara/visarga fold
    applied to every headword key. Report-only (REVISION_BRIEF_P2_OBS.md
    Part 2, item 3) -- does not alter the canonical CSV/rows above."""
    fmult = defaultdict(int)
    fdistinct_keys = set()
    for _name, (_entries, keys) in per_dict.items():
        for k in keys:
            fdistinct_keys.add(folded(k))
    # multiplicity must be counted per-dictionary (a dict contributing both
    # devaM and devaH should count once), so fold within each dict first.
    per_dict_folded = {name: {folded(k) for k in keys} for name, (_e, keys) in per_dict.items()}
    for fkeys in per_dict_folded.values():
        for fk in fkeys:
            fmult[fk] += 1
    f_distinct = len(fmult)
    f_unique = sum(1 for v in fmult.values() if v == 1)
    return f_distinct, f_unique


def main():
    if not os.path.isdir(V02):
        sys.exit(f'csl-orig sources not found at {V02}')

    per_dict, fmt = {}, {}
    mult = defaultdict(int)
    owner = {}
    total_entries = 0
    for name, path in dict_files():
        kind, entries, keys = extract(path)
        fmt[name] = kind
        total_entries += entries
        for k in keys:
            mult[k] += 1
            owner[k] = name           # unambiguous only when mult==1
        per_dict[name] = (entries, keys)

    distinct = len(mult)
    unique = sum(1 for v in mult.values() if v == 1)
    uq_per_dict = defaultdict(int)
    for k, v in mult.items():
        if v == 1:
            uq_per_dict[owner[k]] += 1

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows = []
    for name in per_dict:
        entries, keys = per_dict[name]
        u = uq_per_dict.get(name, 0)
        rows.append({'dict': name, 'format': fmt[name], 'entries': entries,
                     'distinct_lemmas': len(keys), 'unique_to_dict': u,
                     'unique_pct': round(100 * u / len(keys), 1) if keys else 0.0})
    rows.sort(key=lambda r: -r['unique_to_dict'])
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['dict', 'format', 'entries',
                                           'distinct_lemmas', 'unique_to_dict', 'unique_pct'])
        w.writeheader(); w.writerows(rows)

    kosa = [r for r in rows if r['format'] == 'kosa']
    print(f'wrote {OUT_CSV}')
    print(f'  dicts: {len(rows)}  (kośa-format, now included: '
          f'{", ".join(sorted(r["dict"] for r in kosa))})')
    print(f'  total <L> entries: {total_entries:,}')
    print(f'  distinct lemmas:   {distinct:,}   (collapse {total_entries/distinct:.2f}:1)')
    print(f'  redundant (>=2 dicts): {100*(distinct-unique)/distinct:.1f}%   '
          f'independent: {100*unique/distinct:.1f}%')
    print('  kośa contribution (now counted):')
    for r in kosa:
        print(f'    {r["dict"]}: {r["distinct_lemmas"]:,} lemmas, '
              f'{r["unique_to_dict"]:,} unique ({r["unique_pct"]}%)')

    f_distinct, f_unique = fold_sensitivity(per_dict)
    before_pct = 100 * unique / distinct
    after_pct = 100 * f_unique / f_distinct

    # Enveloped headline artifact (P1 §3.2 anchor), under the same
    # dataset_meta envelope discipline as data/obs/citation_registers.json.
    payload = {
        'schemaVersion': '1.0.0',
        **license_fields(),
        'generatedBy': 'scripts/obs/headword_multiplicity.py',
        'sourceRoot': '../csl-orig/v02',
        'method': {
            'headwordKey': 'standard CDSL dicts: <k1> per <L> line; k1-less kosa dicts: '
                           'POS-stripped <syns> lemmas (<s>-wrapped for abch/acph/acsj, '
                           'bare comma list for nmmb)',
            'collapse': 'distinct lemma keys corpus-wide vs raw <L> entry count; a shared '
                        'headword is independent attestation in each dictionary, not '
                        'necessarily a copy, so the unique fraction is a floor for novelty',
            'foldSensitivity': 'final SLP1 anusvara (M) / visarga (H) stripped per key, '
                               'folded within each dict first — a report-only sensitivity '
                               'bound, not a replacement for the canonical keys',
        },
        'documentedIn': 'docs/CORPUS_REDUNDANCY_GENEALOGY.md',
        'perDictCsv': 'data/obs/headword_multiplicity.csv',
        'dictionaryCount': len(rows),
        'kosaFormatDicts': sorted(r['dict'] for r in kosa),
        'totalEntries': total_entries,
        'distinctLemmas': distinct,
        'collapseRatio': round(total_entries / distinct, 2),
        'redundantPct': round(100 * (distinct - unique) / distinct, 1),
        'independentPct': round(before_pct, 1),
        'foldSensitivity': {
            'distinctLemmas': f_distinct,
            'independentPct': round(after_pct, 1),
            'deltaPoints': round(after_pct - before_pct, 1),
        },
        'warnings': [
            'entry counts include homonym-split <L> records; the collapse ratio therefore '
            'mixes lexical redundancy with per-dictionary entry-splitting policy',
        ],
    }
    payload['generatedAt'] = generated_at_for_payload(read_json_if_exists(OUT_JSON), payload)
    with open(OUT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    print(f'wrote {OUT_JSON}')

    print('  anusvara/visarga fold-sensitivity (final M/H stripped, report-only):')
    print(f'    distinct lemmas {distinct:,} -> {f_distinct:,}')
    print(f'    independence {before_pct:.1f}% -> {after_pct:.1f}%'
          f'  (delta {after_pct - before_pct:+.1f} points)')


if __name__ == '__main__':
    main()
