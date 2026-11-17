"""HW 5 beam geometry: one line body along +X, 15 ft (180 in), with vertices at the roller
(x = 10 ft) and at the 500 lb load (x = 12.5 ft, mid-element 2) so supports and loads can be
scoped to vertices. Written in mm (the OCCT STEP writer labels lengths as millimetres).

Run with ../../../../.venv-cad/Scripts/python.exe cad.py
"""
from pathlib import Path

from build123d import Edge, Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

OUT = Path(__file__).parent / "assets"
IN = 25.4
X_IN = [0.0, 120.0, 150.0, 180.0]   # wall, roller, 500 lb load, free end


def main():
    OUT.mkdir(exist_ok=True)
    edges = [Edge.make_line((a * IN, 0, 0), (b * IN, 0, 0)) for a, b in zip(X_IN, X_IN[1:])]
    # One wire (one line body, three edges sharing vertices): a fused compound of edges
    # imports as three unconnected parts.
    mw = BRepBuilderAPI_MakeWire()
    for e in edges:
        mw.Add(e.wrapped)
    shape = mw.Wire()
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    assert w.Write(str(OUT / "beam.step")) == IFSelect_RetDone
    comp = Shape.cast(shape)
    print("edges", len(comp.edges()), "vertices", len(comp.vertices()),
          "lengths (in)", [round(e.length / IN, 4) for e in comp.edges()])


if __name__ == "__main__":
    main()
