# Self-check — answer key

*What a good run of the portable check should surface from [`self-check-sample.md`](self-check-sample.md). Nine planted issues: some catchable by cross-checking the passage against the list (no search needed), some only by looking each record up, and one — the headline case — that no tool can settle for you, only flag.*

*Six of the twelve references are **real** (all re-verified against Crossref / the ACL Anthology on **2026-09-03**): five should come back **verified ✓** — Mizumoto & Eguchi (2023), Jin et al. (2025), Yamashita (2025), Li et al. (2026), Suhan & Wolf (2026) — and one, Bannò et al. (2024), is real with a single planted issue (#5). Everything else is invented or planted. Re-check the real ones if you reuse this later (status drifts).*

## Catchable by eye — passage ↔ list cross-check

| # | Item | Issue |
|---|---|---|
| 1 | **Okonkwo & Reyes (2024)** | **Orphan** — cited in the passage, absent from the list. *The most-missed item in early runs: tools busy verifying records skip the passage↔list cross-check, which needs no search at all.* |
| 2 | **Halvorsen (2022)** | **Reverse orphan** — in the list, never cited. Informational, not fatal ("padding?"). (Invented book chapter; a tool will also find no record — correct.) |
| 3 | **Petrov (2023)** vs **Petrov (n.d.)** | **Duplicate** — the same work appears twice, once with full details, once stripped of its year and volume. The year-less copy also renders as **"n.d."** |

## Catchable only by checking the records

| # | Item | Issue | What the check should say |
|---|---|---|---|
| 4 | **Adeyemi (2025)**, DOI `10.5555/fake.2025.000000` | **Dead / fabricated DOI** — resolves to nothing in Crossref, DataCite, or OpenAlex. | UNRESOLVED — treat as unverified, not automatically "fake": the correct verdict is *"no record found in any index — confirm this reference exists."* |
| 5 | **Bannò et al. (2024)** cited as the arXiv preprint | **Preprint with a version of record** — the same work is published (BEA 2024, ACL Anthology `2024.bea-1.14`). The authors and work are cited correctly; the only fix is to cite the published version. *(Not a criticism of the paper.)* | Flag: a VoR exists; cite it instead (rule 4). |
| 6 | **Larsson & Mehta (2026)** | **Under-review preprint cited as established fact** — the passage states its finding as settled ("AI raters now agree with expert humans across every analytic dimension … increasingly treated as settled"), and even quotes it, from a preprint that has not been peer-reviewed. **This is the headline case.** | Because this preprint is *invented*, a searching tool will — correctly — report **no record found** rather than "provisional." What to score: it must **not** call it fake outright ("no record found — confirm it exists" is the honest verdict), it must flag the quotation as untraceable, and it must **not** rule on whether the finding is true. (The provisional-preprint habit itself is taught in the checklist; a tool that adds "even if found, an under-review preprint is provisional" is doing well.) |

## Also planted (honesty & completeness)

| # | Item | Issue |
|---|---|---|
| 7 | The quotation in ¶1 ("AI raters now agree…") | **Direct quote without a locator** — no page/section number (rule 9). Tools often fold this into the untraceable-quote flag (#6); count it caught if the quote is flagged for lacking a verifiable source or locator. |
| 8 | **Lumley (2005)** in ¶2 | **Secondary framing risk** — a rater-training claim from human-rater research is extended to AI raters in the passage's own voice. If that bridge came from another paper's summary, it needs an *"as cited in"* (rules 5, 6); if it's the citing author's own inference, the source shouldn't carry it. A judgement flag, not a hard error. |
| 9 | **Adeyemi (2025)** claim | **Load-bearing claim on an unverifiable source** — the "agreement drops for lower-proficiency writers" point rests entirely on the reference that doesn't resolve (#4). Worth surfacing as its own risk. |

## Real & correct — the clean decoys (should verify ✓)

Mizumoto & Eguchi (2023), *RMAL* · Jin et al. (2025), *Education and Information Technologies* · Yamashita (2025), *Language Testing* · Li et al. (2026), *Scientific Reports* · Suhan & Wolf (2026), *Language Testing* — every DOI resolves and matches. Bannò et al. (2024) is also real; its *only* issue is preprint-vs-VoR (#5). A realistic reference list is mostly right with a few problems, and a healthy report shows that — these six are why the result shouldn't be all red.

**Claim-faithfulness (offer-only in the pack, so a tool may or may not run it):** the sentences attached to the six real papers are written to match their abstracts — a tool that runs the spot-check should find them supported. If it flags one, check the abstract yourself; if the tool is right, the sample needs fixing — tell us.

**A passed-with-note to watch for:** Suhan & Wolf appeared online in 2025 and in print in 2026 (vol. 43, issue 1). A check comparing against the online-first record may show a year discrepancy — that is a benign *passed-with-note*, not an error: identity verified, publication state normal.

## The one lesson to land

A good report here is **not** "8 fakes found." It's a three-way split: a couple **verified ✓**, several **to fix** (orphans, duplicate, dead DOI, VoR), and at least one parked as **your call** — the under-review preprint (#6). The tool's job is to *route your attention*; deciding whether an unreviewed frontier-model finding is solid enough to build on stays with you.
