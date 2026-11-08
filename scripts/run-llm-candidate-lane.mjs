// H7101 — credentialed runner for the frozen LLM candidate lane.
//
// The runner is intentionally narrow: it reads the committed prompt pack and
// the committed 500-row sample, calls one OpenAI-compatible chat endpoint, and
// writes machine-candidate records only. It never touches a review report and
// it refuses to start without credentials rather than fabricating output.
//
// Usage:
//   H7101_LLM_API_KEY=... H7101_LLM_MODEL=deepseek-chat \
//     node scripts/run-llm-candidate-lane.mjs --out data/llm-candidate-lane/outputs/llm-run.jsonl
//
// Optional: H7101_LLM_BASE_URL (default https://api.deepseek.com/v1),
//           --limit N for a smoke run.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { EDIT_TYPES, LANE_DIR, SAMPLE_PATH, PROMPTS_PATH, renderPrompt } from "./build-llm-candidate-lane.mjs";

const OUT_DEFAULT = path.join(LANE_DIR, "outputs", "llm-run.jsonl");

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function readJsonl(filePath) {
  return fs.readFileSync(filePath, "utf8").split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}

function parsePrediction(content) {
  const cleaned = String(content ?? "").trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "");
  let parsed;
  try {
    parsed = JSON.parse(cleaned);
  } catch {
    const start = cleaned.indexOf("{");
    const end = cleaned.lastIndexOf("}");
    if (start < 0 || end <= start) throw new Error("model did not return JSON");
    parsed = JSON.parse(cleaned.slice(start, end + 1));
  }
  const editType = parsed.editType === null ? null : parsed.editType;
  if (editType !== null && !EDIT_TYPES.includes(editType)) {
    throw new Error(`unknown editType ${JSON.stringify(editType)}`);
  }
  const abstain = parsed.abstain === true || editType === null;
  const confidence = Number(parsed.confidence);
  const span = parsed.span && typeof parsed.span === "object"
    ? {
      text: String(parsed.span.text ?? ""),
      start: Number.isFinite(Number(parsed.span.start)) ? Math.max(0, Math.trunc(Number(parsed.span.start))) : 0,
      end: Number.isFinite(Number(parsed.span.end)) ? Math.max(0, Math.trunc(Number(parsed.span.end))) : 0
    }
    : abstain ? null : { text: "", start: 0, end: 0 };
  return {
    editType: abstain ? null : editType,
    span: abstain ? null : span,
    confidence: Number.isFinite(confidence) ? Math.min(1, Math.max(0, confidence)) : 0,
    abstain,
    rationale: String(parsed.rationale ?? "").slice(0, 500)
  };
}

async function callModel({ baseUrl, apiKey, model, prompt }) {
  const body = {
    model,
    temperature: 0,
    messages: [
      { role: "system", content: "You are a careful Sanskrit dictionary editorial candidate generator. Return JSON only." },
      { role: "user", content: prompt }
    ],
    response_format: { type: "json_object" }
  };
  let lastError;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const response = await fetch(`${baseUrl.replace(/\/$/, "")}/chat/completions`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${apiKey}`
        },
        body: JSON.stringify(body)
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: ${text.slice(0, 300)}`);
      }
      const payload = await response.json();
      return {
        content: payload.choices?.[0]?.message?.content ?? "",
        revision: payload.model ?? model
      };
    } catch (error) {
      lastError = error;
      if (attempt < 2) await new Promise(resolve => setTimeout(resolve, 1000 * 2 ** attempt));
    }
  }
  throw lastError;
}

async function main() {
  const apiKey = process.env.H7101_LLM_API_KEY;
  const modelName = process.env.H7101_LLM_MODEL;
  const baseUrl = process.env.H7101_LLM_BASE_URL || "https://api.deepseek.com/v1";
  if (!apiKey || !modelName) {
    console.error("Refusing to run: set H7101_LLM_API_KEY and H7101_LLM_MODEL. No output written.");
    process.exit(2);
  }

  const args = process.argv.slice(2);
  const outIndex = args.indexOf("--out");
  const outPath = outIndex >= 0 ? args[outIndex + 1] : OUT_DEFAULT;
  const limitIndex = args.indexOf("--limit");
  const limit = limitIndex >= 0 ? Number(args[limitIndex + 1]) : null;
  const concurrencyIndex = args.indexOf("--concurrency");
  const concurrency = concurrencyIndex >= 0 ? Math.max(1, Number(args[concurrencyIndex + 1])) : 4;

  const prompts = JSON.parse(fs.readFileSync(PROMPTS_PATH, "utf8"));
  const variant = prompts.variants.find(item => item.id === prompts.selectedVariant);
  const promptMeta = {
    id: variant.id,
    version: prompts.schemaVersion,
    sha256: variant.sha256
  };
  const sample = readJsonl(SAMPLE_PATH);
  const rows = limit ? sample.slice(0, limit) : sample;
  const outputs = new Array(rows.length);
  let cursor = 0;
  let modelRevision = modelName;
  let failures = 0;

  async function worker() {
    while (cursor < rows.length) {
      const index = cursor;
      cursor += 1;
      const row = rows[index];
      try {
        const result = await callModel({
          baseUrl,
          apiKey,
          model: modelName,
          prompt: renderPrompt(variant, row)
        });
        modelRevision = result.revision;
        const prediction = parsePrediction(result.content);
        outputs[index] = {
          schemaVersion: "1.0.0",
          id: row.id,
          split: row.split,
          sourceRef: row.sourceRef,
          inputSha256: sha256(row.input.text),
          prompt: promptMeta,
          model: {
            provider: new URL(baseUrl).hostname,
            name: modelName,
            revision: result.revision,
            temperature: 0
          },
          prediction,
          provenance: {
            editType: prediction.editType,
            source: row.source,
            model: modelName,
            confidence: prediction.confidence,
            abstain: prediction.abstain,
            revisionStatus: "machine-candidate",
            reviewedValue: null,
            reviewer: null,
            reviewedAt: null
          }
        };
      } catch (error) {
        failures += 1;
        outputs[index] = {
          schemaVersion: "1.0.0",
          id: row.id,
          split: row.split,
          sourceRef: row.sourceRef,
          inputSha256: sha256(row.input.text),
          prompt: promptMeta,
          model: { provider: new URL(baseUrl).hostname, name: modelName, revision: modelName, temperature: 0 },
          prediction: {
            editType: null,
            span: null,
            confidence: 0,
            abstain: true,
            rationale: `runner failure: ${String(error.message).slice(0, 300)}`
          },
          provenance: {
            editType: null,
            source: row.source,
            model: modelName,
            confidence: 0,
            abstain: true,
            revisionStatus: "machine-candidate",
            reviewedValue: null,
            reviewer: null,
            reviewedAt: null
          }
        };
        console.error(`row ${row.id}: ${error.message}`);
      }
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()));
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, outputs.map(record => JSON.stringify(record)).join("\n") + "\n");
  console.log(JSON.stringify({
    out: outPath,
    rows: outputs.length,
    failures,
    model: modelName,
    revision: modelRevision,
    prompt: promptMeta.id
  }, null, 2));
  if (failures) process.exitCode = 1;
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
