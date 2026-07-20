# Changelog

All notable changes to CLARK, one entry per release (the git history carries the commit-level detail). Format follows the spirit of [Keep a Changelog](https://keepachangelog.com/); versioning is semver adapted to a skills-and-docs kit — **patch** = fixes and clarity · **minor** = new capability (a new skill, a released field guide, new script features) · **major** = anything users must react to (renames, conventions-format changes, charter changes). Each minor/major release is archived on Zenodo; cite the concept DOI [10.5281/zenodo.21411273](https://doi.org/10.5281/zenodo.21411273) for all versions. Field guides version independently (each carries its own version and DOI); their releases are noted here.

## [Unreleased]

### Added
- **CLARK Field Guides** — the expert-curated domain-pack series: spec with charter-grade provenance rules and the three contribution rungs (cited / feedback-invited / co-curated), the `_template/` starting kit, the registry, and the founding guide (Automated Writing Evaluation, curated by Sha Liu — in preparation).
- `CONTRIBUTING.md` — how to contribute, ground rules, and the versioning/release policy.
- `docs/09-writing-polish.md` — the writing-polish user guide (the one skill that lacked a guide page); docs/07 gains a "model radar" section; every skill row in the README now links its guide.
- `.github/CODEOWNERS` + branch protection on `main` — all changes now land via pull request with the maintainer's code-owner approval (the propose-never-apply charter applied to the repo itself).

### Changed
- **literature-radar** — Mode S reframed as **seed-based discovery** (build *or expand* a corpus from anchor papers, not only cold-start): Claude runs the citation-snowball directly on the open graphs (OpenAlex, Semantic Scholar), and always offers ResearchRabbit / Litmaps / Connected Papers as an optional *cross-check* — with the honest caveat that none of them, nor the snowball, is an exhaustive search (systematic database search still leads for recall). `docs/07` gains a user-facing "Finding the papers" section.

### Fixed
- DOI badge: Zenodo's auto-badge is refused by GitHub's image proxy (redirect served as `text/html`); replaced with a shields.io badge showing the permanent concept DOI.
- Version badge aligned with the release tag and CITATION.cff (1.0.0).

## [1.0.0] — 2026-07-17

Initial public release: seven integrity-first skills (`zotero-citations` · `citation-integrity` · `literature-review` · `literature-radar` · `pre-submission-review` · `writing-polish` · `model-radar`), the operator's manual (docs 00–08 + the flowchart twins), the stdlib-only starter-kit (render scripts, APA 7th CSL, eight Python tools), and `CITATION.cff`. Released under the name CLARK — Claude Language Assessment Research Kit (renamed pre-release from the working name CLAS). DOI: [10.5281/zenodo.21411275](https://doi.org/10.5281/zenodo.21411275).
