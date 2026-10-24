#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "======================================================================"
echo "Starting ReclaimAI 5-Agent Architecture"
echo "======================================================================"

if [ -d ".venv" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

$PYTHON_BIN run_bureau.py
