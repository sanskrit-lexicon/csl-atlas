// H1621 — agent adjudication of H4 needs-review rows (no human stage).
//
// For each needs-review row: probe local csl-orig (via iterateDict) + the row's
// own sourcePointers, force a closed-vocab decision, write reviewed* fields on
// the packet, and emit gitignored decisions.json matching the sheet schema.
//
// Usage: node scripts/adjudicate-h4-agent.mjs
// Never --reseed. Does not touch csl-orig text.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { dictExists, iterateDict } from "./lib/dict-parser.mjs";
import { from_slp1, slp1_form_key } from "../src/lib/sanskrit-util.js";

const ROOT = process.cwd();
const PACKET_PATH = path.join(ROOT, "data/lexico/h4_semantic_field_review_packet.json");
const DECISIONS_PATH = path.join(ROOT, "review/csl-atlas-h4-semantic-field_89rows_decisions.json");
const REVIEWER = "grok-4.5 (H1621 agent; evidence: local csl-orig + packet pointers)";
const REVIEWED_AT = new Date().toISOString().slice(0, 10);

const indexCache = new Map(); // code -> { exact: Map, fold: Map, bodies: string[] for prose scan limited }

function loadIndex(code) {
  if (indexCache.has(code)) return indexCache.get(code);
  if (!dictExists(code)) {
    const empty = { exact: new Map(), fold: new Map(), records: [] };
    indexCache.set(code, empty);
    return empty;
  }
  const exact = new Map();
  const fold = new Map();
  const records = [];
  for (const rec of iterateDict(code)) {
    if (!rec.k1) continue;
    const k = String(rec.k1);
    if (!exact.has(k)) exact.set(k, rec);
    const fk = slp1_form_key(k);
    if (!fold.has(fk)) fold.set(fk, rec);
    records.push(rec);
  }
  const idx = { exact, fold, records };
  indexCache.set(code, idx);
  return idx;
}

function norm(s) {
  return String(s ?? "").trim();
}

function excerptOf(row) {
  return (row.sourcePointers || []).find((p) => p.bodyExcerpt)?.bodyExcerpt || "";
}

function pointerHeadword(row) {
  return (row.sourcePointers || []).find((p) => p.role === "exact-dictionary-headword" || p.role === "candidate-dictionary-headword");
}

/** Common stem variants for -in adjectives listed as -ī [n] in prose lexica. */
function stemVariants(lemma) {
  const L = norm(lemma);
  const out = new Set([L]);
  if (/in$/.test(L) && L.length > 3) {
    out.add(L.slice(0, -2) + "I"); // sukftin → sukftI
    out.add(L.slice(0, -1)); // drop final n
  }
  if (/I$/.test(L)) out.add(L.slice(0, -1) + "in");
  if (/a$/.test(L)) out.add(L + "H");
  if (/H$/.test(L)) out.add(L.slice(0, -1));
  if (/M/.test(L)) out.add(L.replace(/M/g, "n"));
  if (/n/.test(L)) out.add(L.replace(/n(?=[td])/g, "M"));
  return [...out];
}

function findInDict(code, lemma) {
  const idx = loadIndex(code);
  const L = norm(lemma);
  if (idx.exact.has(L)) return { kind: "exact", rec: idx.exact.get(L) };
  for (const v of stemVariants(L)) {
    if (v !== L && idx.exact.has(v)) return { kind: "variant", rec: idx.exact.get(v), matched: v };
  }
  const fk = slp1_form_key(L);
  if (idx.fold.has(fk)) {
    const rec = idx.fold.get(fk);
    if (norm(rec.k1) !== L) return { kind: "fold", rec, matched: rec.k1 };
  }
  // Prose body scan (bounded): headword-adjacent forms only, first hit.
  const needle = L.toLowerCase();
  const needles = stemVariants(L).map((s) => s.toLowerCase());
  for (const rec of idx.records) {
    const body = (rec.body || "").toLowerCase();
    if (!body) continue;
    // Prefer headword line / early body, skip huge false positives.
    const head = body.slice(0, Math.min(body.length, 400));
    if (needles.some((n) => n.length >= 4 && head.includes(n) && norm(rec.k1).toLowerCase() !== needle)) {
      return { kind: "prose", rec, matched: rec.k1 };
    }
  }
  return { kind: "absent" };
}

function bodyLen(excerpt) {
  return String(excerpt || "").replace(/\s+/g, " ").trim().length;
}

function decideSkdFalseLow(row) {
  const hit = findInDict("skd", row.lemma);
  const iast = from_slp1(row.lemma);
  if (hit.kind === "variant" || hit.kind === "fold") {
    return {
      decision: "variant-headword",
      note: `SKD headword ${hit.matched} (IAST ${from_slp1(hit.matched)}) matches AMAR ${iast} under stem/fold variant; strict key miss is normalization, not true gap.`
    };
  }
  if (hit.kind === "prose") {
    return {
      decision: "prose-present",
      note: `Lemma ${iast} not a SKD k1 but occurs in SKD body near headword ${hit.matched} (L=${hit.rec.L}); prose/citation presence.`
    };
  }
  if (hit.kind === "exact") {
    return {
      decision: "parser-gap",
      note: `Exact SKD k1 ${row.lemma} exists (L=${hit.rec.L}) but coverage table marked missing — parser/coverage join gap.`
    };
  }
  return {
    decision: "true-low",
    note: `No SKD exact/fold/stem/prose hit for ${iast} in local csl-orig; treat as genuine low/missing coverage.`
  };
}

function decideVcpHigh(row) {
  const ex = excerptOf(row);
  const len = bodyLen(ex);
  const iast = from_slp1(row.lemma);
  const ptr = pointerHeadword(row);
  // Thin: gloss-only or stub (< ~50 printable chars after headword separator).
  const afterSep = ex.includes("¦") ? ex.split("¦").slice(1).join("¦") : ex;
  const substance = bodyLen(afterSep);
  if (substance > 0 && substance < 50) {
    return {
      decision: "thin-entry",
      note: `VCP ${iast} L=${ptr?.L ?? "?"} has short body (${substance} chars after ¦); usable headword but thin for field-profile claims.`
    };
  }
  // Normalization risk: pointer headword form diverges from lemma beyond case.
  if (ptr?.form && slp1_form_key(ptr.form) === slp1_form_key(row.lemma) && norm(ptr.form) !== norm(row.lemma)) {
    return {
      decision: "normalization-risk",
      note: `VCP form ${ptr.form} vs AMAR ${row.lemma} is a fold/normalization pair; coverage may overstate identity.`
    };
  }
  if (len >= 50 || substance >= 50) {
    return {
      decision: "true-covered",
      note: `VCP ${iast} L=${ptr?.L ?? "?"} has substantive entry (${Math.max(len, substance)} chars); real usable indigenous-prose coverage.`
    };
  }
  // Fallback when excerpt missing but machineState covered.
  if (ptr) {
    return {
      decision: "true-covered",
      note: `VCP exact pointer L=${ptr.L} for ${iast}; excerpt short/missing but headword present — count as covered.`
    };
  }
  return {
    decision: "thin-entry",
    note: `VCP ${iast} marked covered without usable excerpt; conservative thin-entry.`
  };
}

function decideApAp90(row) {
  const lemma = row.lemma;
  const iast = from_slp1(lemma);
  const ap90 = findInDict("ap90", lemma);
  const ap = findInDict("ap", lemma);
  if (ap90.kind === "fold" || ap90.kind === "variant") {
    return {
      decision: "normalization-risk",
      note: `AP90 has ${ap90.matched} for AMAR ${iast}; AP/AP90 delta is fold/stem normalization, not edition absence.`
    };
  }
  if (ap90.kind === "exact") {
    return {
      decision: "parser-gap",
      note: `AP90 exact k1 ${lemma} exists (L=${ap90.rec.L}) but coverage marked missing vs AP — join/parser gap.`
    };
  }
  if (ap90.kind === "prose") {
    return {
      decision: "parser-gap",
      note: `AP90 prose hit under ${ap90.matched} for ${iast}; coverage miss is parser/extraction, not true edition delta.`
    };
  }
  // AP present, AP90 absent → classic edition history (Apte 1890 vs revised).
  if (ap.kind !== "absent" && ap90.kind === "absent") {
    return {
      decision: "edition-delta",
      note: `AP has ${lemma} (L=${ap.rec?.L ?? pointerHeadword(row)?.L ?? "?"}); AP90 lacks exact/fold/prose — edition history delta.`
    };
  }
  return {
    decision: "true-delta",
    note: `AP/AP90 state for ${iast} not explained by fold or simple edition miss (AP=${ap.kind}, AP90=${ap90.kind}).`
  };
}

// Specialized dict scopes (coarse, from family labels + known charter).
const SPECIALIZED_SCOPE = {
  armh: { fields: /pAtAla|nAga|rasA|Bog/i, note: "ARMH synonym lexicon — underworld/nāga field is in scope" },
  fri: { fields: /vyoma|div|ambara|naBas|antarikza|aBra|puzkara/i, note: "FRI sky/atmosphere lexicon — vyoma field is in scope" },
  bhs: { fields: /DI|prajYA|mati|jYapti|samADAna|praRiDAna|pratipad/i, note: "BHS Buddhist Hybrid Sanskrit — intellect/path terms in scope" }
};

function decideSpecialized(row) {
  const code = row.dictionary.code;
  const fieldKey = row.field?.fieldKey || row.field?.label || "";
  const lemma = row.lemma;
  const iast = from_slp1(lemma);
  const scope = SPECIALIZED_SCOPE[code];
  const ex = excerptOf(row);
  const ptr = pointerHeadword(row);

  if (scope && scope.fields.test(fieldKey + "|" + lemma)) {
    // Substantive headword in a matching field → scope-match.
    if (bodyLen(ex) >= 20 || ptr) {
      return {
        decision: "scope-match",
        note: `${code.toUpperCase()} ${iast} in ${from_slp1(row.field?.label || "")}: ${scope.note}; headword L=${ptr?.L ?? "?"} present.`
      };
    }
  }
  // Weak field control / short coincidence.
  if (bodyLen(ex) < 30 && scope && !scope.fields.test(fieldKey)) {
    return {
      decision: "scope-mismatch",
      note: `${code.toUpperCase()} hit on ${iast} outside its charter field pattern; treat as scope-mismatch.`
    };
  }
  if (bodyLen(ex) < 40) {
    return {
      decision: "incidental-match",
      note: `${code.toUpperCase()} ${iast} is a short/incidental headword hit; not strong scope evidence for the field profile.`
    };
  }
  return {
    decision: "scope-match",
    note: `${code.toUpperCase()} ${iast} L=${ptr?.L ?? "?"} has usable entry aligned with specialized family baseline.`
  };
}

function decideIndexReverse(row) {
  const family = row.dictionary.familyLabel || "";
  const code = row.dictionary.code;
  const iast = from_slp1(row.lemma);
  const ex = excerptOf(row);
  const ptr = pointerHeadword(row);
  const lemma = norm(row.lemma);

  // Reverse bilingual (AE/MWE): English headword → Sanskrit gloss. Particle/
  // interjection/short lemmas are classic direction artifacts.
  if (family === "reverse-bilingual" || code === "ae" || code === "mwe") {
    if (lemma.length <= 3 || /^(cit|ha|he|a|u|o|e|hi|ca|vA|tu|nu)$/i.test(lemma)) {
      return {
        decision: "direction-artifact",
        note: `${code.toUpperCase()} reverse-bilingual hit on short/particle ${iast} (L=${ptr?.L ?? "?"}) is lookup-direction artifact, not AMAR-field coverage.`
      };
    }
    return {
      decision: "direction-artifact",
      note: `${code.toUpperCase()} is reverse-bilingual; ${iast} coverage measures English→Sanskrit lookup, not indigenous field coverage.`
    };
  }

  // Index/catalogue (PUI/INM/IEG): name/place indexes. Famous terms often
  // appear as index articles — still not lexicon field coverage.
  if (family === "index-catalogue" || ["pui", "inm", "ieg"].includes(code)) {
    // Longer encyclopedic excerpts can be meaningful exceptions (real topic page).
    if (bodyLen(ex) >= 180) {
      return {
        decision: "meaningful-exception",
        note: `${code.toUpperCase()} index entry for ${iast} is long (${bodyLen(ex)} chars, L=${ptr?.L ?? "?"}); substantive catalogue article, not empty index stub.`
      };
    }
    return {
      decision: "index-artifact",
      note: `${code.toUpperCase()} index/catalogue hit on ${iast} (L=${ptr?.L ?? "?"}) is genre/index artifact for field-coverage claims.`
    };
  }

  return {
    decision: "index-artifact",
    note: `${code.toUpperCase()} control family ${family || "unknown"}: default index-artifact for ${iast}.`
  };
}

function decideRow(row) {
  switch (row.sampleType) {
    case "skd-false-low":
      return decideSkdFalseLow(row);
    case "vcp-high-coverage":
      return decideVcpHigh(row);
    case "ap-ap90-delta":
      return decideApAp90(row);
    case "specialized-baseline":
      return decideSpecialized(row);
    case "index-reverse-control":
      return decideIndexReverse(row);
    default:
      return { decision: null, note: `unknown sampleType ${row.sampleType}`, blocked: true };
  }
}

function main() {
  const packet = JSON.parse(fs.readFileSync(PACKET_PATH, "utf8"));
  const targets = packet.sampleRows.filter((r) => r.reviewStatus === "needs-review");
  console.log(`Adjudicating ${targets.length} needs-review rows…`);

  // Warm indexes for codes we will probe.
  for (const code of ["skd", "ap", "ap90", "vcp"]) {
    if (dictExists(code)) {
      const t0 = Date.now();
      loadIndex(code);
      console.log(`  index ${code}: ${indexCache.get(code).records.length} records (${Date.now() - t0}ms)`);
    } else {
      console.warn(`  WARNING: csl-orig missing for ${code}`);
    }
  }

  const items = [];
  const byDecision = new Map();
  let blocked = 0;

  for (const row of targets) {
    const allowed = new Set(row.expectedDecisionLabels || []);
    let { decision, note, blocked: isBlocked } = decideRow(row);
    if (isBlocked || !decision || !allowed.has(decision)) {
      // Conservative: if rule emitted out-of-vocab, fall back by sample type.
      const fallback = {
        "skd-false-low": "true-low",
        "vcp-high-coverage": "true-covered",
        "ap-ap90-delta": "edition-delta",
        "specialized-baseline": "incidental-match",
        "index-reverse-control": "index-artifact"
      }[row.sampleType];
      if (!decision || !allowed.has(decision)) {
        note = `${note || ""} [fallback→${fallback}]`.trim();
        decision = fallback;
      }
      if (!allowed.has(decision)) {
        row.reviewStatus = "needs-review";
        row.note = `blocked: could not map to vocab (${note})`;
        blocked += 1;
        items.push({ id: row.reviewId, decision: "defer", note: row.note });
        continue;
      }
    }
    row.reviewedValue = decision;
    row.reviewStatus = "reviewed-ok";
    row.reviewer = REVIEWER;
    row.reviewedAt = REVIEWED_AT;
    row.note = note.slice(0, 400);
    items.push({ id: row.reviewId, decision, note: row.note });
    byDecision.set(decision, (byDecision.get(decision) || 0) + 1);
  }

  // Recount packet headers.
  const still = packet.sampleRows.filter((r) => r.reviewStatus === "needs-review").length;
  const agentReviewed = packet.sampleRows.filter((r) => r.reviewStatus === "reviewed-ok").length;
  packet.counts = packet.counts || {};
  packet.counts.needsHumanReview = still;
  packet.counts.agentReviewed = agentReviewed;
  packet.counts.byReviewedValue = Object.fromEntries(
    [...packet.sampleRows.filter((r) => r.reviewedValue)].reduce((m, r) => {
      m.set(r.reviewedValue, (m.get(r.reviewedValue) || 0) + 1);
      return m;
    }, new Map())
  );
  packet.reviewStatus = still === 0 ? "agent-reviewed" : "needs-human-review";

  fs.writeFileSync(PACKET_PATH, `${JSON.stringify(packet, null, 2)}\n`);

  fs.mkdirSync(path.dirname(DECISIONS_PATH), { recursive: true });
  const decisions = {
    sheet_id: "csl-atlas-h4-semantic-field_89rows",
    generated: REVIEWED_AT,
    decided: new Date().toISOString(),
    reviewer: REVIEWER,
    handoff: "H1621",
    items
  };
  fs.writeFileSync(DECISIONS_PATH, `${JSON.stringify(decisions, null, 2)}\n`);

  console.log(`Wrote ${path.relative(ROOT, PACKET_PATH)}`);
  console.log(`Wrote ${path.relative(ROOT, DECISIONS_PATH)} (${items.length} items)`);
  console.log(`agentReviewed=${agentReviewed} stillNeedsReview=${still} blocked=${blocked}`);
  console.log("by decision:");
  for (const [k, v] of [...byDecision.entries()].sort((a, b) => b[1] - a[1])) {
    console.log(`  ${k}: ${v}`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
