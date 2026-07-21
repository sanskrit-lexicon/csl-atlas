"""
density_fingerprint.py  — H1423 Wave D

A cross-dictionary "how deep is each dictionary" fingerprint. Three uniformly
comparable per-entry density signals (per-dict sense markers are NOT cross-dict
comparable — see the report — so we use a structural-tag proxy instead of a
dict-specific sense count):

  chars_per_entry        tag-stripped body length (H1416 measure)
  sanskrit_spans_per_entry   count of <s>…</s> (MW-family) or {#…#} (others) —
                             a proxy for Sanskrit-token / citation density
  markup_tags_per_entry  total <…> structural tags per entry — structural density

Reports MEDIAN alongside mean everywhere (SKD/VCP are heavy-tailed: single
articles > 100k chars). Dict-level rows + per-letter rows.

Writes: data/pd/density_fingerprint.tsv (+ src/data/pd mirror). Deterministic.
"""
import sys, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import letter_anatomy as la

L_BLOCK = re.compile(r'<L>(.*?)<LEND>', re.DOTALL)
K1 = re.compile(r'<k1>(.*?)(?:<|$)')
TAG = re.compile(r'<[^>]+>')
S_SPAN = re.compile(r'<s>')
BRACE_SPAN = re.compile(r'\{#')

# in-scope: MW/AP/PWG/PWK primary + SKD/VCP contrast
SCOPE = [('MW', 'mw'), ('AP', 'ap90'), ('PWG', 'pwg'),
         ('PWK', 'pwkvn'), ('SKD', 'skd'), ('VCP', 'vcp')]

def parse(txt_path):
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
        k1 = km.group(1) if km else ''
        clean = la.BRACE.sub('', TAG.sub('', body))
        clean = re.sub(r'\s+', ' ', clean).strip()
        n_chars = len(clean)
        n_spans = len(S_SPAN.findall(body)) + len(BRACE_SPAN.findall(body))
        n_tags = len(TAG.findall(body))
        yield k1, n_chars, n_spans, n_tags

def stats(arr):
    a = np.asarray(arr, float)
    return (f'{a.mean():.1f}', f'{np.median(a):.1f}')

def main():
    rows = []
    print('=== Wave D — cross-dictionary density fingerprint ===')
    for did, slug in SCOPE:
        path = la.CSL_ORIG / slug / f'{slug}.txt'
        if not path.exists():
            print(f'  !! missing {path}'); continue
        chars, spans, tags, letters = [], [], [], []
        for k1, nc, ns, nt in parse(path):
            lb = la.base_letter(k1)
            chars.append(nc); spans.append(ns); tags.append(nt); letters.append(lb)
        chars = np.array(chars); spans = np.array(spans); tags = np.array(tags)
        letters = np.array(letters)
        cm, cmed = stats(chars); sm, smed = stats(spans); tm, tmed = stats(tags)
        print(f'  {did:4} n={len(chars):>7,}  chars mean/med={cm}/{cmed}  '
              f'spans={sm}/{smed}  tags={tm}/{tmed}')
        rows.append({'dict': did, 'letter_slp1': 'ALL', 'letter_iast': '',
                     'n_entries': len(chars),
                     'chars_mean': cm, 'chars_median': cmed,
                     'sanskrit_spans_mean': sm, 'sanskrit_spans_median': smed,
                     'markup_tags_mean': tm, 'markup_tags_median': tmed})
        # per-letter (chars only, the primary signal)
        for lb in sorted(set(x for x in letters if x is not None),
                         key=lambda c: la.ALPHA_RANK.get(c, 999)):
            mask = letters == lb
            csub = chars[mask]
            if len(csub) < 5:
                continue
            cm2, cmed2 = stats(csub)
            ssub_m, ssub_med = stats(spans[mask])
            tsub_m, tsub_med = stats(tags[mask])
            rows.append({'dict': did, 'letter_slp1': lb, 'letter_iast': la.IAST.get(lb, lb),
                         'n_entries': int(mask.sum()),
                         'chars_mean': cm2, 'chars_median': cmed2,
                         'sanskrit_spans_mean': ssub_m, 'sanskrit_spans_median': ssub_med,
                         'markup_tags_mean': tsub_m, 'markup_tags_median': tsub_med})

    cols = ['dict', 'letter_slp1', 'letter_iast', 'n_entries',
            'chars_mean', 'chars_median', 'sanskrit_spans_mean', 'sanskrit_spans_median',
            'markup_tags_mean', 'markup_tags_median']
    lines = ['\t'.join(cols)] + ['\t'.join(str(r.get(c, '')) for c in cols) for r in rows]
    body = '\n'.join(lines) + '\n'
    (la.OUT / 'density_fingerprint.tsv').write_text(body, encoding='utf-8')
    (la.SRC_OUT / 'density_fingerprint.tsv').write_text(body, encoding='utf-8')
    print(f'\n  wrote {la.OUT / "density_fingerprint.tsv"} ({len(rows)} rows) [+ mirror]')
    print('DONE.')

if __name__ == '__main__':
    main()
