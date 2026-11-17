"""Write assets/test1_materials.xml: the Q1 shaft material (E = 10.6x10^6 psi, nu = 0.3 as given).
Q2 and Q3 use ANSYS's default Structural Steel."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from materials_xml import write_library  # noqa: E402

PSI = 6894.757293168
(HERE / "assets").mkdir(exist_ok=True)
write_library(HERE / "assets" / "test1_materials.xml",
              [dict(name="Shaft (E = 10.6e6 psi, Test 1 Q1)", E=10.6e6 * PSI, nu=0.3, rho=2770.0,
                    description="Test 1 Q1: E = 10.6x10^6 psi, nu = 0.3 as given")],
              source="General_Materials.xml", template="Aluminum Alloy")
print("wrote assets/test1_materials.xml")
