#!/usr/bin/env python3
"""resolve_check.py — does every reference RESOLVE, and does the resolved record MATCH your entry?

The companion to check_retractions.py. It answers the two questions behind integrity rules 1-3, per
BibTeX entry, against a public index (Crossref) — independently of any AI judgement:

  • Entry WITH a DOI — does the DOI resolve to a real Crossref record, AND do that record's title,
    year, and first author MATCH your entry? A DOI that resolves to a *different* work is a
    mis-attached / "Frankenstein" reference (rule 2); a DOI that resolves to nothing fails rule 3.
  • Entry WITHOUT a DOI — query Crossref by title + author and surface candidate matches, so you can
    add the right DOI. It only PROPOSES candidates; it never edits your library (rule 13, no silent
    corrections) — you confirm and add the DOI in Zotero yourself.

Verifies existence AND consistency, not just existence. Standard library only; free; no key needed.

Usage:  python3 resolve_check.py [path/to/library.bib] [--mailto you@example.org] [--strict]
  --strict : also exit non-zero if a DOI-less entry has no confident Crossref match.
Exit code: 0 = every DOI-bearing entry resolved and matched; 2 = at least one UNRESOLVED or MISMATCH
(so a skill or CI can gate on it). The mailto joins Crossref's "polite pool" (etiquette, not auth).
"""
import difflib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TITLE_MATCH = 0.60      # below this similarity to the resolved title => flag a mismatch
STRONG_CANDIDATE = 0.85  # DOI-less: a candidate this similar is worth proposing as "likely the DOI"

# Type awareness stops us proposing a *review's* DOI (a journal-article) for a book, etc.
BOOKISH_BIB = {"book", "booklet", "incollection", "inbook", "inproceedings",
               "proceedings", "manual", "phdthesis", "mastersthesis"}
CR_BOOK_TYPES = {"book", "monograph", "edited-book", "reference-book",
                 "book-set", "book-track", "book-series", "book-part", "book-section"}


def type_compatible(bib_type, cr_type):
    """A book-ish entry should resolve to a book-ish record, and vice versa."""
    return (bib_type in BOOKISH_BIB) == (cr_type in CR_BOOK_TYPES)


def norm(s):
    s = re.sub(r"[{}]", "", s or "")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def get_field(body, name):
    """Extract a BibTeX field value: {balanced braces, one level of nesting} | "quoted" | bare."""
    m = re.search(r"\b" + name + r"\s*=\s*", body, re.IGNORECASE)
    if not m:
        return None
    i = m.end()
    if i < len(body) and body[i] == "{":
        depth = 0
        for j in range(i, len(body)):
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
                if depth == 0:
                    return body[i + 1:j]
    elif i < len(body) and body[i] == '"':
        j = body.find('"', i + 1)
        return body[i + 1:j] if j != -1 else None
    else:
        m2 = re.match(r"\s*([^,\n]+)", body[i:])
        return m2.group(1).strip() if m2 else None
    return None


def first_author_family(author_field):
    if not author_field:
        return ""
    first = re.split(r"\s+and\s+", author_field.strip())[0]
    if "," in first:                       # "Family, Given" (Zotero/BBT default)
        return norm(first.split(",")[0])
    toks = first.split()                   # "Given Family" fallback
    return norm(toks[-1]) if toks else ""


def parse_bib(path):
    txt = open(path, encoding="utf-8").read()
    entries = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)(?=\n@|\Z)", txt, re.DOTALL):
        body = m.group(3)
        yr = get_field(body, "year")
        yr = int(re.search(r"\d{4}", yr).group()) if yr and re.search(r"\d{4}", yr) else None
        entries.append({
            "key": m.group(2).strip(),
            "type": m.group(1).lower(),
            "doi": (get_field(body, "doi") or "").strip() or None,
            "title": (get_field(body, "title") or "").strip(),
            "year": yr,
            "family": first_author_family(get_field(body, "author")),
        })
    return entries


def _record(msg):
    year = None
    for k in ("published-print", "published-online", "issued", "published", "created"):
        dp = (msg.get(k) or {}).get("date-parts") or [[None]]
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    auths = msg.get("author") or []
    return {"doi": msg.get("DOI", ""),
            "title": (msg.get("title") or [""])[0],
            "year": year,
            "type": msg.get("type", ""),
            "family": norm(auths[0].get("family", "")) if auths else ""}


def _get(url, mailto):
    req = urllib.request.Request(url, headers={"User-Agent": f"resolve-check/1.0 (mailto:{mailto})"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def crossref_by_doi(doi, mailto):
    try:
        data = _get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""), mailto)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None                    # DOI does not resolve to a Crossref record
        raise
    return _record(data.get("message", {}))


def crossref_by_title(entry, mailto, rows=3):
    params = {"query.bibliographic": entry["title"], "rows": str(rows)}
    if entry["family"]:
        params["query.author"] = entry["family"]
    data = _get("https://api.crossref.org/works?" + urllib.parse.urlencode(params), mailto)
    out = []
    for it in data.get("message", {}).get("items", []):
        rec = _record(it)
        rec["sim"] = difflib.SequenceMatcher(None, norm(entry["title"]), norm(rec["title"])).ratio()
        out.append(rec)
    return sorted(out, key=lambda r: r["sim"], reverse=True)


def mismatch_reasons(entry, rec):
    reasons = []
    if entry["title"] and rec["title"]:
        sim = difflib.SequenceMatcher(None, norm(entry["title"]), norm(rec["title"])).ratio()
        if sim < TITLE_MATCH:
            reasons.append(f"title differs (sim {sim:.2f}): DOI resolves to \"{rec['title'][:60]}\"")
    if entry["year"] and rec["year"] and abs(entry["year"] - rec["year"]) > 1:
        reasons.append(f"year differs: entry {entry['year']} vs record {rec['year']}")
    if entry["family"] and rec["family"] and entry["family"] not in rec["family"] and rec["family"] not in entry["family"]:
        reasons.append(f"first author differs: entry '{entry['family']}' vs record '{rec['family']}'")
    return reasons


def main():
    argv = sys.argv[1:]
    strict = "--strict" in argv
    mailto = next((a.split("=", 1)[1] for a in argv if a.startswith("--mailto=")), "example@example.org")
    pos = [a for a in argv if not a.startswith("--")]
    bib = pos[0] if pos else __file__.rsplit("/", 1)[0] + "/library.bib"

    entries = parse_bib(bib)
    with_doi = [e for e in entries if e["doi"]]
    no_doi = [e for e in entries if not e["doi"]]
    print(f"library: {bib}\nentries: {len(entries)}  with DOI: {len(with_doi)}  without DOI: {len(no_doi)}\n")

    verified, unresolved, mismatched, failed = [], [], [], []
    for i, e in enumerate(with_doi, 1):
        try:
            rec = crossref_by_doi(e["doi"], mailto)
        except Exception as ex:
            failed.append((e, str(ex)[:60]))
            print(f"\r  resolved {i}/{len(with_doi)}", end="", flush=True)
            time.sleep(0.2)
            continue
        if rec is None:
            unresolved.append(e)
        else:
            reasons = mismatch_reasons(e, rec)
            (mismatched if reasons else verified).append((e, rec, reasons))
        print(f"\r  resolved {i}/{len(with_doi)}", end="", flush=True)
        time.sleep(0.2)
    if with_doi:
        print("\n")

    proposals, type_diff, no_match = [], [], []
    for e in no_doi:
        try:
            cands = crossref_by_title(e, mailto)
        except Exception as ex:
            failed.append((e, str(ex)[:60]))
            continue
        best = cands[0] if cands else None
        if best and best["sim"] >= STRONG_CANDIDATE and type_compatible(e["type"], best["type"]):
            proposals.append((e, best))
        elif best and best["sim"] >= STRONG_CANDIDATE:
            type_diff.append((e, best))          # same title, wrong kind of record (often a review)
        else:
            no_match.append((e, best))
        time.sleep(0.2)

    # ---- report ----
    if mismatched:
        print("⚠⚠ MISMATCH — the DOI resolves to what looks like a DIFFERENT work (possible mis-attach / Frankenstein, rule 2):")
        for e, rec, reasons in mismatched:
            print(f"  ⚠ {e['key']}  (DOI {e['doi']})")
            for r in reasons:
                print(f"      - {r}")
    if unresolved:
        print("\n✗ UNRESOLVED — DOI does not resolve to any Crossref record (rule 3):")
        for e in unresolved:
            print(f"  ✗ {e['key']}  (DOI {e['doi']})  {e['title'][:60]}")
    if not mismatched and not unresolved and with_doi:
        print(f"✓ All {len(with_doi)} DOI-bearing entries resolved and matched their Crossref record.")

    if proposals:
        print("\n○ NO DOI — a confident, type-matched Crossref record exists; add its DOI in Zotero (propose only — verify, don't auto-apply):")
        for e, c in proposals:
            print(f"  ○ {e['key']}  →  https://doi.org/{c['doi']}  (title sim {c['sim']:.2f}, type '{c['type']}')  \"{c['title'][:55]}\"")
    if type_diff:
        print("\n○ NO DOI — a same-TITLE record exists but its TYPE differs (for a book this is usually a REVIEW, not the book): do NOT attach without checking:")
        for e, c in type_diff:
            print(f"  ○ {e['key']}  candidate https://doi.org/{c['doi']}  is a '{c['type']}' (entry is @{e['type']}) — confirm it is the work itself, not a review")
    if no_match:
        print(f"\n○ NO DOI, no confident match ({len(no_match)}): " +
              ", ".join(e["key"] for e, _ in no_match) + "\n  (books/chapters often have no Crossref DOI — verify by hand; this is expected, not an error)")
    if failed:
        print(f"\n! lookups failed ({len(failed)}): " + ", ".join(e["key"] for e, _ in failed) + "  (network? rate limit? re-run)")

    hard = bool(mismatched or unresolved) or (strict and bool(no_match))
    sys.exit(2 if hard else 0)


if __name__ == "__main__":
    main()
