"""
count_headwords.py — count entries in every CDSL dictionary by counting
`<L>` markers in the canonical .txt files in csl-orig/v02/.

Reads:  ../../csl-orig/v02/<dict>/<dict>.txt
Writes: ../data/headwords.json   keyed by dictionary id (lowercase)
        ../data/snapshots/<date>/headwords.json
"""
import json, sys, datetime, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent / 'data'
CSL_ORIG = Path(__file__).resolve().parent.parent.parent / 'csl-orig' / 'v02'

L_PATTERN = re.compile(r'^<L>', re.MULTILINE)
LEND_PATTERN = re.compile(r'<LEND>')


def count_file(path):
    """Return (L_count, LEND_count, byte_size, line_count) for a dict file."""
    try:
        # Use binary read to avoid UTF-8 decode failures on legacy files
        b = path.read_bytes()
    except Exception as e:
        return None
    text_for_match = b.decode('utf-8', errors='replace')
    L = len(L_PATTERN.findall(text_for_match))
    LE = len(LEND_PATTERN.findall(text_for_match))
    return {
        'L_count': L,
        'LEND_count': LE,
        'balanced': L == LE,
        'bytes': len(b),
        'lines': text_for_match.count('\n') + 1,
    }


def main():
    if not CSL_ORIG.exists():
        print(f'csl-orig/v02 not found at {CSL_ORIG}', file=sys.stderr)
        sys.exit(1)

    out = {}
    for d in sorted(CSL_ORIG.iterdir()):
        if not d.is_dir():
            continue
        slug = d.name
        # Find the canonical text file: <slug>.txt or fall back to first .txt
        candidates = [d / f'{slug}.txt']
        candidates += sorted(d.glob('*.txt'))
        text_file = next((p for p in candidates if p.exists()), None)
        if not text_file:
            continue
        stats = count_file(text_file)
        if stats is None:
            continue
        out[slug] = {
            'dict_id': slug.upper(),
            'source_file': str(text_file.relative_to(CSL_ORIG.parent.parent)).replace('\\', '/'),
            **stats,
        }
        ok = '✓' if stats['balanced'] else '⚠'
        print(f'  {slug:<10} {ok} L={stats["L_count"]:>7,}  LEND={stats["LEND_count"]:>7,}  '
              f'bytes={stats["bytes"]:>10,}  lines={stats["lines"]:>9,}')

    # Aggregate
    summary = {
        'snapshot_date': datetime.date.today().isoformat(),
        'dict_count': len(out),
        'total_entries': sum(v['L_count'] for v in out.values()),
        'unbalanced_dicts': [k for k, v in out.items() if not v['balanced']],
    }
    out['_summary'] = summary

    body = json.dumps(out, indent=2, ensure_ascii=False)
    (DATA / 'headwords.json').write_text(body, encoding='utf-8')
    snap_dir = DATA / 'snapshots' / summary['snapshot_date']
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / 'headwords.json').write_text(body, encoding='utf-8')

    print(f'\n  TOTAL across {summary["dict_count"]} dictionaries: '
          f'{summary["total_entries"]:,} entries')
    if summary['unbalanced_dicts']:
        print(f'  ⚠ Unbalanced <L>/<LEND> in: {summary["unbalanced_dicts"]}')


if __name__ == '__main__':
    main()
