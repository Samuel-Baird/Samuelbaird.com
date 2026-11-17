# In-class tutorial 10-28, problem 1: stepped plate with an R25 fillet, 2D plane stress.
# Runs inside Mechanical with pipeline/mech_common.py and work/test1/line_common.py (solve_retry).
# --var ASSETS, OUT (space-free folders; see run_ansys.sh).
import math

T_MM = 5.0
F_N = 1000.0
FACE_SIZES = [20.0, 10.0, 5.0, 2.5, 1.25]       # face sizing study (mm), no local control
EDGE_SIZES = [5.0, 2.5, 1.25, 0.625]           # fillet edge sizing study (mm), face at 10 mm
EDGE2_SIZES = [1.25, 0.625, 0.3125]            # same with the face at 2.5 mm
X_SEC = 200.0                                  # beam-theory check section (mm)
PROBLEMS = []
R = {"default": None, "face": [], "edge": [], "edge2": [], "adaptive": {}, "fatigue": {}, "problems": PROBLEMS}
NMM = MechanicalUnitSystem.StandardNMM

FULL = ((0.125, 0.05), 0.29)
FILLET_Z = ((0.138, 0.052), 0.05)
WALL_Z = ((0.009, 0.007), 0.026)


def shot(obj, name, frame=FULL, wire=False, true_scale=False):
    """Front view framed explicitly (SetFit crops 2D parts in batch mode)."""
    prev = ExtAPI.Application.ActiveUnitSystem
    ExtAPI.Application.ActiveUnitSystem = NMM
    G = Ansys.Mechanical.DataModel.MechanicalEnums.Graphics
    rp = Graphics.ViewOptions.ResultPreference
    rp.ExtraModelDisplay = G.ExtraModelDisplay.UndeformedWireframe if wire else G.ExtraModelDisplay.NoWireframe
    rp.DeformationScaling = G.DeformationScaling.True if true_scale else G.DeformationScaling.Auto
    try:
        obj.Activate()
        cam = Graphics.Camera
        cam.SetSpecificViewOrientation(ViewOrientationType.Front)
        cam.SetFit()
        cam.FocalPoint = Ansys.Mechanical.Graphics.Point([frame[0][0], frame[0][1], 0.0], "m")
        cam.SceneWidth = Quantity("%r [m]" % frame[1])
        cam.SceneHeight = Quantity("%r [m]" % (frame[1] * 800.0 / 1200.0))
        st = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        st.Width, st.Height = 1200, 800
        st.Resolution = GraphicsResolutionType.EnhancedResolution
        st.Background = GraphicsBackgroundType.White
        st.CurrentGraphicsDisplay = False
        path = os.path.join(OUT, name)
        Graphics.ExportImage(path, GraphicsImageExportFormat.PNG, st)
        return path
    except Exception as ex:
        PROBLEMS.append("shot %s: %s" % (name, str(ex)[:120]))
        return None
    finally:
        ExtAPI.Application.ActiveUnitSystem = prev


def edges_mm():
    es = [edge_info(e) for e in geo_edges()]
    k = 1000.0 if max(e["len"] for e in es) < 1.0 else 1.0
    for e in es:
        e["c"] = [v * k for v in e["c"]]
        e["len"] *= k
    return es


def pick(es, cond, what, n=None):
    ids = [e["id"] for e in es if cond(e)]
    if not ids or (n is not None and len(ids) != n):
        raise Exception("%s: found %s in %s" % (what, ids, [(e["id"], [round(v, 1) for v in e["c"]], round(e["len"], 1)) for e in es]))
    return ids


def setup():
    global AN, FIX, FRC, RES, FACE_SIZ, EDGE_SIZ, PATH, E
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = NMM
    import_geometry(os.path.join(ASSETS, "stepped_plate.step"), two_d=True)
    Model.Geometry.Model2DBehavior = Model2DBehavior.PlaneStress
    for b in bodies():
        b.Thickness = Quantity("%r [mm]" % T_MM)
        b.Material = "Structural Steel"
    es = edges_mm()
    E = {}
    E["wall"] = pick(es, lambda e: abs(e["c"][0]) < 0.5 and abs(e["len"] - 100) < 0.5, "wall edge", 1)
    E["tip"] = pick(es, lambda e: abs(e["c"][0] - 250) < 0.5 and abs(e["len"] - 40) < 0.5, "tip edge", 1)
    E["fillet"] = pick(es, lambda e: abs(e["len"] - 25 * math.pi / 2) < 0.5, "fillet", 1)
    R["edges"] = E
    ns = dict((k, named_selection(k.upper(), v)) for k, v in E.items())
    faces = [f.Id for f in geo_faces()]
    ns["face"] = named_selection("PLATE", faces)

    FACE_SIZ = Model.Mesh.AddSizing()
    FACE_SIZ.Location = ns["face"]
    FACE_SIZ.Name = "Face Sizing"
    EDGE_SIZ = Model.Mesh.AddSizing()
    EDGE_SIZ.Location = ns["fillet"]
    EDGE_SIZ.Name = "Edge Sizing (R25 fillet)"

    AN = Model.AddStaticStructuralAnalysis()
    FIX = AN.AddFixedSupport()
    FIX.Location = ns["wall"]
    FIX.Name = "Fixed support: left edge (wall)"
    FRC = AN.AddForce()
    FRC.Location = ns["tip"]
    FRC.DefineBy = LoadDefineBy.Components
    FRC.YComponent.Output.DiscreteValues = [Quantity("%r [N]" % -F_N)]
    FRC.Name = "Force 1000 N down on the free end"

    cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
    PATH = cg.AddPath()
    PATH.PathType = PathScopingType.Points
    PATH.StartXCoordinate = Quantity("%r [mm]" % X_SEC)
    PATH.StartYCoordinate = Quantity("0 [mm]")
    PATH.EndXCoordinate = Quantity("%r [mm]" % X_SEC)
    PATH.EndYCoordinate = Quantity("40 [mm]")
    PATH.NumberOfSamplingPoints = 41
    PATH.Name = "Section x = 200 mm"

    sol = AN.Solution
    RES = {}
    RES["eqv"] = sol.AddEquivalentStress()
    RES["td"] = sol.AddTotalDeformation()
    RES["dy"] = sol.AddDirectionalDeformation()
    RES["dy"].NormalOrientation = NormalOrientationType.YAxis
    RES["eqv_fillet"] = sol.AddEquivalentStress()
    RES["eqv_fillet"].Location = ns["fillet"]
    RES["eqv_fillet"].Name = "Equivalent stress on the R25 fillet"
    RES["s1_fillet"] = sol.AddMaximumPrincipalStress()
    RES["s1_fillet"].Location = ns["fillet"]
    RES["s1_fillet"].Name = "Max principal stress on the R25 fillet"
    RES["eqv_wall"] = sol.AddEquivalentStress()
    RES["eqv_wall"].Location = ns["wall"]
    RES["eqv_wall"].Name = "Equivalent stress on the fixed edge"
    RES["sx_path"] = sol.AddNormalStress()
    RES["sx_path"].NormalOrientation = NormalOrientationType.XAxis
    RES["sx_path"].ScopingMethod = GeometryDefineByType.Path
    RES["sx_path"].Location = PATH
    RES["sx_path"].Name = "Normal stress X on section x = 200 mm"
    RES["fr"] = sol.AddForceReaction()
    RES["fr"].BoundaryConditionSelection = FIX
    RES["mr"] = sol.AddMomentReaction()
    RES["mr"].BoundaryConditionSelection = FIX
    return "setup: %s" % E


def read(d):
    d["state"] = str(AN.Solution.ObjectState)
    for k in ("eqv", "eqv_fillet", "s1_fillet", "eqv_wall"):
        d[k + "_max"] = qval(RES[k].Maximum, "MPa")
    d["td_max"] = qval(RES["td"].Maximum, "mm")
    d["dy_min"] = qval(RES["dy"].Minimum, "mm")
    d["sx_path_max"] = qval(RES["sx_path"].Maximum, "MPa")
    d["sx_path_min"] = qval(RES["sx_path"].Minimum, "MPa")
    d["Rx"], d["Ry"] = qval(RES["fr"].XAxis, "N"), qval(RES["fr"].YAxis, "N")
    d["Mz"] = qval(RES["mr"].ZAxis, "N mm")
    return d


def mesh_solve(label, face=None, edge=None):
    Model = ExtAPI.DataModel.Project.Model
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    FACE_SIZ.Suppressed = face is None
    EDGE_SIZ.Suppressed = edge is None
    if face is not None:
        FACE_SIZ.ElementSize = Quantity("%r [mm]" % face)
    if edge is not None:
        EDGE_SIZ.ElementSize = Quantity("%r [mm]" % edge)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    return read({"label": label, "face": face, "edge": edge, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements})


def plot_data(res):
    try:
        pd = res.PlotData
        return dict((str(k), [v for v in pd[str(k)]]) for k in pd.Keys)
    except Exception as ex:
        PROBLEMS.append("PlotData %s: %s" % (res.Name, str(ex)[:120]))
        return None


def fillet_profile():
    """Von Mises and max principal at every fillet node, with node coordinates (mm)."""
    out = {}
    try:
        md = AN.MeshData
        nids = list(md.MeshRegionById(E["fillet"][0]).NodeIds)
        xy = {}
        for n in nids:
            nd = md.NodeById(n)
            xy[n] = (nd.X, nd.Y)
        k = 1000.0 if max(abs(c) for p in xy.values() for c in p) < 1.0 else 1.0
        for key in ("eqv_fillet", "s1_fillet"):
            pd = plot_data(RES[key])
            if not pd:
                continue
            nk = [kk for kk in pd if kk.lower().startswith("node")][0]
            vals = pd["Values"]
            rows = []
            for n, v in zip(pd[nk], vals):
                n = int(n)
                if n in xy:
                    rows.append([xy[n][0] * k, xy[n][1] * k, float(v)])
            out[key] = rows
        out["keys"] = list(pd.keys()) if pd else None
    except Exception as ex:
        PROBLEMS.append("fillet profile: %s" % str(ex)[:200])
    return out


def adaptive(tag, res, allowable, loops=6, depth=2):
    Model = ExtAPI.DataModel.Project.Model
    FACE_SIZ.Suppressed = True
    EDGE_SIZ.Suppressed = True
    conv = RES[res].AddConvergence()
    conv.Type = ConvergenceType.Maximum
    conv.AllowableChange = allowable
    AN.Solution.MaximumRefinementLoops = loops
    AN.Solution.RefinementDepth = depth
    d = {"result": res, "allowable_pct": allowable, "loops_max": loops, "depth": depth}
    try:
        Model.Mesh.GenerateMesh()
        d["start_nodes"], d["start_elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
        solve_retry(AN)
        d["nodes"] = Model.Mesh.Nodes
        read(d)
        try:
            d["history"] = [(str(x.Caption), str(x.StringValue)) for x in conv.VisibleProperties]
        except Exception:
            pass
        try:
            d["last_change_pct"] = float(str(conv.LastChange).split()[0])
        except Exception:
            d["last_change_pct"] = None
        d["img_res"] = shot(RES[res], "adapt_%s_res.png" % tag, frame=FILLET_Z, true_scale=True)
    except Exception as ex:
        d["error"] = str(ex)[:300]
    conv.Delete()
    AN.Solution.MaximumRefinementLoops = 1
    R["adaptive"][tag] = d
    return "%s: %s" % (tag, dict((k, v) for k, v in d.items() if k != "history" and not k.startswith("img")))


def fatigue(tag, ratio=None, theory="NoneStress"):
    ft = AN.Solution.AddFatigueTool()
    ft.AnalysisType = FatigueToolAnalysisType.StressLife
    ft.StressComponent = FatigueStressComponentType.FatigueToolVon_Mises
    if ratio is None:
        ft.LoadingType = FatigueLoadType.FullyReversed
    else:
        ft.LoadingType = FatigueLoadType.Ratio
        ft.LoadingRatio = ratio
    ft.MeanStressTheory = getattr(Ansys.Mechanical.DataModel.Enums.MeanStressTheoryType, theory)
    ft.Name = "Fatigue Tool (%s)" % tag
    life = ft.AddLife()
    sf = ft.AddSafetyFactor()
    try:
        sf.DesignLife = Quantity("1e6 [cycles]")
    except Exception:
        try:
            sf.DesignLife = 1e6
        except Exception as ex:
            PROBLEMS.append("DesignLife: %s" % str(ex)[:100])
    AN.Solution.EvaluateAllResults()
    d = {"ratio": -1.0 if ratio is None else ratio, "theory": str(ft.MeanStressTheory)}
    for k, o in (("life", life), ("sf", sf)):
        try:
            d[k + "_min"] = float(str(o.Minimum).split()[0])
            d[k + "_max"] = float(str(o.Maximum).split()[0])
        except Exception as ex:
            PROBLEMS.append("fatigue %s %s: %s" % (tag, k, str(ex)[:100]))
    try:
        d["design_life"] = str(sf.DesignLife)
    except Exception:
        pass
    d["img_life"] = shot(life, "fatigue_%s_life.png" % tag)
    d["img_sf"] = shot(sf, "fatigue_%s_sf.png" % tag)
    d["img_sf_zoom"] = shot(sf, "fatigue_%s_sf_zoom.png" % tag, frame=FILLET_Z)
    R["fatigue"][tag] = d
    return "%s: %s" % (tag, dict((k, v) for k, v in d.items() if not k.startswith("img")))
ExtAPI.DataModel.Project.New()
#%% split
setup()
#%% split
R["default"] = mesh_solve("default")
I0 = shot(Model.Mesh, "mesh_default.png")
"default: %d el, eqv %.2f fillet %.2f wall %.2f" % (R["default"]["elements"], R["default"]["eqv_max"],
                                                    R["default"]["eqv_fillet_max"], R["default"]["eqv_wall_max"])
#%% split
for s in FACE_SIZES:
    R["face"].append(mesh_solve("face %g" % s, face=s))
", ".join("%g mm: %d el, eqv %.2f (fillet %.2f, wall %.2f) td %.5f" % (
    c["face"], c["elements"], c["eqv_max"], c["eqv_fillet_max"], c["eqv_wall_max"], c["td_max"]) for c in R["face"])
#%% split
for s in EDGE_SIZES:
    R["edge"].append(mesh_solve("edge %g" % s, face=10.0, edge=s))
", ".join("%g mm: %d el, fillet %.2f, wall %.2f td %.5f" % (
    c["edge"], c["elements"], c["eqv_fillet_max"], c["eqv_wall_max"], c["td_max"]) for c in R["edge"])
#%% split
for s in EDGE2_SIZES:
    R["edge2"].append(mesh_solve("edge2 %g" % s, face=2.5, edge=s))
", ".join("%g mm: %d el, fillet %.2f td %.5f" % (c["edge"], c["elements"], c["eqv_fillet_max"], c["td_max"]) for c in R["edge2"])
#%% split
# Final mesh: 1.25 mm face sizing (the converged point of the face-sizing study).
R["final"] = mesh_solve("final", face=1.25)
R["final"]["sx_profile"] = plot_data(RES["sx_path"])
R["final"]["fillet"] = fillet_profile()
I = {"default_mesh": I0}
I["model"] = shot(AN, "model.png")
I["fix"] = shot(FIX, "bc_fixed.png")
I["force"] = shot(FRC, "bc_force.png")
I["mesh"] = shot(Model.Mesh, "mesh.png")
I["mesh_fillet"] = shot(Model.Mesh, "mesh_fillet.png", frame=FILLET_Z)
I["deformed"] = shot(RES["td"], "deformed_vs_undeformed.png", wire=True)
I["td"] = shot(RES["td"], "total_deformation.png", true_scale=True)
I["dy"] = shot(RES["dy"], "dir_deformation_y.png", true_scale=True)
I["eqv"] = shot(RES["eqv"], "von_mises.png", true_scale=True)
I["eqv_fillet_zoom"] = shot(RES["eqv"], "von_mises_fillet_zoom.png", frame=FILLET_Z, true_scale=True)
I["eqv_wall_zoom"] = shot(RES["eqv"], "von_mises_wall_zoom.png", frame=WALL_Z, true_scale=True)
I["sx_path"] = shot(RES["sx_path"], "sx_path.png", true_scale=True)
I["fr"] = shot(RES["fr"], "reaction_force.png")
I["mr"] = shot(RES["mr"], "reaction_moment.png")
R["images"] = I
save_json(os.path.join(OUT, "results.json"), R)
"final: %s; fillet keys %s; problems %s" % (
    dict((k, v) for k, v in R["final"].items() if k not in ("sx_profile", "fillet")),
    R["final"]["fillet"].get("keys"), PROBLEMS)
#%% split
fatigue("R-1")
#%% split
fatigue("R-0.5_goodman", ratio=-0.5, theory="Goodman")
#%% split
save_json(os.path.join(OUT, "results.json"), R)
#%% split
adaptive("fillet_5", "eqv_fillet", 5.0)
#%% split
adaptive("fillet_1", "eqv_fillet", 1.0)
#%% split
save_json(os.path.join(OUT, "results.json"), R)
json.dumps({"adaptive": dict((t, dict((k, v) for k, v in d.items() if k != "history" and not k.startswith("img")))
                             for t, d in R["adaptive"].items()), "fatigue": R["fatigue"], "problems": PROBLEMS})
