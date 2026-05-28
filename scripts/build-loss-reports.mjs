import fs from "fs/promises";
import path from "path";

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/neutral-model.json");
  const outputPath = path.resolve(process.cwd(), "data/pilot/loss-reports.json");

  const models = JSON.parse(await fs.readFile(inputPath, "utf-8"));
  const reports = [];

  for (const model of models) {
    for (const p of model.phenomena) {
      if (p === "hedge") {
        reports.push({
          caseId: model.id,
          target: "tei",
          status: "partial",
          phenomenon: "generic-lexicographer-hedge",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "MW L. evidence preservation",
          loss: "TEI can preserve string/type but not shared evidential semantics",
          extensionNeeded: true,
          reviewStatus: "machine"
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "partial",
          phenomenon: "generic-lexicographer-hedge",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "MW L. evidence preservation",
          loss: "Needs explicit evidence/provenance node",
          extensionNeeded: true,
          reviewStatus: "machine"
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
          loss: "Root as entry is preservable; derivational role is not fully explicit",
          extensionNeeded: false,
          reviewStatus: "machine"
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "lossy",
          phenomenon: "root-as-derivational-base",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Root modeling",
          loss: "Root needs lexical plus derivational relation",
          extensionNeeded: true,
          reviewStatus: "machine"
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
          extensionNeeded: false,
          reviewStatus: "machine"
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "partial",
          phenomenon: "compound-decomposition",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Compound modeling",
          loss: "Decomposition needs component graph",
          extensionNeeded: true,
          reviewStatus: "machine"
        });
      } else if (p === "continuation") {
        reports.push({
          caseId: model.id,
          target: "tei",
          status: "partial",
          phenomenon: "continuation-parent",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Continuation modeling",
          loss: "Parent must be recovered from adjacency",
          extensionNeeded: false,
          reviewStatus: "machine"
        });
        reports.push({
          caseId: model.id,
          target: "ontolex",
          status: "lossy",
          phenomenon: "continuation-parent",
          sourceDictionary: "mw",
          sourcePointer: { L: model.records.mw.L, line: model.records.mw.line },
          claim: "Continuation modeling",
          loss: "Suppressed headword needs explicit parent relation",
          extensionNeeded: true,
          reviewStatus: "machine"
        });
      }
    }
  }

  await fs.writeFile(outputPath, JSON.stringify(reports, null, 2), "utf-8");
  console.log(`Generated ${reports.length} loss reports at ${outputPath}`);
}

main().catch(console.error);
