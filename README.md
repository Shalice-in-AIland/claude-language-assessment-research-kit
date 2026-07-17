# Claude Language Assessment Research Kit (CLARK)

**Research skills for the language-assessment and applied-linguistics community, operated by Claude Code.** Each skill packages a complete, integrity-first research workflow — Claude runs the machinery; the scholarly judgement stays yours.

| Skill | What it does | Status |
|---|---|---|
| [`zotero-citations`](skills/zotero-citations/SKILL.md) | Automatic citations & reference lists — Zotero → Better BibTeX → Pandoc → Word, with guided setup for first-time users | ✅ ready |
| [`citation-integrity`](skills/citation-integrity/SKILL.md) | Pre-submission reference audit — every DOI resolves **and matches** your entry; retraction check (Crossref/Retraction Watch); a 16-rule integrity charter aligned to COPE/ICMJE | ✅ ready |
| [`pre-submission-review`](skills/pre-submission-review/SKILL.md) | Evidence-anchored evaluation of YOUR OWN manuscript before submission — verification ledger, fatal/major/minor triage, a prioritized revision plan + a 0–100 quality estimate, and a compliance check against the target journal's current author instructions; original research and research syntheses | ✅ ready |
| [`writing-polish`](skills/writing-polish/SKILL.md) | Polish of YOUR OWN prose across five dimensions — accuracy, clarity/readability, formality, register & conventions, stance — built for multilingual and early-career academics; accuracy errors corrected directly (with a learnable change log), style as numbered proposals you accept one at a time; numbers/citations/claim strength never touched; the AI-declaration reminder is built in | ✅ ready |
| [`literature-review`](skills/literature-review/SKILL.md) | Living review matrix — approval-gated triage (relevance tiers, KEY flags, keep-but-flag quality checklist) + Obsidian views generated from the matrix (citekey-named notes, controlled theme hubs, method/tool hubs) | ✅ ready |
| [`literature-radar`](skills/literature-radar/SKILL.md) | Standing watch for new papers — scheduled sweeps, strict dedup against your corpus, pre-screened triage-ready digests with a "needs your attention" shortlist; discovery only, you approve inclusions | ✅ ready |

*Skills for sub-fields (e.g. automated speaking assessment) join as the toolkit grows. The rest of this page documents the citation skills — the toolkit's foundation.*

---

## The citation pipeline

**You write `[@cheng2026]` in a plain-text draft. You get a Word document with "(Cheng et al., 2026)" formatted perfectly, plus a matched, alphabetised reference list — and a typo'd citation can't hide.** No more hand-formatting citations, no more reference lists that drift out of sync with the text.

This repo packages a tested workflow built from free tools **plus an AI operator that runs it for you**, with a plain-language guide written for people who have **never used any of them**:

| Tool | Think of it as |
|---|---|
| [Zotero](https://www.zotero.org) | your **library catalogue** — drop a PDF in, it fetches the details |
| [Better BibTeX](https://retorque.re/zotero-better-bibtex/) (a Zotero plugin) | the **ID-card printer** — every paper gets a permanent citekey like `cheng2026` |
| [Pandoc](https://pandoc.org) | the **typesetter** — turns your draft + IDs into a finished Word document |
| [Obsidian](https://obsidian.md) *(optional)* | your **writing desk** — a comfortable home for the Markdown drafts you cite in; plugs into the pipeline with zero changes ([docs/06](docs/06-obsidian-editor.md)) |
| [Claude Code](https://claude.com/claude-code) | the **built-in operator** — walks you through setup, runs the renders, reads every warning, audits your library |

Claude Code runs the fiddly parts — terminals, installs, render commands, warning-reading — so you never have to figure out Pandoc or a command line. The few things it *can't* do for you (a handful of clicks inside the Zotero app) it walks you through one checkpoint at a time, with screenshots.

---

## Get started (~30 min, mostly automated)

1. Click the green **Code ▾** button above → **Download ZIP** → unzip. (No git needed.)
2. Install [Claude Code](https://claude.com/claude-code) (desktop app or CLI).
3. Open the unzipped folder in Claude Code and say: **"Read skills/zotero-citations/SKILL.md and set up automatic citations for me."**

Claude then does the computer work itself — checks/installs Pandoc, places the files, renders the demo so you *see it working first* — and guides you click-by-click through the Zotero steps, confirming each one worked before the next. From then on, daily use is three moves: **add a paper to Zotero → cite by `[@key]` → say "render my draft."**

**The operator's manual:** [docs/01](docs/01-zotero-setup.md) (setup, with screenshots), [docs/02](docs/02-daily-workflow.md) (daily use), [docs/03](docs/03-troubleshooting.md) (every gotcha we hit, with fixes), and [docs/04](docs/04-citation-integrity.md) — **the citation-integrity rules**: how this workflow guarantees no fabricated, no "Frankenstein", and no orphaned references. These are the steps and rules Claude itself follows — read them to see exactly what's happening under the hood, or to do any step yourself. The discipline is author-agnostic: however the prose was drafted, references must resolve, numbers must trace to their tables, and described methods must match the instruments actually included.

**Level 2 (recommended once the basics work):** give Claude a *live* connection to your Zotero library — it verifies records against Zotero itself, finds papers by *meaning* (semantic search), and spots duplicates/missing DOIs while you write. **Claude installs this for you**: say *"Read docs/05 and connect yourself to my Zotero library"* — your only manual part is one checkbox in Zotero. Details & what it adds: [docs/05](docs/05-zotero-mcp.md). Reversible; everything stays on your computer.

**Writing in Obsidian (or want to)?** Your drafts are plain Markdown, so Obsidian plugs in with zero pipeline changes — [docs/06](docs/06-obsidian-editor.md) is the two-click setup (open your project folder as a vault), the optional citekey-autocomplete plugins, and a render-tested table of what happens if Obsidian-only syntax (like `%%hidden comments%%` — which Word prints!) leaks into a manuscript.

**Running a literature review?** [docs/07](docs/07-literature-review.md) is the living-review system: a matrix you approve row by row, generated Obsidian views (per-paper notes, theme/method hubs, a dashboard), and an optional cross-vendor AI audit of your own judgements — flag-never-guess throughout.

**About to submit a paper?** [docs/08](docs/08-pre-submission-review.md) is the pre-submission review of **your own manuscript**: page-anchored findings and recomputed statistics, a triage list you adjudicate before anything is written up, a prioritized revision plan with a 0–100 estimate, and a compliance check against the journal's current author instructions.

**How it all fits together:** see [docs/flowchart.md](docs/flowchart.md) — the diagrams render right here on GitHub. A designed, **printable** version is [docs/flowchart.html](docs/flowchart.html) (GitHub shows HTML as code — after downloading the ZIP, just double-click that file to open it in your browser).

## Changing the citation style (APA 7th is just the default)

The output format is controlled by **one file**: `starter-kit/style.csl`. We ship the official **APA Style 7th edition**. To use a different style — another edition, Chicago, MLA, or a specific journal's house style:

1. Search the free [Zotero Style Repository](https://www.zotero.org/styles) for your style or journal name.
2. Download the `.csl` file and save it as `style.csl`, replacing the one in `starter-kit/`.
3. Re-render. Same draft, new format — the in-text citations *and* the reference list both follow the new style automatically.

Your draft never changes: `[@cheng2026]` stays `[@cheng2026]`; only the style file decides how it looks. *(Tip: if you work with two journals, keep two folders with different `style.csl` files.)*

## What Claude Code does here (the built-in operator)

[`skills/zotero-citations/SKILL.md`](skills/zotero-citations/SKILL.md) teaches Claude this workflow's five jobs: **guided onboarding** (the Get-started setup above), **per-project setup** (copies the starter-kit into any new project and verifies the sample render), **render-and-explain** (runs the render, translates every warning into plain language), **library health-check** (missing years/DOIs, duplicates, stale exports), and a **pre-submission integrity pass** (every citation traced to a real record, text ↔ reference list reconciled both ways) — always **flagging anything it can't verify rather than guessing**, under the full rule set in [docs/04-citation-integrity.md](docs/04-citation-integrity.md). The judgement calls — what to read, what to cite, what a source says — stay yours.

The integrity pass is also a **standalone skill** — [`skills/citation-integrity/`](skills/citation-integrity/SKILL.md) — callable on its own ("check my citations") even without the render pipeline. It runs three library checks in `starter-kit/`: `check_retractions.py` (Crossref / Retraction Watch), `resolve_check.py` (does every DOI *resolve* to a real record, and does that record *match* your entry — catching dead DOIs and mis-attached / "Frankenstein" references), and `vor_check.py` (which of your cited preprints now have a published version of record). All are standard-library Python, no install.

To use the skills in *another* project of yours: copy this **whole repo folder** into that project (keeping it together — the skills reference the shared `docs/` and `starter-kit/` folders by relative path, so separating a skill folder from the repo breaks it), then invoke by path: *"Read \<folder\>/skills/zotero-citations/SKILL.md and set up automatic citations for me."* If you place it under the project's `.claude/skills/`, same rule: the repo folder stays intact. (`.claude` is a *hidden* folder; create it if it doesn't exist — Mac Finder shows hidden files with **Cmd+Shift+.**; Windows Explorer: View → Show → Hidden items.) **Full setup patterns and the session habits that keep public tools and private research apart: [docs/00](docs/00-using-clark-in-your-project.md).**

## Requirements & versions

- **Zotero** (free; Mac/Windows/Linux — no account needed for this workflow) + **Better BibTeX** plugin (free)
- **Pandoc** (free; Mac/Windows/Linux)
- **Claude Code** — the operator (subscription or API). *(The underlying pipeline is all free software; the manual in docs/ covers every step if you ever work without Claude.)*
- Any plain-text editor for your draft (Markdown) — including [Obsidian](https://obsidian.md) as a comfortable writing home ([docs/06](docs/06-obsidian-editor.md))

Unsure whether your setup is complete? Ask Claude to **"run the CLARK doctor"** — one command (`starter-kit/clark_doctor.py`) checks everything in this list, your project's files, and whether your audit keys are in place, without changing anything.

**Last verified: July 2026** against Zotero 9, current Better BibTeX, Pandoc 3.10. These tools are open-source and update regularly — a menu may move, but the concepts don't change; each guide step links the official docs as the always-current source.

## License

MIT for everything in this repo, **except** `starter-kit/style.csl` (the APA style file), which comes from the [CSL project](https://citationstyles.org/) and keeps its own Creative Commons BY-SA license (noted inside the file). See [LICENSE](LICENSE).
