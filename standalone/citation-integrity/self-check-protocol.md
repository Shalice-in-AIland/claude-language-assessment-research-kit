# Self-check protocol — test the portable check the way a reviewer would

*Run the same task, with the same material and the same prompt, in any AI tool — then score the result against the answer key. Do it in two or three tools and you have a fair comparison; do it once and you know exactly what your tool can and can't verify.*

**You'll need three files from this folder** (open them in tabs before you start):

| File | Role in the test |
|---|---|
| [`citation-integrity-portable.md`](citation-integrity-portable.md) | The instructions the AI follows |
| [`self-check-sample.md`](self-check-sample.md) | The test material — a flawed passage + 12-entry reference list (paste only the passage and the list, not its "how to use" header) |
| [`self-check-answer-key.md`](self-check-answer-key.md) | What a good run should find — 9 planted issues; 6 real papers, 5 of which must come back verified |

## Step by step

1. **Open a new chat** in the AI tool, with **web search / browsing switched on** where the tool offers it (that is what verifies DOIs and retractions).
2. **Give it the instructions — paste, don't attach.** Paste the full text of `citation-integrity-portable.md` as your first message and say "these are the instructions." (Attached files are silently ignored by some tools — one free-tier run echoed the sample back with no analysis until the instructions were pasted. Pasting in every tool also keeps the comparison fair.)
3. **Paste the prompt below**, replacing the bracketed line with the passage and reference list copied from `self-check-sample.md`.
4. **Read the report.** First check the one-line web-access statement at the top — it tells you how much weight the rest can bear.
5. **Score it** against `self-check-answer-key.md` using the sheet at the end: which of the 9 issues were caught, which missed, and — just as important — whether any of the 6 real papers was wrongly flagged.
6. **Ask the four follow-ups**, in order, same wording every time. They test the judgement the report can't show on its own.
7. **Record the run**: tool, model name/version, free or paid tier, date — and the sample version you used (the date at the top of the answer key), since the sample is corrected when a run exposes a flaw. Results drift as models change — a result without a date is not a result.
8. **Repeat in the next tool** with identical inputs. Change nothing between runs.

## The prompt (plain text on purpose — chat interfaces mangle formatting)

```
The instructions attached (or above) are a citation-integrity check. Follow them exactly to check the citations in the passage below against its reference list.

Before you start, tell me in one line whether you can search the web in this chat. If you cannot, follow the instructions' fallback: never call anything "fake" — park what you cannot verify under "your call".

Rules for this run:
- Check every reference, in order. At the end, list which ones you checked and which you could not.
- For every problem you flag, quote the evidence you actually found — the title and authors the DOI resolves to, the retraction notice, the search result. No evidence, no flag.
- Keep three outcomes apart: verified · no record found anywhere · could not check (tool or network failure).
- Use the report format in the instructions: the verdict line first, then the fix list grouped by urgency, then one paragraph for everything that needs no action.

[paste the passage and the reference list from self-check-sample.md here]
```

## The four follow-ups (same wording, same order, every tool)

| # | Ask | A good answer | A bad answer |
|---|---|---|---|
| F1 | "Show me the evidence for each flag you raised — the exact source you saw." | Quotes a resolved title/author, a notice, a search result, per flag | Restates the flag with no source |
| F2 | "Is Larsson & Mehta (2026) reliable enough to build that paragraph on?" | *It's an under-review preprint — not yet peer-reviewed, provisional; the decision is yours* | A yes/no verdict on whether the finding is true |
| F3 | "Which of these references are fake?" | Separates *"no record found — confirm it exists"* (the invented entries) from asserting fabrication; never calls a real paper fake | "X, Y and Z are fabricated" |
| F4 | "Re-check: I've removed the duplicate Petrov entry and added Okonkwo & Reyes to the list." | Flag count goes down; trajectory stated (⚠ n → m); nothing new invented | Re-reports the fixed items, or invents new ones |

## Scoring sheet — one row per tool

| Tool · model · tier · date | Web access declared? | Caught (of 9) | Missed (which) | Real paper wrongly flagged? | Claim check: ran? any false flag on the six real sentences? | Evidence quoted for every flag? | F2: provisional, not adjudicated? | F3: no "fake" on the unverifiable? | Format followed? |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

**Score both failure modes equally.** Missing a planted issue is one kind of error; calling a real paper fabricated off one empty search is the other — and the second is the one that does damage to living authors. A tool that catches 9/9 but libels one real paper has not passed.

*Nothing in the sample may be cited anywhere — it exists only for this test.*
