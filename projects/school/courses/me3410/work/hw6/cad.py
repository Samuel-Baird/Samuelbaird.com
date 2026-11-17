"""HW 6 geometry (mm). Run with ../../../../.venv-cad/Scripts/python.exe cad.py

L-shaped bracket from the handout figure, in the XY plane, origin at the top-left corner
(top edge y = 0, wall edge x = 0, y down is negative):
  horizontal arm 40 mm deep (top edge 0..200 mm), right end a R20 semicircle about the hole (200, -20);
  vertical arm 40 mm wide down to y = -120, bottom end a R20 semicircle about the hole (20, -120);
  R50 fillet at the inner corner (tangent points (90, -40) and (40, -90));
  three 10 mm holes at (20, -20), (200, -20), (20, -120). Thickness 2 mm (plane stress input in ANSYS).
"""
import math
from pathlib import Path

from build123d import Circle, Pos, Rectangle, Sketch, Unit, export_step, fillet

OUT = Path(__file__).parent / "assets"
ARM, L, H, R_FIL, D_HOLE = 40.0, 200.0, 120.0, 50.0, 10.0
HOLES = [(20.0, -20.0), (200.0, -20.0), (20.0, -120.0)]


def bracket():
    sk = Sketch() + Pos(L / 2, -ARM / 2) * Rectangle(L, ARM)       # horizontal arm, x 0..200
    sk += Pos(ARM / 2, -H / 2) * Rectangle(ARM, H)                  # vertical arm, y 0..-120
    sk += Pos(L, -ARM / 2) * Circle(ARM / 2)                        # right rounded end
    sk += Pos(ARM / 2, -H) * Circle(ARM / 2)                        # bottom rounded end
    inner = [v for v in sk.vertices() if abs(v.X - ARM) < 1e-6 and abs(v.Y + ARM) < 1e-6]
    assert len(inner) == 1, inner
    sk = fillet(inner, radius=R_FIL)
    for x, y in HOLES:
        sk -= Pos(x, y) * Circle(D_HOLE / 2)
    return sk


def expected_area():
    a = L * ARM + ARM * (H - ARM)                     # two arms (overlap counted once)
    a += 2 * (math.pi * (ARM / 2) ** 2 / 2)           # two semicircular ends
    a += R_FIL ** 2 - math.pi * R_FIL ** 2 / 4        # fillet adds the square-minus-quarter-circle
    a -= 3 * math.pi * (D_HOLE / 2) ** 2
    return a


def main():
    OUT.mkdir(exist_ok=True)
    sk = bracket()
    face = sk.faces()[0]
    export_step(face, str(OUT / "bracket_2d.step"), unit=Unit.MM)
    print("faces", len(sk.faces()), "area", round(face.area, 3), "expected", round(expected_area(), 3))
    bb = face.bounding_box()
    print("bbox", bb.min, bb.max)


if __name__ == "__main__":
    main()
