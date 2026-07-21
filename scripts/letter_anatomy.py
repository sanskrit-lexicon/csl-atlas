"""
letter_anatomy.py  — H1416

Per-letter anatomy of the Sanskrit lexicon (samasa share + upasarga profile +
entry-size distribution) and the SKD/VCP "funding-decay" test.

Answers four questions (see reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md):
  Q1  samasa share per initial letter          (dash-marked key2; MW/GRA only)
  Q2  upasarga profile per initial letter       (surface longest-prefix on key1)
  Q3  entry-size distribution per initial letter (csl-orig entry bodies)
  Q4  entry-size decay vs alphabetical position  (letter fixed-effects regression)

Reads:
  headword lists : SanskritLexicography/HeadwordLists/now-2026/<DICT>-unique-key{1,2}-*.txt
  entry bodies   : csl-orig/v02/<slug>/<slug>.txt        (<L>..<LEND>, <k1>/<k2>)
  PD entry bodies: SanskritSpellCheck/external_src/pd/pd.txt

Writes (into data/pd/):
  letter_anatomy.tsv            one row per (dict x letter)
  entry_size_by_position.tsv    per dict: position-bin -> mean size + fitted FE slope/CI
  letter_anatomy_stats.json     machine-readable summary incl. Q4 regression verdicts

Windows-safe: utf-8 stdout, streaming CLI reads, no BOM writes.
"""
import sys, re, json, glob, math
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
from scipy import stats as sps

# ---------------------------------------------------------------- paths
HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent
GITHUB = ATLAS.parent
CSL_ORIG = GITHUB / 'csl-orig' / 'v02'
HW_DIR = GITHUB / 'SanskritLexicography' / 'HeadwordLists' / 'now-2026'
PD_TXT = GITHUB / 'SanskritSpellCheck' / 'external_src' / 'pd' / 'pd.txt'
OUT = ATLAS / 'data' / 'pd'
OUT.mkdir(parents=True, exist_ok=True)
SRC_OUT = ATLAS / 'src' / 'data' / 'pd'   # page-consumable mirror for Observable
SRC_OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- dict config
# id -> (headword-list prefix or None, csl-orig slug or path, label, has_dash_convention)
DICTS = [
    # id      hw-prefix   csl-slug   label                              dash
    ('MW',  'MW',       'mw',      'Monier-Williams 1899',            True),
    ('AP',  'AP',       'ap90',    'Apte 1890',                       False),
    ('PWG', 'PWG',      'pwg',     'Boehtlingk-Roth (grosse) 1855-75',False),
    ('PWK', 'PWK',      'pwkvn',   'Boehtlingk (kuerzere) 1879-89',   False),
    ('SKD', 'SKD',      'skd',     'Sabdakalpadruma 1886',            False),
    ('VCP', 'VCP',      'vcp',     'Vacaspatyam 1873-84',             False),
    ('GRA', 'GRA',      'gra',     'Grassmann (Rig-Veda) 1873',       True),
    ('PD',  None,       'PD',      'Petersburg Dictionary (in prog.)',False),
]

# ---------------------------------------------------------------- upasargas (SLP1 surface)
# canonical label -> list of surface prefix variants (longest-match, min 2-char stem left)
UPASARGAS = [
    ('pra',      ['pra']),
    ('parA',     ['parA']),
    ('apa',      ['apa']),
    ('sam',      ['sam', 'saM']),
    ('anu',      ['anu']),
    ('ava',      ['ava']),
    ('nis/nir',  ['nis', 'nir', 'niz', 'niH', 'niS']),
    ('dus/dur',  ['dus', 'dur', 'duz', 'duH', 'duS']),
    ('vi',       ['vi']),
    ('A',        ['A']),
    ('ni',       ['ni']),
    ('aDi',      ['aDi']),
    ('api',      ['api']),
    ('ati',      ['ati']),
    ('su',       ['su']),
    ('ud',       ['ud', 'ut']),
    ('aBi',      ['aBi']),
    ('prati',    ['prati']),
    ('pari',     ['pari']),
    ('upa',      ['upa']),
]
# flat (variant, label) sorted longest-first so 'prati' wins over 'pra', 'parA' over ...
_VARIANTS = sorted(
    ((v, lab) for lab, vs in UPASARGAS for v in vs),
    key=lambda t: -len(t[0]),
)

def classify_upasarga(hw):
    """Return canonical upasarga label if hw surface-starts with one (>=2 stem chars left)."""
    for v, lab in _VARIANTS:
        if hw.startswith(v) and len(hw) - len(v) >= 2:
            return lab
    return None

# ---------------------------------------------------------------- initial-letter buckets
# SLP1 first char -> base letter (merge long/short vowel pairs)
VOWEL_MERGE = {'A': 'a', 'I': 'i', 'U': 'u', 'F': 'f', 'X': 'x'}
# canonical alphabetical order of SLP1 base letters (traditional varnamala order)
ALPHA_ORDER = ['a', 'i', 'u', 'f', 'x', 'e', 'E', 'o', 'O',
               'k', 'K', 'g', 'G', 'N',
               'c', 'C', 'j', 'J', 'Y',
               'w', 'W', 'q', 'Q', 'R',
               't', 'T', 'd', 'D', 'n',
               'p', 'P', 'b', 'B', 'm',
               'y', 'r', 'l', 'v', 'S', 'z', 's', 'h', 'L']
ALPHA_RANK = {c: i for i, c in enumerate(ALPHA_ORDER)}
# IAST gloss for the report
IAST = {'a': 'a/ā', 'i': 'i/ī', 'u': 'u/ū', 'f': 'ṛ/ṝ', 'x': 'ḷ',
        'e': 'e', 'E': 'ai', 'o': 'o', 'O': 'au',
        'k': 'k', 'K': 'kh', 'g': 'g', 'G': 'gh', 'N': 'ṅ',
        'c': 'c', 'C': 'ch', 'j': 'j', 'J': 'jh', 'Y': 'ñ',
        'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
        't': 't', 'T': 'th', 'd': 'd', 'D': 'dh', 'n': 'n',
        'p': 'p', 'P': 'ph', 'b': 'b', 'B': 'bh', 'm': 'm',
        'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v', 'S': 'ś', 'z': 'ṣ',
        's': 's', 'h': 'h', 'L': 'ḻ'}

def base_letter(hw):
    """First SLP1 char of a headword -> base bucket, or None if unclassifiable."""
    if not hw:
        return None
    c = hw[0]
    c = VOWEL_MERGE.get(c, c)
    return c if c in ALPHA_RANK else None

# ---------------------------------------------------------------- headword lists (Q1/Q2)
def read_hw_list(prefix, key):
    """Return list of headwords from HeadwordLists/now-2026/<prefix>-unique-key<key>-*.txt."""
    hits = sorted(glob.glob(str(HW_DIR / f'{prefix}-unique-key{key}-*.txt')))
    if not hits:
        return None
    p = Path(hits[0])
    b = p.read_bytes()
    if b[:3] == b'\xef\xbb\xbf':
        b = b[3:]
    return [ln.strip() for ln in b.decode('utf-8', 'replace').splitlines() if ln.strip()]

# ---------------------------------------------------------------- entry bodies (Q3/Q4)
L_BLOCK = re.compile(r'<L>(.*?)<LEND>', re.DOTALL)
K1K2 = re.compile(r'<k1>(.*?)<k2>(.*?)(?:<|$)')
TAG = re.compile(r'<[^>]+>')
BRACE = re.compile(r'\{[#%@]|[#%@]\}|[{}⟨⟩〈〉]')
SANSKRIT_SPAN = re.compile(r'<s>|\{#')

def parse_entries(txt_path):
    """Yield (k1, body_chars, s_tokens) per <L>..<LEND> block, in file order."""
    b = txt_path.read_bytes()
    if b[:3] == b'\xef\xbb\xbf':
        b = b[3:]
    text = b.decode('utf-8', 'replace')
    for m in L_BLOCK.finditer(text):
        block = m.group(1)
        nl = block.find('\n')
        header = block if nl < 0 else block[:nl]
        body = '' if nl < 0 else block[nl + 1:]
        km = K1K2.search(header)
        k1 = km.group(1) if km else ''
        # tag-stripped body length (definition-text proxy, consistent within a dict)
        clean = BRACE.sub('', TAG.sub('', body))
        clean = re.sub(r'\s+', ' ', clean).strip()
        s_tokens = len(SANSKRIT_SPAN.findall(body))
        yield k1, len(clean), s_tokens

# ---------------------------------------------------------------- Q4 fixed-effects regression
def _within_ols(xc, yc, n_groups):
    """Within-transformed OLS slope + 95% CI + t/p. Arrays already letter-centred."""
    sxx = float((xc * xc).sum())
    if sxx == 0:
        return None
    n = len(yc)
    slope = float((xc * yc).sum() / sxx)
    resid = yc - slope * xc
    df = n - n_groups - 1            # G letter FEs + 1 slope
    s2 = float((resid * resid).sum() / df) if df > 0 else float('nan')
    se = math.sqrt(s2 / sxx) if s2 == s2 else float('nan')
    tcrit = float(sps.t.ppf(0.975, df)) if df > 0 else float('nan')
    tstat = slope / se if se else float('nan')
    pval = float(2 * sps.t.sf(abs(tstat), df)) if df > 0 else float('nan')
    return {'slope': slope, 'ci_lo': slope - tcrit * se, 'ci_hi': slope + tcrit * se,
            'se': se, 't': tstat, 'p': pval}


def robust_decay(letters, positions, sizes, min_n=10):
    """Robust (outlier-immune) funding-decay test: per-letter Spearman(position, size),
    aggregated across letters.

    Each initial letter is analysed on its own — so the letter-composition confound
    (Q3: later letters host shorter words) is removed by construction — and the
    rank-based rho is immune to the handful of gigantic encyclopedic articles that
    wreck the parametric estimate for SKD/VCP (VCP max entry = 310,090 chars vs
    median 112). Aggregation: Fisher-z weighted by (n_g - 3); combined rho + 95% CI,
    plus a sign test on how many letters show a negative slope. This is the ARBITER
    where the parametric FE is unstable.
    """
    letters = np.asarray(letters)
    x = np.asarray(positions, float)
    y = np.asarray(sizes, float)
    per = []   # (letter, n_g, rho_g)
    for g in np.unique(letters):
        idx = letters == g
        n_g = int(idx.sum())
        if n_g < min_n:
            continue
        rho, _ = sps.spearmanr(x[idx], y[idx])
        if rho != rho:      # nan (no size variance)
            continue
        per.append((str(g), n_g, float(rho)))
    if len(per) < 3:
        return None
    zs = np.array([math.atanh(min(max(r, -0.999999), 0.999999)) for _, _, r in per])
    w = np.array([n - 3 for _, n, _ in per], float)
    zbar = float((w * zs).sum() / w.sum())
    se = math.sqrt(1.0 / w.sum())
    zlo, zhi = zbar - 1.96 * se, zbar + 1.96 * se
    rho_comb = math.tanh(zbar)
    Z = zbar / se
    p = float(2 * sps.norm.sf(abs(Z)))
    neg = sum(1 for _, _, r in per if r < 0)
    m = len(per)
    sign_p = float(sps.binomtest(neg, m, 0.5).pvalue)
    # verdict from combined CI (rho scale)
    rlo, rhi = math.tanh(zlo), math.tanh(zhi)
    if rhi < 0:
        verdict = 'DECAY'
    elif rlo > 0:
        verdict = 'GROWTH'
    else:
        verdict = 'inconclusive'
    return {
        'rho_combined': rho_comb, 'rho_ci_lo': rlo, 'rho_ci_hi': rhi, 'p': p,
        'n_letters': m, 'neg_letters': neg, 'sign_test_p': sign_p,
        'verdict': verdict,
        'per_letter': [{'letter': g, 'n': n, 'rho': round(r, 3)} for g, n, r in per],
    }


def fe_regression(letters, positions, sizes):
    """Within-letter (fixed-effects) OLS of entry size ~ position + C(letter).

    Primary DV is log1p(chars) — robust to the heavy right tail of encyclopedic
    (SKD/VCP) entries; the log slope is ~proportional change per full 0->1 alphabet
    traversal. Raw-char FE slope and the naive (no-FE, confounded) slope are kept
    for contrast. A significant negative slope after letter FE is the funding-decay
    signal; the alphabet's own size variation is partialled out by the FE.

    NOTE: even in log, this parametric estimator remains sensitive to VCP/SKD's
    extreme outliers (a few 100k+ char articles) -> use robust_decay() as the arbiter.
    """
    letters = np.asarray(letters)
    x = np.asarray(positions, float)
    y = np.asarray(sizes, float)
    ylog = np.log1p(y)
    n = len(y)
    uniq = np.unique(letters)
    # within-transform (subtract per-letter means) for x, raw y, log y
    xc = np.empty(n); yc = np.empty(n); ylc = np.empty(n)
    for g in uniq:
        idx = letters == g
        xc[idx] = x[idx] - x[idx].mean()
        yc[idx] = y[idx] - y[idx].mean()
        ylc[idx] = ylog[idx] - ylog[idx].mean()
    raw = _within_ols(xc, yc, len(uniq))
    log = _within_ols(xc, ylc, len(uniq))
    if raw is None or log is None:
        return None
    # naive raw slope (confounded: no letter FE)
    xn = x - x.mean(); yn = y - y.mean()
    naive = float((xn * yn).sum() / (xn * xn).sum())
    rho, rho_p = sps.spearmanr(xc, ylc)
    # verdict from the robust log FE CI
    lo, hi = log['ci_lo'], log['ci_hi']
    if hi < 0:
        verdict = 'DECAY'
    elif lo > 0:
        verdict = 'GROWTH'
    else:
        verdict = 'inconclusive'
    return {
        'n': n, 'n_letters': int(len(uniq)),
        # robust log-scale (primary)
        'log_slope': log['slope'], 'log_ci_lo': lo, 'log_ci_hi': hi,
        'log_p': log['p'],
        'pct_change_per_traversal': 100.0 * (math.exp(log['slope']) - 1.0),
        # raw-char scale (secondary)
        'fe_slope': raw['slope'], 'fe_ci_lo': raw['ci_lo'], 'fe_ci_hi': raw['ci_hi'],
        'fe_p': raw['p'],
        'naive_slope': naive,
        'spearman_rho': float(rho), 'spearman_p': float(rho_p),
        'verdict': verdict,
    }

# ---------------------------------------------------------------- main
def main():
    anatomy_rows = []          # dict x letter
    by_position_rows = []      # dict x position-bin
    q4 = {}                    # dict -> regression result
    per_dict_meta = {}

    for did, hwpref, slug, label, has_dash in DICTS:
        print(f'\n=== {did} — {label} ===')

        # ---- Q1/Q2 from headword lists (or from PD entries for PD) ----
        if hwpref is not None:
            key1 = read_hw_list(hwpref, 1)
            key2 = read_hw_list(hwpref, 2)
        else:
            key1 = key2 = None   # PD handled from entries below

        # ---- entry bodies from csl-orig (or PD external) ----
        if slug == 'PD':
            txt_path = PD_TXT
        else:
            txt_path = CSL_ORIG / slug / f'{slug}.txt'
        entries = list(parse_entries(txt_path)) if txt_path.exists() else []
        if not txt_path.exists():
            print(f'  !! entry text missing: {txt_path}')

        # For PD, synthesise headword lists (dedup by k1) from entries
        if hwpref is None and entries:
            seen = []
            s = set()
            for k1, _, _ in entries:
                if k1 and k1 not in s:
                    s.add(k1); seen.append(k1)
            key1 = seen
            key2 = None   # PD has no dash convention

        # ---- bucket headwords by letter (Q1/Q2) ----
        # Q1 compound share: fraction of key2 with a dash joint (em-dash U+2014 or hyphen)
        q1_by_letter = {}    # letter -> [n_total, n_dashed]
        if key2 is not None and has_dash:
            for hw in key2:
                lb = base_letter(hw)
                if lb is None:
                    continue
                d = q1_by_letter.setdefault(lb, [0, 0])
                d[0] += 1
                if ('—' in hw) or ('-' in hw):
                    d[1] += 1

        # Q2 upasarga: on key1 (SLP1)
        q2_by_letter = {}    # letter -> {upasarga_label: count}
        n_hw_by_letter = {}  # letter -> n headwords (from key1)
        if key1 is not None:
            for hw in key1:
                lb = base_letter(hw)
                if lb is None:
                    continue
                n_hw_by_letter[lb] = n_hw_by_letter.get(lb, 0) + 1
                lab = classify_upasarga(hw)
                if lab:
                    d = q2_by_letter.setdefault(lb, {})
                    d[lab] = d.get(lab, 0) + 1

        # ---- Q3 entry-size per letter + collect regression arrays (Q4) ----
        letters_arr, pos_arr, size_arr = [], [], []
        size_by_letter = {}    # letter -> list of body_chars
        N = len(entries)
        for i, (k1, chars, stoks) in enumerate(entries):
            lb = base_letter(k1)
            if lb is None:
                continue
            size_by_letter.setdefault(lb, []).append(chars)
            letters_arr.append(lb)
            pos_arr.append(i / (N - 1) if N > 1 else 0.0)
            size_arr.append(chars)

        # ---- assemble anatomy rows (union of letters seen) ----
        letters_seen = set(n_hw_by_letter) | set(size_by_letter) | set(q1_by_letter)
        for lb in sorted(letters_seen, key=lambda c: ALPHA_RANK.get(c, 999)):
            n_hw = n_hw_by_letter.get(lb, 0)
            # Q1
            if lb in q1_by_letter and q1_by_letter[lb][0] > 0:
                tot, dsh = q1_by_letter[lb]
                pct_comp = 100.0 * dsh / tot
            else:
                pct_comp = ''
            # Q2 top-5 upasargas
            ups = q2_by_letter.get(lb, {})
            top5 = sorted(ups.items(), key=lambda kv: -kv[1])[:5]
            denom = n_hw if n_hw else 1
            top5_str = '; '.join(f'{lab}:{c}({100.0*c/denom:.1f}%)' for lab, c in top5)
            n_ups = sum(ups.values())
            # Q3
            sizes = size_by_letter.get(lb, [])
            if sizes:
                arr = np.array(sizes)
                mean_c = float(arr.mean()); med_c = float(np.median(arr)); n_entries = len(arr)
            else:
                mean_c = med_c = ''; n_entries = 0
            anatomy_rows.append({
                'dict': did, 'letter_slp1': lb, 'letter_iast': IAST.get(lb, lb),
                'alpha_rank': ALPHA_RANK.get(lb, ''),
                'n_headwords': n_hw, 'n_entries': n_entries,
                'pct_compound': (f'{pct_comp:.1f}' if pct_comp != '' else ''),
                'n_upasarga_initial': n_ups,
                'pct_upasarga': (f'{100.0*n_ups/n_hw:.1f}' if n_hw else ''),
                'top5_upasargas': top5_str,
                'mean_entry_chars': (f'{mean_c:.0f}' if mean_c != '' else ''),
                'median_entry_chars': (f'{med_c:.0f}' if med_c != '' else ''),
            })

        # ---- Q4 regression ----
        if len(size_arr) >= 50 and len(set(letters_arr)) >= 3:
            res = fe_regression(letters_arr, pos_arr, size_arr)
            rob = robust_decay(letters_arr, pos_arr, size_arr)
            if res is not None:
                res['robust'] = rob
            q4[did] = res
            if res and rob:
                print(f'  Q4 ROBUST rho={rob["rho_combined"]:+.3f} '
                      f'[{rob["rho_ci_lo"]:+.3f},{rob["rho_ci_hi"]:+.3f}] '
                      f'neg={rob["neg_letters"]}/{rob["n_letters"]} (sign p={rob["sign_test_p"]:.1e}) '
                      f'-> {rob["verdict"]}   '
                      f'| parametric log-FE={res["log_slope"]:+.3f}'
                      f'[{res["log_ci_lo"]:+.3f},{res["log_ci_hi"]:+.3f}] '
                      f'naive-raw={res["naive_slope"]:+.0f}  n={res["n"]:,}')
            # position bins (deciles) for the by-position TSV
            x = np.array(pos_arr); y = np.array(size_arr)
            for k in range(10):
                m = (x >= k / 10) & (x < (k + 1) / 10 if k < 9 else x <= 1.0)
                if m.any():
                    by_position_rows.append({
                        'dict': did, 'position_decile': k + 1,
                        'n': int(m.sum()),
                        'mean_entry_chars': f'{float(y[m].mean()):.0f}',
                        'median_entry_chars': f'{float(np.median(y[m])):.0f}',
                    })

        per_dict_meta[did] = {
            'label': label, 'has_dash': has_dash,
            'n_headwords': (len(key1) if key1 else 0),
            'n_entries': N,
            'entry_text': str(txt_path).replace('\\', '/'),
        }

    # ---------------------------------------------------------------- write TSVs
    def write_tsv(path, rows, cols):
        lines = ['\t'.join(cols)]
        for r in rows:
            lines.append('\t'.join(str(r.get(c, '')) for c in cols))
        body = '\n'.join(lines) + '\n'
        path.write_text(body, encoding='utf-8')
        (SRC_OUT / path.name).write_text(body, encoding='utf-8')   # mirror for the site
        print(f'  wrote {path}  ({len(rows)} rows)  [+ src/data/pd mirror]')

    write_tsv(OUT / 'letter_anatomy.tsv', anatomy_rows,
              ['dict', 'letter_slp1', 'letter_iast', 'alpha_rank', 'n_headwords',
               'n_entries', 'pct_compound', 'n_upasarga_initial', 'pct_upasarga',
               'top5_upasargas', 'mean_entry_chars', 'median_entry_chars'])

    # by_position: append FE slope/CI as trailing rows per dict
    for did, res in q4.items():
        if res:
            rob = res.get('robust') or {}
            by_position_rows.append({
                'dict': did, 'position_decile': 'DECAY_TEST',
                'n': res['n'],
                'mean_entry_chars': f'robust_rho={rob.get("rho_combined", float("nan")):+.3f}',
                'median_entry_chars': f'rhoCI[{rob.get("rho_ci_lo", float("nan")):+.3f},'
                                      f'{rob.get("rho_ci_hi", float("nan")):+.3f}] '
                                      f'neg={rob.get("neg_letters","?")}/{rob.get("n_letters","?")} '
                                      f'| logFE={res["log_slope"]:+.3f}'
                                      f'[{res["log_ci_lo"]:+.3f},{res["log_ci_hi"]:+.3f}] '
                                      f'VERDICT={rob.get("verdict","?")}',
            })
    write_tsv(OUT / 'entry_size_by_position.tsv', by_position_rows,
              ['dict', 'position_decile', 'n', 'mean_entry_chars', 'median_entry_chars'])

    stats = {
        'handoff': 'H1416',
        'generator': 'scripts/letter_anatomy.py',
        'model': 'Opus 4.8 (claude-opus-4-8)',
        'dicts': per_dict_meta,
        'q4_regression': q4,
        'upasarga_method': 'surface longest-prefix match on key1 (SLP1), >=2 stem chars; '
                           'over-counts A/vi/ni/su (common stem-initials); privative a-/an- '
                           'not surface-separable and reported via Q1 dash-share for a.',
        'q1_scope': 'dash-marked samasa share meaningful only for MW (71.6% dashed) and '
                    'GRA (36.6%); AP/PWG/PWK/SKD/VCP/VEI have ~0 dash marks.',
    }
    stats_body = json.dumps(stats, indent=2, ensure_ascii=False)
    (OUT / 'letter_anatomy_stats.json').write_text(stats_body, encoding='utf-8')
    (SRC_OUT / 'letter_anatomy_stats.json').write_text(stats_body, encoding='utf-8')
    print(f'\n  wrote {OUT / "letter_anatomy_stats.json"}  [+ src/data/pd mirror]')
    print('\nDONE.')


if __name__ == '__main__':
    main()
