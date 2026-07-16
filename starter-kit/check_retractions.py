#!/usr/bin/env python3
"""check_retractions.py — automated retraction check for a BibTeX library (integrity rule 14).

For every DOI in the .bib, queries the Crossref REST API (which incorporates the human-verified
Retraction Watch database, acquired by Crossref in 2023) for any notice that UPDATES that DOI:
retractions, withdrawals, expressions of concern, and corrections. Entries without a DOI are
listed as unverifiable-by-DOI (check them by hand: books/chapters often have none).

Usage:  python3 check_retractions.py [path/to/library.bib] [--mailto you@example.org]
Free, no key needed; the mailto goes in the User-Agent per Crossref's "polite pool" etiquette.
Exit code: 0 = no retractions/EoC found; 2 = at least one found (so CI or a skill can gate on it).
"""
import json
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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    bib = args[0] if args else str(__file__).rsplit("/", 1)[0] + "/library.bib"
    mailto = "example@example.org"
    for a in sys.argv[1:]:
        if a.startswith("--mailto"):
            mailto = a.split("=", 1)[1] if "=" in a else "example@example.org"
    entries = parse_bib(bib)
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
    else:
        print("✓ No retractions, withdrawals, or expressions of concern found for any DOI-bearing entry.")
    if corrections:
        print(f"\nℹ corrections/errata on {len(corrections)} entr{'y' if len(corrections)==1 else 'ies'} (usually fine — check the notice):")
        for e, n in corrections:
            print(f"  ℹ {e['key']}  [{n['type']}]  https://doi.org/{n['notice_doi']}")
    if no_doi:
        print(f"\n○ unverifiable by DOI ({len(no_doi)}): " + ", ".join(e["key"] for e in no_doi)
              + "\n  (books/chapters often lack DOIs — verify these by hand; see integrity rule 14)")
    if failed:
        print(f"\n✗ lookups failed ({len(failed)}): " + ", ".join(e["key"] for e, _ in failed))
    sys.exit(2 if flagged else 0)


if __name__ == "__main__":
    main()
