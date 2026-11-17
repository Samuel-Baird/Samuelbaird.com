"""In-class tutorial (1D / truss / beam) line-body geometry, one STEP per question (written in mm: the
OCCT STEP writer labels lengths as millimetres). Each segment is its own edge; ANSYS imports every edge
as a line body and ansys_q*.py joins them with node merges (work/test1/line_common.py).

  Q1 stepped shaft (in): walls at 0 and 22, load point B at 10; D (4) and F (17) are probe points.
  Q2 two-bar truss (in): supports 1 (0, 0) and 2 (36, 0), apex A (18, 36 sin 60) with 36 in members.
  Q3 overhanging beam (in): pin A (0), roller B (180), load at C (228); vertex at L/sqrt(3), where the
     upward deflection of span AB peaks.

Run with ../../../../.venv-cad/Scripts/python.exe cad.py
"""
import math
from pathlib import Path

from build123d import Edge, Shape
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

OUT = Path(__file__).parent / "assets"
IN = 25.4

Q1_X = [0.0, 4.0, 10.0, 17.0, 22.0]
Q2_J = {"1": (0.0, 0.0), "A": (18.0, 36.0 * math.sin(math.radians(60))), "2": (36.0, 0.0)}
Q2_M = ["1A", "A2"]
Q3_X = [0.0, 180.0 / math.sqrt(3), 180.0, 228.0]


def write(edges, name):
    shape = edges[0].wrapped
    for e in edges[1:]:
        shape = BRepAlgoAPI_Fuse(shape, e.wrapped).Shape()
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    assert w.Write(str(OUT / name)) == IFSelect_RetDone
    comp = Shape.cast(shape)
    print(name, "edges", len(comp.edges()), "vertices", len(comp.vertices()))


def line_x(xs):
    return [Edge.make_line((a * IN, 0, 0), (b * IN, 0, 0)) for a, b in zip(xs, xs[1:])]


def main():
    OUT.mkdir(exist_ok=True)
    write(line_x(Q1_X), "q1_shaft.step")
    mm = {k: (x * IN, y * IN, 0.0) for k, (x, y) in Q2_J.items()}
    write([Edge.make_line(mm[m[0]], mm[m[1]]) for m in Q2_M], "q2_truss.step")
    write(line_x(Q3_X), "q3_beam.step")


if __name__ == "__main__":
    main()
