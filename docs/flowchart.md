# CLAS — how the toolkit fits together

Six skills stationed along one research lifecycle: **you keep every judgement call, Claude operates the machinery, and nothing is written without your yes.** (Built on Zotero + Better BibTeX + Pandoc + Claude Code; style = APA 7th or any journal's.)

**Legend:** 👤 you — judgement · 🤖 Claude — drafts, checks, audits, never invents · ⚙️ automatic — tools · ⚠️ built-in check

## The research lifecycle — where each skill works

```mermaid
flowchart LR
    A["<b>1 · DISCOVER</b><br/>literature-radar<br/>🤖 scheduled sweeps, strict dedup<br/>👤 you approve keepers"]
    B["<b>2 · REVIEW</b><br/>literature-review<br/>🤖 drafts triage + Obsidian views<br/>👤 you rule tier & ★KEY"]
    C["<b>3 · WRITE</b><br/>zotero-citations · writing-polish<br/>👤 you write & accept proposals<br/>⚙️ render to Word"]
    D["<b>4 · CHECK</b><br/>citation-integrity<br/>⚠️ DOI resolve+match · retractions · preprint→VoR<br/>👤 you fix in Zotero"]
    E["<b>5 · EVALUATE</b><br/>pre-submission-review<br/>🤖 evidence ledger, recomputed numbers<br/>👤 you adjudicate the triage"]
    F["<b>6 · SUBMIT</b><br/>venue checklist +<br/>your AI-use declaration 👤"]
    A --> B --> C --> D --> E --> F
    F -. "revision rounds: resolution audit · sync check · re-score" .-> E
```

*Every station also works alone — check citations without a matrix, review a draft without a radar, polish a paragraph any time. The lifecycle is the map, not a required march.*

## The citation pipeline underneath (set up once — it feeds every stage)

```mermaid
flowchart LR
    Z["<b>1 · COLLECT</b><br/>drop the PDF into Zotero<br/>👤 you pick · ⚙️ metadata auto-fills"]
    K["<b>2 · KEY</b><br/>Better BibTeX mints a citekey<br/>e.g. cheng2026 — pin it<br/>⚙️ automatic"]
    X["<b>3 · EXPORT</b><br/>'Keep updated' writes library.bib<br/>straight into the project<br/>⚙️ automatic"]
    W["<b>4 · WRITE</b><br/>cite by ID in plain text:<br/>[@cheng2026]<br/>👤 you choose the paper"]
    R["<b>5 · RENDER</b><br/>one command → Word<br/>citations + matched reference list<br/>⚙️ Pandoc + style file"]
    Q["<b>6 · CHECK</b><br/>unknown keys print as (key?)<br/>⚠️ orphans can't hide"]
    Z --> K --> X --> W --> R --> Q
```

## Claude Code — the built-in operator

Claude runs the toolkit with you — bookkeeping and vigilance, never invention (docs 00–08 = the manual Claude follows; every step is inspectable):

- **Set-up:** installs and wires the tools per project (no-admin setups included), copies the starter-kit, verifies the sample render — then walks you through the few Zotero clicks it can't do for you.
- **Discovery & review:** radar sweeps, dedup, drafted triage rows and generated vault views — every judgement call queued for your approval, never written silently.
- **Render & report:** runs the renders, reads every warning, explains orphans in plain language.
- **Verification:** DOI resolve-and-match, retractions, preprint→version-of-record; manuscript evidence ledgers with recomputed statistics and page anchors; then a fresh agent re-checks the review itself before you see it.
- **Second opinions (optional — your key, your call, per run):** a different vendor's model re-judges review rows or the whole manuscript evaluation, propose-only; pinned models are re-verified on a schedule so a retired ID never silently breaks an audit.

## The standing rules

| | |
|---|---|
| **Judgement stays human** | What to read, cite, tier, and claim is yours; approval gates sit before every write, and interpretation questions are routed to you, never settled by a model. |
| **Flag, never guess** | Nothing is invented, "remembered", or silently corrected — the 16-rule integrity charter ([docs/04](04-citation-integrity.md)) is the single source, and fixes are proposals you apply in Zotero. |
| **Errors surface, they don't lurk** | `(key?)` warnings at every render; PASS/FAIL ledgers on every checkable number; dashboards that count what changed. |
| **One reading is never trusted alone** | Fresh-agent verification comes standard; optional cross-vendor audits show you the spread between two independent reads. |

---

*Prefer a designed, printable one-pager? [flowchart.html](flowchart.html) is the same picture with full styling — GitHub shows HTML as code, so open it after downloading the ZIP (just double-click the file). Companion: docs/00–08 + the starter-kit/ folder. Last verified July 2026.*
