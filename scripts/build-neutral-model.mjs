import fs from "fs/promises";
import path from "path";

function parseGenderOrGrammar(raw) {
  if (!raw) return null;
  // Match standard grammatical tags
  const m = raw.match(/<ab>(cl\.|m\.|f\.|n\.|ind\.|adj\.)<\/ab>/);
  if (m) {
    const code = m[1];
    if (code === "m.") return "masculine";
    if (code === "f.") return "feminine";
    if (code === "n.") return "neuter";
    if (code === "ind.") return "indeclinable";
    if (code === "adj.") return "adjective";
    return code;
  }
  return null;
}

function extractFormsAndRelations(item, id) {
  const forms = [];
  const relations = [];
  const citations = [];
  
  // Extract Lemma Form from MW / PWG / PWK
  const baseForm = {
    orth: item.key,
    type: "lemma",
    grammar: parseGenderOrGrammar(item.records.mw?.raw || item.records.pwg?.raw)
  };
  forms.push(baseForm);

  // Extract L. Hedge citations
  const mwRaw = item.records.mw?.raw || "";
  if (/<ls>L\.<\/ls>/.test(mwRaw)) {
    citations.push({
      source: "L.",
      type: "generic-lexicographer-hedge",
      context: "MW lexicographer-only attestation"
    });
  }

  // Handle Root Phenomena
  if (item.phenomena.includes("root")) {
    // Look up verb class info
    const infoVerb = mwRaw.match(/<info verb="genuineroot" cp="([^"]+)"\/>/) || mwRaw.match(/<ab>cl\.<\/ab>\s*(\d+)/);
    if (infoVerb) {
      baseForm.type = "verbal-root";
      baseForm.verbClass = infoVerb[1];
    }
    
    // Check Whitney root association
    const whitneyMatch = mwRaw.match(/<info whitneyroots="([^"]+)"\/>/);
    if (whitneyMatch) {
      relations.push({
        type: "whitney-root-association",
        target: whitneyMatch[1]
      });
    }
  }

  // Handle Compound Phenomena
  if (item.phenomena.includes("compound")) {
    baseForm.type = "compound";
    // Check if there is an explicit segmentation or separator in k2
    const k2 = item.records.mw?.k2 || "";
    if (k2.includes("—") || k2.includes("-")) {
      const parts = k2.split(/[—–-]/).map(p => p.trim()).filter(Boolean);
      if (parts.length > 1) {
        relations.push({
          type: "lexical-decomposition",
          components: parts
        });
      }
    }
  }

  // Handle Continuation Phenomena
  if (item.phenomena.includes("continuation")) {
    baseForm.type = "continuation";
    // Find parent from raw metadata (usually is a sibling continuation)
    const eAttr = item.records.mw?.e || "";
    relations.push({
      type: "adjacency-continuation-parent",
      eCode: eAttr
    });
  }

  return { forms, relations, citations };
}

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/hard-cases.json");
  const outputPaths = [
    path.resolve(process.cwd(), "data/pilot/neutral-model.json"),
    path.resolve(process.cwd(), "src/data/pilot/neutral-model.json")
  ];

  const data = JSON.parse(await fs.readFile(inputPath, "utf-8"));
  
  // Count occurrences of each key to handle duplicates
  const keyCounts = {};
  for (const item of data.items) {
    keyCounts[item.key] = (keyCounts[item.key] || 0) + 1;
  }

  const models = data.items.map(item => {
    const id = item.id || (
      keyCounts[item.key] > 1
        ? `mw-pwg-pwk:${item.key}-mw${item.records.mw.L}`
        : `mw-pwg-pwk:${item.key}`
    );

    const { forms, relations, citations } = extractFormsAndRelations(item, id);

    return {
      id,
      key: item.key,
      phenomena: item.phenomena || [],
      records: {
        mw: {
          L: item.records.mw?.L || null,
          line: item.records.mw?.line || null,
          pc: item.records.mw?.pc || null,
          raw: item.records.mw?.raw || null
        },
        pwg: {
          L: item.records.pwg?.L || null,
          line: item.records.pwg?.line || null,
          pc: item.records.pwg?.pc || null,
          raw: item.records.pwg?.raw || null
        },
        pwk: {
          L: item.records.pwk?.L || null,
          line: item.records.pwk?.line || null,
          pc: item.records.pwk?.pc || null,
          raw: item.records.pwk?.raw || null
        }
      },
      forms,
      senses: [],
      citations,
      relations,
      loss: []
    };
  });

  for (const outputPath of outputPaths) {
    await fs.mkdir(path.dirname(outputPath), { recursive: true });
    await fs.writeFile(outputPath, `${JSON.stringify(models, null, 2)}\n`, "utf-8");
  }
  console.log(`Generated neutral model for ${models.length} items at ${outputPaths.join(", ")}`);
}

main().catch(console.error);
