#!/usr/bin/env python3
"""notice_scan.py — scan the PDFs you hold for publisher notices printed on the page.

Part of CLARK (claude-language-assessment-research-kit). Standard library only; uses
PyMuPDF automatically for a precise per-page scan when it happens to be installed
(never required).

Some publishers (SAGE among them) print correction, corrigendum, erratum, expression-of-
concern and retraction statements on the FIRST page of a re-issued article PDF (sometimes
the last); Wiley-style "[Correction added on <date> …]" and Springer-style "A Correction to
this article has been published" lines are covered too. Some of these notices never reach
Crossref, and sit on the publisher's page only inside a collapsed panel. This scan reads
page 1 and the last page of every PDF given (or every PDF under a folder) and reports each
match verbatim, with the file's creation date. Report-only: it never edits anything.

What a clean result means — and does not mean: it describes the COPY YOU HOLD. A file
downloaded before a re-issue carries no notice; an image-only page has no text to search;
a publisher whose phrasing is not in the pattern list is not covered. Pair a clean result
with the record's dates and — for load-bearing sources — with the publisher page.

Usage:
  python3 notice_scan.py <file.pdf | folder> [more ...] [--json] [--stdlib] [--selftest]
  --stdlib    force the standard-library engine: whole-file literal strings, no page
              attribution; text in CID/Identity-H encodings is unreadable and is reported
              as PARTIAL, never as clean
  --selftest  write two one-page PDFs carrying notice lines to a temporary folder and
              confirm the scan finds them (both engines when PyMuPDF is present)
Exit codes: 0 = no notice found · 2 = at least one notice found · 1 = usage error, nothing
scanned, a file that could not be read, or self-test failure
"""
import json
import os
import re
import sys
import tempfile
import zlib

MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|"
         r"Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
# Anchored on purpose: a bare "Correction:" matches "Grammatical Error Correction" and
# "post-ASR correction". These are the printed forms observed on publisher PDFs; the list
# is not exhaustive — a miss is not evidence of a clean record.
PATTERNS = [
    ("correction-dated", re.compile(r"Correction\s*\((?:\d{1,2}\s+)?(?:" + MONTH + r"\s+)?\d{4}\)", re.I)),
    ("correction-added", re.compile(r"\bCorrection added on\b", re.I)),
    ("correction-published", re.compile(r"\bA Correction to this (?:paper|article)\b", re.I)),
    ("published-with-errors", re.compile(r"\boriginally published with errors?\b", re.I)),
    ("corrigendum", re.compile(r"\bCorrigend(?:um|a)\b")),
    ("erratum", re.compile(r"\bErrat(?:um|a)\b")),
    ("expression-of-concern", re.compile(r"\bExpression of Concern\b", re.I)),
    ("retraction", re.compile(r"\bRETRACTED\b|\bRetracted Article\b|\bRetraction Note\b|\bRetraction:\s")),
    ("article-updated", re.compile(r"\bThis article has been (?:corrected|retracted|updated|withdrawn)\b", re.I)),
    ("withdrawn", re.compile(r"\bWITHDRAWN\b")),
]
CONTEXT = 90
VERDICT_EXIT = {"NOTICE": 2, "ERROR": 1, "NOT-PDF": 1}


def _matches(text):
    hits = []
    flat = re.sub(r"\s+", " ", text)
    for label, rx in PATTERNS:
        for m in rx.finditer(flat):
            a, b = max(0, m.start() - 12), min(len(flat), m.end() + CONTEXT)
            hits.append({"kind": label, "context": flat[a:b].strip()})
    return hits


def _pdf_date(raw):
    """'D:20250911170832+05'30'' -> '2025-09-11' (None if absent)."""
    if not raw:
        return None
    m = re.search(r"(\d{4})(\d{2})(\d{2})", raw)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def _result(verdict, engine, **kw):
    r = {"verdict": verdict, "engine": engine, "pages": None, "created": None, "hits": [], "note": None}
    r.update(kw)
    return r


# ---------- engine: PyMuPDF (page-precise) ----------

def scan_pymupdf(path):
    import fitz
    doc = fitz.open(path)
    if doc.needs_pass:
        return _result("ENCRYPTED", "pymupdf", note="needs a user password — cannot be read")
    n = len(doc)
    if n == 0:
        return _result("UNREADABLE", "pymupdf", pages=0, note="no pages")
    pages = [0] + ([n - 1] if n > 1 else [])
    hits, text_seen = [], False
    for p in pages:
        t = doc[p].get_text()
        text_seen = text_seen or bool(t.strip())
        for h in _matches(t):
            h["page"] = p + 1
            hits.append(h)
    created = _pdf_date(doc.metadata.get("creationDate", ""))
    if hits:
        return _result("NOTICE", "pymupdf", pages=n, created=created, hits=hits)
    if not text_seen:
        return _result("UNREADABLE", "pymupdf", pages=n, created=created,
                       note="no text layer on the scanned pages (image-only?) — nothing to search")
    return _result("CLEAN", "pymupdf", pages=n, created=created)


# ---------- engine: standard library (whole-file, literal strings) ----------

_ESC = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\"}


def _text_literals(chunk):
    """Linear scan of a content stream: returns the byte strings shown by `(…) Tj` and `[…] TJ`.

    Nested and escaped parentheses, octal escapes, and backslash line continuations follow the
    PDF spec; inside a TJ array fragments are joined directly, with a space only for a large
    negative kern (a word gap). Hex strings are ignored (they are CID text the stdlib path
    cannot decode anyway). No regex over the whole stream — never backtracks.
    """
    out, i, n = [], 0, len(chunk)
    array = None  # list of fragments while inside [ … ]

    def read_literal(j):
        depth, buf = 1, bytearray()
        j += 1
        while j < n and depth:
            ch = chunk[j:j + 1]
            if ch == b"\\":
                nxt = chunk[j + 1:j + 2]
                if nxt in (b"\r", b"\n"):
                    j += 2 + (1 if nxt == b"\r" and chunk[j + 2:j + 3] == b"\n" else 0)
                    continue
                if nxt and nxt in b"01234567":
                    digs = re.match(rb"[0-7]{1,3}", chunk[j + 1:j + 4]).group(0)
                    buf += bytes([int(digs, 8) & 0xFF])
                    j += 1 + len(digs)
                    continue
                buf += _ESC.get(nxt, nxt)
                j += 2
                continue
            if ch == b"(":
                depth += 1
            elif ch == b")":
                depth -= 1
                if depth == 0:
                    return bytes(buf), j + 1
            buf += ch
            j += 1
        return bytes(buf), j

    while i < n:
        ch = chunk[i:i + 1]
        if ch == b"(":
            lit, i = read_literal(i)
            m = re.match(rb"\s*(Tj|')", chunk[i:i + 8])
            if array is not None:
                array.append(lit)
            elif m:
                out.append(lit)
            continue
        if ch == b"[" and array is None:
            array, i = [], i + 1
            continue
        if ch == b"]" and array is not None:
            m = re.match(rb"\s*TJ", chunk[i + 1:i + 8])
            if m and array:
                out.append(b"".join(array))
            array, i = None, i + 1
            continue
        if array is not None and ch in b"-0123456789.":
            m = re.match(rb"-?\d+(?:\.\d+)?", chunk[i:i + 16])
            if m:
                try:
                    if float(m.group(0)) < -200:
                        array.append(b" ")
                except ValueError:
                    pass
                i += len(m.group(0))
                continue
        if ch == b"<" and chunk[i + 1:i + 2] != b"<":  # hex string: skip to '>'
            e = chunk.find(b">", i)
            i = n if e == -1 else e + 1
            continue
        i += 1
    return out


def scan_stdlib(path):
    data = open(path, "rb").read()
    if not data.startswith(b"%PDF"):
        return _result("NOT-PDF", "stdlib", note="missing %PDF header")
    if b"/Encrypt" in data:
        return _result("ENCRYPTED", "stdlib",
                       note="encrypted — often only an owner password, which PyMuPDF opens without asking; "
                            "the standard-library engine cannot")
    m = re.search(rb"/CreationDate\s*\(\s*(D:[^)]*)\)", data)
    created = _pdf_date(m.group(1).decode("latin-1")) if m else None
    chunks = [data]
    for s in re.finditer(rb"(?<!end)stream\r?\n", data):
        end = data.find(b"endstream", s.end())
        if end == -1:
            continue
        try:
            chunks.append(zlib.decompress(data[s.end():end]))
        except Exception:
            pass
    literals = []
    for c in chunks:
        literals.extend(_text_literals(c))
    text = b" ".join(literals).decode("latin-1", errors="replace")
    printable = sum(ch.isprintable() for ch in text)
    cid_like = len(text) > 40 and printable / len(text) < 0.6
    hits = _matches(text)
    if hits:
        return _result("NOTICE", "stdlib", created=created, hits=hits)
    # the stdlib engine can never certify a clean page 1 (whole-file, literal strings only): PARTIAL, never CLEAN
    return _result("PARTIAL", "stdlib", created=created,
                   note=("text appears CID/Identity-H encoded — unreadable without PyMuPDF" if cid_like else
                         "stdlib engine: whole-file literal strings, no page attribution — a miss here is not a clean page 1"))


# ---------- self-test ----------

def _tiny_pdf(line):
    """A valid one-page, uncompressed PDF (Helvetica) carrying `line` — readable by both engines."""
    esc = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = f"BT /F1 12 Tf 72 720 Td ({esc}) Tj ET".encode("latin-1")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Producer (notice_scan selftest) /CreationDate (D:20250911170832Z) >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R /Info 6 0 R >>\nstartxref\n{xref}\n%%EOF\n").encode()
    return bytes(out)


SELFTEST_LINES = [
    ("correction-dated", "Correction (September 2025): There are minor changes to data in the Methods section of this article."),
    ("correction-added", "[Correction added on 12 September 2025, after first online publication: the author list was amended.]"),
]


def selftest():
    tmp = tempfile.mkdtemp(prefix="notice_scan_selftest_")
    ok = True
    try:
        engines = [("stdlib", scan_stdlib)]
        try:
            import fitz  # noqa: F401
            engines.append(("pymupdf", scan_pymupdf))
        except ImportError:
            print("PyMuPDF not installed — testing the standard-library engine only")
        for kind, line in SELFTEST_LINES:
            path = os.path.join(tmp, f"{kind}.pdf")
            open(path, "wb").write(_tiny_pdf(line))
            for name, fn in engines:
                r = fn(path)
                found = r["verdict"] == "NOTICE" and any(h["kind"] == kind for h in r["hits"])
                print(f"[{'PASS' if found else 'FAIL'}] {name} · {kind}: verdict={r['verdict']} "
                      f"created={r['created']} hits={[h['kind'] for h in r['hits']]}")
                ok = ok and found
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)
    return ok


# ---------- CLI ----------

def collect(args):
    files = []
    for a in args:
        if os.path.isdir(a):
            for root, _, names in os.walk(a):
                files.extend(os.path.join(root, n) for n in sorted(names)
                             if n.lower().endswith(".pdf") and not n.startswith("."))
        else:
            files.append(a)
    return files


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json, force_stdlib = "--json" in sys.argv, "--stdlib" in sys.argv
    if not args:
        sys.exit(__doc__)
    engine = scan_stdlib
    if not force_stdlib:
        try:
            import fitz  # noqa: F401
            engine = scan_pymupdf
        except ImportError:
            pass
    files = collect(args)
    if not files:
        sys.exit("notice_scan: no PDF files found under " + ", ".join(args) + " — nothing scanned (exit 1, not a clean result)")
    results = []
    for path in files:
        try:
            with open(path, "rb") as f:
                magic = f.read(5)
            if not magic.startswith(b"%PDF"):
                r = _result("NOT-PDF", "none", note="missing %PDF header")
            else:
                r = engine(path)
        except Exception as e:
            r = _result("ERROR", engine.__name__.split("_")[-1], note=str(e)[:200])
        r["file"] = path
        results.append(r)
    worst = max((VERDICT_EXIT.get(r["verdict"], 0) for r in results), default=0)
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            extra = f" (engine: {r['engine']}" + (f", created {r['created']}" if r["created"] else "") + ")"
            print(f"[{r['verdict']}] {r['file']}{extra}")
            for h in r["hits"]:
                where = f"p.{h['page']}" if "page" in h else "page ?"
                print(f"    {where} [{h['kind']}]: “{h['context']}”")
            if r["note"]:
                print(f"    note: {r['note']}")
        counts = {}
        for r in results:
            counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
        print(f"\n{len(results)} file(s): " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        print("A CLEAN result describes the copy you hold — a file downloaded before a re-issue carries no notice, and "
              "phrasings outside the pattern list are not covered; pair it with the record's dates and, for "
              "load-bearing sources, the publisher page. Report-only.")
    sys.exit(worst)


if __name__ == "__main__":
    main()
