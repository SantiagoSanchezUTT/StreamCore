#!/usr/bin/env bash
set -euo pipefail

# Run tests locally and produce reports in tests/results
mkdir -p tests/results
pytest "$@" --junitxml=tests/results/junit.xml --cov=. --cov-report=xml:tests/results/coverage.xml --cov-report=html:tests/results/htmlcov
echo "Resultados en tests/results/ (junit/coverage/html)"