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
  python3 matrix_to_vault.py --selftest
  --selftest  build a tiny workbook, bibliography and conventions file in a temporary folder —
              with an empty text cell saved without content and a '- bibliography:' line with
              prose after the path — and confirm they read and project correctly

The conventions' optional '- bibliography:' line names the project's .bib (relative to the
conventions file); when prose follows, put the path first, in backticks. A bibliography that
cannot be found, checked or read is reported (⚠ — preprint register skipped); it never stops the run.

Exit codes: 0 = clean · 2 = flags to review (unlisted themes / skipped files / an unusable bibliography line)
            1 = usage or read error, or self-test failure.
"""
import argparse
import contextlib
import csv
import datetime
import io
import os
import pathlib
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from xml.sax.saxutils import escape

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
        return shared[int(v.text)] if v is not None and v.text and v.text.strip() else ""
    if t == "inlineStr":
        # some spreadsheet writers save an empty text cell as <c t="inlineStr"></c> — no <is> at all
        inline = c.find(M + "is")
        if inline is None:  # a stray <v> in such a cell is kept, never silently dropped
            v = c.find(M + "v")
            return (v.text or "") if v is not None else ""
        return "".join(e.text or "" for e in inline.iter(M + "t"))
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
    "recordstate": "record_state", "lastverified": "last_verified",  # optional (radar Mode C); skipped when absent
}


def find_header(rows):
    for i, row in enumerate(rows):
        cells = [str(c).strip().lower() for c in row]
        if cells and cells[0] == "#" and any(c.startswith("cite key") for c in cells):
            mapping = {}
            for key, prefix in CANON.items():
                for j, c in enumerate(cells):
                    if c == prefix or c.startswith(prefix) or c.replace(" ", "_").startswith(prefix):
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


def bibliography_from_conventions(path):
    """The conventions' '- bibliography:' line -> (bib path, None), or (None, warning or None).

    Only lines starting '- bibliography:' count, as always; one holding only a template
    ⟨placeholder⟩ is skipped. The value may carry prose around the path — - bibliography:
    `library.bib` (the live export; …) — or sit on the next non-blank line when the bullet line is
    empty (not a list item or heading), and then only when that line opens with the path. A '#' outside backticks starts a comment and template
    ⟨notes⟩ are dropped. The path is then the whole text when that names an existing file (the
    bare form that always worked, spaces allowed); else the first token when it ends in .bib or
    names a file (a backticked or double-quoted span is one token); else the line's only .bib token — several
    different ones are flagged, never guessed between; else the first token when it is
    backticked or the only one. It is read relative to the conventions file. A path the
    filesystem refuses to check (e.g. too long) is a warning, never a crash.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8")
    for m in re.finditer(r"^- bibliography:[ \t]*(.*)(?:\n(?:[^\S\n]*\n)*[^\S\n]*(?![-*+]\s|#|\d+[.)]\s)(\S.*))?",
                         text, re.M):
        value = m.group(1) if m.group(1).strip() else (m.group(2) or "")
        head = re.sub(r"(`[^`]*`)|#.*", lambda x: x.group(1) or "", value)
        head = re.sub(r"⟨[^⟩]*⟩|⟨.*", "", head).strip()
        if head or "⟨" not in value:
            from_next = not m.group(1).strip()
            break
    else:
        return None, None
    base = pathlib.Path(path).parent
    hint = "put the path first, in backticks, e.g. - bibliography: `library.bib` (prose may follow it)"

    def is_file(name):
        try:
            return (base / name).is_file()
        except (OSError, ValueError):
            return False

    tokens = []  # (delimited by backticks or double quotes, text, where the text ends in head)
    for t in re.finditer(r"`([^`]*)`|\"([^\"]*)\"|“([^”]*)”|([^\s`]+)", head):
        span = next((g for g in t.groups()[:3] if g is not None), None)
        if span is not None:
            tokens.append((True, span.strip(), t.end()))
        else:
            word = t.group(4).lstrip("\"'“‘([<*")
            lead = len(t.group(4)) - len(word)
            word = word.rstrip("\"'”’)]>,;:.!?*")
            tokens.append((False, word, t.start(4) + lead + len(word)))
    tokens = [tok for tok in tokens if tok[1]]
    bibs = [tok for tok in tokens if tok[1].lower().endswith(".bib")]
    opens_with_path = ("`" not in head and is_file(head)) or bool(
        tokens and (tokens[0][0] or tokens[0] in bibs or is_file(tokens[0][1])))
    first = value.strip()[:1]
    if from_next and not (opens_with_path and (first.isalnum() or first in "`\"“./~\\_")):
        # a comment, quote, table row or prose line is never read as the path
        where = "line is empty" + (" and the next line does not open with a path" if head else "")
        return None, f"{where} — preprint register skipped; {hint}"
    if "`" not in head and is_file(head):
        ticked, name = False, head
    elif tokens and (tokens[0] in bibs or is_file(tokens[0][1])):
        ticked, name, _ = tokens[0]
    elif len({tok[1] for tok in bibs}) > 1:
        named = ", ".join(dict.fromkeys(tok[1] for tok in bibs))
        return None, f"line names several .bib files ({named}) — preprint register skipped; {hint}"
    elif bibs:
        ticked, name, end = bibs[0]
        if not ticked and is_file(head[:end]):  # a bare path with spaces, prose after it
            name = head[:end]
    elif tokens and (tokens[0][0] or len(tokens) == 1):
        ticked, name, _ = tokens[0]
    else:
        return None, f"line names no .bib file — preprint register skipped; {hint}"
    bib = base / name
    shown = name if len(name) <= 80 else name[:77] + "…"
    tip = f"; {hint}" if not ticked and len(tokens) > 1 else ""
    try:
        if bib.is_file():
            return bib, None
        problem = (f"not a file: {os.path.abspath(bib)}" if bib.exists() else
                   f"not found: {os.path.abspath(bib)} (read relative to the conventions file)")
    except (OSError, ValueError) as e:
        problem = f"path could not be checked ({getattr(e, 'strerror', None) or e}): '{shown}'"
    return None, f"{problem} — preprint register skipped{tip}"

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
      + ([f'publication: "{pub_status}"'] if pub_status else []) \
      + ([f'record-state: "{sanitize(vals["recordstate"])}"'] if vals.get("recordstate") else []) \
      + ([f'last-verified: "{sanitize(vals["lastverified"])}"'] if vals.get("lastverified") else []) + [
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

# ---------- self-test ----------

def _tiny_xlsx(path, rows, shared):
    """A minimal valid .xlsx: one sheet 'Matrix' holding `rows` (lists of <c> XML) + a shared-string table."""
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg_rels = "http://schemas.openxmlformats.org/package/2006/relationships"
    ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml"
    parts = {
        "[Content_Types].xml":
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            f'<Override PartName="/xl/workbook.xml" ContentType="{ctype}.sheet.main+xml"/>'
            f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="{ctype}.worksheet+xml"/>'
            f'<Override PartName="/xl/sharedStrings.xml" ContentType="{ctype}.sharedStrings+xml"/></Types>',
        "_rels/.rels":
            f'<Relationships xmlns="{pkg_rels}">'
            f'<Relationship Id="rId1" Type="{rel_ns}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml":
            f'<workbook xmlns="{main_ns}" xmlns:r="{rel_ns}">'
            '<sheets><sheet name="Matrix" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels":
            f'<Relationships xmlns="{pkg_rels}">'
            f'<Relationship Id="rId1" Type="{rel_ns}/worksheet" Target="/xl/worksheets/sheet1.xml"/>'
            f'<Relationship Id="rId2" Type="{rel_ns}/sharedStrings" Target="sharedStrings.xml"/></Relationships>',
        "xl/sharedStrings.xml":
            f'<sst xmlns="{main_ns}" count="{len(shared)}" uniqueCount="{len(shared)}">'
            + "".join(f"<si><t>{escape(s)}</t></si>" for s in shared) + "</sst>",
        "xl/worksheets/sheet1.xml":
            f'<worksheet xmlns="{main_ns}"><sheetData>'
            + "".join(f'<row r="{i}">{"".join(cells)}</row>' for i, cells in enumerate(rows, 1))
            + "</sheetData></worksheet>",
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, xml in parts.items():
            z.writestr(name, '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml)


def selftest():
    def s(ref, text):  # an inline-string cell, the way the matrices in the wild store text
        return f'<c r="{ref}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'

    header = ["#", "Authors (Year)", "Short focus", "Theme", "Relevance", "Manuscript section",
              "Key points / notes", "Flags", "Cite key"]
    rows = [
        [s(f"{chr(65 + i)}1", h) for i, h in enumerate(header)],
        ['<c r="A2" t="n"><v>1</v></c>', s("B2", "Alpha & Beta (2024)"), s("C2", "rater agreement"),
         s("D2", "Theme One"), s("E2", "High"), '<c r="F2" t="inlineStr"></c>',  # empty, no <is>: the crash
         s("G2", "★ KEY — anchors the design"), s("I2", "alpha2024")],
        ['<c r="A3" t="n"><v>2</v></c>', s("B3", "Gamma (2025)"), s("C3", "a preprint"), s("D3", "Theme One"),
         s("E3", "Medium"), '<c r="F3" t="inlineStr"/>', s("I3", "gamma2025")],
        ['<c r="A4" t="n"><v>3</v></c>', s("B4", "Delta (2023)"), '<c r="C4" t="inlineStr"><v>kept</v></c>',
         s("D4", "Theme One"), s("E4", "Low"),
         '<c r="F4" t="s"/>', '<c r="G4" t="s"><v></v></c>',  # shared-string cells with no value
         '<c r="I4" t="s"><v>0</v></c>'],
    ]
    expected = [header,
                ["1", "Alpha & Beta (2024)", "rater agreement", "Theme One", "High", "",
                 "★ KEY — anchors the design", "", "alpha2024"],
                ["2", "Gamma (2025)", "a preprint", "Theme One", "Medium", "", "", "", "gamma2025"],
                ["3", "Delta (2023)", "kept", "Theme One", "Low", "", "", "", "delta2023"]]
    prose = "the reference manager's automatic export, refreshed on every change and never edited by hand; " * 4
    b = "- bibliography: "
    cases = [  # (case, the conventions lines holding the bibliography, file it must resolve to, warning expected)
        ("backticked path + prose (too long to be a file name)", f"{b}`library.bib` (kept beside this file; {prose})",
         "library.bib", False),
        ("bare path + '# comment', the form that always worked", f"{b}library.bib  # live export, not `field.bib`",
         "library.bib", False),
        ("bare path + prose", f"{b}library.bib (kept beside this file; the live export)", "library.bib", False),
        ("bare path first, prose naming another existing .bib", f"{b}library.bib (the live export, not `field.bib`)",
         "library.bib", False),
        ("two different .bib files, neither first: flagged, not guessed", f"{b}the `field.bib` snapshot, not `library.bib`",
         None, True),
        ("template notes, one left unclosed", f"{b}`library.bib` ⟨relative to this file  # ⟨note⟩", "library.bib", False),
        ("an earlier nested bullet naming another existing .bib", f"  - bibliography: was `field.bib`\n{b}library.bib",
         "library.bib", False),
        ("path after a blank line, unindented", "- bibliography:\n\nlibrary.bib", "library.bib", False),
        ("path too long to check", f"{b}{'x' * 300}.bib", None, True),
        ("file not found", f"{b}`nowhere.bib` (moved?)", None, True),
        ("empty value", "- bibliography:", None, True),
        ("empty line, next line a comment naming an existing .bib: warned, not picked",
         "- bibliography:\n<!-- TODO: point at field.bib -->", None, True),
        ("empty line, next line a table row naming an existing .bib", "- bibliography:\n| field.bib | snapshot |", None, True),
        ("empty line, next line a quote naming an existing .bib", "- bibliography:\n> field.bib", None, True),
        ("double-quoted path with a space, prose after it", f'{b}"My Refs/library.bib" (the live export)',
         "library.bib", False),
        ("template placeholder", f"{b}⟨path to the project's `library.bib`⟩", None, False),
        ("template placeholder, closing bracket lost", f"{b}⟨path to the project's `library.bib`", None, False),
    ]

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="matrix_to_vault_selftest_"))
    results = []

    def check(label, fn):
        try:
            ok, detail = fn()
        except Exception as e:  # a crash is a failure, reported like one
            ok, detail = False, f"{type(e).__name__}: {e}"
        print(f"[{'PASS' if ok else 'FAIL'}] {label}: {detail}")
        results.append(ok)

    def run(argv, encoding=None):  # main() in-process; encoding= stands in for a legacy console code page
        out = io.TextIOWrapper(io.BytesIO(), encoding=encoding) if encoding else io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out):
                main([str(a) for a in argv])
        except SystemExit as e:
            code = e.code
        out.flush()
        return code, out.buffer.getvalue().decode(encoding) if encoding else out.getvalue()

    def conventions(name, lines):
        p = tmp / name
        p.write_text("# Review conventions — self-test\n\n## Theme vocabulary\n- Theme One\n\n## Matrix\n"
                     "- field bibliography: `field.bib` (a snapshot — never read as the bibliography)\n"
                     f"{lines}\n", encoding="utf-8")
        return p

    try:
        xlsx = tmp / "matrix.xlsx"
        _tiny_xlsx(xlsx, rows, ["delta2023"])
        (tmp / "library.bib").write_text(
            "@article{alpha2024,\n  title = {Alpha},\n  year = {2024}\n}\n\n"
            "@misc{gamma2025,\n  title = {Gamma},\n  eprint = {2501.00001},\n  archiveprefix = {arXiv},\n}\n\n"
            "@article{delta2023,\n  title = {Delta},\n  year = {2023}\n}\n", encoding="utf-8")
        (tmp / "field.bib").write_text("@misc{gamma2025,\n  title = {Gamma}\n}\n", encoding="utf-8")
        (tmp / "My Refs").mkdir()
        shutil.copy(tmp / "library.bib", tmp / "My Refs" / "library.bib")

        def read_back():
            got = read_xlsx(xlsx)
            return got == expected, "empty inline-string and value-less shared-string cells read as blank; a stray value kept" \
                if got == expected else f"read {got}"
        check("xlsx reader", read_back)

        for i, (case, lines, want, warn_expected) in enumerate(cases):
            def resolve(lines=lines, want=want, warn_expected=warn_expected, i=i):
                bib, warning = bibliography_from_conventions(conventions(f"conventions-{i}.md", lines))
                ok = (bib.name if bib else None) == want and bool(warning) == warn_expected
                return ok, (f"resolves to {bib.name}" if bib else "no bibliography") + (f"; warns: {warning}" if warning else "")
            check(f"bibliography line · {case}", resolve)

        vault = tmp / "vault"
        argv = [xlsx, "--notes-dir", vault, "--conventions", tmp / "conventions-0.md", "--sheet", "Matrix"]

        def dry_run():
            code, out = run(argv + ["--dry-run"])
            return code == 0 and "paper notes: 3" in out and not vault.exists(), \
                f"exit {code}, {'WROTE FILES' if vault.exists() else 'nothing written'}"
        check("projection · dry run", dry_run)

        def projection():
            code, out = run(argv)
            papers = vault / "Papers"
            gamma = (papers / "gamma2025.md").read_text(encoding="utf-8")
            alpha = (papers / "alpha2024.md").read_text(encoding="utf-8")
            dash = (vault / "Review Dashboard.md").read_text(encoding="utf-8")
            ok = (code == 0 and "⚠" not in out and len(list(papers.glob("*.md"))) == 3
                  and 'publication: "preprint"' in gamma and 'publication: "published"' in alpha
                  and "key-paper: true" in alpha and "## Preprints in the corpus (1)" in dash)
            return ok, f"exit {code}, 3 notes, preprint register built from the prose bibliography line" \
                if ok else f"exit {code}; report: {out.strip()[:300]}"
        check("projection · written", projection)

        def unusable_bibliography():
            code, out = run([xlsx, "--notes-dir", vault, "--conventions", conventions("unusable.md", f"{b}{'x' * 300}.bib"),
                             "--dry-run"], encoding="cp1252")
            ok = code == 2 and "BIBLIOGRAPHY" in out
            return ok, "exit 2 (a flag to review), warned and carried on, even on a console that cannot print the warning sign" \
                if ok else f"exit {code}; report: {out.strip()[:300]}"
        check("projection · unusable bibliography path", unusable_bibliography)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return all(results)


def main(argv=None):
    if getattr(sys.stdout, "errors", None) in ("strict", "surrogateescape") and hasattr(sys.stdout, "reconfigure"):
        try:
            "⚠—".encode(sys.stdout.encoding or "utf-8")
        except (UnicodeEncodeError, LookupError):  # a legacy console code page: print '?', never crash the report
            sys.stdout.reconfigure(errors="replace")
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("matrix", help="review matrix (.xlsx or .csv)")
    ap.add_argument("--notes-dir", required=True, help="vault folder to generate into (gets Papers/ and Themes/)")
    ap.add_argument("--conventions", help="review-conventions.md (controlled vocabulary + hub terms)")
    ap.add_argument("--sheet", help="worksheet name (default: first sheet)")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    a = ap.parse_args(argv)

    path = pathlib.Path(a.matrix)
    if not path.exists():
        sys.exit(f"error: {path} not found")
    rows = read_csv(path) if path.suffix.lower() == ".csv" else read_xlsx(path, a.sheet)
    h, col = find_header(rows)
    vocab, hub_terms = parse_conventions(a.conventions)
    bib_status, bib_warning = {}, None
    if a.conventions:
        bib_path, bib_warning = bibliography_from_conventions(a.conventions)
        if bib_path:
            try:
                bib_status = parse_bib_status(bib_path)
                if not bib_status:
                    bib_warning = f"no BibTeX entries read from {bib_path} — preprint register skipped"
            except OSError as e:
                bib_warning = f"could not be read ({e.strerror or e}): {bib_path} — preprint register skipped"

    notes_dir = pathlib.Path(a.notes_dir)
    papers, themes_dir = notes_dir / "Papers", notes_dir / "Themes"
    if not a.dry_run:
        papers.mkdir(parents=True, exist_ok=True)
        themes_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    made, no_key, unlisted, skipped = 0, 0, {}, []
    theme_use, hub_use = {}, {}
    tier_counts, read_counts, key_rows, care_rows, preprint_keys, studytype_counts = {}, {}, [], [], [], {}
    state_rows = []  # rows whose record_state is set and not 'normal' (radar Mode C)

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
        rs = (vals.get("recordstate") or "").strip()
        if rs and rs.lower() != "normal":
            state_rows.append((vals["citekey"], rs, (vals.get("lastverified") or "").strip()))
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
        *(([f"## Record state — rows not in state normal ({len(state_rows)}) — corrected · retracted · VoR-updated (radar Mode C)",
           *[f"- [[{k}]] — {s}" + (f" — last verified {d}" if d else "") for k, s, d in state_rows], ""]) if state_rows else []),
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
    if bib_warning:
        print(f"⚠ BIBLIOGRAPHY {bib_warning}")
    if unlisted:
        print(f"⚠ UNLISTED themes ({len(unlisted)}) — not in the controlled vocabulary; add to review-conventions.md or fix the matrix (never auto-added):")
        for t, keys in sorted(unlisted.items()):
            print(f"   · '{t}' — {len(keys)} paper(s): {', '.join(keys[:6])}{'…' if len(keys) > 6 else ''}")
    if skipped:
        print(f"⚠ SKIPPED {len(skipped)} file(s) without the generated-by marker (hand-edited — user edits win):")
        for s in skipped:
            print(f"   · {s}")
    sys.exit(2 if (unlisted or skipped or bib_warning) else 0)


if __name__ == "__main__":
    main()
