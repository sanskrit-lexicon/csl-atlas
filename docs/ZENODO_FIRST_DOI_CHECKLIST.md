_Created: 24-09-2026 · Last updated: 24-09-2026_

# Zenodo first DOI checklist — csl-atlas v1.0.0

Cold-readable: every step is copy-pasteable and assumes zero context.
The goal is the atlas's first archival DOI. Total time: ~15 minutes.
Nothing below publishes data by itself until you press "Publish release" in
step 8.

You need: a browser logged into GitHub as an account holder of
`sanskrit-lexicon/csl-atlas`, and the same Google/GitHub account you will
connect to [Zenodo](https://zenodo.org). Steps 1–4 run in a terminal; 5–10 in
the browser.

---

## 0. Pre-flight facts (read once)

- The draft release notes with all record counts live in
  [`docs/releases/v1.0.0.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/releases/v1.0.0.md).
- The reserved tag name is `v1.0.0` (reserved since the
  [v0.2.0 release notes](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/releases/v0.2.0.md)).
- The metadata already validates: `CITATION.cff` against the
  [Citation File Format 1.2.0 schema](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema.json),
  `.zenodo.json` against the official
  [Zenodo legacy deposit schema](https://github.com/zenodo/zenodo/blob/master/zenodo/modules/deposit/jsonschemas/deposits/records/legacyrecord.json).
- ORCIDs: Gasūns `0000-0003-4513-884X` is in both files. Funderburk and
  Andhrabharati still have none — the release can be cut without them; they
  can be added in a later metadata commit.

## 1. Sync the three version fields to 1.0.0 (~2 min)

The metadata currently says `0.19.2` (the last tagged state). The release you
are about to cut is `v1.0.0`, so all three files must say `1.0.0` **before**
you tag.

In the repo root (`csl-atlas`):

```bash
sed -i '' 's/"version": "0.19.2"/"version": "1.0.0"/' .zenodo.json
sed -i '' 's/^version: 0.19.2/version: 1.0.0/' CITATION.cff
sed -i '' 's/"version": "0.18.0"/"version": "1.0.0"/' package.json
grep -n '1.0.0' .zenodo.json CITATION.cff package.json
```

If the `grep` shows three lines containing `1.0.0`, continue. (If it shows
`0.19.2` / `0.18.0` anywhere in those three lines, a later commit moved the
version — open each file and set `"version"` / `version:` to `1.0.0` by hand.)

If you skip this step: the Zenodo record will permanently carry the wrong
version string, and the mismatch between tag and metadata will surface in
every future citation export. Fixing it later means a Zenodo support ticket.

## 2. Validate the metadata (~1 min)

```bash
python3 - <<'EOF'
import json, jsonschema, yaml, datetime, urllib.request
def cast(o):
    if isinstance(o, datetime.date): return o.isoformat()
    if isinstance(o, dict): return {k: cast(v) for k, v in o.items()}
    if isinstance(o, list): return [cast(v) for v in o]
    return o

# (a) CITATION.cff vs official CFF 1.2.0 schema
cff = cast(yaml.safe_load(open('CITATION.cff')))
sch = json.load(urllib.request.urlopen(
    'https://raw.githubusercontent.com/citation-file-format/citation-file-format/1.2.0/schema.json'))
jsonschema.Draft7Validator.check_schema(sch)
errs = list(jsonschema.Draft7Validator(sch).iter_errors(cff))
print('CITATION.cff:', 'VALID' if not errs else 'FAIL: ' + errs[0].message)

# (b) .zenodo.json vs official Zenodo legacy deposit schema. The upstream
# schema file is missing the documented `version` deposit field, so that one
# key is allowed explicitly (everything else stays strict).
zen = json.load(open('.zenodo.json'))
zsch = json.load(urllib.request.urlopen(
    'https://raw.githubusercontent.com/zenodo/zenodo/master/zenodo/modules/deposit/jsonschemas/deposits/records/legacyrecord.json'))
zsch['properties']['version'] = {'type': 'string'}
errs = list(jsonschema.Draft7Validator(zsch).iter_errors(zen))
print('.zenodo.json:', 'VALID' if not errs else 'FAIL: ' + errs[0].message)
EOF
```

Expected: `CITATION.cff: VALID` and `.zenodo.json: VALID`. If anything else
prints, stop and fix the named file before tagging.

## 3. Stamp the build commit into the release notes (~1 min)

```bash
git rev-parse --short HEAD
```

Open [`docs/releases/v1.0.0.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/releases/v1.0.0.md)
and replace both placeholders with that SHA: the `bbca791` line under
"Build commit" and the `<fill final SHA here>` line inside the draft tag
annotation.

## 4. Commit the sync, create and push the tag (~2 min)

```bash
git add .zenodo.json CITATION.cff package.json docs/releases/v1.0.0.md
git commit -m "Release v1.0.0: sync version fields, stamp build commit"
git push origin main
git tag -a v1.0.0 -m "csl-atlas v1.0.0 - first archival data release (see docs/releases/v1.0.0.md)"
git push origin v1.0.0
```

Wait for CI to go green on `main` before continuing
(`gh run watch` in the repo, or the Actions tab). If CI is red, stop — do not
release a red build.

## 5. Connect the repository to Zenodo (~3 min, account holder only)

This is the one step only you can do — it needs your Zenodo login.

1. Open <https://zenodo.org> and log in **using GitHub** (same account as the
   GitHub org membership).
2. Click your name (top right) → **GitHub** (or open
   <https://zenodo.org/account/settings/github/> directly).
3. Click **Get started**, then **Grant** access to Zenodo on the GitHub
   authorisation page.
4. On the Zenodo GitHub page find `sanskrit-lexicon/csl-atlas` and flip its
   switch to **ON**.

If you skip this step: nothing mints a DOI — the tag exists but Zenodo never
sees the release, and no archival copy of the data is created.

## 6. Create the GitHub release from the tag (~2 min)

1. Open <https://github.com/sanskrit-lexicon/csl-atlas/releases/new?tag=v1.0.0>.
2. Title: `csl-atlas v1.0.0 — first archival data release`.
3. Body: paste the full content of
   [`docs/releases/v1.0.0.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/releases/v1.0.0.md)
   (sections "What ships" through "Metadata state"; drop this checklist's
   internal pointers if you like).
4. Leave "Set as the latest release" ticked. Do NOT tick "Set as a pre-release".

## 7. Watch the Zenodo mint (~2 min)

1. Zenodo finishes within a few minutes; a badge appears on the repo's right
   sidebar once the DOI exists.
2. Or check <https://zenodo.org/account/settings/github/> — the release row
   turns green with a DOI link.

## 8. Publish the Zenodo record (~1 min)

Zenodo creates the record as soon as the release lands; new Zenodo accounts
publish records immediately. If your record sits in a draft state, open the
DOI link from step 7 and press **Publish** on the record.

## 9. Record the DOI back home (~1 min)

Copy the DOI (form `10.5281/zenodo.XXXXXXX`), then either run the DOI
back-fill unit or by hand:

- add `doi: https://doi.org/<DOI>` to [`CITATION.cff`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CITATION.cff);
- add `"doi": "<DOI>"` to [`.zenodo.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.zenodo.json);
- add a `doi` badge line to [`README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/README.md);
- commit and push on `main`.

## 10. Known caveats to keep visible

- `publication_date` is stamped by the Zenodo integration from the release
  date — never hardcode it in `.zenodo.json`, a stale value would override the
  real one.
- Zenodo deposits are **immutable**: after publishing, metadata fixes go
  through the record's edit form, data fixes need a new version. That is why
  steps 1–3 exist.
- The Zenodo record's version string comes from `.zenodo.json` `version` —
  which is exactly what step 1 syncs.

_Dr. Mārcis Gasūns_
