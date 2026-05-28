import fs from "fs/promises";
import path from "path";

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/neutral-model.json");
  const outputDir = path.resolve(process.cwd(), "data/pilot/ontolex");

  await fs.mkdir(outputDir, { recursive: true });
  const models = JSON.parse(await fs.readFile(inputPath, "utf-8"));

  for (const model of models) {
    // Make a file-safe ID similar to TEI, e.g. replacing ':' with '-'
    const safeId = model.id.replace(/:/g, "-");
    
    // In the ID IRI, we use the original key, or safeId. The spec uses 'ac' so model.key
    // Wait, if there are duplicates, we need unique IDs. Let's use the stable id.
    const jsonld = {
      "@context": {
        "ontolex": "http://www.w3.org/ns/lemon/ontolex#",
        "lexicog": "http://www.w3.org/ns/lemon/lexicog#",
        "csl": "https://sanskrit-lexicon.github.io/csl-atlas/ns#"
      },
      "@id": `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(model.key)}`,
      "@type": "lexicog:Entry",
      "ontolex:canonicalForm": {
        "ontolex:writtenRep": model.key
      },
      "csl:phenomenon": model.phenomena || []
    };

    // If we want the @id to be truly unique for duplicates, we can append the L like in the safeId
    if (model.id !== `mw-pwg-pwk:${model.key}`) {
      jsonld["@id"] = `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(model.id)}`;
    }

    const filePath = path.join(outputDir, `${safeId}.json`);
    await fs.writeFile(filePath, JSON.stringify(jsonld, null, 2), "utf-8");
  }

  console.log(`Exported ${models.length} OntoLex JSON-LD stubs to ${outputDir}`);
}

main().catch(console.error);
