# Starter kit — copy this folder into your project

Everything needed to render a Markdown draft into Word with automatic citations and a matched reference list.

| File | What it is |
|---|---|
| `render.sh` / `render.bat` | The one-command renderer (Mac/Linux · Windows) |
| `check_retractions.py` | Retraction check for your whole library — every DOI queried against Crossref + the Retraction Watch database (integrity rule 14): `python3 check_retractions.py library.bib` |
| `notice_scan.py` | First-page / last-page scan of the PDFs you hold for printed publisher notices — correction · corrigendum · erratum · expression of concern · retraction — the ones that never reach Crossref: `python3 notice_scan.py Literature/` (folder or files; `--selftest` proves the scan on your machine). A clean result describes the copy you hold, not the record |
| `pdf_probe.py` | "Can this PDF be read, and how?" — TEXT-RICH / TEXT-SPARSE / IMAGE-ONLY / ENCRYPTED verdict and the pages to read as images: `python3 pdf_probe.py paper.pdf` |
| `resolve_check.py` | Resolve + consistency check (integrity rules 1–3): every DOI *resolves* to a real Crossref record **and** its title/year/author *match* your entry — catches dead DOIs and mis-attached / "Frankenstein" references; proposes DOIs for DOI-less entries (verify, never auto-applied): `python3 resolve_check.py library.bib` |
| `review_audit.py` | Second-model audit of a literature-review matrix — a different vendor's model re-judges every row against your own conventions and files a propose-only report: `python3 review_audit.py matrix.xlsx --conventions review-conventions.md --dry-run` (needs your own API key) |
| `manuscript_audit.py` | Second-rater audit of a pre-submission review — sends the manuscript plus the review's findings to a second model for concur/dispute verdicts and an independent score. Refuses to transmit without `--confirm-send` |
| `llm_api.py` | Not run directly — the single request/response implementation both audit scripts share, so their wire format cannot drift apart. Speaks two formats, pinned as `- api:` in the conventions' `## Audit` block: `chat` (the default, `/chat/completions`) and `responses` (OpenAI's newer `/responses`, always with `store: false`). `python3 llm_api.py --selftest` checks the parser, both request shapes and the endpoint builder against saved samples without calling anything |
| `clark_doctor.py` | "Is my kit complete and are my tools installed?" — checks every starter-kit file is present and reports on Pandoc and the optional PyMuPDF: `python3 clark_doctor.py` |
| `style.csl` | The citation style — ships as **APA 7th**; swap for any style from [zotero.org/styles](https://www.zotero.org/styles) |
| `library.bib` | **Sample** bibliography (3 real entries) — replace with your own Zotero auto-export |
| `sample-draft.md` | A tiny demo manuscript citing the 3 samples |

## Try it (2 minutes)
*Working with Claude Code? Just say **"render the sample draft"** — it installs anything missing and runs this for you. The by-hand version:*

Needs one free program — **Pandoc** (`pandoc --version` in a terminal confirms it's installed; if not, [troubleshooting](../docs/03-troubleshooting.md) has the one-line install per operating system).

Open a terminal **in this folder**, then run:
```bash
bash render.sh sample-draft.md      # Mac / Linux
.\render.bat sample-draft.md        # Windows
```
*(How to open a terminal here — **Mac:** right-click this folder in Finder → Services → New Terminal at Folder. **Windows:** open the folder in File Explorer, click the address bar, type `cmd`, press Enter.)*

Open `sample-draft.docx` → formatted citations + a reference list. That's the whole trick.

## Make it yours
1. **Replace `library.bib`** with your own: in Zotero (with Better BibTeX installed — see [docs/01-zotero-setup.md](../docs/01-zotero-setup.md)), right-click your library → *Export Library…* → format **Better BibTeX** → tick ☑ **Keep updated** → save **over this file**. It then updates itself.
2. **Cite by key** in your draft: `[@yourkey]` (keys are in Zotero's right-hand pane).
3. **Render**, and read any warnings — `(key?)` means a citekey didn't match the library.
