# Dependency security posture

Last checked: 17-07-2026

`npm audit --audit-level=high` is a required release and CI gate. The lockfile
is refreshed without `--force`; it currently resolves all high and moderate
advisories that were present before the v0.2.0 stabilization pass.

Two low-severity development-server advisories remain through `esbuild`
(`GHSA-g7r4-m6w7-qqqr`). Observable Framework 1.13.4 currently constrains the
affected range, and the available automated remediation would force a downgrade
to Framework 1.13.3. The issue concerns arbitrary local file reads while a
Windows development server is exposed to untrusted clients; it does not affect
the committed static Pages artifact. Do not expose `npm run dev` on an
untrusted network. Re-evaluate when Observable publishes a compatible release
that carries a fixed esbuild version.
