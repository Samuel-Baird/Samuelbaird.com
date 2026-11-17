"""Test 1 line-body geometry, one STEP per question (written in mm: the OCCT STEP writer labels
lengths as millimetres). Each member/segment is its own edge; ANSYS imports every edge as a line
body and ansys_q*.py joins them at the joints with node merges.

  Q1 stepped shaft (in): nodes 1 (0), 2 (12), 3 (21), 4 (29); element 1 is split at x = 6 in so the
     midpoint displacement can be probed.
  Q2 truss (m): A(0,0) B(1.5,0) C(3,0) D(4.5,0) E(6,0) H(1.5,1) G(3,2) J(4.5,1), 13 members.
  Q3 beam (in): supports at 0 and 44, loads at 16 and 28, midspan vertex at 22.

Run with ../../../../.venv-cad/Scripts/python.exe cad.py
"""
from pathlib import Path

from build123d import Edge, Shape
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

OUT = Path(__file__).parent / "assets"
IN = 25.4

Q1_X = [0.0, 6.0, 12.0, 21.0, 29.0]                       # in
Q2_J = {"A": (0.0, 0.0), "B": (1.5, 0.0), "C": (3.0, 0.0), "D": (4.5, 0.0), "E": (6.0, 0.0),
        "H": (1.5, 1.0), "G": (3.0, 2.0), "J": (4.5, 1.0)}  # m
Q2_M = ["AB", "BC", "CD", "DE", "AH", "HG", "GJ", "JE", "BH", "CG", "DJ", "HC", "CJ"]
Q3_X = [0.0, 16.0, 22.0, 28.0, 44.0]                      # in


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


def main():
    OUT.mkdir(exist_ok=True)
    write([Edge.make_line((a * IN, 0, 0), (b * IN, 0, 0)) for a, b in zip(Q1_X, Q1_X[1:])], "q1_shaft.step")
    mm = {k: (x * 1000, y * 1000, 0.0) for k, (x, y) in Q2_J.items()}
    write([Edge.make_line(mm[m[0]], mm[m[1]]) for m in Q2_M], "q2_truss.step")
    write([Edge.make_line((a * IN, 0, 0), (b * IN, 0, 0)) for a, b in zip(Q3_X, Q3_X[1:])], "q3_beam.step")


if __name__ == "__main__":
    main()
