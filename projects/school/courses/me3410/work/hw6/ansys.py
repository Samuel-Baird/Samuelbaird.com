# HW 6: L-bracket under distributed pressure, 2D plane stress.
# Runs inside Mechanical with pipeline/mech_common.py and work/test1/line_common.py (solve_retry).
# --var ASSETS, OUT (space-free folders; see run_ansys.sh).
import math

P_MPA = 2.5            # 250 N/cm^2
T_MM = 2.0             # 0.2 cm
SIZES = [4.0, 2.0, 1.0, 0.7]     # global element size (mm); fillet and holes get size/4
X_SEC = 140.0          # beam-theory check section (mm), well away from the fillet and the end hole
HOLES = {"TL": (20.0, -20.0), "R": (200.0, -20.0), "B": (20.0, -120.0)}
PROBLEMS = []
R = {"convergence": [], "adaptive": {}, "problems": PROBLEMS}
NMM = MechanicalUnitSystem.StandardNMM


FULL = ((0.085, -0.062), 0.32)      # whole bracket: focal point (m) and scene width (m)
CORNER_Z = ((0.009, -0.007), 0.03)  # wall/top corner close-up (x -6..24, y -17..3 mm)
CORNER_TIP = ((0.0015, -0.001), 0.004)  # 4 mm across the corner: the adaptive refinement
FILLET_Z = ((0.065, -0.065), 0.075)  # fillet close-up


def shot(obj, name, frame=FULL, wire=False, true_scale=False):
    """Front view framed explicitly (SetFit crops this part in batch mode, and a custom view vector skews it)."""
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
        cam.SceneHeight = Quantity("%r [m]" % (frame[1] * 800.0 / 1200.0))  # else it keeps the fitted height
        st = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        st.Width, st.Height = 1200, 800
        st.Resolution = GraphicsResolutionType.EnhancedResolution
        st.Background = GraphicsBackgroundType.White
        st.CurrentGraphicsDisplay = False
        path = os.path.join(OUT, name)
        Graphics.ExportImage(path, GraphicsImageExportFormat.PNG, st)
        return path
    finally:
        ExtAPI.Application.ActiveUnitSystem = prev


def edges_mm():
    es = [edge_info(e) for e in geo_edges()]
    k = 1000.0 if max(e["len"] for e in es) < 1.0 else 1.0   # GeoData may report metres
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
    global AN, FIX, PRES, RES, SIZ, PATH, CORNER
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = NMM
    import_geometry(os.path.join(ASSETS, "bracket_2d.step"), two_d=True)
    Model.Geometry.Model2DBehavior = Model2DBehavior.PlaneStress
    for b in bodies():
        b.Thickness = Quantity("%r [mm]" % T_MM)
        b.Material = "Structural Steel"   # E = 200 GPa, nu = 0.3: the handout's values
    es = edges_mm()
    E = {}
    E["wall"] = pick(es, lambda e: abs(e["c"][0]) < 0.5 and abs(e["len"] - 120) < 0.5, "wall edge", 1)
    E["top"] = pick(es, lambda e: abs(e["c"][1]) < 0.5 and abs(e["len"] - 200) < 0.5, "top edge", 1)
    E["fillet"] = pick(es, lambda e: abs(e["len"] - 50 * math.pi / 2) < 0.5, "fillet", 1)
    for k, (hx, hy) in HOLES.items():
        E["hole_" + k] = pick(es, lambda e, hx=hx, hy=hy: math.hypot(e["c"][0] - hx, e["c"][1] - hy) < 2.0
                              and e["len"] < 32.0, "hole " + k)
    R["edges"] = E
    ns = dict((k, named_selection(k.upper(), v)) for k, v in E.items())
    ns["holes"] = named_selection("HOLES", E["hole_TL"] + E["hole_R"] + E["hole_B"])
    # Vertex where the fixed wall edge meets the loaded top edge (x = 0, y = 0).
    vs = {}
    for asm in ExtAPI.DataModel.GeoData.Assemblies:
        for part in asm.Parts:
            for b in part.Bodies:
                for v in b.Vertices:
                    vs[v.Id] = (v.X, v.Y)
    k = 1000.0 if max(abs(c) for xy in vs.values() for c in xy) < 1.0 else 1.0
    corner = [i for i, (x, y) in vs.items() if abs(x * k) < 0.5 and abs(y * k) < 0.5]
    if len(corner) != 1:
        raise Exception("corner vertex: %s" % vs)
    CORNER = named_selection("CORNER_WALL_TOP", corner)

    SIZ = Model.Mesh.AddSizing()
    SIZ.Location = named_selection("REFINED_EDGES", E["fillet"] + E["hole_TL"] + E["hole_R"] + E["hole_B"])
    SIZ.Name = "Fillet + hole refinement (global size / 4)"

    AN = Model.AddStaticStructuralAnalysis()
    FIX = AN.AddFixedSupport()
    FIX.Location = ns["wall"]
    FIX.Name = "Fixed support: left edge bolted/welded to the wall"
    PRES = AN.AddPressure()
    PRES.Location = ns["top"]
    PRES.Magnitude.Output.DiscreteValues = [Quantity("%r [MPa]" % P_MPA)]
    PRES.Name = "Pressure 250 N/cm^2 (2.5 MPa) on the top edge"

    cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
    PATH = cg.AddPath()
    PATH.PathType = PathScopingType.Points
    PATH.StartXCoordinate = Quantity("%r [mm]" % X_SEC)
    PATH.StartYCoordinate = Quantity("0 [mm]")
    PATH.EndXCoordinate = Quantity("%r [mm]" % X_SEC)
    PATH.EndYCoordinate = Quantity("-40 [mm]")
    PATH.NumberOfSamplingPoints = 41
    PATH.Name = "Section x = 140 mm"

    sol = AN.Solution
    RES = {}
    RES["eqv"] = sol.AddEquivalentStress()
    RES["td"] = sol.AddTotalDeformation()
    RES["dy"] = sol.AddDirectionalDeformation()
    RES["dy"].NormalOrientation = NormalOrientationType.YAxis
    for key, loc, nm in (("eqv_fillet", ns["fillet"], "Equivalent stress on the R50 fillet"),
                         ("eqv_holes", ns["holes"], "Equivalent stress on the hole edges"),
                         ("eqv_corner", CORNER, "Equivalent stress at the wall/top corner (singular)")):
        RES[key] = sol.AddEquivalentStress()
        RES[key].Location = loc
        RES[key].Name = nm
    RES["sx_path"] = sol.AddNormalStress()
    RES["sx_path"].NormalOrientation = NormalOrientationType.XAxis
    RES["sx_path"].ScopingMethod = GeometryDefineByType.Path
    RES["sx_path"].Location = PATH
    RES["sx_path"].Name = "Normal stress X on section x = 140 mm"
    RES["fr"] = sol.AddForceReaction()
    RES["fr"].BoundaryConditionSelection = FIX
    RES["mr"] = sol.AddMomentReaction()
    RES["mr"].BoundaryConditionSelection = FIX
    return "setup: %s corner %s" % (E, corner)


def read(d):
    d["state"] = str(AN.Solution.ObjectState)
    for k, u in (("eqv", "MPa"), ("eqv_fillet", "MPa"), ("eqv_holes", "MPa"), ("eqv_corner", "MPa")):
        d[k + "_max"] = qval(RES[k].Maximum, u)
    d["td_max"] = qval(RES["td"].Maximum, "mm")
    d["dy_min"] = qval(RES["dy"].Minimum, "mm")
    d["sx_path_max"] = qval(RES["sx_path"].Maximum, "MPa")
    d["sx_path_min"] = qval(RES["sx_path"].Minimum, "MPa")
    fr, mr = RES["fr"], RES["mr"]
    d["Rx"], d["Ry"] = qval(fr.XAxis, "N"), qval(fr.YAxis, "N")
    d["Mz"] = qval(mr.ZAxis, "N mm")
    return d


def mesh_solve(size):
    Model = ExtAPI.DataModel.Project.Model
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity("%r [mm]" % size)
    SIZ.ElementSize = Quantity("%r [mm]" % (size / 4.0))
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    return read({"size": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements})


def path_profile():
    try:
        pd = RES["sx_path"].PlotData
        keys = [str(k) for k in pd.Keys]
        return dict((k, [float(v) for v in pd[k]]) for k in keys)
    except Exception as ex:
        PROBLEMS.append("path PlotData: %s" % str(ex)[:120])
        return None


def adaptive(tag, res, start, allowable=5.0, loops=6, depth=2, zoom=None):
    """Mechanical's Convergence tool: refine where the result changes most, re-solve, stop when
    the change between loops is below `allowable` %."""
    Model = ExtAPI.DataModel.Project.Model
    SIZ.Suppressed = True
    Model.Mesh.ElementSize = Quantity("%r [mm]" % start)
    conv = RES[res].AddConvergence()
    conv.Type = ConvergenceType.Maximum
    conv.AllowableChange = allowable
    AN.Solution.MaximumRefinementLoops = loops
    AN.Solution.RefinementDepth = depth
    d = {"result": res, "start": start, "allowable_pct": allowable, "loops_max": loops, "depth": depth}
    try:
        Model.Mesh.GenerateMesh()
        solve_retry(AN)
        d["nodes"] = Model.Mesh.Nodes
        d["converged"] = str(conv.Converged) if hasattr(conv, "Converged") else None
        try:
            d["last_change_pct"] = float(str(conv.LastChange).split()[0])
        except Exception:
            d["last_change_pct"] = None
        read(d)
        try:
            d["history"] = [(str(x.Caption), str(x.StringValue)) for x in conv.VisibleProperties]
            d["converged"] = dict(d["history"]).get("Converged")
        except Exception:
            pass
        d["img_mesh"] = shot(Model.Mesh, "adapt_%s_mesh.png" % tag)
        d["img_res"] = shot(RES[res], "adapt_%s_res.png" % tag, true_scale=True)
        for suffix, fr in (zoom or []):
            d["img_%s_mesh" % suffix] = shot(Model.Mesh, "adapt_%s_%s_mesh.png" % (tag, suffix), frame=fr)
            d["img_%s_res" % suffix] = shot(RES[res], "adapt_%s_%s_res.png" % (tag, suffix), frame=fr, true_scale=True)
    except Exception as ex:
        d["error"] = str(ex)[:300]
    conv.Delete()
    AN.Solution.MaximumRefinementLoops = 1
    SIZ.Suppressed = False
    R["adaptive"][tag] = d
    return "%s: %s" % (tag, dict((k, v) for k, v in d.items() if k not in ("history",) and not k.startswith("img")))
ExtAPI.DataModel.Project.New()
#%% split
setup()
#%% split
for s in SIZES:
    R["convergence"].append(mesh_solve(s))
", ".join("%g mm: %d nodes, eqv %.1f (fillet %.2f, corner %.1f) MPa, td %.5f mm" % (
    c["size"], c["nodes"], c["eqv_max"], c["eqv_fillet_max"], c["eqv_corner_max"], c["td_max"]) for c in R["convergence"])
#%% split
R["final"] = R["convergence"][-1]
R["final"]["sx_profile"] = path_profile()
I = {}
I["model"] = shot(AN, "model.png")
I["fix"] = shot(FIX, "bc_fixed.png")
I["pres"] = shot(PRES, "bc_pressure.png")
I["mesh"] = shot(Model.Mesh, "mesh.png")
I["mesh_fillet"] = shot(Model.Mesh, "mesh_fillet.png", frame=FILLET_Z)
I["mesh_corner"] = shot(Model.Mesh, "mesh_corner.png", frame=CORNER_Z)
I["deformed"] = shot(RES["td"], "deformed_vs_undeformed.png", wire=True)
I["td"] = shot(RES["td"], "total_deformation.png", true_scale=True)
I["dy"] = shot(RES["dy"], "dir_deformation_y.png", true_scale=True)
I["eqv"] = shot(RES["eqv"], "von_mises.png", true_scale=True)
I["eqv_corner_zoom"] = shot(RES["eqv"], "von_mises_corner_zoom.png", frame=CORNER_Z, true_scale=True)
I["eqv_fillet_zoom"] = shot(RES["eqv"], "von_mises_fillet_zoom.png", frame=FILLET_Z, true_scale=True)
I["sx_path"] = shot(RES["sx_path"], "sx_path.png", true_scale=True)
I["fr"] = shot(RES["fr"], "reaction_force.png")
I["mr"] = shot(RES["mr"], "reaction_moment.png")
R["images"] = I
save_json(os.path.join(OUT, "results.json"), R)
"images done; problems %s" % PROBLEMS
#%% split
adaptive("td", "td", 4.0)
#%% split
adaptive("eqv", "eqv", 4.0)
#%% split
adaptive("fillet", "eqv_fillet", 4.0)
#%% split
# Same tool on the global maximum, but starting from the 1 mm mesh, where the singular corner already
# carries the peak: every loop refines the corner and the peak keeps rising.
adaptive("eqv_fine", "eqv", 1.0, loops=4, depth=1, zoom=[("zoom", CORNER_Z), ("tip", CORNER_TIP)])
#%% split
save_json(os.path.join(OUT, "results.json"), R)
json.dumps({"final": dict((k, v) for k, v in R["final"].items() if k != "sx_profile"),
            "adaptive": dict((t, dict((k, v) for k, v in d.items() if k != "history" and not k.startswith("img")))
                             for t, d in R["adaptive"].items()), "problems": PROBLEMS})
