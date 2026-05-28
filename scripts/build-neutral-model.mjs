import fs from "fs/promises";
import path from "path";

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/hard-cases.json");
  const outputPath = path.resolve(process.cwd(), "data/pilot/neutral-model.json");

  const data = JSON.parse(await fs.readFile(inputPath, "utf-8"));
  
  // Count occurrences of each key to handle duplicates
  const keyCounts = {};
  for (const item of data.items) {
    keyCounts[item.key] = (keyCounts[item.key] || 0) + 1;
  }

  const models = data.items.map(item => {
    let id = `mw-pwg-pwk:${item.key}`;
    if (keyCounts[item.key] > 1) {
      id = `mw-pwg-pwk:${item.key}-mw${item.records.mw.L}`;
    }

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
      forms: [],
      senses: [],
      citations: [],
      relations: [],
      loss: []
    };
  });

  await fs.writeFile(outputPath, JSON.stringify(models, null, 2), "utf-8");
  console.log(`Generated neutral model for ${models.length} items at ${outputPath}`);
}

main().catch(console.error);
