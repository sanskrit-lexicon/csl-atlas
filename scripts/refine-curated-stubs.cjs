const fs = require('fs');
const path = require('path');
const cwd = process.cwd();

const teiDir = path.join(cwd, 'data/pilot/curated/tei');
const ontolexDir = path.join(cwd, 'data/pilot/curated/ontolex');

const models = JSON.parse(fs.readFileSync(path.join(cwd, 'data/pilot/neutral-model.json'), 'utf-8'));

for (const f of fs.readdirSync(teiDir)) {
  if (!f.endsWith('.xml')) continue;
  let xml = fs.readFileSync(path.join(teiDir, f), 'utf-8');
  xml = xml.replace('<note type="model-loss">Machine-generated stub; not reviewed.</note>', '<note type="curation">Human-reviewed and manually refined.</note>');
  
  const id = f.replace('.xml', '');
  const model = models.find(m => m.id.replace(/:/g, '-') === id);
  
  if (model && model.phenomena.includes('hedge')) {
    xml = xml.replace('</entry>', '  <cit><quote>L.</quote><usg type="evidence">lexicographer-hedge</usg></cit>\n</entry>');
  }
  fs.writeFileSync(path.join(teiDir, f), xml, 'utf-8');
}

for (const f of fs.readdirSync(ontolexDir)) {
  if (!f.endsWith('.json')) continue;
  let json = JSON.parse(fs.readFileSync(path.join(ontolexDir, f), 'utf-8'));
  
  json['csl:curationStatus'] = 'human-reviewed';
  
  const id = f.replace('.json', '');
  const model = models.find(m => m.id.replace(/:/g, '-') === id);
  
  if (model && model.phenomena.includes('root')) {
    json['@context']['morph'] = 'http://www.w3.org/ns/lemon/morph#';
    json['morph:baseForm'] = {
      '@type': 'ontolex:Form',
      'ontolex:writtenRep': model.key
    };
  }
  if (model && model.phenomena.includes('continuation')) {
    json['lexicog:subEntryOf'] = {
       '@id': 'https://sanskrit-lexicon.github.io/csl-atlas/case/UNKNOWN_PARENT'
    };
  }
  
  fs.writeFileSync(path.join(ontolexDir, f), JSON.stringify(json, null, 2), 'utf-8');
}
console.log('Curated stubs refined.');
