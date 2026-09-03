# Self-check — answer key

*What a good run of the portable check should surface from [`self-check-sample.md`](self-check-sample.md). Nine planted issues: some catchable by cross-checking the passage against the list (no search needed), some only by looking each record up, and one — the headline case — that no tool can settle for you, only flag.*

*Two references are **real and correct** and should come back verified; everything else is invented or planted. Verified against the primary record on **2026-09-03** — re-check the two real ones if you reuse this later (status drifts).*

## Catchable by eye — passage ↔ list cross-check

| # | Item | Issue |
|---|---|---|
| 1 | **Okonkwo & Reyes (2024)** | **Orphan** — cited in the passage, absent from the list. |
| 2 | **Halvorsen (2022)** | **Reverse orphan** — in the list, never cited. Informational, not fatal ("padding?"). |
| 3 | **Petrov (2023)** vs **Petrov (n.d.)** | **Duplicate** — the same work appears twice, once with full details, once stripped of its year and volume. The year-less copy also renders as **"n.d."** |

## Catchable only by checking the records

| # | Item | Issue | What the check should say |
|---|---|---|---|
| 4 | **Adeyemi (2025)**, DOI `10.5555/fake.2025.000000` | **Dead / fabricated DOI** — resolves to nothing in Crossref, DataCite, or OpenAlex. | UNRESOLVED — treat as unverified, not automatically "fake": the correct verdict is *"no record found in any index — confirm this reference exists."* |
| 5 | **Bannò et al. (2024)** cited as the arXiv preprint | **Preprint with a version of record** — the same work is published (BEA 2024, ACL Anthology `2024.bea-1.14`). The authors and work are cited correctly; the only fix is to cite the published version. *(Not a criticism of the paper.)* | Flag: a VoR exists; cite it instead (rule 4). |
| 6 | **Larsson & Mehta (2026)** | **Under-review preprint cited as established fact** — the passage states its finding as settled ("AI raters now agree with expert humans across every analytic dimension … increasingly treated as settled"), and even quotes it, from a preprint that has not been peer-reviewed. **This is the headline case.** | The check should (a) confirm it's labelled a preprint, (b) remind you it is **not yet peer-reviewed — provisional evidence**, (c) flag that the prose treats it as fact and carries a load-bearing claim on it alone, and (d) note the quote has no locator. It must **not** rule on whether the finding is true — that's your judgement. |

## Also planted (honesty & completeness)

| # | Item | Issue |
|---|---|---|
| 7 | The quotation in ¶1 ("AI raters now agree…") | **Direct quote without a locator** — no page/section number (rule 9). |
| 8 | **Lumley (2005)** in ¶2 | **Secondary framing risk** — a rater-training claim from human-rater research is extended to AI raters in the passage's own voice. If that bridge came from another paper's summary, it needs an *"as cited in"* (rules 5, 6); if it's the citing author's own inference, the source shouldn't carry it. A judgement flag, not a hard error. |
| 9 | **Adeyemi (2025)** claim | **Load-bearing claim on an unverifiable source** — the "agreement drops for lower-proficiency writers" point rests entirely on the reference that doesn't resolve (#4). Worth surfacing as its own risk. |

**Real & correct (should verify ✓):** Mizumoto & Eguchi (2023), *RMAL* — real, DOI resolves and matches. Bannò et al. (2024) — real work (the *only* issue is preprint-vs-VoR, #5). These two are why the report shouldn't be all red: a healthy check shows verified items too.

## The one lesson to land

A good report here is **not** "8 fakes found." It's a three-way split: a couple **verified ✓**, several **to fix** (orphans, duplicate, dead DOI, VoR), and at least one parked as **your call** — the under-review preprint (#6). The tool's job is to *route your attention*; deciding whether an unreviewed frontier-model finding is solid enough to build on stays with you.
