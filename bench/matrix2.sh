#!/bin/bash
# Haiku comparison matrix: pipeline, pipeline with Argos drafts, local route (Argos + Ollama), Pulpit; one run at a time
cd "$(dirname "$0")/.."
mkdir bench/matrix.lock 2>/dev/null || { echo "another matrix is running"; exit 1; }
trap 'rmdir bench/matrix.lock' EXIT
PY=mcp/.venv/Scripts/python
for L in es pt; do $PY bench/run.py --arm pipeline --agent claude --model haiku --lang $L --talks 6; done
for L in es pt; do $PY bench/run.py --arm pipeline --draft --agent claude --model haiku --lang $L --talks 6; done
for L in es pt; do $PY bench/run.py --arm local --agent claude --model haiku --lang $L --talks 6; done
$PY bench/run.py --arm pulpit --agent claude --model haiku --lang es --talks 6
$PY bench/run.py --score
