---
name: model-radar
description: >-
  Maintenance watch over the AI models a project's audit layers pin. Use when a
  scheduled model-radar day arrives, when the user asks "check my model pins",
  "is my audit model still alive", "any prompting-guide changes", or once at
  audit set-up time. Verifies every pinned model ID still exists and isn't
  scheduled for retirement, diffs the vendors' current prompting guidance, and
  notes new releases and price changes relevant to task tiering — propose-only,
  appended to the project's model radar log.
---

# model-radar — the maintenance watch on pinned models

The audit layers pin exact model IDs and prompt versions for reproducibility (the `## Audit` section of `review-conventions.md`). But vendors retire model aliases, reprice tiers, and revise their prompting guidance — and a dead pin silently breaks a project's audits months later. This skill is the standing check that catches that early. It changes nothing itself: findings are proposals; the user edits their own conventions.

## The three homes (check all, every run)

1. **Pinned-ID liveness — the priority check.** For each model pinned in the conventions (`model:`, `manuscript-model:`): verify the ID still exists — query the provider's `/v1/models` endpoint using the user's own key (the environment variable named in `key-env`; test presence only, never print or echo any part of a key; if unset in this session, say "verify manually" and fall back to the vendor's models/deprecations page via web search). Also search for announced retirements of the pinned IDs. **A dead or retiring pin is the highest-priority finding.**
2. **Prompting-guide deltas.** The vendor guides that govern the project's prompts — the guide for the audit scripts' model family, and the Claude prompting guidance that governs skill authoring. Diff against the log's previous entry; report material changes only. If guidance changed enough to warrant a prompt revision, recommend a review and remind: **any prompt change bumps the pinned `prompt-version`**.
3. **Releases and prices.** New models or tiers relevant to the task-tiering doctrine (budget tier for volume row-audits, frontier tier for whole-manuscript audits), and price changes that alter that math.

## Output — one propose-only log entry

Append a dated entry, newest on top, to the project's model radar log (default: `Model radar log.md` beside `review-conventions.md`; create it with a short header on first run — the log is also the radar's memory between runs). Open with a verdict line: **NO CHANGES** / **CHANGES — see below** / **⚠ ACTION NEEDED** (a dead or retiring pin). Everything is a recommendation; the radar never edits conventions, skills, or scripts. A "no changes" entry still gets logged — it is the next run's diff baseline.

## Scheduling

Monthly fits how fast models move relative to review projects. Pair with the platform's scheduler ("run the model radar for ⟨project⟩", e.g. the 1st of each month); any manual "check my model pins" works between runs. Scheduled sessions often lack the user's key environment — use the web fallback and say so in the entry.

## Boundaries

Report-only · never touches conventions, prompts, or scripts · key-env names only, never key values · findings cite their source (the vendor page or endpoint checked).

## Provenance

Field-neutralized from the maintainer's live monthly radar, whose first scheduled run caught a newly published vendor prompting guide and a missing frontier-tier pin on the same day — both would otherwise have surfaced mid-audit. The user-facing summary of this doctrine lives in `../../starter-kit/review-conventions-template.md` (the "Model radar" paragraph); the founding example is a retired model alias: pins die quietly, which is why the radar exists.
