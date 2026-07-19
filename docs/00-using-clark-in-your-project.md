# Using CLARK in your own project — setup and session habits

*CLARK is a toolkit you point at **your** research project; this page is how to wire it in once, and the two habits that keep public tools and private research cleanly apart. Every step that needs no clicks from you is one sentence — ask Claude and it happens.*

> **Who does what.** You choose where things live and open the right folder; Claude does the copying, wiring, and checking. Nothing here requires a terminal.

## One-time: get CLARK onto your computer

Click **Code ▾ → Download ZIP** on the repo page and unzip (no git needed) — or ask Claude to clone it. **Keep the folder intact**: the skills reference the shared `docs/` and `starter-kit/` folders by relative path, so a skill folder separated from the repo breaks.

## Wiring it into a project (choose one, tell Claude)

1. **Sibling folder (recommended)** — keep `claude-language-assessment-research-kit/` next to your project folder and invoke skills by path: *"Read ../claude-language-assessment-research-kit/skills/zotero-citations/SKILL.md and set up automatic citations for me."* One CLARK copy serves every project, and updates land once.
2. **Inside the project** — copy the whole repo folder in (or under the project's `.claude/skills/`, keeping the repo folder whole). Self-contained, travels with the project.

**You should see:** after the first skill run, a small `starter-kit` copy inside *your* project (render scripts, style file, checkers) — your project never depends on files it doesn't contain, except the skills themselves.

## First moves, per skill

- *"Set up automatic citations for me"* → guided Zotero + render pipeline ([docs/01](01-zotero-setup.md)).
- *"Set up my literature review"* → the interview that creates your `review-conventions.md` ([docs/07](07-literature-review.md)).
- *"Set up a literature radar for this project"* → scheduled sweeps feeding your triage ([docs/07](07-literature-review.md)).
- *"Polish this paragraph"* → the five-dimension writing polish (accuracy corrected, style proposed — [the skill](../skills/writing-polish/SKILL.md)).
- *"Check my citations"* → the integrity pass, any time ([docs/04](04-citation-integrity.md)).
- *"Review my draft for submission to ⟨journal⟩"* → the pre-submission review ([docs/08](08-pre-submission-review.md)).
- *"Check my model pins"* → the model radar: verifies the AI models your audits pin are still live and current (propose-only log).

Everything the skills create — conventions, matrices, notes, digests, review files — lives in **your project**, not in CLARK.

## The two session habits (they matter more than they look)

1. **One Claude Code session per project, opened at that project's folder.** Claude loads the folder's own `CLAUDE.md`, conventions, and permissions — your assessment project's context, not another project's. Keep a separate session for the CLARK folder itself only if you're modifying CLARK.
2. **Public and private stay structurally apart.** CLARK is public-facing; your manuscripts, review matrices, and (above all) anything you review *for a journal* are not. Working in per-project sessions makes that boundary structural rather than something to remember: nothing from your research folders can drift into a repo you might push, and the skills' confidential outputs (notes, plans) stay beside the manuscripts they quote. A one-page `CLAUDE.md` in your project folder (ask Claude to draft one) tells every future session what the project is and where its rules live.

## Updating CLARK later

Ask Claude, in your CLARK-folder session: *"check for and fetch the latest CLARK."* Your projects don't change — conventions files and matrices are yours; only the toolkit refreshes.
