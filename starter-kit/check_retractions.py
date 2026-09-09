#!/usr/bin/env python3
"""check_retractions.py — automated retraction check for a BibTeX library (integrity rule 14).

For every DOI in the .bib, queries the Crossref REST API (which incorporates the human-verified
Retraction Watch database, acquired by Crossref in 2023) for any notice that UPDATES that DOI:
retractions, withdrawals, expressions of concern, and corrections — but only those the publisher
DEPOSITED in Crossref. A correction that exists only on the publisher's article page (sometimes
inside a collapsed panel) or printed on the PDF's first page is invisible here: a clean result is
"index-checked", never "clean" — pair it with notice_scan.py over the PDFs you hold and, for
load-bearing sources, the publisher page. Entries without a DOI are listed as unverifiable-by-DOI
(check them by hand: books/chapters often have none).

Usage:  python3 check_retractions.py [path/to/library.bib] [--mailto you@example.org] [--only key1,key2]
Free, no key needed; the mailto goes in the User-Agent per Crossref's "polite pool" etiquette.
Exit code: 0 = index-checked, none found; 2 = at least one serious notice found (so CI or a skill can gate
on it); 1 = nothing was checked or some lookups failed (never read a 1 as clean).
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

SERIOUS = {"retraction", "partial_retraction", "withdrawal", "removal", "expression_of_concern"}


def parse_bib(path):
    txt = open(path, encoding="utf-8").read()
    entries = []
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)(?=\n@|\Z)", txt, re.DOTALL):
        key, body = m.group(1).strip(), m.group(2)
        doi = re.search(r"\bdoi\s*=\s*[{\"]([^}\"]+)[}\"]", body, re.IGNORECASE)
        title = re.search(r"\btitle\s*=\s*\{(.{0,80})", body, re.IGNORECASE)
        entries.append({"key": key,
                        "doi": doi.group(1).strip() if doi else None,
                        "title": re.sub(r"[{}]", "", title.group(1)).strip() if title else ""})
    return entries


def check_doi(doi, mailto):
    url = ("https://api.crossref.org/works?filter=updates:"
           + urllib.parse.quote(doi, safe="") + "&rows=10")
    req = urllib.request.Request(url, headers={
        "User-Agent": f"check-retractions/1.0 (mailto:{mailto})"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    notices = []
    for item in data.get("message", {}).get("items", []):
        for upd in item.get("update-to", []):
            if upd.get("DOI", "").lower() == doi.lower():
                notices.append({"type": upd.get("type", "unknown"),
                                "notice_doi": item.get("DOI", ""),
                                "date": (upd.get("updated", {}) or {}).get("date-parts", [[None]])[0]})
    return notices


def main():
    argv = sys.argv[1:]
    mailto, only, positional = "example@example.org", None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--mailto", "--only") or a.startswith(("--mailto=", "--only=")):
            if "=" in a:
                flag, val = a.split("=", 1)
            else:
                flag, i = a, i + 1
                val = argv[i] if i < len(argv) else ""
            if not val or val.startswith("--"):
                sys.exit(f"usage: {flag} needs a value\n\n" + __doc__)
            if flag == "--mailto":
                if "@" not in val:
                    sys.exit(f"usage: --mailto expects an email address, got {val!r}")
                mailto = val
            else:
                only = {k.strip() for k in val.split(",") if k.strip()}
        elif a.startswith("--"):
            sys.exit(f"usage: unknown option {a}\n\n" + __doc__)
        else:
            positional.append(a)
        i += 1
    bib = positional[0] if positional else os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.bib")
    entries = parse_bib(bib)
    if only:
        total = len(entries)
        entries = [e for e in entries if e["key"] in only]
        print(f"restricted to {len(entries)} of {total} entries (--only)")
        missing = only - {e["key"] for e in entries}
        if missing:
            print("  keys not in the library: " + ", ".join(sorted(missing)))
        if not entries:
            sys.exit("no entry matched --only — nothing checked (exit 1, not a clean result)")
    with_doi = [e for e in entries if e["doi"]]
    no_doi = [e for e in entries if not e["doi"]]
    print(f"library: {bib}\nentries: {len(entries)}  with DOI: {len(with_doi)}  without DOI: {len(no_doi)}\n")

    flagged, corrections, failed = [], [], []
    for i, e in enumerate(with_doi, 1):
        try:
            notices = check_doi(e["doi"], mailto)
        except Exception as ex:
            failed.append((e, str(ex)[:60]))
            continue
        for n in notices:
            (flagged if n["type"] in SERIOUS else corrections).append((e, n))
        print(f"\r  checked {i}/{len(with_doi)}", end="", flush=True)
        time.sleep(0.15)   # polite pacing
    print("\n")

    if flagged:
        print("⚠⚠ SERIOUS NOTICES (retraction / withdrawal / expression of concern):")
        for e, n in flagged:
            print(f"  ⚠ {e['key']}  [{n['type']}]  notice DOI: https://doi.org/{n['notice_doi']}\n     {e['title']}")
    elif not with_doi:
        print("○ no DOI-bearing entries — nothing was checked against Crossref.")
    elif failed:
        print(f"✗ {len(failed)} of {len(with_doi)} lookups failed — the library is NOT index-checked; re-run when online.")
    else:
        print("✓ Crossref lists no retraction, withdrawal, or expression of concern for any DOI-bearing entry"
              " (index-checked, not clean: a notice that exists only on the publisher's page or the PDF's first"
              " page is invisible here — run notice_scan.py over the PDFs you hold).")
    if corrections:
        print(f"\nℹ corrections/errata on {len(corrections)} entr{'y' if len(corrections)==1 else 'ies'} (usually fine — check the notice):")
        for e, n in corrections:
            print(f"  ℹ {e['key']}  [{n['type']}]  https://doi.org/{n['notice_doi']}")
    if no_doi:
        print(f"\n○ unverifiable by DOI ({len(no_doi)}): " + ", ".join(e["key"] for e in no_doi)
              + "\n  (books/chapters often lack DOIs — verify these by hand; see integrity rule 14)")
    if failed:
        print(f"\n✗ lookups failed ({len(failed)}): " + ", ".join(e["key"] for e, _ in failed))
    sys.exit(2 if flagged else (1 if (failed or not with_doi) else 0))


if __name__ == "__main__":
    main()
