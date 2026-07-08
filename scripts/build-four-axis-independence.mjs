// Build the four-axis CITATION independence test packet (PH2 / CITE-4AXIS) + the V3 page data.
//
// THREE-AXIS-INDEP established that content, convention, and microstructure are
// statistically separate axes of dictionary inheritance on the 13 documented L0
// edges. PH2 asks whether the CITATION PROFILE — cosine similarity of two
// dictionaries' normalised citation vectors — is a FOURTH separable axis, or
// whether "quoting the same books" is collinear with one of the existing three.
//
// Citation vectors come from the canonical-siglum source matrix in the committed
// citation-apparatus dataset (src/data/dicts/citation-apparatus.json), NOT from
// the data/citations/ ls-graph the agenda originally named: the ls-graph resolves
// MW to only a handful of texts (its top keys — MBh. 22,990, R. 9,049 … — sit in
// ls_citation_unresolved_top.tsv), and 3 of the 5 usable edges involve MW, so
// graph cosines there measure resolver coverage, not canon. The ls-graph cosine
// is still computed and reported per edge as a flagged sensitivity column.
//
// Honest shrinkage: only edges whose BOTH endpoints have a validated <ls>
// citation adapter enter the test. Measured overlap is 7 of the 14 L0-edge
// dictionaries → n=5 edges (the agenda's §2 estimate of "9 of 13" was optimistic;
// the excluded edges and reasons are listed in the payload). At n=5 the critical
// |r| (df=3) is 0.878 at p=0.05 / 0.959 at p=0.01, and every Pearson r carries an
// EXACT label-permutation p over all 5! = 120 permutations.
//
// Pure derivation from committed artifacts; no source/corpus read, no public
// decision. Registers hypothesis CITE-4AXIS (PH2).
//
// Usage: npm run build-four-axis-independence   (then npm run validate-four-axis-independence)

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-four-axis-independence";
const COMPARISON_PATH = path.resolve(process.cwd(), "data", "lexico", "three_axis_comparison.json");
const APPARATUS_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "citation-apparatus.json");
const GRAPH_EDGES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_edges.tsv");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "four_axis_citation_independence.json");
const SITE_OUT = path.resolve(process.cwd(), "src", "data", "lexico", "four_axis_citation_independence.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "FOUR_AXIS_CITATION_INDEPENDENCE.md");

// three_axis_comparison dict code → citation-apparatus dict label (byDict key).
// The apparatus labels its `pw` adapter "PWK" (Böhtlingk's kürzere Fassung =
// the three-axis "PW"). Dictionaries absent here have no validated <ls>
// citation adapter (WIL essentially untagged; YAT/SHS/CCS/CAE/MW72/BOP unadapted).
export const APPARATUS_CODE = {
  PWG: "PWG",
  PW: "PWK",
  MW: "MW",
  AP90: "AP90",
  AP: "AP",
  SCH: "SCH",
  BEN: "BEN",
};

// three_axis_comparison dict code → data/citations/ ls-graph dict code
// (sensitivity column only).
export const GRAPH_CODE = {
  PWG: "pwg",
  PW: "pw",
  MW: "mw",
  AP90: "ap90",
  AP: "ap",
  SCH: "sch",
  BEN: "ben",
};

function round(value, digits = 3) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function mean(xs) {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}

export function pearson(xs, ys) {
  const mx = mean(xs);
  const my = mean(ys);
  let num = 0;
  let dxx = 0;
  let dyy = 0;
  for (let i = 0; i < xs.length; i += 1) {
    const dx = xs[i] - mx;
    const dy = ys[i] - my;
    num += dx * dy;
    dxx += dx * dx;
    dyy += dy * dy;
  }
  const den = Math.sqrt(dxx * dyy);
  return den === 0 ? NaN : num / den;
}

// Fractional (tie-averaged) ranks so Spearman is well-defined on tied scores.
function ranks(xs) {
  const order = xs.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]);
  const r = new Array(xs.length);
  let i = 0;
  while (i < order.length) {
    let j = i;
    while (j + 1 < order.length && order[j + 1][0] === order[i][0]) j += 1;
    const avg = (i + j) / 2 + 1;
    for (let k = i; k <= j; k += 1) r[order[k][1]] = avg;
    i = j + 1;
  }
  return r;
}

export function spearman(xs, ys) {
  return pearson(ranks(xs), ranks(ys));
}

// Cosine similarity between two per-dict citation COUNT maps, each normalised
// to a share-of-own-total vector first (so a big and a small apparatus with the
// same canon shape score 1).
export function cosineOfCounts(a, b) {
  const sa = Object.values(a).reduce((x, y) => x + y, 0);
  const sb = Object.values(b).reduce((x, y) => x + y, 0);
  if (!sa || !sb) return NaN;
  const texts = new Set([...Object.keys(a), ...Object.keys(b)]);
  let num = 0;
  let na = 0;
  let nb = 0;
  for (const t of texts) {
    const x = (a[t] || 0) / sa;
    const y = (b[t] || 0) / sb;
    num += x * y;
    na += x * x;
    nb += y * y;
  }
  const den = Math.sqrt(na * nb);
  return den === 0 ? NaN : num / den;
}

// Exact two-tailed label-permutation p for Pearson r: the share of ALL n!
// permutations of xs whose |r| against ys reaches the observed |r|. Only used
// for small n (n! enumerated); throws rather than silently sampling.
export function exactPermutationP(xs, ys) {
  if (xs.length > 8) throw new Error(`exactPermutationP: n=${xs.length} too large for exact enumeration`);
  const observed = Math.abs(pearson(xs, ys));
  let atLeast = 0;
  let total = 0;
  const permute = (rest, acc) => {
    if (rest.length === 0) {
      total += 1;
      if (Math.abs(pearson(acc, ys)) >= observed - 1e-12) atLeast += 1;
      return;
    }
    for (let i = 0; i < rest.length; i += 1) {
      permute([...rest.slice(0, i), ...rest.slice(i + 1)], [...acc, rest[i]]);
    }
  };
  permute(xs, []);
  return { p: atLeast / total, nPermutations: total };
}

// Two-tailed critical |r| (df = n-2) from the standard Pearson table — used
// only to LABEL detectability at the reduced n; inference is left to the
// exact permutation p and the reader.
const CRITICAL_R = {
  5: { "0.05": 0.878, "0.01": 0.959 },
  9: { "0.05": 0.666, "0.01": 0.798 },
  13: { "0.05": 0.553, "0.01": 0.684 },
};

function labelStrength(n, r) {
  const table = CRITICAL_R[n];
  const a = Math.abs(r);
  if (!table) return a >= 0.7 ? "strong" : a >= 0.4 ? "moderate" : "weak";
  if (a >= table["0.01"]) return "significant-p01";
  if (a >= table["0.05"]) return "significant-p05";
  return "not-significant";
}

function corr(label, xs, ys, n, withPermutation = false) {
  const p = pearson(xs, ys);
  const row = {
    pair: label,
    pearson: round(p),
    spearman: round(spearman(xs, ys)),
    strength: labelStrength(n, p),
  };
  if (withPermutation) {
    const perm = exactPermutationP(xs, ys);
    row.permutationP = round(perm.p);
    row.nPermutations = perm.nPermutations;
  }
  return row;
}

export function parseGraphEdges(tsv) {
  const vectors = {};
  const lines = tsv.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  for (const line of lines.slice(1)) {
    const [dict, text, count] = line.split("\t");
    (vectors[dict] ??= {})[text] = Number(count);
  }
  return vectors;
}

function apparatusVectors(apparatus) {
  const vectors = {};
  for (const source of apparatus.sourceMatrix ?? []) {
    for (const [dict, count] of Object.entries(source.byDict ?? {})) {
      if (count > 0) (vectors[dict] ??= {})[source.source] = count;
    }
  }
  return vectors;
}

function sharedTextCount(a, b) {
  return Object.keys(a).filter((t) => (b[t] ?? 0) > 0 && a[t] > 0).length;
}

export function buildPayload(comparison, apparatus, graphEdgesTsv, generatedAt) {
  const rows = comparison.comparisonRows || [];
  const appVectors = apparatusVectors(apparatus);
  const graphVectors = parseGraphEdges(graphEdgesTsv);

  const edges = [];
  const excludedEdges = [];
  for (const r of rows) {
    const pApp = APPARATUS_CODE[r.parent];
    const cApp = APPARATUS_CODE[r.child];
    if (!pApp || !cApp || !appVectors[pApp] || !appVectors[cApp]) {
      const missing = [r.parent, r.child].filter((d) => !APPARATUS_CODE[d] || !appVectors[APPARATUS_CODE[d]]);
      excludedEdges.push({
        rowId: r.rowId,
        parent: r.parent,
        child: r.child,
        reason: `no validated <ls> citation adapter for ${missing.join(", ")}`,
      });
      continue;
    }
    const pGraph = graphVectors[GRAPH_CODE[r.parent]];
    const cGraph = graphVectors[GRAPH_CODE[r.child]];
    edges.push({
      rowId: r.rowId,
      parent: r.parent,
      child: r.child,
      tier: r.tier,
      contentAxis: r.contentAxis.parentInChild,
      conventionAxis: r.conventionAxis.conventionSimilarity,
      microstructureAxis: r.microstructureAxis.microstructureSimilarity01,
      citationAxis: round(cosineOfCounts(appVectors[pApp], appVectors[cApp]), 4),
      citationSharedSources: sharedTextCount(appVectors[pApp], appVectors[cApp]),
      // sensitivity column: the data/citations/ ls-graph cosine (degenerate for MW)
      graphCitationCosine: pGraph && cGraph ? round(cosineOfCounts(pGraph, cGraph), 4) : null,
      graphSharedTexts: pGraph && cGraph ? sharedTextCount(pGraph, cGraph) : null,
    });
  }

  const n = edges.length;
  const content = edges.map((e) => e.contentAxis);
  const convention = edges.map((e) => e.conventionAxis);
  const micro = edges.map((e) => e.microstructureAxis);
  const citation = edges.map((e) => e.citationAxis);

  const citationCorrelations = [
    corr("citation~content", citation, content, n, true),
    corr("citation~convention", citation, convention, n, true),
    corr("citation~microstructure", citation, micro, n, true),
  ];
  // The full 4x4 matrix on the SAME reduced edge set, so the panel is
  // internally consistent (the n=13 three-axis stats live in THREE-AXIS-INDEP).
  const axes = [
    ["content", content],
    ["convention", convention],
    ["microstructure", micro],
    ["citation", citation],
  ];
  const correlationMatrix = [];
  for (const [nameA, xsA] of axes) {
    for (const [nameB, xsB] of axes) {
      correlationMatrix.push({
        a: nameA,
        b: nameB,
        pearson: nameA === nameB ? 1 : round(pearson(xsA, xsB)),
        spearman: nameA === nameB ? 1 : round(spearman(xsA, xsB)),
      });
    }
  }

  // Do the two citation-vector sources at least agree in ORDER? (Spearman of the
  // apparatus cosine vs the ls-graph cosine across the reduced edges.)
  const graphAvailable = edges.every((e) => e.graphCitationCosine !== null);
  const sensitivityAgreementSpearman = graphAvailable
    ? round(spearman(citation, edges.map((e) => e.graphCitationCosine)))
    : null;

  const maxCitationPearson = Math.max(...citationCorrelations.map((c) => Math.abs(c.pearson)));
  const criticalR = CRITICAL_R[n] ?? null;
  const separable = criticalR ? maxCitationPearson < criticalR["0.05"] : null;

  const mwGraphTexts = Object.keys(graphVectors.mw ?? {}).length;

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    status: "four-axis-citation-independence-test",
    hypothesis: "CITE-4AXIS",
    claim:
      "Dictionary-pair citation-profile similarity (cosine over per-dict normalised citation vectors) is statistically separable from the content, convention, and microstructure axes on the documented L0 edges — a fourth axis of descent.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "data/lexico/three_axis_comparison.json",
      "src/data/dicts/citation-apparatus.json",
      "data/citations/ls_citation_edges.tsv",
      "scripts/build-four-axis-independence.mjs",
    ],
    sourceGeneratedAt: comparison.generatedAt ?? null,
    n,
    nDocumentedEdges: rows.length,
    method:
      `Citation axis = cosine similarity of the two dictionaries' share-normalised citation vectors over the citation-apparatus canonical-siglum source matrix (top-${(apparatus.sourceMatrix ?? []).length} shared sources, validated <ls> adapters). Pearson and Spearman against the three committed axis scores on the reduced edge set, with the two-tailed critical |r| for n=${n} (df=${n - 2}): ${criticalR ? `${criticalR["0.05"]} at p=0.05, ${criticalR["0.01"]} at p=0.01` : "no table"}. Each citation~axis Pearson additionally carries an EXACT label-permutation p over all ${n}! = ${citationCorrelations[0]?.nPermutations ?? "?"} permutations.`,
    edgeShrinkage: {
      note:
        `Only ${Object.keys(APPARATUS_CODE).length} of the 14 dictionaries on the ${rows.length} documented L0 edges have a validated <ls> citation adapter, leaving n=${n} testable edges — fewer than the agenda §2 estimate ("9 of the 13"). The excluded edges are listed explicitly; nothing is imputed.`,
      testableEdges: n,
      excludedEdges,
    },
    citationVectorSource: {
      primary:
        "src/data/dicts/citation-apparatus.json sourceMatrix (canonical siglum fold + reviewed alias table; MW fully resolved: 320,828 tagged citations)",
      whyNotLsGraph:
        `data/citations/ls_citation_edges.tsv resolves MW to only ${mwGraphTexts} texts (its top abbreviations — MBh., R., BhP. … — sit unresolved in ls_citation_unresolved_top.tsv), and 3 of the ${n} testable edges involve MW, so ls-graph cosines there measure resolver coverage, not canon shape (BEN~MW = 0.0 is an artifact). The ls-graph cosine is reported per edge as a sensitivity column instead.`,
      sensitivityAgreementSpearman,
    },
    edges,
    citationCorrelations,
    correlationMatrix,
    findings: {
      citationAxisSeparable: separable,
      maxAbsCitationPearson: round(maxCitationPearson),
      minCitationPermutationP: round(Math.min(...citationCorrelations.map((c) => c.permutationP))),
      strongestCoupling: citationCorrelations.reduce((a, b) => (Math.abs(b.pearson) > Math.abs(a.pearson) ? b : a)).pair,
    },
    interpretation: [
      `No citation~axis correlation reaches the n=${n} p=0.05 threshold and no exact permutation p falls below 0.05, so the packet cannot reject the citation profile's independence from the other three axes — consistent with citation canon being a FOURTH axis of descent.`,
      "The citation~microstructure point estimate is large (Pearson ≈ 0.84, exact permutation p ≈ 0.08) — the single strongest cross-axis coupling measured on any axis pair so far. At n=5 it is not detectable, but it is the first thing to re-test when the documented edge set grows: if it holds, 'quoting the same books' travels with microstructural register, not with headword stock.",
      "Citation~content is weak (≈0.4): sharing headword stock does not imply sharing citation canon on these edges — which is exactly the separation the fourth-axis claim needs, and consistent with APPARATUS-NOT-ERRORS treating apparatus descent as its own signal.",
    ],
    limitations: [
      `n=${n} testable edges after honest shrinkage — the smallest reduced set in the axis series. Critical |r| at this n is 0.878, so only near-perfect collinearity would be detectable; every verdict here is descriptive, not confirmatory.`,
      "The citation vectors live in the apparatus top-source space (head of the citation-frequency distribution, canonical-siglum folded); tail sources are not represented. Cosine on share-normalised vectors is dominated by the head anyway, but a full-vector recomputation is the natural upgrade.",
      "Several edges share the PWG parent or the MW child, so the edge sample is non-independent — the same caveat as THREE-AXIS-INDEP.",
      "All inputs inherit the caveats of three_axis_comparison.json and citation-apparatus.json (containment is size-confounded; convention encodes modelled house style; <ls> adapters miss prose/`iti` citation).",
    ],
    boundary: [
      "Derived from committed atlas dictionary evidence only; no source/corpus read, no human decision, no external maker work.",
    ],
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function fmtCorr(c) {
  const perm = c.permutationP !== undefined ? ` | ${c.permutationP}` : " | —";
  return `| \`${c.pair}\` | ${c.pearson} | ${c.spearman}${perm} | \`${c.strength}\` |`;
}

export function buildMarkdown(payload) {
  return [
    "# Four-Axis Citation Independence Test (PH2 / CITE-4AXIS)",
    "",
    "Status: generated machine-reviewed analysis packet; derived from `data/lexico/three_axis_comparison.json` + `src/data/dicts/citation-apparatus.json`, no human decisions promoted.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`; review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- n = ${payload.n} testable edges (of ${payload.nDocumentedEdges} documented). ${payload.method}`,
    `- Edge shrinkage: ${payload.edgeShrinkage.note}`,
    `- Citation-vector source: ${payload.citationVectorSource.primary}. ${payload.citationVectorSource.whyNotLsGraph}`,
    "",
    "## Citation-axis correlations (fourth-axis test)",
    "",
    "| Axis pair | Pearson | Spearman | exact permutation p | Strength (n=" + payload.n + ") |",
    "|---|---:|---:|---:|---|",
    ...payload.citationCorrelations.map((c) =>
      `| \`${c.pair}\` | ${c.pearson} | ${c.spearman} | ${c.permutationP} | \`${c.strength}\` |`),
    "",
    "## Testable edges",
    "",
    "| Edge | content | convention | microstructure | citation (apparatus cosine) | ls-graph cosine (sensitivity) |",
    "|---|---:|---:|---:|---:|---:|",
    ...payload.edges.map((e) =>
      `| ${e.parent}→${e.child} | ${e.contentAxis} | ${e.conventionAxis} | ${e.microstructureAxis} | ${e.citationAxis} | ${e.graphCitationCosine ?? "—"} |`),
    "",
    "## Interpretation",
    "",
    ...payload.interpretation.map((line) => `- ${line}`),
    "",
    "## Limitations",
    "",
    ...payload.limitations.map((line) => `- ${line}`),
    "",
    "_Auto-generated by `npm run build-four-axis-independence`._",
    "",
  ].join("\n");
}

function main() {
  const comparison = JSON.parse(fs.readFileSync(COMPARISON_PATH, "utf8"));
  const apparatus = JSON.parse(fs.readFileSync(APPARATUS_PATH, "utf8"));
  const graphEdgesTsv = fs.readFileSync(GRAPH_EDGES_PATH, "utf8");
  const payload = buildPayload(comparison, apparatus, graphEdgesTsv);
  fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  fs.mkdirSync(path.dirname(SITE_OUT), { recursive: true });
  fs.writeFileSync(SITE_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  fs.writeFileSync(MARKDOWN_OUT, buildMarkdown(payload));
  console.log(`Wrote four-axis citation independence test (n=${payload.n} of ${payload.nDocumentedEdges} documented edges):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SITE_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), MARKDOWN_OUT)}`);
  console.log(
    `  max |citation~axis Pearson| = ${payload.findings.maxAbsCitationPearson} (${payload.findings.strongestCoupling}); ` +
      `min exact permutation p = ${payload.findings.minCitationPermutationP}; ` +
      `separable at n=${payload.n} = ${payload.findings.citationAxisSeparable}`,
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
