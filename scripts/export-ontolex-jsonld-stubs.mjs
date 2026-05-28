import fs from "fs/promises";
import path from "path";

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/neutral-model.json");
  const outputDir = path.resolve(process.cwd(), "data/pilot/ontolex");

  await fs.mkdir(outputDir, { recursive: true });
  const models = JSON.parse(await fs.readFile(inputPath, "utf-8"));

  for (const model of models) {
    const safeId = model.id.replace(/:/g, "-");
    
    const jsonld = {
      "@context": {
        "ontolex": "http://www.w3.org/ns/lemon/ontolex#",
        "lexicog": "http://www.w3.org/ns/lemon/lexicog#",
        "decomp": "http://www.w3.org/ns/lemon/decomp#",
        "frac": "http://www.w3.org/ns/lemon/frac#",
        "csl": "https://sanskrit-lexicon.github.io/csl-atlas/ns#"
      },
      "@id": `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(model.key)}`,
      "@type": "lexicog:Entry",
      "ontolex:canonicalForm": {
        "@type": "ontolex:Form",
        "ontolex:writtenRep": model.key
      },
      "csl:phenomenon": model.phenomena || []
    };

    if (model.id !== `mw-pwg-pwk:${model.key}`) {
      jsonld["@id"] = `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(model.id)}`;
    }

    // Add forms and grammar properties
    if (model.forms && model.forms[0]) {
      const mainForm = model.forms[0];
      if (mainForm.grammar) {
        jsonld["ontolex:canonicalForm"]["ontolex:gender"] = mainForm.grammar;
      }
      if (mainForm.type) {
        jsonld["@type"] = `lexicog:${mainForm.type.charAt(0).toUpperCase() + mainForm.type.slice(1)}Entry`;
      }
    }

    // Map compound components (decomposition)
    const decompRel = model.relations?.find(r => r.type === "lexical-decomposition");
    if (decompRel && decompRel.components) {
      jsonld["decomp:constituent"] = decompRel.components.map((comp, idx) => ({
        "@id": `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(model.key)}#component${idx + 1}`,
        "@type": "decomp:Component",
        "ontolex:correspondsTo": {
          "@id": `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(comp)}`
        }
      }));
    }

    // Map evidential attributes (e.g. hedges) using frac:Attestation
    const hedgeCite = model.citations?.find(c => c.type === "generic-lexicographer-hedge");
    if (hedgeCite) {
      jsonld["frac:attestation"] = {
        "@type": "frac:Attestation",
        "frac:value": hedgeCite.source,
        "csl:evidenceType": hedgeCite.type
      };
    }

    const filePath = path.join(outputDir, `${safeId}.json`);
    await fs.writeFile(filePath, JSON.stringify(jsonld, null, 2), "utf-8");
  }

  console.log(`Exported ${models.length} OntoLex JSON-LD stubs to ${outputDir}`);
}

main().catch(console.error);

