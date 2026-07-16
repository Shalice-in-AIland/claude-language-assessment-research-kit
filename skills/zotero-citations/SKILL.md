---
name: zotero-citations
description: Set up, run, and audit an automatic citation pipeline (Zotero + Better BibTeX + Pandoc) — with guided onboarding for first-time users. Use when the user wants automatic citations/references set up ("set up my citations", "set up automatic citations for me"), a Markdown manuscript rendered to Word with citations, citation problems checked or fixed ((key?) orphans, "n.d." years, stale .bib), the citation style changed (APA/journal CSL), or a pre-submission reference-integrity pass.
---

# Zotero + Claude Code automated citations — set up, render, and audit the reference pipeline

You operate a plain-text citation pipeline: **Zotero** (reference manager) → **Better BibTeX** ("Keep updated" export to `library.bib`, stable citekeys) → Markdown drafts citing `[@key]` → **Pandoc** `--citeproc` + a CSL style file (`style.csl`) → `.docx` with formatted in-text citations and a matched reference list. In this design **you are built in as the operator**: you run the terminal work, read every warning, and audit the library — the user only does the judgement calls and the few Zotero clicks you cannot do for them.

**Prime directive — flag, never guess.** You may cite/verify only what the bibliography verifiably holds. Never invent, "remember," or auto-correct a reference; when anything is uncertain, stop and show the user. The pipeline automates *formatting*; judgement (what to read, cite, and claim) stays human. **The full rule set you enforce is `../../docs/04-citation-integrity.md` (16 rules)** — including: no Frankenstein entries (fields from one single record only), cite the version/edition actually used, unread = not citable (ask the user, don't assume), secondary sources declared as "as cited in", weak evidence flagged and never load-bearing, no citation padding/manipulation, primary sources over stand-ins, and venue AI-disclosure reminders.

## Mode 0 — guided onboarding (trigger: "set up automatic citations for me")
For a user who has never used Zotero, Pandoc, or a terminal. Drive the whole of `../../docs/01-zotero-setup.md` interactively, **doing every step you can yourself** and checkpointing the rest:
1. **You do:** check/install Pandoc (Mode 1 step 2), copy `../../starter-kit/` into their project, verify the sample render works — before asking them to touch anything.
2. **They do (you checkpoint):** the Zotero clicks — install Zotero, install the Better BibTeX `.xpi` (warn Firefox users: right-click → save), set up the ☑ Keep updated export *saved directly to the `library.bib` you will read*, pin citekeys. One step at a time; confirm each "You should see" before the next; show the matching screenshot from `../../docs/images/`.
3. **Finish:** render `sample-draft.md`, then (if they have a draft) convert one real paragraph to `[@key]` citations together and render it. End by telling them the three things they'll do daily (add paper → cite by key → ask you to render).
4. **Offer — and perform — the live-library upgrade (../../docs/05-zotero-mcp.md).** Once the base pipeline works, offer to connect yourself to their Zotero library. On a yes, **you do the machine steps**: install `uv` (official installer, `~/.local/bin`), `uv tool install "zotero-mcp-server[semantic]"`, build the index (`ZOTERO_LOCAL=true zotero-mcp update-db`, Zotero open), and register the server in the user-level MCP config (`command: ~/.local/bin/zotero-mcp`, `args: ["serve"]`, `env: ZOTERO_LOCAL=true`) — back up the config file first. **They do** the one Zotero click (Settings → Advanced → "Allow other applications…") and must know: new **local** session to load the tools (cloud sessions can never reach their Zotero), Zotero running when used, and `update-db` re-run after adding many papers.

## Mode 1 — setup (once per project)
1. Create (or locate) the project's tooling folder containing `render.sh`/`render.bat`, `style.csl`, `library.bib` (this repo's `../../starter-kit/` is the template — copy it in).
2. Check Pandoc: `pandoc --version` (else guide install: Mac `.pkg` installer from the Pandoc releases page — or `brew install pandoc` if the user has Homebrew, or unpack the release zip to `~/.local/bin` when there are no admin rights; Windows `.msi`).
3. Walk the user through Zotero + Better BibTeX using `../../docs/01-zotero-setup.md` — you cannot click Zotero's UI for them; give one step at a time and confirm the "you should see" checkpoint before the next. Critical points: the `.xpi` is a manual download (Firefox: right-click → save); the "Keep updated" export must be saved **directly to the `library.bib` the render script reads** (the #1 failure is two diverging files); **pin citekeys before any metadata clean-up**.
4. Verify end-to-end by rendering `sample-draft.md` and confirming citations + reference list appear.

## Mode 2 — render
1. Run `bash render.sh "<draft>.md"` (Windows: `render.bat`).
2. Parse stderr for citeproc WARNINGs; report orphans in plain language: which key, where it appears in the draft, and the likely cause (typo vs missing from library vs stale export — check `library.bib` mtime vs the user's last Zotero edit).
3. Never silently edit the draft's citekeys to "fix" an orphan — show the mismatch and ask (the correct fix may be in Zotero, not the draft).
4. **Obsidian-authored drafts (`../../docs/06-obsidian-editor.md`):** before rendering, sweep the draft for leaked vault-only syntax — `%%…%%` comments **print in the .docx** (Obsidian hides them — the dangerous one), `[[wikilinks]]`/`![[embeds]]`/callout `[!…]` markers/`==highlights==`/`#tags` print literally, frontmatter `title:` becomes a visible Word title line while other properties vanish. Report anything found and propose the edits — never strip silently.

## Mode 3 — health-check (run on request, or before big writing pushes)
Report, don't auto-fix:
- **Sync gap:** does the Zotero export target = the file the renderer reads? Is `library.bib` older than expected?
- **Entry quality:** entries missing year (`grep`-able; they render "n.d.") or DOI; duplicate keys; duplicate works under different keys.
- **Orphan sweep:** every `[@key]` in the draft(s) vs the .bib, both directions (cited-but-absent; present-but-never-cited is informational only).
- **Style:** confirm `style.csl` is the intended style (read its `<title>`); note that with no CSL Pandoc defaults to Chicago author-date, not APA.

## Mode 4 — integrity-pass (pre-submission)
Delegate to the **`citation-integrity`** skill (`../citation-integrity/SKILL.md`) — the authoritative pass, so the rules live in one place. It enforces all of `../../docs/04-citation-integrity.md` and runs the three tools in `../../starter-kit/`: **`resolve_check.py`** (every DOI *resolves* to a real Crossref record **and** that record's title/year/first-author *match* the entry — catching dead DOIs and a DOI attached to a *different* work, i.e. mis-attach/"Frankenstein"; for DOI-less entries it *proposes* type-matched candidate DOIs, never assigns them), **`check_retractions.py`** (Crossref / Retraction Watch), and **`vor_check.py`** (preprints whose published version of record now exists — proposed, author-surname-guarded, updated in Zotero by the user). Layered gates, most objective first: resolve+consistency → retraction → orphans both ways → field/version completeness → citing-honesty (read-status, secondary sources, weak evidence — ask, don't assume) → quote locators → an optional, opt-in claim-faithfulness spot-check. **Propose fixes, never silently apply** — the fix is usually in Zotero, not the draft. Output ✓ verified / ⚠ flagged (with the Zotero fix, keyed to the ../../docs/04 rule #) / ○ your-call, then the venue-required **AI-disclosure** reminder (rule 15).

## If the Zotero MCP connection is available (../../docs/05-zotero-mcp.md)
When `zotero` MCP tools are present in the session, **prefer live-library checks over the exported .bib** for all verification (years/DOIs/authors — the export can be stale; Zotero is the truth), use **semantic search** to find papers by concept when the user asks "which papers deal with X", and read the user's Zotero notes/annotations when hunting a quote's page number. Boundaries: library access is for *bookkeeping and verification* — a paper is cited only if the user's reading log says it's read (rule 5; ask, don't assume), and the .bib consumed by `render.sh` remains the render-time source (if live Zotero and the .bib disagree, that's a **sync-gap finding to report**, not to silently fix).

**Citekey discipline over MCP (learned the hard way):**
- **Never present Zotero item keys** (`ABC123XY`-style) to the user as an end product — they're internal IDs. Always resolve to the BibTeX **citekey** before presenting.
- **The key truth is the pinned Citation Key** (the item's Extra field `Citation Key: <key>` line) and, ultimately, **the key as it appears in the project's render-time `library.bib`**. An ad-hoc BibTeX export fetched through MCP can generate *different* keys (authorYYYY defaults) than the pinned ones — cross-check against the .bib and say so if they differ. Pinned keys can also be irregular (e.g. a bare `authorname` with no year, pinned before a year was fixed) — **look them up, never guess patterns**.
- Broad concept queries can match half a library: when hits exceed ~15, group the landscape and ask which slice to resolve into citekeys, rather than firing dozens of metadata fetches.

## Lessons burned in (treat as rules)
- Citekeys are **handles**; rendered citations come from entry *fields*. Don't chase pretty keys; never "fix" a key that renders correctly.
- **Pin before metadata edits** — keys are derived from metadata and orphan the draft when they churn.
- One "Keep updated" export, on-idle, saved to the consumed path. A doubled .bib = a stale export, not key collisions.
- Style swap = replace `style.csl` (any style from zotero.org/styles); the draft never changes.
- These tools update regularly: if a documented menu doesn't match, defer to the official docs (zotero.org/support · retorque.re/zotero-better-bibtex) and tell the user which step drifted.
