_Created: 17-07-2026 · Last updated: 05-09-2026_

# Dependency security posture

Last checked: 25-07-2026

`npm audit --omit=dev --audit-level=high` is a required release and CI gate
(`scripts/verify.mjs`). The lockfile is refreshed without `--force`; it
currently resolves every advisory that has a fix inside the declared semver
ranges.

**Why `--omit=dev` (25-07-2026):** the deployed artifact is static HTML on
GitHub Pages; the repo's only dependency tree is the build toolchain
(`@observablehq/framework`, devDependencies) — nothing from `node_modules`
ships. On 25-07-2026 a new `brace-expansion` advisory
(`GHSA-mh99-v99m-4gvg`, unbounded-expansion OOM DoS, all versions ≤ 5.0.7)
landed with a fix only in 5.0.8 and no backport to the 1.x/2.x majors that
`minimatch` (and through it `glob` → `@rollup/plugin-commonjs` →
`@observablehq/framework`) pins — making the unscoped gate unpassable without
either a forced framework downgrade (breaking) or waiting on upstream
backports, while blocking every site deploy. Scoping the gate to production
dependencies matches the standing posture below: dev-server-only advisories
do not affect the committed static Pages artifact. Production dependencies —
if any are ever added — remain fully gated at `high`.

Known accepted dev-only advisories (do not affect the Pages artifact):

- `esbuild` (`GHSA-g7r4-m6w7-qqqr`, low): arbitrary local file reads while a
  Windows development server is exposed to untrusted clients. Do not expose
  `npm run dev` on an untrusted network.
- `brace-expansion` (`GHSA-mh99-v99m-4gvg`, high): OOM DoS on crafted glob
  patterns fed to the build toolchain; the build only globs repo-controlled
  paths. Re-evaluate when `minimatch`-compatible backports (2.x) publish, then
  refresh the lockfile.

Re-evaluate both when Observable publishes a release carrying fixed
transitives.

_Dr. Mārcis Gasūns_
