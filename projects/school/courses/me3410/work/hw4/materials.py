"""Write assets/hw4_materials.xml: ANSYS Aluminum Alloy with E = 70 GPa as given in HW 4."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from materials_xml import write_library  # noqa: E402

write_library(HERE / "assets" / "hw4_materials.xml",
              [dict(name="Aluminum Alloy (E = 70 GPa, HW 4)", E=70e9, nu=0.33, rho=2770.0,
                    description="HW 4: E = 70 GPa as given")],
              source="General_Materials.xml", template="Aluminum Alloy")
print("wrote assets/hw4_materials.xml")
