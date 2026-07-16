---
name: literature-radar
description: Scheduled or on-demand sweep for NEW papers in a project's research scope — web-search the recent window, deduplicate against the project's corpus, pre-screen each keeper into a triage-ready digest, and stop for approval. Use when the user asks "what's new" in their field ("run my radar", "check for new papers", "anything new since last time"), wants a recurring literature watch set up, or a scheduled radar day arrives. Discovery + pre-screen ONLY — inclusion decisions belong to the human and flow through the literature-review skill.
---

# literature-radar — a standing watch on the field

You run a **literature radar**: a periodic sweep that surfaces *new* work in the project's scope and delivers it **pre-screened** — deduplicated, quality-flagged, drafted into triage-ready blocks — so the scholar opens a near-finished digest, not a raw search dump. **Prime directive: discovery and pre-screening only.** You never write to the review matrix or the synthesis; every keeper waits for approval, then enters through the **`literature-review`** skill's triage flow (Mode 1), whose rules govern tiers, KEY, and the quality checklist.

## Step 0 — load the project's rules
Read `review-conventions.md` (the same file the literature-review skill uses): the **Scope** section defines what's in/out; the **`## Radar`** section (template: `../../starter-kit/review-conventions-template.md`) defines cadence, search window, venue list, preprint servers, the digest file's path, and any standing attention-criteria. Also load the current **dedup state**: the matrix's Authors + Cite-key columns, the project's PDF folder filenames, prior digest sections, and — when Zotero MCP tools are present — the live library. If no Radar section exists, offer to set one up (a two-minute interview).

## The sweep
1. **Search the window** (default ~since the last digest, or ~3 weeks): the conventions' topic phrasings × venue list × preprint servers, via web search. **Precision over recall** — "no clearly new in-scope papers this run" is a perfectly good result, and web search is not exhaustive (say so: the radar complements, never replaces, periodic database sweeps like Scopus/WoS).
2. **Dedup ruthlessly** against matrix + folder + prior digests + live Zotero. Watch preprint↔published pairs (match authors + title, not strings). A prior digest's "requested follow-up" items count as in-window even if older.
3. **Per keeper — pre-screen, behind the reading-quality gate:** fetch **open-access PDFs only** (never paywalled; a free-but-bot-blocked PDF = one click for the user — say which). Read what you fetched and declare the **Read basis** (full / partial / abstract-only). Then draft the full triage block per the literature-review skill's Mode 1: every matrix column, tier + KEY + cite-with-care via the project's checklist, and a one-line **corpus-benchmark** (corroborates / extends / contradicts / supersedes which existing row or contested finding).
4. **File the digest**: append a dated section (newest on top) to the project's radar inbox file, with a **"Needs your attention" shortlist** at the top (borderline scope, weak/uncertain quality, possible duplicate or supersession, partial reads, contested-finding impact). Summarise the shortlist + one line per keeper in your reply.
5. **STOP.** Approvals are per-paper and human; on a yes, integration runs through literature-review Mode 1 Step 8 (backup, write, verify), then a Mode 2 regeneration syncs the vault.

## Mode S — cold-start seeding (a NEW project with few or no known papers)
The sweep above is *maintenance*: it assumes a corpus to dedup against and watches for what's new. A project starting near-zero needs the opposite motion — **finding the field, backwards**. On "help me build a starting corpus":
1. Interview for 2–3 **anchor papers** the user already trusts (or find the field's recent *syntheses* first — reviews and meta-analyses are pre-aggregated reading lists).
2. **Citation-snowball from the anchors** programmatically via the open citation-graph APIs — OpenAlex (free, no key) and Semantic Scholar's Graph API — walking references (backward) and citations (forward) one or two hops, ranked by citation count within scope. These are the same graphs the visual explorer tools ride on; suggest **Connected Papers / ResearchRabbit** to the user as *interactive* companions for the same job (Connected Papers has a Python client with access tokens on request; ResearchRabbit has no public API — but it sources from Semantic Scholar/OpenAlex, so the skill reaches the same data directly).
3. Deliver as a **seeding digest** (same triage-ready format), explicitly marked provisional: tiers on a young corpus are guesses that firm up as the matrix grows. Then switch the project to normal radar cadence.

## Scheduling
The cadence lives in the conventions (e.g. 1st and 15th). Pair this skill with the platform's scheduler (a scheduled task/cron that invokes "run the literature radar for ⟨project⟩") for hands-free runs; any manual "run my radar" works between schedules. Each digest section is dated — the next run reads the previous ones as its dedup floor.

## Boundaries
Never write to the matrix or synthesis · OA-only fetching · declare search-coverage limits honestly (engine, region, recency) · a candidate the user rejects goes into the digest's record (so it never resurfaces as "new") — rejection is information.

## Lessons burned in (provenance)
Field-neutralized from the maintainer's own twice-monthly radar (which pre-screens into a triage-ready `RADAR_INBOX.md`): the pre-filled-digest principle ("the user opens a near-finished triage, not raw candidates"), the attention-shortlist-first layout, OA-only discipline, dedup against *three* surfaces (matrix, folder, prior digests), and the precision-over-recall stance that makes "nothing new" a trustworthy answer.
