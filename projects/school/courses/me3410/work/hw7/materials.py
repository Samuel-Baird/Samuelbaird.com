"""Write assets/hw7_materials.xml: ANSYS Composite library + Kevlar 49 and isotropic carbon.

E-Glass and S-Glass are used straight from the library. Kevlar 49 is not in any ANSYS library,
so it comes from the HW 7 table (E = 19.0 Msi, 89.9 lb/ft^3) with nu = 0.36 assumed. Carbon fiber
uses the library's Carbon Fiber (230 GPa) fiber-direction E and nu_xz, idealized as isotropic
like the handout's table.
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from materials_xml import write_library  # noqa: E402

PSI, LBFT3 = 6894.757, 16.01846
write_library(HERE / "assets" / "hw7_materials.xml", [
    dict(name="Kevlar 49 (handout)", E=19.0e6 * PSI, nu=0.36, rho=89.9 * LBFT3,
         description="Kevlar 49: E from HW 7 table (19.0 Msi); nu = 0.36 assumed (not in ANSYS library)"),
    dict(name="Carbon Fiber 230 GPa (isotropic)", E=230e9, nu=0.20, rho=1800.0,
         description="ANSYS Carbon Fiber (230 GPa) fibre-direction E and nu_xz, idealized as isotropic"),
])
print("wrote assets/hw7_materials.xml")
