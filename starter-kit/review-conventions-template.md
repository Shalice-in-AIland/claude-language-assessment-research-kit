# Review conventions — ⟨project name⟩

*This file is the rulebook for THIS project's literature review. The `literature-review` skill reads it before every triage and every vault regeneration — edit it here, and Claude follows. Copy it into your project as `review-conventions.md` and replace every ⟨placeholder⟩. Keep it short: every line is an instruction.*

## Scope
**IN** — a paper belongs if it bears on at least one of:
- ⟨your phenomenon, e.g. "peer feedback in L2 writing"⟩
- ⟨your construct or genre, e.g. "spoken fluency measures"⟩
- ⟨your methods family, e.g. "rater-agreement designs"⟩

**OUT** — recommend skipping: ⟨e.g. "opinion pieces with no evidence; adjacent-field work with no assessment angle"⟩. Excluded papers are moved to a folder, never deleted.

## Relevance tiers (matrix "Relevance" column)
- **High** — directly models the design, construct, or comparison this review builds on.
- **Medium-High** — strong overlap on method, construct, or population, one step removed.
- **Medium** — relevant context.
- **Low-Medium / Low** — tangential or foundational background.

## KEY papers
Reserve `★ KEY` (prefix in Key points) for papers that directly shape the design or argument. Keep the set small and load-bearing — don't inflate it.

## Quality checklist — "keep but flag" (never an exclusion gate)
Score each ✓ / ✗ / unclear at triage; weak items go verbatim into the Flags column as `cite with care (…)`:
1. Reliability of the key measures reported?
2. Robustness — replication, multiple runs, or sensitivity checks?
3. Enough procedural detail to reproduce?
4. Reference standard / ground truth defensible?
5. Sample and context adequate for the claims?
6. Analysis/metric appropriate to the question?

## Theme vocabulary (controlled — the anti-sprawl rule)
The matrix's Theme column and the vault's theme hubs use ONLY these entries (aim for ≤ ~10; grow it deliberately, one approved entry at a time). **Order matters: most-specific first** — the generator assigns each paper to the FIRST entry that matches its Theme text:
- ⟨Theme 1, e.g. "human–AI comparison"⟩
- ⟨Theme 2, e.g. "construct definition"⟩
- ⟨Theme 3, e.g. "methods"⟩

## Hub terms (optional — method/tool cross-links in the vault)
Term (word-boundary matched, plural-tolerant, in the matrix's own wording) ⇒ hub note it links to. Method hubs use **family-as-prefix naming** — `⟨Family⟩ — ⟨specific⟩` — so each hub names the exact method while a graph Group searching the family word shows the whole family together (mixed-methods papers link into both families). Namespaces: `⟨Family⟩ — ⟨method⟩`, `AI tool — ⟨model⟩`, `Interface — API/GUI`:
- ⟨MFRM⟩ => ⟨Quantitative — MFRM⟩
- ⟨QWK⟩ => ⟨Quantitative — QWK⟩
- ⟨interview⟩ => ⟨Qualitative — interviews⟩
- ⟨ChatGPT⟩ => ⟨AI tool — ChatGPT⟩
- ⟨API⟩ => ⟨Interface — API⟩

## Study types (optional matrix column — controlled, 3 values; subtype in parentheses, e.g. `Synthesis (meta-analysis)`)
- **Empirical** — reports a primary study: new data collected and analysed by the authors.
- **Synthesis** — aggregates OTHER studies as its data: systematic/scoping/narrative reviews, meta-analyses, structured research agendas.
- **Foundational** — the works a review stands on rather than reviews: theory, books/textbooks, mechanism/position pieces. Test: *"would I cite this for its argument or framework rather than its results?"*
Publication status (preprint/published) is NOT a study type — it derives automatically from the bibliography (see `- bibliography:` above).

## Matrix
- File: ⟨path, e.g. `Literature Review Matrix.xlsx`⟩ (first sheet, or name it here: ⟨sheet⟩)
- bibliography: ⟨path to the project's `library.bib`, relative to this file — enables the automatic preprint register: entry types (arXiv/unpublished/misc) mark each note `publication: preprint|published`, and the dashboard lists preprints to re-verify at write-up⟩
- Core columns, in order: `# · Authors (Year) · Short focus · Folder · Theme · Primary use · Relevance · Construct link · Manuscript section · Read? · Key points / notes · Flags · Cite key`

## Vault projection (optional — delete this section if the project doesn't use Obsidian)
- Notes folder: ⟨e.g. `Notes` — the generator creates `Papers/` and `Themes/` inside it⟩
- Regenerate with: *ask Claude to "update my literature notes"* (it dry-runs first and shows you the report before writing).

## Radar (optional — the standing watch for new papers; delete if unused)
- Cadence: ⟨e.g. 1st and 15th of the month⟩ · Window: ⟨e.g. since the last digest / ~3 weeks⟩
- Venues to scan: ⟨journal list for your field⟩ · Preprint servers: ⟨e.g. arXiv cs.CL, PsyArXiv⟩
- Digest file: ⟨e.g. `RADAR_INBOX.md` — dated sections, newest on top, "Needs your attention" shortlist first⟩
- Dedup against: the matrix (Authors + Cite key), the PDF folder, prior digests, live Zotero.
- Rules: open-access fetching only · precision over recall ("nothing new" is a valid result) · discovery + pre-screen only — inclusions go through triage approval.

## Audit (highly recommended before submission milestones — needs your own API key; delete if unused)
*A different vendor's model re-judges every row against THIS file's rules and files a propose-only report. Pin the exact model here (reproducibility — verify current model IDs and prices the day you set this up; names retire: e.g. DeepSeek's `deepseek-reasoner` alias is scheduled to retire 2026-07-24).*
- model: ⟨e.g. deepseek-v4-pro⟩
- base-url: ⟨e.g. https://api.deepseek.com/v1 — any OpenAI-compatible endpoint⟩
- key-env: ⟨name of the environment variable holding YOUR API key, e.g. OPENAI_API_KEY — set it in your own shell; never paste the key into chat or files⟩
- effort: low  ⟨for reasoning models (GPT-5/o-series): they reject `temperature`; low is the validated census setting — factual findings are effort-stable, and a stricter cheap auditor surfaces more for the human gate⟩
- temperature: 0  ⟨used only for non-reasoning models; ignored when `effort` is set⟩
- prompt-version: v1
- price-in: ⟨USD per 1M input tokens, from the provider's pricing page — enables spend reporting⟩
- price-out: ⟨USD per 1M output tokens⟩
- manuscript-model: ⟨optional, e.g. gpt-5.6-sol — frontier-tier override used only by manuscript_audit.py⟩
- manuscript-effort: high  ⟨optional override for manuscript audits⟩

*Task-tiering doctrine: match the model tier to the stakes, not the habit. Volume row-audits (this file's `model:`) run on a budget reasoning tier — measured better at low effort, and a stricter cheap auditor just surfaces more for your gate. A whole-manuscript audit is ONE high-stakes judgment call: pin a frontier-tier model (`manuscript-model:`) where correctness matters more than cost — a full audit still measures in cents. Hard disputes from the cheap tier can be escalated row-by-row to the frontier tier (`review_audit.py --citekeys …`). And the ceiling is fixed: better tiers give better fact-checks and sharper questions, but interpretation calls (tiers, KEY, construct readings) end with you, not with any model.*

*Prompting note: the audit prompts shipped with CLARK follow the structural advice both major vendors publish for their current models (unambiguous, contradiction-free instructions; XML-tagged payload sections; long documents before the query; verbatim-quote grounding). If you re-point the audit at a new model family, skim that vendor's current prompting guide before trusting a pilot — and any prompt change bumps the `prompt-version` you pin here.*

*Model radar (recommended — packaged as the `model-radar` skill): models and their guides move faster than review projects. Once a month — or ask Claude to set up a scheduled task that does it for you — re-check three things: (1) the vendors' current prompting guides for material changes, (2) new frontier releases relevant to the tiering above, and (3) that every model ID pinned here still exists and isn't scheduled for retirement (aliases die: that is how this practice started). Log findings propose-only; a dead or retiring pin is the highest-priority finding.*
