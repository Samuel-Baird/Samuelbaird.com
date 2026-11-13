"""Spar A (I-section) geometry for Term Project Part I.

Run with the CAD venv:  ../../../../.venv-cad/Scripts/python.exe cad.py
Writes assets/spar_a_constant.step and assets/spar_a_tapered.step (mm).
Axes: x = span (root at x=0), y = flapwise (up), z = chordwise.

The bottom flange is built as two halves (z<0, z>0) and fused without cleaning, so its
lower face stays split along z=0. Mechanical only takes single-variable load formulas,
so the eccentric load case (LC2) is applied as two x-only pressures, one per half.
"""
from pathlib import Path

from build123d import Plane, Pos, Rectangle, export_step, extrude, loft

H, B, TF, TW, L = 60.0, 55.0, 6.0, 4.0, 1500.0
S_TIP = 0.625
OUT = Path(__file__).parent / "assets"


def pieces(s: float, x: float):
    """Faces of the I-section at station x, scaled by s: top flange, web, two bottom halves."""
    h, b, tf, tw = H * s, B * s, TF * s, TW * s
    pl = Plane.YZ.offset(x)  # local x -> global +Y, local y -> global +Z
    yc = h / 2 - tf / 2
    return [
        pl * (Pos(yc, 0) * Rectangle(tf, b)),
        pl * Rectangle(h - 2 * tf, tw),
        pl * (Pos(-yc, -b / 4) * Rectangle(tf, b / 2)),
        pl * (Pos(-yc, b / 4) * Rectangle(tf, b / 2)),
    ]


def fuse_keep_faces(solids):
    """Raw OCCT fuse (no face unification), so the split bottom face survives."""
    from build123d import Shape
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

    shape = solids[0].wrapped
    for s in solids[1:]:
        shape = BRepAlgoAPI_Fuse(shape, s.wrapped).Shape()
    return Shape.cast(shape)


def main():
    OUT.mkdir(exist_ok=True)
    root = pieces(1.0, 0.0)
    const = fuse_keep_faces([extrude(f, amount=L) for f in root])
    tip = pieces(S_TIP, L)
    taper = fuse_keep_faces([loft([a, b], ruled=True) for a, b in zip(root, tip)])
    for name, part in (("constant", const), ("tapered", taper)):
        solids = part.solids()
        down = [f for f in part.faces() if f.normal_at().Y < -0.9 and f.center().Y < -20]
        print(name, "solids", len(solids), "volume", round(part.volume, 1),
              "bottom faces", len(down), "faces", len(part.faces()))
        export_step(part, str(OUT / f"spar_a_{name}.step"))


if __name__ == "__main__":
    main()
