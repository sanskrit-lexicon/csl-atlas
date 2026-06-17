// Benchmark harness (Month 6) — review-queue precision + model benchmarks.
//
// A leaderboard-style report over the review layer: for every queue it measures
// the MACHINE precision against the human-reviewed gold subset — `reviewed-ok`
// means the machine verdict held up, `reviewed-corrected` means a human
// overrode it, so precision = reviewed-ok / (reviewed-ok + reviewed-corrected).
// It fills in as reviewers work; today most Dharmamitra cross-checks have zero
// gold, so they read "pending review" — the framework is what's delivered.
//
// It also surfaces known MODEL benchmarks (the German-aware langdetect held-out
// accuracy from #115). The ByT5 task accuracies (gender / lemma / segmentation),
// and an external comparison via dharmamitra-leaderboard, need a GPU run of the
// model on a gold corpus — recorded as pending.
//
// Deterministic, reads committed review JSON. Output is a report, not a review
// queue (no schema validation). Usage: npm run build-benchmark-report.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const ROOT = process.cwd();
const REVIEW_DIR = path.resolve(ROOT, "src", "data", "review");
const LANGDETECT_METRICS = path.resolve(ROOT, "src", "data", "external", "langdetect-german-metrics.json");
const OUTPUT = path.resolve(ROOT, "src", "data", "benchmark-report.json");

// Queues that ARE Dharmamitra cross-check outputs (vs underlying atlas queues / other work).
const DHARMAMITRA_QUEUES = new Set([
  "pos-gender-model-crosscheck", "source-layer-anchoring", "compound-depth-crosscheck",
  "lemma-normalization-crosscheck", "langdetect-markup-crosscheck", "citation-link-target",
  "source-date-anchor"
]);
const HUMAN_OK = "reviewed-ok";
const HUMAN_FIX = "reviewed-corrected";

function readJson(f) { return JSON.parse(fs.readFileSync(f, "utf8")); }

function main() {
  const queues = [];
  for (const file of fs.readdirSync(REVIEW_DIR).filter(f => f.endsWith(".json")).sort()) {
    const doc = readJson(path.join(REVIEW_DIR, file));
    const items = doc.items || [];
    const statusCounts = {};
    for (const it of items) statusCounts[it.reviewStatus] = (statusCounts[it.reviewStatus] || 0) + 1;
    const ok = statusCounts[HUMAN_OK] || 0;
    const fix = statusCounts[HUMAN_FIX] || 0;
    const gold = ok + fix;
    queues.push({
      queue: doc.queue || file.replace(/-review\.json$/, ""),
      file: `src/data/review/${file}`,
      dharmamitra: DHARMAMITRA_QUEUES.has(doc.queue),
      total: items.length,
      gold,
      coverage: items.length ? Number((gold / items.length).toFixed(4)) : 0,
      precision: gold ? Number((ok / gold).toFixed(4)) : null,   // machine verdict accept rate
      statusCounts
    });
  }

  // Known model benchmarks.
  const modelBenchmarks = {};
  if (fs.existsSync(LANGDETECT_METRICS)) {
    const m = readJson(LANGDETECT_METRICS);
    modelBenchmarks.langdetectGerman = {
      task: "PWG Sanskrit-vs-German classification (held-out)",
      baselineAccuracy: m.baseline_eng_vs_skt?.accuracy ?? null,
      germanAwareAccuracy: m.germanAware_san_vs_deu?.accuracy ?? null,
      accuracyLift: m.accuracyLift ?? null,
      source: "src/data/external/langdetect-german-metrics.json (#115)"
    };
  }
  modelBenchmarks.byt5Pending = {
    note: "ByT5 task accuracy (gender / lemma / segmentation) and an external comparison via dharmamitra-leaderboard need a GPU run of the model on a gold corpus.",
    blockedOn: "GPU (no torch/transformers in-session)"
  };

  const dh = queues.filter(q => q.dharmamitra);
  const dhGold = dh.reduce((s, q) => s + q.gold, 0);
  const allGold = queues.reduce((s, q) => s + q.gold, 0);
  const allOk = queues.reduce((s, q) => s + (q.statusCounts[HUMAN_OK] || 0), 0);

  const payload = {
    schemaVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    generatedBy: "npm run build-benchmark-report",
    method: "Per review queue: precision = reviewed-ok / (reviewed-ok + reviewed-corrected) over the human-reviewed gold subset; coverage = gold / total. Fills in as reviewers adjudicate.",
    summary: {
      queueCount: queues.length,
      totalItems: queues.reduce((s, q) => s + q.total, 0),
      totalGold: allGold,
      overallPrecision: allGold ? Number((allOk / allGold).toFixed(4)) : null,
      dharmamitraQueues: dh.length,
      dharmamitraGold: dhGold,
      dharmamitraGoldPending: dhGold === 0
    },
    queues: queues.sort((a, b) => (b.gold - a.gold) || (b.total - a.total)),
    modelBenchmarks,
    notes: [
      "precision here is the machine-verdict accept rate under human review, not classifier precision on an external gold set.",
      "Most Dharmamitra cross-checks have zero gold today (pending review); this report is the framework that scores them as reviews land.",
      "The langdetect German model has a real held-out benchmark (#115); the ByT5 queues need a GPU run for task-level accuracy."
    ]
  };

  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUTPUT, fs), payload);
  fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
  fs.writeFileSync(OUTPUT, `${JSON.stringify(payload, null, 2)}\n`);

  // Console leaderboard.
  console.log(`Benchmark report: ${payload.summary.queueCount} queues, ${payload.summary.totalItems} items, ${allGold} human-reviewed (gold).`);
  console.log("  queue".padEnd(36) + "total".padStart(7) + "gold".padStart(7) + "prec".padStart(8) + "  dh");
  for (const q of payload.queues) {
    console.log("  " + q.queue.padEnd(34) + String(q.total).padStart(7) + String(q.gold).padStart(7) +
      (q.precision == null ? "    —" : q.precision.toFixed(3)).padStart(8) + "  " + (q.dharmamitra ? "✓" : ""));
  }
  if (modelBenchmarks.langdetectGerman) {
    const l = modelBenchmarks.langdetectGerman;
    console.log(`  model: langdetect-german accuracy ${l.baselineAccuracy} -> ${l.germanAwareAccuracy} (lift ${l.accuracyLift})`);
  }
  console.log(`Wrote ${path.relative(ROOT, OUTPUT)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
