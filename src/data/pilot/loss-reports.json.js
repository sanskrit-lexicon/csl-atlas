import fs from "fs/promises";
import path from "path";

const dataPath = path.resolve(process.cwd(), "data", "pilot", "loss-reports.json");
const data = await fs.readFile(dataPath, "utf-8");

process.stdout.write(data);
