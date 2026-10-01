#!/usr/bin/env python3
"""review_audit.py — independent second-model audit of a literature-review matrix.

Part of CLARK (claude-language-assessment-research-kit). Standard library only — no installs.

Sends each matrix row (metadata only — no PDFs) to a SECOND, cross-vendor model,
which re-judges the row against the project's OWN rules (the review-conventions
file is transmitted verbatim as the rulebook) and returns strict-JSON verdicts:
tier consistency, KEY justification, internal row inconsistencies.

Charter: PROPOSE-ONLY. This script never writes to the matrix or the vault —
it produces one dated report the human adjudicates. The audit checks
consistency with the project's rules; it does not certify truth, and it never
replaces the scholar's reading.

Reproducibility (the project's own §-reproducibility doctrine, applied to us):
model ID, request format, sampling control (an effort or a temperature) and
prompt version are PINNED in review-conventions.md (## Audit section) and stamped
into every report, along with measured token usage and — if prices are
configured — the actual spend. The same prompt sent through a different API or a
different effort is a different run, so none of them changes mid-census.

Conventions ## Audit section (all bullets '- key: value'):
  - model: deepseek-v4-pro
  - base-url: https://api.deepseek.com/v1
  - key-env: DEEPSEEK_API_KEY          # env var NAME; the key itself never appears in any file Claude reads
  - temperature: 0
  - api: chat                          # optional: chat (default) | responses — see llm_api.py
  - max-output-tokens: 25000           # optional cap; OpenAI suggests reserving >=25,000 for
                                       #   reasoning + output. Omit for the model's own maximum.
  - prompt-version: v1
  - price-in: 0.435                    # optional, USD per 1M input tokens — enables spend reporting
  - price-out: 0.87                    # optional, USD per 1M output tokens
    # The two figures above are an ILLUSTRATION ONLY, and a dated one: they are a single flat
    # rate, while some providers (DeepSeek among them) now bill peak and off-peak separately.
    # Read your provider's current rate card the day you pin these, and note which tier they
    # assume — the spend line in the report is only as good as these two numbers.

Usage:
  python3 review_audit.py <matrix.xlsx|.csv> --conventions review-conventions.md
                          [--sheet <name>] [--limit N] [--only-key] [--citekeys k1,k2]
                          [--effort <level>] [--api chat|responses]
                          [--out "Review Audit — DATE.md"] [--dry-run]

Start with a pilot:  --limit 3  (measures real token usage; extrapolate before the full run).
Exit codes: 0 = all verdicts agree · 2 = disagreements/issues to adjudicate · 1 = usage/config error.
"""
import argparse
import datetime
import json
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from matrix_to_vault import CANON, find_header, read_csv, read_xlsx  # noqa: E402
# one request/parse implementation, shared with manuscript_audit.py, so the two cannot drift apart
try:
    import llm_api  # noqa: E402
except ModuleNotFoundError:
    sys.exit("this script now needs llm_api.py, which belongs beside it in the starter kit. "
             "Copy the current starter-kit/llm_api.py into this folder, then run "
             "`python3 clark_doctor.py` to check the rest of the kit is complete.")

FIELD_LABELS = [
    ("num", "Matrix row #"), ("authors", "Authors (Year)"), ("focus", "Short focus"),
    ("theme", "Theme"), ("primary", "Primary use"), ("relevance", "Relevance tier"),
    ("construct", "Construct link"), ("section", "Manuscript section"), ("read", "Read status"),
    ("keypoints", "Key points / notes"), ("flags", "Flags"), ("citekey", "Cite key"),
    ("recordstate", "Record state"), ("lastverified", "Last verified"),  # optional; blank rows omit them
]

SCHEMA = ('{"tier_verdict":"agree|disagree","tier_suggested":"<tier or same>",'
          '"key_verdict":"agree|disagree","key_reason":"<one line>",'
          '"row_issues":[{"issue":"<the inconsistency>","where":"<matrix field(s) involved>",'
          '"suggested_fix":"<concrete fix, or \'requires the paper\'>",'
          '"fix_basis":"row-internal|requires-paper"}],'
          '"confidence":"high|medium|low"}\n'
          'Rules for suggested_fix: propose a fix ONLY when the row itself contains enough information to '
          'resolve the issue (fix_basis=row-internal); if resolving would require reading the paper, say so '
          'plainly (fix_basis=requires-paper) and do NOT guess. Never invent page numbers, quotes, or facts '
          'not present in the row.')


def parse_audit_config(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    cfg, in_audit = {}, False
    for line in text.splitlines():
        low = line.strip().lower()
        if low.startswith("## "):
            in_audit = low.startswith("## audit")
            continue
        if in_audit and line.strip().startswith("- ") and ":" in line:
            k, v = line.strip()[2:].split(":", 1)
            # Drop trailing comments AND the template's own ⟨explanatory⟩ annotations, then
            # ignore the key entirely if nothing is left: an unfilled template line is not a value.
            v = v.split("#")[0].split("\u27e8")[0].strip()
            if v:
                cfg[k.strip().lower()] = v
    return cfg, text


def parse_verdict(content):
    m = re.search(r"\{.*\}", content, re.S)  # tolerate fences/prose around the JSON
    return json.loads(m.group(0)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("matrix")
    ap.add_argument("--conventions", required=True)
    ap.add_argument("--sheet")
    ap.add_argument("--limit", type=int, help="audit only the first N eligible rows (pilot mode)")
    ap.add_argument("--only-key", action="store_true", help="audit only rows carrying the ★ KEY marker")
    ap.add_argument("--citekeys", help="comma-separated citekeys to audit (targeted re-runs / A-B comparisons)")
    ap.add_argument("--effort",
                    help="override the conventions' reasoning effort for this run (logged in the report). "
                         f"Known values: {' | '.join(llm_api.KNOWN_EFFORTS)} — support is model-dependent "
                         "and the provider is the authority, so anything is passed through")
    ap.add_argument("--api", type=str.lower, choices=list(llm_api.APIS),
                    help="override the conventions' request format for this run (logged in the report)")
    ap.add_argument("--out", help="report path (default: 'Review Audit — <date>.md' in the current folder)")
    ap.add_argument("--dry-run", action="store_true", help="show the request plan and payload sizes; call nothing")
    a = ap.parse_args()

    cfg, rules_text = parse_audit_config(a.conventions)
    model = cfg.get("model")
    base_url = cfg.get("base-url")
    key_env = cfg.get("key-env", "")
    def num(key, cast=float):
        """A pinned number, or a legible config error instead of a traceback."""
        try:
            return cast(cfg[key])
        except (ValueError, TypeError):
            sys.exit(f"config error: '- {key}: {cfg[key]}' in the conventions' ## Audit block is not a number")
    api = (a.api or cfg.get("api") or "chat").lower()
    if api not in llm_api.APIS:
        sys.exit(f"error: '- api: {api}' is not recognised — use one of {' | '.join(llm_api.APIS)}")
    effort = a.effort or cfg.get("effort", "")
    if effort and effort not in llm_api.KNOWN_EFFORTS:
        print(f"note: effort '{effort}' is outside the values OpenAI documents "
              f"({', '.join(llm_api.KNOWN_EFFORTS)}); passing it through for the provider to accept or reject",
              file=sys.stderr)
    # Sampling and effort are mutually exclusive, and temperature is sent ONLY when pinned:
    # reasoning models take an effort instead, and vendors ask that temperature be omitted
    # whenever one is set. With neither pinned, the provider's own defaults apply.
    temperature = num("temperature") if (not effort and cfg.get("temperature")) else None
    if effort and cfg.get("temperature"):
        print(f"note: '- temperature: {cfg['temperature']}' is ignored because an effort ({effort}) is set",
              file=sys.stderr)
    max_out = num("max-output-tokens", int) if cfg.get("max-output-tokens") else None
    if not effort and temperature is None:
        print("note: no sampling control is pinned, so the provider's own default applies — which is not "
              "reproducible across runs. Pin '- effort:' (reasoning models) or '- temperature: 0' in the "
              "conventions' ## Audit block if this audit needs to be repeatable.", file=sys.stderr)
    sampling = llm_api.stamp(api, effort, temperature, cli_override=bool(a.effort))
    prompt_version = cfg.get("prompt-version", "v1")
    if not (model and base_url):
        sys.exit("error: the conventions file needs an '## Audit' section with '- model:' and '- base-url:' "
                 "(see review-conventions-template.md)")

    path = pathlib.Path(a.matrix)
    rows = read_csv(path) if path.suffix.lower() == ".csv" else read_xlsx(path, a.sheet)
    h, col = find_header(rows)
    papers = []
    for row in rows[h + 1:]:
        get = lambda k: str(row[col[k]]).strip() if k in col and col[k] < len(row) else ""
        vals = {k: get(k) for k in CANON}
        if not vals["citekey"]:
            continue
        if a.only_key and "★" not in (vals["keypoints"] + vals["flags"]):
            continue
        papers.append(vals)
    if a.citekeys:
        wanted = {k.strip() for k in a.citekeys.split(",") if k.strip()}
        papers = [v for v in papers if v["citekey"] in wanted]
        missing = wanted - {v["citekey"] for v in papers}
        if missing:
            print(f"warning: citekeys not found in matrix: {sorted(missing)}", file=sys.stderr)
    if a.limit:
        papers = papers[: a.limit]

    system = (
        "You are an independent, skeptical auditor of an academic literature-review matrix. "
        "You are NOT the model that wrote these rows. Judge each row ONLY against the project's own rules, "
        "which follow verbatim between the markers. Be conservative: a 'disagree' verdict requires a concrete, "
        "rule-based reason. The KEY rule reserves the marker for a SMALL, load-bearing set of papers. "
        f"Respond with STRICT JSON only, exactly this shape: {SCHEMA}\n"
        "=== PROJECT RULES START ===\n" + rules_text + "\n=== PROJECT RULES END ==="
    )

    def user_msg(v):
        lines = [f"{label}: {v.get(k)}" for k, label in FIELD_LABELS if v.get(k)]
        lines.append("KEY marker present: " + ("yes (★)" if "★" in (v["keypoints"] + v["flags"]) else "no"))
        lines.append("Audit questions: 1) Is the Relevance tier consistent with the tier definitions? "
                     "2) Is the KEY marking (present or absent) justified under the KEY rule? "
                     "3) Any internal inconsistencies within the row? Answer as the required JSON.")
        return "\n".join(lines)

    if a.dry_run:
        sizes = [len(system) + len(user_msg(v)) for v in papers]
        print(f"[DRY-RUN] would send {len(papers)} requests to {model} @ "
              f"{llm_api.endpoint(base_url, api)} ({sampling}, prompt {prompt_version})")
        print(f"rules payload: {len(system):,} chars per request · row payloads: "
              f"{min(sizes) - len(system):,}–{max(sizes) - len(system):,} chars · total: {sum(sizes):,} chars")
        print(f"key comes from ${key_env or '<key-env not set!>'} (currently "
              f"{'SET' if os.environ.get(key_env) else 'NOT SET'})")
        print("pilot suggestion: rerun with --limit 3 (no --dry-run) to measure real token usage first")
        sys.exit(0)

    key = os.environ.get(key_env or "", "")
    if not key:
        sys.exit(f"error: API key env var '{key_env}' is not set. Set it in your own shell "
                 f"(e.g. add  export {key_env}=<your key>  to ~/.zshrc) — never share the key in chat.")

    results, in_tok, out_tok = [], 0, 0
    for i, v in enumerate(papers, 1):
        for attempt in (1, 2):
            try:
                content, pt, ct, _ = llm_api.call(base_url, key, api, model, system, user_msg(v),
                                                  effort=effort or None, temperature=temperature,
                                                  max_output_tokens=max_out)
                in_tok += pt
                out_tok += ct
                verdict = parse_verdict(content)
                results.append((v, verdict if verdict else {"error": "unparseable response"}))
                break
            except llm_api.LLMError as e:
                if attempt == 2 or not e.retryable:
                    results.append((v, {"error": str(e)}))
                    break
                time.sleep(3)
            except json.JSONDecodeError as e:
                # the model replied, but not with parseable JSON — a row-level failure, never a crash
                results.append((v, {"error": f"unparseable JSON in the reply: {e}"}))
                break
        print(f"  audited {i}/{len(papers)}: {v['citekey']}", file=sys.stderr)

    today = datetime.date.today().isoformat()
    disagree = [(v, r) for v, r in results if r.get("tier_verdict") == "disagree" or r.get("key_verdict") == "disagree"]
    issues = [(v, r) for v, r in results if r.get("row_issues") and any(str(x).strip() for x in r["row_issues"])]
    errors = [(v, r) for v, r in results if "error" in r]
    agree_n = len(results) - len({v["citekey"] for v, _ in disagree} | {v["citekey"] for v, _ in errors})

    cost_line = f"- Tokens: {in_tok:,} in / {out_tok:,} out"
    if errors:
        cost_line += (f" · counts EXCLUDE {len(errors)} failed call(s), which the provider may still have "
                      f"billed for input and reasoning")
    if cfg.get("price-in") and cfg.get("price-out"):
        spend = in_tok / 1e6 * num("price-in") + out_tok / 1e6 * num("price-out")
        cost_line += f" · spend ≈ ${spend:.4f} (at ${cfg['price-in']}/{cfg['price-out']} per M, from conventions)"

    rep = [
        f"# Review Audit — {today}", "",
        "*PROPOSE-ONLY: an independent second model re-judged each matrix row against the project's own rules. "
        "Every disagreement below is a question for the human, not a correction. Nothing was changed anywhere.*", "",
        "## Configuration (pinned — reproducibility)",
        f"- Model: `{model}` @ {base_url} · {sampling} · prompt {prompt_version} · run {today}",
        "- Request format and sampling are part of what makes this reproducible: an identical prompt "
        "sent through a different API or effort is a different run.",
        cost_line, "",
        f"## Summary — {len(results)} rows audited",
        f"- Fully concurring: {agree_n}",
        f"- Disagreements to adjudicate: {len(disagree)}",
        f"- Rows with internal-consistency notes: {len(issues)}",
        f"- Audit failures (retry later): {len(errors)}", "",
        "## Disagreements (KEY first)",
    ]
    for v, r in sorted(disagree, key=lambda x: x[1].get("key_verdict") != "disagree"):
        rep.append(f"### [[{v['citekey']}]] — {v['authors']} (row {v['num']})")
        if r.get("key_verdict") == "disagree":
            rep.append(f"- **KEY disputed** — {r.get('key_reason', '')} (confidence: {r.get('confidence', '?')})")
        if r.get("tier_verdict") == "disagree":
            rep.append(f"- **Tier disputed** — has {v['relevance']}, auditor suggests {r.get('tier_suggested', '?')} "
                       f"(confidence: {r.get('confidence', '?')})")
        rep.append("")
    rep.append("## Internal-consistency notes")
    for v, r in issues:
        for note in r["row_issues"]:
            if isinstance(note, dict):  # schema v2: structured issue with field pointer + guarded fix
                if not str(note.get("issue", "")).strip():
                    continue
                line = f"- [[{v['citekey']}]] (field: {note.get('where', '?')}): {note['issue']}"
                fix, basis = note.get("suggested_fix", ""), note.get("fix_basis", "")
                if basis == "row-internal" and fix:
                    line += f" → **proposed fix (from the row itself):** {fix}"
                elif basis == "requires-paper":
                    line += " → **requires the paper** (escalate to a full-text check)"
                rep.append(line)
            elif str(note).strip():  # v1 back-compat
                rep.append(f"- [[{v['citekey']}]]: {note}")
    if errors:
        rep.append("")
        rep.append("## Failed (rerun with --limit on these rows)")
        rep += [f"- {v['citekey']}: {r['error']}" for v, r in errors]

    out = pathlib.Path(a.out or f"Review Audit — {today}.md")
    out.write_text("\n".join(rep) + "\n", encoding="utf-8")
    print(f"report -> {out}")
    print(cost_line.lstrip("- "))
    sys.exit(2 if (disagree or issues or errors) else 0)


if __name__ == "__main__":
    main()
