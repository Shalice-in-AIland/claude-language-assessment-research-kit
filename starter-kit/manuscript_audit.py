#!/usr/bin/env python3
"""manuscript_audit.py — independent second-model audit of a pre-submission review.

Part of CLARK (claude-language-assessment-research-kit). Standard library only — no installs.

Sends the MANUSCRIPT TEXT plus the review's numbered findings to a SECOND,
cross-vendor model, which acts as an independent rater: it re-judges each
finding against the manuscript (concur / dispute / cannot-judge, with reasons),
lists anything the review missed (evidence-anchored, propose-only), and returns
its own 0-100 score and readiness verdict. Two independent raters on the same
review — agreement is information, disagreement is a question for the author.

CONFIDENTIALITY — read before running: this script TRANSMITS the unpublished
manuscript to the configured provider. That is the author's call to make, each
time: use your own API key (set as an environment variable — the key itself
never appears in any file), check your institution's policy on external AI
services and the target venue's AI policy, and prefer providers whose terms
exclude training on API data. The --confirm-send flag exists so the
transmission is always an explicit, per-run decision. Outputs stay local and
are part of the manuscript's confidential record.

Charter: PROPOSE-ONLY. This script never edits anything — it produces one
dated report the author adjudicates. The audit is a second rater, not a truth
oracle: qualified human reviewers routinely span the full decision range on
one manuscript, so divergence here measures uncertainty, not error.

Reproducibility: model ID, sampling/effort, and prompt version are pinned —
either in the project's review-conventions.md (## Audit section, shared with
review_audit.py) or via flags — and stamped into every report with measured
token usage and, if prices are configured, the actual spend.

Usage:
  python3 manuscript_audit.py <manuscript.md|.txt> --findings <triage.md>
        [--conventions review-conventions.md]            # reuse the pinned ## Audit block
        [--model M --base-url URL --key-env VAR]         # or pin explicitly
        [--effort low|medium|high | --temperature T]
        [--out "Manuscript Audit — DATE.md"] [--dry-run] --confirm-send

Start with --dry-run (payload sizes + estimated spend; nothing is transmitted).
Exit codes: 0 = all findings concurred, nothing missed · 2 = disputes/missed items
to adjudicate · 1 = usage/config error.
"""
import argparse
import datetime
import json
import pathlib
import os
import re
import sys
import urllib.error
import urllib.request

PROMPT_VERSION = "MA-v2"  # v2: XML payload tags, quote-first evidence, factual-vs-judgment dispute typing (per both vendors' published prompting guides)

SYSTEM = (
    "You are an independent second rater auditing a pre-submission review of a manuscript in "
    "language assessment / applied linguistics. The user message contains a <manuscript> and the "
    "first reviewer's numbered <findings>. Judge every finding ONLY from the manuscript text provided.\n"
    "Rules: include the shortest decisive verbatim quote from the manuscript in each reason where "
    "possible. Never invent quotes, page numbers, statistics, or literature. If a finding cannot be "
    "judged from the text alone (e.g., it depends on a figure image or an external source), use "
    "cannot-judge and say why. Classify every dispute: dispute_type=\"factual\" when the manuscript "
    "text contradicts the finding, \"judgment\" when the finding rests on an interpretation that "
    "permits a defensible alternative reading. Missed findings must be evidence-anchored: name the "
    "section and quote or describe the exact text.\n"
    "Respond with ONE JSON object and nothing else:\n"
    '{"finding_verdicts":[{"n":<finding number>,"verdict":"concur|dispute|cannot-judge",'
    '"dispute_type":"factual|judgment|n/a",'
    '"reason":"<one line, evidence-anchored, with a short verbatim quote where possible>"}],'
    '"missed_findings":[{"where":"<section / printed page if visible>","issue":"<the defect>",'
    '"evidence":"<what in the manuscript shows it>","severity":"major|minor"}],'
    '"independent_score":<0-100>,"score_drivers":"<one line>",'
    '"readiness":"ready|minor-revision|major-revision|structural","confidence":"high|medium|low"}'
)


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
            cfg[k.strip().lower()] = v.split("#")[0].strip()
    return cfg


def call_model(base_url, key, model, params, system, user, timeout=300):
    body = {"model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    body.update(params)
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.loads(r.read().decode())
    content = body["choices"][0]["message"]["content"]
    usage = body.get("usage", {})
    return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manuscript", help="manuscript TEXT file (.md/.txt — extract PDFs to text first)")
    ap.add_argument("--findings", required=True, help="the review's numbered findings/triage (compact .md)")
    ap.add_argument("--conventions", help="review-conventions.md carrying the shared '## Audit' pinning block")
    ap.add_argument("--model")
    ap.add_argument("--base-url")
    ap.add_argument("--key-env", help="NAME of the env var holding the key (the key never appears in files)")
    ap.add_argument("--effort", choices=["low", "medium", "high"])
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true", help="payload sizes + estimated spend; transmits nothing")
    ap.add_argument("--confirm-send", action="store_true",
                    help="REQUIRED to transmit: acknowledges the manuscript text will be sent to the provider")
    a = ap.parse_args()

    cfg = parse_audit_config(a.conventions) if a.conventions else {}
    model = a.model or cfg.get("manuscript-model") or cfg.get("model")
    base_url = a.base_url or cfg.get("base-url")
    key_env = a.key_env or cfg.get("key-env")
    if not (model and base_url and key_env):
        sys.exit("config error: need model, base-url and key-env (via --conventions '## Audit' block or flags)")
    params = {}
    eff = a.effort or cfg.get("manuscript-effort") or cfg.get("reasoning-effort") or cfg.get("effort")
    if eff:
        params["reasoning_effort"] = eff
    elif a.temperature is not None or cfg.get("temperature"):
        params["temperature"] = a.temperature if a.temperature is not None else float(cfg["temperature"])

    ms_text = pathlib.Path(a.manuscript).read_text(encoding="utf-8")
    findings = pathlib.Path(a.findings).read_text(encoding="utf-8")
    user = (f"<manuscript>\n{ms_text}\n</manuscript>\n\n"
            f"<findings>\n{findings}\n</findings>\n\n"
            f"Audit per the system instructions. Prompt version {PROMPT_VERSION}.")

    approx_in = (len(SYSTEM) + len(user)) // 4  # rough chars/4 preview only; the report uses measured usage
    pin, pout = cfg.get("price-in"), cfg.get("price-out")
    est = f" · est. input cost ${approx_in / 1e6 * float(pin):.3f}" if pin else ""
    print(f"[plan] model={model} params={params or 'provider defaults'} prompt={PROMPT_VERSION} "
          f"payload≈{approx_in:,} tokens (chars/4 preview){est}")
    if a.dry_run:
        print("[dry-run] nothing transmitted.")
        return
    if not a.confirm_send:
        sys.exit("refusing to transmit: re-run with --confirm-send (this sends the manuscript text to the "
                 "provider — your key, your institution's policy, your call) or use --dry-run.")

    key = os.environ.get(key_env or "")
    if not key:
        sys.exit(f"config error: environment variable {key_env} is not set")
    try:
        content, tin, tout = call_model(base_url, key, model, params, SYSTEM, user)
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code}: {e.read().decode()[:400]}")
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        sys.exit(f"could not parse a JSON verdict from the response:\n{content[:600]}")
    v = json.loads(m.group(0))

    disputes = [x for x in v.get("finding_verdicts", []) if x.get("verdict") == "dispute"]
    cannot = [x for x in v.get("finding_verdicts", []) if x.get("verdict") == "cannot-judge"]
    missed = v.get("missed_findings", [])
    date = datetime.date.today().isoformat()
    spend = ""
    if pin and pout:
        spend = f" · spend ${tin / 1e6 * float(pin) + tout / 1e6 * float(pout):.4f}"
    lines = [
        f"# Manuscript Audit — {date}",
        "",
        f"*Second-rater audit (cross-vendor). Model **{model}** · params {params or 'provider defaults'} · "
        f"prompt {PROMPT_VERSION} · measured usage {tin:,} in / {tout:,} out{spend}. "
        f"PROPOSE-ONLY: disagreements are questions for the author, not corrections. "
        f"This report quotes an unpublished manuscript — keep it with the manuscript's confidential record.*",
        "",
        f"## Independent verdict: score {v.get('independent_score')} · {v.get('readiness')} "
        f"(confidence {v.get('confidence')})",
        f"{v.get('score_drivers', '')}",
        "",
        "## Per-finding verdicts",
        "",
        "| # | Verdict | Dispute type | Reason |",
        "|---|---|---|---|",
    ]
    for x in v.get("finding_verdicts", []):
        lines.append(f"| {x.get('n')} | {x.get('verdict')} | {x.get('dispute_type', 'n/a')} | "
                     f"{x.get('reason', '').replace('|', '/')} |")
    lines += ["", f"## Findings the review may have missed ({len(missed)})", ""]
    for x in missed:
        lines.append(f"- **[{x.get('severity')}] {x.get('where')}** — {x.get('issue')} · "
                     f"evidence: {x.get('evidence')}")
    if not missed:
        lines.append("- none proposed")
    lines += ["", "## Adjudication",
              f"- {len(disputes)} dispute(s), {len(cannot)} cannot-judge, {len(missed)} proposed missed finding(s).",
              "- The author adjudicates each item with the manuscript in hand; the first review's evidence "
              "ledger is the tie-breaker discipline (page-anchored beats plausible). Factual disputes "
              "are checkable; judgment disputes are the expert-adjudication layer — no model tier "
              "converts interpretation into fact.",
              ""]
    out = pathlib.Path(a.out or f"Manuscript Audit — {date}.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[done] {out} · {len(disputes)} dispute(s) · {len(missed)} missed-finding proposal(s){spend}")
    sys.exit(2 if (disputes or missed) else 0)


if __name__ == "__main__":
    main()
