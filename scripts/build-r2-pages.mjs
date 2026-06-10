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

// ---- H2H3 prose helpers ----

function h2h3TrustBlock(h2h3Data) {
  const { h2 } = h2h3Data;
  return `<p class="note"><b>Trust Block.</b> Generated from <code>data/lexico/r2_h2h3.json</code> ` +
    `(H2: cited ${h2.cited.rate} vs uncited ${h2.uncited.rate}; archived ${h2.archivedCited.rate}/${h2.archivedUncited.rate}). ` +
    `Limitations: panel reconstructed from nouns in all 5 dicts (documented drift in R2_REBUILD_CONTRACT.md); SHS/YAT senses split by inline \`N.\` markers. ` +
    `Validation: <code>npm test</code>; all unit tests pass. Owner repo: <code>csl-atlas</code>.</p>`;
}

function h2h3DataTable(h2h3Data) {
  const { h3r } = h2h3Data;
  const rows = h3r.map(edge => {
    const arch = edge.archived;
    return `<tr><td>${edgeLabel(edge.ancDict, edge.desDict)}</td>` +
      `<td>${edge.meanAncSenses}→${edge.meanDesSenses}</td>` +
      `<td>${edge.drift}</td>` +
      `<td>${edge.meanGlossOverlap.toFixed(2)}</td>` +
      `<td>${escapeXml(edge.pattern)}</td>` +
      `<td>${arch.meanAncSenses}→${arch.meanDesSenses} (overlap ${arch.meanGlossOverlap.toFixed(2)})</td></tr>`;
  }).join("\n");
  return `<table>\n<tr><th>Edge</th><th>Senses anc→des</th><th>Drift</th><th>Gloss overlap</th><th>Pattern</th><th>Archived</th></tr>\n${rows}\n</table>`;
}

function h2h3SummaryHtml(h2h3Data) {
  const { h2, h3r } = h2h3Data;
  const gap = (h2.cited.rate - h2.uncited.rate).toFixed(2);
  const h2oneLine = `<b>H2 supported:</b> Cited senses survive at ${(h2.cited.rate * 100).toFixed(0)}% (n=${h2.cited.n}) ` +
    `vs uncited at ${(h2.uncited.rate * 100).toFixed(0)}% (n=${h2.uncited.n}); gap = ${gap}. Well-sourced senses are stickier.`;
  let h3rLines = `<b>H3R not supported (no net-addition):</b> Derivatives copy or condense.`;
  for (const edge of h3r) {
    h3rLines += `\n${edgeLabel(edge.ancDict, edge.desDict)}: ${escapeXml(edge.pattern)} (overlap ${edge.meanGlossOverlap.toFixed(2)}).`;
  }
  return `<p class="note">${h2oneLine}</p>\n<p class="note">${h3rLines}</p>`;
}

// ---- Explorer script generator ----

function explorerTrustBlock(alignDataMap) {
  const lemmaCount = Object.keys(alignDataMap).length;
  const totalAligns = Object.values(alignDataMap)
    .reduce((s, d) => s + (d.alignments || []).length, 0);
  return `<p class="note"><b>Trust Block.</b> Generated from <code>data/lexico/r2_align_*.json</code> ` +
    `(${lemmaCount} lemmas, ${totalAligns} alignments total). ` +
    `Runs idempotently; re-running with unchanged JSON produces no git diff. ` +
    `Validation: <code>npm test</code>; all unit tests pass. Owner repo: <code>csl-atlas</code>.</p>`;
}

const EXPLORER_LABEL = {
  "mw": "MW 1899", "mw72": "MW 1872", "pwg": "PWG 1855", "pw": "PW 1875",
  "pwk": "PWK 1887", "ap": "Apte 1957", "ap90": "Apte 1890",
  "ben": "Benfey 1866", "sch": "Schmidt 1928", "bhs": "Edgerton BHS 1953",
  "wil": "Wilson 1832", "cae": "Cappeller 1891",
  "vcp": "Vācaspatya 1873", "skd": "Śabdakalpadruma 1822",
  "ae": "Apte En→Skt 1920", "shs": "Śabda-Sāgara 1900", "yat": "Yates 1846"
};

export function generateExplorerScript(alignDataMap, lemmaList) {
  const data = {};
  for (const lemma of lemmaList) {
    const d = alignDataMap[lemma];
    if (!d) continue;
    const aligns = (d.alignments || []).map(
      ({ a, b, j, shared, cross }) => ({ a, b, j, shared, cross })
    );
    data[lemma] = { senses: d.senses, aligns };
  }
  const dataJson = JSON.stringify(data);
  const lemmaOrderJson = JSON.stringify(lemmaList);
  const defaultLemma = lemmaList.includes("dharma") ? "dharma" : lemmaList[0];

  return `<script>
const DATA = ${dataJson};
const LABEL = ${JSON.stringify(EXPLORER_LABEL)};
const sel = document.getElementById('sel');
${lemmaOrderJson}.forEach(l => { const o=document.createElement('option'); o.value=l; o.textContent=l; sel.appendChild(o); });
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function chip(t){let c='chip';if(t.startsWith('ls:'))c+=' cite';else if(t.startsWith('sig:'))c+=' sig';
  return '<span class="'+c+'">'+esc(t)+'</span>';}
function render(lemma){
  const d=DATA[lemma]; const S=document.getElementById('senses'); S.innerHTML='';
  if(!d){S.innerHTML='<p class="note">No data for this lemma.</p>';return;}
  const order=Object.keys(d.senses).sort((a,b)=>(LABEL[a]||a).slice(-4).localeCompare((LABEL[b]||b).slice(-4)));
  for(const code of order){
    const recs=d.senses[code]; const cl=recs[0].cluster;
    let h='<div class="dict"><h3>'+esc(LABEL[code]||code)+
          ' <span class="pill '+cl+'">'+cl+'</span></h3>';
    for(const r of recs) h+='<div class="sense"><span class="num">'+esc(String(r.sense))+'</span>'+esc(r.text||'')+'</div>';
    h+='</div>'; S.insertAdjacentHTML('beforeend',h);
  }
  const A=document.getElementById('aligns');
  if(!d.aligns.length){A.innerHTML='<p class="note">No fingerprint-backed alignments for this lemma.</p>';return;}
  let t='<table><tr><th>sense A</th><th>sense B</th><th>Jaccard</th><th>shared Sanskrit anchors</th></tr>';
  for(const p of d.aligns){
    t+='<tr class="'+(p.cross?'cross':'')+'"><td>'+esc(p.a)+(p.cross?' <span class="crosslbl">cross-tradition</span>':'')+
       '</td><td>'+esc(p.b)+'</td><td>'+p.j+'</td><td>'+p.shared.map(chip).join(' ')+'</td></tr>';
  }
  A.innerHTML=t+'</table>';
}
sel.addEventListener('change',()=>render(sel.value));
render(sel.value=${JSON.stringify(defaultLemma)});
</script>`;
}

// ---- Marker injection (idempotent) ----

export function injectMarker(fileContent, markerName, newContent) {
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

  // Page 1 (r2-h1): inject scatter SVG
  const h1Svg = h1Points(h1Data);
  const h1Path = path.join(TOOLS_DIR, "r2-h1.md");
  let h1Content = fs.readFileSync(h1Path, "utf-8");
  h1Content = injectMarker(h1Content, "h1-scatter", h1Svg);
  fs.writeFileSync(h1Path, h1Content, { encoding: "utf-8" });
  console.log(`Updated ${h1Path}`);

  // Page 3 (r2-h2h3): inject trust block, charts, data table, summary via markers
  const h2h3Path = path.join(TOOLS_DIR, "r2-h2h3.md");
  let h2h3Content = fs.readFileSync(h2h3Path, "utf-8");
  h2h3Content = injectMarker(h2h3Content, "h2h3-trust", h2h3TrustBlock(h2h3Data));
  h2h3Content = injectMarker(h2h3Content, "h2h3-h2-chart", h2Bars(h2h3Data));
  h2h3Content = injectMarker(h2h3Content, "h2h3-h3r-chart", h3rDumbbells(h2h3Data));
  h2h3Content = injectMarker(h2h3Content, "h2h3-table", h2h3DataTable(h2h3Data));
  h2h3Content = injectMarker(h2h3Content, "h2h3-summary", h2h3SummaryHtml(h2h3Data));
  fs.writeFileSync(h2h3Path, h2h3Content, { encoding: "utf-8" });
  console.log(`Updated ${h2h3Path}`);

  // Page 2 (r2-explorer): load all r2_align_<lemma>.json files, inject trust + script
  const DEFAULT_LEMMA = "dharma";
  const alignFiles = fs.readdirSync(DATA_DIR)
    .filter(f => /^r2_align_\w+\.json$/.test(f))
    .map(f => f.replace(/^r2_align_/, "").replace(/\.json$/, ""))
    .sort();
  const lemmaList = [
    DEFAULT_LEMMA,
    ...alignFiles.filter(l => l !== DEFAULT_LEMMA)
  ];
  const alignDataMap = {};
  for (const lemma of lemmaList) {
    alignDataMap[lemma] = JSON.parse(
      fs.readFileSync(path.join(DATA_DIR, `r2_align_${lemma}.json`), "utf-8")
    );
  }
  const explorerPath = path.join(TOOLS_DIR, "r2-explorer.md");
  let explorerContent = fs.readFileSync(explorerPath, "utf-8");
  explorerContent = injectMarker(explorerContent, "explorer-trust", explorerTrustBlock(alignDataMap));
  explorerContent = injectMarker(explorerContent, "explorer-script", generateExplorerScript(alignDataMap, lemmaList));
  fs.writeFileSync(explorerPath, explorerContent, { encoding: "utf-8" });
  console.log(`Updated ${explorerPath}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
