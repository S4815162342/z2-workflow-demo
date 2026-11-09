#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/report"
xelatex -interaction=nonstopmode -halt-on-error Z2_workflow_demo_report.tex
xelatex -interaction=nonstopmode -halt-on-error Z2_workflow_demo_report.tex
