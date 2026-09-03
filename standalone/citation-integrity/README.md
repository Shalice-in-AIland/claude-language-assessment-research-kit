# Citation integrity — the standalone pack

**The one check every manuscript deserves, in portable form.** CLARK's citation-integrity skill is the toolkit's most-requested feature — so here it is, extractable: no repo download, no setup, no Claude Code required.

| File | For | How to use |
|---|---|---|
| [`citation-integrity-portable.md`](citation-integrity-portable.md) | **Any researcher, any AI assistant** | Paste the file's full text into your AI chat as your first message (paste, don't attach) — Claude, or another assistant — then your reference list and draft, and say *"check my citations."* Self-contained instructions; the AI verifies by web search and reports action-first. |
| [`citation-checklist-for-students.md`](citation-checklist-for-students.md) (+ printable [`.docx`](citation-checklist-for-students.docx)) | **Research students and their supervisors — no AI required** | A one-page practice checklist: the habits that prevent citation problems and the checks to run before submission, written for humans. Print it, share it, put it in your programme handbook. |
| [`self-check-sample.md`](self-check-sample.md) + [`self-check-answer-key.md`](self-check-answer-key.md) + [`self-check-protocol.md`](self-check-protocol.md) | **Anyone — a practice run before you trust it** | Before you trust the check with your own manuscript, watch it work on a sample whose answers you already know: a deliberately flawed passage + reference list, an answer key, and a protocol — a practice run that shows what *your* tool can and can't verify, comparable across tools — plus the same follow-up probes templated for your own draft. Nothing in the sample may be cited. |

## Quick start (any AI chat — ChatGPT, Claude, Kimi, Gemini…)

1. **Open a new chat**, ideally in a tool with web search / browsing enabled (that's what verifies DOIs and retractions).
2. **Give it the instructions**: paste the full text of [`citation-integrity-portable.md`](citation-integrity-portable.md) as your first message (paste, don't attach — some tools silently ignore attached files).
3. **Second message — your materials and the ask together**: paste your **reference list** (a `.bib` file's contents, or the list copied as text) and, ideally, the **draft** that cites it, ending with (copy-paste):

   > Follow the citation-integrity instructions above: check the citations in my draft against my reference list.

   No draft? End with: *"Follow the citation-integrity instructions above: check my reference list."*

**You should see:** first a one-line statement of what the tool could do (search the web; open the records — read that line first, it tells you how much weight the rest can bear), then a verdict banner — ✅ CLEAR or ⚠ FLAGS TO RESOLVE (with any 🚫 blockers named first) — followed by a checkbox fix list, each item with its fix and the evidence beneath it. Apply the fixes in your reference manager (never let the chat "fix" your list for you), then say **"re-check my citations"** (pasting the revised list) and watch the flags count down to CLEAR.

**Then press it.** The follow-up probes in [`self-check-protocol.md`](self-check-protocol.md) (Part B) work on any draft — they make the tool show the record behind every ✅ and keep "couldn't find it" apart from "fake." The everyday prompt above is all a real run needs: the instructions carry the rigour; the protocol's longer test prompt adds only harness lines (check in order, list what you checked, follow the format) so runs are comparable.

*Two honest notes. First, verification quality follows your tool's abilities and tier: a free tier may search but not open pages or read PDFs; a paid tier with browsing and file reading verifies more. Either way the instructions make the tool say "could not check" rather than pretend — and if it has no web search at all, unverifiable items are parked under "your call." Second, no AI chat can check what it isn't given: the pass covers the list and draft you provide.*

**What the checks catch** — from the obvious to the subtle: dead DOIs (reported as *"no record found — confirm this reference exists"* — never "fabricated" on absence alone) · a real DOI attached to the *wrong* work · retracted papers cited as live findings · citations copied from another paper's summary rather than the source · a source cited for a concept it never actually develops · numbers or methods credited to a source that reports them differently · missing years, orphaned citations, quotes without page numbers.

*The portable edition is kept in sync with the in-repo [`citation-integrity` skill](../../skills/citation-integrity/SKILL.md): when the skill's checks evolve, this file evolves in the same commit.*

**The standing rule, in both files:** an AI may *format and check* a citation — it may never *supply* one. Every fix is proposed; the researcher decides.

**The full version:** the in-repo [`citation-integrity` skill](../../skills/citation-integrity/SKILL.md) adds scripted, deterministic checks (every DOI resolved against Crossref, then DataCite and OpenAlex before any dead-DOI verdict, retraction sweep, preprint→version-of-record), rendering, and live Zotero — under the complete [16-rule integrity charter](../../docs/04-citation-integrity.md). These portable editions follow the same rules; the charter remains the single source.

*Part of [CLARK — the Claude Language Assessment Research Kit](https://github.com/Shalice-in-AIland/claude-language-assessment-research-kit) · MIT · cite: DOI [10.5281/zenodo.21411273](https://doi.org/10.5281/zenodo.21411273)*
