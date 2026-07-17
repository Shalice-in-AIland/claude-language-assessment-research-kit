# CLAUDE.md — Claude Language Assessment Research Kit (CLARK)

**What this repo is.** A public, field-scoped toolkit of Claude Code skills for researchers in **language assessment / applied linguistics / EAP writing research**. Each skill packages a complete, integrity-first workflow; Claude operates the machinery, the scholar keeps the judgement calls. Maintainer: Sha Liu. License: MIT (except `starter-kit/style.csl`, CSL project, CC BY-SA — noted in LICENSE).

## Layout
- `skills/zotero-citations/` — the citation pipeline operator (Zotero → Better BibTeX → Pandoc → Word); guided onboarding for users who have never used any of the tools.
- `skills/citation-integrity/` — standalone pre-submission reference audit: DOI resolve-and-match, retraction check, preprint→version-of-record check (`starter-kit/resolve_check.py` · `check_retractions.py` · `vor_check.py`); enforces `docs/04`.
- `skills/literature-review/` — living review matrix (approval-gated triage; matrix = source of truth) + generated Obsidian views via `starter-kit/matrix_to_vault.py`; per-project rules live in that project's `review-conventions.md` (template in starter-kit); optional cross-vendor row audit (`starter-kit/review_audit.py`).
- `skills/literature-radar/` — the standing watch: scheduled/on-demand sweeps → dedup (matrix + folder + digests + Zotero) → pre-screened triage-ready digest; discovery-only, feeds literature-review Mode 1.
- `skills/pre-submission-review/` — evidence-anchored evaluation of the USER'S OWN manuscript only: two-pass evidence discipline (ledger with PASS/FAIL recomputation, claim–warrant checks, triage gate), revision plan + 0–100 estimate with readiness verdict, live author-instructions compliance, fresh-agent verification, optional cross-vendor audit (`starter-kit/manuscript_audit.py`, gated by `--confirm-send`). `references/` = the two article-type criteria modules (built from publisher/journal-provided reviewer material) + what major venues tell their reviewers to look for.
- `skills/writing-polish/` — five-dimension polish of the user's own prose (accuracy corrected directly with a change log; everything stylistic propose-only), built for multilingual and early-career academics.
- `skills/model-radar/` — the maintenance watch on pinned audit models: pinned-ID liveness (highest priority: dead/retiring pins), vendor prompting-guide deltas, release/price changes → one propose-only log entry per run; keeps the audit layers reproducible.
- `docs/00–08` — the user-facing operator's manual (project wiring + session hygiene, setup, daily use, troubleshooting, the integrity charter, the Zotero-MCP upgrade, Obsidian-as-editor, the living literature review, the pre-submission review) + the flowchart twins (`flowchart.md` — Mermaid, renders on GitHub; `flowchart.html` — styled, printable; keep them in sync) + `images/`.
- `starter-kit/` — the copy-into-your-project kit: `render.sh`/`render.bat`, `style.csl` (APA 7th default, swappable), sample `library.bib` + draft, and the stdlib-only Python tools (`resolve_check` · `check_retractions` · `vor_check` · `pdf_probe` · `matrix_to_vault` · `review_audit` · `manuscript_audit` · `clark_doctor`).
- `_private/` — the maintainer's records, git-ignored, never published. **Maintainer sessions: if `_private/CLAUDE-maintainer-log.md` exists, read it at session start** — it carries the working history, state, and roadmap. (In a downloaded copy of this repo that file doesn't exist; ignore this line.)

## Non-negotiable design rules
1. **`docs/04-citation-integrity.md` is the single source of truth for the 16 integrity rules** (COPE/ICMJE-aligned). Skills reference it; never fork or restate the rules elsewhere.
2. **Flag, never guess; propose, never apply.** No skill or script invents, "remembers," or silently corrects a reference. Fixes are proposed with evidence; the user applies them in Zotero. Scripts only ever *report* (exit codes for gating).
3. **An AI may format and check citations — it may never supply one.** Reading, choosing, and interpreting sources stay human.

## Doc-writing standard (all user-facing docs)
- **Automatic-first:** lead with "ask Claude to ⟨do X⟩". If a step needs nothing from the user, do **not** document the how-to in the main guides — one sentence pointing at Claude. Raw commands live only in the by-hand homes: `starter-kit/README.md` (render + terminal how-to) and `docs/03` (Pandoc install).
- **Signpost who-does-what:** the user does the clicks *inside Zotero* + the judgement calls; Claude does terminal work, rendering, and audits.
- **Plain language** (every tool gets a "think of it as…"; every step ends with "You should see…"). **Field-neutral examples** (generic citekeys; no personal-project content). Illustrative *output* (e.g. a `(key?)` warning) is fine — that explains a feature.
- Exceptions: `SKILL.md` files are Claude-facing and stay prescriptive; `docs/04` is a rules charter and stays strict.

## Skill house style
- A `SKILL.md` opens with a clean title + what-the-skill-does — no persona taglines, no rhetorical essay openers; descriptive title suffixes are fine.
- Any YAML `description:` containing ": " must be a `>-` block scalar (a bare colon-space breaks YAML compact-mapping).
- Validation accounts in docs stay generic: real projects and test materials are never identifiable in this repo.

## Positioning (verified 2026-07-13, point-in-time)
Benchmarked against: ARS (`Imbad0202/academic-research-skills`, ~37.7k★, CC BY-NC — ideas only, never code), `Galaxy-Dawn/claude-scholar` (~4.6k★, MIT), `54yyyu/zotero-mcp` (~4.3k★, MIT — the MCP server the Level-2 upgrade uses). CLARK's niche (found open): the focused **render + citation-integrity layer, novice-first, field-scoped** — none of the big generic pipelines renders *and* enforces a retraction-checked integrity charter. CLARK *consumes* generic infrastructure (zotero-mcp, Pandoc) rather than forking it.

## Provenance & sweep discipline
- External ideas are adopted with credit and license respect: MIT projects may be consumed or adapted with attribution; CC BY-NC projects are ideas-only; every CLARK script is written fresh, standard-library-only.
- Before any public push: sweep the tree for credentials, local paths, personal names/emails, personal-project content, and private-folder references. `_private/` and `.claude/settings.local.json` stay git-ignored.
