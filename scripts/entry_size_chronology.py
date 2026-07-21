"""
entry_size_chronology.py  — H1423 Wave B

The funding-decay "why": regress dictionary entry-size on REAL publication time,
not just alphabetical position (H1416). PWG is the clean case — its <pc> field
encodes volume 1-7, each with a known year — so every entry maps to a calendar
year. Also tests the editorial-compression counter-explanation, and best-effort
covers the other serial dicts (flagged date_quality).

Writes:
  data/pd/entry_size_by_year.tsv  (+ src/data/pd mirror)

Reuses letter_anatomy.py constants/paths; measures body length the same way (H1416).
Deterministic (no random/now).
"""
import sys, re, math
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from scipy import stats as sps
import letter_anatomy as la   # reuse CSL_ORIG, OUT, SRC_OUT, base_letter, TAG, BRACE

# ---- entry parser that also yields the <pc> field (Wave-B extension) ----
L_BLOCK = re.compile(r'<L>(.*?)<LEND>', re.DOTALL)
K1 = re.compile(r'<k1>(.*?)(?:<|$)')
PC = re.compile(r'<pc>(.*?)(?:<|$)')

def parse_entries_pc(txt_path):
    """Yield (k1, pc, body_chars) per <L>..<LEND>, in file order."""
    b = txt_path.read_bytes()
    if b[:3] == b'\xef\xbb\xbf':
        b = b[3:]
    text = b.decode('utf-8', 'replace')
    for m in L_BLOCK.finditer(text):
        block = m.group(1)
        nl = block.find('\n')
        header = block if nl < 0 else block[:nl]
        body = '' if nl < 0 else block[nl + 1:]
        km = K1.search(header)
        pm = PC.search(header)
        k1 = km.group(1) if km else ''
        pc = pm.group(1) if pm else ''
        clean = la.BRACE.sub('', la.TAG.sub('', body))
        clean = re.sub(r'\s+', ' ', clean).strip()
        yield k1, pc, len(clean)

# ---- date models per dict ----
# PWG: <pc> leading digit = volume; volume -> year (exact).
PWG_VOLUME_YEARS = {1: 1855, 2: 1858, 3: 1861, 4: 1865, 5: 1868, 6: 1871, 7: 1875}
LEAD_DIGIT = re.compile(r'^\s*(\d+)')

def pwg_year(pc):
    m = LEAD_DIGIT.match(pc or '')
    if not m:
        return None, None
    vol = int(m.group(1))
    return (vol, PWG_VOLUME_YEARS.get(vol))

# Serial dicts in scope + how we can date them.
#   date_quality: 'exact' (per-volume year), 'span' (only start-end known -> position proxy),
#                 'point' (single edition year, no within-work spread).
DATE_MODELS = {
    'pwg':  ('PWG', 'exact', (1855, 1875)),
    'pwkvn':('PWK', 'span',  (1879, 1889)),   # 7 vols 1879-89, no per-vol map available
    'skd':  ('SKD', 'point', (1886, 1886)),   # single 1886 edition
    'vcp':  ('VCP', 'span',  (1873, 1884)),   # multi-fascicle, no per-fascicle map
}

def within_year_slope(years, sizes):
    """OLS slope of log1p(size) on year; return (chars/decade %, ci, p, n). Robust log DV."""
    y = np.asarray(years, float); s = np.log1p(np.asarray(sizes, float))
    n = len(y)
    if n < 30 or len(np.unique(y)) < 2:
        return None
    x = y - y.mean(); sc = s - s.mean()
    sxx = float((x * x).sum())
    slope = float((x * sc).sum() / sxx)          # log-units per year
    resid = sc - slope * x
    df = n - 2
    se = math.sqrt((resid @ resid) / df / sxx)
    t = float(sps.t.ppf(0.975, df))
    lo, hi = slope - t * se, slope + t * se
    pval = float(2 * sps.t.sf(abs(slope / se), df))
    pct_decade = 100.0 * (math.exp(slope * 10) - 1)   # % size change per decade
    return {'slope_log_per_yr': slope, 'pct_per_decade': pct_decade,
            'ci_lo_pct': 100.0 * (math.exp(lo * 10) - 1),
            'ci_hi_pct': 100.0 * (math.exp(hi * 10) - 1), 'p': pval, 'n': n}

def main():
    rows = []          # per (dict x year/volume)
    slope_rows = []    # trailing YEAR_SLOPE per dict
    print('=== Wave B — entry-size chronology ===')

    for slug, (did, quality, span) in DATE_MODELS.items():
        path = la.CSL_ORIG / slug / f'{slug}.txt'
        if not path.exists():
            print(f'  !! missing {path}'); continue
        entries = list(parse_entries_pc(path))
        N = len(entries)

        if slug == 'pwg':
            # exact per-volume year
            years, sizes = [], []
            by_vol = {}
            unknown = 0
            for k1, pc, chars in entries:
                vol, yr = pwg_year(pc)
                if yr is None:
                    unknown += 1; continue
                years.append(yr); sizes.append(chars)
                d = by_vol.setdefault(vol, []); d.append(chars)
            # validate: buckets sum to entries-with-year, all 7 volumes present
            got_vols = sorted(by_vol)
            print(f'  PWG: {N:,} entries, {unknown} without a parseable <pc> volume; '
                  f'volumes present = {got_vols}')
            for vol in sorted(by_vol):
                arr = np.array(by_vol[vol])
                rows.append({'dict': did, 'volume': vol, 'year': PWG_VOLUME_YEARS[vol],
                             'n_entries': len(arr), 'mean_chars': f'{arr.mean():.0f}',
                             'median_chars': f'{np.median(arr):.0f}', 'date_quality': 'exact'})
            res = within_year_slope(years, sizes)
            if res:
                # sign vs H1416 alphabetical-position robust rho (-0.186, DECAY)
                sign = 'DECAY' if res['pct_per_decade'] < 0 else 'GROWTH'
                agree = 'agrees with H1416 pos-slope (DECAY)' if res['pct_per_decade'] < 0 else 'DISAGREES with H1416 (was DECAY)'
                print(f'  PWG year-slope = {res["pct_per_decade"]:+.1f}%/decade '
                      f'[{res["ci_lo_pct"]:+.1f},{res["ci_hi_pct"]:+.1f}] p={res["p"]:.1e} '
                      f'n={res["n"]:,} -> {sign}; {agree}')
                # compression counter-test: is decay smooth, or a one-time vol-1 break?
                v1 = np.array(by_vol.get(1, []))
                later = np.concatenate([np.array(by_vol[v]) for v in by_vol if v >= 2]) if len(by_vol) > 1 else np.array([])
                ct = ''
                if len(v1) and len(later):
                    # median-based (heavy tail): vol-1 vs later, and slope excluding vol-1
                    yrs2 = [PWG_VOLUME_YEARS[pwg_year(pc)[0]] for k1, pc, c in entries
                            if pwg_year(pc)[0] and pwg_year(pc)[0] >= 2]
                    sz2 = [c for k1, pc, c in entries if pwg_year(pc)[0] and pwg_year(pc)[0] >= 2]
                    res2 = within_year_slope(yrs2, sz2)
                    v1med, latermed = float(np.median(v1)), float(np.median(later))
                    drop = 100.0 * (latermed - v1med) / v1med
                    still = (res2['pct_per_decade'] if res2 else float('nan'))
                    if res2 and res2['ci_hi_pct'] < 0:
                        verdict = 'SMOOTH decay (still negative after dropping vol-1)'
                    elif res2 and res2['ci_lo_pct'] <= 0 <= res2['ci_hi_pct']:
                        verdict = 'ONE-TIME vol-1 break (no decay among vols 2-7)'
                    else:
                        verdict = 'inconclusive counter-test'
                    ct = (f'vol1 median {v1med:.0f} vs later {latermed:.0f} ({drop:+.0f}%); '
                          f'vols2-7 slope {still:+.1f}%/dec -> {verdict}')
                    print(f'  PWG compression counter-test: {ct}')
                slope_rows.append({'dict': did, 'volume': 'YEAR_SLOPE', 'year': '',
                                   'n_entries': res['n'],
                                   'mean_chars': f'{res["pct_per_decade"]:+.1f}%/decade',
                                   'median_chars': f'CI[{res["ci_lo_pct"]:+.1f},{res["ci_hi_pct"]:+.1f}]% '
                                                   f'p={res["p"]:.1e} {sign}; counter-test: {ct}',
                                   'date_quality': 'exact'})
        else:
            # best-effort: no within-work per-year map -> cannot regress on real time.
            sizes = np.array([c for _, _, c in entries])
            print(f'  {did}: {N:,} entries, date_quality={quality} '
                  f'(span {span[0]}-{span[1]}) — no per-fascicule year map; '
                  f'real-time regression NOT possible, reporting overall only')
            rows.append({'dict': did, 'volume': '', 'year': f'{span[0]}-{span[1]}',
                         'n_entries': N, 'mean_chars': f'{sizes.mean():.0f}',
                         'median_chars': f'{np.median(sizes):.0f}', 'date_quality': quality})
            slope_rows.append({'dict': did, 'volume': 'YEAR_SLOPE', 'year': '',
                               'n_entries': N, 'mean_chars': 'n/a',
                               'median_chars': f'insufficient date granularity ({quality}); '
                                               f'use H1416 alphabetical-position decay instead',
                               'date_quality': quality})

    all_rows = rows + slope_rows
    cols = ['dict', 'volume', 'year', 'n_entries', 'mean_chars', 'median_chars', 'date_quality']
    lines = ['\t'.join(cols)] + ['\t'.join(str(r.get(c, '')) for c in cols) for r in all_rows]
    body = '\n'.join(lines) + '\n'
    (la.OUT / 'entry_size_by_year.tsv').write_text(body, encoding='utf-8')
    (la.SRC_OUT / 'entry_size_by_year.tsv').write_text(body, encoding='utf-8')
    print(f'\n  wrote {la.OUT / "entry_size_by_year.tsv"} ({len(all_rows)} rows) [+ mirror]')
    print('DONE.')

if __name__ == '__main__':
    main()
