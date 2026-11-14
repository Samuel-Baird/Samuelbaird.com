# In-class tutorial: 3D aluminum bracket. Static structural, bearing load on the 30 mm hole, base fixed.
# Runs inside Mechanical with pipeline/mech_common.py and work/test1/line_common.py (solve_retry).
# --var ASSETS, OUT (space-free folders; see run_ansys.sh).
import math

FX, FY, FZ = 5500.0, 3500.0, 1700.0
SIZES = [8.0, 5.0, 3.5, 2.5]         # global element size (mm); fillet and bearing hole get size / 2
NODE_LIMIT = 120000                  # ANSYS Student stops at 128,000 nodes
Y_SEC = 35.0                         # beam-theory check section on the upright (mm)
PROBLEMS = []
R = {"convergence": [], "variant": {}, "problems": PROBLEMS}
NMM = MechanicalUnitSystem.StandardNMM

ISO = "iso"                          # Mechanical's isometric view: from +X +Y +Z, like the handout figure
BACK = "back_iso"                    # the same view turned 180 deg about the screen's vertical axis
FULL = ((0.030, 0.052, 0.025), 0.26)   # whole part: focal point (m), scene width (m)


def faces_mm():
    fs = [face_info(f) for f in geo_faces()]
    k = 1000.0 if max(abs(c) for f in fs for c in f["c"]) < 1.0 else 1.0
    a = k * k
    for f in fs:
        f["c"] = [v * k for v in f["c"]]
        f["area"] *= a
    return fs


def pick(fs, cond, what, n=None):
    ids = [f["id"] for f in fs if cond(f)]
    if not ids or (n is not None and len(ids) != n):
        raise Exception("%s: found %s in %s" % (what, ids, [(f["id"], [round(v, 1) for v in f["c"]], round(f["area"], 1)) for f in fs]))
    return ids


def add_path(name, p0, p1, n=41):
    cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
    p = cg.AddPath()
    p.PathType = PathScopingType.Points
    p.StartXCoordinate, p.StartYCoordinate, p.StartZCoordinate = [Quantity("%r [mm]" % v) for v in p0]
    p.EndXCoordinate, p.EndYCoordinate, p.EndZCoordinate = [Quantity("%r [mm]" % v) for v in p1]
    p.NumberOfSamplingPoints = n
    p.Name = name
    return p


def setup():
    global AN, FIX, BEAR, FZL, FALL, RES, SIZ, NS, F
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = NMM
    import_geometry(os.path.join(ASSETS, "bracket.step"))
    assign_material("Aluminum Alloy")
    fs = faces_mm()
    F = {}
    F["base"] = pick(fs, lambda f: abs(f["c"][1]) < 0.3 and f["area"] > 2000, "base bottom face", 1)
    F["bearing"] = pick(fs, lambda f: math.hypot(f["c"][0] - 30, f["c"][1] - 70) < 16 and 4 < f["c"][2] < 6
                        and f["area"] > 300, "bearing hole")
    F["fillet"] = pick(fs, lambda f: 10.5 < f["c"][1] < 16 and 10.5 < f["c"][2] < 16, "R10 fillet")
    F["back"] = pick(fs, lambda f: abs(f["c"][2]) < 0.3 and f["area"] > 3000, "back face", 1)
    R["faces"] = F
    NS = dict((k, named_selection(k.upper(), v)) for k, v in F.items())
    NS["refine"] = named_selection("REFINED_FACES", F["bearing"] + F["fillet"])

    SIZ = Model.Mesh.AddSizing()
    SIZ.Location = NS["refine"]
    SIZ.Name = "Fillet + bearing-hole sizing (global / 2)"

    AN = Model.AddStaticStructuralAnalysis()
    FIX = AN.AddFixedSupport()
    FIX.Location = NS["base"]
    FIX.Name = "Fixed support: base bottom face"
    BEAR = AN.AddBearingLoad()
    BEAR.Location = NS["bearing"]
    BEAR.DefineBy = LoadDefineBy.Components
    BEAR.XComponent.Output.DiscreteValues = [Quantity("%r [N]" % FX)]
    BEAR.YComponent.Output.DiscreteValues = [Quantity("%r [N]" % FY)]
    BEAR.Name = "Bearing load: 5500 N (X), 3500 N (Y)"
    FZL = AN.AddForce()
    FZL.Location = NS["bearing"]
    FZL.DefineBy = LoadDefineBy.Components
    FZL.ZComponent.Output.DiscreteValues = [Quantity("%r [N]" % FZ)]
    FZL.Name = "Force 1700 N (Z, along the hole axis)"
    # Variant: all three components as one uniform force on the hole surface (suppressed by default)
    FALL = AN.AddForce()
    FALL.Location = NS["bearing"]
    FALL.DefineBy = LoadDefineBy.Components
    FALL.XComponent.Output.DiscreteValues = [Quantity("%r [N]" % FX)]
    FALL.YComponent.Output.DiscreteValues = [Quantity("%r [N]" % FY)]
    FALL.ZComponent.Output.DiscreteValues = [Quantity("%r [N]" % FZ)]
    FALL.Name = "Variant: uniform surface force (5500, 3500, 1700) N"
    FALL.Suppressed = True

    pb = add_path("Back face z = 0, y = %g (across the width)" % Y_SEC, (0.0, Y_SEC, 0.0), (60.0, Y_SEC, 0.0), 61)
    pt = add_path("Thickness at x = 30, y = %g" % Y_SEC, (30.0, Y_SEC, 0.0), (30.0, Y_SEC, 10.0), 21)
    ps = add_path("Side x = 0, y = %g (through the thickness)" % Y_SEC, (0.0, Y_SEC, 0.0), (0.0, Y_SEC, 10.0), 21)

    sol = AN.Solution
    RES = {}
    RES["eqv"] = sol.AddEquivalentStress()
    RES["td"] = sol.AddTotalDeformation()
    for ax, ori in (("dx", NormalOrientationType.XAxis), ("dy", NormalOrientationType.YAxis), ("dz", NormalOrientationType.ZAxis)):
        RES[ax] = sol.AddDirectionalDeformation()
        RES[ax].NormalOrientation = ori
    for key, ns, nm in (("eqv_fillet", NS["fillet"], "Equivalent stress on the R10 fillet"),
                        ("eqv_bearing", NS["bearing"], "Equivalent stress on the bearing hole"),
                        ("eqv_base", NS["base"], "Equivalent stress on the fixed base face")):
        RES[key] = sol.AddEquivalentStress()
        RES[key].Location = ns
        RES[key].Name = nm
    for key, p, nm in (("sy_back", pb, "Normal stress Y, back face"), ("sy_thick", pt, "Normal stress Y, through thickness"),
                       ("sy_side", ps, "Normal stress Y, side x = 0")):
        RES[key] = sol.AddNormalStress()
        RES[key].NormalOrientation = NormalOrientationType.YAxis
        RES[key].ScopingMethod = GeometryDefineByType.Path
        RES[key].Location = p
        RES[key].Name = nm
    RES["fr"] = sol.AddForceReaction()
    RES["fr"].BoundaryConditionSelection = FIX
    RES["mr"] = sol.AddMomentReaction()
    RES["mr"].BoundaryConditionSelection = FIX
    return "setup: %s" % F


def read(d):
    d["state"] = str(AN.Solution.ObjectState)
    for k in ("eqv", "eqv_fillet", "eqv_bearing", "eqv_base"):
        d[k + "_max"] = qval(RES[k].Maximum, "MPa")
    d["td_max"] = qval(RES["td"].Maximum, "mm")
    for k in ("dx", "dy", "dz"):
        d[k + "_max"] = qval(RES[k].Maximum, "mm")
        d[k + "_min"] = qval(RES[k].Minimum, "mm")
    for k in ("sy_back", "sy_thick", "sy_side"):
        d[k + "_max"] = qval(RES[k].Maximum, "MPa")
        d[k + "_min"] = qval(RES[k].Minimum, "MPa")
    fr, mr = RES["fr"], RES["mr"]
    d["R"] = [qval(fr.XAxis, "N"), qval(fr.YAxis, "N"), qval(fr.ZAxis, "N")]
    d["M"] = [qval(mr.XAxis, "N mm"), qval(mr.YAxis, "N mm"), qval(mr.ZAxis, "N mm")]
    try:
        d["max_loc"] = location_of_max(RES["eqv"])
    except Exception as ex:
        PROBLEMS.append("max location: %s" % str(ex)[:100])
    return d


def location_of_max(res):
    """Coordinates (mm) of the node with the highest value of a nodal result."""
    pd = res.PlotData
    keys = [str(k) for k in pd.Keys]
    nk = [k for k in keys if k.lower().startswith("node")][0]
    vals = list(pd["Values"])
    nodes = list(pd[nk])
    i = max(range(len(vals)), key=lambda j: vals[j])
    nd = AN.MeshData.NodeById(int(nodes[i]))
    c = [nd.X, nd.Y, nd.Z]
    k = 1000.0 if max(abs(v) for v in c) < 1.0 else 1.0
    return [v * k for v in c]


def plot_data(res):
    try:
        pd = res.PlotData
        return dict((str(k), [v for v in pd[str(k)]]) for k in pd.Keys)
    except Exception as ex:
        PROBLEMS.append("PlotData %s: %s" % (res.Name, str(ex)[:120]))
        return None


def mesh_solve(size):
    Model = ExtAPI.DataModel.Project.Model
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity("%r [mm]" % size)
    SIZ.ElementSize = Quantity("%r [mm]" % (size / 2.0))
    Model.Mesh.GenerateMesh()
    d = {"size": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    if d["nodes"] > NODE_LIMIT:
        d["skipped"] = "over node limit"
        return d
    solve_retry(AN)
    return read(d)


def view_export(obj, path, view="iso", frame=None, true_scale=False, wire=False, width=1400, height=800):
    """Named view (iso / back_iso / bottom ...), optionally re-centred on frame = ((x, y, z) m, scene width m).
    A custom ViewVector does not take in batch mode (the camera stays on its last orientation), so the back view
    is the iso view rotated about the screen Y axis."""
    prev = ExtAPI.Application.ActiveUnitSystem
    ExtAPI.Application.ActiveUnitSystem = NMM
    G = Ansys.Mechanical.DataModel.MechanicalEnums.Graphics
    rp = Graphics.ViewOptions.ResultPreference
    rp.ExtraModelDisplay = G.ExtraModelDisplay.UndeformedWireframe if wire else G.ExtraModelDisplay.NoWireframe
    rp.DeformationScaling = G.DeformationScaling.True if true_scale else G.DeformationScaling.Auto
    try:
        obj.Activate()
        cam = Graphics.Camera
        names = {"iso": ViewOrientationType.Iso, "back_iso": ViewOrientationType.Iso,
                 "bottom": ViewOrientationType.Bottom, "front": ViewOrientationType.Front, "back": ViewOrientationType.Back}
        cam.SetSpecificViewOrientation(names[view])
        cam.SetFit()
        if view == "back_iso":
            cam.Rotate(180.0, CameraAxisType.ScreenY)
            cam.SetFit()
        if frame is None and view in ("iso", "back_iso"):
            frame = FULL
        if frame:
            cam.FocalPoint = Ansys.Mechanical.Graphics.Point(list(frame[0]), "m")
            cam.SceneWidth = Quantity("%r [m]" % frame[1])
            cam.SceneHeight = Quantity("%r [m]" % (frame[1] * height / float(width)))
        st = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        st.Width, st.Height = width, height
        st.Resolution = GraphicsResolutionType.EnhancedResolution
        st.Background = GraphicsBackgroundType.White
        st.CurrentGraphicsDisplay = False
        Graphics.ExportImage(path, GraphicsImageExportFormat.PNG, st)
        return path
    finally:
        ExtAPI.Application.ActiveUnitSystem = prev


def shots(tag, items):
    out = {}
    for key, obj, view, kw in items:
        try:
            out[key] = view_export(obj, os.path.join(OUT, "%s%s.png" % (tag, key)), view=view, **kw)
        except Exception as ex:
            PROBLEMS.append("image %s: %s" % (key, str(ex)[:120]))
    return out
ExtAPI.DataModel.Project.New()
#%% split
setup()
#%% split
for s in SIZES:
    R["convergence"].append(mesh_solve(s))
    if R["convergence"][-1].get("skipped"):
        break
", ".join("%g mm: %d nodes, eqv %.1f fillet %.1f base %.1f back %.2f td %.4f %s" % (
    c["size"], c["nodes"], c.get("eqv_max", 0), c.get("eqv_fillet_max", 0), c.get("eqv_base_max", 0),
    c.get("sy_back_max", 0), c.get("td_max", 0), c.get("max_loc")) for c in R["convergence"])
#%% split
fin = [c for c in R["convergence"] if not c.get("skipped")][-1]
if R["convergence"][-1].get("skipped"):           # re-mesh at the finest size that solved
    fin = mesh_solve(fin["size"])
R["final"] = fin
for k in ("sy_back", "sy_thick", "sy_side"):
    R["final"][k + "_profile"] = plot_data(RES[k])
I = {}
I.update(shots("", [
    ("model", AN, ISO, {}), ("bc_fixed", FIX, ISO, {}), ("bc_bearing", BEAR, ISO, {}), ("bc_force_z", FZL, ISO, {}),
    ("mesh", Model.Mesh, ISO, {}), ("mesh_back", Model.Mesh, BACK, {}),
    ("deformed", RES["td"], ISO, {"wire": True}),
    ("td", RES["td"], ISO, {}), ("dx", RES["dx"], ISO, {}), ("dy", RES["dy"], ISO, {}), ("dz", RES["dz"], ISO, {}),
    ("eqv", RES["eqv"], ISO, {"true_scale": True}), ("eqv_back", RES["eqv"], BACK, {"true_scale": True}),
    ("eqv_fillet", RES["eqv_fillet"], ISO, {"true_scale": True}),
    ("eqv_bearing", RES["eqv_bearing"], ISO, {"true_scale": True}),
    ("eqv_base", RES["eqv_base"], "bottom", {"true_scale": True}),
    ("fr", RES["fr"], ISO, {}), ("mr", RES["mr"], ISO, {}),
]))
R["images"] = I
save_json(os.path.join(OUT, "results.json"), R)
"final: %s; problems %s" % (dict((k, v) for k, v in R["final"].items() if not k.endswith("profile")), PROBLEMS)
#%% split
# Variant: the same load as one uniform force spread over the hole surface (no bearing distribution).
BEAR.Suppressed = True
FZL.Suppressed = True
FALL.Suppressed = False
solve_retry(AN)
R["variant"] = read({"size": R["final"]["size"], "nodes": Model.Mesh.Nodes})
R["variant"]["images"] = shots("variant_", [("eqv", RES["eqv"], ISO, {"true_scale": True}),
                                           ("eqv_bearing", RES["eqv_bearing"], ISO, {"true_scale": True})])
BEAR.Suppressed = False
FZL.Suppressed = False
FALL.Suppressed = True
save_json(os.path.join(OUT, "results.json"), R)
json.dumps({"variant": dict((k, v) for k, v in R["variant"].items() if k != "images"), "problems": PROBLEMS})
