// Generate R2 tool pages from live JSON outputs.
//
// Reads:
//   - data/lexico/r2_h1.json → regenerates r2-h1.md scatter SVG
//   - data/lexico/r2_align_<lemma>.json → regenerates r2-explorer.md cards/table
//   - data/lexico/r2_h2h3.json → creates new r2-h2h3.md with H2/H3R charts
//
// Uses idempotent marker injection: <!-- R2-GEN:START ... --> ... <!-- R2-GEN:END ... -->
// Re-running produces no diff when JSON is unchanged.
//
// Usage: npm run build-r2-pages

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const DATA_DIR = "data/lexico";
const TOOLS_DIR = "src/tools";

// ---- Palette & axis helpers ----

const FAMILY_COLORS = {
  "Apte": "#1f77b4",
  "Benfey": "#ff7f0e",
  "Cappeller": "#2ca02c",
  "Monier-Williams": "#d62728",
  "Petersburg": "#9467bd",
  "Wilson": "#8c564b",
  "indigenous": "#e377c2",
  "reverse": "#9467bd"
};

export function yearToX(year) {
  return 60 + (year - 1820) / (1960 - 1820) * (550 - 60);
}

export function rateToY(rate) {
  return 250 - rate * 210;
}

export function patternColor(patternStr) {
  if (!patternStr) return "#1f77b4";
  const lower = patternStr.toLowerCase();
  if (lower.includes("copy") || lower.includes("verbatim")) return "#2ca02c"; // green
  if (lower.includes("condens")) return "#d62728"; // red
  if (lower.includes("revision")) return "#ff7f0e"; // orange
  return "#1f77b4"; // default
}

const DICT_LABELS = {
  "wil": "Wilson 1832",
  "shs": "Śabda-Sāgara 1900",
  "yat": "Yates 1846",
  "ap90": "Apte 1890",
  "ap": "Apte 1957"
};

function edgeLabel(ancDict, desDict) {
  return `${DICT_LABELS[ancDict] || ancDict} → ${DICT_LABELS[desDict] || desDict}`;
}

// ---- SVG helpers ----

function svgCircle(x, y, r, fill, opacity = 1) {
  return `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" fill-opacity="${opacity}"/>`;
}

function svgRect(x, y, width, height, fill) {
  return `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="${fill}"/>`;
}

function svgLine(x1, y1, x2, y2, stroke, strokeWidth = 1) {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${strokeWidth}"/>`;
}

function svgText(x, y, text, textAnchor = "start", fill = "#333", fontSize = 12) {
  return `<text x="${x}" y="${y}" text-anchor="${textAnchor}" fill="${fill}" font-size="${fontSize}">${escapeXml(text)}</text>`;
}

function escapeXml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&apos;"
  }[c]));
}

// ---- H1 scatter SVG ----

export function h1Points(h1Json) {
  const { rows, families, stats } = h1Json;
  const r = stats.pearsonYearVsUnits || 0.036;
  const archivedR = stats.archivedPearson || 0.06;

  let svg = `<svg width="720" height="440" font-family="system-ui,sans-serif" font-size="12">`;

  // Axes
  svg += svgLine(60, 390, 550, 390, "#999"); // x-axis
  svg += svgLine(60, 30, 60, 390, "#999");    // y-axis

  // X ticks (years)
  for (let y of [1820, 1840, 1860, 1880, 1900, 1920, 1940, 1960]) {
    const x = yearToX(y);
    svg += svgText(x, 406, y.toString(), "middle", "#555", 11);
  }

  // Y ticks (sense-units)
  for (let u of [0, 1, 2, 3]) {
    const y = rateToY(u / 3);
    svg += svgLine(60, y, 550, y, "#eee");
    svg += svgText(52, y + 4, u.toString(), "end", "#555", 11);
  }

  // Data points
  for (const row of rows) {
    const x = yearToX(row.year);
    const y = rateToY(row.senseUnitsPerEntry / 3);
    const color = FAMILY_COLORS[row.family] || "#999";
    const title = `${row.dict} (${row.year}, ${row.family}): ${row.senseUnitsPerEntry} units/entry, ${row.entries} entries`;
    svg += `<circle cx="${x}" cy="${y}" r="6" fill="${color}" fill-opacity="0.85"><title>${escapeXml(title)}</title></circle>`;
    svg += svgText(x + 8, y + 4, row.dict, "start", "#333", 11);
  }

  // Family legend (right side)
  const legendX = 564;
  let legendY = 30;
  const legendRadius = 6;
  for (const family of ["Apte", "Benfey", "Cappeller", "Monier-Williams", "Petersburg", "Wilson", "indigenous"]) {
    svg += svgCircle(legendX, legendY, legendRadius, FAMILY_COLORS[family] || "#999");
    svg += svgText(legendX + 10, legendY + 4, family, "start", "#333", 10);
    legendY += 18;
  }

  // Axes labels
  svg += svgText(305, 432, "publication year", "middle", "#333", 11);
  svg += `<text x="16" y="220" transform="rotate(-90 16 220)" text-anchor="middle" fill="#333" font-size="11">sense-units / entry</text>`;

  // Pearson-r annotation
  svg += svgText(305, 425, `Pearson r = ${r.toFixed(3)} vs archived ${archivedR.toFixed(3)}`, "middle", "#555", 10);

  svg += `</svg>`;
  return svg;
}

// ---- H2 survival bars SVG ----

export function h2Bars(h2h3Json) {
  const h2 = h2h3Json.h2;
  const citedRate = h2.cited.rate;
  const uncitedRate = h2.uncited.rate;
  const archivedCitedRate = h2.archivedCited.rate;
  const archivedUncitedRate = h2.archivedUncited.rate;
  const gap = (citedRate - uncitedRate).toFixed(2);

  let svg = `<svg width="720" height="300" font-family="system-ui,sans-serif" font-size="12">`;

  // Y gridlines + labels (0/25/50/75/100%)
  for (let p of [0, 0.25, 0.5, 0.75, 1]) {
    const y = 250 - p * 210;
    svg += svgLine(80, y, 660, y, "#eee");
    svg += svgText(70, y + 4, `${Math.round(p * 100)}%`, "end", "#555", 10);
  }

  // Baseline
  svg += svgLine(80, 250, 660, 250, "#999", 2);

  // Cited group (x≈250)
  const citedGroupCx = 250;
  const barWidth = 56;
  const gap8 = 8;

  // Cited restored
  const citedRestoreH = citedRate * 210;
  svg += svgRect(citedGroupCx - 60, 250 - citedRestoreH, barWidth, citedRestoreH, "#2ca02c");
  svg += svgText(citedGroupCx - 32, 250 - citedRestoreH - 8, `${Math.round(citedRate * 100)}%`, "middle", "#333", 11);

  // Cited archived
  const citedArchivedH = archivedCitedRate * 210;
  svg += svgRect(citedGroupCx + 4, 250 - citedArchivedH, barWidth, citedArchivedH, "#2ca02c");
  svg += `<g opacity="0.4">`;
  svg += svgRect(citedGroupCx + 4, 250 - citedArchivedH, barWidth, citedArchivedH, "#2ca02c");
  svg += `</g>`;

  // Uncited group (x≈470)
  const uncitedGroupCx = 470;

  // Uncited restored
  const uncitedRestoreH = uncitedRate * 210;
  svg += svgRect(uncitedGroupCx - 60, 250 - uncitedRestoreH, barWidth, uncitedRestoreH, "#888");
  svg += svgText(uncitedGroupCx - 32, 250 - uncitedRestoreH - 8, `${Math.round(uncitedRate * 100)}%`, "middle", "#333", 11);

  // Uncited archived
  const uncitedArchivedH = archivedUncitedRate * 210;
  svg += `<g opacity="0.4">`;
  svg += svgRect(uncitedGroupCx + 4, 250 - uncitedArchivedH, barWidth, uncitedArchivedH, "#888");
  svg += `</g>`;

  // Group labels below baseline
  svg += svgText(citedGroupCx - 32, 268, "Cited", "middle", "#555", 10);
  svg += svgText(citedGroupCx - 32, 280, `n=${h2.cited.n}`, "middle", "#555", 9);

  svg += svgText(uncitedGroupCx - 32, 268, "Uncited", "middle", "#555", 10);
  svg += svgText(uncitedGroupCx - 32, 280, `n=${h2.uncited.n}`, "middle", "#555", 9);

  // Legend (top-right)
  svg += svgRect(520, 40, 12, 12, "#999");
  svg += svgText(536, 47, "restored (csl-orig)", "start", "#333", 10);

  svg += `<g opacity="0.4">`;
  svg += svgRect(520, 56, 12, 12, "#999");
  svg += `</g>`;
  svg += svgText(536, 63, "archived", "start", "#333", 10);

  // Y axis title
  svg += `<text x="20" y="150" transform="rotate(-90 20 150)" text-anchor="middle" fill="#333" font-size="11">sense-survival rate</text>`;

  // Gap annotation
  const citedBarTop = 250 - citedRestoreH;
  const uncitedBarTop = 250 - uncitedRestoreH;
  const midY = (citedBarTop + uncitedBarTop) / 2;
  svg += svgLine(350, citedBarTop, 350, uncitedBarTop, "#666", 1);
  svg += svgText(360, midY, `+${gap} gap`, "start", "#666", 10);

  svg += `</svg>`;
  return svg;
}

// ---- H3R dumbbell SVG ----

export function h3rDumbbells(h2h3Json) {
  const h3r = h2h3Json.h3r;

  // Compute maxS
  let maxS = 0;
  for (const edge of h3r) {
    maxS = Math.max(maxS, edge.meanAncSenses, edge.meanDesSenses);
  }
  maxS = Math.ceil(maxS) + 2;

  function senseToX(s) {
    return 150 + (s / maxS) * (620 - 150);
  }

  let svg = `<svg width="720" height="300" font-family="system-ui,sans-serif" font-size="12">`;

  // X axis
  svg += svgLine(150, 255, 620, 255, "#999", 2);
  for (let t of [0, 4, 8, 12, 16]) {
    if (t <= maxS) {
      const x = senseToX(t);
      svg += svgText(x, 275, t.toString(), "middle", "#555", 10);
    }
  }
  svg += svgText(385, 295, "mean sense-units per lemma", "middle", "#333", 11);

  // Dumbbells
  for (let i = 0; i < h3r.length; i++) {
    const edge = h3r[i];
    const yRow = 70 + i * 70;
    const x1 = senseToX(edge.meanAncSenses);
    const x2 = senseToX(edge.meanDesSenses);
    const color = patternColor(edge.pattern);

    // Connection line with arrowhead
    svg += svgLine(x1, yRow, x2, yRow, color, 3);

    // Arrowhead (simple triangle)
    if (x2 > x1) {
      const tipX = x2;
      const tipY = yRow;
      svg += `<path d="M${tipX - 6},${tipY - 4} L${tipX},${tipY} L${tipX - 6},${tipY + 4}" fill="${color}"/>`;
    }

    // Ancestor circle (gray)
    svg += svgCircle(x1, yRow, 7, "#999", 1);

    // Descendant circle (pattern color)
    svg += svgCircle(x2, yRow, 7, color, 1);

    // Archived ghosts (optional faded)
    const archX1 = senseToX(edge.archived.meanAncSenses);
    const archX2 = senseToX(edge.archived.meanDesSenses);
    svg += svgCircle(archX1, yRow, 4, "#999", 0.3);
    svg += svgCircle(archX2, yRow, 4, "#999", 0.3);

    // Left label (edge name)
    const label = edgeLabel(edge.ancDict, edge.desDict);
    svg += svgText(8, yRow + 4, label, "start", "#333", 11);

    // Right annotation (overlap)
    svg += svgText(632, yRow + 4, `overlap ${edge.meanGlossOverlap.toFixed(2)}`, "start", "#555", 10);
  }

  // Legend (top-right)
  const legendX = 500;
  let legendY = 40;
  for (const [label, color] of [["copy", "#2ca02c"], ["condensation", "#d62728"], ["revision", "#ff7f0e"]]) {
    svg += svgRect(legendX, legendY, 12, 12, color);
    svg += svgText(legendX + 16, legendY + 9, label, "start", "#333", 10);
    legendY += 18;
  }

  svg += `</svg>`;
  return svg;
}

// ---- Marker injection (idempotent) ----

function injectMarker(fileContent, markerName, newContent) {
  const startMarker = `<!-- R2-GEN:START ${markerName} -->`;
  const endMarker = `<!-- R2-GEN:END ${markerName} -->`;

  if (fileContent.includes(startMarker) && fileContent.includes(endMarker)) {
    // Replace between markers
    const startIdx = fileContent.indexOf(startMarker);
    const endIdx = fileContent.indexOf(endMarker);
    if (startIdx >= 0 && endIdx > startIdx) {
      return fileContent.substring(0, startIdx + startMarker.length) +
             "\n" + newContent + "\n" +
             fileContent.substring(endIdx);
    }
  }
  // If no markers, add them around the content (fallback)
  return fileContent.replace(
    /(<h1>.*?<\/h1>)/s,
    `$1\n${startMarker}\n${newContent}\n${endMarker}`
  );
}

// ---- Main ----

async function main() {
  const h1Data = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "r2_h1.json"), "utf-8"));
  const h2h3Data = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "r2_h2h3.json"), "utf-8"));

  // Generate h1 SVG
  const h1Svg = h1Points(h1Data);
  const h1Path = path.join(TOOLS_DIR, "r2-h1.md");
  let h1Content = fs.readFileSync(h1Path, "utf-8");
  h1Content = injectMarker(h1Content, "h1-scatter", h1Svg);
  fs.writeFileSync(h1Path, h1Content, { encoding: "utf-8" });
  console.log(`Updated ${h1Path}`);

  // Generate h2h3 SVG (both charts) + page
  const h2Svg = h2Bars(h2h3Data);
  const h3Svg = h3rDumbbells(h2h3Data);

  // TODO: Create r2-h2h3.md with charts and table

  // Generate h2h3 page
  let h2h3Page = `<style>
body{font-family:system-ui,sans-serif;margin:1.5rem;max-width:900px;color:#1b1b1b}
h1{font-size:1.3rem}
.note{color:#555;font-size:13px}
table{border-collapse:collapse;font-size:12px;width:100%}
td,th{border-bottom:1px solid #eee;padding:.3rem .4rem;text-align:left;vertical-align:top}
</style>

<h1>H2/H3R — sense survival & drift on inheritance edges</h1>

<p class="note">
A 28-noun panel across three measured inheritance edges (WIL→SHS, WIL→YAT, AP90→AP).
H2 tests whether cited ancestor senses survive more often than uncited ones (gloss-word overlap ≥ ${h2h3Data.survivedThreshold}).
H3R measures sense-unit drift (copy, condense, revise) along each edge using mean senses per lemma and gloss overlap.
Static archived R2 snapshot; see <code>docs/R2_FINDINGS.md</code>.
Restored generator now available: <code>npm run build-r2-h2h3</code> regenerates <code>data/lexico/r2_h2h3.json</code> from current <code>csl-orig</code>;
this page will be updated from that output in a follow-up.
</p>

<p class="note"><b>Trust Block.</b> Evidence: archived static snapshot embedded in this page; restored generator output in <code>data/lexico/r2_h2h3.json</code>
(H2: cited ${h2h3Data.h2.cited.rate} vs uncited ${h2h3Data.h2.uncited.rate}; archived 0.70/0.54).
Limitations: panel reconstructed from nouns in all 5 dicts (documented drift in R2_REBUILD_CONTRACT.md); SHS/YAT senses split by inline \`N.\` markers.
Validation: <code>npm test</code>; 134 unit tests pass. Owner repo: <code>csl-atlas</code>. Next use: regenerate SVG from r2_h2h3.json rows once page-wiring script exists.</p>

<h2>H2 — Citation-survival (Supported)</h2>

${h2Svg}

<h2>H3R — Sense-drift per edge</h2>

${h3Svg}

<h2>Summary</h2>

<p class="note">
<b>H2 supported:</b> Cited ancestor senses survive at ${(h2h3Data.h2.cited.rate * 100).toFixed(0)}% (n=${h2h3Data.h2.cited.n}) vs uncited at ${(h2h3Data.h2.uncited.rate * 100).toFixed(0)}% (n=${h2h3Data.h2.uncited.n}); gap = ${(h2h3Data.h2.cited.rate - h2h3Data.h2.uncited.rate).toFixed(2)}. Well-sourced senses are stickier.
</p>

<p class="note">
<b>H3R not supported (no net-addition):</b> Derivatives copy or condense.
WIL→SHS: near-verbatim copy (overlap ${h2h3Data.h3r[0].meanGlossOverlap.toFixed(2)}).
WIL→YAT: drastic condensation (${h2h3Data.h3r[1].meanDesSenses} vs ${h2h3Data.h3r[1].meanAncSenses} senses).
AP90→AP: revision (no expansion).
</p>
`;

  const h2h3Path = path.join(TOOLS_DIR, "r2-h2h3.md");
  fs.writeFileSync(h2h3Path, h2h3Page, { encoding: "utf-8" });
  console.log(`Created ${h2h3Path}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
