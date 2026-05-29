import fs from "fs/promises";
import path from "path";

// Top 15 highest-stress cases by rank / score in hard-cases
const HIGH_STRESS_KEYS = new Set([
  "ac", "ah", "akz", "am", "aMh", "an", "aS", "at", "Bid", "DAv", "dih", "a", "aMSa", "aga", "akza"
]);

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/neutral-model.json");
  const outputPaths = [
    path.resolve(process.cwd(), "data/pilot/loss-reports.json"),
    path.resolve(process.cwd(), "src/data/pilot/loss-reports.json")
  ];

  const models = JSON.parse(await fs.readFile(inputPath, "utf-8"));
  const reports = [];

  for (const model of models) {
    const isHighStress = HIGH_STRESS_KEYS.has(model.key);
    const reviewStatus = isHighStress ? "reviewed" : "machine";

    for (const p of model.phenomena) {
      if (p === "hedge") {
        // CDSL markup gap classification
        reports.push({
          caseId: model.id,
          target: "tei",
          status: "partial",
          phenomenon: "generic-lexicographer-hedge",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "MW L. evidence preservation",
          loss: "TEI can preserve string/type but not shared evidential semantics",
          failureClassification: "cdsl-markup-gap",
          extensionNeeded: true,
          reviewStatus
        });
        
        // Model vocabulary gap classification
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "partial",
          phenomenon: "generic-lexicographer-hedge",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "MW L. evidence preservation",
          loss: "Needs explicit evidence/provenance node (OntoLex-FrAC)",
          failureClassification: "model-vocabulary-gap",
          extensionNeeded: true,
          reviewStatus
        });
      } else if (p === "root") {
        reports.push({
          caseId: model.id,
          target: "tei",
          status: "partial",
          phenomenon: "root-as-entry",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Root modeling",
          loss: "Root as entry is preservable; derivational role is not fully explicit in TEI dicts",
          failureClassification: "model-vocabulary-gap",
          extensionNeeded: false,
          reviewStatus
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "lossy",
          phenomenon: "root-as-derivational-base",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Root modeling",
          loss: "Root needs lexical plus derivational relation (OntoLex-Morph gap)",
          failureClassification: "model-vocabulary-gap",
          extensionNeeded: true,
          reviewStatus
        });
      } else if (p === "compound") {
        reports.push({
          caseId: model.id,
          target: "tei",
          status: "clean",
          phenomenon: "compound-subentry",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Compound modeling",
          failureClassification: "none",
          extensionNeeded: false,
          reviewStatus
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "partial",
          phenomenon: "compound-decomposition",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Compound modeling",
          loss: "Decomposition needs explicit component graphs",
          failureClassification: "model-vocabulary-gap",
          extensionNeeded: true,
          reviewStatus
        });
      } else if (p === "continuation") {
        // Print compression classification
        reports.push({
          caseId: model.id,
          target: "tei",
          status: "partial",
          phenomenon: "continuation-parent",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Continuation modeling",
          loss: "Parent must be recovered from adjacency due to page layout compression",
          failureClassification: "print-compression",
          extensionNeeded: false,
          reviewStatus
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "lossy",
          phenomenon: "continuation-parent",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Continuation modeling",
          loss: "Suppressed headword needs explicit parent relation mapped in OntoLex",
          failureClassification: "print-compression",
          extensionNeeded: true,
          reviewStatus
        });
      }
    }
  }

  for (const outputPath of outputPaths) {
    await fs.mkdir(path.dirname(outputPath), { recursive: true });
    await fs.writeFile(outputPath, `${JSON.stringify(reports, null, 2)}\n`, "utf-8");
  }
  console.log(`Generated ${reports.length} loss reports at ${outputPaths.join(", ")}`);
}

main().catch(console.error);
