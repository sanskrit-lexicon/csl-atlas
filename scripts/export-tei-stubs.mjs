import fs from "fs/promises";
import path from "path";

function escapeXml(unsafe) {
  if (!unsafe) return "";
  return unsafe.replace(/[<>&'"]/g, function (c) {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
    }
  });
}

async function main() {
  const inputPath = path.resolve(process.cwd(), "data/pilot/neutral-model.json");
  const outputDir = path.resolve(process.cwd(), "data/pilot/tei");

  await fs.mkdir(outputDir, { recursive: true });
  const models = JSON.parse(await fs.readFile(inputPath, "utf-8"));

  for (const model of models) {
    const safeId = model.id.replace(/:/g, "-");
    const safeKey = escapeXml(model.key);
    
    let xml = `<entry xml:id="${safeId}">\n`;
    xml += `  <form type="lemma"><orth notation="SLP1">${safeKey}</orth></form>\n`;
    
    for (const dict of ['mw', 'pwg', 'pwk']) {
      const raw = model.records[dict]?.raw;
      if (raw) {
        xml += `  <note type="source" target="${dict}">${escapeXml(raw)}</note>\n`;
      }
    }
    
    xml += `  <note type="model-loss">Machine-generated stub; not reviewed.</note>\n`;
    xml += `</entry>\n`;

    const filePath = path.join(outputDir, `${safeId}.xml`);
    await fs.writeFile(filePath, xml, "utf-8");
  }

  console.log(`Exported ${models.length} TEI XML stubs to ${outputDir}`);
}

main().catch(console.error);
