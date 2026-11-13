"""Make an Engineering Data XML with extra isotropic materials, cloned from a library entry.

Mechanical's scripting API cannot edit material properties, but it can import an Engineering
Data XML. This copies a library file and inserts clones of an isotropic entry (default: the
Composite library's "E-Glass") with a new name, E, nu and density.

    from materials_xml import write_library
    write_library(out_xml, [dict(name="Kevlar 49 (handout)", E=131e9, nu=0.36, rho=1440.0,
                                 description="...")])
"""
import re
from pathlib import Path

LIB = Path(r"C:\Program Files\ANSYS Inc\ANSYS Student\v261\Addins\EngineeringData\Samples")


def _block(xml, name):
    i = xml.find(f"<Name>{name}</Name>")
    if i < 0:
        raise KeyError(name)
    s = xml.rfind("<Material>", 0, i)
    e = xml.find("</Material>", i) + len("</Material>")
    return s, e


def _set_param(block, prop_id, param_id, value):
    """Replace <Data> of ParameterValue param_id inside PropertyData prop_id."""
    ps = block.find(f'<PropertyData property="{prop_id}">')
    pe = block.find("</PropertyData>", ps)
    seg = block[ps:pe]
    new, n = re.subn(rf'(<ParameterValue parameter="{param_id}" format="float">\s*<Data>)[^<]*(</Data>)',
                     lambda m: f"{m.group(1)}{value!r}{m.group(2)}", seg, count=1)
    if n == 0:
        raise ValueError(f"{prop_id}/{param_id} not found")
    return block[:ps] + new + block[pe:]


def _id(xml, kind, name):
    """Metadata id (prN / paN) of a property or parameter by its name; ids differ per library."""
    tag = "PropertyDetails" if kind == "pr" else "ParameterDetails"
    m = re.search(rf'<{tag} id="({kind}\d+)">\s*<Unitless\s*/>\s*<Name>{re.escape(name)}</Name>', xml) or \
        re.search(rf'<{tag} id="({kind}\d+)">(?:(?!</{tag}>).)*?<Name>{re.escape(name)}</Name>', xml, re.S)
    if not m:
        raise KeyError(f"{tag} {name}")
    return m.group(1)


def write_library(out_xml, extra, source="Composite_Materials.xml", template="E-Glass"):
    xml = (LIB / source).read_text(encoding="utf-8")
    s, e = _block(xml, template)
    tpl = xml[s:e]
    pr_el, pr_rho = _id(xml, "pr", "Elasticity"), _id(xml, "pr", "Density")
    pa_E, pa_nu = _id(xml, "pa", "Young's Modulus"), _id(xml, "pa", "Poisson's Ratio")
    pa_K, pa_G, pa_rho = _id(xml, "pa", "Bulk Modulus"), _id(xml, "pa", "Shear Modulus"), _id(xml, "pa", "Density")
    clones = []
    for m in extra:
        b = tpl.replace(f"<Name>{template}</Name>", f"<Name>{m['name']}</Name>", 1)
        b = re.sub(r"<Description>[^<]*</Description>", f"<Description>{m.get('description', '')}</Description>", b, count=1)
        E, nu = float(m["E"]), float(m["nu"])
        b = _set_param(b, pr_el, pa_E, E)
        b = _set_param(b, pr_el, pa_nu, nu)
        b = _set_param(b, pr_el, pa_K, E / (3 * (1 - 2 * nu)))
        b = _set_param(b, pr_el, pa_G, E / (2 * (1 + nu)))
        b = _set_param(b, pr_rho, pa_rho, float(m["rho"]))
        clones.append(b)
    out = xml[:e] + "\n" + "\n".join(clones) + xml[e:]
    Path(out_xml).write_text(out, encoding="utf-8")
    return out_xml
