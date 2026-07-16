---
name: citation-integrity
description: Verify that a manuscript's references are real, correctly attached, un-retracted, and honestly cited — the pre-submission citation-integrity pass. Use when the user wants citations/references checked, verified, or audited ("check my citations", "verify my references", "are these citations real", "did I cite anything retracted", "integrity pass before I submit"), whether or not they use the render pipeline.
---

# Citation integrity — verify references are real, right, and honestly cited

You audit the **truth** of a manuscript's citations (the render pipeline handles their *formatting*). **Prime directive: flag, never guess.** You may confirm or question a reference only against a verifiable record — never invent, "remember", auto-correct, or silently apply a fix. Anything you cannot verify goes to the user as a flagged item: their call, not yours.

**The rules you enforce live in one place — `../../docs/04-citation-integrity.md` (16 rules, aligned to COPE/ICMJE).** This skill does not restate them; it operationalises them. Read that file and key every finding to its rule numbers.

## What you need
- The **manuscript** — the Markdown draft, or the rendered `.docx` / reference list.
- The **bibliography** — the project's `library.bib` (the render-time source of truth) and/or the **live Zotero library** when the `zotero` MCP tools are present (prefer live Zotero for field checks; the export can be stale).

## The pass — layered gates, most objective first
Run the tool-backed checks before the judgement calls, so machine-verifiable facts are settled independently of any AI reading.

1. **Resolve & consistency (tool).** `python3 ../../starter-kit/resolve_check.py <library.bib> --mailto=<user's email>`. For every DOI-bearing entry it confirms the DOI *resolves* to a real Crossref record **and** that the record's title / year / first author *match* the entry — catching both dead DOIs (rule 3) and a DOI attached to a *different* work (mis-attach / "Frankenstein", rule 2). For DOI-less entries it *proposes* type-matched candidate DOIs for the user to verify — it never assigns them. Exit code 2 = at least one UNRESOLVED or MISMATCH; surface those first.
2. **Retraction (tool).** `python3 ../../starter-kit/check_retractions.py <library.bib> --mailto=<user's email>` (Crossref, which incorporates the Retraction Watch database). Report any retraction / withdrawal / expression-of-concern prominently; list DOI-less entries for hand-checking (rule 14).
3. **Preprint → version-of-record (tool).** `python3 ../../starter-kit/vor_check.py <library.bib> --mailto=<user's email>`: for every preprint-typed entry, Crossref is searched for a published journal version, guarded against same-title/different-authors false positives by requiring **author-surname overlap** in the evidence. Candidates are proposals — the user verifies and updates the record in Zotero (**pin the citekey before editing the year**, or the key churns and orphans the draft). Enforces rules 4/6: cite the preprint as such, or the version of record once it exists.
4. **Orphans, both directions.** Every in-text `[@key]` resolves to exactly one reference-list entry and vice versa (rule 11). The render enforces this via `(key?)` warnings — verify against the **rendered** file, not assumptions.
5. **Field completeness & version.** Flag entries missing a year (they render "n.d.") or a DOI; check edition / reprint / preprint-vs-version-of-record consistency, asking which copy the user actually read when it matters (rules 3, 4).
6. **Honesty of the citing (ask, don't assume).** Confirm read-status of anything not obviously worked with; flag secondary sources to be declared "as cited in"; flag weak evidence used as load-bearing; flag preprints to be marked as such; note primary-source substitutions (rules 5, 6, 7).
7. **Quotes.** Every quotation is verbatim and carries a page / section locator (rule 9).
8. **Optional deeper — claim-faithfulness spot-check (opt-in; ask first).** For a sample of load-bearing citations, *if the source text is reachable* (a Zotero PDF / annotation, or an open-access full text), fetch the relevant passage and judge whether it actually supports the specific claim it is attached to (rule 1). Report supported / not-clearly-supported / couldn't-check — never downgrade a citation silently. This augments the human's judgement; it does not replace reading.

## Propose, never apply
When a check suggests a fix — a candidate DOI, a year correction, a likely-wrong attachment — **present it as a proposal the user applies in Zotero**, with the evidence and a confidence read. Never edit the `.bib` or the draft yourself to "fix" it (rule 13). The correct fix is usually in Zotero, not the draft, and a silent edit is how a correct record becomes a wrong one.

## Report — deterministic, keyed to the charter
Three buckets, each item tagged with its `docs/04` rule number:
- **✓ Verified** — resolved + matched + un-retracted (the tool-confirmed set; state the count).
- **⚠ Flagged** — with the specific reason and the fix to make in Zotero (mismatches, unresolved DOIs, missing years, orphans, undeclared secondary/preprint, un-located quotes).
- **○ Unverifiable / your call** — anything a tool couldn't settle (DOI-less books, read-status, claim-faithfulness where the text wasn't reachable). Hand these over plainly.

Close with the one reminder no tool can give: the venue-required **AI-use disclosure** at submission (rule 15).

## Boundaries
Verification and bookkeeping only. *Whether* to cite, *what* to read, and *what a source actually says* stay human decisions (rule 5). An AI may format and check a citation — it may never supply one.

---
*Provenance of the checks: the resolve-and-consistency and opt-in claim-faithfulness gates adapt ideas seen in comparable projects (multi-index DOI resolution; sampled claim audits) to this pipeline's charter-first, propose-never-apply model; the retraction check and the 16-rule charter are this project's own.*
