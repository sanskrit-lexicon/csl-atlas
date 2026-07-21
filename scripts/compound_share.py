"""
compound_share.py  — H1423 Wave A (deterministic; reads committed model snapshot)

Generalises the H1416 per-letter compound-share law beyond MW. Reads the committed
ByT5 segmentation sample, computes per (dict x letter):
  - splitter compound share (n_segments >= 2) with a Wilson 95% CI
  - dash-truth compound share where the dict has the dash convention (MW, GRA)
  - the splitter's calibration vs MW dash-truth (precision/recall/F1) — the error
    bar that rides with every estimate.

Writes: data/pd/compound_share_by_letter.tsv (+ src/data/pd mirror).
Fallback: if the snapshot is absent (ByT5 unavailable), emits a dash-truth-only
table for MW/GRA and marks the splitter columns 'n/a (model unavailable)'.
"""
import sys, json, math
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import letter_anatomy as la

SNAP = la.ATLAS / 'data' / 'dharmamitra' / 'compound_segmentation_sample.json'
SCOPE = ['MW', 'AP', 'PWG', 'PWK', 'SKD', 'VCP', 'GRA']
DASH_DICTS = {'MW', 'GRA'}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


def main():
    rows = []
    calib = {}
    if not SNAP.exists():
        print(f'!! snapshot absent ({SNAP}) — FALLBACK: dash-truth-only (MW/GRA).')
        # dash-truth-only from headword lists (H1416 logic)
        for did in ('MW', 'GRA'):
            key2 = la.read_hw_list(did, 2)
            if not key2:
                continue
            by = {}
            for hw in key2:
                lb = la.base_letter(hw.replace('—', '').replace('-', ''))
                if lb is None:
                    continue
                d = by.setdefault(lb, [0, 0]); d[0] += 1
                if ('—' in hw) or ('-' in hw):
                    d[1] += 1
            for lb in sorted(by, key=lambda c: la.ALPHA_RANK.get(c, 999)):
                tot, dsh = by[lb]
                rows.append({'dict': did, 'letter_slp1': lb, 'letter_iast': la.IAST.get(lb, lb),
                             'n_sampled': tot, 'dash_truth_pct': f'{100*dsh/tot:.1f}',
                             'splitter_pct': 'n/a (model unavailable)', 'splitter_ci': '',
                             'calib_precision': '', 'calib_recall': ''})
        _write(rows, calib)
        return

    doc = json.loads(SNAP.read_text(encoding='utf-8'))
    data = doc['rows']
    print(f'read {len(data)} segmented headwords from snapshot ({doc.get("model")})')

    # calibration on MW (and GRA): splitter is_compound vs dash-truth
    for cd in DASH_DICTS:
        tp = fp = fn = tn = 0
        for r in data:
            if r['dict'] != cd or r.get('had_dash') is None:
                continue
            pred = r['n_segments'] >= 2
            truth = bool(r['had_dash'])
            tp += pred and truth; fp += pred and not truth
            fn += (not pred) and truth; tn += (not pred) and (not truth)
        prec = tp / (tp + fp) if (tp + fp) else float('nan')
        rec = tp / (tp + fn) if (tp + fn) else float('nan')
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else float('nan')
        calib[cd] = {'precision': prec, 'recall': rec, 'f1': f1,
                     'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'n': tp + fp + fn + tn}
        print(f'  calibration {cd}: P={prec:.3f} R={rec:.3f} F1={f1:.3f} '
              f'(tp={tp} fp={fp} fn={fn} tn={tn})')

    # per (dict x letter)
    agg = {}   # (did, lb) -> [n, splitter_compound, dash_total, dash_compound]
    for r in data:
        key = (r['dict'], r['letter'])
        a = agg.setdefault(key, [0, 0, 0, 0])
        a[0] += 1
        if r['n_segments'] >= 2:
            a[1] += 1
        if r.get('had_dash') is not None:
            a[2] += 1
            if r['had_dash']:
                a[3] += 1
    for did in SCOPE:
        for lb in sorted({k[1] for k in agg if k[0] == did},
                         key=lambda c: la.ALPHA_RANK.get(c, 999)):
            n, sc, dt, dc = agg[(did, lb)]
            lo, hi = wilson(sc, n)
            row = {'dict': did, 'letter_slp1': lb, 'letter_iast': la.IAST.get(lb, lb),
                   'n_sampled': n,
                   'dash_truth_pct': (f'{100*dc/dt:.1f}' if dt else ''),
                   'splitter_pct': f'{100*sc/n:.1f}',
                   'splitter_ci': f'[{lo:.1f},{hi:.1f}]',
                   'calib_precision': (f'{calib[did]["precision"]:.3f}' if did in calib else ''),
                   'calib_recall': (f'{calib[did]["recall"]:.3f}' if did in calib else '')}
            rows.append(row)
    _write(rows, calib)


def _write(rows, calib):
    cols = ['dict', 'letter_slp1', 'letter_iast', 'n_sampled', 'dash_truth_pct',
            'splitter_pct', 'splitter_ci', 'calib_precision', 'calib_recall']
    lines = ['\t'.join(cols)] + ['\t'.join(str(r.get(c, '')) for c in cols) for r in rows]
    # trailing calibration summary rows
    for cd, c in calib.items():
        lines.append('\t'.join([f'{cd}_CALIBRATION', '', str(c['n']), '',
                                f'P={c["precision"]:.3f}', f'R={c["recall"]:.3f}',
                                f'F1={c["f1"]:.3f}', f'tp={c["tp"]}fp={c["fp"]}',
                                f'fn={c["fn"]}tn={c["tn"]}']))
    body = '\n'.join(lines) + '\n'
    (la.OUT / 'compound_share_by_letter.tsv').write_text(body, encoding='utf-8')
    (la.SRC_OUT / 'compound_share_by_letter.tsv').write_text(body, encoding='utf-8')
    print(f'wrote {la.OUT / "compound_share_by_letter.tsv"} ({len(rows)} rows) [+ mirror]')


if __name__ == '__main__':
    main()
