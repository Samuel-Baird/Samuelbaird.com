"""Write assets/hw5_materials.xml: ANSYS Structural Steel with E = 29x10^6 psi as given in HW 5."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from materials_xml import write_library  # noqa: E402

PSI = 6894.757293168
write_library(HERE / "assets" / "hw5_materials.xml",
              [dict(name="Structural Steel (E = 29e6 psi, HW 5)", E=29e6 * PSI, nu=0.3, rho=7850.0,
                    description="HW 5: E = 29x10^6 psi as given")],
              source="General_Materials.xml", template="Structural Steel")
print("wrote assets/hw5_materials.xml")
