# HW 7 Q1: equilateral triangle plate, 2D plane stress and 3D models.
# Runs inside Mechanical with pipeline/mech_common.py. --var ASSETS, OUT.
import math
import traceback

F_C = 15000.0                     # lbf, horizontal (+x) at hole C
RP = 3.5
HOLES = {"A": (RP * math.cos(math.radians(210)), RP * math.sin(math.radians(210))),
         "B": (RP * math.cos(math.radians(330)), RP * math.sin(math.radians(330))),
         "C": (0.0, RP)}
SIZES = {"2d": [0.4, 0.2, 0.1, 0.05], "3d": [0.4, 0.3, 0.2, 0.15]}
PROBLEMS = []
R = {"2d": {"convergence": []}, "3d": {"convergence": []}, "problems": PROBLEMS}


def hole_entities(kind):
    """Edges (2D) or faces (3D) of each small hole, found by centroid near the hole centre."""
    ents = [edge_info(e) for e in geo_edges()] if kind == "2d" else [face_info(f) for f in geo_faces()]
    out = {}
    for k, (hx, hy) in HOLES.items():
        # GeoData coordinates are in mm even for an inch STEP; hole circumference 1.57 in = 39.9 mm.
        out[k] = [e["id"] for e in ents
                  if math.hypot(e["c"][0] / 25.4 - hx, e["c"][1] / 25.4 - hy) < 0.3
                  and (e.get("len", 0) / 25.4 < 1.7 if kind == "2d" else e["area"] / 645.16 < 1.7)]
        if not out[k]:
            raise Exception("hole %s not found: %s" % (k, ents))
    return out


def setup(kind):
    global AN, SUP, RES, LOAD
    Model = ExtAPI.DataModel.Project.Model
    ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
    step = os.path.join(ASSETS, "q1_plate_%s.step" % kind)
    import_geometry(step, two_d=(kind == "2d"))
    if kind == "2d":
        Model.Geometry.Model2DBehavior = Model2DBehavior.PlaneStress
        for b in bodies():
            b.Thickness = Quantity("1 [in]")
    for b in bodies():
        b.Material = "Structural Steel"
    H = hole_entities(kind)
    R[kind]["holes"] = H
    ns = dict((k, named_selection("HOLE_" + k, v)) for k, v in H.items())
    global HOLE_SIZING
    HOLE_SIZING = Model.Mesh.AddSizing()
    HOLE_SIZING.Location = named_selection("PIN_HOLES", H["A"] + H["B"] + H["C"])
    HOLE_SIZING.Name = "Pin-hole refinement (global size / 4)"
    AN = Model.AddStaticStructuralAnalysis()
    SUP = {}
    for k in ("A", "B"):
        s = AN.AddCylindricalSupport()
        s.Location = ns[k]
        s.Radial = FixedOrFree.Fixed
        s.Axial = FixedOrFree.Fixed
        s.Tangential = FixedOrFree.Free
        s.Name = "Cylindrical support %s (radial, axial fixed; tangential free)" % k
        SUP[k] = s
    # Remote force through the centre of hole C, deformable behaviour: acts like a pin pulling
    # the hole and keeps exact equilibrium in both 2D and 3D. (A Bearing Load on 2D edges gave a
    # mesh-dependent total of 15,137-15,610 lbf in this release, so it is not used.)
    LOAD = AN.AddRemoteForce()
    LOAD.Location = ns["C"]
    LOAD.DefineBy = LoadDefineBy.Components
    LOAD.XComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % F_C)]
    LOAD.Behavior = LoadBehavior.Deformable
    LOAD.Name = "Remote force 15,000 lbf (+x) at hole C (deformable)"
    sol = AN.Solution
    RES = {}
    RES["eqv"] = sol.AddEquivalentStress()
    RES["td"] = sol.AddTotalDeformation()
    RES["dx"] = sol.AddDirectionalDeformation()
    RES["dx"].NormalOrientation = NormalOrientationType.XAxis
    RES["dy"] = sol.AddDirectionalDeformation()
    RES["dy"].NormalOrientation = NormalOrientationType.YAxis
    for key, base in (("td_C", "td"), ("dx_C", "dx"), ("dy_C", "dy")):
        if base == "td":
            RES[key] = sol.AddTotalDeformation()
        else:
            RES[key] = sol.AddDirectionalDeformation()
            RES[key].NormalOrientation = NormalOrientationType.XAxis if base == "dx" else NormalOrientationType.YAxis
        RES[key].Location = ns["C"]
        RES[key].Name = {"td_C": "Total deformation at C", "dx_C": "X deformation at C", "dy_C": "Y deformation at C"}[key]
    for k in ("A", "B"):
        fr = sol.AddForceReaction()
        fr.BoundaryConditionSelection = SUP[k]
        fr.Name = "Reaction at %s" % k
        RES["fr_" + k] = fr
    return "%s setup: holes %s" % (kind, H)


def mesh_solve(kind, size, images=False):
    Model = ExtAPI.DataModel.Project.Model
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    HOLE_SIZING.ElementSize = Quantity("%r [in]" % (size / 4.0))
    Model.Mesh.GenerateMesh()
    AN.Solve(True)
    AN.Solution.EvaluateAllResults()
    d = {"size_in": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements, "state": str(AN.Solution.ObjectState)}
    d["eqv_max_psi"] = qval(RES["eqv"].Maximum, "psi")
    d["td_max_in"] = qval(RES["td"].Maximum, "in")
    for key in ("td_C", "dx_C", "dy_C"):
        d[key + "_avg_in"] = qval(RES[key].Average, "in")
    for k in ("A", "B"):
        fr = RES["fr_" + k]
        d["R%s" % k] = {"x": qval(fr.XAxis, "lbf"), "y": qval(fr.YAxis, "lbf"), "z": qval(fr.ZAxis, "lbf"), "total": qval(fr.Total, "lbf")}
    if images:
        V2 = dict(view="front", width=1000, height=700, units=MechanicalUnitSystem.StandardBIN)
        V = V2 if kind == "2d" else dict(view="iso", width=1000, height=700, units=MechanicalUnitSystem.StandardBIN, true_scale=True)
        imgs = {}
        imgs["model"] = export_image(AN, os.path.join(OUT, "q1_%s_model.png" % kind), **V)
        imgs["mesh"] = export_image(Model.Mesh, os.path.join(OUT, "q1_%s_mesh.png" % kind), **V)
        for key in ("eqv", "td", "dx", "dy", "td_C", "dx_C", "dy_C", "fr_A", "fr_B"):
            imgs[key] = export_image(RES[key], os.path.join(OUT, "q1_%s_%s.png" % (kind, key)), **V)
        if kind == "3d":
            imgs["eqv_front"] = export_image(RES["eqv"], os.path.join(OUT, "q1_3d_eqv_front.png"), **V2)
        d["images"] = imgs
    return d


def run_series(kind):
    for s in SIZES[kind]:
        R[kind]["convergence"].append(mesh_solve(kind, s))
    c = R[kind]["convergence"]
    return "%s: " % kind + ", ".join("%g in: %d nodes, %.0f psi" % (x["size_in"], x["nodes"], x["eqv_max_psi"]) for x in c)
ExtAPI.DataModel.Project.New()
#%% split
setup("2d")
#%% split
run_series("2d")
#%% split
R["2d"]["final"] = mesh_solve("2d", SIZES["2d"][-1], images=True)
"2d final done"
#%% split
ExtAPI.DataModel.Project.New()
#%% split
setup("3d")
#%% split
run_series("3d")
#%% split
R["3d"]["final"] = mesh_solve("3d", SIZES["3d"][-1], images=True)
save_json(os.path.join(OUT, "q1_results.json"), R)
json.dumps({"2d": R["2d"]["final"]["RA"], "3d": R["3d"]["final"]["RA"], "problems": PROBLEMS})
