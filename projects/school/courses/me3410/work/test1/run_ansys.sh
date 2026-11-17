#!/usr/bin/env bash
# Run one Test 1 Mechanical script: bash run_ansys.sh ansys_q1.py
# Mechanical's geometry import and image export reject paths with spaces ("AI projects"), so
# assets and outputs go through a space-free temp folder and are copied back to ansys_out/.
set -euo pipefail
cd "$(dirname "$0")"
TMP="$(cygpath -m "${LOCALAPPDATA:-$HOME/AppData/Local}")/Temp/me3410_test1"
mkdir -p "$TMP/assets" "$TMP/out" ansys_out
cp assets/* "$TMP/assets/"
MECHPY=~/.mcp-servers/pymechanical-mcp/venv/Scripts/python.exe
$MECHPY ../../../../scripts/mech.py "$1" --lib ../../pipeline/mech_common.py --lib line_common.py \
  --var "ASSETS=$TMP/assets" --var "OUT=$TMP/out"
cp "$TMP"/out/* ansys_out/
