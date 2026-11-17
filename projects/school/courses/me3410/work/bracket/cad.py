"""In-class tutorial (3D bracket): geometry (mm). Run with ../../../../.venv-cad/Scripts/python.exe cad.py

Axes as in the handout figure: X along the 60 mm front edge, Y up, Z toward the front (the viewer).
  base plate     x 0..60, y 0..10, z 0..50 (bottom face y = 0 is fixed);
  upright        x 0..60, y 0..100, z 0..10 (back edge of the base), top corners R20;
  bearing hole   dia 30, axis along Z, centre (30, 70);
  inside fillet  R10 where the upright meets the base (edge at y = 10, z = 10);
  bolt holes     dia 10, axis along Y, 15 mm from the front edge and from the side edges: (15, z = 35), (45, z = 35).
Thickness 10 mm everywhere.
"""
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Pos, Rot, Unit, export_step, fillet

OUT = Path(__file__).parent / "assets"
W, H, D, T = 60.0, 100.0, 50.0, 10.0
R_TOP, R_IN = 20.0, 10.0
D_BEAR, Y_BEAR = 30.0, 70.0
D_BOLT, E_BOLT = 10.0, 15.0
LO = (Align.MIN, Align.MIN, Align.MIN)


def bracket():
    base = Box(W, T, D, align=LO)
    upright = Box(W, H, T, align=LO)
    part = base + upright
    # top corners of the upright: edges parallel to Z at (0, 100) and (60, 100)
    top = [e for e in part.edges().filter_by(Axis.Z) if abs(e.center().Y - H) < 1e-6]
    assert len(top) == 2, top
    part = fillet(top, radius=R_TOP)
    # inside corner where the upright meets the base: edge parallel to X at y = 10, z = 10
    inner = [e for e in part.edges().filter_by(Axis.X)
             if abs(e.center().Y - T) < 1e-6 and abs(e.center().Z - T) < 1e-6]
    assert len(inner) == 1, inner
    part = fillet(inner, radius=R_IN)
    part -= Pos(W / 2, Y_BEAR, T / 2) * Cylinder(D_BEAR / 2, 3 * T)                      # axis along Z
    for x in (E_BOLT, W - E_BOLT):
        part -= Pos(x, T / 2, D - E_BOLT) * Rot(90, 0, 0) * Cylinder(D_BOLT / 2, 3 * T)  # axis along Y
    return part


def main():
    OUT.mkdir(exist_ok=True)
    p = bracket()
    export_step(p, str(OUT / "bracket.step"), unit=Unit.MM)
    bb = p.bounding_box()
    print("solids", len(p.solids()), "faces", len(p.faces()), "volume", round(p.volume, 2))
    print("bbox", bb.min, bb.max)
    print("cyl faces", sorted(round(f.area, 2) for f in p.faces() if f.geom_type.name == "CYLINDER"))


if __name__ == "__main__":
    main()
