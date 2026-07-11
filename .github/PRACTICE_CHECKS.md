# Practice Checks For csl-atlas

Use these checks for manuscript, article, changelog, publication-index, and generated documentation PRs.

## PR slicing
Why this is needed here:
- Atlas PRs often mix manuscript text, bibliography/publication metadata, indexes, changelogs, and generated site output.
- Reviewers need to see the editorial decision before generated or index churn dominates the diff.

Before merge, classify the PR:
- article or manuscript text,
- metadata/index registration,
- generated site output,
- navigation or changelog.

Split when the article decision and generated/index updates are large enough to need different review questions.

## Narrow review prompt
Suggested prompt:

```md
Please review only whether the manuscript or article is registered in every required index and changelog. Ignore generated formatting unless a link or title is wrong.
```

## Stacked PR hygiene
Use when article drafts, registration PRs, and generated site updates depend on each other.

Before merging:
- Parent article PR is merged or stable.
- Registration PR is retargeted to the intended base.
- Generated files are regenerated after retarget.
- Branch deletion will not close child PRs.

## PR checklist
- [ ] Editorial change and registration/index changes are clearly separated.
- [ ] Generated output has a command or provenance note.
- [ ] Reviewer is asked one concrete registration or navigation question.
- [ ] Dependent PRs include merge and retarget plan.
