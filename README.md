# mod-ci

Shared GitHub Actions workflows for the Minecraft mod repos.

Public on purpose: reusable workflows in a private repo can only be called from
that same repo, and some callers live under other accounts.

## Workflows

| Workflow | Does |
| --- | --- |
| `sync-nohtml.yml` | Regenerates `README_nohtml.md` from `README.md` for CurseForge |
| `publish.yml` | Gradle build and publish over a matrix of subprojects |

## Using one

Pin a tag. Never point a caller at `main`, or an edit here changes every repo at once.

    jobs:
      nohtml:
        uses: duzos/mod-ci/.github/workflows/sync-nohtml.yml@v1
        permissions:
          contents: write
        with:
          modules: '["."]'

## Versioning

`v1` is a moving tag on the latest backwards-compatible commit. Breaking changes get `v2`.
