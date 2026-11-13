# Helpers that run INSIDE Mechanical (IronPython-compatible: no f-strings).
# scripts/mech.py prepends this file to an assignment's ansys.py via --lib.
import json
import os

Model = ExtAPI.DataModel.Project.Model
MATXML = r"C:\Program Files\ANSYS Inc\ANSYS Student\v261\Addins\EngineeringData\Samples\General_Materials.xml"


def new_model(step_path, unit_system=None, fresh=True):
    """Import geometry into a model. Call ExtAPI.DataModel.Project.New() in its *own* script
    call first and pass fresh=False: right after New() in the same call, mesh properties can be
    read-only (Mechanical has not finished resetting)."""
    if fresh:
        ExtAPI.DataModel.Project.New()
    global Model
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = unit_system or MechanicalUnitSystem.StandardMKS
    gi = Model.GeometryImportGroup.AddGeometryImport()
    prefs = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
    prefs.ProcessLines = True
    gi.Import(step_path, Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic, prefs)
    return Model


def bodies():
    return Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)


def geo_faces():
    out = []
    for asm in ExtAPI.DataModel.GeoData.Assemblies:
        for part in asm.Parts:
            for b in part.Bodies:
                for f in b.Faces:
                    out.append(f)
    return out


def face_info(f):
    n = f.NormalAtParam(0.5, 0.5)
    return {"id": f.Id, "c": list(f.Centroid), "area": f.Area, "n": list(n)}


def named_selection(name, ids, kind="geo"):
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids = list(ids)
    ns = Model.AddNamedSelection()
    ns.Location = sel
    ns.Name = name
    return ns


def assign_material(name):
    Model.Materials.Import(MATXML)
    for b in bodies():
        b.Material = name


def material_props(name):
    """E [Pa], nu, Sy [Pa], rho [kg/m^3] from Engineering Data."""
    import materials
    m = [x for x in Model.Materials.Children if x.Name == name][0]
    ed = m.GetEngineeringDataMaterial()
    out = {}
    try:
        el = materials.GetMaterialPropertyByName(ed, "Elasticity")
        out["E"] = float(el["Young's Modulus"][1])
        out["nu"] = float(el["Poisson's Ratio"][1])
    except Exception as e:
        out["err_el"] = str(e)
    try:
        ty = materials.GetMaterialPropertyByName(ed, "Tensile Yield Strength")
        out["Sy"] = float(ty["Tensile Yield Strength"][1])
    except Exception as e:
        out["err_sy"] = str(e)
    try:
        d = materials.GetMaterialPropertyByName(ed, "Density")
        out["rho"] = float(d["Density"][1])
    except Exception as e:
        out["err_rho"] = str(e)
    return out


def q(v, unit):
    return Quantity("%r [%s]" % (v, unit))


def export_image(obj, path, view="iso", width=1400, height=800, fit=True, units=None, frame=None):
    """Activate a tree object and save a PNG of the graphics window.

    Plots are shown in mm / MPa (units=StandardNMM) without element edges; the active unit
    system is restored afterwards so formula loads (written in m, Pa) are never reinterpreted.
    """
    prev = ExtAPI.Application.ActiveUnitSystem
    ExtAPI.Application.ActiveUnitSystem = units or MechanicalUnitSystem.StandardNMM
    Graphics.ViewOptions.ResultPreference.ExtraModelDisplay = \
        Ansys.Mechanical.DataModel.MechanicalEnums.Graphics.ExtraModelDisplay.NoWireframe
    try:
        return _export_image(obj, path, view, width, height, fit, frame)
    finally:
        ExtAPI.Application.ActiveUnitSystem = prev


def _export_image(obj, path, view, width, height, fit, frame):
    """view: a named orientation, or a (vx, vy, vz) view vector with frame=((x, y, z) m, width m)
    giving the focal point and scene width (SetFit does not refit after a custom view vector)."""
    obj.Activate()
    cam = Graphics.Camera
    if isinstance(view, tuple):
        cam.SetSpecificViewOrientation(ViewOrientationType.Iso)
        cam.ViewVector = Ansys.ACT.Math.Vector3D(view[0], view[1], view[2])
        cam.UpVector = Ansys.ACT.Math.Vector3D(0, 1, 0)
        if frame:
            cam.FocalPoint = Ansys.Mechanical.Graphics.Point(list(frame[0]), "m")
            cam.SceneWidth = Quantity("%r [m]" % frame[1])
        view, fit = None, False
    views = {
        "iso": ViewOrientationType.Iso, "front": ViewOrientationType.Front,
        "top": ViewOrientationType.Top, "right": ViewOrientationType.Right,
        "left": ViewOrientationType.Left, "bottom": ViewOrientationType.Bottom,
        "back": ViewOrientationType.Back,
    }
    if view:
        cam.SetSpecificViewOrientation(views[view])
    if fit:
        cam.SetFit()
    s = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
    s.Width = width
    s.Height = height
    s.Resolution = GraphicsResolutionType.EnhancedResolution
    s.Background = GraphicsBackgroundType.White
    s.CurrentGraphicsDisplay = False
    Graphics.ExportImage(path, GraphicsImageExportFormat.PNG, s)
    return path


def qval(quantity, unit):
    """Quantity -> float in the given unit."""
    return float(quantity.ConvertUnit(unit).Value)


def save_json(path, data):
    with open(path, "w") as fh:
        fh.write(json.dumps(data, indent=2))
