import test from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fig2AlignmentAnchor } from "../scripts/build-r2-paper-figures.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function loadAlign(lemma) {
  return JSON.parse(fs.readFileSync(path.join(repoRoot, "data", "lexico", `r2_align_${lemma}.json`), "utf-8"));
}

test("fig2AlignmentAnchor renders both pinned §4 examples with IAST anchors", () => {
  const svg = fig2AlignmentAnchor({ dharma: loadAlign("dharma"), bodhisattva: loadAlign("bodhisattva") });
  assert.ok(svg.includes("<svg"), "output should contain SVG tag");
  // Panel A: Apte cross-edition identity alignment (paper §4, first example)
  assert.ok(svg.includes("J = 1"), "ap#4 ~ ap90#4 should align at Jaccard 1.0");
  assert.ok(svg.includes("ṣaṣṭhāṃśavṛtterapi"), "shared content word rendered in IAST, not SLP1");
  assert.ok(svg.includes("Ms. 1. 114"), "shared citation anchor present");
  // Panel B: cross-tradition German ~ Sanskrit alignment (paper §4, bodhisattva example)
  assert.ok(svg.includes("jīmūtavāhanāt"), "cross-tradition anchor rendered in IAST");
  assert.ok(svg.includes("Śabdakalpadruma"), "indigenous side labeled");
  assert.ok(!/\b(?:ls|sig|s):[A-Za-z]/.test(svg), "no raw anchor-token prefixes leak into the figure");
});

test("fig2AlignmentAnchor fails loudly when a pinned alignment row is missing", () => {
  const dharma = loadAlign("dharma");
  const gutted = { ...dharma, alignments: dharma.alignments.filter(r => !(r.a === "ap#4" && r.b === "ap90#4")) };
  assert.throws(
    () => fig2AlignmentAnchor({ dharma: gutted, bodhisattva: loadAlign("bodhisattva") }),
    /no longer reproduces/,
    "missing pinned row must be a hard error, not a silent fallback"
  );
});

test("committed paper-figure SVGs are current for the committed data", () => {
  const fig2Path = path.join(repoRoot, "docs", "figures", "r2_fig2_alignment_anchor.svg");
  const committed = fs.readFileSync(fig2Path, "utf-8").replace(/\r\n/g, "\n");
  const regenerated = (`<?xml version="1.0" encoding="UTF-8"?>\n` +
    fig2AlignmentAnchor({ dharma: loadAlign("dharma"), bodhisattva: loadAlign("bodhisattva") })
      .replace("<svg ", `<svg xmlns="http://www.w3.org/2000/svg" `)).replace(/\r\n/g, "\n");
  assert.equal(committed, regenerated, "docs/figures/r2_fig2_alignment_anchor.svg has drifted — re-run npm run build-r2-paper-figures");
});
