#!/bin/bash
# the full benchmark matrix, one run at a time so wall times are not skewed by each other
cd "$(dirname "$0")/.."
mkdir bench/matrix.lock 2>/dev/null || { echo "another matrix is running"; exit 1; }
trap 'rmdir bench/matrix.lock' EXIT
PY=mcp/.venv/Scripts/python
for L in es pt; do $PY bench/run.py --arm pipeline --agent claude --model haiku --lang $L --talks 6; done
for L in es pt; do $PY bench/run.py --arm pipeline --agent codex --lang $L --talks 3; done
for L in es pt; do $PY bench/run.py --arm pulpit --agent claude --model haiku --lang $L --talks 6; done
$PY bench/run.py --score
