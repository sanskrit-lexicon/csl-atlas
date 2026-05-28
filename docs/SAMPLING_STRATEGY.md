# Automatic Hard-Case Sampling Strategy

The pilot sample is not meant to be statistically representative. It is meant to stress TEI and OntoLex.

## Target Size

Initial target: 50 MW-led cases with matching PWG and/or PWK records where possible.

## Candidate Sources

Local CDSL source files:

- `../csl-orig/v02/mw/mw.txt`
- `../csl-orig/v02/pwg/pwg.txt`
- `../csl-orig/v02/pw/pw.txt`

MW supplies the first candidate list because its markup has the richest hard-case signals for this project.

## Hard-Case Signatures

| Signature | Detection | Why It Matters |
|---|---|---|
| `hedge` | MW record contains `<ls>L.</ls>` | Tests generic lexicographer-only evidence |
| `root` | MW record contains `<info verb="genuineroot"` | Tests root as lexical and grammatical object |
| `compound` | MW `<e>` starts with `3` or `<k2>` contains compound dash | Tests subentry versus decomposition graph |
| `continuation` | MW `<e>` starts with `1A` | Tests adjacency and suppressed-headword recovery |
| `pwg-rich` | PWG counterpart has more citations than MW | Tests citation compression/transformation |
| `pwk-abridged` | PWK counterpart has fewer citations than PWG | Tests abridgement as semantic loss |
| `tri-dict` | Same `k1` occurs in MW, PWG, and PWK | Supports comparative display |

## Scoring

Candidates are scored by accumulated stress:

- `hedge`: +6
- `root`: +5
- `compound`: +5
- `continuation`: +4
- all three dictionaries present: +3
- PWG has more citations than MW: +2
- PWK has fewer citations than PWG: +2
- MW has no citation but PWG has one: +2
- homophone marker: +1

The sampler then applies soft quotas so the top 50 are not all compounds.

## Output

Generated file:

```text
data/pilot/hard-cases.json
```

Each case records:

- rank and score;
- hard-case phenomena;
- key and source record ids;
- source line pointers;
- citation counts;
- raw snippets from MW/PWG/PWK;
- preliminary loss hints.

## Human Review

Automatic sampling finds useful trouble. It does not decide the scholarly interpretation.

Every case chosen for the paper should be reviewed manually before it is cited.
