// Generate the two PAPER_SENSE_ALIGNMENT figures as standalone SVG files.
//
// Reads:
//   - data/lexico/r2_h1_panel.json      → Figure 1: fixed-panel H1 scatter
//   - data/lexico/r2_align_dharma.json  → Figure 2 panel A: ap#4 ~ ap90#4 (cross-edition, J=1)
//   - data/lexico/r2_align_bodhisattva.json → Figure 2 panel B: pwg#preface ~ skd#2 (cross-tradition)
//
// Writes docs/figures/r2_fig1_h1_panel.svg and docs/figures/r2_fig2_alignment_anchor.svg.
// Deterministic: same inputs → byte-identical output. The Figure 2 alignment rows are
// pinned by sense-id pair; if a pinned row disappears after a data refresh the script
// fails loudly — that is a regression signal for the paper's §4 examples, not a case
// to paper over with a fallback.
//
// Usage: npm run build-r2-paper-figures

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { h1PanelPoints } from "./build-r2-pages.mjs";
import { slp1ToIast } from "../src/lib/lookup-normalize.js";

const DATA_DIR = "data/lexico";
const FIG_DIR = "docs/figures";

function escapeXml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;"
  }[c]));
}

function standalone(svg) {
  // The page-embedded SVGs omit xmlns; a standalone .svg file needs it.
  return `<?xml version="1.0" encoding="UTF-8"?>\n` +
    svg.replace("<svg ", `<svg xmlns="http://www.w3.org/2000/svg" `)
      .replace("<svg ", match => match); // idempotent single replace
}

// ---- Figure 2: anchor-alignment examples ----

function findAlignment(alignJson, aId, bId) {
  const row = (alignJson.alignments || []).find(r => r.a === aId && r.b === bId);
  if (!row) {
    throw new Error(
      `Pinned alignment ${aId} ~ ${bId} not found in current data — ` +
      `the paper's §4 example no longer reproduces; investigate before regenerating figures.`
    );
  }
  return row;
}

function findSense(alignJson, dict, senseId) {
  const rec = (alignJson.senses[dict] || []).find(s => String(s.sense) === String(senseId));
  if (!rec) throw new Error(`Sense ${dict}#${senseId} not found in current data.`);
  return rec;
}

function anchorLabel(token) {
  // "s:zazWAMSavftterapi" → IAST content word; "ls:Ms. 1. 114" → citation as-is.
  if (token.startsWith("ls:")) return { text: token.slice(3), kind: "cite" };
  if (token.startsWith("sig:")) return { text: token.slice(4), kind: "sig" };
  if (token.startsWith("s:")) return { text: slp1ToIast(token.slice(2)), kind: "skt" };
  return { text: token, kind: "skt" };
}

function wrapText(text, maxChars) {
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const w of words) {
    if ((line + " " + w).trim().length > maxChars) {
      lines.push(line.trim());
      line = w;
      if (lines.length >= 3) {
        lines[2] = lines[2].replace(/\s*$/, "") ;
        return { lines, truncated: words.length > 0 };
      }
    } else {
      line = (line + " " + w).trim();
    }
  }
  if (line) lines.push(line);
  return { lines: lines.slice(0, 3), truncated: false };
}

function senseBox(x, y, width, heading, cluster, text) {
  const CHIP = { western: "#1f77b4", indigenous: "#e377c2", reverse: "#9467bd" };
  const { lines } = wrapText(text.length > 200 ? text.slice(0, 200) + "…" : text, 46);
  let svg = `<rect x="${x}" y="${y}" width="${width}" height="86" rx="6" fill="#fff" stroke="#bbb"/>`;
  svg += `<text x="${x + 10}" y="${y + 18}" font-size="12" font-weight="bold" fill="#333">${escapeXml(heading)}</text>`;
  svg += `<rect x="${x + width - 84}" y="${y + 7}" width="74" height="15" rx="7" fill="${CHIP[cluster] || "#999"}" fill-opacity="0.15"/>`;
  svg += `<text x="${x + width - 47}" y="${y + 18}" font-size="9" text-anchor="middle" fill="${CHIP[cluster] || "#999"}">${escapeXml(cluster)}</text>`;
  let ty = y + 38;
  for (const line of lines) {
    svg += `<text x="${x + 10}" y="${ty}" font-size="10.5" fill="#555">${escapeXml(line)}</text>`;
    ty += 15;
  }
  return svg;
}

function anchorChips(cx, y, tokens, maxTokens) {
  const shown = tokens.slice(0, maxTokens);
  const extra = tokens.length - shown.length;
  const CHIP_COLORS = { cite: "#8c564b", skt: "#2ca02c", sig: "#e377c2" };
  let svg = "";
  let cy = y;
  for (const token of shown) {
    const { text, kind } = anchorLabel(token);
    const label = text.length > 26 ? text.slice(0, 25) + "…" : text;
    const w = Math.max(56, label.length * 6.4 + 16);
    const color = CHIP_COLORS[kind];
    svg += `<rect x="${cx - w / 2}" y="${cy}" width="${w}" height="18" rx="9" fill="${color}" fill-opacity="0.12" stroke="${color}" stroke-width="0.8"/>`;
    svg += `<text x="${cx}" y="${cy + 13}" font-size="10" text-anchor="middle" fill="${color}"${kind === "skt" ? ` font-style="italic"` : ""}>${escapeXml(label)}</text>`;
    cy += 24;
  }
  if (extra > 0) {
    svg += `<text x="${cx}" y="${cy + 12}" font-size="10" text-anchor="middle" fill="#888">+${extra} more</text>`;
  }
  return svg;
}

export function fig2AlignmentAnchor({ dharma, bodhisattva }) {
  const panels = [
    {
      title: "A — same tradition, two editions (dharma): identical sense, Jaccard 1.0",
      row: findAlignment(dharma, "ap#4", "ap90#4"),
      left: { heading: "Apte 1957 · sense 4", rec: findSense(dharma, "ap", "4") },
      right: { heading: "Apte 1890 · sense 4", rec: findSense(dharma, "ap90", "4") }
    },
    {
      title: "B — across tradition and language (bodhisattva): German gloss ~ Sanskrit exposition",
      row: findAlignment(bodhisattva, "pwg#preface", "skd#2"),
      left: { heading: "PWG 1855 (German)", rec: findSense(bodhisattva, "pwg", "preface") },
      right: { heading: "Śabdakalpadruma 1822 (Sanskrit)", rec: findSense(bodhisattva, "skd", "2") }
    }
  ];

  let svg = `<svg width="760" height="470" font-family="system-ui,sans-serif" font-size="12">`;
  svg += `<rect x="0" y="0" width="760" height="470" fill="#fdfdfd"/>`;

  let py = 18;
  for (const panel of panels) {
    svg += `<text x="16" y="${py + 4}" font-size="12" font-weight="bold" fill="#333">${escapeXml(panel.title)}</text>`;
    const boxY = py + 16;
    svg += senseBox(16, boxY, 250, panel.left.heading, panel.left.rec.cluster, panel.left.rec.text);
    svg += senseBox(494, boxY, 250, panel.right.heading, panel.right.rec.cluster, panel.right.rec.text);
    // Connector through the shared-anchor column
    svg += `<line x1="266" y1="${boxY + 43}" x2="494" y2="${boxY + 43}" stroke="#2ca02c" stroke-width="1.4" stroke-dasharray="5,4" opacity="0.55"/>`;
    svg += `<text x="380" y="${boxY - 2}" font-size="10" text-anchor="middle" fill="#555">shared Sanskrit anchors · J = ${panel.row.j}</text>`;
    svg += anchorChips(380, boxY + 8, panel.row.shared, 5);
    py = boxY + 190;
  }

  // Legend
  svg += `<text x="16" y="452" font-size="10" fill="#666">anchors:</text>`;
  svg += `<rect x="66" y="443" width="10" height="10" rx="5" fill="#2ca02c" fill-opacity="0.12" stroke="#2ca02c" stroke-width="0.8"/>`;
  svg += `<text x="80" y="452" font-size="10" fill="#2ca02c" font-style="italic">Sanskrit content word (IAST)</text>`;
  svg += `<rect x="240" y="443" width="10" height="10" rx="5" fill="#8c564b" fill-opacity="0.12" stroke="#8c564b" stroke-width="0.8"/>`;
  svg += `<text x="254" y="452" font-size="10" fill="#8c564b">citation siglum</text>`;
  svg += `<text x="380" y="452" font-size="10" fill="#666">— alignment uses no translation: fingerprints are Sanskrit-side only</text>`;
  svg += `</svg>`;
  return svg;
}

// ---- Main ----

async function main() {
  fs.mkdirSync(FIG_DIR, { recursive: true });

  const panelData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "r2_h1_panel.json"), "utf-8"));
  const fig1 = standalone(h1PanelPoints(panelData));
  const fig1Path = path.join(FIG_DIR, "r2_fig1_h1_panel.svg");
  fs.writeFileSync(fig1Path, fig1, { encoding: "utf-8" });
  console.log(`Wrote ${fig1Path}`);

  const dharma = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "r2_align_dharma.json"), "utf-8"));
  const bodhisattva = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "r2_align_bodhisattva.json"), "utf-8"));
  const fig2 = standalone(fig2AlignmentAnchor({ dharma, bodhisattva }));
  const fig2Path = path.join(FIG_DIR, "r2_fig2_alignment_anchor.svg");
  fs.writeFileSync(fig2Path, fig2, { encoding: "utf-8" });
  console.log(`Wrote ${fig2Path}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
