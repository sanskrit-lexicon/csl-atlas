import fs from "node:fs/promises";
import path from "node:path";

const INPUT = path.resolve(process.cwd(), "data", "pilot", "hard-cases.json");
const OUTPUTS = [
  path.resolve(process.cwd(), "data", "pilot", "review-cases.json"),
  path.resolve(process.cwd(), "src", "data", "pilot", "review-cases.json")
];

const QUOTAS = [
  {
    bucket: "root",
    count: 5,
    reason: "root/verbal lemma with MW L. hedge and PWG/PWK compression",
    predicate: item => item.phenomena?.includes("root")
  },
  {
    bucket: "compound",
    count: 5,
    reason: "compound entry requiring archival subentry preservation and semantic decomposition review",
    predicate: item => item.phenomena?.includes("compound")
  },
  {
    bucket: "continuation",
    count: 3,
    reason: "continuation entry requiring adjacency recovery before semantic modeling",
    predicate: item => item.phenomena?.includes("continuation")
  },
  {
    bucket: "hedge-only",
    count: 2,
    reason: "MW generic lexicographer hedge without root/compound/continuation confound",
    predicate: item => item.phenomena?.includes("hedge")
      && !item.phenomena?.some(p => ["root", "compound", "continuation"].includes(p))
  }
];

function safeId(id) {
  return id.replace(/:/g, "-");
}

async function main() {
  const data = JSON.parse(await fs.readFile(INPUT, "utf8"));
  const items = [...(data.items || [])].sort((a, b) => a.rank - b.rank);
  const selected = [];
  const seen = new Set();

  for (const quota of QUOTAS) {
    let used = 0;
    for (const item of items) {
      if (used >= quota.count) break;
      if (seen.has(item.id) || !quota.predicate(item)) continue;
      seen.add(item.id);
      used += 1;
      selected.push({item, quota});
    }
  }

  if (selected.length < 15) {
    for (const item of items) {
      if (selected.length >= 15) break;
      if (seen.has(item.id)) continue;
      seen.add(item.id);
      selected.push({
        item,
        quota: {
          bucket: "fallback",
          reason: "highest remaining hard case needed to fill the 15-case review slice"
        }
      });
    }
  }

  const output = {
    generatedAt: new Date().toISOString(),
    generator: "scripts/select-review-cases.mjs",
    profileVersion: "interoperability-profile-v0.1",
    description: "Deterministic 15-case validation slice for TEI archival and OntoLex/FrAC modeling.",
    selectionPolicy: {
      quotas: QUOTAS.map(({bucket, count, reason}) => ({bucket, count, reason})),
      ordering: "Use existing hard-case rank inside each quota; fill any shortage from remaining rank order."
    },
    items: selected.map(({item, quota}, index) => {
      const id = item.id;
      const stem = safeId(id);
      return {
        id,
        reviewRank: index + 1,
        originalRank: item.rank,
        key: item.key,
        score: item.score,
        bucket: quota.bucket,
        selectionReason: quota.reason,
        phenomena: item.phenomena || [],
        validationTargets: ["tei-archival-profile", "ontolex-frac-profile", "rdf-turtle"],
        reviewStatus: "profile-validated-by-script",
        artifacts: {
          tei: `data/pilot/tei/${stem}.xml`,
          ontolexJsonld: `data/pilot/ontolex/${stem}.json`,
          turtle: `data/pilot/rdf/${stem}.ttl`
        }
      };
    })
  };

  for (const outputPath of OUTPUTS) {
    await fs.mkdir(path.dirname(outputPath), {recursive: true});
    await fs.writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
  }

  const summary = output.items.reduce((counts, item) => {
    counts[item.bucket] = (counts[item.bucket] || 0) + 1;
    return counts;
  }, {});
  console.log(`Selected ${output.items.length} review cases: ${JSON.stringify(summary)}`);
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
