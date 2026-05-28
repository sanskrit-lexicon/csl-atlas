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
    
    // Output parsed forms
    for (const f of model.forms || []) {
      const typeAttr = f.type ? ` type="${escapeXml(f.type)}"` : "";
      xml += `  <form${typeAttr}>\n`;
      xml += `    <orth notation="SLP1">${escapeXml(f.orth)}</orth>\n`;
      if (f.grammar) {
        xml += `    <gramGrp><gram>${escapeXml(f.grammar)}</gram></gramGrp>\n`;
      }
      if (f.verbClass) {
        xml += `    <note type="verb-class">${escapeXml(f.verbClass)}</note>\n`;
      }
      xml += `  </form>\n`;
    }

    // Output mapped relations
    for (const rel of model.relations || []) {
      const typeAttr = rel.type ? ` type="${escapeXml(rel.type)}"` : "";
      if (rel.components) {
        xml += `  <etym${typeAttr}>\n`;
        for (const comp of rel.components) {
          xml += `    <seg type="component">${escapeXml(comp)}</seg>\n`;
        }
        xml += `  </etym>\n`;
      } else {
        const targetVal = rel.target || rel.eCode || "";
        xml += `  <xr${typeAttr} target="${escapeXml(targetVal)}"/>\n`;
      }
    }

    // Output source records
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

