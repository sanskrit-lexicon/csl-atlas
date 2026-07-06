#!/usr/bin/env python3
# Canonicalized <ls> citation graph: resolve each dict's raw abbreviations to a shared
# canonical text node using csl-guides/abbreviations.json (per-dict works/mixed keys).
import os, re, sys, glob, json, unicodedata
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def fold_key(name):
    # diacritic- + case-insensitive merge key so MAHABHARATA == Mahābhārata
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^a-zA-Z]', '', s).lower()
    return s
# GitHub root = three levels up (data/citations/ -> csl-atlas -> GitHub root);
# override with env SIBLING_ROOT if the sibling layout differs.
ROOT = os.environ.get('SIBLING_ROOT') or os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..'))
LS = re.compile(r'<ls[^>]*>(.*?)</ls>', re.S)
ROMAN = re.compile(r'^[ivxlcdm]+[.,;:]?$', re.I)

# --- load per-dict abbreviation -> expansion maps ---
ab = json.load(open(os.path.join(ROOT,'csl-guides','src','data','abbreviations.json'),encoding='utf-8'))
def norm_abbr(s):
    s = re.sub(r'\s+',' ', s.strip())
    return s.rstrip(' .,;:')
DICT_ABBR = {}   # dict_code(lower) -> {norm_abbr: expansion}
DICT_MAXTOK = {}
for x in ab['dicts']:
    code = x['code'].lower()
    m = {}
    for src in (x.get('works') or []) + (x.get('mixed') or []):
        a = norm_abbr(src.get('abbr',''))
        if a: m.setdefault(a, src.get('expansion','').strip())
        # also a casefold key for fallback
    if m:
        DICT_ABBR[code] = m
        DICT_MAXTOK[code] = max(len(a.split(' ')) for a in m)
        # casefold index
        DICT_ABBR[code+'|ci'] = {a.casefold(): a for a in m}

def canonical_node(expansion):
    # canonical text name = expansion up to first editorial tail (. , ( — or " ed"/" nach"/" in ")
    e = re.split(r'[.,(]| ed\.| nach | in der | im ', expansion)[0].strip()
    e = re.sub(r'\s+',' ', e).strip(" .;:'")
    return e or expansion.strip()

def resolve(dc, content):
    m = DICT_ABBR.get(dc)
    if not m:
        return None, None
    c = re.sub(r'<[^>]+>','', content)
    c = re.sub(r'\s+',' ', c).strip()
    toks = c.split(' ')
    ci = DICT_ABBR.get(dc+'|ci', {})
    maxt = DICT_MAXTOK.get(dc, 3)
    for n in range(min(maxt, len(toks)), 0, -1):
        cand = norm_abbr(' '.join(toks[:n]))
        if not cand:
            continue
        if cand in m:
            return cand, canonical_node(m[cand])
        cf = cand.casefold()
        if cf in ci:
            return ci[cf], canonical_node(m[ci[cf]])
    return None, None

# --- harvest ---
edges = defaultdict(Counter)      # dict -> Counter(canonical_node)
raw_total = Counter(); resolved = Counter()
unresolved = defaultdict(Counter)
node_dicts = defaultdict(set)     # canonical_node -> set(dicts)
node_total = Counter()

for f in sorted(glob.glob(os.path.join(ROOT,'csl-orig','v02','*','*.txt'))):
    dc = os.path.basename(os.path.dirname(f))
    if dc not in DICT_ABBR:
        continue
    try: txt = open(f,encoding='utf-8').read()
    except Exception as e:
        sys.stderr.write(f"SKIP {f}: {type(e).__name__} {e}\n"); continue
    for h in LS.findall(txt):
        if not h.strip(): continue
        raw_total[dc]+=1
        ab_key, node = resolve(dc, h)
        if node:
            resolved[dc]+=1
            edges[dc][node]+=1
            node_dicts[node].add(dc)
            node_total[node]+=1
        else:
            key = re.sub(r'<[^>]+>','',h); key=re.sub(r'\s+',' ',key).strip()[:30]
            unresolved[dc][key]+=1

# --- fold canonical nodes by diacritic/case-insensitive key ---
fold_display = {}   # fold_key -> best display name (prefer Title-case, shortest)
fold_forms = defaultdict(Counter)
for node in list(node_total):
    fk = fold_key(node)
    if not fk: fk = node
    fold_forms[fk][node] += node_total[node]
def best_display(fk):
    # prefer a Title/mixed-case form over ALL-CAPS, then shortest
    cands = list(fold_forms[fk])
    cands.sort(key=lambda s:(s.isupper(), len(s)))
    return cands[0]
# rebuild folded aggregates
f_total = Counter(); f_dicts = defaultdict(set); f_edges = defaultdict(Counter)
for dc in edges:
    for node,n in edges[dc].items():
        fk = fold_key(node) or node
        f_edges[dc][fk]+=n; f_total[fk]+=n; f_dicts[fk].add(dc)

print("=== RESOLUTION COVERAGE (dicts with an abbreviation key) ===")
print(f"{'dict':6s} {'raw':>8s} {'resolved':>9s} {'%':>6s} {'nodes':>6s}")
for dc in sorted(raw_total, key=lambda d:-raw_total[d]):
    r=resolved[dc]; t=raw_total[dc]
    print(f"{dc:6s} {t:8,d} {r:9,d} {100*r/t if t else 0:5.1f}% {len(edges[dc]):6d}")

print("\n=== TOP 30 CANONICAL TEXTS ACROSS THE TRADITION (folded across dicts) ===")
print(f"{'cites':>9s} {'#dicts':>6s}  canonical text")
for fk,n in f_total.most_common(30):
    print(f"{n:9,d} {len(f_dicts[fk]):6d}  {best_display(fk)}")

print("\n=== PER-DICT TOP 6 CANONICAL TEXTS ===")
for dc in sorted(resolved, key=lambda d:-resolved[d]):
    top=edges[dc].most_common(6)
    print(f"{dc:6s} " + " · ".join(f"{s} {n:,}" for s,n in top))

# write artifacts (FOLDED canonical nodes)
out=os.path.dirname(__file__)
with open(os.path.join(out,'ls_canon_edges.tsv'),'w',encoding='utf-8') as fh:
    fh.write("dict\tcanonical_text\tcount\n")
    for dc in f_edges:
        for fk,n in f_edges[dc].most_common():
            fh.write(f"{dc}\t{best_display(fk)}\t{n}\n")
with open(os.path.join(out,'ls_canon_nodes.tsv'),'w',encoding='utf-8') as fh:
    fh.write("canonical_text\ttotal_cites\tn_dicts\tvariant_forms\n")
    for fk,n in f_total.most_common():
        variants='; '.join(sorted(fold_forms[fk], key=lambda s:-fold_forms[fk][s])[:4])
        fh.write(f"{best_display(fk)}\t{n}\t{len(f_dicts[fk])}\t{variants}\n")
# top unresolved for QA
with open(os.path.join(out,'ls_canon_unresolved_top.tsv'),'w',encoding='utf-8') as fh:
    fh.write("dict\traw_key\tcount\n")
    for dc in unresolved:
        for k,n in unresolved[dc].most_common(40):
            fh.write(f"{dc}\t{k}\t{n}\n")
print("\n[wrote ls_canon_edges.tsv, ls_canon_nodes.tsv, ls_canon_unresolved_top.tsv]")
print(f"distinct canonical nodes: {len(node_total):,}  total resolved: {sum(resolved.values()):,}")
