"""Run a Mechanical script against ANSYS Student 2026 R1 through PyMechanical.

Run with the PyMechanical venv (it has ansys-mechanical-core):
  MECHPY=~/.mcp-servers/pymechanical-mcp/venv/Scripts/python.exe
  $MECHPY scripts/mech.py <script.py> [--var NAME=VALUE ...] [--port 10000] [--new]

The script body runs *inside* Mechanical (ExtAPI, Model, DataModel, Quantity...).
`--var` values are injected as Python string assignments at the top of the script,
so a script can read e.g. OUT_DIR. The last expression's value is printed.
Connects to a running instance on --port if there is one, otherwise launches a
batch instance (and leaves it running for the next call unless --exit).
"""
import argparse
import sys
from pathlib import Path

import ansys.mechanical.core as pymech

EXE = r"C:\Program Files\ANSYS Inc\ANSYS Student\v261\aisol\bin\winx64\AnsysWBU.exe"


def get_app(port: int, new: bool):
    if not new:
        try:
            return pymech.Mechanical(ip="127.0.0.1", port=port), False
        except Exception:
            pass
    return pymech.launch_mechanical(exec_file=EXE, batch=True, port=port, cleanup_on_exit=False), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--var", action="append", default=[])
    ap.add_argument("--port", type=int, default=10000)
    ap.add_argument("--new", action="store_true")
    ap.add_argument("--exit", action="store_true")
    ap.add_argument("--lib", action="append", default=[], help="file(s) prepended before the script")
    a = ap.parse_args()
    head = []
    for kv in a.var:
        k, v = kv.split("=", 1)
        head.append(f"{k} = {v!r}")
    libs = [Path(p).read_text(encoding="utf-8") for p in a.lib]
    # Lines "#%% split" cut the script into phases run as separate calls. Globals persist
    # between calls, and Mechanical refreshes object states (e.g. formula loads) in between.
    chunks = Path(a.script).read_text(encoding="utf-8").split("\n#%% split")
    chunks[0] = "\n".join(head + libs) + "\n" + chunks[0]
    app, launched = get_app(a.port, a.new)
    try:
        for i, chunk in enumerate(chunks):
            out = app.run_python_script(chunk, enable_logging=True)
            if out:
                print(out if i == len(chunks) - 1 else f"[phase {i + 1}] {out}")
    except Exception as e:  # show Mechanical-side errors plainly
        print("MECHANICAL ERROR:", e, file=sys.stderr)
        sys.exit(1)
    finally:
        if a.exit:
            app.exit()


if __name__ == "__main__":
    main()
