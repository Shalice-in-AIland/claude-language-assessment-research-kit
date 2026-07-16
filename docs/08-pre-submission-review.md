# Your pre-submission review — page-anchored findings, a revision plan, a score

*The literature skills (docs/07) manage what your field says; this page is about what your field will say **about your paper**. The `pre-submission-review` skill evaluates **your own manuscript** before you submit it — through the same section-by-section questions the target journal's reviewers will be asked, while every problem still costs a revision instead of a rejection. It is for your own drafts only: reviewing someone else's submission for a journal is a different activity, with confidentiality obligations this skill does not manage.*

> **Who does what.** Your part is the scholarship: confirming what the paper claims, adjudicating the list of concerns before anything is written up, deciding what to change — and making the **AI-use declaration** your target journal requires. Claude's part is the legwork: reading the manuscript (and saying honestly how well it could read it), recomputing the statistics, checking every number in the abstract against the tables, fetching the journal's current author instructions, and drafting the plan. The standing rule: **a concern without a page number is not a finding** — nothing vague enough to be uncheckable gets raised.

## Think of it as…

- **The evaluation** is a **dress rehearsal with the real script** — the criteria come from what publishers put on their reviewer forms and what your target journal tells its reviewers to look for, per article type (original research vs. review article).
- **The evidence notes** are the **lab notebook behind the review** — every observation carries a page number; every checkable number is recomputed and marked PASS or FAIL; a "do-not-raise" list records what *looked* wrong but checks out, so you never burn time on non-problems.
- **The score** is a **fuel gauge, not a verdict** — a 0–100 estimate derived from the findings, useful for trajectory (re-score after revising and watch the direction), never a prediction of what an editor will decide.

## One move

**Say: _"Read skills/pre-submission-review/SKILL.md and review my draft for submission to ⟨journal⟩."_** Claude reads the manuscript, loads the article-type criteria and your journal's reviewer guidance, builds the evidence notes — then **stops and shows you the concern list** (fatal / major / minor) before writing anything up. That pause is yours: you know your study better than any reader, and a misunderstanding is cheapest to catch there. On your go, it writes the revision plan. **You should see:** first a short triage list to approve or correct — *no score yet; the score is computed from the triage you've corrected, so it arrives with the plan* — split into two blocks: **verified facts** (recomputed numbers, checked citations — skimmable) and **needs your expert judgment** (construct questions, severity calls on conceptual issues — the layer where your read outranks any model's). Then two files next to your manuscript: the evidence notes and a prioritized revision plan ending with the score and its drivers. (Reviewing a half-finished draft is normal and encouraged — the earlier the cheaper; you'll get a score for the written sections, and the full readiness score when the draft is complete.)

## What the plan contains

- **A verdict paragraph** — what the paper genuinely contributes, then the honest read on where it stands, ending in an explicit readiness verdict (ready to submit · major revision first · structural work first · not yet assessable — partial draft).
- **Prioritized fixes**, each with the concern stated up front, the page-anchored evidence, why it matters, and a concrete remedy (often as options) — labeled must-fix vs. would-strengthen.
- **A compliance checklist** from the journal's *current* author instructions (fetched live: word limits, structure, anonymization, data statements — and the AI-use declaration), including a preprint pass: whether the venue says anything about citing preprints, whether any cited preprint now has a published version to cite instead (checked automatically), and whether any key claim leans on a source that hasn't been peer reviewed.
- **The score, with its honesty clause attached**: 85+ submit after the minors · 70–84 major revision first · below 70 structural work first — and always the caveat that this is one AI reading, not an editorial outcome.

Before delivery, a **fresh checker** — with no memory of writing the plan — re-reads the manuscript and the plan and verifies every page reference, every quoted number, and every criticism against the actual text. Self-checking rereads what you meant; the fresh pass reads what you wrote.

**Optional: a second reviewer from another lab.** On your explicit request, a second AI — deliberately from a **different vendor** — re-judges the whole review: it concurs with or disputes each finding (with evidence), proposes anything the first review missed, and gives its own independent score. Real reviewers diverge on the same paper; two independent reads tell you how solid the verdict is. Practicalities Claude walks you through: this **sends your unpublished manuscript to that provider**, so it is your call every time — your own API key (never shared in chat), your institution's policy on external AI services, and a dry-run first so you see the cost before anything is transmitted (real audits measure in cents). The report is propose-only: disagreements are questions for you, not corrections.

## Revising after peer review?

Run it again on each revised version — **say: _"review my revision against the reviewers' comments."_** It audits every prior comment as resolved, partial, or *responded-but-not-resolved* (a response letter is not a fix — it checks the manuscript actually delivers what the letter claims), checks that the abstract and highlights caught up with the body (they are where fixes go to be forgotten), sweeps for sentences duplicated when text was moved, re-checks the references both ways, and re-scores so you can watch the trajectory. Where two reviewers pull in opposite directions — it happens between entirely competent reviewers — it names the tension and recommends a resolution instead of pretending both can be satisfied verbatim.

## The habits that keep it honest

1. **Correct the triage before the prose** — the pause exists so your knowledge of the study overrides a misreading.
2. **Use the score for direction, not absolution** — re-score after revising; the trend is the information.
3. **A flagged "couldn't check" is your cue** — figure-heavy results and scanned pages get named, not guessed at; those are the pages your eyes are for.
4. **The declaration is yours** — most journals now require authors to declare AI use, and depending on the journal's wording, an AI evaluation like this one may itself belong in the declaration. Check the instructions for authors; the call is the author's.
5. **Keep the outputs with the manuscript** — the notes and plan quote your unpublished draft, so they are part of its confidential record: store them beside the manuscript, never in a public folder or repository. And never run this on a manuscript you are *reviewing* for a journal — that is a different role with obligations this tool does not manage (most publishers prohibit uploading others' submissions to AI tools at all).

*The criteria are field-wide, not project-specific: the section-by-section questions come from publishers' structured reviewer forms and the reviewer guidance of the field's major journals (see the skill's `references/`), applied to original research and research syntheses alike. The workflow has been validated in a blind test against a published article's complete three-round review history — the tool's verdicts tracked the real editorial decisions at every round, and its mechanical findings included errors that survived every human stage into print. (The test materials are private; none appear in this kit.)*
