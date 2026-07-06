#!/usr/bin/env python3
# Canonicalized <ls> citation graph: resolve each dict's raw abbreviations to a shared
# canonical text node using csl-guides/abbreviations.json (per-dict works/mixed keys).
#
# v2 (H213, 06-07-2026):
#   - MW non-text filter: MW reuses <ls> for grammatical/editorial markers (L.=lexicographers,
#     ibid., mn., Cat., A.=Active ...). These resolve to non-bibliographic "texts" and are
#     excluded from the citation graph via NONTEXT_NODES (reported separately, not silently dropped).
#   - Key-borrow: dicts with no abbreviation key of their own but a documented shared convention
#     borrow another dict's key (ap<-ap90 same author; sch,pwkvn<-pwg PW-Nachtrag tradition).
#   - Curated alias fold: the top author's-genitive / German-description PWG expansions
#     (MANU'S Gesetzbuch, PANINI'S acht Bucher ...) fold to their standard indological text name.
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

# --- dicts that borrow another dict's abbreviation key (no own key, but a documented
#     shared abbreviation convention). Justified + measured (resolved-% in the README):
#       ap    <- ap90  (both Apte; same abbreviation system)         83.7%
#       pwkvn <- pwg   (PW "Kürzere ... Nachträge", PW convention)   60.5%
#       sch   <- pwg   (Schmidt, Nachträge zum PW, PW convention)    44.6%
BORROW = {'ap': 'ap90', 'pwkvn': 'pwg', 'sch': 'pwg'}

# --- canonical nodes that are NOT bibliographic works. MW reuses <ls> for grammatical
#     voice/case markers, editorial reference markers, and the "lexicographers" (L.) tag.
#     Matched on the folded key of the canonical node; excluded from the citation graph
#     and counted separately (nontext) so the exclusion is auditable, not silent.
NONTEXT_NODES = {fold_key(x) for x in [
    'lexicographers', 'ibidem', 'masculine or neuter', 'catalogue or catalogues',
    'column', 'Active', 'Name', 'grammar', 'Introduction', 'edition', 'indeclinable',
]}
# 'ibidem or ...' is a long expansion — also drop any node whose fold starts with 'ibidem'.
NONTEXT_PREFIX = ('ibidem',)

# --- curated alias fold (hand-verified, not guessed): the highest-count author's-genitive
#     and German-description PWG/PW expansions -> their standard indological text name, so
#     they present as one clean node. Keyed on the folded canonical-node key; the target's
#     own fold key is what merges variants. Every mapping is a well-established identification.
CANON_ALIAS_RAW = {
    "PĀṆINI'S acht Bücher grammatischer Regeln": 'Aṣṭādhyāyī (Pāṇini)',
    "MANU'S Gesetzbuch": 'Manusmṛti',
    "YĀJÑAVALKYA'S Gesetzbuch": 'Yājñavalkyasmṛti',
    "HEMACANDRA'S ABHIDHĀNACINTĀMAṆI": 'Abhidhānacintāmaṇi',
    "HEMACANDRA'S ANEKĀRTHASAM̃GRAHA": 'Anekārthasaṃgraha',
    "VARĀHAMIHIRA'S BṚHATSAM̃HITĀ": 'Bṛhatsaṃhitā',
    "KĀTYĀYANA'S ŚRAUTASŪTRĀṆI": 'Kātyāyana-Śrautasūtra',
    "VOPADEVA'S Grammatik": 'Mugdhabodha (Vopadeva)',
    "ĀPASTAMBA'S DHARMASŪTRA": 'Āpastamba-Dharmasūtra',
    "KAUŚIKA'S SŪTRA zum ATHARVAVEDA": 'Kauśika-Sūtra',
    "ŚĀṄKHĀYANA'S ŚRAUTASŪTRĀṆI": 'Śāṅkhāyana-Śrautasūtra',
    "ĀŚVALĀYANA'S ŚRAUTASŪTRĀṆI in 12 Adhyāya": 'Āśvalāyana-Śrautasūtra',
    "ĀŚVALĀYANA'S GṚHYASŪTRĀṆI in 4 Adhyāya": 'Āśvalāyana-Gṛhyasūtra',
    "LĀṬYĀYANA'S SŪTRA zum SV": 'Lāṭyāyana-Śrautasūtra',
    "GAUTMA'S DHARMAŚĀSTRA": 'Gautama-Dharmasūtra',
    "WEBER'S Indische Studien": 'Indische Studien (Weber)',
    "WILSON'S Wörterbuch": 'Wilson (dictionary)',
    "YĀSKA'S NIRUKTA sammt den NIGHAṆṬAVA'S herausgegeben und erklärt von RUDOLPH ROTH": 'Nirukta (Yāska)',
    # title-synonymy folds (the same work under a second standard name) — high-confidence,
    # bounded set of the largest offenders; the long tail of title-synonymy is left as a
    # documented residual rather than guessed at.
    'Mānavadharmaśāstra': 'Manusmṛti',
    'ŚATAPATHABRĀHMAṆA': 'Śatapatha-Brāhmaṇa',
    'ATHARVAVEDASAM̃HITĀ': 'Atharvaveda',
    'RĀJANIRGHAṆṬA': 'Rājanighaṇṭu',
}
CANON_ALIAS = {fold_key(k): v for k, v in CANON_ALIAS_RAW.items()}

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
    if m:
        DICT_ABBR[code] = m
        DICT_MAXTOK[code] = max(len(a.split(' ')) for a in m)
        DICT_ABBR[code+'|ci'] = {a.casefold(): a for a in m}
# wire borrowed keys in for dicts without their own
for borrower, lender in BORROW.items():
    if borrower not in DICT_ABBR and lender in DICT_ABBR:
        DICT_ABBR[borrower] = DICT_ABBR[lender]
        DICT_ABBR[borrower+'|ci'] = DICT_ABBR[lender+'|ci']
        DICT_MAXTOK[borrower] = DICT_MAXTOK[lender]

ARTICLE = re.compile(r'^(the|die|der|das|den)\s+', re.I)
def canonical_node(expansion):
    # Cologne's "? [Cologne Addition]" is an unidentified-source placeholder, not a text.
    # Strip it (and its bare "?" marker); if nothing survives, the source stays UNRESOLVED
    # (caller treats an empty return as a non-match). A compound like
    # "Divyāvadāna ? [Cologne Addition]" recovers to "Divyāvadāna".
    e = re.sub(r'[\[{]\s*Cologne Addition\s*[\]}]', ' ', expansion).replace('?', ' ')
    e = re.sub(r'\s+', ' ', e).strip()
    if not e:
        return ''
    # canonical text name = expansion up to first editorial tail (. , ( — or " ed"/" nach"/" in ")
    e = re.split(r'[.,(]| ed\.| nach | in der | in the | im ', e)[0].strip()
    e = ARTICLE.sub('', e)   # drop a leading article ("The ŚATAPATHABRĀHMAṆA ..." -> "ŚATAPATHABRĀHMAṆA ...")
    e = re.sub(r'\s+',' ', e).strip(" .;:'")
    # empty here => the expansion was a pure placeholder / parenthetical editorial note
    # (e.g. "(A different Number of previous reference)") — not a text; leave UNRESOLVED.
    return e

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
            node = canonical_node(m[cand])
            if node:
                return cand, node
            continue   # matched a "? [Cologne Addition]" placeholder — try a shorter prefix
        cf = cand.casefold()
        if cf in ci:
            node = canonical_node(m[ci[cf]])
            if node:
                return ci[cf], node
            continue
    return None, None

def is_nontext(node):
    fk = fold_key(node)
    if fk in NONTEXT_NODES:
        return True
    return any(fk.startswith(p) for p in NONTEXT_PREFIX)

def alias(node):
    # apply the curated alias fold, if any, else return the node unchanged
    return CANON_ALIAS.get(fold_key(node), node)

# --- harvest ---
edges = defaultdict(Counter)      # dict -> Counter(canonical_node)
raw_total = Counter(); resolved = Counter(); nontext = Counter()
unresolved = defaultdict(Counter)
node_dicts = defaultdict(set)     # canonical_node -> set(dicts)
node_total = Counter()

DICTS = sorted({dc for dc in DICT_ABBR if '|ci' not in dc})
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
            if is_nontext(node):
                nontext[dc]+=1
                continue
            node = alias(node)
            resolved[dc]+=1
            edges[dc][node]+=1
            node_dicts[node].add(dc)
            node_total[node]+=1
        else:
            key = re.sub(r'<[^>]+>','',h); key=re.sub(r'\s+',' ',key).strip()[:30]
            unresolved[dc][key]+=1

# --- fold canonical nodes by diacritic/case-insensitive key ---
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

print("=== RESOLUTION COVERAGE (dicts with an abbreviation key; * = borrowed key) ===")
print(f"{'dict':7s} {'raw':>9s} {'nontext':>8s} {'resolved':>9s} {'%text':>7s} {'nodes':>6s}")
for dc in sorted(raw_total, key=lambda d:-raw_total[d]):
    r=resolved[dc]; t=raw_total[dc]; nt=nontext[dc]; denom=t-nt
    star='*' if dc in BORROW else ''
    print(f"{dc+star:7s} {t:9,d} {nt:8,d} {r:9,d} {100*r/denom if denom else 0:6.1f}% {len(edges[dc]):6d}")

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
with open(os.path.join(out,'ls_citation_edges.tsv'),'w',encoding='utf-8') as fh:
    fh.write("dict\tcanonical_text\tcount\n")
    for dc in sorted(f_edges):
        for fk,n in f_edges[dc].most_common():
            fh.write(f"{dc}\t{best_display(fk)}\t{n}\n")
with open(os.path.join(out,'ls_citation_nodes.tsv'),'w',encoding='utf-8') as fh:
    fh.write("canonical_text\ttotal_cites\tn_dicts\tvariant_forms\n")
    for fk,n in f_total.most_common():
        variants='; '.join(sorted(fold_forms[fk], key=lambda s:-fold_forms[fk][s])[:4])
        fh.write(f"{best_display(fk)}\t{n}\t{len(f_dicts[fk])}\t{variants}\n")
# top unresolved for QA
with open(os.path.join(out,'ls_citation_unresolved_top.tsv'),'w',encoding='utf-8') as fh:
    fh.write("dict\traw_key\tcount\n")
    for dc in sorted(unresolved):
        for k,n in unresolved[dc].most_common(40):
            fh.write(f"{dc}\t{k}\t{n}\n")
# non-text markers filtered from MW etc. (audit trail)
with open(os.path.join(out,'ls_citation_nontext_filtered.tsv'),'w',encoding='utf-8') as fh:
    fh.write("dict\tnontext_markers_filtered\n")
    for dc in sorted(nontext, key=lambda d:-nontext[d]):
        fh.write(f"{dc}\t{nontext[dc]}\n")
print("\n[wrote ls_citation_edges.tsv, ls_citation_nodes.tsv, ls_citation_unresolved_top.tsv, ls_citation_nontext_filtered.tsv]")
print(f"distinct canonical nodes: {len(node_total):,}  total resolved: {sum(resolved.values()):,}  nontext filtered: {sum(nontext.values()):,}")
