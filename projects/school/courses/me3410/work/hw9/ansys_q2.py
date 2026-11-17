# HW 9 Q2: lifting bracket, structural steel, 20 kN bearing load (+Y) on the lug hole, bottom face fixed.
# Two models: full bracket and the z >= 0 half (frictionless symmetry plane z = 0, half the load).
# Runs inside Mechanical with pipeline/mech_common.py and work/test1/line_common.py. --var ASSETS, OUT.
import math
P_FULL = 20000.0                                   # N
SIZES = [12.0, 8.0, 6.0, 4.5, 3.5]                 # global element size, mm; bearing hole faces get size / 2
NODE_LIMIT = 120000
PROBLEMS = []
try:
    ONLY
except NameError:
    ONLY = "all"                                    # --var ONLY=half re-runs just the half model
R = {"full": {"convergence": []}, "half": {"convergence": []}, "problems": PROBLEMS}
if ONLY == "half":
    R = json.loads(open(os.path.join(OUT, "q2_results.json")).read())
    R["half"] = {"convergence": []}
    R["problems"] = PROBLEMS
NMM = MechanicalUnitSystem.StandardNMM
ISO, BACK = "iso", "back_iso"
FULL_FRAME = ((0.0, 0.04, 0.0), 0.36)
MAT = "Structural Steel"
S = {}                                              # per-model state: AN, RES, SIZ, ...


def faces_mm():
    fs = [face_info(f) for f in geo_faces()]
    k = 1000.0 if max(abs(c) for f in fs for c in f["c"]) < 1.0 else 1.0
    for f in fs:
        f["c"] = [v * k for v in f["c"]]
        f["area"] *= k * k
    return fs


def pick(fs, cond, what, n=None):
    ids = [f["id"] for f in fs if cond(f)]
    if not ids or (n is not None and len(ids) != n):
        raise Exception("%s: found %s in %s" % (what, ids, [(f["id"], [round(v, 1) for v in f["c"]], round(f["area"], 1)) for f in fs]))
    return ids


def build(kind):
    """Import the STEP, make the named selections, loads and results for 'full' or 'half'."""
    global Model
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = NMM
    import_geometry(os.path.join(ASSETS, "q2_%s.step" % kind))
    assign_material(MAT)
    fs = faces_mm()
    F = {}
    F["bottom"] = pick(fs, lambda f: abs(f["c"][1] + 30) < 0.3 and f["area"] > 10000, "bottom face", 1)
    F["bearing"] = pick(fs, lambda f: math.hypot(f["c"][0], f["c"][1] - 80) < 16 and f["area"] > 300, "lug hole")
    if kind == "half":
        F["sym"] = pick(fs, lambda f: abs(f["c"][2]) < 0.1 and f["area"] > 1000, "symmetry plane z = 0", 1)
    NS = dict((k, named_selection(k.upper(), v)) for k, v in F.items())
    SIZ = Model.Mesh.AddSizing()
    SIZ.Location = NS["bearing"]
    SIZ.Name = "Bearing-hole sizing (global / 2)"
    AN = Model.AddStaticStructuralAnalysis()
    FIX = AN.AddFixedSupport()
    FIX.Location = NS["bottom"]
    FIX.Name = "Fixed support: bottom face (y = -30)"
    p = P_FULL if kind == "full" else P_FULL / 2.0
    BEAR = AN.AddBearingLoad()
    BEAR.Location = NS["bearing"]
    BEAR.DefineBy = LoadDefineBy.Components
    BEAR.YComponent.Output.DiscreteValues = [Quantity("%r [N]" % p)]
    BEAR.Name = "Bearing load %g N (+Y) on the lug hole" % p
    SYM = None
    if kind == "half":
        SYM = AN.AddFrictionlessSupport()
        SYM.Location = NS["sym"]
        SYM.Name = "Frictionless support: symmetry plane z = 0"
    sol = AN.Solution
    RES = {}
    RES["td"] = sol.AddTotalDeformation()
    RES["dy"] = sol.AddDirectionalDeformation()
    RES["dy"].NormalOrientation = NormalOrientationType.YAxis
    RES["dy"].Name = "Directional deformation Y"
    RES["eqv"] = sol.AddEquivalentStress()
    RES["sxy"] = sol.AddShearStress()
    RES["sxy"].ShearOrientation = ShearOrientationType.XYPlane
    RES["sxy"].Name = "Shear stress XY"
    RES["tmax"] = sol.AddMaximumShearStress()
    RES["eqv_bearing"] = sol.AddEquivalentStress()
    RES["eqv_bearing"].Location = NS["bearing"]
    RES["eqv_bearing"].Name = "Equivalent stress on the lug hole"
    RES["fr"] = sol.AddForceReaction()
    RES["fr"].BoundaryConditionSelection = FIX
    S[kind] = dict(AN=AN, RES=RES, SIZ=SIZ, FIX=FIX, BEAR=BEAR, SYM=SYM, F=F, NS=NS)
    R[kind]["faces"] = F
    return "setup %s: %s" % (kind, F)


def read(kind, d):
    AN, RES = S[kind]["AN"], S[kind]["RES"]
    d["state"] = str(AN.Solution.ObjectState)
    d["td_max"] = qval(RES["td"].Maximum, "mm")
    d["dy_max"] = qval(RES["dy"].Maximum, "mm")
    d["dy_min"] = qval(RES["dy"].Minimum, "mm")
    d["eqv_max"] = qval(RES["eqv"].Maximum, "MPa")
    d["eqv_bearing_max"] = qval(RES["eqv_bearing"].Maximum, "MPa")
    d["sxy_max"] = qval(RES["sxy"].Maximum, "MPa")
    d["sxy_min"] = qval(RES["sxy"].Minimum, "MPa")
    d["tmax_max"] = qval(RES["tmax"].Maximum, "MPa")
    fr = RES["fr"]
    d["R"] = [qval(fr.XAxis, "N"), qval(fr.YAxis, "N"), qval(fr.ZAxis, "N")]
    try:
        d["max_loc"] = location_of_max(AN, RES["eqv"])
    except Exception as ex:
        PROBLEMS.append("max location: %s" % str(ex)[:100])
    return d


def location_of_max(AN, res):
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


def mesh_solve(kind, size):
    SIZ, AN = S[kind]["SIZ"], S[kind]["AN"]
    try:
        Model.Mesh.ElementOrder = ElementOrder.Quadratic
    except Exception:                               # read-only in a second project of the same session: Program Controlled
        PROBLEMS.append("ElementOrder read-only, left at %s" % Model.Mesh.ElementOrder)   # gives quadratic elements
    Model.Mesh.ElementSize = Quantity("%r [mm]" % size)
    SIZ.ElementSize = Quantity("%r [mm]" % (size / 2.0))
    Model.Mesh.GenerateMesh()
    d = {"size": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    if d["nodes"] > NODE_LIMIT:
        d["skipped"] = "over node limit"
        return d
    solve_retry(AN)
    return read(kind, d)


def view_export(obj, path, view="iso", wire=False, width=1400, height=800, true_scale=True, frame=None):
    prev = ExtAPI.Application.ActiveUnitSystem
    ExtAPI.Application.ActiveUnitSystem = NMM
    G = Ansys.Mechanical.DataModel.MechanicalEnums.Graphics
    rp = Graphics.ViewOptions.ResultPreference
    rp.ExtraModelDisplay = G.ExtraModelDisplay.UndeformedWireframe if wire else G.ExtraModelDisplay.NoWireframe
    rp.DeformationScaling = G.DeformationScaling.True if true_scale else G.DeformationScaling.Auto
    try:
        obj.Activate()
        cam = Graphics.Camera
        names = {"iso": ViewOrientationType.Iso, "back_iso": ViewOrientationType.Iso, "front": ViewOrientationType.Front,
                 "right": ViewOrientationType.Right, "top": ViewOrientationType.Top}
        cam.SetSpecificViewOrientation(names[view])
        cam.SetFit()
        if view == "back_iso":
            cam.Rotate(180.0, CameraAxisType.ScreenY)
            cam.SetFit()
        fr = frame or (FULL_FRAME if view in ("iso", "back_iso") else None)
        if fr:
            cam.FocalPoint = Ansys.Mechanical.Graphics.Point(list(fr[0]), "m")
            cam.SceneWidth = Quantity("%r [m]" % fr[1])
            cam.SceneHeight = Quantity("%r [m]" % (fr[1] * height / float(width)))
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


def study(kind):
    for s in SIZES:
        R[kind]["convergence"].append(mesh_solve(kind, s))
        if R[kind]["convergence"][-1].get("skipped"):
            break
    ok = [c for c in R[kind]["convergence"] if not c.get("skipped")]
    fin = ok[-1]
    if R[kind]["convergence"][-1].get("skipped"):
        fin = mesh_solve(kind, fin["size"])
    R[kind]["final"] = fin
    s = S[kind]
    RES = s["RES"]
    items = [("model", s["AN"], ISO, {"true_scale": False}), ("bc_fixed", s["FIX"], ISO, {"true_scale": False}),
             ("bc_bearing", s["BEAR"], ISO, {"true_scale": False}), ("mesh", Model.Mesh, ISO, {"true_scale": False}),
             ("td", RES["td"], ISO, {}), ("dy", RES["dy"], ISO, {}), ("eqv", RES["eqv"], ISO, {}),
             ("sxy", RES["sxy"], ISO, {}), ("tmax", RES["tmax"], ISO, {}), ("eqv_bearing", RES["eqv_bearing"], ISO, {}),
             ("deformed", RES["td"], ISO, {"wire": True})]
    if kind == "half":
        items += [("bc_sym", s["SYM"], BACK, {"true_scale": False}), ("eqv_back", RES["eqv"], BACK, {}),
                  ("mesh_back", Model.Mesh, BACK, {"true_scale": False})]
    R[kind]["images"] = shots("%s_" % kind, items)
    save_json(os.path.join(OUT, "q2_results.json"), R)
    return "%s: %s problems %s" % (kind, dict((k, v) for k, v in fin.items()), PROBLEMS)
ExtAPI.DataModel.Project.New()
#%% split
if ONLY == "all":
    build("full")
#%% split
if ONLY == "all":
    study("full")
#%% split
if ONLY == "all":
    ExtAPI.DataModel.Project.New()
#%% split
build("half")
#%% split
study("half")
