#!/usr/bin/env python3
"""pdf_probe.py — deterministic "can this PDF be read, and how?" check.

Part of CLARK (claude-language-assessment-research-kit). Standard library only; uses
PyMuPDF automatically for a more precise per-page report when it happens to be
installed (never required).

Run this BEFORE reading any PDF. It answers, mechanically, what the skills'
"reading basis" declaration needs: does the file have a usable text layer, is
it a scan (image-only), which pages are figure/table-heavy and must be read as
rendered page images, is it encrypted or broken. The probe's verdict routes the
reading:

  TEXT-RICH   → prose from the text layer; render the flagged 2-D pages (tables,
                figures) as images and read those visually.
  TEXT-SPARSE → text layer exists but is thin; read visually page-by-page,
                using the text layer only as a search index.
  IMAGE-ONLY  → a scan: no OCR tool needed — read the rendered page images
                visually (that IS the OCR), and say so in the reading basis.
  ENCRYPTED / NOT-PDF / ERROR → flag; do not guess at contents.

Usage:
  python3 pdf_probe.py <file.pdf> [more.pdf ...] [--json]
Exit codes: 0 = readable via text layer · 2 = visual-read or flag required for
at least one file · 1 = usage error.
"""
import json
import re
import sys
import zlib


def probe_stdlib(path):
    """Byte-level heuristic probe: no dependencies, works on most PDFs."""
    data = open(path, "rb").read()
    if not data.startswith(b"%PDF"):
        return {"verdict": "NOT-PDF", "detail": "missing %PDF header"}
    if b"/Encrypt" in data[:4096] or b"/Encrypt" in data[-4096:]:
        return {"verdict": "ENCRYPTED", "detail": "/Encrypt found in trailer region"}
    pages = max(len(re.findall(rb"/Type\s*/Page[^s]", data)), 1)
    images = len(re.findall(rb"/Subtype\s*/Image", data))
    # count text-showing operators in raw + FlateDecode-decompressed streams
    text_ops = len(re.findall(rb"\bTj\b|\bTJ\b", data))
    decompress_failures = 0
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end == -1:
            continue
        try:
            chunk = zlib.decompress(data[start:end])
            text_ops += len(re.findall(rb"\bTj\b|\bTJ\b", chunk))
        except Exception:
            decompress_failures += 1
    ops_per_page = text_ops / pages
    if text_ops == 0 and images > 0:
        verdict = "IMAGE-ONLY"
    elif ops_per_page < 20:
        verdict = "TEXT-SPARSE"
    else:
        verdict = "TEXT-RICH"
    return {"verdict": verdict, "engine": "stdlib-heuristic", "pages~": pages,
            "text_ops": text_ops, "images": images,
            "note": ("heuristic only — page/word figures are approximate; "
                     f"{decompress_failures} stream(s) undecodable" if decompress_failures else
                     "heuristic only — page/word figures are approximate")}


def probe_pymupdf(path):
    import fitz  # noqa: F401  (import checked by caller)
    import fitz as _f
    doc = _f.open(path)
    if doc.needs_pass:
        return {"verdict": "ENCRYPTED", "engine": "pymupdf", "pages": len(doc)}
    per_page = []
    for i, page in enumerate(doc):
        words = len(page.get_text().split())
        images = len(page.get_images())
        per_page.append((i + 1, words, images))
    total_words = sum(w for _, w, _ in per_page)
    wpp = total_words / max(len(doc), 1)
    visual_pages = [n for n, w, im in per_page if w < 60 or im > 0]
    if total_words < 40 * len(doc) and any(im for _, _, im in per_page) and wpp < 20:
        verdict = "IMAGE-ONLY"
    elif wpp < 80:
        verdict = "TEXT-SPARSE"
    else:
        verdict = "TEXT-RICH"
    return {"verdict": verdict, "engine": "pymupdf", "pages": len(doc),
            "total_words": total_words, "words_per_page": round(wpp),
            "visual_read_pages": visual_pages,
            "note": "visual_read_pages = low-text or image-carrying pages: render and read these as images"}


ROUTE = {
    "TEXT-RICH": "text layer for prose; RENDER the listed 2-D/figure pages and read them visually",
    "TEXT-SPARSE": "thin text layer: read rendered pages visually; use the text layer only as a search index",
    "IMAGE-ONLY": "scan: read rendered page images visually (no OCR tool needed); declare 'scan — read visually' as the basis",
    "ENCRYPTED": "flag to the user; do not guess at contents",
    "NOT-PDF": "flag to the user; not a readable PDF",
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        sys.exit(__doc__)
    try:
        import fitz  # noqa: F401
        engine = probe_pymupdf
    except ImportError:
        engine = probe_stdlib
    worst = 0
    results = []
    for path in args:
        try:
            r = engine(path)
        except Exception as e:
            r = {"verdict": "ERROR", "detail": str(e)[:200]}
        r["file"] = path
        r["route"] = ROUTE.get(r["verdict"], "flag to the user")
        results.append(r)
        if r["verdict"] != "TEXT-RICH":
            worst = 2
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r['verdict']}] {r['file']}")
            for k, v in r.items():
                if k not in ("verdict", "file"):
                    print(f"    {k}: {v}")
    sys.exit(worst)


if __name__ == "__main__":
    main()
