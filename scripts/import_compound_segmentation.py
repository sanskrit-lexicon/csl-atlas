"""
import_compound_segmentation.py  — H1423 Wave A (import-once, networked/model step)

Segments a stratified per-letter sample of headwords from every in-scope dict
via the Dharmamitra ByT5 model (local HF, `S ` segmentation prefix — the pypi
`unsandhied` API mangles isolated headwords, so local only), and writes a
committed snapshot. Normal builds never call the model — compound_share.py reads
this JSON. Model output is review EVIDENCE only (house rule).

Usage:
  python scripts/import_compound_segmentation.py --source local [--per-letter 300]
Writes: data/dharmamitra/compound_segmentation_sample.json
"""
import sys, json, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'lib'))
import letter_anatomy as la
import dharmamitra_infer as dm
from dict_sample import stratified_sample

OUT = la.ATLAS / 'data' / 'dharmamitra' / 'compound_segmentation_sample.json'
OUT.parent.mkdir(parents=True, exist_ok=True)

# in-scope dicts; MW/GRA carry the dash convention = compound ground-truth for calibration
SCOPE = ['MW', 'AP', 'PWG', 'PWK', 'SKD', 'VCP', 'GRA']
DASH_DICTS = {'MW', 'GRA'}
LOCAL_PREFIX = 'S '   # segmentation task prefix
DASH = ('—', '-')   # em-dash, hyphen


def seg_count(s):
    return len([t for t in (s or '').replace('_', ' ').split() if t])


def dedash(hw):
    for d in DASH:
        hw = hw.replace(d, '')
    return hw


def main():
    ap = dm.add_common_args(argparse.ArgumentParser(description=__doc__))
    ap.add_argument('--per-letter', type=int, default=300)
    args = ap.parse_args()
    if args.source != 'local':
        print('NOTE: forcing --source local (pypi unsandhied mangles isolated headwords).')
        args.source = 'local'

    # build the stratified sample across all scope dicts, from key2 (carries the dash
    # convention where present); the splitter surface is the de-dashed SLP1 form, and
    # dash-presence is the compound ground-truth for MW/GRA.
    rows = []           # (rowkey, surface_slp1)
    meta = []           # parallel [(did, letter, key2_original, had_dash)]
    seen_keys = set()
    for did in SCOPE:
        hw_list = la.read_hw_list(did, 2) or la.read_hw_list(did, 1)
        if not hw_list:
            print(f'  !! no headword list for {did}'); continue
        # stratify on the de-dashed surface's initial letter
        samp = stratified_sample(hw_list, lambda h: la.base_letter(dedash(h)),
                                 per_letter=args.per_letter)
        for lb, hw in samp:
            surface = dedash(hw)
            rowkey = f'{did}|{hw}'
            if rowkey in seen_keys:
                continue
            seen_keys.add(rowkey)
            had_dash = any(d in hw for d in DASH) if did in DASH_DICTS else None
            rows.append((rowkey, surface))
            meta.append((did, lb, hw, had_dash))
        print(f'  {did}: sampled {len([m for m in meta if m[0]==did])} headwords'
              f'{" (dash-truth)" if did in DASH_DICTS else ""}')
    print(f'Total sample: {len(rows)} headwords -> ByT5 segmentation (local)...')

    raw_by_key, extra = dm.run(rows, pypi_mode='unsandhied', local_prefix=LOCAL_PREFIX, args=args)

    out_rows = []
    for (did, lb, hw, had_dash), (rowkey, surface) in zip(meta, rows):
        seg = raw_by_key.get(rowkey, '')
        n = seg_count(seg)
        out_rows.append({'dict': did, 'letter': lb, 'key2': hw, 'surface': surface,
                         'had_dash': had_dash, 'segmentation': seg, 'n_segments': n})

    doc = {
        'model': dm.HF_MODEL_ID,
        'revision': getattr(args, 'revision', None),
        'task': 'segmentation (local prefix "S ")',
        'license': 'CC-BY-SA-4.0',
        'note': 'model prediction — review EVIDENCE only; is_compound := n_segments >= 2',
        'per_letter': args.per_letter,
        'n': len(out_rows),
        'rows': out_rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'wrote {OUT} ({len(out_rows)} rows)')


if __name__ == '__main__':
    main()
