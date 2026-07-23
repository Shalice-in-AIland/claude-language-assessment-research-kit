# Changelog

All notable changes to CLARK, one entry per release (the git history carries the commit-level detail). Format follows the spirit of [Keep a Changelog](https://keepachangelog.com/); versioning is semver adapted to a skills-and-docs kit — **patch** = fixes and clarity · **minor** = new capability (a new skill, a released field guide, new script features) · **major** = anything users must react to (renames, conventions-format changes, charter changes). Each minor/major release is archived on Zenodo; cite the concept DOI [10.5281/zenodo.21411273](https://doi.org/10.5281/zenodo.21411273) for all versions. Field guides version independently (each carries its own version and DOI); their releases are noted here.

## [Unreleased]

### Changed
- README — a **"What's new"** section now carries release headlines (newest first; the Field Guides invitation lives there too), and the skills table gains a **Standalone** column marking which skills ship a portable any-AI edition (currently: citation-integrity).

## [1.1.0] — 2026-07-23

**Citation integrity goes standalone.** The kit's most-requested check becomes extractable — one self-contained file for any AI chat, one printable checklist for supervision — and the in-repo skill it mirrors gains a sharper claim-faithfulness layer and an action-first report. DOI: [10.5281/zenodo.21504577](https://doi.org/10.5281/zenodo.21504577).

### Added
- **`standalone/citation-integrity/`** — the citation check, extractable: a self-contained **portable edition** for any AI assistant (paste + "check my citations"; search-based verification, action-first report, the same precision guards and find-never-supply rule as the full skill) and a **one-page practice checklist for supervisors and research students** (human-facing, rule-numbers keyed to docs/04, printable .docx included).
- **CLARK Field Guides** — the expert-curated domain-pack series: spec with charter-grade provenance rules and the three contribution rungs (cited / feedback-invited / co-curated), the `_template/` starting kit, the registry, and the founding guide (Automated Writing Evaluation, curated by Sha Liu — in preparation).
- `CONTRIBUTING.md` — how to contribute, ground rules, and the versioning/release policy.
- `docs/09-writing-polish.md` — the writing-polish user guide (the one skill that lacked a guide page); docs/07 gains a "model radar" section; every skill row in the README now links its guide.
- `.github/CODEOWNERS` + branch protection on `main` — all changes now land via pull request with the maintainer's code-owner approval (the propose-never-apply charter applied to the repo itself).

### Changed
- **citation-integrity + pre-submission-review** — the claim-faithfulness layer sharpened from live review experience: the two subtle failure modes are now named (mis-attached claims, including neighbouring-idea retrofitting; second-hand-citation mismatch), with hard precision guards (verbatim source quote beside any flag; default verdict "not-clearly-supported"; explicit "couldn't fully judge — your call" where field depth is needed). When a claim is left unsupported, the skills may *offer* the literature-radar's seed-based discovery to surface real candidate papers — **candidates to read, never citations to insert**. The spot-check also extends to **abstracts** where full text is unreachable (OpenAlex, no key — reaching paywalled sources, with the honest scope caveat "not covered in the abstract ≠ unsupported") and names a third failure mode, **attribution mismatch** (a number or method credited to a source that reports it differently).
- **citation-integrity report redesigned action-first**: a verdict banner (✅ CLEAR / ⚠ FLAGS TO RESOLVE with 🚫 blockers named first — no averaging; one retracted citation is never offset by verified ones), a progress strip and re-run trajectory, and the fix list as urgency-grouped checkboxes each leading with the action, its Zotero fix, a time estimate, and the rule number; a styled HTML one-pager is offered (not defaulted) at milestone runs; the verified bucket expands on request into a per-item fields-matched table with **passed-with-note** for benign discrepancies such as online-first vs print years.
- **literature-radar** — Mode S reframed as **seed-based discovery** (build *or expand* a corpus from anchor papers, not only cold-start): Claude runs the citation-snowball directly on the open graphs (OpenAlex, Semantic Scholar), and always offers ResearchRabbit / Litmaps / Connected Papers as an optional *cross-check* — with the honest caveat that none of them, nor the snowball, is an exhaustive search (systematic database search still leads for recall). `docs/07` gains a user-facing "Finding the papers" section.
- **Crediting policy applied to public surfaces** — provenance notes (CLAUDE.md positioning, two skill provenance paragraphs) now describe adopted patterns without naming third-party repositories; every source remains fully credited in the maintainer's external-sources register. Consumed infrastructure stays named: Zotero, Better BibTeX, Pandoc, Obsidian, `zotero-mcp`, and the open scholarly APIs (Crossref, OpenAlex, Semantic Scholar).
- README — a short "note on the name" footnote explaining the pre-release CLAS → CLARK rename, so the name in early commits / the v1.0.0 entry / the internal `clas-literature-review` marker doesn't puzzle newcomers.

### Fixed
- DOI badge: Zenodo's auto-badge is refused by GitHub's image proxy (redirect served as `text/html`); replaced with a shields.io badge showing the permanent concept DOI.
- Version badge aligned with the release tag and CITATION.cff (1.0.0).

## [1.0.0] — 2026-07-17

Initial public release: seven integrity-first skills (`zotero-citations` · `citation-integrity` · `literature-review` · `literature-radar` · `pre-submission-review` · `writing-polish` · `model-radar`), the operator's manual (docs 00–08 + the flowchart twins), the stdlib-only starter-kit (render scripts, APA 7th CSL, eight Python tools), and `CITATION.cff`. Released under the name CLARK — Claude Language Assessment Research Kit (renamed pre-release from the working name CLAS). DOI: [10.5281/zenodo.21411275](https://doi.org/10.5281/zenodo.21411275).
