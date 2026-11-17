"""Write assets/ict1_materials.xml: the Q2 aluminum (E = 10x10^6 psi, as given) and the Q3 steel
(E = 29x10^6 psi, as given). Q1 uses ANSYS's default Structural Steel, as the handout says."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from materials_xml import write_library  # noqa: E402

PSI = 6894.757293168
(HERE / "assets").mkdir(exist_ok=True)
write_library(HERE / "assets" / "ict1_materials.xml",
              [dict(name="Aluminum (E = 10e6 psi, tutorial Q2)", E=10e6 * PSI, nu=0.33, rho=2770.0,
                    description="In-class tutorial Q2: E = 10x10^6 psi as given"),
               dict(name="Steel (E = 29e6 psi, tutorial Q3)", E=29e6 * PSI, nu=0.3, rho=7850.0,
                    description="In-class tutorial Q3: E = 29x10^6 psi as given")],
              source="General_Materials.xml", template="Structural Steel")
print("wrote assets/ict1_materials.xml")
