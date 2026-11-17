"""In-class tutorial 10-28, problem 2 (bonus): long pressurized concrete block with a circular cavity.
Run with ../../../../.venv-cad/Scripts/python.exe cad.py

Cross-section in the XY plane (mm), origin at the bottom-left corner (handout "PLANE STRAIN-STRESS TUTORIAL - V2"):
  bottom 0..400 at y = 0; left edge x = 0, height 200; left top y = 200 for x 0..150;
  step down at x = 150 to the right top y = 100, with an R20 fillet in the inside corner
  (tangent points (150, 120) and (170, 100), centre (170, 120)); right edge x = 400, height 100.
  The right top edge is split at x = 250: the 25 MPa load acts on the last 150 mm (x 250..400), as drawn.
  Bolt hole: diameter 50, centre 100 mm from the y-axis and 50 mm from the x-axis, i.e. (100, 50).
Out of plane the block is 500 mm long (plane strain in ANSYS).

Writes assets/block_R<r>.step for the fillet-radius study, assets/block_nohole.step (R20, no hole) for the
nominal stress field at the hole location, and assets/concrete_handout.xml (the handout's concrete).
"""
import math
import re
import uuid
from pathlib import Path

from build123d import Edge, Face, Line, Plane, ThreePointArc, Unit, Wire, export_step

OUT = Path(__file__).parent / "assets"
L, H_L, H_R, X_STEP, X_LOAD2 = 400.0, 200.0, 100.0, 150.0, 250.0
HOLE_C, HOLE_D = (100.0, 50.0), 50.0
RADII = [5.0, 10.0, 20.0, 30.0, 40.0]
MATXML = Path(r"C:\Program Files\ANSYS Inc\ANSYS Student\v261\Addins\EngineeringData\Samples\General_Materials.xml")
CONCRETE = dict(E=30e9, nu=0.20, Sc=40e6, St=3e6, alpha=1.0e-5)   # handout values (SI)


def outline(r):
    a, b = (X_STEP + r, H_R), (X_STEP, H_R + r)
    c = (X_STEP + r - r * math.cos(math.pi / 4), H_R + r - r * math.sin(math.pi / 4))
    edges = [Line((0, 0), (L, 0)), Line((L, 0), (L, H_R)), Line((L, H_R), (X_LOAD2, H_R)),
             Line((X_LOAD2, H_R), a), ThreePointArc(a, c, b), Line(b, (X_STEP, H_L)),
             Line((X_STEP, H_L), (0, H_L)), Line((0, H_L), (0, 0))]
    return Wire(edges)


def block(r, hole=True):
    outer = outline(r)
    if not hole:
        return Face(outer)
    circ = Wire([Edge.make_circle(HOLE_D / 2, Plane((HOLE_C[0], HOLE_C[1], 0)))])
    return Face(outer, [circ])


def area(r, hole=True):
    a = X_STEP * H_L + (L - X_STEP) * H_R + r ** 2 - math.pi * r ** 2 / 4
    return a - (math.pi * HOLE_D ** 2 / 4 if hole else 0.0)


def concrete_xml():
    """General_Materials.xml with only Concrete, renamed and set to the handout's properties."""
    x = MATXML.read_text(encoding="utf-8")
    mats = re.findall(r"      <Material>.*?</Material>\n", x, re.S)
    conc = [m for m in mats if "<Name>Concrete</Name>" in m][0]
    E, nu = CONCRETE["E"], CONCRETE["nu"]

    def setp(block, pa, val):
        new, n = re.subn(r'(<ParameterValue parameter="%s" format="float">\s*<Data>)[^<]*(</Data>)' % pa,
                         lambda m: m.group(1) + repr(float(val)) + m.group(2), block)
        assert n >= 1, pa
        return new

    conc = conc.replace("<Name>Concrete</Name>\n          <Class>", "<Name>Concrete (handout)</Name>\n          <Class>", 1)
    for pa, v in (("pa19", E), ("pa20", nu), ("pa21", E / (3 * (1 - 2 * nu))), ("pa22", E / (2 * (1 + nu))),
                  ("pa4", CONCRETE["Sc"]), ("pa12", CONCRETE["St"]), ("pa10", CONCRETE["alpha"])):
        conc = setp(conc, pa, v)
    conc = re.sub(r'(<Qualifier name="guid">)[^<]*(</Qualifier>)', lambda m: m.group(1) + str(uuid.uuid4()) + m.group(2), conc)
    head = x[:x.index("      <Material>")]
    tail = x[x.index("      <Metadata>"):]
    (OUT / "concrete_handout.xml").write_text(head + conc + tail, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    for r in RADII:
        f = block(r)
        export_step(f, str(OUT / f"block_R{r:g}.step"), unit=Unit.MM)
        print(f"R{r:g}: area {f.area:.3f} expected {area(r):.3f}, edges {len(f.edges())}")
    f = block(20.0, hole=False)
    export_step(f, str(OUT / "block_nohole.step"), unit=Unit.MM)
    print(f"no hole: area {f.area:.3f} expected {area(20.0, False):.3f}, edges {len(f.edges())}")
    concrete_xml()
    print("wrote", OUT / "concrete_handout.xml")


if __name__ == "__main__":
    main()
