#!/usr/bin/env bash
set -euo pipefail
# Render a Markdown manuscript to a .docx with in-text citations + reference list resolved.
# Pipeline: Zotero -> Better BibTeX (library.bib) -> Pandoc --citeproc + a CSL style (style.csl).
#
# Usage:  bash render.sh "path/to/Draft.md"  ["Optional Output.docx"]
# Cite in the .md with [@citekey]; narrative form: @citekey .
# Any [@key] not in the library renders as (key?) and prints a WARNING — that is the orphan check.
#
# Change citation style: replace style.csl with any style from zotero.org/styles (free).

HERE="$(cd "$(dirname "$0")" && pwd)"                          # this folder (holds library.bib + style.csl)
PANDOC="${PANDOC:-$(command -v pandoc || echo "$HOME/.local/bin/pandoc")}"  # PATH first, then ~/.local/bin
IN="${1:?usage: render.sh <manuscript.md> [out.docx]}"
OUT="${2:-${IN%.*}.docx}"

"$PANDOC" "$IN" --citeproc \
  --bibliography="$HERE/library.bib" \
  --csl="$HERE/style.csl" \
  -o "$OUT"
echo "rendered -> $OUT"
