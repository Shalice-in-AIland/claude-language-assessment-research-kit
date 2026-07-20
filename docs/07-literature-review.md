# Your living literature review — one matrix, three views, an independent auditor

*The citation pipeline (docs/01–02) formats what you cite; this page is about deciding and remembering **what your field says** — the review you build over months. The `literature-review` skill runs it: **you** read papers and make every judgement call; **Claude** drafts, files, projects, counts, and audits — and never changes anything without your yes.*

> **Who does what.** Your part is the scholarship: reading papers, ruling in/out, choosing tiers and ★ KEY, blessing the theme vocabulary. Claude's part is everything mechanical: drafting each paper's row for your approval, keeping the matrix tidy, generating the Obsidian views, and running the checks. The one standing rule everywhere: **flag, never guess; propose, never apply.**

## Think of it as…

- **The matrix** (a spreadsheet, one row per paper) is your **specimen register** — the single source of truth about what's in the review and what you decided about it.
- **The vault projection** (Obsidian) is the **reading room built from the register** — one note per paper, hub pages per theme and method, a clickable graph. It is *generated*: never edit these notes; fix the matrix and regenerate.
- **The dashboard** is the **wall chart** — standing counts (tiers, read-status, ★ KEY register, theme and method coverage) that answer "what does my review hold?" at a glance.
- **The audit** is an **independent co-rater from another lab** — a second, different-vendor AI that re-judges every row against *your own rules* and files its disagreements as questions for you.

## Getting started (once per project)

**Say to Claude: _"set up my literature review."_** It interviews you to fill one page of rules — `review-conventions.md`: what's in and out of scope, what the relevance tiers mean, and your **theme vocabulary**. That vocabulary is the anti-sprawl device: aim for **ten-ish entries**, because themes are the section headings of your future lit-review chapter, not keywords. (A paper *lives in* one theme; it can *use* many methods and tools — those get **hub terms**, which are unlimited and mechanical.) **You should see:** a one-page conventions file in your project that reads like your own lab rules — because it is; every later step obeys it.

## Daily use — one move

**Say: _"triage this paper"_** (with a PDF, DOI, or citation). Claude reads it — declaring honestly *how well* it could read it (scanned PDFs and figure-heavy results get flagged, not faked) — and returns a complete triage report: in or out, the drafted matrix row, a tier and KEY recommendation with one-line rationales, a quality checklist that **flags weaknesses but never excludes** a paper, and how it sits against your existing corpus (corroborates? contradicts? supersedes?). **Then it stops.** Nothing is written until you say yes; on your yes, the row lands with a dated backup and an integrity check.

## Finding the papers in the first place (discovery, before triage)

**Building a corpus from scratch — or already have a few key papers and want the work around them? Say: _"help me find related work from these anchor papers."_** Claude walks the citation graph outward from your seeds — following *references* (backward) and *citations* (forward) — and hands you a triage-ready seeding digest. It does this on the **same open citation data (OpenAlex, Semantic Scholar) that the popular visual explorers ride on** — so if you'd rather browse it visually, or double-check coverage, those tools are a good **cross-check**: [ResearchRabbit](https://www.researchrabbit.ai/), [Litmaps](https://www.litmaps.com/) (whose *Monitor* emails you new papers on a saved map — the manual version of CLARK's radar), and [Connected Papers](https://www.connectedpapers.com/) (a *similarity* map rather than a citation trail). Because they share the underlying data, treat them as a coverage cross-check, not an independent source.

One honest limit — the same one those tools carry: this is **discovery, not exhaustive search**. For reproducible completeness, systematic database searching (Scopus, Web of Science) still leads; the radar and the snowball complement it, they don't replace it. Then, to keep watching for new work: **_"set up a literature radar"_** runs scheduled sweeps in your scope, pre-screened into the same triage-ready digest.

## The Obsidian views (optional, and worth it)

**Say: _"update my literature notes."_** Claude dry-runs first and shows you the plan, then generates into your vault:

- **One note per paper**, named by its citekey, carrying your matrix columns as properties, your key points verbatim, and a **Show in Zotero** link (one click from note to the full paper).
- **Theme and method hubs** listing their member papers — open `Method — ⟨your statistic⟩` and see every paper that uses it; open the graph and watch your review arrange itself around the hubs.
- **`Review Dashboard.md`** — the wall chart, regenerated every run.

Afterwards you can **say: _"lint my literature notes"_** — Claude reports orphan notes (papers no longer in the matrix), broken links, and any hub whose member list has drifted from the matrix. It reports; you decide what to prune.

Three guarantees: generated files carry a marker, and **anything you hand-edited is skipped, never overwritten**; themes outside your vocabulary are **flagged, never invented**; and the matrix stays the source of truth — the views are always rebuildable, so deleting them costs nothing.

## The audit (highly recommended before submission milestones)

**Say: _"audit my review."_** A second AI — deliberately from a **different vendor** than the one that drafted your rows — re-judges every row against your conventions and files a propose-only report: tier disagreements, ★ KEY challenges, and internal inconsistencies (a row whose flags contradict its notes), each with a field pointer and, where the row itself contains the answer, a suggested fix. Disagreements are **questions, not corrections** — you adjudicate. Practicalities Claude will walk you through: it needs **your own API key** (set in your own shell, never shared in chat — and check your institution's policy on external AI services first); it always **dry-runs and pilots a few papers first** so you see the measured cost before committing (real reviews have measured at roughly **1–2 US cents per paper**); and the model, effort, and prompt version are **pinned in your conventions** and stamped into every report, so audits are reproducible and comparable over time.

## The model radar

Pinned models are a promise that needs maintenance: vendors retire model names quietly, reprice tiers, and revise their prompting guidance — and a dead pin breaks your audit months later, silently. **Say: _"check my model pins"_** (or let a monthly scheduled task say it for you): the `model-radar` skill verifies every pinned model still exists and isn't scheduled for retirement, notes material changes in the vendors' prompting guides, and flags price changes that alter the budget-vs-frontier arithmetic — one dated, propose-only log entry per run. A dead or retiring pin is the highest-priority finding; you edit the conventions, the radar never does. What no audit does: certify truth, or replace your reading — it checks *consistency with your own rules*, and the final calls stay yours, made at write-up time with the papers in hand.

## The habits that keep it healthy

1. **Fix the matrix, not the notes** — then regenerate; the views follow.
2. **Grow the vocabulary deliberately** — one approved entry at a time; merge variants with the `Entry <= alias` syntax rather than letting near-duplicates multiply.
3. **Audit at milestones** — before submission, after big triage batches; diff the reports over time.
4. **Trust the flags** — "unlisted theme," "read basis: figures not visible," "requires the paper" are the system telling you where *your* eyes are needed. That's the design working, not failing.

*Verified July 2026: generator and auditor exercised end-to-end on a real 104-row review matrix (85 projected notes, a full second-model audit census, and an effort-level comparison). Both tools are standard-library Python — no installs; commands for by-hand use are in each script's header in `starter-kit/`.*
