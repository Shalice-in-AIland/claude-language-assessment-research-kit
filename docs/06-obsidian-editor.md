# Optional: Obsidian as your writing home (same pipeline, nicer desk)

*The base pipeline needs nothing in this file. Your drafts are plain-text Markdown, so any editor works — this page is for [Obsidian](https://obsidian.md), a free notes app many researchers write in, as the place you draft and keep notes. Nothing about the pipeline changes: same files, same `[@key]` citations, same "render my draft".*

> **Who does what.** Your part is the clicks inside the Obsidian app — install it, open your folder, optionally add a plugin (Claude can't click Obsidian's UI for you). Claude's part is everything it always does (renders, warnings, audits) **plus one Obsidian-specific service: the syntax sweep** — we render-tested exactly what happens when Obsidian-only syntax leaks into a manuscript (the table below), and you can ask Claude to check any draft for it.

## Think of it as…

Obsidian is a **reading room built over your existing filing cabinet**. It works directly on a folder of plain-text files — it calls that folder a **vault** — and adds comfortable writing, links between notes, and fast search *on top*. Your files never move and never convert; they stay ordinary `.md` files that the render script reads exactly as before. That's why this page is short: the pipeline was editor-agnostic by design, so Obsidian plugs in with **zero changes to the machinery**.

What you gain for this workflow:
- **Manuscript and notes in one place** — your draft, your reading notes, your to-dos: one folder, linkable, searchable.
- **Plain text forever** — nothing gets locked into an app; every file still works with Zotero, Pandoc, Claude, and git.
- **A live preview while you write** — headings, emphasis, and structure render as you type, instead of raw Markdown symbols.

## Step 1 — Install Obsidian
1. Download from **[obsidian.md/download](https://obsidian.md/download)** (free; Mac/Windows/Linux — no account needed).
2. Open it. **You should see:** a welcome screen asking you to create or open a vault.

## Step 2 — Open your project folder as a vault
1. On that screen, find **"Open folder as vault"** → click **Open** → choose your project folder (the one holding your drafts and the `starter-kit/` folder).
2. **You should see:** your draft files listed in Obsidian's left-hand pane. Click one — it opens for editing. That's the whole setup.

*Two harmless things you may notice:* Obsidian quietly adds a hidden `.obsidian/` folder (its own settings — ignore it), and it shows only Markdown/media files by default, so `library.bib`, `style.csl`, and the render scripts stay invisible in Obsidian while remaining exactly where the pipeline needs them. *(Already keep a vault? The other direction works too: copy `starter-kit/` and your drafts into the vault — the render script always finds its own files.)*

## Step 3 — Write and cite exactly as before
Type citations the same way — they're plain text, and we verified a vault changes nothing:

> Genre analysis models a text type as an ordered set of communicative moves `[@swales1990]`.

**Optional comfort: citekey autocomplete.** Community plugins can suggest citekeys from your library as you type and jump from a citekey to the paper. Two established ones (both community-maintained; their linked pages are the always-current setup source):
- **[Zotero Integration](https://github.com/obsidian-community/obsidian-zotero-integration)** — insert citations and import annotations from Zotero.
- **[ZotLit](https://github.com/aidenlx/zotlit)** — tight Zotero↔Obsidian linking with citekey completion.

**Optional, for Claude itself: [obsidian-skills](https://github.com/kepano/obsidian-skills)** — agent skills maintained by Obsidian's creator (MIT) that teach Claude Obsidian's native formats (Obsidian-flavored Markdown, Bases database views, JSON Canvas). Worth adding if you want Claude to build richer vault views than this kit's plain-Markdown generator produces — the pipeline's rules still don't move.

To add one: Obsidian **Settings → Community plugins → "Turn on community plugins"** → **Browse** → search the name → Install + Enable. **You should see:** the plugin listed under *Installed plugins* with its toggle on. *(Obsidian ships with community plugins off — "Restricted Mode" — as a safety default; turning them on is [their documented flow](https://help.obsidian.md/community-plugins).)*

Whatever the plugin does, **the pipeline's rules don't move**: `library.bib` stays the render-time source of truth, and citekeys come from Zotero's pinned Citation Keys ([setup guide](01-zotero-setup.md)).

## Step 4 — Render, as always
**Say to Claude: _"render my draft."_** Same command, same result — a `.docx` appears next to your draft with formatted citations and a matched reference list. *(Verified end-to-end on a vault-structured folder, July 2026, Pandoc 3.10.)*

## The leak table — Obsidian-only syntax in a manuscript (render-tested)

Obsidian adds its own Markdown extras. **They belong in your notes, which never get rendered — not in the manuscript.** If they leak into a draft, this is exactly what lands in the Word file:

| You typed (Obsidian syntax) | Obsidian shows you | The rendered Word file shows |
|---|---|---|
| `%%a private comment%%` | *nothing — hidden* | **your comment, printed in full** ⚠ |
| `[[Note name]]` or `[[Note\|shown text]]` | a clickable link | the literal `[[brackets and all]]` |
| `![[embedded note or image]]` | the embedded content | the literal `![[…]]` text |
| `> [!note] callout` | a styled callout box | a plain quote with `[!note]` printed |
| `==highlighted==` | a highlight | literal `==` signs |
| `#tag` | a clickable tag | the literal `#tag` text |
| Property `title:` (frontmatter) | the Properties panel | **a title line at the top** of the document (also set in the file's properties) |
| Other properties (`tags:`, `aliases:`, `status:`…) | the Properties panel | nothing — they vanish silently |

The one to respect is the first row: **Obsidian hides `%%comments%%`; Word prints them.** Never park anything in a draft comment you wouldn't submit. The rest are cosmetic and easy to spot — and none of them break citations (a `[@key]` on the same line still renders correctly; verified).

**The safety net:** before rendering something that lived in a vault, ask Claude — *"check my draft for Obsidian-only syntax, then render."* It sweeps for every pattern in this table, shows you anything found (it proposes; you decide), and renders.

## What this page deliberately doesn't cover

Using the vault as a structured **literature-notes knowledge base** — one note per paper, relevance tiers, theme hubs, a browsable graph — is the job of the [`literature-review` skill](../skills/literature-review/SKILL.md): your review matrix stays the source of truth, and the vault notes are *generated* from it (ask Claude to *"set up my literature review"*). This page is just the editor.

---
*Verified July 2026: renders tested on a real vault-structured folder with Pandoc 3.10; Obsidian UI steps quoted from the [official help](https://help.obsidian.md) (menus may drift — that link is the always-current source).*
