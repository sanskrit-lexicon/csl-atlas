// H1684 — agent adjudication of the 102 sampled SKD iti-units (В2 stage).
//
// The sheet `csl-atlas-skd-iti_100units` asks a reviewer to confirm or correct
// build-r2-kosa-fusion's three-way class for each sampled iti-unit:
//
//   authority-terminal — the definition run ends *in* its own authority formula
//   separable          — the unit is essentially just the authority tag
//   other-no-authority — no authority marker in the unit
//
// This script re-derives every sampled unit from local csl-orig (the packet's
// own `text` is cleanText(...,200)-TRUNCATED, so it cannot settle a unit whose
// authority marker sits past character 200), re-runs the classifier's decision
// with an explicit citational-vs-grammatical reading, and writes a verdict per
// row with cited evidence.
//
// Two defects in the shipped classifier motivate the rule set below; both are
// re-measured here rather than asserted:
//
//   FN — SKD_AUTHORITY_HINTS (build-r2-source-anchors.mjs) is a 17-entry
//        curated list dominated by *text* citations. Bare kośa authorities that
//        open a tail unit (halāyudhaḥ, trikāṇḍaśeṣaḥ, rājanighaṇṭuḥ,
//        durgādāsaḥ, sāyaṇaḥ, uṇādivṛttiḥ ...) match neither that list nor the
//        `ity[a-zA-Z]{3,}` fused pattern, so they land in other-no-authority.
//   FP — `ity[a-zA-Z]{3,}` also fires on the *grammatical* formulae
//        (ityarthaḥ "such is the meaning", ityādi "et cetera"). Those are
//        explanatory boundaries, not citational ones — precisely the
//        distinction the sheet puts to the reviewer.
//
// Usage: node scripts/adjudicate-h1684-skd-iti.mjs
// Read-only against csl-orig. Writes the packet + decisions.json only.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { R2_DICTS, splitRecord, cleanText } from "./build-r2-source-anchors.mjs";

const ROOT = process.cwd();
const SAMPLE_PATH = path.join(ROOT, "data/lexico/r2_kosa_fusion_sample.json");
const PACKET_PATH = path.join(ROOT, "data/lexico/h1684_skd_iti_adjudication_packet.json");
const DECISIONS_PATH = path.join(ROOT, "review/csl-atlas-skd-iti_100units_decisions.json");
const HANDOFF = "H1684";
const REVIEWER = "Opus 5 1M (`claude-opus-5[1m]`) — H1684 agent; evidence: local csl-orig v02/skd full unit text";

// The classifier's own documented (uncalibrated) cut point, mirrored so the
// re-derivation is commensurable with the shipped numbers.
const FUSION_MIN_CONTENT_CHARS = 20;
// Rows whose content-before-authority lands in this band are NOT auto-decided:
// the threshold is documented as "a threshold, not a calibrated cut point", so
// a row that only just clears or misses it is a genuine human call.
const BOUNDARY_BAND = [12, 30];

const CLASSES = ["authority-terminal", "separable", "other-no-authority"];

// ---------------------------------------------------------------------------
// Authority lexicon
// ---------------------------------------------------------------------------
// Indigenous citation authorities as they surface in SKD (SLP1). Kośas and
// their commentaries, nighaṇṭus, uṇādi literature, named commentators, and the
// text citations the shipped hint list already recognised. Matching is on a
// de-hyphenated copy of the unit (SKD breaks words across lines with "-").
const AUTHORITY_NAMES = [
  // Amara + its commentaries
  "amaraH", "amarakozaH", "amarawIkAyAM", "amarawIkA", "amaraBaratO", "amaraBarataH", "BarataH",
  // The great kośas
  "medinI", "medinIkaraH", "medinIkarahemacandrO", "hemacandraH", "hemacandra",
  "viSvaH", "viSvaprakASaH", "trikARqaSezaH", "halAyuDaH", "ajayaH", "raBasaH", "rABasaH",
  "SabdaratnAvalI", "ratnamAlA", "jawADaraH", "dvirUpakozaH", "nAnArTakozaH",
  "ekAkzarakozaH", "SabdacandrikA", "BUriprayogaH", "SabdamAlA",
  // uṇādi literature
  "uRAdikozaH", "uRAdivfttiH", "saMkziptasAroRAdivfttiH", "uRAdisUtraM",
  // nighaṇṭu / medical
  "rAjanirGaRwaH", "rAjavallaBaH", "BAvaprakASaH", "SArNgaDaraH", "suSrutaH", "vEdyakaM",
  // named commentators / śāstric authorities
  "durgAdAsaH", "sAyaRaH", "gopInATatarkAcAryyaH", "tarkAlaNkAraH",
  "SabdaSaktiprakASikA", "SabdArTacintAmaRiH", "mugDaboDawIkAyAM", "ujjvalanIlamaRiH"
];

// Work titles the shipped SKD_AUTHORITY_HINTS list also carries. These are a
// DIFFERENT apparatus: in SKD they nearly always arrive inside a `yathā, X . “…”`
// illustrative quotation, not as the `iti <authority>` formula this class scheme
// is about. So a bare occurrence of one is recorded as evidence but is never
// decisive; only an `ity<Work>`-fused occurrence counts as an iti-borne citation.
// (Measured: exactly one sampled unit — skd-iti:14583:1 — had a bare text name as
// its earliest signal, and it carries a real `ityamaraBaratO` later in the same
// unit, so this restriction changes no label. It keeps the rule charter-clean.)
const TEXT_CITATIONS = [
  "BAgavate", "BAgavatam", "SrIBAgavatam", "DarmmadIpikA", "hitodeSe",
  "kaTAsaritsAgare", "mahABAratam", "manuH", "matsyapurARe",
  "pAdmaBUmiKaRqe", "pAdmottaraKaRqam", "rAmAyaRe", "yogasAre"
];

// Sandhi-fused `ity<X>` whose X is a grammatical/explanatory formula, NOT an
// authority: these mark an *explanatory* boundary. Longest-prefix tested first.
const FORMULA_STEMS = [
  "arTaH", "arTaM", "arTe", "arTAt",
  "AdiH", "Adi", "AdayaH", "AdInAM", "AdiSabdaH",
  "evam", "eva", "anena", "atra", "Avat", "yAvat",
  "aBiprAyaH", "vacanAt", "nyAyAt",
  // "thus stated / thus designated / up to -iti / is an indeclinable" — all
  // metalinguistic closers, none of them the name of an authority.
  "ukte", "uktaM", "uktam", "uktAni", "uktA", "ukta",
  "aBiDAnAt", "aBiDIyate", "aBiDIyante",
  "antam", "antaM", "avyayaM", "avyayam"
];

const FUSED_RE = /\bity[a-zA-Z]{3,}\b/g;

/** SKD hyphenates across line breaks; join those before token matching so
 *  "ityuRA- dikozaH" reads as the single token "ityuRAdikozaH". */
function dehyphenate(text) {
  return String(text ?? "").replace(/([a-zA-Z])-\s+([a-zA-Z])/g, "$1$2");
}

function contentCharsBefore(text, offset) {
  if (offset < 0) return 0;
  return text.slice(0, offset).replace(/<[^>]+>/g, " ").replace(/\s+/g, "").length;
}

/** Classify one sandhi-fused ity-token. */
function classifyFused(token) {
  const rest = token.slice(3); // strip "ity"
  // An authority name anywhere in the remainder wins, even behind a formula
  // prefix: "ityAdigopInATatarkAcAryyaH" is Gopīnātha Tarkācārya cited after
  // an ity-ādi, i.e. a real citation.
  const name = AUTHORITY_NAMES.find((n) => rest.toLowerCase().includes(n.toLowerCase()));
  if (name) return { kind: "authority", label: name };
  // An `ity<Work>`-fused work title IS an iti-borne citation, unlike a bare one.
  const work = TEXT_CITATIONS.find((n) => rest.toLowerCase().includes(n.toLowerCase()));
  if (work) return { kind: "authority", label: work };
  const stem = FORMULA_STEMS.find((s) => rest.toLowerCase().startsWith(s.toLowerCase()));
  if (stem) return { kind: "formula", label: `ity-${stem}` };
  return { kind: "unknown", label: token };
}

/** All authority/formula signals in a unit, earliest offset first. */
function signals(rawText) {
  const text = dehyphenate(rawText);
  const found = [];
  FUSED_RE.lastIndex = 0;
  for (const m of text.matchAll(FUSED_RE)) {
    const verdict = classifyFused(m[0]);
    found.push({ form: "fused", token: m[0], offset: m.index, ...verdict });
  }
  // Bare authority names (the "iti medinī" tail pattern: the split leaves the
  // name at the head of the next unit). Word-boundary matched. Work titles are
  // scanned too, but recorded as non-decisive `text-citation` evidence.
  for (const [names, kind] of [[AUTHORITY_NAMES, "authority"], [TEXT_CITATIONS, "text-citation"]]) {
    for (const name of names) {
      const re = new RegExp(`\\b${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`);
      const m = re.exec(text);
      if (!m) continue;
      // Skip when it is only the tail of a fused token already recorded.
      if (found.some((f) => f.form === "fused" && m.index >= f.offset && m.index < f.offset + f.token.length)) continue;
      found.push({ form: "bare", token: m[0], offset: m.index, kind, label: name });
    }
  }
  found.sort((a, b) => a.offset - b.offset);
  return { text, found };
}

function decide(rawText) {
  const { text, found } = signals(rawText);
  const authorities = found.filter((f) => f.kind === "authority");
  const formulas = found.filter((f) => f.kind === "formula");
  const unknowns = found.filter((f) => f.kind === "unknown");

  if (!authorities.length) {
    if (unknowns.length) {
      return {
        klass: "other-no-authority",
        rule: "unknown-ity-token",
        certain: false,
        evidence: `Unrecognised sandhi-fused token(s) ${unknowns.map((u) => u.token).join(", ")}; neither a known authority name nor a known grammatical formula.`,
        signals: found
      };
    }
    if (formulas.length) {
      return {
        klass: "other-no-authority",
        rule: "grammatical-formula-only",
        certain: true,
        evidence: `Only explanatory formula(e) ${formulas.map((f) => f.token).join(", ")} present — a grammatical boundary ("such is the meaning" / "et cetera"), not a citation of an authority.`,
        signals: found
      };
    }
    return {
      klass: "other-no-authority",
      rule: "no-authority-signal",
      certain: true,
      evidence: "No sandhi-fused ity-authority and no bare indigenous authority name in the full unit text.",
      signals: found
    };
  }

  const first = authorities[0];
  const before = contentCharsBefore(text, first.offset);
  const boundary = before >= BOUNDARY_BAND[0] && before <= BOUNDARY_BAND[1];
  const klass = before >= FUSION_MIN_CONTENT_CHARS ? "authority-terminal" : "separable";
  return {
    klass,
    rule: klass === "authority-terminal" ? "content-then-authority" : "authority-leads-unit",
    certain: !boundary,
    before,
    evidence:
      `Authority ${first.form === "fused" ? `«${first.token}»` : `«${first.label}»`} at offset ${first.offset}; ` +
      `${before} non-space content chars precede it in the unit ` +
      `(threshold ${FUSION_MIN_CONTENT_CHARS})` +
      (boundary ? ` — inside the uncalibrated boundary band ${BOUNDARY_BAND[0]}–${BOUNDARY_BAND[1]}, so the fused/separable call is not agent-decidable.` : "."),
    signals: found
  };
}

// ---------------------------------------------------------------------------

function loadSkdUnits(wanted) {
  const dict = R2_DICTS.find((d) => d.code === "skd");
  const byL = new Map();
  for (const rec of iterateDict("skd")) {
    const L = String(rec.L);
    if (!wanted.has(L)) continue;
    const parts = splitRecord(rec.body || "", dict);
    byL.set(L, { k1: rec.k1, units: parts.map((p) => p.text) });
  }
  return byL;
}

function main() {
  if (!dictExists("skd")) {
    console.error("csl-orig v02/skd is required for H1684 adjudication (full unit text); aborting.");
    process.exit(1);
  }
  const sample = JSON.parse(fs.readFileSync(SAMPLE_PATH, "utf8"));
  const wanted = new Set(sample.rows.map((r) => String(r.L)));
  console.log(`Re-deriving ${wanted.size} SKD records for ${sample.rows.length} sampled units…`);
  const t0 = Date.now();
  const byL = loadSkdUnits(wanted);
  console.log(`  resolved ${byL.size}/${wanted.size} records (${Date.now() - t0}ms)`);

  const rows = [];
  const items = [];
  const tally = { confirm: 0, correct: 0, uncertain: 0 };
  const byRule = new Map();
  let truncationSaved = 0;

  for (const row of sample.rows) {
    const rec = byL.get(String(row.L));
    const fullText = rec?.units?.[row.unitIndex];
    if (fullText == null) {
      rows.push({
        ...row,
        reviewId: `skd-iti:${row.L}:${row.unitIndex}`,
        agentClass: null,
        verdict: "uncertain",
        rule: "unit-not-resolvable",
        certain: false,
        evidence: `Could not re-derive unit ${row.unitIndex} of SKD L${row.L} from local csl-orig; sampled text is truncated, so no defensible call.`
      });
      tally.uncertain += 1;
      items.push({ id: `skd-iti:${row.L}:${row.unitIndex}`, decision: "defer", note: "unit not resolvable from local csl-orig" });
      continue;
    }
    if (fullText.length > row.text.length) truncationSaved += 1;

    const d = decide(fullText);
    const proposed = row.klass;
    let verdict;
    if (!d.certain) verdict = "uncertain";
    else if (d.klass === proposed) verdict = "confirm";
    else verdict = "correct";
    tally[verdict] += 1;
    byRule.set(d.rule, (byRule.get(d.rule) || 0) + 1);

    const reviewId = `skd-iti:${row.L}:${row.unitIndex}`;
    rows.push({
      reviewId,
      L: row.L,
      k1: row.k1,
      unitIndex: row.unitIndex,
      proposedClass: proposed,
      agentClass: d.klass,
      verdict,
      rule: d.rule,
      certain: d.certain,
      contentCharsBeforeAuthority: d.before ?? null,
      evidence: d.evidence,
      authoritySignals: d.signals.map((s) => ({ form: s.form, token: s.token, offset: s.offset, kind: s.kind, label: s.label })),
      fullUnitChars: fullText.length,
      sampledUnitChars: row.text.length,
      unitText: cleanText(fullText, 600),
      sourceHref: `https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L${row.L}`
    });
    items.push({
      id: reviewId,
      decision: verdict === "confirm" ? "approve" : verdict === "correct" ? "reject" : "defer",
      note: verdict === "correct" ? `corrected-label: ${d.klass}. ${d.evidence}` : d.evidence
    });
  }

  const byProposed = {};
  for (const c of CLASSES) {
    const sub = rows.filter((r) => r.proposedClass === c);
    byProposed[c] = {
      n: sub.length,
      confirm: sub.filter((r) => r.verdict === "confirm").length,
      correct: sub.filter((r) => r.verdict === "correct").length,
      uncertain: sub.filter((r) => r.verdict === "uncertain").length
    };
  }
  const byAgentClass = {};
  for (const c of CLASSES) byAgentClass[c] = rows.filter((r) => r.agentClass === c).length;

  const packet = {
    schemaVersion: "1.0.0",
    handoff: HANDOFF,
    sheetId: "csl-atlas-skd-iti_100units",
    reviewer: REVIEWER,
    evidenceLabel: "agent-adjudicated",
    source: {
      sample: "data/lexico/r2_kosa_fusion_sample.json",
      corpus: "../csl-orig/v02/skd/skd.txt (local, read-only)",
      classifier: "scripts/build-r2-kosa-fusion.mjs (FUSION_MIN_CONTENT_CHARS=20)"
    },
    method: {
      fusionMinContentChars: FUSION_MIN_CONTENT_CHARS,
      boundaryBand: BOUNDARY_BAND,
      authorityNames: AUTHORITY_NAMES.length,
      formulaStems: FORMULA_STEMS.length,
      rules: [
        "no-authority-signal → other-no-authority",
        "grammatical-formula-only (ity-arthaḥ / ity-ādi with no name) → other-no-authority",
        "unknown-ity-token → other-no-authority, flagged not-certain",
        "authority present, <20 content chars before → separable",
        "authority present, ≥20 content chars before → authority-terminal",
        `content chars in ${BOUNDARY_BAND[0]}–${BOUNDARY_BAND[1]} → not agent-decidable (uncalibrated threshold)`
      ]
    },
    counts: {
      rows: rows.length,
      ...tally,
      unitsWhereFullTextExceededSample: truncationSaved,
      byProposedClass: byProposed,
      byAgentClass,
      byRule: Object.fromEntries([...byRule.entries()].sort((a, b) => b[1] - a[1]))
    },
    rows
  };

  fs.writeFileSync(PACKET_PATH, `${JSON.stringify(packet, null, 2)}\n`);
  fs.mkdirSync(path.dirname(DECISIONS_PATH), { recursive: true });
  fs.writeFileSync(
    DECISIONS_PATH,
    `${JSON.stringify({ sheet_id: "csl-atlas-skd-iti_100units", handoff: HANDOFF, reviewer: REVIEWER, items }, null, 2)}\n`
  );

  console.log(`Wrote ${path.relative(ROOT, PACKET_PATH)}`);
  console.log(`Wrote ${path.relative(ROOT, DECISIONS_PATH)} (${items.length} items)`);
  console.log(`confirm=${tally.confirm} correct=${tally.correct} uncertain=${tally.uncertain}`);
  console.log(`units whose full text exceeded the sampled 200-char excerpt: ${truncationSaved}`);
  console.log("by rule:");
  for (const [k, v] of [...byRule.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${k}: ${v}`);
  console.log("proposed → verdict:");
  for (const c of CLASSES) {
    const p = byProposed[c];
    console.log(`  ${c}: n=${p.n} confirm=${p.confirm} correct=${p.correct} uncertain=${p.uncertain}`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
