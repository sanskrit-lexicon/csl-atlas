import fs from "fs/promises";
import path from "path";

// Resolves to the root data/pilot/hard-cases.json
const dataPath = path.resolve(process.cwd(), "data", "pilot", "hard-cases.json");
const data = await fs.readFile(dataPath, "utf-8");

process.stdout.write(data);
