#!/usr/bin/env python3
"""matrix_to_vault.py — project a literature-review matrix into Obsidian-ready notes.

Part of CLARK (claude-language-assessment-research-kit). Standard library only — no installs.

Reads a review matrix (.xlsx or .csv) whose header row carries the core columns
(see review-conventions-template.md) and generates, under --notes-dir:
  Papers/<citekey>.md            one note per row that has a Cite key
  Themes/Theme — <entry>.md      one hub per controlled-vocabulary theme in use
  Themes/<hub>.md                one hub per matched hub-term (from conventions)

Safety model (mirrors the literature-review skill's charter):
  * The MATRIX is the source of truth; notes are a generated projection.
  * Every generated file carries a `generated-by: clas-literature-review` marker.
    A target file WITHOUT that marker is never overwritten — it is skipped and
    reported (user edits win).
  * Themes outside the controlled vocabulary are FLAGGED, never invented.
  * --dry-run prints the full report and writes nothing.

Usage:
  python3 matrix_to_vault.py <matrix.xlsx|.csv> --notes-dir <dir>
                             [--conventions review-conventions.md]
                             [--sheet <name>] [--dry-run]

Exit codes: 0 = clean · 2 = flags to review (unlisted themes / skipped files)
            1 = usage or read error.
"""
import argparse
import csv
import datetime
import io
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
# Historic marker string from the toolkit's original name (CLAS) — NEVER rename it:
# existing vaults' generated notes carry this exact string, and a mismatch would make
# regeneration skip them all as hand-edited.
MARKER = "generated-by: clas-literature-review"

# ---------- matrix readers ----------

def _col_index(ref):
    """'BC12' -> 0-based column index (54)."""
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _cell_text(c, shared):
    t = c.get("t")
    if t == "s":
        v = c.find(M + "v")
        return shared[int(v.text)] if v is not None else ""
    if t == "inlineStr":
        return "".join(e.text or "" for e in c.find(M + "is").iter(M + "t"))
    v = c.find(M + "v")
    if v is None or v.text is None:
        return ""
    txt = v.text
    if re.fullmatch(r"-?\d+\.0", txt):  # 104.0 -> 104
        txt = txt[:-2]
    return txt


def read_xlsx(path, sheet_name=None):
    with zipfile.ZipFile(path) as z:
        wb = ET.parse(io.BytesIO(z.read("xl/workbook.xml"))).getroot()
        rels = ET.parse(io.BytesIO(z.read("xl/_rels/workbook.xml.rels"))).getroot()
        rid_to_target = {rel.get("Id"): rel.get("Target") for rel in rels}
        sheets = [(s.get("name"), rid_to_target[s.get(R + "id")]) for s in wb.iter(M + "sheet")]
        if sheet_name:
            matches = [t for n, t in sheets if n.strip().lower() == sheet_name.strip().lower()]
            if not matches:
                sys.exit(f"error: sheet '{sheet_name}' not found; sheets: {[n for n, _ in sheets]}")
            target = matches[0]
        else:
            target = sheets[0][1]
        # rel targets appear as 'worksheets/sheet1.xml' (relative to xl/) or '/xl/worksheets/sheet1.xml' (absolute)
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            sst = ET.parse(io.BytesIO(z.read("xl/sharedStrings.xml"))).getroot()
            shared = ["".join(t.text or "" for t in si.iter(M + "t")) for si in sst.iter(M + "si")]
        ws = ET.parse(io.BytesIO(z.read(target))).getroot()
        rows = []
        for row in ws.iter(M + "row"):
            cells = {}
            for c in row.iter(M + "c"):
                cells[_col_index(c.get("r", "A1"))] = _cell_text(c, shared)
            width = max(cells) + 1 if cells else 0
            rows.append([cells.get(i, "") for i in range(width)])
        return rows


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [list(r) for r in csv.reader(f)]

# ---------- structure ----------

CANON = {  # canonical key -> header prefix (case-insensitive)
    "num": "#", "authors": "authors", "focus": "short focus", "folder": "folder",
    "theme": "theme", "primary": "primary use", "relevance": "relevance",
    "construct": "construct", "section": "manuscript", "read": "read",
    "keypoints": "key points", "flags": "flags", "citekey": "cite key",
    "studytype": "study type",  # optional column; skipped gracefully when absent
}


def find_header(rows):
    for i, row in enumerate(rows):
        cells = [str(c).strip().lower() for c in row]
        if cells and cells[0] == "#" and any(c.startswith("cite key") for c in cells):
            mapping = {}
            for key, prefix in CANON.items():
                for j, c in enumerate(cells):
                    if c == prefix or c.startswith(prefix):
                        mapping[key] = j
                        break
            missing = [k for k in ("citekey", "theme", "authors") if k not in mapping]
            if missing:
                sys.exit(f"error: header found (row {i+1}) but missing columns: {missing}")
            return i, mapping
    sys.exit("error: no header row found (need first cell '#' and a 'Cite key' column)")


def parse_conventions(path):
    themes, hubs = [], []
    if not path:
        return themes, hubs
    section = None
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        low = line.strip().lower()
        if low.startswith("## "):
            section = "themes" if "theme vocabulary" in low else "hubs" if "hub terms" in low else None
            continue
        item = line.strip()
        if not item.startswith("- ") or "⟨" in item:  # skip non-bullets and template placeholders
            continue
        item = item[2:].strip()
        if section == "themes" and item:
            # "Entry <= alias1, alias2" merges variants into one hub named Entry (all match by substring)
            if "<=" in item:
                name, aliases = item.split("<=", 1)
                themes.append((name.strip(), [name.strip()] + [x.strip() for x in aliases.split(",") if x.strip()]))
            else:
                themes.append((item, [item]))
        elif section == "hubs" and "=>" in item:
            term, hub = (p.strip() for p in item.split("=>", 1))
            if term and hub:
                hubs.append((term, hub))
    return themes, hubs

# ---------- generation ----------

def sanitize(s):
    return re.sub(r"[\\/:|#^\[\]{}]", "–", str(s).strip())[:80]


def parse_bib_status(bib_path):
    """citekey -> 'preprint' | 'published', derived from the bibliography the renderer already uses.
    Preprint = BibTeX entry type unpublished/misc/online/preprint, or an arXiv marker in the entry."""
    status = {}
    text = pathlib.Path(bib_path).read_text(encoding="utf-8", errors="replace")
    for chunk in re.split(r"\n(?=@)", text):
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)", chunk)
        if not m:
            continue
        etype, key = m.group(1).lower(), m.group(2).strip()
        preprint = etype in ("unpublished", "misc", "online", "preprint") or "arxiv" in chunk.lower()
        status[key] = "preprint" if preprint else "published"
    return status


def note_text(vals, theme_hub, hub_links, today, pub_status=None):
    key_paper = "★" in (vals["keypoints"] + vals["flags"])
    fm = [
        "---",
        f"{MARKER}",
        "tags: [paper]",
        f'theme: "{sanitize(vals["theme"])}"',
        f'relevance: "{sanitize(vals["relevance"])}"',
        f'read: "{sanitize(vals["read"])}"',
        f"key-paper: {str(key_paper).lower()}",
        f"matrix-row: {vals['num']}",
    ] + ([f'study-type: "{sanitize(vals["studytype"])}"'] if vals.get("studytype") else []) \
      + ([f'publication: "{pub_status}"'] if pub_status else []) + [
        "---",
    ]
    key = vals["citekey"]
    body = [
        f"# {vals['authors']} — {sanitize(vals['focus'])[:70]}",
        "",
        f"*Generated {today} from the review matrix (row {vals['num']}) — the matrix is the source of truth; "
        f"fix the matrix and regenerate rather than editing here (edits would make this file skip future syncs).*",
        "",
        f"**Read:** [Show in Zotero](zotero://select/items/@{key}) *(needs Zotero running + Better BibTeX; "
        f"the PDF is one click from there)*",
        "",
    ]
    if theme_hub:
        body.append(f"Theme: [[Theme — {sanitize(theme_hub)}]]")
    for hub in hub_links:
        body.append(f"Linked hub: [[{sanitize(hub)}]]")
    if vals["keypoints"]:
        body += ["", f"**Key points (matrix):** {vals['keypoints']}"]
    if vals["flags"]:
        body += ["", f"**Flags (matrix):** {vals['flags']}"]
    return "\n".join(fm + body) + "\n"


def write_guarded(path, content, dry, skipped):
    if path.exists() and MARKER not in path.read_text(encoding="utf-8", errors="replace"):
        skipped.append(str(path))
        return
    if not dry:
        path.write_text(content, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("matrix", help="review matrix (.xlsx or .csv)")
    ap.add_argument("--notes-dir", required=True, help="vault folder to generate into (gets Papers/ and Themes/)")
    ap.add_argument("--conventions", help="review-conventions.md (controlled vocabulary + hub terms)")
    ap.add_argument("--sheet", help="worksheet name (default: first sheet)")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    a = ap.parse_args()

    path = pathlib.Path(a.matrix)
    if not path.exists():
        sys.exit(f"error: {path} not found")
    rows = read_csv(path) if path.suffix.lower() == ".csv" else read_xlsx(path, a.sheet)
    h, col = find_header(rows)
    vocab, hub_terms = parse_conventions(a.conventions)
    bib_status = {}
    if a.conventions:
        conv_text = pathlib.Path(a.conventions).read_text(encoding="utf-8")
        mbib = re.search(r"^- bibliography:\s*(.+?)\s*(?:#.*)?$", conv_text, re.M)
        if mbib:
            bib_path = (pathlib.Path(a.conventions).parent / mbib.group(1).strip()).resolve()
            if bib_path.exists():
                bib_status = parse_bib_status(bib_path)

    notes_dir = pathlib.Path(a.notes_dir)
    papers, themes_dir = notes_dir / "Papers", notes_dir / "Themes"
    if not a.dry_run:
        papers.mkdir(parents=True, exist_ok=True)
        themes_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    made, no_key, unlisted, skipped = 0, 0, {}, []
    theme_use, hub_use = {}, {}
    tier_counts, read_counts, key_rows, care_rows, preprint_keys, studytype_counts = {}, {}, [], [], [], {}

    for idx, row in enumerate(rows[h + 1:], h + 2):
        get = lambda k: str(row[col[k]]).strip() if k in col and col[k] < len(row) and row[col[k]] is not None else ""
        vals = {k: get(k) for k in CANON}
        if not vals["citekey"]:
            if any(vals.values()):
                no_key += 1
            continue
        theme = vals["theme"]
        theme_hub = None
        if vocab:
            for entry, matchers in vocab:
                if any(m.lower() == theme.lower() or m.lower() in theme.lower() for m in matchers):
                    theme_hub = entry
                    break
            if theme_hub is None and theme:
                unlisted.setdefault(theme, []).append(vals["citekey"])
        elif theme:  # no controlled vocabulary: mechanical first-segment fallback
            theme_hub = sanitize(re.split(r"[+(/·]", theme)[0])
        if theme_hub:
            theme_use.setdefault(theme_hub, []).append((vals["citekey"], vals["authors"]))
        tier_counts[vals["relevance"] or "(blank)"] = tier_counts.get(vals["relevance"] or "(blank)", 0) + 1
        read_counts[vals["read"] or "(blank)"] = read_counts.get(vals["read"] or "(blank)", 0) + 1
        if "★" in (vals["keypoints"] + vals["flags"]):
            key_rows.append((vals["citekey"], vals["authors"]))
        if "cite with care" in vals["flags"].lower():
            care_rows.append((vals["citekey"], sanitize(vals["flags"])[:90]))
        if bib_status.get(vals["citekey"]) == "preprint":
            preprint_keys.append(vals["citekey"])
        if vals.get("studytype"):
            base = vals["studytype"].split("(")[0].strip()  # count by controlled prefix; subtype stays on the note
            studytype_counts[base] = studytype_counts.get(base, 0) + 1
        haystack = " ".join(vals[k] for k in ("theme", "focus", "keypoints", "flags"))
        # word-boundary matching: bare substrings would false-match (GUI in 'linguistic', API in 'rapid')
        links = list(dict.fromkeys(
            hub for term, hub in hub_terms
            if re.search(rf"(?<![A-Za-z]){re.escape(term)}s?(?![A-Za-z])", haystack, re.I)))  # s? keeps plurals (APIs, correlations)
        for hub in links:
            hub_use.setdefault(hub, []).append((vals["citekey"], vals["authors"]))
        write_guarded(papers / f"{vals['citekey']}.md",
                      note_text(vals, theme_hub, links, today, bib_status.get(vals["citekey"])), a.dry_run, skipped)
        made += 1

    def hub_note(kind, blurb, members):
        lines = ["---", MARKER, f"tags: [{kind}]", "---", blurb, "", f"## Papers ({len(members)})"]
        lines += [f"- [[{k}]] — {au}" for k, au in members]
        return "\n".join(lines) + "\n"

    for hub, members in sorted(theme_use.items()):
        write_guarded(themes_dir / f"Theme — {sanitize(hub)}.md",
                      hub_note("theme-hub", f"#theme-hub — generated {today}; the vocabulary lives in review-conventions.md.", members),
                      a.dry_run, skipped)
    for hub, members in sorted(hub_use.items()):
        prefix = hub.split(" — ")[0].strip().lower().replace(" ", "-")  # quantitative / qualitative / ai-tool / interface …
        hub_tag = {"quantitative": "quant-method-hub", "qualitative": "qual-method-hub",
                   "method": "method-hub", "methods": "method-family-hub", "ai-tool": "tool-hub",
                   "tool": "tool-hub", "interface": "interface-hub"}.get(prefix, "hub")
        write_guarded(themes_dir / f"{sanitize(hub)}.md",
                      hub_note(hub_tag, f"#{hub_tag} — text-match over the matrix's own wording; terms live in "
                               f"review-conventions.md. Generated {today}.", members),
                      a.dry_run, skipped)

    # ---- Review Dashboard: the reporting surface (regenerated every run) ----
    def table(d):
        return ["| | Papers |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(d.items(), key=lambda x: -x[1])]
    dash = [
        "---", MARKER, "tags: [review-dashboard]", "---",
        "# Review Dashboard", "",
        f"*Generated {today} from the review matrix — the standing answer to \"what does this review hold?\". "
        f"Regenerates with every projection; edit the matrix, not this note.*", "",
        "## Corpus",
        f"- Papers projected (rows with a Cite key): **{made}**",
        f"- Rows without a Cite key (not projected — fill column M in the matrix): {no_key}",
        f"- Themes outside the controlled vocabulary: {len(unlisted)}"
        + ("" if not unlisted else " — " + "; ".join(f"'{t}' ({', '.join(k)})" for t, k in sorted(unlisted.items()))),
        "",
        "## Relevance tiers", *table(tier_counts), "",
        "## Read status", *table(read_counts), "",
        *((["## Study types", *table(studytype_counts), ""]) if studytype_counts else []),
        f"## ★ KEY papers ({len(key_rows)})",
        *[f"- [[{k}]] — {a}" for k, a in key_rows], "",
        f"## Cite-with-care register ({len(care_rows)})",
        *[f"- [[{k}]] — {f}" for k, f in care_rows], "",
        "## Themes (controlled vocabulary)",
        *table({f"[[Theme — {sanitize(h)}]]": len(m) for h, m in theme_use.items()}), "",
        "## Methods & tools (hub terms)",
        *table({f"[[{sanitize(h)}]]": len(m) for h, m in hub_use.items()}), "",
    ]
    if bib_status:
        dash += [f"## Preprints in the corpus ({len(preprint_keys)}) — verify version-of-record at write-up",
                 "*Derived automatically from the bibliography's entry types (arXiv/unpublished/misc) — "
                 "the integrity charter asks preprints to be cited as such, or upgraded if since published.*",
                 *[f"- [[{k}]]" for k in preprint_keys], ""]
    write_guarded(notes_dir / "Review Dashboard.md", "\n".join(dash) + "\n", a.dry_run, skipped)

    mode = "DRY-RUN (nothing written)" if a.dry_run else "written"
    print(f"[{mode}] paper notes: {made}   rows without citekey: {no_key}   + Review Dashboard.md")
    print(f"theme hubs: {len(theme_use)}" + ("" if vocab else "   ⚠ no controlled vocabulary — mechanical first-segment grouping; add a Theme vocabulary to review-conventions.md to control this"))
    for hub, m in sorted(theme_use.items(), key=lambda x: -len(x[1])):
        print(f"   {len(m):3d}  Theme — {hub}")
    for hub, m in sorted(hub_use.items(), key=lambda x: -len(x[1])):
        print(f"   {len(m):3d}  {hub}")
    if unlisted:
        print(f"⚠ UNLISTED themes ({len(unlisted)}) — not in the controlled vocabulary; add to review-conventions.md or fix the matrix (never auto-added):")
        for t, keys in sorted(unlisted.items()):
            print(f"   · '{t}' — {len(keys)} paper(s): {', '.join(keys[:6])}{'…' if len(keys) > 6 else ''}")
    if skipped:
        print(f"⚠ SKIPPED {len(skipped)} file(s) without the generated-by marker (hand-edited — user edits win):")
        for s in skipped:
            print(f"   · {s}")
    sys.exit(2 if (unlisted or skipped) else 0)


if __name__ == "__main__":
    main()
