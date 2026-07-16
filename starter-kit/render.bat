@echo off
setlocal
rem Render a Markdown manuscript to .docx with citations + reference list (Windows).
rem Usage:  render.bat "My Draft.md" ["Optional Output.docx"]
rem Requires Pandoc (install the .msi from https://github.com/jgm/pandoc/releases, then open a NEW terminal).
rem Change citation style: replace style.csl with any style from zotero.org/styles (free).

set "HERE=%~dp0"
if "%~1"=="" (
  echo usage: render.bat ^<manuscript.md^> [out.docx]
  exit /b 1
)
set "IN=%~1"
set "OUT=%~2"
if "%OUT%"=="" set "OUT=%~dpn1.docx"

pandoc "%IN%" --citeproc --bibliography="%HERE%library.bib" --csl="%HERE%style.csl" -o "%OUT%"
if errorlevel 1 exit /b 1
echo rendered -^> %OUT%
