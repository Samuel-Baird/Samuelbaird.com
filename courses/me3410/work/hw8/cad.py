"""HW 8 geometry (mm): the tutorial's pipe elbow with a second, identical flange at the free end.
Run with ../../../../.venv-cad/Scripts/python.exe cad.py

Dimensions from the tutorial (THERMAL-STRESS ANALYSIS TUTORIAL - PIPE ELBOW - V1):
  flange    OD 100, ID 50, 20 mm thick, four 10 mm bolt holes on the axes 40 mm from the centre (80 mm apart);
  pipe      OD 60, ID 50 (5 mm wall);
  path      sketch in the YZ plane: a 170 mm line, a 170 mm line at 90 deg and a R70 fillet between them,
            so each straight leg is 170 - 70 = 100 mm and the bend is a 90 deg arc of centreline radius 70.
Axes: flange 1 back face on z = 0 (centre at the origin), first leg along +Z, bend centre at (y, z) = (70, 100),
second leg along +Y in the plane z = 170, free end at y = 170. Flange 2 (HW 8) sits on the free end like
flange 1 sits on the start: y = 150..170, outer face on y = 170, bolt holes on the X and Z axes of that end.
"""
import math
from pathlib import Path

from build123d import Cylinder, Edge, Plane, Pos, Rot, Unit, Wire, Transition, export_step, sweep, Circle, Sketch

OUT = Path(__file__).parent / "assets"
D_FO, D_FI, T_F = 100.0, 50.0, 20.0      # flange
D_BOLT, R_BOLT = 10.0, 40.0
D_PO, D_PI = 60.0, 50.0                  # pipe
L_LEG, R_BEND = 100.0, 70.0              # straight leg, bend centreline radius
Z_END = L_LEG + R_BEND                   # 170: plane of the second leg
Y_END = R_BEND + L_LEG                   # 170: free end


def tube(length, d_out, d_in):
    return Cylinder(d_out / 2, length) - Cylinder(d_in / 2, length)


def flange():
    """Flange on the Z axis, z = 0..20."""
    f = Pos(0, 0, T_F / 2) * tube(T_F, D_FO, D_FI)
    for x, y in ((R_BOLT, 0), (-R_BOLT, 0), (0, R_BOLT), (0, -R_BOLT)):
        f -= Pos(x, y, T_F / 2) * Cylinder(D_BOLT / 2, 2 * T_F)
    return f


def path():
    """Pipe centreline in the YZ plane: 100 mm along +Z, R70 quarter arc, 100 mm along +Y."""
    a = Edge.make_line((0, 0, 0), (0, 0, L_LEG))
    b = Edge.make_three_point_arc((0, 0, L_LEG),
                                  (0, R_BEND * (1 - math.cos(math.pi / 4)), L_LEG + R_BEND * math.sin(math.pi / 4)),
                                  (0, R_BEND, Z_END))
    c = Edge.make_line((0, R_BEND, Z_END), (0, Y_END, Z_END))
    return Wire([a, b, c])


def elbow(second_flange=True):
    ring = Plane.XY * (Sketch() + Circle(D_PO / 2) - Circle(D_PI / 2))       # profile at the start of the path
    pipe = sweep(ring, path=path(), transition=Transition.ROUND)
    part = flange() + pipe
    if second_flange:
        # flange 1 rotated so its axis is +Y, outer face on y = 170 (flange occupies y = 150..170)
        part += Pos(0, Y_END, Z_END) * Rot(90, 0, 0) * flange()
    return part


def main():
    OUT.mkdir(exist_ok=True)
    p = elbow()
    bb = p.bounding_box()
    print("solids", len(p.solids()), "faces", len(p.faces()), "volume", round(p.volume, 1))
    print("bbox", bb.min, bb.max)
    # expected volume: two flanges + pipe outside the flanges (legs 80 mm each beyond the flange + bend)
    a_f = math.pi / 4 * (D_FO ** 2 - D_FI ** 2) - 4 * math.pi / 4 * D_BOLT ** 2
    a_p = math.pi / 4 * (D_PO ** 2 - D_PI ** 2)
    v = 2 * a_f * T_F + a_p * (2 * (L_LEG - T_F) + math.pi / 2 * R_BEND)
    print("expected volume", round(v, 1))
    for f in p.faces():
        c = f.center()
        print("  %-8s area %9.1f  centre (%6.1f %6.1f %6.1f)" % (f.geom_type.name, f.area, c.X, c.Y, c.Z))
    export_step(p, str(OUT / "elbow.step"), unit=Unit.MM)


if __name__ == "__main__":
    main()
