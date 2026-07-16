# Optional upgrade: connect Claude directly to your Zotero library (MCP)

*The base pipeline needs nothing in this file. This upgrade gives Claude a live connection to your Zotero library — so it can verify records, find papers, and search by meaning while you write. Fully reversible, everything stays on your computer.*

> **You do one thing; Claude does the rest.** Setup is a single checkbox you tick inside Zotero — then Claude installs and connects everything else for you (see **Setup** below). The exact commands Claude runs are tucked into the **appendix at the end**, for the curious or for manual debugging — you don't need them for normal use.

## What is "MCP"? (plain-language, no jargon required)

**MCP** stands for *Model Context Protocol* — think of it as a **standard plug socket for giving Claude new abilities**. Out of the box, Claude can't open Zotero any more than your word processor can. What we install here is a small **translator program** (an "MCP server") that sits between them, on your computer.

When you ask *"which papers in my library discuss X?"*, this happens:

**You ask Claude → Claude asks the translator → the translator asks Zotero** (through a local-only door Zotero opens on your machine — the checkbox in Step 1) **→ Zotero answers from its database → the answer flows back into your conversation.**

Three things worth knowing:
- **Everything stays on your computer.** The Claude↔Zotero connection is machine-internal; your library isn't uploaded anywhere, and the connection itself costs nothing.
- **"Semantic search"** is the one extra we build in Step 3: every paper's title and abstract gets converted into a mathematical "meaning fingerprint" (stored locally). Your question gets the same treatment, and papers with *nearby* fingerprints match — which is why a search for "scoring harshness" finds papers that only ever say "rater severity", and why typos don't matter.
- **MCP is a general mechanism** — the same socket can connect Claude to calendars, databases, and other tools. This guide uses it for exactly one thing: your reference library.

## What it adds (beyond the base pipeline)

| Without MCP | With MCP |
|---|---|
| Claude reads only the exported `library.bib` (can be stale) | Claude checks **Zotero itself, live** — a year/DOI/author verification can never be out of date |
| You hunt for the right citekey in Zotero | Ask *"which papers in my library deal with rater severity?"* → paper list + citekeys, ready to paste |
| Keyword search only | **Semantic search**: finds papers by *meaning* ("scoring harshness" finds "severity" papers), not just matching words |
| Library problems found at the final check | On-demand hygiene: duplicates, missing years/DOIs, dead attachment links |

**What it deliberately does *not* change:** the citing rules. Claude's library access is for **bookkeeping and verification** — a paper still gets *cited* only after you've actually read it ([rule 5](04-citation-integrity.md)). And Claude still never supplies a reference from memory.

## Setup: one step for you, the rest is automatic

**What only you can do (one step).** In **Zotero → Settings → Advanced**, tick **"Allow other applications on this computer to communicate with Zotero."** This is a consent checkbox *inside* Zotero, so Claude can't tick it for you. (It opens a local-only door on your machine — nothing goes to the cloud, nothing is billed.)

**What Claude does (everything else).** In a Claude Code session, just say:

> *"Read docs/05 and connect yourself to my Zotero library."*

Claude installs the connector, builds the semantic-search index, registers itself, and confirms the connection — **you run no commands**. Then keep **Zotero open**, start a **new local session** (cloud sessions can't reach your computer — see [troubleshooting](03-troubleshooting.md)), and try: *"Search my Zotero library for papers about X and give me their citekeys."*

That's the whole setup. If you'd rather do it by hand, or something needs debugging, the exact commands Claude runs are in the **appendix at the end of this page**.

## Sample questions — a guided tour of what to ask

*Tip: narrow beats broad. "Which papers deal with AI writing evaluation?" may match half your library (Claude will group the landscape and ask which slice you want); the patterns below get you precise answers in one step. Square brackets = fill in your own.*

**Finding papers** *(semantic search finds papers by meaning — it works even when a paper uses different words than you, and survives typos):*
- "Which papers in my library discuss **[your concept — e.g. teacher feedback]**? Citekeys please." *(citekeys = the `[@key]` handles you write with)*
- "Which studies used **[your method — e.g. interviews / regression / a randomised trial]**? Citekeys."
- "Which papers studied **[your population — e.g. undergraduates / nurses / L2 writers]** specifically?"
- "Which papers **compare [two things you care about — e.g. two teaching approaches, two AI models]**?"
- "I need studies where **[the thing you manipulate — e.g. feedback timing]** was the variable being tested — what do I have?"

**Supporting an argument (the high-value one):**
- "Any **verbatim quotes** from papers in my library that support **[scoring via API rather than a chat interface]**? Include page locations."
- "What did **[paper]** actually find about **[consistency]**? Quote the results sentence."
- "Which paper is my **strongest evidence** for [claim] — and are there any that *contradict* it?"

**Verification & hygiene (run these before submission days):**
- "Verify the **year, authors, and DOI** of everything I cite in [draft] against Zotero directly."
- "Find library entries with **missing years or DOIs**." · "Any **duplicate** entries?" · "Any entries whose **linked PDF is missing**?"
- "Cross-check: do the citekeys in my draft match the **pinned** Citation Keys in Zotero?"

**Working with your own reading (notes & annotations):**
- "What did I **highlight** in [paper]? I need the page number for a quote."
- "Pull my notes on [paper] and summarise what *I* flagged as important."

**Deciding what to read next** *(help choosing what to **read** — never a substitute for reading before you **cite**; see [rule 5](04-citation-integrity.md)):*
- "Look at the papers in my **[folder name]** folder in Zotero *(Zotero calls folders "collections")* and summarise: what topics do they cover, and what's missing?"
- "Which papers in my library that I **haven't tagged as read** are most relevant to **[topic]**? Give me a ranked reading list."

*Key-name note: if Claude shows internal Zotero item keys (random letters like `ABC123XY`) instead of citekeys, or keys that don't match the ones in your drafts, say so — the **pinned Citation Key** on the Zotero item is the truth.*

## Reading full papers: which Claude for which job

Claude Code reads the **text** of your PDFs (through the Zotero connection or extraction tools) — ideal for finding and quoting passages, checking what a paper actually says, and structured extraction. Two honest limits, and what to do about them:

- **Scanned PDFs with no text layer** (common for older theses/book chapters) have nothing to extract. Spot them early: ask *"report the extractable text length of the PDFs in [folder]"* — anything near zero needs OCR before Claude can read it.
- **Figure- and table-heavy content**: Code works from text, so a result that lives *in a figure* is invisible to it — unless you ask for eyes. **Checking a specific table or figure is a one-sentence ask** — *"check Table 2 in ⟨paper⟩"* — and Claude finds the PDF through Zotero, locates the right page, renders it as an image, and *looks* at it (needs the small free PyMuPDF library once; Claude installs it on first use). For whole-paper visual reading, uploading the PDF to a **claude.ai chat** (or Cowork mode) remains the fuller route — bring the takeaways back to your Code session.

Rule of thumb: **Code for text, quotes, and pipeline work; claude.ai/Cowork when the figures are the point.** Either way, an AI reading a paper never substitutes for *your* reading when it comes to citing it (rule 5).

## Caveats, honestly

- **Zotero must be running** for the connection to work; it's your-computer-only (cloud/web sessions can never see it).
- The server is a community project (not official Zotero) — solid in our use, but expect occasional rough edges.
- Semantic search reads your library locally to build its index; the index lives on your machine.

## Appendix — the commands Claude runs

*You don't need this section for normal use: Claude performs these when you ask it to connect. It's here for transparency and as a manual fallback if you'd rather set it up yourself.*

1. **Enable the local connection** — the one step you do yourself: Zotero → Settings → Advanced → tick "Allow other applications on this computer to communicate with Zotero."
2. **Install the connector** (in a terminal):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh        # uv: a no-admin tool manager (once per computer)
   ~/.local/bin/uv tool install "zotero-mcp-server[semantic]"
   ```
   *(The `[semantic]` part adds search-by-meaning; omit it for a lighter install.)*
3. **Build the semantic-search index** (with Zotero open):
   ```bash
   ZOTERO_LOCAL=true ~/.local/bin/zotero-mcp update-db
   ```
   Re-run occasionally (or after adding many papers) to refresh it.
4. **Register with Claude Code** — a stdio MCP server named `zotero`: command `~/.local/bin/zotero-mcp`, args `serve`, env `ZOTERO_LOCAL=true`. It lives in your user-level Claude config, so it works in every project.
5. **Use it:** start a new local session with Zotero open.
