// Canonical review-sheet emitter lives in csl-pyutil; keep this Node entry
// point so existing npm commands remain cross-platform.
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const result = spawnSync("python", [path.join(root, "scripts", "build-review-sheets.py"), ...process.argv.slice(2)], {
  cwd: root,
  stdio: "inherit"
});
process.exit(result.status ?? 1);
