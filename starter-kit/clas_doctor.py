#!/usr/bin/env python3
"""clas_doctor.py — one-command health check for a CLAS setup.

Part of CLAS (claude-language-assessment-skills). Standard library only.

Checks, without changing anything:
  · Python version (3.8+)
  · Pandoc present (PATH or ~/.local/bin/pandoc, mirroring render.sh) + version
  · PyMuPDF (optional — upgrades pdf_probe.py precision and PDF page rendering;
    its absence is a note, not a failure)
  · starter-kit integrity (the scripts and style file all present)
  · with --project <dir>: the project's library.bib and style.csl exist
  · with --conventions <file>: every key-env named in the '## Audit' block is
    set in the environment (presence only — values are never read or printed),
    and which model pins are declared

Usage:  python3 clas_doctor.py [--project <dir>] [--conventions <file>]
Exit codes: 0 = all required checks pass · 2 = something needs attention.
"""
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
EXPECTED = ["render.sh", "render.bat", "style.csl", "resolve_check.py", "check_retractions.py",
            "vor_check.py", "matrix_to_vault.py", "review_audit.py", "manuscript_audit.py",
            "pdf_probe.py"]


def find_pandoc():
    p = shutil.which("pandoc")
    if not p:
        cand = pathlib.Path.home() / ".local" / "bin" / "pandoc"
        p = str(cand) if cand.exists() else None
    if not p:
        return None, None
    try:
        v = subprocess.run([p, "--version"], capture_output=True, text=True, timeout=10)
        return p, v.stdout.splitlines()[0]
    except Exception:
        return p, "present (version check failed)"


def parse_audit(path):
    cfg, in_audit = {}, False
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        low = line.strip().lower()
        if low.startswith("## "):
            in_audit = low.startswith("## audit")
            continue
        if in_audit and line.strip().startswith("- ") and ":" in line:
            k, v = line.strip()[2:].split(":", 1)
            cfg[k.strip().lower()] = v.split("#")[0].strip()
    return cfg


def main():
    project = conventions = None
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--project" and i + 1 < len(argv):
            project = pathlib.Path(argv[i + 1])
        if a == "--conventions" and i + 1 < len(argv):
            conventions = argv[i + 1]

    problems = 0
    def report(status, label, detail=""):
        nonlocal problems
        if status == "FAIL":
            problems += 1
        print(f"[{status:4}] {label}" + (f" — {detail}" if detail else ""))

    v = sys.version_info
    report("OK" if v >= (3, 8) else "FAIL", f"Python {v.major}.{v.minor}.{v.micro}",
           "" if v >= (3, 8) else "3.8+ required")

    p, pv = find_pandoc()
    report("OK" if p else "FAIL", "Pandoc", pv or "not found on PATH or ~/.local/bin — see docs/03 for install")

    has_mupdf = importlib.util.find_spec("fitz") is not None
    report("OK" if has_mupdf else "NOTE", "PyMuPDF (optional)",
           "installed — pdf_probe gives precise per-page reports and pages can be rendered to images"
           if has_mupdf else
           "not installed — pdf_probe falls back to the stdlib heuristic; install with "
           "'pip install --user pymupdf' for per-page precision and page rendering (optional)")

    missing = [f for f in EXPECTED if not (HERE / f).exists()]
    report("OK" if not missing else "FAIL", "starter-kit integrity",
           "all scripts present" if not missing else f"missing: {', '.join(missing)} — the repo folder must stay intact")

    if project:
        hits = list(project.rglob("library.bib"))
        report("OK" if hits else "FAIL", "project library.bib",
               str(hits[0]) if hits else f"not found under {project} — see docs/01")
        csl = list(project.rglob("*.csl"))
        report("OK" if csl else "FAIL", "project citation style (*.csl)",
               str(csl[0]) if csl else f"no .csl file under {project} — copy starter-kit/style.csl (see docs/01)")

    if conventions:
        try:
            cfg = parse_audit(conventions)
        except FileNotFoundError:
            report("FAIL", "conventions file", f"{conventions} not found")
            cfg = {}
        if cfg:
            for key in ["model", "manuscript-model"]:
                report("OK" if cfg.get(key) else "NOTE", f"pin '{key}:'",
                       cfg.get(key, "not declared" + (" (audits fall back to 'model:')" if key != "model" else "")))
            env_name = cfg.get("key-env")
            if env_name:
                report("OK" if os.environ.get(env_name) else "FAIL", f"key env ${env_name}",
                       "set" if os.environ.get(env_name) else
                       "NOT set in this shell (keys exported in interactive-only profiles will not show here) — "
                       "ensure it is exported where the audits run; the key itself never goes in files")

    print()
    print("All good — ready to render, audit, and probe." if problems == 0
          else f"{problems} item(s) need attention (see FAIL lines).")
    sys.exit(0 if problems == 0 else 2)


if __name__ == "__main__":
    main()
