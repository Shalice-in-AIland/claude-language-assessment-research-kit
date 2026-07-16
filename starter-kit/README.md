# Starter kit — copy this folder into your project

Everything needed to render a Markdown draft into Word with automatic citations and a matched reference list.

| File | What it is |
|---|---|
| `render.sh` / `render.bat` | The one-command renderer (Mac/Linux · Windows) |
| `check_retractions.py` | Retraction check for your whole library — every DOI queried against Crossref + the Retraction Watch database (integrity rule 14): `python3 check_retractions.py library.bib` |
| `resolve_check.py` | Resolve + consistency check (integrity rules 1–3): every DOI *resolves* to a real Crossref record **and** its title/year/author *match* your entry — catches dead DOIs and mis-attached / "Frankenstein" references; proposes DOIs for DOI-less entries (verify, never auto-applied): `python3 resolve_check.py library.bib` |
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
