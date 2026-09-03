# Citation integrity — the standalone pack

**The one check every manuscript deserves, in two portable forms.** CLARK's citation-integrity skill is the toolkit's most-requested feature — so here it is, extractable: no repo download, no setup, no Claude Code required.

| File | For | How to use |
|---|---|---|
| [`citation-integrity-portable.md`](citation-integrity-portable.md) | **Any researcher, any AI assistant** | Paste (or attach) the file into your AI chat — Claude, or another assistant — together with your reference list and draft, and say *"check my citations."* Self-contained instructions; the AI verifies by web search and reports action-first. |
| [`citation-checklist-for-students.md`](citation-checklist-for-students.md) | **Research students and their supervisors — no AI required** | A one-page practice checklist: the habits that prevent citation problems and the checks to run before submission, written for humans. Print it, share it, put it in your programme handbook. |
| [`self-check-sample.md`](self-check-sample.md) + [`self-check-answer-key.md`](self-check-answer-key.md) + [`self-check-protocol.md`](self-check-protocol.md) | **Anyone — a practice run before you trust it** | Before you trust the check with your own manuscript, watch it work on a sample whose answers you already know: a deliberately flawed passage + reference list, an answer key, and a protocol — a practice run that shows what *your* tool can and can't verify, comparable across tools — plus the same follow-up probes templated for your own draft. Nothing in the sample may be cited. |

## Quick start (any AI chat — ChatGPT, Claude, Kimi, Gemini…)

1. **Open a new chat**, ideally in a tool with web search / browsing enabled (that's what verifies DOIs and retractions).
2. **Give it the instructions**: paste the full text of [`citation-integrity-portable.md`](citation-integrity-portable.md) as your first message (paste, don't attach — some tools silently ignore attached files).
3. **Give it your materials** as your second message: paste your **reference list** (a `.bib` file's contents, or the list copied as text) and, ideally, the **draft** that cites it.
4. **Say** (copy-paste):

   > Follow the citation-integrity instructions above: check the citations in my draft against my reference list.

**You should see:** a verdict banner — ✅ CLEAR or ⚠ FLAGS TO RESOLVE (with any 🚫 blockers named first) — followed by a checkbox fix list, each item with its fix and the evidence beneath it. Apply the fixes in your reference manager (never let the chat "fix" your list for you), then say **"re-check my citations"** (pasting the revised list) and watch the flags count down to CLEAR.

**Then press it.** The follow-up probes in [`self-check-protocol.md`](self-check-protocol.md) (Part B) work on any draft — they make the tool show the record behind every ✅ and keep "couldn't find it" apart from "fake." The everyday prompt above is all a real run needs: the instructions carry the rigour; the protocol's longer test prompt adds only harness lines (check in order, list what you checked, follow the format) so runs are comparable.

*Two honest notes: if your tool has no web search, the instructions tell it to park unverifiable items under "your call" rather than pretend — verification quality follows the tool's search ability — and its tier: free tiers may not open pages or read PDFs, paid tiers with browsing and file reading verify more; either way the instructions make the tool degrade honestly ("could not check") rather than pretend. And no AI chat can check what it isn't given: the pass covers the list and draft you provide.*

**What the checks catch** — from the obvious to the subtle: dead or fabricated DOIs · a real DOI attached to the *wrong* work · retracted papers cited as live findings · citations copied from another paper's summary rather than the source · a source cited for a concept it never actually develops · numbers or methods credited to a source that reports them differently · missing years, orphaned citations, quotes without page numbers.

*The portable edition is kept in sync with the in-repo [`citation-integrity` skill](../../skills/citation-integrity/SKILL.md): when the skill's checks evolve, this file evolves in the same commit.*

**The standing rule, in both files:** an AI may *format and check* a citation — it may never *supply* one. Every fix is proposed; the researcher decides.

**The full version:** the in-repo [`citation-integrity` skill](../../skills/citation-integrity/SKILL.md) adds scripted, deterministic checks (every DOI queried against Crossref, retraction sweep, preprint→version-of-record), rendering, and live Zotero — under the complete [16-rule integrity charter](../../docs/04-citation-integrity.md). These portable editions follow the same rules; the charter remains the single source.

*Part of [CLARK — the Claude Language Assessment Research Kit](https://github.com/Shalice-in-AIland/claude-language-assessment-research-kit) · MIT · cite: DOI [10.5281/zenodo.21411273](https://doi.org/10.5281/zenodo.21411273)*
