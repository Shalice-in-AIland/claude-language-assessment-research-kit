# Contributing to CLARK

Thank you for considering it. CLARK runs on the same rule it enforces — **flag, never guess; propose, never apply** — and contributions follow the same spirit: everything is proposed, discussed, and editorially reviewed before it lands.

## Ways to contribute

1. **Report something** — a broken step, a menu that moved, a venue whose guidance changed, a script bug. Open an issue; a "docs say X, the tool now does Y" report is genuinely valuable, since these tools update often.
2. **Add a venue** — the reviewer-guides file grows on demand. Propose a new journal section with the same discipline as the existing ones: short verbatim extracts from *official reviewer-facing sources*, linked, dated.
3. **Curate a Field Guide** — the flagship contribution: your domain's venues, criteria, and review vocabularies as a living, *citable* publication with your byline and its own DOI. Spec, provenance rules, and the three contribution rungs (from "cite my published work" to full co-curatorship): [field-guides/README.md](field-guides/README.md).
4. **Improve a skill or script** — welcome, but open an issue first to discuss: the skills carry deliberate design decisions (approval gates, propose-only outputs, the preserve-lists) that look like friction and are the point.

## Ground rules (all contributions)

- **All changes land by pull request.** The maintainer is the code owner ([.github/CODEOWNERS](.github/CODEOWNERS)); every PR needs their approving review before it merges into `main`.
- The **16-rule integrity charter** ([docs/04](docs/04-citation-integrity.md)) governs everything and is the single source of those rules — nothing forks or restates it.
- **Provenance:** criteria and venue content trace to published/publisher sources — never an invented rubric. Published instruments are summarized and cited, never reproduced. Nothing unpublished or privately shared without the owner's written consent.
- **Field-neutral examples** in all user-facing docs; no personal-project content, credentials, or local paths.
- Scripts stay **standard-library-only** (the no-installs promise).
- Acknowledgments never imply endorsement without the person's explicit agreement on the wording.

## Versioning & releases

Semver, adapted to a skills-and-docs kit:

| Level | What triggers it | Release? |
|---|---|---|
| **Patch** (1.0.x) | Fixes and clarity: typos, links, badges, doc rewording, script fixes with no behavior change | Accumulates; rides with the next release |
| **Minor** (1.x.0) | New capability, backwards-compatible: a new skill, a released field guide, new script features, substantive venue/criteria additions | Yes — GitHub release; Zenodo archives it and mints the version DOI |
| **Major** (x.0.0) | Anything users must react to: renamed files/skills, conventions-format changes that break existing `review-conventions.md` files, charter changes | Yes — with migration notes in the changelog |

**Release checklist:** move `[Unreleased]` into a dated version entry in [CHANGELOG.md](CHANGELOG.md) → bump `version:` and `date-released:` in [CITATION.cff](CITATION.cff) → bump the README version badge → tag `vX.Y.Z` and publish the GitHub release (Zenodo mints the DOI automatically). Field guides version independently, each with its own DOI; their releases get a changelog line here.

## Credit

Field-guide curators are credited where scholars look: the guide's **byline, citation, and DOI**, plus the [registry](field-guides/README.md#registry). Code and docs contributors appear in the repository's contributor graph; an acknowledgments roster will be added with the first external contribution. Maintainer and editorial gate: Sha Liu.
