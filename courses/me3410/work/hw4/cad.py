"""HW 4 truss geometry (written in mm): four line members as one compound so Mechanical imports one
line body and the members share nodes at the joints.

Joints: 1 (0, 0), 2 (1.5, 0), 3 (0, 1), 4 (1.5, 1). Members: 1-2, 2-3, 3-4, 2-4.
Run with ../../../../.venv-cad/Scripts/python.exe cad.py
"""
from pathlib import Path

from build123d import Edge, Shape, Unit, export_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

OUT = Path(__file__).parent / "assets"
# Coordinates in mm: the OCCT STEP writer labels lengths as millimetres.
J = {1: (0.0, 0.0, 0.0), 2: (1500.0, 0.0, 0.0), 3: (0.0, 1000.0, 0.0), 4: (1500.0, 1000.0, 0.0)}
MEMBERS = [(1, 2), (2, 3), (3, 4), (2, 4)]


def main():
    OUT.mkdir(exist_ok=True)
    edges = [Edge.make_line(J[a], J[b]) for a, b in MEMBERS]
    # Fuse the edges so coincident joints become shared vertices (one connected line body).
    shape = edges[0].wrapped
    for e in edges[1:]:
        shape = BRepAlgoAPI_Fuse(shape, e.wrapped).Shape()
    comp = Shape.cast(shape)
    # Write the fused shape as ONE STEP product (build123d's exporter splits a compound into
    # one product per edge, which Mechanical imports as four unconnected bodies).
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    assert w.Write(str(OUT / "truss.step")) == IFSelect_RetDone
    _unused = (export_step, Unit)
    print("edges", len(comp.edges()), "vertices", len(comp.vertices()),
          "lengths", [round(e.length, 4) for e in comp.edges()])


if __name__ == "__main__":
    main()
