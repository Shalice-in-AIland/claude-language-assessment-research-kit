# CLARK Field Guides — expert-curated domain knowledge for the pipeline

**The skills are the verbs; the field guides are the nouns.** CLARK's seven skills carry the *machinery* — triage, audit, render, review — and deliberately ship only a backbone of domain specifics. A **field guide** is the specifics layer for one domain, curated by a named expert: the venues and what they tell reviewers, the construct-specific evaluation criteria, the controlled vocabularies and quality checklists a living review needs, the watch-lists a radar sweeps. Drop a guide into a project and every skill gets domain-fluent without a single change to the machinery.

*Like the field guides naturalists carry: expert-compiled, meant for use in the field, revised as the field changes.*

## What a guide contains

Each guide is one folder, `field-guides/<domain-slug>/`, built from the [`_template/`](_template/):

| File | Feeds | Contents |
|---|---|---|
| `README.md` | everything | Scope, curator(s), version, last-verified date, changelog, and the guide's own citation |
| `venues.md` | pre-submission-review · writing-polish | Reviewer-facing guidance of the domain's journals — same format as the core `journal-reviewer-guides.md`, extracted verbatim-with-links from official sources |
| `criteria.md` | pre-submission-review | Construct- and design-specific evaluation criteria, each item traced to publisher/journal/standards material — never an invented rubric |
| `conventions-starter.md` | literature-review · literature-radar | A pre-filled `review-conventions.md` starter: theme vocabulary, hub terms, quality-checklist items, radar venue/preprint lists for the domain |
| `notes.md` *(optional)* | writing-polish · any | Register and terminology notes, key open resources (link-only, license-respecting) |

## The provenance rules (non-negotiable, inherited from the charter)

1. **Every criterion traces to a published source** — publisher reviewer forms, journal guidance, published standards/instruments. A guide documents where each item comes from; nothing is invented.
2. **Point and cite, never republish.** Published instruments (checklists, scales, frameworks) are summarized and DOI-linked, not reproduced — the guide sends readers to the authors' own work.
3. **Nothing unpublished or privately shared** enters a guide without the owner's written consent.
4. **Dated honesty:** every `venues.md`/`criteria.md` carries a *last-verified* date; guidance drifts, and guides say when they last looked.
5. Guides extend the **specifics layer only** — no guide modifies the seven skills or the 16-rule integrity charter (`docs/04`).

## Contributing — the three rungs

Experts join at whichever rung fits:

- **Rung A — built on your published work, credited.** A guide operationalizes a published, citable instrument or body of work with full citation. No involvement required from the original author; the credit is the citation itself, worded strictly descriptively ("based on the published X (Author, Year)").
- **Rung B — feedback-invited.** A drafted guide is sent to the domain's named expert for review before release. Their feedback is incorporated and acknowledged — **with their explicit agreement on the exact wording**. An acknowledgment is never phrased to imply endorsement.
- **Rung C — co-curated.** The expert joins as co-curator: real authorship on the guide's byline, citation, and DOI. A field guide is a **living, versioned, citable publication** — closer to a handbook chapter that never goes out of date than to a config file.

## Credit and citation

Each released guide carries its curator byline, a version, and (on release) its own archived DOI. Cite a guide like the publication it is:

> ⟨Curator(s)⟩ (Year). *The CLARK Field Guide to ⟨Domain⟩* (v⟨X.Y⟩). Zenodo. https://doi.org/⟨DOI⟩

Editorial review of every guide (structure, provenance, integrity fit) is by the CLARK maintainer before merge — the same propose-and-approve discipline the skills run on, one level up.

## Registry

| Guide | Domain | Curator(s) | Status |
|---|---|---|---|
| `awe/` | Automated Writing Evaluation (AI-mediated writing assessment & feedback) | Sha Liu | **founding guide — in preparation** |
| — | Automated Speaking Assessment | Sha Liu | proposed |
| — | Research synthesis in applied linguistics | — | proposed (in conversation) |

*Want to curate a guide for your domain — listening assessment, item writing, young learners, teacher assessment literacy…? Open an issue or contact the maintainer. The template plus an afternoon of your expertise is a first draft; the machinery, formatting, and archiving are handled for you.*

---

*Series provenance: the compile-sources-once-into-cited-Markdown pattern resonates with Andrej Karpathy's LLM-wiki idea (2026); CLARK's guides are the shareable, expert-authored, editorially-gated variant — curated data for a fixed integrity pipeline, not a self-evolving wiki.*
