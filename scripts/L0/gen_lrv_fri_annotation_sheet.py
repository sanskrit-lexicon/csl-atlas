"""Generate the LRV/FRI Patel-convention annotation sheet (interactive HTML).

The convention fingerprint (data/L0/convention_fingerprint.csv) carries dims
1,3,5,6,7 from Patel 2016 gold for the 33 dicts Patel covers. LRV and FRI are
the only two *sourced* dicts NOT in Patel's set (KNA/KOW/AMAR have no reachable
source), so those five judgement-bound dims sit at "unknown" for them — which
leaves LRV/FRI loosely placed in the cladogram.

s2c_patel_evidence.py already computed the discriminating evidence (rates + real
headword examples) per (dict,dim); assigning the actual Patel option is the human
gate (design §12.3). This script turns that gate into a one-click interactive
sheet: M.G. confirms/overrides an evidence-based suggestion per item and exports
review/csl-atlas-lrv-fri-patel_l0dictset_decisions.json, which
apply_lrv_fri_annotation.py consumes.

Input : data/L0/lrv_fri_annotation_items.json  (evidence + Patel option taxonomy)
Output: review/csl-atlas-lrv-fri-patel_l0dictset_review.html  (gitignored personal
        artifact; named per the org sheet-naming convention — see
        Uprava/REVIEW_SHEETS_INDEX.md, FINDINGS.md §34)

Run from repo root:  python scripts/L0/gen_lrv_fri_annotation_sheet.py
"""

import os
import sys
import json
import html

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(REPO, "data", "L0")
FILLIN = os.path.join(DATA, "patel_fillin.csv")          # s2c evidence (rates + examples)
PATEL_GOLD = os.path.join(DATA, "patel2016_assignments.csv")  # option taxonomy per convention
ITEMS = os.path.join(DATA, "lrv_fri_annotation_items.json")   # emitted for inspection (not an input)
OUT_DIR = os.path.join(REPO, "review")
SHEET_ID = "csl-atlas-lrv-fri-patel_l0dictset"
OUT = os.path.join(OUT_DIR, SHEET_ID + "_review.html")
GATE_DICTS = ("LRV", "FRI")
GATE_DIMS = ("1", "3", "5", "6", "7")

# Evidence-based suggestions (pre-selected in the sheet; M.G. confirms/overrides).
# Keyed (dict, dim) -> {options:[patel option ids], rationale, mixed:bool}
SUGGEST = {
    ("LRV", 1): {"options": [], "mixed": True,
                 "rationale": "anusvāra-share 0.565 — genuinely mixed, no dominant form; needs the eye."},
    ("LRV", 3): {"options": ["3.1", "3.4"], "mixed": False,
                 "rationale": "bare -at (ajahat, adat) → 3.1; bare -vat/-mat (anAtmavat, arcizmat) → 3.4."},
    ("LRV", 5): {"options": [], "mixed": True,
                 "rationale": "both M-form and n/m-form roots attested (4+ each) — mixed; needs the eye."},
    ("LRV", 6): {"options": ["6.3"], "mixed": False,
                 "rationale": "nominative -ā dominant (314) vs ṛ-stem 37 vs -ar/-ṛ 3 → 6.3 (kartā)."},
    ("LRV", 7): {"options": ["7.1"], "mixed": False,
                 "rationale": "-vas/-yas forms (…kftvas, …Sravas; ativayas) → 7.1."},
    ("FRI", 1): {"options": ["1.2"], "mixed": False,
                 "rationale": "anusvāra-share 0.235 — homorganic dominant (751 vs 231) → 1.2."},
    ("FRI", 3): {"options": ["3.1", "3.4"], "mixed": False,
                 "rationale": "bare -at (Izat, jagat) → 3.1; bare -vat (aBItavat, tadvat) → 3.4 (no -mat attested)."},
    ("FRI", 5): {"options": [], "mixed": True,
                 "rationale": "both M-form and n/m-form roots attested (4+ each) — mixed; needs the eye."},
    ("FRI", 6): {"options": ["6.1"], "mixed": False,
                 "rationale": "-ar/-ṛ dominant (176) vs nom-ā 61 vs ṛ-stem 9; examples end -ar (attar, adAtar) → 6.1 (kartar)."},
    ("FRI", 7): {"options": ["7.1"], "mixed": False,
                 "rationale": "-vas/-yas forms (citraSravas; aByas) → 7.1."},
}


def esc(s):
    return html.escape(str(s), quote=True)


def build_items():
    """Assemble the 10 gate items straight from the s2c evidence + Patel taxonomy CSVs.

    No hand-maintained input file — the sheet is fully regenerable from committed data.
    """
    import csv
    opts = {}
    with open(PATEL_GOLD, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            opts.setdefault(r["convention"], []).append(
                {"option": r["option"], "definition": r["definition"],
                 "n_dicts": len(r["member_dicts"].split())})
    ev = {}
    with open(FILLIN, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["dict"] in GATE_DICTS and r["dim_id"] in GATE_DIMS:
                ev[(r["dict"], r["dim_id"])] = r
    items = []
    for d in GATE_DICTS:
        for dim in GATE_DIMS:
            r = ev[(d, dim)]
            items.append({"dict": d, "dim": int(dim), "dim_name": r["dim_name"],
                          "question": r["convention_question"], "evidence": r["evidence"],
                          "examples": r["examples"], "patel_options": opts[dim]})
    return items


def main():
    items = build_items()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(ITEMS, "w", encoding="utf-8") as f:  # emit for inspection only
        json.dump(items, f, ensure_ascii=False, indent=2)

    cards = []
    for it in items:
        d, dim = it["dict"], it["dim"]
        iid = f"{d}-dim{dim}"
        sug = SUGGEST.get((d, dim), {"options": [], "mixed": False, "rationale": ""})
        sug_set = set(sug["options"])

        opt_rows = []
        for o in it["patel_options"]:
            oid = o["option"]
            checked = "checked" if oid in sug_set else ""
            sug_tag = ' <span class="sug">◀ suggested</span>' if oid in sug_set else ""
            opt_rows.append(
                f'<label class="opt"><input type="checkbox" data-item="{esc(iid)}" '
                f'value="{esc(oid)}" {checked}> '
                f'<b>{esc(oid)}</b> — {esc(o["definition"])} '
                f'<span class="ndicts">[{o["n_dicts"]} dicts use this]</span>{sug_tag}</label>'
            )

        mixed_banner = (
            '<div class="mixed">⚠ evidence is mixed — no dominant form. Assign by eye or defer.</div>'
            if sug["mixed"] else ""
        )
        cards.append(f"""
<div class="card" id="card-{esc(iid)}" data-item="{esc(iid)}" data-dict="{esc(d)}" data-dim="{dim}">
  <div class="chead">
    <span class="tag">{esc(d)}</span>
    <span class="dim">dim {dim} — {esc(it['dim_name'])}</span>
    <span class="status" id="st-{esc(iid)}">● unset</span>
  </div>
  <div class="q">{esc(it['question'])}</div>
  <div class="ev"><b>Evidence:</b> {esc(it['evidence'])}</div>
  <div class="ex"><b>Examples:</b> <code>{esc(it['examples'])}</code></div>
  {mixed_banner}
  <div class="sugbox"><b>Suggested:</b> {esc(sug['rationale']) or '—'}</div>
  <div class="opts">{''.join(opt_rows)}</div>
  <div class="actions">
    <button class="defer" data-item="{esc(iid)}">⏸ defer (leave unknown)</button>
    <input class="note" data-item="{esc(iid)}" placeholder="note (optional)…">
  </div>
</div>""")

    tpl = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LRV / FRI Patel convention annotation</title>
<style>
 :root{font-family:-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.5}
 body{max-width:900px;margin:0 auto;padding:1rem;color:#1a1a1a;background:#fafafa}
 h1{font-size:1.35rem;margin:.2rem 0}
 .sub{color:#555;font-size:.9rem;margin-bottom:1rem}
 .bar{position:sticky;top:0;background:#fff;border:1px solid #ddd;border-radius:8px;
      padding:.6rem .9rem;display:flex;gap:1.2rem;align-items:center;z-index:10;
      box-shadow:0 2px 6px rgba(0,0,0,.06);flex-wrap:wrap}
 .bar b{font-size:1.05rem}
 .bar .dl{margin-left:auto}
 button{cursor:pointer;border:1px solid #bbb;border-radius:6px;padding:.4rem .7rem;
        background:#fff;font-size:.85rem}
 button.dl{background:#1a7f37;color:#fff;border-color:#1a7f37;font-weight:600}
 button.defer.on{background:#8250df;color:#fff;border-color:#8250df}
 .card{background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:1rem;margin:1rem 0}
 .card.done{border-color:#1a7f37;box-shadow:0 0 0 2px #1a7f3722}
 .card.deferred{border-color:#8250df;box-shadow:0 0 0 2px #8250df22}
 .chead{display:flex;gap:.7rem;align-items:center;margin-bottom:.5rem}
 .tag{background:#0969da;color:#fff;border-radius:5px;padding:.1rem .5rem;font-weight:700;font-size:.8rem}
 .dim{font-weight:600}
 .status{margin-left:auto;font-size:.8rem;color:#999}
 .status.set{color:#1a7f37;font-weight:600}
 .status.deferred{color:#8250df;font-weight:600}
 .q{font-size:.9rem;color:#333;margin:.3rem 0}
 .ev{font-size:.88rem;background:#f0f6ff;padding:.4rem .6rem;border-radius:6px;margin:.3rem 0}
 .ex{font-size:.82rem;margin:.3rem 0}
 .ex code{background:#f6f8fa;padding:.15rem .3rem;border-radius:4px;font-size:.8rem;word-break:break-word}
 .mixed{background:#fff8e5;border:1px solid #f0d48a;border-radius:6px;padding:.4rem .6rem;font-size:.85rem;margin:.3rem 0}
 .sugbox{font-size:.85rem;color:#444;margin:.4rem 0}
 .opts{display:flex;flex-direction:column;gap:.3rem;margin:.5rem 0}
 .opt{font-size:.86rem;display:flex;align-items:flex-start;gap:.4rem;cursor:pointer}
 .opt .ndicts{color:#888;font-size:.78rem}
 .sug{color:#1a7f37;font-weight:700;font-size:.78rem}
 .actions{display:flex;gap:.6rem;align-items:center;margin-top:.5rem}
 .note{flex:1;padding:.35rem .5rem;border:1px solid #ccc;border-radius:6px;font-size:.83rem}
</style></head><body>
<h1>LRV / FRI — Patel convention annotation</h1>
<div class="sub">Sheet __SHEET__ · __N__ items (2 dicts × dims 1,3,5,6,7) · the last two sourced dicts outside Patel 2016.
Tick the Patel option(s) that hold for each dict (multiple sub-rules may co-occur), or <b>defer</b> to leave it unknown.
Green suggestions are pre-ticked from the evidence rates — confirm or override. Votes autosave to this browser.</div>
<div class="bar">
  <b><span id="cAssigned">0</span></b>&nbsp;assigned
  <b><span id="cDeferred">0</span></b>&nbsp;deferred
  <b><span id="cLeft">__N__</span></b>&nbsp;left
  <button class="dl" id="dl">⬇ Download decisions.json</button>
</div>
__CARDS__
<div class="bar" style="margin-top:1rem"><span id="hint">Assign or defer every item, then download.</span>
  <button class="dl" id="dl2">⬇ Download decisions.json</button></div>
<script>
const SHEET="__SHEET__";
const KEY="reviewsheet:"+SHEET;
let store=JSON.parse(localStorage.getItem(KEY)||"{}"); // iid -> {selected:[],deferred:bool,note:""}
function rec(iid){ if(!store[iid]) store[iid]={selected:[],deferred:false,note:""}; return store[iid]; }
function save(){ localStorage.setItem(KEY, JSON.stringify(store)); render(); }
function render(){
  let a=0,def=0;
  document.querySelectorAll(".card").forEach(c=>{
    const iid=c.dataset.item, r=store[iid]||{selected:[],deferred:false};
    const st=document.getElementById("st-"+iid);
    c.classList.remove("done","deferred"); st.classList.remove("set","deferred");
    if(r.deferred){ def++; c.classList.add("deferred"); st.classList.add("deferred"); st.textContent="⏸ deferred"; }
    else if(r.selected.length){ a++; c.classList.add("done"); st.classList.add("set"); st.textContent="✓ "+r.selected.join(", "); }
    else { st.textContent="● unset"; }
  });
  cAssigned.textContent=a; cDeferred.textContent=def; cLeft.textContent=(__N__-a-def);
  hint.textContent=(a+def===__N__)?"All items decided — download decisions.json.":"Assign or defer every item, then download.";
}
document.querySelectorAll(".opt input").forEach(cb=>cb.addEventListener("change",e=>{
  const iid=e.target.dataset.item, r=rec(iid); r.deferred=false;
  r.selected=[...document.querySelectorAll('.opt input[data-item="'+iid+'"]:checked')].map(x=>x.value);
  save();
}));
document.querySelectorAll(".defer").forEach(b=>b.addEventListener("click",e=>{
  const iid=e.target.dataset.item, r=rec(iid);
  r.deferred=!r.deferred;
  if(r.deferred){ r.selected=[]; document.querySelectorAll('.opt input[data-item="'+iid+'"]').forEach(x=>x.checked=false); }
  e.target.classList.toggle("on",r.deferred); save();
}));
document.querySelectorAll(".note").forEach(n=>n.addEventListener("input",e=>{
  rec(e.target.dataset.item).note=e.target.value; localStorage.setItem(KEY,JSON.stringify(store));
}));
// restore
document.querySelectorAll(".card").forEach(c=>{
  const iid=c.dataset.item, r=store[iid]; if(!r) return;
  (r.selected||[]).forEach(v=>{const cb=c.querySelector('.opt input[value="'+CSS.escape(v)+'"]'); if(cb) cb.checked=true;});
  if(r.deferred) c.querySelector(".defer").classList.add("on");
  const nb=c.querySelector(".note"); if(nb&&r.note) nb.value=r.note;
});
function download(){
  const items=[...document.querySelectorAll(".card")].map(c=>{
    const iid=c.dataset.item, r=store[iid]||{selected:[],deferred:false,note:""};
    let status=r.deferred?"deferred":(r.selected&&r.selected.length?"assigned":null);
    return {id:iid, dict:c.dataset.dict, dim:+c.dataset.dim, selected:r.selected||[], status, note:r.note||""};
  });
  const out={sheet_id:SHEET, generated:"__GEN__", decided:new Date().toISOString(),
             items};
  const blob=new Blob([JSON.stringify(out,null,2)],{type:"application/json"});
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob);
  a.download=SHEET+"_decisions.json"; a.click();
}
dl.onclick=download; dl2.onclick=download;
render();
</script></body></html>"""

    gen = "2026-07-03"
    out = (tpl.replace("__SHEET__", SHEET_ID)
              .replace("__CARDS__", "\n".join(cards))
              .replace("__N__", str(len(items)))
              .replace("__GEN__", gen))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {OUT} ({len(items)} items)")


if __name__ == "__main__":
    main()
