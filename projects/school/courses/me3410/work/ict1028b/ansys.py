# In-class tutorial 10-28, problem 2 (bonus): long pressurized concrete block with a circular cavity, 2D plane strain.
# Runs inside Mechanical with pipeline/mech_common.py and work/test1/line_common.py (solve_retry).
# --var ASSETS, OUT (space-free folders; see run_ansys.sh).
import math

Q_LEFT, Q_RIGHT, P_LAT = 50.0, 25.0, 10.0          # MPa
HOLE_C, HOLE_R = (100.0, 50.0), 25.0
FACE_SIZES = [20.0, 10.0, 5.0, 2.5]                # face sizing study (mm), no local control
EDGE_SIZES = [2.0, 1.0, 0.5, 0.25]                 # hole + fillet edge sizing, face at 2.5 mm
FINAL = (2.5, 0.5)                                 # final mesh: face 2.5 mm, edges 0.5 mm
RADII = [5.0, 10.0, 30.0, 40.0]                    # fillet study (R20 is the main model)
PROBLEMS = []
R = {"default": None, "face": [], "edge": [], "adaptive": {}, "radius": {}, "nohole": {}, "problems": PROBLEMS}
NMM = MechanicalUnitSystem.StandardNMM

FULL = ((0.17, 0.1), 0.56)
HOLE_Z = ((0.1, 0.05), 0.11)
FILLET_Z = ((0.162, 0.108), 0.07)
BASE_Z = ((0.03, 0.02), 0.09)


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


def near(e, x=None, y=None, ln=None, tol=0.5):
    ok = True
    if x is not None:
        ok = ok and abs(e["c"][0] - x) < tol
    if y is not None:
        ok = ok and abs(e["c"][1] - y) < tol
    if ln is not None:
        ok = ok and abs(e["len"] - ln) < tol
    return ok


def setup(step, fillet_r=20.0, hole=True):
    """New geometry in the current (already New()'d) project: plane strain, concrete, BCs, loads, results."""
    global AN, FIX, PRES, RES, FACE_SIZ, EDGE_SIZ, E, NS, PATHS
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = NMM
    import_geometry(os.path.join(ASSETS, step), two_d=True)
    Model.Geometry.Model2DBehavior = Model2DBehavior.PlaneStrain
    import_materials(os.path.join(ASSETS, "concrete_handout.xml"), ["Concrete (handout)"])
    for b in bodies():
        b.Material = "Concrete (handout)"
    es = edges_mm()
    E = {}
    E["base"] = pick(es, lambda e: near(e, y=0, ln=400), "base", 1)
    E["left"] = pick(es, lambda e: near(e, x=0, ln=200), "left", 1)
    E["right"] = pick(es, lambda e: near(e, x=400, ln=100), "right", 1)
    E["top_left"] = pick(es, lambda e: near(e, y=200, ln=150), "top left", 1)
    E["top_right"] = pick(es, lambda e: near(e, x=325, y=100, ln=150), "top right (loaded)", 1)
    E["fillet"] = pick(es, lambda e: abs(e["len"] - fillet_r * math.pi / 2) < 0.05 and e["c"][0] < 150 + fillet_r + 0.5
                       and e["c"][1] < 100 + fillet_r + 0.5, "fillet", 1)
    if hole:
        E["hole"] = pick(es, lambda e: math.hypot(e["c"][0] - HOLE_C[0], e["c"][1] - HOLE_C[1]) < HOLE_R and e["len"] < 160,
                         "hole")
    R["edges"] = E
    NS = dict((k, named_selection(k.upper(), v)) for k, v in E.items())
    NS["face"] = named_selection("BLOCK", [f.Id for f in geo_faces()])
    NS["refine"] = named_selection("HOLE_AND_FILLET", E["fillet"] + E.get("hole", []))

    FACE_SIZ = Model.Mesh.AddSizing()
    FACE_SIZ.Location = NS["face"]
    FACE_SIZ.Name = "Face Sizing"
    EDGE_SIZ = Model.Mesh.AddSizing()
    EDGE_SIZ.Location = NS["refine"]
    EDGE_SIZ.Name = "Edge Sizing (hole + R%g fillet)" % fillet_r

    AN = Model.AddStaticStructuralAnalysis()
    FIX = AN.AddFixedSupport()
    FIX.Location = NS["base"]
    FIX.Name = "Fixed support: base (y = 0)"
    PRES = {}
    for key, mag, label in (("top_left", Q_LEFT, "q = 50 MPa on the left top"),
                            ("top_right", Q_RIGHT, "q = 25 MPa on the right top (x 250-400)"),
                            ("left", P_LAT, "p = 10 MPa lateral, left side"),
                            ("right", P_LAT, "p = 10 MPa lateral, right side")):
        p = AN.AddPressure()
        p.Location = NS[key]
        p.Magnitude.Output.DiscreteValues = [Quantity("%r [MPa]" % mag)]
        p.Name = "Pressure: " + label
        PRES[key] = p

    cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
    PATHS = {}
    for key, (x0, y0, x1, y1) in (("h50", (0, 50, 400, 50)), ("v100", (100, 0, 100, 200))):
        pth = cg.AddPath()
        pth.PathType = PathScopingType.Points
        pth.StartXCoordinate = Quantity("%r [mm]" % x0)
        pth.StartYCoordinate = Quantity("%r [mm]" % y0)
        pth.EndXCoordinate = Quantity("%r [mm]" % x1)
        pth.EndYCoordinate = Quantity("%r [mm]" % y1)
        pth.NumberOfSamplingPoints = 201
        pth.Name = "Path %s" % key
        PATHS[key] = pth

    sol = AN.Solution
    RES = {}
    RES["eqv"] = sol.AddEquivalentStress()
    RES["td"] = sol.AddTotalDeformation()
    RES["dy"] = sol.AddDirectionalDeformation()
    RES["dy"].NormalOrientation = NormalOrientationType.YAxis
    RES["dx"] = sol.AddDirectionalDeformation()
    RES["dx"].NormalOrientation = NormalOrientationType.XAxis
    for k, ax in (("sx", NormalOrientationType.XAxis), ("sy", NormalOrientationType.YAxis), ("sz", NormalOrientationType.ZAxis)):
        RES[k] = sol.AddNormalStress()
        RES[k].NormalOrientation = ax
    RES["sxy"] = sol.AddShearStress()
    RES["s1"] = sol.AddMaximumPrincipalStress()
    RES["s3"] = sol.AddMinimumPrincipalStress()
    scoped = ["fillet"] + (["hole"] if hole else [])
    for where in scoped:
        for k, fn in (("eqv", sol.AddEquivalentStress), ("s1", sol.AddMaximumPrincipalStress),
                      ("s3", sol.AddMinimumPrincipalStress), ("sx", sol.AddNormalStress), ("sy", sol.AddNormalStress),
                      ("sxy", sol.AddShearStress)):
            o = fn()
            if k in ("sx", "sy"):
                o.NormalOrientation = NormalOrientationType.XAxis if k == "sx" else NormalOrientationType.YAxis
            o.Location = NS[where]
            o.Name = "%s on %s" % (k, where)
            RES["%s_%s" % (k, where)] = o
    for pk, pth in PATHS.items():
        for k, ax in (("sx", NormalOrientationType.XAxis), ("sy", NormalOrientationType.YAxis)):
            o = sol.AddNormalStress()
            o.NormalOrientation = ax
            o.ScopingMethod = GeometryDefineByType.Path
            o.Location = pth
            o.Name = "%s along %s" % (k, pth.Name)
            RES["%s_%s" % (k, pk)] = o
    RES["fr"] = sol.AddForceReaction()
    RES["fr"].BoundaryConditionSelection = FIX
    return "setup %s: %s" % (step, E)


def read(d):
    d["state"] = str(AN.Solution.ObjectState)
    for k, o in RES.items():
        if k in ("fr", "td", "dx", "dy") or "_h50" in k or "_v100" in k:
            continue
        d[k + "_max"] = qval(o.Maximum, "MPa")
        d[k + "_min"] = qval(o.Minimum, "MPa")
    d["td_max"] = qval(RES["td"].Maximum, "mm")
    d["dy_min"] = qval(RES["dy"].Minimum, "mm")
    d["dy_max"] = qval(RES["dy"].Maximum, "mm")
    d["dx_min"] = qval(RES["dx"].Minimum, "mm")
    d["dx_max"] = qval(RES["dx"].Maximum, "mm")
    d["Rx"], d["Ry"] = qval(RES["fr"].XAxis, "N"), qval(RES["fr"].YAxis, "N")
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


def edge_profile(where, keys=("sx", "sy", "sxy", "eqv", "s1", "s3")):
    """Result values at every node of an edge, with node coordinates (mm): rows [x, y, v1, v2, ...]."""
    out = {"keys": list(keys)}
    try:
        md = AN.MeshData
        xy = {}
        for gid in E[where]:
            for n in md.MeshRegionById(gid).NodeIds:
                nd = md.NodeById(n)
                xy[n] = (nd.X, nd.Y)
        k = 1000.0 if max(abs(c) for p in xy.values() for c in p) < 1.0 else 1.0
        cols = {}
        for key in keys:
            pd = plot_data(RES["%s_%s" % (key, where)])
            if not pd:
                continue
            nk = [kk for kk in pd if kk.lower().startswith("node")][0]
            cols[key] = dict((int(n), float(v)) for n, v in zip(pd[nk], pd["Values"]))
        out["rows"] = [[xy[n][0] * k, xy[n][1] * k] + [cols[key].get(n) for key in keys if key in cols]
                       for n in xy if all(n in cols[key] for key in cols)]
        out["have"] = [key for key in keys if key in cols]
    except Exception as ex:
        PROBLEMS.append("edge profile %s: %s" % (where, str(ex)[:200]))
    return out


def paths():
    return dict(("%s_%s" % (k, p), plot_data(RES["%s_%s" % (k, p)])) for p in PATHS for k in ("sx", "sy"))


def stress_tool():
    """Mohr-Coulomb stress tool (brittle concrete: tensile 3 MPa, compressive 40 MPa)."""
    d = {}
    try:
        st = AN.Solution.AddStressTool()
        st.Theory = SafetyTheoryType.MohrCoulombStress
        st.TensileLimitType = SafetyLimitType.UltimatePerMaterial      # default yield limits are 0 for concrete
        st.CompressiveLimitType = SafetyLimitType.UltimatePerMaterial
        st.Name = "Stress Tool: Mohr-Coulomb (St = 3, Sc = 40 MPa)"
        kids = list(st.Children)
        sf = kids[0] if kids else st.AddSafetyFactor()
        AN.Solution.EvaluateAllResults()
        d["sf_min"] = float(str(sf.Minimum).split()[0])
        d["sf_max"] = float(str(sf.Maximum).split()[0])
        d["img"] = shot(sf, "mohr_coulomb_sf.png", true_scale=True)
        d["img_hole"] = shot(sf, "mohr_coulomb_sf_hole.png", frame=HOLE_Z, true_scale=True)
        d["img_fillet"] = shot(sf, "mohr_coulomb_sf_fillet.png", frame=FILLET_Z, true_scale=True)
        R["mohr"] = d
    except Exception as ex:
        PROBLEMS.append("stress tool: %s" % str(ex)[:200])
    return d


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
        d["nodes"], d["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
        read(d)
        try:
            d["last_change_pct"] = float(str(conv.LastChange).split()[0])
        except Exception:
            d["last_change_pct"] = None
        d["img_mesh"] = shot(Model.Mesh, "adapt_%s_mesh.png" % tag)
    except Exception as ex:
        d["error"] = str(ex)[:300]
    conv.Delete()
    AN.Solution.MaximumRefinementLoops = 1
    R["adaptive"][tag] = d
    return "%s: %s" % (tag, dict((k, v) for k, v in d.items() if not k.startswith("img")))


def short(d):
    keys = ("elements", "nodes", "eqv_max", "eqv_hole_max", "s3_hole_min", "s1_hole_max", "eqv_fillet_max",
            "s3_fillet_min", "td_max", "dy_min", "Rx", "Ry")
    return ", ".join("%s %s" % (k, ("%.4g" % d[k]) if isinstance(d.get(k), float) else d.get(k)) for k in keys if k in d)
ExtAPI.DataModel.Project.New()
#%% split
setup("block_R20.step")
#%% split
R["default"] = mesh_solve("default")
I0 = shot(Model.Mesh, "mesh_default.png")
short(R["default"])
#%% split
for s in FACE_SIZES:
    R["face"].append(mesh_solve("face %g" % s, face=s))
" | ".join(short(c) for c in R["face"])
#%% split
for s in EDGE_SIZES:
    R["edge"].append(mesh_solve("edge %g" % s, face=2.5, edge=s))
" | ".join(short(c) for c in R["edge"])
#%% split
R["final"] = mesh_solve("final", face=FINAL[0], edge=FINAL[1])
R["final"]["hole"] = edge_profile("hole")
R["final"]["fillet"] = edge_profile("fillet")
R["final"]["paths"] = paths()
I = {"default_mesh": I0}
I["model"] = shot(AN, "model.png")
I["fix"] = shot(FIX, "bc_fixed.png")
for k, p in PRES.items():
    I["p_" + k] = shot(p, "load_%s.png" % k)
I["mesh"] = shot(Model.Mesh, "mesh.png")
I["mesh_hole"] = shot(Model.Mesh, "mesh_hole.png", frame=HOLE_Z)
I["mesh_fillet"] = shot(Model.Mesh, "mesh_fillet.png", frame=FILLET_Z)
I["deformed"] = shot(RES["td"], "deformed_vs_undeformed.png", wire=True)
for k in ("td", "dy", "dx", "eqv", "sx", "sy", "sxy", "sz", "s1", "s3"):
    I[k] = shot(RES[k], "%s.png" % k, true_scale=True)
for k in ("eqv", "s1", "s3", "sx", "sy"):
    I[k + "_hole"] = shot(RES[k], "%s_hole_zoom.png" % k, frame=HOLE_Z, true_scale=True)
for k in ("eqv", "s3", "s1"):
    I[k + "_fillet"] = shot(RES[k], "%s_fillet_zoom.png" % k, frame=FILLET_Z, true_scale=True)
I["eqv_base"] = shot(RES["eqv"], "eqv_base_zoom.png", frame=BASE_Z, true_scale=True)
I["fr"] = shot(RES["fr"], "reaction_force.png")
R["images"] = I
save_json(os.path.join(OUT, "results.json"), R)
"final: %s; hole have %s rows %d; fillet rows %d; problems %s" % (
    short(R["final"]), R["final"]["hole"].get("have"), len(R["final"]["hole"].get("rows", [])),
    len(R["final"]["fillet"].get("rows", [])), PROBLEMS)
#%% split
stress_tool()
save_json(os.path.join(OUT, "results.json"), R)
"mohr %s problems %s" % (R.get("mohr"), PROBLEMS)
#%% split
adaptive("hole_2", "eqv_hole", 2.0)
#%% split
save_json(os.path.join(OUT, "results.json"), R)
#%% split
ExtAPI.DataModel.Project.New()
#%% split
setup("block_nohole.step", hole=False)
#%% split
R["nohole"] = mesh_solve("nohole", face=FINAL[0], edge=FINAL[1])
R["nohole"]["paths"] = paths()
R["nohole"]["fillet"] = edge_profile("fillet")
R["nohole"]["img_sy"] = shot(RES["sy"], "nohole_sy.png", true_scale=True)
R["nohole"]["img_sx"] = shot(RES["sx"], "nohole_sx.png", true_scale=True)
save_json(os.path.join(OUT, "results.json"), R)
"nohole: %s" % short(R["nohole"])
#%% split
ExtAPI.DataModel.Project.New()
#%% split
setup("block_R5.step", fillet_r=5.0)
#%% split
R["radius"]["5"] = mesh_solve("R5", face=FINAL[0], edge=FINAL[1])
R["radius"]["5"]["fillet"] = edge_profile("fillet")
short(R["radius"]["5"])
#%% split
ExtAPI.DataModel.Project.New()
#%% split
setup("block_R10.step", fillet_r=10.0)
#%% split
R["radius"]["10"] = mesh_solve("R10", face=FINAL[0], edge=FINAL[1])
R["radius"]["10"]["fillet"] = edge_profile("fillet")
short(R["radius"]["10"])
#%% split
ExtAPI.DataModel.Project.New()
#%% split
setup("block_R30.step", fillet_r=30.0)
#%% split
R["radius"]["30"] = mesh_solve("R30", face=FINAL[0], edge=FINAL[1])
R["radius"]["30"]["fillet"] = edge_profile("fillet")
short(R["radius"]["30"])
#%% split
ExtAPI.DataModel.Project.New()
#%% split
setup("block_R40.step", fillet_r=40.0)
#%% split
R["radius"]["40"] = mesh_solve("R40", face=FINAL[0], edge=FINAL[1])
R["radius"]["40"]["fillet"] = edge_profile("fillet")
save_json(os.path.join(OUT, "results.json"), R)
short(R["radius"]["40"]) + "; problems %s" % PROBLEMS
