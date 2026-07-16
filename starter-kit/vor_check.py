#!/usr/bin/env python3
"""vor_check.py — find published versions-of-record for the preprints in a bibliography.

Part of CLAS (claude-language-assessment-skills). Standard library only — no installs.

For every PREPRINT-typed entry in a .bib (entry type unpublished/misc/online/preprint, or an
arXiv marker), queries Crossref for a journal-article whose title closely matches, then
GUARDS against the classic false positive (a similarly-titled paper by different people) by
requiring author-surname overlap before reporting a candidate.

PROPOSE-ONLY: prints candidates with their evidence (title similarity + shared surnames).
Updating the record happens in Zotero, by the user — per the integrity charter, a preprint
is cited as such or upgraded to the version of record once verified (docs/04).

Usage:  python3 vor_check.py <library.bib> --mailto <your-email> [--only key1,key2]
Exit:   0 = no candidates · 2 = candidates found (verify + update in Zotero) · 1 = error
"""
import argparse
import difflib
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request


def parse_bib(path):
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    out = {}
    for chunk in re.split(r"\n(?=@)", text):
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)", chunk)
        if not m:
            continue
        etype, key = m.group(1).lower(), m.group(2).strip()
        preprint = etype in ("unpublished", "misc", "online", "preprint") or "arxiv" in chunk.lower()
        t = re.search(r"title\s*=\s*[{\"]{1,2}(.+?)[}\"]{1,2},?\n", chunk, re.S)
        a = re.search(r"author\s*=\s*[{\"](.+?)[}\"],?\n", chunk, re.S)
        title = re.sub(r"[{}]", "", re.sub(r"\s+", " ", t.group(1))).strip() if t else ""
        surnames = set(s.strip().split(",")[0].strip().lower()
                       for s in (a.group(1) if a else "").split(" and ") if s.strip())
        if preprint and title:
            out[key] = (title, surnames)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib")
    ap.add_argument("--mailto", required=True, help="your email — Crossref etiquette")
    ap.add_argument("--only", help="comma-separated citekeys to check (default: every preprint)")
    a = ap.parse_args()
    preprints = parse_bib(a.bib)
    if a.only:
        wanted = {k.strip() for k in a.only.split(",")}
        preprints = {k: v for k, v in preprints.items() if k in wanted}
    if not preprints:
        print("no preprint-typed entries found")
        sys.exit(0)

    candidates = 0
    for key, (title, surnames) in sorted(preprints.items()):
        url = ("https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(title[:150])
               + "&filter=type:journal-article&rows=3&mailto=" + urllib.parse.quote(a.mailto))
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                items = json.load(r)["message"]["items"]
        except Exception as e:
            print(f"{key}: lookup failed ({type(e).__name__})")
            continue
        best = None
        for it in items:
            cand = (it.get("title") or [""])[0]
            sim = difflib.SequenceMatcher(None, title.lower(), cand.lower()).ratio()
            cand_surnames = {au.get("family", "").lower() for au in it.get("author", [])}
            shared = surnames & cand_surnames
            if sim > 0.75 and shared and (best is None or sim > best[0]):
                best = (sim, it, cand, shared)
        if best:
            sim, it, cand, shared = best
            yr = (it.get("published") or {}).get("date-parts", [["?"]])[0][0]
            venue = (it.get("container-title") or [""])[0]
            print(f"★ {key}: LIKELY PUBLISHED — '{cand[:70]}' · {venue[:45]} ({yr}) · doi:{it['DOI']}")
            print(f"    evidence: title-sim {sim:.2f} · shared surnames: {', '.join(sorted(shared))}"
                  f" → verify, then update the record in Zotero (pin the citekey first!)")
            candidates += 1
        else:
            print(f"  {key}: still preprint-only (no author-matched journal version on Crossref)")
    sys.exit(2 if candidates else 0)


if __name__ == "__main__":
    main()
