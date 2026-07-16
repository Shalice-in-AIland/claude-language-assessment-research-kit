# Daily workflow — the whole thing in four moves

*(Setup done? If not: [01-zotero-setup.md](01-zotero-setup.md).)*

## 1 · Add a paper
Drag its PDF into Zotero → details auto-fill → **glance at the year and DOI** (fix gaps now, not at proof stage). The paper's **Citation Key** (right-hand pane) is its permanent ID.

## 2 · Cite by ID in your draft
Your draft is a plain-text (Markdown) file. Cite like this:

| You type | Renders as (APA 7th) — try these with the starter-kit sample library |
|---|---|
| `[@swales1990]` | (Swales, 1990) |
| `@hyland2005 describes…` | Hyland (2005) describes… |
| `[@hyland2005; @swales1990]` | (Hyland, 2005; Swales, 1990) |
| `[@andrich1978, p. 561]` | (Andrich, 1978, p. 561) |

End the draft with a `# References` heading — the list builds itself there.

## 3 · Render
**Just say _"render my draft"_** — Claude runs it and reads the warnings for you. A `.docx` appears next to your draft: citations formatted, reference list matched and alphabetised — containing **only** works you actually cited. *(Running the workflow entirely by hand instead? The command is in the [starter-kit README](../starter-kit/README.md).)*

## 4 · Read the warnings (the free safety net)
A typo'd or missing key renders as **`(key?)`** in the document **and** prints a WARNING naming the key. That's a *feature*: every unmatched citation surfaces at every render, not at proof stage. Fix the key (or add the paper to Zotero) and re-render.

Real output (we typo'd `swales1990` → `swales199` and re-rendered):
```
$ bash render.sh sample-draft.md
[WARNING] Citeproc: citation swales199 not found
rendered -> sample-draft.docx
```
…and in the Word document the citation appears as: `…an ordered set of communicative moves (swales199?).` — impossible to miss.

---

## The 5-minute live demo (for showing colleagues)
1. Drag a PDF into Zotero → point at the auto-filled details and the citekey. *(30 s)*
2. Open the sample draft → show the `[@key]` citations in plain text. *(30 s)*
3. Run the render → open the Word file → formatted citations + reference list. *(2 min)*
4. **Break it on purpose:** change one citekey to a typo, re-render → show `(key?)` + the warning. "The system catches what we'd miss." *(1 min)*
5. Swap `style.csl` for another journal's style file, re-render → same draft, new journal's format. *(1 min)*

## Claude Code — the built-in operator
This workflow ships with Claude Code as its operator (`skills/zotero-citations/SKILL.md`): in daily use, steps 3–4 become simply *"render my draft"* — Claude runs the render, reads every warning, and explains any orphan in plain language. On request it also audits the library (missing years/DOIs, duplicates, stale exports) and runs the pre-submission integrity pass (every citation traced to a real record; text ↔ list reconciled both ways) — **flagging what it can't verify instead of guessing**. What to read, what to cite, and what a source says stay human decisions. *(This page doubles as the reference manual — every step also works by hand exactly as written.)*
