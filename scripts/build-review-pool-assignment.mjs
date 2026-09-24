// B6 (H5308, design §5) — deal the three blocked packets to the review pool with
// the rotating-offset rule: for row i, key A = annotator[i % n],
// key B = annotator[(i % n + 1 + (i // n) % (n - 1)) % n]. Deterministic, no RNG,
// never the same annotator twice on one row, exact load balance, rotating partners.
// Usage: node scripts/build-review-pool-assignment.mjs --annotators pool-a01,pool-a02[,…]
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : undefined;
};

const annotators = (flag("annotators") ?? "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean)
  .sort();
if (annotators.length < 2) {
  console.error("need at least 2 annotators: --annotators pool-a01,pool-a02[,…]");
  process.exit(1);
}
const n = annotators.length;

// Keyable rows per packet (design §3): canonical order, auto-resolved rows out.
const r2 = JSON.parse(readFileSync(path.join(root, "data/lexico/r2_checkpoint_review_packet.json"), "utf8"));
const h4 = JSON.parse(readFileSync(path.join(root, "data/lexico/h4_semantic_field_review_packet.json"), "utf8"));
const xref = JSON.parse(readFileSync(path.join(root, "data/lexico/xref_source_check_packet.json"), "utf8"));

const r2Rows = r2.checkpointRows.map((r) => r.checkpointId);
const h4Open = h4.sampleRows.filter((r) => r.reviewStatus === "needs-review");
const h4Rows = (h4Open.length ? h4Open : h4.sampleRows.filter((r) => r.reviewStatus === "reviewed-ok"))
  .map((r) => r.reviewId);
const xrefRows = xref.sharedCoreRows.map((r) => r.sampleId);

const packets = {};
for (const [sheetId, rows] of [
  ["csl-atlas-r2-checkpoint_10rows", r2Rows],
  ["csl-atlas-h4-semantic-field_89rows", h4Rows],
  ["csl-atlas-xref-shared-core_40edges", xrefRows],
]) {
  const deal = {};
  rows.forEach((rowId, i) => {
    const b = Math.floor(i / n);
    const p = i % n;
    const k = 1 + (b % Math.max(n - 1, 1));
    deal[rowId] = [annotators[p], annotators[(p + k) % n]];
  });
  packets[sheetId] = {
    sourcePacket:
      sheetId.includes("h4") ? "data/lexico/h4_semantic_field_review_packet.json"
        : sheetId.includes("xref") ? "data/lexico/xref_source_check_packet.json"
          : "data/lexico/r2_checkpoint_review_packet.json",
    rows: deal,
  };
}

const manifest = {
  schemaVersion: "1.0.0",
  poolVersion: "v1",
  generatedAt: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
  generatedBy: "npm run build-review-pool-assignment",
  rule: "rotating-offset-blocks; keys(i) = [A[i%n], A[(i%n + 1 + (i//n) % (n-1)) % n]]",
  annotators,
  packets,
};

const outPath = path.join(root, "data/review/pool_assignment.json");
mkdirSync(path.dirname(outPath), { recursive: true });
writeFileSync(outPath, JSON.stringify(manifest, null, 2) + "\n");

const coverage = Object.entries(packets)
  .map(([id, p]) => `${id}: ${Object.keys(p.rows).length} rows dealt`)
  .join("; ");
console.log(`wrote ${path.relative(root, outPath)} — ${coverage}; pool n=${n}`);
