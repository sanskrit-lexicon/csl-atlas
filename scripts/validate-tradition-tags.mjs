// Validate the tradition-community packet (H340, agenda backlog #9).
//
// Fails (exit 1) when:
// - the output JSON / source envelope is missing or unparseable;
// - a tagged text is missing from the citation node table (unknown text);
// - a tradition is outside the closed vocabulary;
// - per-dict tradition-share sums diverge from the per-dict tagged-cites total;
// - the review-state counts (reviewed, byConfidence) disagree with the rows;
// - reviewStatus is inconsistent with the reviewed count;
// - a per-dict taggedCites exceeds its totalInGraphCites.
//
// Usage: npm run validate-tradition-tags   (run after build-tradition-tags)

import fs from "node:fs";
import path from "node:path";
import { parseTsv, TRADITION_VOCAB } from "./build-tradition-tags.mjs";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "citations");
const JSON_OUT = path.join(OUT_DIR, "tradition_tags.json");
const SOURCE_OUT = path.join(OUT_DIR, "tradition_tags.source.json");
const NODES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_nodes.tsv");
const TAGS_PATH = path.resolve(process.cwd(), "data", "citations", "tradition_tags.tsv");

const errors = [];
const notes = [];

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON ${path.relative(process.cwd(), file)}: ${e.message}`);
    return null;
  }
}

const packet = readJson(JSON_OUT);
const envelope = readJson(SOURCE_OUT);

if (packet) {
  const nodeTexts = new Set(parseTsv(fs.readFileSync(NODES_PATH, "utf8")).map((r) => r.canonical_text));
  const tagRows = parseTsv(fs.readFileSync(TAGS_PATH, "utf8"));

  // Row count matches.
  if (packet.taggedTexts.length !== tagRows.length) {
    errors.push(`taggedTexts count ${packet.taggedTexts.length} != TSV rows ${tagRows.length}`);
  }

  // Every tagged text exists in the node table; every tradition is in vocab.
  for (const t of packet.taggedTexts) {
    if (!nodeTexts.has(t.text)) errors.push(`tagged text not in node table: "${t.text}"`);
    if (!TRADITION_VOCAB.includes(t.tradition)) errors.push(`tradition outside vocabulary: "${t.tradition}" (${t.text})`);
    if (!["high", "medium", "low"].includes(t.confidence)) errors.push(`bad confidence "${t.confidence}" (${t.text})`);
  }

  // Per-dict tradition shares sum to the tagged-cites total; coverage sane.
  for (const d of packet.perDict) {
    const sumCites = d.byTradition.reduce((a, s) => a + s.cites, 0);
    if (sumCites !== d.taggedCites) errors.push(`${d.dict}: byTradition cites ${sumCites} != taggedCites ${d.taggedCites}`);
    if (d.taggedCites > d.totalInGraphCites) errors.push(`${d.dict}: taggedCites ${d.taggedCites} > totalInGraphCites ${d.totalInGraphCites}`);
    const sumShare = d.byTradition.reduce((a, s) => a + s.share, 0);
    if (d.byTradition.length && Math.abs(sumShare - 1) > 0.01) errors.push(`${d.dict}: shares sum ${sumShare.toFixed(3)} != 1`);
  }

  // Review-state counts consistent with rows.
  const reviewed = packet.taggedTexts.filter((t) => t.reviewed).length;
  if (reviewed !== packet.reviewState.reviewed) errors.push(`reviewState.reviewed ${packet.reviewState.reviewed} != counted ${reviewed}`);
  const conf = { high: 0, medium: 0, low: 0 };
  for (const t of packet.taggedTexts) conf[t.confidence] += 1;
  for (const k of Object.keys(conf)) {
    if (conf[k] !== packet.reviewState.byConfidence[k]) errors.push(`byConfidence.${k} ${packet.reviewState.byConfidence[k]} != counted ${conf[k]}`);
  }
  const allReviewed = reviewed === packet.taggedTexts.length && packet.taggedTexts.length > 0;

  // H1684 — review PROVENANCE. The load-bearing check is the last one: the map
  // may only call itself human-reviewed when every reviewed row was read by a
  // human. Agent verdicts promoted through the Wilson gate are real review, but
  // they are not that claim, and a bare `reviewed` boolean cannot tell them
  // apart — which is exactly how an agent pass could silently upgrade its own
  // evidence label.
  const agentReviewed = packet.taggedTexts.filter((t) => t.reviewed && (t.reviewedBy || "") !== "human").length;
  const expectStatus = !allReviewed
    ? "inferred-pending-review"
    : agentReviewed > 0 ? "agent-adjudicated-human-gated" : "human-reviewed";
  const expectLabel = !allReviewed
    ? "inferred"
    : agentReviewed > 0 ? "agent-adjudicated" : "human-verified";
  if (packet.reviewStatus !== expectStatus) errors.push(`reviewStatus "${packet.reviewStatus}" inconsistent with ${reviewed}/${packet.taggedTexts.length} reviewed, ${agentReviewed} agent-attributed (expected "${expectStatus}")`);
  if (packet.evidenceLabel !== expectLabel) errors.push(`evidenceLabel "${packet.evidenceLabel}" inconsistent with review state (expected "${expectLabel}")`);
  if (packet.reviewState && packet.reviewState.agentReviewed !== agentReviewed) errors.push(`reviewState.agentReviewed ${packet.reviewState.agentReviewed} != counted ${agentReviewed}`);
  for (const t of packet.taggedTexts) {
    if (t.reviewed && !t.reviewedBy) errors.push(`row marked reviewed with no reviewed_by provenance: "${t.text}"`);
    if (!t.reviewed && t.reviewedBy) errors.push(`row carries reviewed_by "${t.reviewedBy}" but is not marked reviewed: "${t.text}"`);
  }
  if (allReviewed && agentReviewed > 0 && packet.reviewStatus === "human-reviewed") {
    errors.push("packet claims human-reviewed while carrying agent-attributed rows");
  }

  // Traditions in use are a subset of vocab, sorted by cites desc.
  for (const tr of packet.traditions) {
    if (!TRADITION_VOCAB.includes(tr.tradition)) errors.push(`traditions[] outside vocabulary: "${tr.tradition}"`);
  }

  notes.push(`${packet.taggedTexts.length} tagged texts, ${packet.traditions.length} traditions in use, ${reviewed} reviewed, status ${packet.reviewStatus}`);
}

if (envelope && packet && envelope.generatedAt !== packet.generatedAt) {
  errors.push("source envelope generatedAt does not match packet generatedAt");
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length) {
  console.error(`validate-tradition-tags: ${errors.length} error(s):`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log("validate-tradition-tags: OK");
