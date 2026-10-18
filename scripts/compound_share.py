"""
compound_share.py  — H1423 Wave A (deterministic; reads committed model snapshot)

Generalises the H1416 per-letter compound-share law beyond MW. Reads the committed
ByT5 segmentation sample, computes per (dict x letter):
  - splitter compound share (n_segments >= 2) with a Wilson 95% CI
  - dash-truth compound share where the dict has the dash convention (MW, GRA)
  - the splitter's calibration against BOTH dash truths (H6964 / A68 Q13):
      * loose  = headword carries any dash joint (em dash or hyphen);
      * strict = em-dash depth >= 3 (>= 2 em dashes), i.e. the joint reading;
    precision/recall/F1 per truth, with n and the tp/fp/fn/tn counts.

The strict population is the em-dash entries only (denominator of the 6.8 % figure);
the loose population is every sampled headword. The prediction is the splitter's
is-compound verdict (n_segments >= 2) in both readings — so the two F1s measure the
same call against two different truths and neither is silently presented alone.

Writes: data/pd/compound_share_by_letter.tsv (+ src/data/pd mirror).
Fallback: if the snapshot is absent (ByT5 unavailable), emits a dash-truth-only
table for MW/GRA and marks the splitter columns 'n/a (model unavailable)'.
"""
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import letter_anatomy as la

SNAP = la.ATLAS / 'data' / 'dharmamitra' / 'compound_segmentation_sample.json'
SCOPE = ['MW', 'AP', 'PWG', 'PWK', 'SKD', 'VCP', 'GRA']
DASH_DICTS = {'MW', 'GRA'}
EM = '\u2014'   # em dash — the strict (joint) marker


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


def _confusion(pairs):
    """pairs = [(pred, truth), ...] -> dict with n, tp/fp/fn/tn, precision/recall/f1."""
    tp = fp = fn = tn = 0
    for pred, truth in pairs:
        tp += pred and truth
        fp += pred and not truth
        fn += (not pred) and truth
        tn += (not pred) and (not truth)
    n = tp + fp + fn + tn
    prec = tp / (tp + fp) if (tp + fp) else None
    rec = tp / (tp + fn) if (tp + fn) else None
    f1 = (2 * prec * rec / (prec + rec)) if (prec is not None and rec is not None
                                            and (prec + rec)) else None
    return {'n': n, 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': prec, 'recall': rec, 'f1': f1,
            'truth_rate': (100 * (tp + fn) / n if n else None),
            'pred_rate': (100 * (tp + fp) / n if n else None)}


def _fmt(x, nd=3):
    return '' if x is None else f'{x:.{nd}f}'


def strict_truth(key2):
    """Strict joint reading: mark-up has >= 2 em dashes (3+ members)."""
    return (key2 or '').count(EM) >= 2


def loose_truth(key2, had_dash):
    if had_dash is not None:
        return bool(had_dash)
    return (EM in (key2 or '')) or ('-' in (key2 or ''))


def main():
    rows = []
    calib = {}
    per_letter = {}
    if not SNAP.exists():
        print(f'!! snapshot absent ({SNAP}) — FALLBACK: dash-truth-only (MW/GRA).')
        # dash-truth-only from headword lists (H1416 logic)
        for did in ('MW', 'GRA'):
            key2 = la.read_hw_list(did, 2)
            if not key2:
                continue
            by = {}
            for hw in key2:
                lb = la.base_letter(hw.replace(EM, '').replace('-', ''))
                if lb is None:
                    continue
                d = by.setdefault(lb, [0, 0]); d[0] += 1
                if (EM in hw) or ('-' in hw):
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
    print(f'read {len(data)} segmented headwords from snapshot '
          f'({doc.get("model")}@{str(doc.get("revision"))[:12]}, {doc.get("date")})')

    # Calibration on MW (and GRA) against both dash truths. Same splitter verdict
    # (n_segments >= 2) against each truth; strict truth restricted to em-dash rows.
    for cd in sorted(DASH_DICTS):
        d = [r for r in data if r['dict'] == cd]
        loose = _confusion([(r['n_segments'] >= 2, loose_truth(r.get('key2'), r.get('had_dash')))
                            for r in d])
        # The strict joint reading is MW's em-dash convention (Q13; the GRA
        # marker convention is a separate question, A68 Q8), so it is only
        # defined for MW.
        strict = None
        if cd == 'MW':
            em_rows = [r for r in d if EM in (r.get('key2') or '')]
            strict = _confusion([(r['n_segments'] >= 2, strict_truth(r.get('key2')))
                                 for r in em_rows])
        calib[cd] = {'loose': loose, 'strict': strict}
        for name, c in (('loose', loose), ('strict', strict)):
            if c is None:
                continue
            print(f'  calibration {cd} [{name}]: n={c["n"]} base={_fmt(c["truth_rate"],1)}% '
                  f'P={_fmt(c["precision"])} R={_fmt(c["recall"])} F1={_fmt(c["f1"])} '
                  f'(tp={c["tp"]} fp={c["fp"]} fn={c["fn"]} tn={c["tn"]})')

        # per-letter calibration for this dict
        letters = sorted({r['letter'] for r in d}, key=lambda c: la.ALPHA_RANK.get(c, 999))
        for lb in letters:
            dl = [r for r in d if r['letter'] == lb]
            per_letter[(cd, lb, 'loose')] = _confusion(
                [(r['n_segments'] >= 2, loose_truth(r.get('key2'), r.get('had_dash'))) for r in dl])
            if cd == 'MW':
                dl_em = [r for r in dl if EM in (r.get('key2') or '')]
                per_letter[(cd, lb, 'strict')] = _confusion(
                    [(r['n_segments'] >= 2, strict_truth(r.get('key2'))) for r in dl_em])

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
            lc = per_letter.get((did, lb, 'loose'))
            st = per_letter.get((did, lb, 'strict'))
            row = {'dict': did, 'letter_slp1': lb, 'letter_iast': la.IAST.get(lb, lb),
                   'n_sampled': n,
                   'dash_truth_pct': (f'{100*dc/dt:.1f}' if dt else ''),
                   'splitter_pct': f'{100*sc/n:.1f}',
                   'splitter_ci': f'[{lo:.1f},{hi:.1f}]',
                   'calib_precision': _fmt(lc['precision']) if lc else '',
                   'calib_recall': _fmt(lc['recall']) if lc else '',
                   'calib_f1': _fmt(lc['f1']) if lc else '',
                   'calib_n': lc['n'] if lc else '',
                   'calib_tp': lc['tp'] if lc else '',
                   'calib_fp': lc['fp'] if lc else '',
                   'calib_fn': lc['fn'] if lc else '',
                   'calib_tn': lc['tn'] if lc else '',
                   'calib_precision_strict': _fmt(st['precision']) if st else '',
                   'calib_recall_strict': _fmt(st['recall']) if st else '',
                   'calib_f1_strict': _fmt(st['f1']) if st else '',
                   'calib_n_strict': st['n'] if st else '',
                   'calib_tp_strict': st['tp'] if st else '',
                   'calib_fp_strict': st['fp'] if st else '',
                   'calib_fn_strict': st['fn'] if st else '',
                   'calib_tn_strict': st['tn'] if st else ''}
            rows.append(row)
    _write(rows, calib)


def _write(rows, calib):
    cols = ['dict', 'letter_slp1', 'letter_iast', 'n_sampled', 'dash_truth_pct',
            'splitter_pct', 'splitter_ci', 'calib_precision', 'calib_recall',
            'calib_f1', 'calib_n', 'calib_tp', 'calib_fp', 'calib_fn', 'calib_tn',
            'calib_precision_strict', 'calib_recall_strict', 'calib_f1_strict',
            'calib_n_strict', 'calib_tp_strict', 'calib_fp_strict',
            'calib_fn_strict', 'calib_tn_strict']
    lines = ['\t'.join(cols)] + [
        '\t'.join(str(r.get(c, '')) for c in cols).rstrip('\t') for r in rows]
    # trailing calibration summary rows: one per dict per truth
    for cd in sorted(calib):
        for name in ('loose', 'strict'):
            c = calib[cd][name]
            if c is None:
                continue
            lines.append('\t'.join([
                f'{cd}_CALIBRATION_{name}', '', '', str(c['n']),
                _fmt(c['truth_rate'], 1), _fmt(c['pred_rate'], 1), '',
                _fmt(c['precision']), _fmt(c['recall']), _fmt(c['f1']),
                str(c['n']), str(c['tp']), str(c['fp']), str(c['fn']), str(c['tn']),
                '', '', '', '', '', '', '', '']).rstrip('\t'))
    body = '\n'.join(lines) + '\n'
    (la.OUT / 'compound_share_by_letter.tsv').write_text(body, encoding='utf-8')
    (la.SRC_OUT / 'compound_share_by_letter.tsv').write_text(body, encoding='utf-8')
    print(f'wrote {la.OUT / "compound_share_by_letter.tsv"} ({len(rows)} rows) [+ mirror]')


if __name__ == '__main__':
    main()
