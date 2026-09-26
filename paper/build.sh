#!/usr/bin/env bash
set -e

# Change directory to paper/
cd "$(dirname "$0")"

# Remove stale build artifacts
rm -f main.aux main.bbl main.blg main.log main.out main.toc main.fls main.fdb_latexmk

# Prefer latexmk if available
if command -v latexmk >/dev/null 2>&1; then
    echo "Running latexmk..."
    if latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex > latexmk.log 2>&1; then
        echo "BUILD OK"
        exit 0
    else
        echo "BUILD FAILED"
        if [ -f main.log ]; then
            echo "First error from main.log:"
            grep -A 2 -m 1 "^!" main.log || true
        fi
        exit 1
    fi
else
    echo "latexmk not found, falling back to pdflatex -> bibtex -> pdflatex -> pdflatex..."

    # Pass 1: pdflatex
    if ! pdflatex -interaction=nonstopmode -halt-on-error main.tex > pdflatex_pass1.log 2>&1; then
        echo "BUILD FAILED"
        if [ -f main.log ]; then
            echo "First error from main.log:"
            grep -A 2 -m 1 "^!" main.log || true
        fi
        exit 1
    fi

    # Pass 2: bibtex (allow zero citations in initial skeleton)
    bibtex main > bibtex.log 2>&1 || true

    # Pass 3: pdflatex
    if ! pdflatex -interaction=nonstopmode -halt-on-error main.tex > pdflatex_pass2.log 2>&1; then
        echo "BUILD FAILED"
        if [ -f main.log ]; then
            echo "First error from main.log:"
            grep -A 2 -m 1 "^!" main.log || true
        fi
        exit 1
    fi

    # Pass 4: pdflatex final
    if ! pdflatex -interaction=nonstopmode -halt-on-error main.tex > pdflatex_pass3.log 2>&1; then
        echo "BUILD FAILED"
        if [ -f main.log ]; then
            echo "First error from main.log:"
            grep -A 2 -m 1 "^!" main.log || true
        fi
        exit 1
    fi

    echo "BUILD OK"
    exit 0
fi
