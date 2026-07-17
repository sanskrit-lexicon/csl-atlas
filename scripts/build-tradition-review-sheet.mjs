import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const result = spawnSync("python", [path.join(root, "scripts", "build-review-sheets.py"), "--only", "tradition"], {
  cwd: root,
  stdio: "inherit"
});
process.exit(result.status ?? 1);
