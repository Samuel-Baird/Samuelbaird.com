# HW 8: aluminium pipe elbow with a flange at each end. Steady-state thermal (100 C bore, h = 10 W/m^2 C to 30 C air)
# -> static structural with the imported body temperature and both flange outer faces fixed.
# Runs inside Mechanical with pipeline/mech_common.py and work/test1/line_common.py (solve_retry).
# --var ASSETS, OUT (space-free folders; see run_ansys.sh). Units inside: mm, N, MPa (StandardNMM).
import math

T_BORE, T_AIR, H_CONV, T_INIT = 100.0, 30.0, 10.0, 30.0   # C, C, W/m^2 C, C (tutorial values)
T_REF = 22.0                                              # structural environment / zero-strain temperature (C)
MAT = "Aluminum Alloy"
SIZES = [8.0, 6.0, 5.0, 4.0, 3.5, 3.0]   # global element size (mm); the pipe wall is 5 mm thick
NODE_LIMIT = 120000                # ANSYS Student stops at 128,000 nodes
PROBLEMS = []
R = {"convergence": [], "problems": PROBLEMS}
NMM = MechanicalUnitSystem.StandardNMM

ISO = "iso"
FULL = ((0.0, 0.075, 0.105), 0.34)              # whole elbow: focal point (m), scene width (m)
FL1 = ((0.0, 0.0, 0.012), 0.13)                 # flange 1 close-up
FL2 = ((0.0, 0.158, 0.170), 0.13)               # flange 2 close-up

# face areas (mm^2) from cad.py
A_FLANGE_OUT = math.pi / 4 * (100 ** 2 - 50 ** 2) - math.pi * 10 ** 2   # bolted face, 5576.3
A_FLANGE_IN = math.pi / 4 * (100 ** 2 - 60 ** 2) - math.pi * 10 ** 2    # pipe-side annulus, 4712.4
A_FLANGE_OD = math.pi * 100 * 20                                        # 6283.2
A_BOLT = math.pi * 10 * 20                                              # 628.3
A_BORE_LEG = math.pi * 50 * 100                                         # 15708.0 (flange bore + leg bore)
A_OUT_LEG = math.pi * 60 * 80                                           # 15079.6
A_BORE_BEND = math.pi ** 2 * 70 * 25                                    # 17271.6 (90 deg torus)
A_OUT_BEND = math.pi ** 2 * 70 * 30                                     # 20725.9


def faces_mm():
    fs = [face_info(f) for f in geo_faces()]
    k = 1000.0 if max(abs(c) for f in fs for c in f["c"]) < 1.0 else 1.0
    for f in fs:
        f["c"] = [v * k for v in f["c"]]
        f["area"] *= k * k
    return fs


def near(a, b, tol=0.005):
    return abs(a - b) <= tol * b


def pick(fs, cond, what, n=None):
    ids = [f["id"] for f in fs if cond(f)]
    if not ids or (n is not None and len(ids) != n):
        raise Exception("%s: found %s in %s" % (what, ids, [(f["id"], [round(v, 1) for v in f["c"]], round(f["area"], 1)) for f in fs]))
    return ids


def flange_no(f):
    """1 for faces on the first flange (z < 25), 2 for the second (y > 145)."""
    return 1 if f["c"][2] < 25 else 2


def mat_table(ed, prop, col):
    import materials
    p = materials.GetMaterialPropertyByName(ed, prop)
    out = {}
    for k in p.keys():
        try:
            out[str(k)] = [str(v) for v in p[k]]
        except Exception:
            out[str(k)] = str(p[k])
    return out


def setup():
    global TH, ST, TEMP, CONV, FIX1, FIX2, IBT, RT, RS, NS, F
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = NMM
    import_geometry(os.path.join(ASSETS, "elbow.step"))
    assign_material(MAT)
    m = [x for x in Model.Materials.Children if x.Name == MAT][0]
    ed = m.GetEngineeringDataMaterial()
    R["material"] = {}
    for prop in ("Elasticity", "Tensile Yield Strength", "Tensile Ultimate Strength", "Coefficient of Thermal Expansion",
                 "Thermal Conductivity", "Density", "Zero-Thermal-Strain Reference Temperature"):
        try:
            R["material"][prop] = mat_table(ed, prop, None)
        except Exception as ex:
            R["material"][prop] = "ERR " + str(ex)[:150]

    fs = faces_mm()
    R["faces_all"] = [(f["id"], [round(v, 2) for v in f["c"]], round(f["area"], 1)) for f in fs]
    F = {}
    F["fix1"] = pick(fs, lambda f: near(f["area"], A_FLANGE_OUT) and abs(f["c"][2]) < 0.5, "flange 1 outer face", 1)
    F["fix2"] = pick(fs, lambda f: near(f["area"], A_FLANGE_OUT) and abs(f["c"][1] - 170) < 0.5, "flange 2 outer face", 1)
    F["bore"] = pick(fs, lambda f: near(f["area"], A_BORE_LEG) or near(f["area"], A_BORE_BEND), "bore", 3)
    F["bend_out"] = pick(fs, lambda f: near(f["area"], A_OUT_BEND), "bend outer surface", 1)
    F["legs_out"] = pick(fs, lambda f: near(f["area"], A_OUT_LEG), "leg outer surfaces", 2)
    F["flange_od"] = pick(fs, lambda f: near(f["area"], A_FLANGE_OD), "flange rims", 2)
    F["flange_in"] = pick(fs, lambda f: near(f["area"], A_FLANGE_IN), "flange pipe-side faces", 2)
    F["bolts"] = pick(fs, lambda f: near(f["area"], A_BOLT), "bolt holes", 8)
    F["conv"] = F["legs_out"] + F["bend_out"] + F["flange_od"] + F["flange_in"]
    R["faces"] = F
    NS = dict((k, named_selection(k.upper(), v)) for k, v in F.items())

    # ---- Part I: steady-state thermal
    TH = Model.AddSteadyStateThermalAnalysis()
    ic = list(TH.InitialConditions)
    if ic:
        ic[0].InitialTemperatureValue = Quantity("%r [C]" % T_INIT)
    else:
        PROBLEMS.append("no initial-condition object")
    TEMP = TH.AddTemperature()
    TEMP.Location = NS["bore"]
    TEMP.Magnitude.Output.DiscreteValues = [Quantity("%r [C]" % T_INIT), Quantity("%r [C]" % T_BORE)]
    TEMP.Name = "Temperature 100 C: bore (pipe and both flanges)"
    CONV = TH.AddConvection()
    CONV.Location = NS["conv"]
    CONV.FilmCoefficient.Output.DiscreteValues = [Quantity("%r [W m^-1 m^-1 C^-1]" % H_CONV)]
    CONV.AmbientTemperature.Output.DiscreteValues = [Quantity("%r [C]" % T_AIR)]
    CONV.Name = "Convection h = 10 W/m2 C, 30 C: outside of pipe and flanges"
    s = TH.Solution
    RT = {}
    RT["temp"] = s.AddTemperature()
    RT["flux"] = s.AddTotalHeatFlux()
    RT["temp_out"] = s.AddTemperature()
    RT["temp_out"].Location = NS["conv"]
    RT["temp_out"].Name = "Temperature: convection faces"
    RT["temp_bend"] = s.AddTemperature()
    RT["temp_bend"].Location = NS["bend_out"]
    RT["temp_bend"].Name = "Temperature: bend outer surface"
    RT["temp_fix"] = s.AddTemperature()
    RT["temp_fix"].Location = NS["fix1"]
    RT["temp_fix"].Name = "Temperature: flange 1 bolted face"
    RT["flux_legs"] = s.AddTotalHeatFlux()
    RT["flux_legs"].Location = NS["legs_out"]
    RT["flux_legs"].Name = "Total heat flux: leg outer surfaces"
    RT["flux_bore"] = s.AddTotalHeatFlux()
    RT["flux_bore"].Location = NS["bore"]
    RT["flux_bore"].Name = "Total heat flux: bore"
    RT["q_temp"] = s.AddReactionProbe() if hasattr(s, "AddReactionProbe") else None
    if RT["q_temp"] is not None:
        RT["q_temp"].BoundaryConditionSelection = TEMP
        RT["q_temp"].Name = "Heat reaction: 100 C bore"
    RT["q_conv"] = s.AddReactionProbe() if hasattr(s, "AddReactionProbe") else None
    if RT["q_conv"] is not None:
        RT["q_conv"].BoundaryConditionSelection = CONV
        RT["q_conv"].Name = "Heat reaction: convection"

    # ---- Part II: static structural with the imported temperature
    ST = Model.AddStaticStructuralAnalysis()
    ST.EnvironmentTemperature = Quantity("%r [C]" % T_REF)
    ST.ImportLoad(TH)
    FIX1 = ST.AddFixedSupport()
    FIX1.Location = NS["fix1"]
    FIX1.Name = "Fixed support: flange 1 outer face"
    FIX2 = ST.AddFixedSupport()
    FIX2.Location = NS["fix2"]
    FIX2.Name = "Fixed support: flange 2 outer face"
    s = ST.Solution
    RS = {}
    RS["td"] = s.AddTotalDeformation()
    RS["eqv"] = s.AddEquivalentStress()
    RS["epel"] = s.AddEquivalentElasticStrain()
    RS["eptot"] = s.AddEquivalentTotalStrain() if hasattr(s, "AddEquivalentTotalStrain") else None
    RS["s1"] = s.AddMaximumPrincipalStress()
    for key, ns, nm in (("eqv_bend", NS["bend_out"], "Equivalent stress: bend outer surface"),
                        ("eqv_bore", NS["bore"], "Equivalent stress: bore"),
                        ("eqv_legs", NS["legs_out"], "Equivalent stress: leg outer surfaces"),
                        ("eqv_fix", NS["fix1"], "Equivalent stress: flange 1 bolted face")):
        RS[key] = s.AddEquivalentStress()
        RS[key].Location = ns
        RS[key].Name = nm
    st = s.AddStressTool()
    kids = list(st.Children)
    RS["sf"] = kids[0] if kids else st.AddSafetyFactor()
    RS["tool"] = st
    for key, fx in (("fr1", FIX1), ("fr2", FIX2)):
        RS[key] = s.AddForceReaction()
        RS[key].BoundaryConditionSelection = fx
    for key, fx in (("mr1", FIX1), ("mr2", FIX2)):
        RS[key] = s.AddMomentReaction()
        RS[key].BoundaryConditionSelection = fx
    return "setup: %s" % dict((k, len(v)) for k, v in F.items())


def qv(res, attr, unit):
    try:
        return qval(getattr(res, attr), unit)
    except Exception as ex:
        PROBLEMS.append("%s.%s: %s" % (res.Name, attr, str(ex)[:100]))
        return None


def location_of_max(an, res, lowest=False):
    """Coordinates (mm) and value of the node with the highest (or lowest) value of a nodal result."""
    pd = res.PlotData
    keys = [str(k) for k in pd.Keys]
    nk = [k for k in keys if k.lower().startswith("node")][0]
    vals = list(pd["Values"])
    nodes = list(pd[nk])
    f = min if lowest else max
    i = f(range(len(vals)), key=lambda j: vals[j])
    nd = an.MeshData.NodeById(int(nodes[i]))
    c = [nd.X, nd.Y, nd.Z]
    k = 1000.0 if max(abs(v) for v in c) < 1.0 else 1.0
    return [v * k for v in c]


def heat(probe):
    if probe is None:
        return None
    for attr in ("Heat", "HeatFlowRate", "Total"):
        if hasattr(probe, attr):
            try:
                return qval(getattr(probe, attr), "W")
            except Exception:
                pass
    PROBLEMS.append("heat probe attrs: %s" % [a for a in dir(probe) if not a.startswith("_")][:80])
    return None


def read_thermal(d):
    d["th_state"] = str(TH.Solution.ObjectState)
    for k in ("temp", "temp_out", "temp_bend", "temp_fix"):
        d[k + "_min"] = qv(RT[k], "Minimum", "C")
        d[k + "_max"] = qv(RT[k], "Maximum", "C")
    for k in ("flux", "flux_legs", "flux_bore"):
        d[k + "_min"] = qv(RT[k], "Minimum", "W m^-1 m^-1")
        d[k + "_max"] = qv(RT[k], "Maximum", "W m^-1 m^-1")
        d[k + "_avg"] = qv(RT[k], "Average", "W m^-1 m^-1")
    d["Q_bore"] = heat(RT["q_temp"])
    d["Q_conv"] = heat(RT["q_conv"])
    try:
        d["temp_min_loc"] = location_of_max(TH, RT["temp"], lowest=True)
    except Exception as ex:
        PROBLEMS.append("temp min loc: %s" % str(ex)[:100])
    return d


def read_struct(d):
    d["st_state"] = str(ST.Solution.ObjectState)
    d["td_max"] = qv(RS["td"], "Maximum", "mm")
    for k in ("eqv", "eqv_bend", "eqv_bore", "eqv_legs", "eqv_fix", "s1"):
        d[k + "_max"] = qv(RS[k], "Maximum", "MPa")
    d["eqv_bend_min"] = qv(RS["eqv_bend"], "Minimum", "MPa")
    d["epel_max"] = qv(RS["epel"], "Maximum", "mm mm^-1")
    if RS["eptot"] is not None:
        d["eptot_max"] = qv(RS["eptot"], "Maximum", "mm mm^-1")
    try:
        d["sf_min"] = float(RS["sf"].Minimum.Value) if hasattr(RS["sf"].Minimum, "Value") else float(RS["sf"].Minimum)
    except Exception as ex:
        PROBLEMS.append("sf: %s" % str(ex)[:100])
    for k in ("fr1", "fr2"):
        d[k] = [qv(RS[k], a, "N") for a in ("XAxis", "YAxis", "ZAxis")]
    for k in ("mr1", "mr2"):
        d[k] = [qv(RS[k], a, "N mm") for a in ("XAxis", "YAxis", "ZAxis")]
    for k in ("eqv", "eqv_bend", "eqv_legs"):
        try:
            d[k + "_loc"] = location_of_max(ST, RS[k])
        except Exception as ex:
            PROBLEMS.append("%s loc: %s" % (k, str(ex)[:100]))
    return d


def add_path(name, p0, p1, n=41):
    Model = ExtAPI.DataModel.Project.Model
    cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
    p = cg.AddPath()
    p.PathType = PathScopingType.Points
    p.StartXCoordinate, p.StartYCoordinate, p.StartZCoordinate = [Quantity("%r [mm]" % v) for v in p0]
    p.EndXCoordinate, p.EndYCoordinate, p.EndZCoordinate = [Quantity("%r [mm]" % v) for v in p1]
    p.NumberOfSamplingPoints = n
    p.Name = name
    return p


def path_result(sol, kind, path, name, axis=None):
    r = getattr(sol, kind)()
    if axis is not None:
        r.NormalOrientation = axis
    r.ScopingMethod = GeometryDefineByType.Path
    r.Location = path
    r.Name = name
    return r


def add_paths():
    """Through-wall lines at the middle of leg 1 (z = 60) and lines along each flange rim from the fixed face."""
    global P, RP
    P = {}
    P["wall_top"] = add_path("Leg 1 wall at z = 60, top (y = 25..30)", (0.0, 25.02, 60.0), (0.0, 29.98, 60.0), 21)
    P["wall_bot"] = add_path("Leg 1 wall at z = 60, bottom (y = -30..-25)", (0.0, -29.98, 60.0), (0.0, -25.02, 60.0), 21)
    P["wall_side"] = add_path("Leg 1 wall at z = 60, side (x = 25..30)", (25.02, 0.0, 60.0), (29.98, 0.0, 60.0), 21)
    P["rim1"] = add_path("Flange 1 rim at x = 50, from the fixed face (z = 0..20)", (49.95, 0.0, 0.0), (49.95, 0.0, 20.0), 41)
    P["rim2"] = add_path("Flange 2 rim at x = 50, from the fixed face (y = 170..150)", (49.95, 170.0, 170.0), (49.95, 150.0, 170.0), 41)
    RP = {}
    RP["t_wall"] = path_result(TH.Solution, "AddTemperature", P["wall_top"], "Temperature through the leg 1 wall")
    RP["q_wall"] = path_result(TH.Solution, "AddTotalHeatFlux", P["wall_top"], "Total heat flux through the leg 1 wall")
    for k in ("wall_top", "wall_bot", "wall_side"):
        RP["sz_" + k] = path_result(ST.Solution, "AddNormalStress", P[k], "Normal stress Z: " + P[k].Name,
                                   NormalOrientationType.ZAxis)
    for k in ("rim1", "rim2"):
        RP["eqv_" + k] = path_result(ST.Solution, "AddEquivalentStress", P[k], "Equivalent stress: " + P[k].Name)
    return "paths: %s" % list(P.keys())


def plot_data(res):
    try:
        pd = res.PlotData
        return dict((str(k), [v for v in pd[str(k)]]) for k in pd.Keys)
    except Exception as ex:
        PROBLEMS.append("PlotData %s: %s" % (res.Name, str(ex)[:120]))
        return None


def path_unit(k):
    if k.startswith("sz") or k.startswith("eqv") or k.startswith("s1") or k.startswith("s3"):
        return "MPa"
    return "C" if k.startswith("t_") else "W m^-1 m^-1"


def read_paths(d):
    for k, r in RP.items():
        try:
            d[k + "_min"] = qval(r.Minimum, path_unit(k))
            d[k + "_max"] = qval(r.Maximum, path_unit(k))
        except Exception as ex:
            PROBLEMS.append("path %s: %s" % (k, str(ex)[:100]))
    return d


def mesh_solve(size):
    Model = ExtAPI.DataModel.Project.Model
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity("%r [mm]" % size)
    Model.Mesh.GenerateMesh()
    d = {"size": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    if d["nodes"] > NODE_LIMIT:
        d["skipped"] = "over node limit"
        return d
    solve_retry(TH)
    read_thermal(d)
    solve_retry(ST)
    read_struct(d)
    return read_paths(d)


def view_export(obj, path, view="iso", frame=None, true_scale=False, wire=False, width=1400, height=900):
    """Named view (iso / back_iso / front / right ...), re-centred on frame = ((x, y, z) m, scene width m)."""
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
                 "right": ViewOrientationType.Right, "left": ViewOrientationType.Left, "back": ViewOrientationType.Back,
                 "top": ViewOrientationType.Top, "bottom": ViewOrientationType.Bottom}
        cam.SetSpecificViewOrientation(names[view])
        cam.SetFit()
        if view == "back_iso":
            cam.Rotate(180.0, CameraAxisType.ScreenY)
            cam.SetFit()
        if frame is None:
            frame = FULL
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


def shots(items):
    out = {}
    for key, obj, view, kw in items:
        try:
            out[key] = view_export(obj, os.path.join(OUT, key + ".png"), view=view, **kw)
        except Exception as ex:
            PROBLEMS.append("image %s: %s" % (key, str(ex)[:120]))
    return out


def imported_temperature():
    for c in ST.Children:
        if "Imported" in c.Name or "ImportedLoad" in str(type(c)):
            for g in c.Children:
                return g
            return c
    return None


def summary(c):
    f, m = c.get("fr1") or [0, 0, 0], c.get("mr1") or [0, 0, 0]
    return ("%g mm: %d nodes, Q %.2f W, Tmin %.3f, td %.4f, eqv %.1f bend %.1f legs %.1f rim1 %.1f rim2 %.1f, "
            "Fy %.0f Fz %.0f Mx %.0f" % (c["size"], c["nodes"], c.get("Q_bore") or 0, c.get("temp_min") or 0,
                                        c.get("td_max") or 0, c.get("eqv_max") or 0, c.get("eqv_bend_max") or 0,
                                        c.get("eqv_legs_max") or 0, c.get("eqv_rim1_max") or 0,
                                        c.get("eqv_rim2_max") or 0, f[1], f[2], m[0]))
ExtAPI.DataModel.Project.New()
#%% split
setup()
#%% split
add_paths()
#%% split
for s in SIZES:
    R["convergence"].append(mesh_solve(s))
    save_json(os.path.join(OUT, "results.json"), R)
    if R["convergence"][-1].get("skipped"):
        break
"; ".join(summary(c) for c in R["convergence"] if not c.get("skipped"))
#%% split
fin = [c for c in R["convergence"] if not c.get("skipped")][-1]
if R["convergence"][-1].get("skipped"):           # re-mesh at the finest size that solved
    fin = mesh_solve(fin["size"])
R["final"] = fin
R["profiles"] = dict((k, plot_data(r)) for k, r in RP.items())
save_json(os.path.join(OUT, "results.json"), R)
"final %g mm; problems %s" % (fin["size"], PROBLEMS)
#%% split
IBT = imported_temperature()
R["ibt"] = None if IBT is None else IBT.Name
I = {}
I.update(shots([
    ("th_model", TH, ISO, {}), ("th_temp_bc", TEMP, ISO, {}), ("th_conv", CONV, ISO, {}), ("th_conv_back", CONV, "back_iso", {}),
    ("mesh", Model.Mesh, ISO, {}), ("mesh_fl1", Model.Mesh, "back_iso", {"frame": FL1}),
    ("temp", RT["temp"], ISO, {}), ("temp_back", RT["temp"], "back_iso", {}), ("temp_fl2", RT["temp"], ISO, {"frame": FL2}),
    ("flux", RT["flux"], ISO, {}), ("flux_back", RT["flux"], "back_iso", {}), ("flux_fl2", RT["flux"], ISO, {"frame": FL2}),
    ("st_model", ST, ISO, {}), ("st_fix1", FIX1, "back_iso", {}), ("st_fix2", FIX2, ISO, {}),
    ("deformed", RS["td"], ISO, {"wire": True}), ("td", RS["td"], ISO, {}),
    ("eqv", RS["eqv"], ISO, {"true_scale": True}), ("eqv_back", RS["eqv"], "back_iso", {"true_scale": True}),
    ("eqv_fl2", RS["eqv"], ISO, {"true_scale": True, "frame": FL2}),
    ("eqv_bend", RS["eqv_bend"], ISO, {"true_scale": True}), ("eqv_bore", RS["eqv_bore"], "back_iso", {"true_scale": True}),
    ("epel", RS["epel"], ISO, {"true_scale": True}), ("s1", RS["s1"], ISO, {"true_scale": True}),
    ("sf", RS["sf"], ISO, {"true_scale": True}), ("sf_back", RS["sf"], "back_iso", {"true_scale": True}),
    ("fr1", RS["fr1"], ISO, {}), ("mr1", RS["mr1"], ISO, {}),
]))
if IBT is not None:
    I.update(shots([("ibt", IBT, ISO, {}), ("ibt_back", IBT, "back_iso", {})]))
R["images"] = I
save_json(os.path.join(OUT, "results.json"), R)
"images %d; ibt %s; problems %s" % (len(I), R["ibt"], PROBLEMS)
