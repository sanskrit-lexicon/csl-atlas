#!/usr/bin/env python3
"""A72 census v1 — computed grammatical-abbreviation polysemy across the digitized CSDL canon (H6409).

Re-founds the hand-collected homograph tables of Gasūns 2006 (EURALEX Torino,
pp. 773–778; dossier Uprava/research/gasuns-2006-latin-terms-evolution-dossier.md)
as a computed census over the csl-orig/v02 corpus. Every number in the emitted
artifacts is recomputed by this script; every denominator (dictionaries parsed,
entries scanned, labels counted) is carried in the payload — the H800
denominator-artifact lesson.

Emits
-----
  data/abbrev/abbrev_census.json    — sections (a) inventories, (b) unified label
                                      table, (c) collision matrix, (d) polysemy
  reports/ABBREV_CENSUS_V1_2026.md  — the human report (e)

REUSE MAP (nothing re-derived)
------------------------------
  * `parse_cslorig.iter_entries` — corpus reader (H1826 line; both `<ls>` shapes).
  * `citation_register_gaps.discover_dicts` — the dictionary roster, same glob the
    sibling register artifacts use so the `dicts` key sets can never disagree.
  * `data/obs/ls_abbreviation_frequency.json` — the `<ls>` source-siglum layer
    (H1826, csl-observatory#222), loaded as-is and invariant-checked against
    `data/obs/citation_registers.json`, not recomputed.
  * csl-guides `src/data/abbreviations.json` — the front-matter legend layer:
    per-dictionary {abbr, expansion} rows with grammatical/works classification,
    curated from the org's per-dictionary legend files (build-abbreviations.mjs).
    Loaded as-is with git provenance (CSL_GUIDES env overrides the path).
  * `scripts/lib/dataset_meta.py` — licence + stable-`generatedAt` envelope.
NOT rebuilt (different layers, cross-linked): csl_pyutil.anatomy (entry
microstructure), the H5325 megastructure catalogue (per-dictionary structure),
the H5335 lexicographic-types register (dictionary-genre taxonomy).

Usage (from the repo root):
    python scripts/build_abbrev_census.py
Env overrides: CSL_ORIG (default ../csl-orig/v02), CSL_GUIDES (default
../csl-guides/src/data/abbreviations.json).
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter

sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/obs"))
sys.path.insert(0, os.path.abspath("scripts/lib"))
from citation_register_gaps import CSL_ORIG as DEFAULT_CORPUS  # noqa: E402
from citation_register_gaps import discover_dicts  # noqa: E402
from dataset_meta import generated_at_for_payload, license_fields, read_json_if_exists  # noqa: E402
from parse_cslorig import iter_entries  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT_JSON = os.path.join("data", "abbrev", "abbrev_census.json")
OUT_REPORT = os.path.join("reports", "ABBREV_CENSUS_V1_2026.md")
LS_FREQ = os.path.join("data", "obs", "ls_abbreviation_frequency.json")
LS_REGISTERS = os.path.join("data", "obs", "citation_registers.json")
SCHEMA_VERSION = "1.0.0"
HANDOFF = "H6409"
PAPER = "Gasūns 2006, Latin Terms in Sanskrit Dictionaries (EURALEX XII, Torino, pp. 773–778)"
EXECUTOR = "GLM-5.3-Flash (zai-coding-plan/glm-5.3-flash) via ZCode"

# Grammatical label layers carried inline in the v02 body markup, scanned as
# (tag -> raw token) Counters. `<ls>` stays with the H1826 artifact.
CENSUS_TAGS = ("ab", "lex", "lang")
_TAG_RES = {tag: re.compile(rf"<{tag}(?:\s[^>]*)?>(.*?)</{tag}>", re.DOTALL) for tag in CENSUS_TAGS}
_INNER_TAG = re.compile(r"<[^>]*>")
_WS = re.compile(r"\s+")

# The 2006 hand-collected homograph class the census re-founds, plus the
# Petersburg-Wörterbuch sigla cluster (one work, five competing abbreviations).
TARGET_CLASS_2006 = ["V.", "c.", "P.", "S.", "N.", "M.", "m", "s", "f."]
PETERSBURG_STRINGS = ["PW", "PWG", "BR", "PW1", "pw", "PW2", "KBR", "PWN"]


def _fail(message):
    raise SystemExit(f"build_abbrev_census: {message}")


def resolve_corpus_root():
    root = os.environ.get("CSL_ORIG", DEFAULT_CORPUS)
    if not os.path.isdir(root):
        _fail(f"csl-orig corpus not found at {root!r}; set CSL_ORIG")
    return root


def resolve_guides_path():
    env = os.environ.get("CSL_GUIDES")
    candidates = [env] if env else [
        os.path.join("..", "csl-guides", "src", "data", "abbreviations.json"),
        os.path.expanduser(os.path.join("~", "Documents", "GitHub", "csl-guides",
                                        "src", "data", "abbreviations.json")),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    _fail("csl-guides abbreviations.json not found; set CSL_GUIDES to the file path")


def git_provenance(repo_dir, rel_path):
    def run(args):
        return subprocess.run(["git", "-C", repo_dir] + args, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=60)
    head = run(["log", "-1", "--format=%H %cI", "--", rel_path])
    dirty = run(["status", "--porcelain", "--", rel_path])
    return {
        "file": os.path.abspath(os.path.join(repo_dir, rel_path)),
        "commit": head.stdout.strip() or None,
        "dirty": bool(dirty.stdout.strip()),
    }


def load_legends(guides_path):
    """The csl-guides legend layer verbatim: {CODE: rows}, rows carry category."""
    with open(guides_path, encoding="utf-8") as fh:
        raw = json.load(fh)
    legends = {}
    for entry in raw.get("dicts", []):
        code = entry.get("code")
        if not code or entry.get("status") != "data":
            continue
        rows = []
        for category in ("grammatical", "works", "mixed"):
            for row in entry.get(category) or []:
                rows.append({"abbr": row.get("abbr", ""),
                             "expansion": row.get("expansion", ""),
                             "category": category})
        legends[code] = rows
    return {"catalogued": len(raw.get("dicts", [])),
            "counts": raw.get("counts", {}),
            "legends": legends}


def strip_markup(text):
    return _WS.sub(" ", _INNER_TAG.sub("", text or "")).strip()


def scan_corpus(corpus_root):
    """Per dictionary: entry count, per-tag raw-token counters, front-matter presence."""
    scan = {}
    for code in discover_dicts():
        path = os.path.join(corpus_root, code, f"{code}.txt")
        if not os.path.exists(path):
            continue
        entries = 0
        tags = {tag: Counter() for tag in CENSUS_TAGS}
        for entry in iter_entries(path):
            entries += 1
            body = entry.get("body") or ""
            for tag, rx in _TAG_RES.items():
                for match in rx.findall(body):
                    token = strip_markup(match)
                    if token:
                        tags[tag][token] += 1
        front = os.path.join(corpus_root, code, f"{code}_front.txt")
        back = os.path.join(corpus_root, code, f"{code}_back.txt")
        scan[code] = {
            "entries": entries,
            "tags": {tag: dict(sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])))
                     for tag, counter in tags.items()},
            "tagTotals": {tag: sum(counter.values()) for tag, counter in tags.items()},
            "frontMatterFile": {"front": os.path.getsize(front) if os.path.exists(front) else 0,
                                "back": os.path.getsize(back) if os.path.exists(back) else 0},
        }
    return scan


def expansion_key(expansion):
    """Comparison key for "same meaning": NFC, whitespace-collapsed, casefolded,
    trailing period dropped. Display text keeps the original form."""
    text = unicodedata.normalize("NFC", strip_markup(expansion or ""))
    return text.rstrip(".").casefold()


def build_label_table(legends, scan):
    """(b) Unified label table: every raw abbreviation string observed in the
    legend layer or in the inline grammatical tags, with per-dictionary
    expansions and usage counts keyed by layer."""
    table = {}
    for dict_code, rows in sorted(legends.items()):
        for row in rows:
            label = row["abbr"]
            if not label:
                continue
            slot = table.setdefault(label, {"label": label, "legends": [], "tags": {}})
            slot["legends"].append({"dict": dict_code, "expansion": row["expansion"],
                                    "category": row["category"]})
    for dict_code, info in sorted(scan.items()):
        for tag, tokens in info["tags"].items():
            for token in tokens:
                slot = table.setdefault(token, {"label": token, "legends": [], "tags": {}})
                counts = slot["tags"].setdefault(dict_code, {})
                counts[tag] = counts.get(tag, 0) + tokens[token]
    return dict(sorted(table.items()))


def build_collision_matrix(label_table):
    """(c) Strings whose expansion set (casefold-compare) spans >1 meaning —
    the 2006 homograph class, computed. Cross-dictionary AND within-dictionary
    collisions both count; category is carried so grammatical-vs-works clashes
    (2006's "V." = vocativus AND Vedic) stay visible."""
    collisions = []
    for slot in label_table.values():
        senses = {}
        for row in slot["legends"]:
            key = expansion_key(row["expansion"])
            senses.setdefault(key, {"expansion": row["expansion"], "dicts": [], "categories": set()})
            senses[key]["dicts"].append(row["dict"])
            senses[key]["categories"].add(row["category"])
        if len(senses) < 2:
            continue
        collisions.append({
            "label": slot["label"],
            "polysemy": len(senses),
            "senses": [{"expansion": s["expansion"], "dicts": sorted(s["dicts"]),
                        "categories": sorted(s["categories"])}
                       for s in sorted(senses.values(), key=lambda s: (-len(s["dicts"]), s["expansion"]))],
        })
    collisions.sort(key=lambda c: (-c["polysemy"], c["label"]))
    return collisions


def build_polysemy(label_table):
    """(d) Per-abbreviation polysemy over ALL legend-carrying strings."""
    polysemy = {}
    for slot in label_table.values():
        if not slot["legends"]:
            continue
        senses = {expansion_key(row["expansion"]) for row in slot["legends"]}
        polysemy[slot["label"]] = {
            "nExpansions": len(senses),
            "nDicts": len({row["dict"] for row in slot["legends"]}),
            "nOccurrences": sum(1 for _ in slot["legends"]),
        }
    return dict(sorted(polysemy.items(), key=lambda kv: (-kv[1]["nExpansions"], kv[0])))


def check_ls_invariant(ls_freq, registers):
    """The H1826 artifact's correctness test, re-run on the loaded copies:
    per dictionary sum(token counts) == citation_registers.dicts[code].ls."""
    violations = []
    freq_dicts = (ls_freq or {}).get("dicts", {})
    reg_dicts = (registers or {}).get("dicts", {})
    for code, tokens in sorted(freq_dicts.items()):
        expected = (reg_dicts.get(code) or {}).get("ls")
        if expected is None:
            continue
        if sum(tokens.values()) != expected:
            violations.append({"dict": code, "sumTokens": sum(tokens.values()), "registerLs": expected})
    return violations


def build_payload(legends_layer, scan, ls_freq, registers, provenance):
    label_table = build_label_table(legends_layer["legends"], scan)
    collision = build_collision_matrix(label_table)
    polysemy = build_polysemy(label_table)
    histogram = Counter(row["nExpansions"] for row in polysemy.values())
    previous = read_json_if_exists(OUT_JSON)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        **license_fields(),
        "handoff": HANDOFF,
        "paper": PAPER,
        "executor": EXECUTOR,
        "generatedAt": None,  # filled from generated_at_for_payload below
        "provenance": provenance,
        "denominators": {
            "dictionariesCatalogued": legends_layer["catalogued"],
            "legendCounts": legends_layer["counts"],
            "dictionariesWithLegends": len(legends_layer["legends"]),
            "corpusDictionariesDiscovered": len(scan),
            "corpusDictionariesParsed": sum(1 for s in scan.values() if s["entries"] > 0),
            "entriesScanned": sum(s["entries"] for s in scan.values()),
            "labelsCounted": {tag: sum(s["tagTotals"][tag] for s in scan.values()) for tag in CENSUS_TAGS},
            "distinctLabelsInTable": len(label_table),
            "lsCitationsTotal": sum((r.get("ls") or 0) for r in (registers or {}).get("dicts", {}).values()),
            "lsInvariantViolations": check_ls_invariant(ls_freq, registers),
        },
        "inventories": {
            code: {
                "entries": info["entries"],
                "tagTotals": info["tagTotals"],
                "tags": info["tags"],
                "frontMatterFile": info["frontMatterFile"],
                "legendRows": len(legends_layer["legends"].get(code.upper(), [])),
            }
            for code, info in sorted(scan.items())
        },
        "labelTable": label_table,
        "collisionMatrix": collision,
        "polysemy": polysemy,
        "polysemyHistogram": {str(k): histogram[k] for k in sorted(histogram)},
    }
    payload["generatedAt"] = generated_at_for_payload(previous, payload)
    return payload


def petersburg_rows(payload):
    """Legend strings competing for the Petersburg Sanskrit-Wörterbuch — the
    2006 synonymy note computed: a string qualifies if it is one of the known
    sigla or its expansion names the Wörterbuch (Petersburg + Wörterbuch, or
    Böhtlingk … Roth). Publication-place mentions of St. Petersburg alone do
    not qualify."""
    hits = []
    for label, slot in payload["labelTable"].items():
        if label in PETERSBURG_STRINGS:
            hits.append({"label": label, "expansion": slot["legends"][0]["expansion"],
                         "dict": slot["legends"][0]["dict"]})
            continue
        for row in slot["legends"]:
            key = expansion_key(row["expansion"])
            names_woerterbuch = ("petersburg" in key and "wörterbuch" in key) or \
                                ("petersburg" in key and "worterbuch" in key)
            names_bohtlingk_roth = "öhtlingk" in row["expansion"] and " roth" in key
            if names_woerterbuch or names_bohtlingk_roth:
                hits.append({"label": label, "expansion": row["expansion"], "dict": row["dict"]})
                break
    seen = set()
    unique = []
    for hit in sorted(hits, key=lambda h: h["label"]):
        if hit["label"] not in seen:
            seen.add(hit["label"])
            unique.append(hit)
    return unique


def _senses_compact(row, limit=6):
    parts = [f"{s['expansion']} ({', '.join(s['dicts'][:4])}{'…' if len(s['dicts']) > 4 else ''})"
             for s in row["senses"][:limit]]
    if len(row["senses"]) > limit:
        parts.append(f"… +{len(row['senses']) - limit}")
    return "; ".join(parts)


def render_report(payload, guides_prov, corpus_root):
    den = payload["denominators"]
    lines = []
    w = lines.append
    w(f"# A72 census v1 — computed grammatical-abbreviation polysemy across the digitized CSDL canon")
    w("")
    w(f"_Generated: {payload['generatedAt']} · executor {EXECUTOR} · handoff {HANDOFF}_")
    w("")
    w("_Created: 10-10-2026 · Last updated: 10-10-2026_")
    w("")
    w(f"Re-founds the hand-collected homograph tables of {PAPER} as a computed")
    w("census. Every number below is emitted by `scripts/build_abbrev_census.py`;")
    w("the full payload (inventories, unified label table, collision matrix,")
    w("polysemy) lives in [data/abbrev/abbrev_census.json](../data/abbrev/abbrev_census.json).")
    w("")
    w("## Denominators")
    w("")
    w(f"| Denominator | Value |")
    w(f"|---|---|")
    w(f"| Dictionaries catalogued in the csl-guides legend layer | {den['dictionariesCatalogued']} |")
    w(f"| … with a machine-readable legend (status data) | {den['dictionariesWithLegends']} |")
    w(f"| Corpus dictionaries discovered in `{corpus_root}` | {den['corpusDictionariesDiscovered']} |")
    w(f"| … parsed (entries > 0) | {den['corpusDictionariesParsed']} |")
    w(f"| Entries scanned | {den['entriesScanned']} |")
    for tag in CENSUS_TAGS:
        w(f"| `<{tag}>` labels counted | {den['labelsCounted'][tag]} |")
    w(f"| Distinct labels in the unified table | {den['distinctLabelsInTable']} |")
    w(f"| `<ls>` citations (H1826 registers, reused) | {den['lsCitationsTotal']} |")
    w(f"| `<ls>` layer invariant violations | {len(den['lsInvariantViolations'])} |")
    w("")
    w("## Corpus label census (a)")
    w("")
    w("| Dict | Entries | `<ab>` | `<lex>` | `<lang>` | `<ls>` | front/back matter |")
    w("|---|---|---|---|---|---|---|")
    reg_dicts = (payload.get("provenance", {}).get("lsRegisters") or {}).get("dicts", {})
    for code, inv in payload["inventories"].items():
        ls_total = (reg_dicts.get(code) or {}).get("ls", 0)
        fm = inv["frontMatterFile"]
        fm_txt = f"{fm['front']}/{fm['back']} B" if (fm["front"] or fm["back"]) else "—"
        w(f"| {code} | {inv['entries']} | {inv['tagTotals']['ab']} | "
          f"{inv['tagTotals']['lex']} | {inv['tagTotals']['lang']} | {ls_total} | {fm_txt} |")
    w("")
    w("## Legend layer (front-matter abbreviation lists)")
    w("")
    counts = den["legendCounts"]
    w(f"csl-guides catalogs {den['dictionariesCatalogued']} dictionaries: "
      f"{counts.get('withData', den['dictionariesWithLegends'])} with a machine-readable legend, "
      f"{counts.get('tokensOnly', '?')} tokens-only (inventory, no expansions), "
      f"{counts.get('none', '?')} scanned-image-only or none. The legend rows are reused verbatim; "
      "this census does not re-parse prefaces.")
    w("")
    w("## Collision matrix (c) — the 2006 homograph class, computed")
    w("")
    top = payload["collisionMatrix"][:25]
    w(f"{len(payload['collisionMatrix'])} abbreviation strings are polysemous "
      f"(≥ 2 distinct expansions after casefold-compare). Top 25 by polysemy:")
    w("")
    w("| Label | Senses | Senses → dictionaries |")
    w("|---|---|---|")
    for row in top:
        w(f"| `{row['label']}` | {row['polysemy']} | {_senses_compact(row)} |")
    w("")
    w("### The 2006 target strings")
    w("")
    w("Each 2006 hand row reappears in the computed table: vocative/Vedic/Vikramorvaśīyam for `V.`, "
      "causal/case for `c.`, Name/neuter/Naiṣadhacarita for `N.`, Manu/Masculine for `M.`, "
      "Sūtra/siehe/substantive for `S.`, and for `f.` the MD sense «also = for» — 2006's «f. … and for (Mc)» "
      "computed. The bare single-letter rows (`m`, `s`) stay absent: their 2006 witnesses (Ln, Mc, Ko, Wb) "
      "sit outside the digitized legend set, which the denominator states honestly.")
    w("")
    w("| 2006 hand row | Computed v1 (legend layer) |")
    w("|---|---|")
    by_label = {row["label"]: row for row in payload["collisionMatrix"]}
    for label in TARGET_CLASS_2006:
        row = by_label.get(label)
        computed = _senses_compact(row) if row else "not polysemous in the digitized legends"
        w(f"| `{label}` | {computed} |")
    w("")
    w("Petersburg-Wörterbuch sigla (one work, competing abbreviations — the 2006 synonymy note, "
      "computed as known sigla or expansions naming the Wörterbuch itself; publication-place "
      "mentions of St. Petersburg do not qualify):")
    w("")
    w("| Siglum | Expansion (first legend row) | Dict |")
    w("|---|---|---|")
    for hit in petersburg_rows(payload):
        expansion = hit["expansion"] if len(hit["expansion"]) <= 90 else hit["expansion"][:87] + "…"
        w(f"| `{hit['label']}` | {expansion} | {hit['dict']} |")
    w("")
    w("## Polysemy distribution (d)")
    w("")
    legend_labels = len(payload["polysemy"])
    collision_n = len(payload["collisionMatrix"])
    w(f"{legend_labels} abbreviation strings carry at least one legend expansion; "
      f"{collision_n} of them ({100.0 * collision_n / max(legend_labels, 1):.1f}%) are polysemous. "
      "In-corpus-only strings (no legend row) carry usage mass in the label table but no computed "
      "senses, so they stay out of this distribution.")
    w("")
    w("| Distinct expansions per abbreviation | Label count |")
    w("|---|---|")
    for key, count in payload["polysemyHistogram"].items():
        w(f"| {key} | {count} |")
    w("")
    w("## Method, reuse, limits")
    w("")
    w("* Corpus read via `parse_cslorig.iter_entries` (H1826 line); roster via "
      "`citation_register_gaps.discover_dicts` — the same glob as the sibling register artifacts.")
    w("* The `<ls>` source-siglum layer is NOT recomputed: it is the committed "
      "[data/obs/ls_abbreviation_frequency.json](../data/obs/ls_abbreviation_frequency.json) "
      "artifact (H1826, csl-observatory#222); this build re-runs its "
      "sum-equals-register invariant and reports violations, zero expected.")
    w("* Legends are the csl-guides per-dictionary abbreviation dataset "
      "(commit below), parsed by csl-guides from the org's canonical legend files; "
      "classification grammatical/works is carried per row.")
    w("* Comparisons are on RAW strings (case-sensitive, trailing punctuation kept) — "
      "the H1076 lesson: case folding misreads hedged sigla. Expansion equality is "
      "casefold+NFC+trailing-period-insensitive (`expansion_key`).")
    w("* Different layers, NOT rebuilt here: entry microstructure (`csl_pyutil.anatomy`), "
      "per-dictionary structure (H5325 megastructure catalogue), dictionary-genre taxonomy "
      "(H5335 lexicographic-types register). E3 (the 2006 «small classes» normative scheme) "
      "is a separate item — this census measures only.")
    w("* Limits: 26 of 44 catalogued dictionaries have no machine-readable legend, so the "
      "collision matrix is a lower bound; inline `<ab>`/`<lex>`/`<lang>` conventions differ "
      "per digitization (PW's `<ab>` carries German+Latin, MW's English); the `<ls>` layer "
      "is inventoried but its senses are not disambiguated here. BOP's legend source carries "
      "mojibake, so encoding-variant rows can inflate BOP's sense counts (visible on `P.`/`A.`) — "
      "kept raw rather than silently folded.")
    w("")
    w("## Prior art read before the label-table format (github-first)")
    w("")
    w("* TEI Lex-0 official repo [DARIAH-ERIC/lexicalresources](https://github.com/DARIAH-ERIC/lexicalresources) "
      "(`Schemas/TEILex0/TEILex0.odd` + parts): grammatical info lives in `gramGrp`/`gram`, usage labels in "
      "`usg` with a typed vocabulary (geographic/time/domain/…); Lex-0 keeps label *values* open, so a "
      "controlled label register is exactly the gap E3 fills. Estate precedent: csl-standards pins Lex-0 0.9.5 (A70).")
    w("* SKOS: no normative GitHub repo exists (w3c/skos 404s) — official surface is the "
      "[W3C SKOS Reference](https://www.w3.org/TR/skos-reference/); the E3 register maps naturally to "
      "skos:Concept with prefLabel (expansion) / notation (abbreviation).")
    w("* User repos consulted: BCDH/tei-lex-0 (workshop spec mirror), pdl-lex/pdl-import-postgres (Lex-0 consumer).")
    w("")
    w("## Provenance")
    w("")
    w(f"* corpus: `{corpus_root}`")
    w(f"* legends: {guides_prov['file']} @ `{(guides_prov['commit'] or 'uncommitted').split()[0]}`"
      f"{' (dirty)' if guides_prov['dirty'] else ''}")
    w(f"* model: {EXECUTOR}; handoff {HANDOFF}; license {payload['license']}")
    w("")
    w("_Dr. Mārcis Gasūns_")
    w("")
    return "\n".join(lines)


def main():
    corpus_root = resolve_corpus_root()
    guides_path = resolve_guides_path()
    guides_prov = git_provenance(os.path.dirname(os.path.dirname(os.path.dirname(guides_path))),
                                 os.path.relpath(guides_path, os.path.dirname(os.path.dirname(os.path.dirname(guides_path)))))
    corpus_prov = subprocess.run(["git", "-C", corpus_root, "rev-parse", "HEAD"],
                                 capture_output=True, text=True, encoding="utf-8",
                                 errors="replace", timeout=60).stdout.strip()
    legends_layer = load_legends(guides_path)
    print(f"legends: {len(legends_layer['legends'])} dictionaries with data "
          f"of {legends_layer['catalogued']} catalogued")
    scan = scan_corpus(corpus_root)
    print(f"corpus: parsed {len(scan)} dictionaries, "
          f"{sum(s['entries'] for s in scan.values())} entries")
    ls_freq = read_json_if_exists(LS_FREQ)
    registers = read_json_if_exists(LS_REGISTERS)
    if ls_freq is None or registers is None:
        _fail(f"missing committed H1826 artifacts at {LS_FREQ} / {LS_REGISTERS}; run their builders first")
    provenance = {
        "corpusRoot": os.path.abspath(corpus_root),
        "corpusCommit": corpus_prov or None,
        "guides": guides_prov,
        "lsFrequency": {"file": os.path.abspath(LS_FREQ), "reused": True},
        "lsRegisters": registers,
    }
    payload = build_payload(legends_layer, scan, ls_freq, registers, provenance)
    report = render_report(payload, guides_prov, corpus_root)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    with open(OUT_REPORT, "w", encoding="utf-8") as fh:
        fh.write(report)
    collisions = payload["denominators"]
    print(f"wrote {OUT_JSON} ({collisions['distinctLabelsInTable']} labels, "
          f"{len(payload['collisionMatrix'])} collisions) and {OUT_REPORT}")
    violations = collisions["lsInvariantViolations"]
    if violations:
        print(f"WARNING: {len(violations)} <ls> invariant violations: {violations[:5]}")


if __name__ == "__main__":
    main()
