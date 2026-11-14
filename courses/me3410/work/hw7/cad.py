"""HW 7 geometry (inches). Run with ../../../../.venv-cad/Scripts/python.exe cad.py

Q1: equilateral triangle plate, side 8, t = 1, centre hole D = 3.5, three d = 0.5 holes on
    radius 3.5 from the centre toward the vertices (C at top, A bottom-left, B bottom-right).
    2D: face in the XY plane. 3D: extruded to z = -0.5 .. 0.5 (mid-plane at z = 0).
Q2: spherical vessel, inner diameter 75, wall 2. Axisymmetric quarter section in the XY plane
    (x >= 0 radial, y = axis of symmetry): annulus between r = 37.5 and r = 39.5, first quadrant.
"""
import math
from pathlib import Path

from build123d import (Circle, Plane, Polygon, Pos, Sketch, Unit, export_step, extrude, Face, Wire, Edge,
                       Vector)

OUT = Path(__file__).parent / "assets"
SIDE, T, D_BIG, D_PIN, R_PIN = 8.0, 1.0, 3.5, 0.5, 3.5
RI, RO = 37.5, 39.5


def vertex(angle_deg, r):
    a = math.radians(angle_deg)
    return (r * math.cos(a), r * math.sin(a))


def triangle_sketch():
    rc = SIDE / math.sqrt(3)  # circumradius
    verts = [vertex(90, rc), vertex(210, rc), vertex(330, rc)]
    sk = Sketch() + Polygon(*verts, align=None)
    sk -= Circle(D_BIG / 2)
    for ang in (90, 210, 330):  # C, A, B
        sk -= Pos(*vertex(ang, R_PIN)) * Circle(D_PIN / 2)
    return sk


def main():
    OUT.mkdir(exist_ok=True)
    sk = triangle_sketch()
    face2d = sk.faces()[0]
    export_step(face2d, str(OUT / "q1_plate_2d.step"), unit=Unit.IN)
    solid = extrude(Plane.XY.offset(-T / 2) * sk, amount=T)
    export_step(solid, str(OUT / "q1_plate_3d.step"), unit=Unit.IN)
    # Q2 quarter annulus, x >= 0, y >= 0
    outer = Edge.make_circle(RO, start_angle=0, end_angle=90)
    inner = Edge.make_circle(RI, start_angle=0, end_angle=90)
    w = Wire([Edge.make_line((RI, 0, 0), (RO, 0, 0)), outer,
              Edge.make_line((0, RO, 0), (0, RI, 0)), inner.reversed() if hasattr(inner, "reversed") else inner])
    ring = Face(w)
    export_step(ring, str(OUT / "q2_sphere_axisym.step"), unit=Unit.IN)
    print("plate area", round(face2d.area, 4), "solid vol", round(solid.volume, 4), "ring area", round(ring.area, 3),
          "expected ring", round(math.pi / 4 * (RO ** 2 - RI ** 2), 3))


if __name__ == "__main__":
    main()
