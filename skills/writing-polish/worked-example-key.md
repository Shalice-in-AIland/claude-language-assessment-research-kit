# writing-polish — worked-example key

*Expected outcomes for [worked-example.md](worked-example.md). Score a run against every row. Wording will differ between runs; what is scored is whether the right thing was found, on the right layer, in the right direction.*

**Pass rule.** Every must-not holds, every required element is present, and every expected item is found. A violated must-not is a defect in the skill. A missed expected item is a regression to investigate.

## Expected: accuracy, corrected directly and logged

| # | Original | Expected | Layer |
|---|---|---|---|
| A1 | "The raters was trained" | "The raters were trained", corrected in place and listed in the change log | accuracy, corrected directly |
| A2 | "overestimated scores in low proficiency" | A tracked-changes-style suggestion offering a reading such as "for low-proficiency essays" or "at low proficiency levels", because two corrections are plausible and they differ in meaning. A silent correction to one reading fails this row. | accuracy, meaning-risk |

## Expected: style proposals, numbered, each with a reason

| # | Original | Expected direction | Dimension |
|---|---|---|---|
| S1 | "the analysis of the scores was conducted using" | A verb in place of the nominalisation, e.g. "we analysed the scores using" | clarity |
| S2 | "a lot of attention" | A formal equivalent, e.g. "considerable attention" | formality |
| S3 | "Roe clearly failed to notice this problem [@roe2023]" | About the evidence rather than the person, e.g. "earlier work did not report this pattern [@roe2023]". The citation stays attached to that claim. | register and conventions (stance also accepted) |
| S4 | "This proves that the model cannot replace human raters" | A flagged proportionality proposal: "proves" claims more than 48 essays can carry, and the author decides. Silently changing "proves" fails this row. | stance |

## Expected: voice restoration in paragraph 2, matched to the author's first draft

| # | Fault in the revised paragraph | Expected restoration |
|---|---|---|
| V1 | "high overall — but it concealed" | The dash replaced by the author's own connective: "However, this agreement concealed" |
| V2 | Three claims chained through semicolons | Separate sentences with their dependence stated, restoring "Consequently" before the claim about the overall statistic |
| V3 | The fragment "A clear limitation." | A full predicate, or folded into the restored sentence about the prompts |
| V4 | The run-in label "**Key implication:**" | Converted back to prose |
| V5 | "the prompts were not varied" severed from its consequence | The causal frame rejoined as in the draft: "Furthermore, because the prompts were not varied, we cannot say whether…" |
| V6 | The author's short pivot "This matters." missing | Optional. Restoring it, or noting its loss, scores; omitting it does not fail the run. |

## Must not happen

| # | Must not |
|---|---|
| N1 | The long sentence beginning "Because the model received…" is split. It is long but well subordinated, so the clarity dimension leaves it alone. |
| N2 | "κ = .71, n = 48 essays" changes in any character. |
| N3 | "[@doe2019]" or "[@roe2023]" changes, or ends up attached to a different claim. |
| N4 | "many-facet Rasch measurement" is reworded. |
| N5 | The output says or implies anything about how paragraph 2 was produced beyond the author's own statement, or mentions AI detection. |
| N6 | A restoration adds a claim, or changes claim strength, that is not in the author's first draft. |
| N7 | A full rewritten section is delivered without being asked for. |
| N8 | A dimension is reported to the author as a bare letter. |

## Required elements

| # | Required |
|---|---|
| R1 | A reminder to check the venue's AI policy and make whatever declaration it asks for |
| R2 | A recurring-patterns note of at most three patterns, each pointing at a free resource |
| R3 | Style proposals in the form original, proposed, one-line reason |

## Acceptable extras

A run may raise these. Each is correct, none is required, and none counts against a run, provided it arrives as a proposal or a flag rather than an edit.

- **The narrative citation renders the name twice.** "Roe … [@roe2023]" prints as "Roe … (Roe, 2023)"; the narrative form is `@roe2023`. This was not planted, and the right response is to flag it and leave it alone, because citations are on the preserve-list. A run that rewrites the citekey violates N3.
- Splitting "human raters, and Roe" into two sentences, since the "and" joins two unrelated claims.
- A paragraph break before "Because the model received…", with no words changed.
- Treating S3 as a flagged proportionality proposal rather than a plain register proposal.
- Pointing the author at the `pre-submission-review` skill because claim-strength flags cluster in two paragraphs.

## Runs

| Date | Model | Session | Result |
|---|---|---|---|
| 2026-10-22 | claude-opus-5-5 | Fresh, reading only `SKILL.md` and `worked-example.md` | **Pass.** All 12 expected items found, including the optional V6. All 8 must-nots held. All 3 required elements present. Raised all five acceptable extras. |
