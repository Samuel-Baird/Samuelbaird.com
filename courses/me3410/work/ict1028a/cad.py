"""In-class tutorial 10-28, problem 1: geometry (mm). Run with ../../../../.venv-cad/Scripts/python.exe cad.py

Stepped flat plate from the instructor's 10-28 notes, in the XY plane, origin at the bottom-left corner:
  deep block x 0..120, y 0..100 (fixed to the wall along x = 0);
  arm x 120..250, y 0..40 (bottom edge flush with the block);
  R25 fillet at the inside corner (120, 40): tangent points (120, 65) and (145, 40), centre (145, 65).
Thickness 5 mm (plane stress input in ANSYS).
"""
import math
from pathlib import Path

from build123d import Pos, Rectangle, Sketch, Unit, export_step, fillet

OUT = Path(__file__).parent / "assets"
L, D, d, L1, R = 250.0, 100.0, 40.0, 120.0, 25.0


def plate():
    sk = Sketch() + Pos(L1 / 2, D / 2) * Rectangle(L1, D)            # deep block
    sk += Pos(L / 2, d / 2) * Rectangle(L, d)                          # arm (overlaps the block)
    inner = [v for v in sk.vertices() if abs(v.X - L1) < 1e-6 and abs(v.Y - d) < 1e-6]
    assert len(inner) == 1, inner
    return fillet(inner, radius=R)


def expected_area():
    return L1 * D + (L - L1) * d + R ** 2 - math.pi * R ** 2 / 4


def main():
    OUT.mkdir(exist_ok=True)
    face = plate().faces()[0]
    export_step(face, str(OUT / "stepped_plate.step"), unit=Unit.MM)
    print("area", round(face.area, 3), "expected", round(expected_area(), 3))
    bb = face.bounding_box()
    print("bbox", bb.min, bb.max)


if __name__ == "__main__":
    main()
