#!/usr/bin/env bash
cd "$(dirname "$0")"
SCRIPT=ansys_q1.py bash run_ansys.sh --new > q1_run.log 2>&1
SCRIPT=ansys_q1_3d.py bash run_ansys.sh > q1_3d_run.log 2>&1
echo done > q1_done.flag
