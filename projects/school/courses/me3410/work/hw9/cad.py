"""HW 9 geometry (mm). Run with ../../../../.venv-cad/Scripts/python.exe cad.py

Q1  rotating part (handout sketch). Half cross-section in the (r, z) plane, r >= 5:
      hub   r 5..13,  z -15..15   (bore R5, hub 30 mm tall)
      web   r 13..30, z -6..6     (12 mm thick)
      rim   r 30..46, z -25..25   (50 mm tall, 16 mm wide)
    q1_axisym.step : that face in the XY plane (x = r, y = axis of rotation, as Mechanical's 2D axisymmetric wants).
    q1_3d.step     : the same profile revolved 360 deg about Z.
Q2  lifting bracket (handout + DesignModeler hints); y up, load along +Y, bottom face y = -30 fixed.
      base   x +-60 (12 cm), z +-100 (20 cm), y -30..0, R17.5 corners, four d20 holes at x = +-30, z = +-60
      lug    profile in XY: base (+-60, 0) to (+-30, 80), R30 arc about (0, 80), d30 hole; thickness 30 (z +-15)
    q2_full.step, q2_half.step (z >= 0, symmetry plane z = 0).
"""
import math
from pathlib import Path

from build123d import (Axis, Box, Cylinder, Edge, Face, Plane, Pos, Rot, Unit, Wire, export_step, extrude, fillet,
                       revolve)

OUT = Path(__file__).parent / "assets"

# ---- Q1
R_BORE, R_HUB, R_WEB, R_RIM = 5.0, 13.0, 30.0, 46.0
H_HUB, T_WEB, H_RIM = 30.0, 12.0, 50.0


def q1_pts():
    h, w, r = H_HUB / 2, T_WEB / 2, H_RIM / 2
    return [(R_BORE, -h), (R_HUB, -h), (R_HUB, -w), (R_WEB, -w), (R_WEB, -r), (R_RIM, -r),
            (R_RIM, r), (R_WEB, r), (R_WEB, w), (R_HUB, w), (R_HUB, h), (R_BORE, h)]


def poly_face(pts, plane):
    es = [Edge.make_line(tuple(plane.from_local_coords(a)), tuple(plane.from_local_coords(b)))
          for a, b in zip(pts, pts[1:] + pts[:1])]
    return Face(Wire(es))


# ---- Q2
BX, BZ, BT, RF = 60.0, 100.0, 30.0, 17.5
HX, HZ, HR = 30.0, 60.0, 10.0
LUG_Y, LUG_R, HOLE_R, TH = 80.0, 30.0, 15.0, 30.0


def bracket():
    base = Pos(0, -BT / 2, 0) * Box(2 * BX, BT, 2 * BZ)
    corners = [e for e in base.edges().filter_by(Axis.Y)]
    assert len(corners) == 4
    base = fillet(corners, radius=RF)
    for sx in (-1, 1):
        for sz in (-1, 1):
            base -= Pos(sx * HX, -BT / 2, sz * HZ) * Cylinder(HR, 3 * BT, rotation=(90, 0, 0))
    a = (-BX, 0.0, 0.0), (BX, 0.0, 0.0)
    p1, p2 = (HX, LUG_Y, 0.0), (-HX, LUG_Y, 0.0)
    es = [Edge.make_line(a[0], a[1]), Edge.make_line(a[1], p1),
          Edge.make_three_point_arc(p1, (0.0, LUG_Y + LUG_R, 0.0), p2), Edge.make_line(p2, a[0])]
    prof = Face(Wire(es))
    lug = Pos(0, 0, -TH / 2) * extrude(prof, amount=TH)
    lug -= Pos(0, LUG_Y, 0) * Cylinder(HOLE_R, 3 * TH)
    return base + lug


def main():
    OUT.mkdir(exist_ok=True)
    f = poly_face(q1_pts(), Plane.XY)
    export_step(f, str(OUT / "q1_axisym.step"), unit=Unit.MM)
    # revolve about Z: profile in the XZ plane
    fz = poly_face(q1_pts(), Plane.XZ)
    solid = revolve(fz, axis=Axis.Z, revolution_arc=360)
    export_step(solid, str(OUT / "q1_3d.step"), unit=Unit.MM)
    quarter = revolve(fz, axis=Axis.Z, revolution_arc=90)       # 0..90 deg wedge: cut faces on y = 0 and x = 0
    export_step(quarter, str(OUT / "q1_3d_quarter.step"), unit=Unit.MM)
    print("Q1 quarter volume", round(quarter.volume, 1), "faces", len(quarter.faces()))
    area = f.area
    print("Q1 face area", round(area, 2), "solid volume", round(solid.volume, 1), "faces", len(solid.faces()))
    # Pappus check
    cx = f.center().X
    print("  Pappus 2*pi*xbar*A =", round(2 * math.pi * cx * area, 1), "xbar", round(cx, 3))

    full = bracket()
    export_step(full, str(OUT / "q2_full.step"), unit=Unit.MM)
    half = full & Pos(0, 0, 200) * Box(1000, 1000, 400)    # z >= 0
    export_step(half, str(OUT / "q2_half.step"), unit=Unit.MM)
    print("Q2 full: solids", len(full.solids()), "faces", len(full.faces()), "vol", round(full.volume, 1),
          "bbox", full.bounding_box().min, full.bounding_box().max)
    print("Q2 half: solids", len(half.solids()), "faces", len(half.faces()), "vol", round(half.volume, 1))


if __name__ == "__main__":
    main()
