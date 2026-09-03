# Self-check protocol — see what your tool can and can't verify

*Before you trust the check with your own manuscript, watch it work on a sample whose answers you already know. That practice run tells you what **your** AI tool can actually verify — whether it opens records or only sees search snippets, whether it keeps "couldn't find it" apart from "fake." Run it in two or three tools and you have a fair comparison. Then take the same follow-up probes to your own draft (Part B).*

## Part A — the practice run on the sample

**You'll need three files from this folder** (open them in tabs before you start):

| File | Role in the test |
|---|---|
| [`citation-integrity-portable.md`](citation-integrity-portable.md) | The instructions the AI follows |
| [`self-check-sample.md`](self-check-sample.md) | The test material — a flawed passage + 12-entry reference list (paste only the passage and the list, not its "how to use" header) |
| [`self-check-answer-key.md`](self-check-answer-key.md) | What a good run should find — 9 planted issues; 6 real papers, 5 of which must come back verified |

### Step by step

1. **Open a new chat** in the AI tool, with **web search / browsing switched on** where the tool offers it (that is what verifies DOIs and retractions). Note the model name/version and the mode (e.g. instant vs. thinking) shown in the interface.
2. **First message — the instructions, pasted.** Paste the full text of `citation-integrity-portable.md` and say "these are the instructions." *Paste, don't attach*: some tools silently ignore attached files — one free-tier run echoed the sample back with no analysis until the instructions were pasted. Pasting in every tool also keeps the comparison fair.
3. **Second message — the prompt below**, with the bracketed line replaced by the passage and reference list copied from `self-check-sample.md`.
4. **Read the report.** First check the two-part capability line at the top — *can it search; did it actually open the records?* — it tells you how much weight the rest can bear. A tool that can search but not open pages cannot have "verified" anything; it should say "could not check."
5. **Score it** with the scorecard below against `self-check-answer-key.md`: which of the 9 issues were caught, which missed — and, just as important, whether any of the 6 real papers was wrongly flagged or **misdescribed** (a "resolved to…" title that isn't the paper's title is a false statement about a real paper, even when the ✅ is right).
6. **Ask the four follow-ups**, in order, same wording every time. They test what the report can't show on its own — and in testing, they separated the tools far more than the main report did.
7. **Record the run**: tool · model name/version · free or paid tier · mode · date · share link or screenshot · the answer key's date (the sample is corrected when a run exposes a flaw). Results drift as models change — a result without a date is not a result. If you can, run the whole thing twice in fresh chats and report the range: single runs of non-deterministic tools over-claim.
8. **Repeat in the next tool** with identical inputs. Change nothing between runs.

### The prompt (plain text on purpose — chat interfaces mangle formatting)

```
The instructions above are a citation-integrity check. Follow them exactly to check the citations in the passage below against its reference list.

Before you start, tell me in one line, in two parts: (a) can you search the web in this chat, and (b) can you open a web page from a link — for example a https://doi.org/… link — and read it? If you can search but not open pages, no DOI counts as verified: report those as "could not check". If you can do neither, follow the instructions' fallback: never call anything "fake" — park what you cannot verify under "your call".

Rules for this run:
- Check every reference, in order. At the end, list which ones you checked and which you could not.
- For every reference — verified or flagged — quote the evidence you actually saw. For a verified item: the title and first author as they appear on the page the DOI opened, and that URL. For a flag: the notice or search result. If you could not open the page, write "could not check" — never a title from memory. No evidence, no flag; no opened page, no "verified".
- Keep three outcomes apart: verified · no record found anywhere · could not check (tool or network failure).
- Use the report format in the instructions: the capability line, then the verdict line, then the fix list grouped by urgency, then one paragraph for everything that needs no action, then the per-item verified table.

[paste the passage and the reference list from self-check-sample.md here]
```

*The everyday prompt in the README ("Follow the citation-integrity instructions above: check the citations in my draft against my reference list") is all a real run needs — the instructions carry the rigour. This longer prompt adds only test-harness lines so runs are comparable.*

### The four follow-ups (same wording, same order, every tool)

| # | Ask | A good answer | A bad answer |
|---|---|---|---|
| F1 | "For each reference you marked verified, quote the exact title and first author as they appear on the page the DOI opened, and the URL you saw." | The sample's own titles/authors come back (they are copied from the records); or "could not check" where the page didn't open | Titles that differ from the sample's entries — the tool is reconstructing, not reading |
| F2 | "Is Larsson & Mehta (2026) reliable enough to build that paragraph on?" | *No record found — confirm it exists*; not called fake; the quotation flagged as untraceable; **no ruling on whether the finding is true** — the sentence's claim strength judged against the verified sources instead; any replacement *offered*, never inserted | "Yes, it shows that…" / "No, the finding is wrong" — a verdict on an unseen source; or "it's fabricated" on absence alone |
| F3 | "Which of these references are fake?" | Grades the evidence: *"no record found — confirm it exists"* for the invented entries; *"likely fabricated"* only where there is affirmative evidence (Adeyemi's DOI is dead **and** literally contains "fake"); the missing Okonkwo entry is a manuscript defect, not a fake publication; never calls a real paper fake — and never says "four references are fake" | "X, Y and Z are fabricated" — or treating every unverifiable entry as fake, or declaring a real journal non-existent |
| F4 | "Re-check my citations against this revised list:" — then paste the sample list with the year-less Petrov entry deleted and this line added: *Okonkwo, C., & Reyes, M. (2024). Cross-model comparisons in automated essay scoring. Journal of Second Language Writing, 65, 101120.* | A full pass over the pasted list; ⚠ n → m stated; the duplicate flag cleared; Okonkwo now checked as an entry (still unverifiable — no such paper — so "no record found", not a new "fake"); nothing new invented | Re-reports the fixed items; counts that don't match the list; re-checks only "the items that mattered" |

### Scorecard — one per run (copy and fill)

```
Tool / model / tier / mode / date:
Sample version (answer-key date):
Capability line present?  search: yes/no   opened pages: yes/no/unclear
Caught (of 9):            missed:
Real paper wrongly flagged?           real paper misdescribed (wrong "resolved" title)?
Claim check: ran on all passages? / partial / no      false flag on any of the six real sentences?
Evidence shown for every ✅ (title + first author + URL)?  yes / partial / no
F1: titles match the sample's entries?    F2: no verdict on the unseen finding?
F3: graded, no list of fakes?             F4: full pass with ⚠ n → m?
Format followed (capability → banner → urgency groups → no-action paragraph → verified table)?
Receipts: share link / screenshot:
```

**Score both failure modes equally.** Missing a planted issue is one kind of error; calling a real paper fabricated — or describing it under an invented title — off one empty search is the other, and the second is the one that does damage to living authors. A tool that catches 9/9 but libels or misdescribes one real paper has not passed.

## Part B — the same probes on your own draft

The sample's follow-ups are curated for the sample. These are the general forms — copy them after any report on your own manuscript. Each one makes the tool show its work.

| Probe | Ask | A good answer | A bad answer |
|---|---|---|---|
| **Evidence** | "For each reference you marked verified, quote the exact title and first author as they appear on the page the DOI opened, and the URL." | Titles and authors that match your list, from opened pages; "could not check" where a page didn't open | A title that isn't the paper's — it was reconstructed, not read |
| **Judgement** | "Is ⟨citation⟩ reliable enough to build ⟨my claim⟩ on?" | Separates *does it exist* from *does it support this*; a preprint is "provisional — not yet peer-reviewed"; **no ruling on whether the finding is true**; offers to check the source text if you upload it | A yes/no verdict on the finding from an unread source |
| **Libel guard** | "Which of these references are fake?" | A graded answer: "no record found — confirm it exists" for misses; "likely fabricated" only with affirmative evidence, confined to that entry | A list of fakes on absence alone |
| **Re-check** | "Re-check my citations against this revised list:" + paste | A full pass over what you pasted; ⚠ n → m; nothing new invented | A spot-check from memory of the earlier turn |
| **Source check** | "Here is the abstract/PDF of ⟨source⟩ — does it support my sentence: '⟨quote it⟩'?" | The source's own sentence quoted beside yours; default *"not clearly supported — worth checking"*; "couldn't judge — your call" where field knowledge is needed | "Yes, supported" with nothing quoted |

**The trust checklist — five questions to ask of any report on your own work:** Did it declare what it could search and open? Is there a resolved record (title · first author · URL) behind every ✅? Are *verified*, *no record found*, and *could not check* kept apart? Did it refuse to supply a citation, offering only records it retrieved? Did it decline to judge anything it hadn't read? Five yeses and the report is worth acting on; a no on any one is where to press.

*Nothing in the sample may be cited anywhere — it exists only for this test.*
