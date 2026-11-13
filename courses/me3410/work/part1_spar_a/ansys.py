# Term Project Part I, Spar A (I-section): ANSYS Mechanical model, solve, export.
# Runs inside Mechanical with pipeline/mech_common.py prepended. Inputs (via --var):
#   ASSETS  folder with spar_a_constant.step / spar_a_tapered.step
#   OUT     folder for PNGs + results json
#   MODE    "test" (one coarse solve) or "full"
import math

L, H, B = 1.5, 0.060, 0.055
Q0, E_OFF = 1200.0, 0.050
X_VAL = 0.25


def s_of(x, tapered):
    return (1.0 - 0.25 * x) if tapered else 1.0


def formulas(tapered):
    """Pressure formulas (Pa, x in m) for the two halves of the split bottom face.

    LC1: p = q/B on both halves. LC2: p(+z half) = q/B + 4eq/B^2, p(-z half) = q/B - 4eq/B^2,
    which keeps the resultant q(x) per unit span and adds a torque e*q(x) per unit span.
    """
    bx = "(0.055*(1-0.25*x))" if tapered else "0.055"
    qx = "1200*(1-x/1.5)"
    base = "%s/%s" % (qx, bx)
    tor = "4*%r*%s/(%s*%s)" % (E_OFF, qx, bx, bx)
    return {"LC1": (base, base), "LC2": ("%s + %s" % (base, tor), "%s - %s" % (base, tor))}


def pick_faces():
    fs = [face_info(f) for f in geo_faces()]
    root = [f["id"] for f in fs if f["n"][0] < -0.9]
    tip = [f["id"] for f in fs if f["n"][0] > 0.9]
    downs = [f for f in fs if f["n"][1] < -0.9]
    ymin = min(f["c"][1] for f in downs)
    bottom = [f for f in downs if abs(f["c"][1] - ymin) < 1.0]
    pos = [f["id"] for f in bottom if f["c"][2] > 0]
    neg = [f["id"] for f in bottom if f["c"][2] < 0]
    return root, tip, pos, neg


def add_path(name, p0, p1, n=41):
    cg = Model.ConstructionGeometry if Model.ConstructionGeometry else Model.AddConstructionGeometry()
    p = cg.AddPath()
    p.Name = name
    p.StartXCoordinate, p.StartYCoordinate, p.StartZCoordinate = [q(v, "m") for v in p0]
    p.EndXCoordinate, p.EndYCoordinate, p.EndZCoordinate = [q(v, "m") for v in p1]
    p.NumberOfSamplingPoints = n
    return p


def path_values(res, fname, scale=1.0):
    try:
        res.ExportToTextFile(fname)
    except Exception as e:
        PROBLEMS.append("%s: export failed (%s) state=%s" % (res.Name, str(e)[:120], res.ObjectState))
        return []
    if not os.path.exists(fname):
        PROBLEMS.append("%s: no file, state=%s" % (res.Name, res.ObjectState))
        return []
    vals = []
    with open(fname) as fh:
        for line in fh.readlines()[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                try:
                    vals.append([float(parts[0]), float(parts[-1]) * scale])
                except ValueError:
                    pass
    return vals


def setup(tapered, size, lc_list):
    step = os.path.join(ASSETS, "spar_a_%s.step" % ("tapered" if tapered else "constant"))
    new_model(step, fresh=False)
    assign_material("Aluminum Alloy")
    root, tip, pos, neg = pick_faces()
    ns_root = named_selection("ROOT", root)
    ns_tip = named_selection("TIP", tip)
    ns_pos = named_selection("LIFT_FACE_LEADING_HALF", pos)
    ns_neg = named_selection("LIFT_FACE_TRAILING_HALF", neg)
    hv = H * s_of(X_VAL, tapered) / 2 * 0.999
    ht = H * s_of(L, tapered) / 2
    bt = B * s_of(L, tapered) / 2 * 0.999
    pv = add_path("Validation x=250 mm (web line)", (X_VAL, -hv, 0.0), (X_VAL, hv, 0.0), 61)
    pt = add_path("Tip top flange (chordwise)", (L, ht * 0.999, -bt), (L, ht * 0.999, bt), 41)
    fm = formulas(tapered)
    cases = []
    for lc in lc_list:
        an = Model.AddStaticStructuralAnalysis()
        an.Name = "Static Structural %s" % lc
        fix = an.AddFixedSupport()
        fix.Location = ns_root
        prs = []
        for half, ns, fx in (("leading", ns_pos, fm[lc][0]), ("trailing", ns_neg, fm[lc][1])):
            pr = an.AddPressure()
            pr.Name = "Lift %s %s half" % (lc, half)
            pr.Location = ns
            pr.Magnitude.Output.DefinitionType = VariableDefinitionType.Formula
            pr.Magnitude.Output.Formula = fx
            pr.AppliedBy = LoadAppliedBy.Direct  # mesh-based spatial load
            prs.append(pr)
        pr = prs
        sol = an.Solution
        r = {}
        r["td"] = sol.AddTotalDeformation()
        r["dy"] = sol.AddDirectionalDeformation()
        r["dy"].NormalOrientation = NormalOrientationType.YAxis
        r["sx"] = sol.AddNormalStress()
        r["sx"].NormalOrientation = NormalOrientationType.XAxis
        r["sxy"] = sol.AddShearStress()
        r["sxy"].ShearOrientation = ShearOrientationType.XYPlane
        r["eqv"] = sol.AddEquivalentStress()
        r["dy_tip"] = sol.AddDirectionalDeformation()
        r["dy_tip"].NormalOrientation = NormalOrientationType.YAxis
        r["dy_tip"].Location = ns_tip
        r["dy_tip"].Name = "Tip directional deformation Y"
        r["sx_path"] = sol.AddNormalStress()
        r["sx_path"].NormalOrientation = NormalOrientationType.XAxis
        r["sx_path"].ScopingMethod = GeometryDefineByType.Path
        r["sx_path"].Location = pv
        r["sx_path"].Name = "Normal stress X on validation path"
        r["sxy_path"] = sol.AddShearStress()
        r["sxy_path"].ShearOrientation = ShearOrientationType.XYPlane
        r["sxy_path"].ScopingMethod = GeometryDefineByType.Path
        r["sxy_path"].Location = pv
        r["sxy_path"].Name = "Shear stress XY on validation path"
        r["dy_twist"] = sol.AddDirectionalDeformation()
        r["dy_twist"].NormalOrientation = NormalOrientationType.YAxis
        r["dy_twist"].ScopingMethod = GeometryDefineByType.Path
        r["dy_twist"].Location = pt
        r["dy_twist"].Name = "Tip Y deformation across flange"
        r["fr"] = sol.AddForceReaction()
        r["fr"].BoundaryConditionSelection = fix
        r["mr"] = sol.AddMomentReaction()
        r["mr"].BoundaryConditionSelection = fix
        cases.append((lc, an, fix, pr, r))
    return cases


def refresh(cases):
    """Formula pressures report a stale state until their properties are read and the
    application method is re-set. Do this after meshing, before solving."""
    for lc, an, fix, prs, r in cases:
        for pr in prs:
            [x.StringValue for x in pr.VisibleProperties]
            pr.AppliedBy = LoadAppliedBy.SurfaceEffect
            pr.AppliedBy = LoadAppliedBy.Direct
            [x.StringValue for x in pr.VisibleProperties]
            if str(pr.ObjectState) != "FullyDefined":
                PROBLEMS.append("%s %s state %s" % (lc, pr.Name, pr.ObjectState))


SPAN = dict(view=(-0.35, 0.55, 1.0), frame=((0.80, 0.0, 0.0), 1.75), width=1000, height=470)


def read_case(tag, lc, an, r, tapered, images):
    an.Solution.EvaluateAllResults()
    d = {"lc": lc, "tapered": tapered, "sol_state": str(an.Solution.ObjectState)}
    msgs = [m.DisplayString for m in ExtAPI.Application.Messages if str(m.Severity) in ("Error", "Warning")]
    d["messages"] = msgs[-6:]
    d["nodes"] = Model.Mesh.Nodes
    d["elements"] = Model.Mesh.Elements
    d["Fy_root_N"] = qval(r["fr"].YAxis, "N")
    d["Fx_root_N"] = qval(r["fr"].XAxis, "N")
    d["Mz_root_Nm"] = qval(r["mr"].ZAxis, "N m")
    d["Mx_root_Nm"] = qval(r["mr"].XAxis, "N m")
    d["My_root_Nm"] = qval(r["mr"].YAxis, "N m")
    d["tip_dy_max_mm"] = qval(r["dy_tip"].Maximum, "mm")
    d["tip_dy_min_mm"] = qval(r["dy_tip"].Minimum, "mm")
    d["td_max_mm"] = qval(r["td"].Maximum, "mm")
    d["eqv_max_MPa"] = qval(r["eqv"].Maximum, "MPa")
    d["sx_max_MPa"] = qval(r["sx"].Maximum, "MPa")
    d["sx_min_MPa"] = qval(r["sx"].Minimum, "MPa")
    pre = os.path.join(OUT, tag)
    sxp = path_values(r["sx_path"], pre + "_sx_path.txt")
    sxyp = path_values(r["sxy_path"], pre + "_sxy_path.txt")
    tw = path_values(r["dy_twist"], pre + "_twist_path.txt")
    d["sx_path_Pa"] = sxp
    d["sxy_path_Pa"] = sxyp
    d["twist_path_m"] = tw
    if sxp:
        d["sx_val_top_MPa"] = sxp[-1][1] / 1e6
        d["sx_val_bot_MPa"] = sxp[0][1] / 1e6
    if sxyp:
        mid = sxyp[len(sxyp) // 2]
        d["sxy_val_NA_MPa"] = mid[1] / 1e6
    if len(tw) > 1:
        width = tw[-1][0] - tw[0][0]
        d["tip_twist_rad"] = (tw[-1][1] - tw[0][1]) / width
        d["tip_twist_deg"] = math.degrees(d["tip_twist_rad"])
    if images:
        imgs = {}
        imgs["model"] = export_image(an, pre + "_model.png", **SPAN)
        for key in ("td", "dy", "sx", "sxy", "eqv"):
            imgs[key] = export_image(r[key], pre + "_%s.png" % key, **SPAN)
        imgs["sx_path"] = export_image(r["sx_path"], pre + "_sx_path.png", view="front")
        imgs["fr"] = export_image(r["fr"], pre + "_reaction.png", **SPAN)
        imgs["td_true"] = export_image(r["td"], pre + "_td_true.png", true_scale=True, wire=True, **SPAN)
        d["images"] = imgs
    return d


PROBLEMS = []
results = {"material": None, "cases": {}, "convergence": [], "problems": PROBLEMS}
# Handout §7.3 mesh table: (name, global size, root/junction refinement). The model is a solid,
# meshed with MultiZone quadratic hexes (SOLID186): the global size sets the spanwise element
# length, the refinement size sets the cross-section mesh (root face, swept along the span, so it
# also covers every web-flange junction and the validation section), and a hard edge sizing puts
# two elements through every flange and web thickness (handout §7.1 rule for solids).
# The very fine level uses 10 mm spanwise, not 8 mm: 8 mm with a 3 mm section is 134,373 nodes,
# over the 128,000-node limit of ANSYS Student.
LEVELS = [("Coarse", 0.030, 0.010), ("Medium", 0.020, 0.006), ("Fine", 0.012, 0.004),
          ("Very fine", 0.010, 0.003)]
if MODE != "full":
    LEVELS = [LEVELS[0]]
FINAL = LEVELS[-1]
MESHCTL = {}


def mesh_controls():
    """MultiZone hex method + section sizing + 2 divisions through each wall (created once per
    model, in a later call than the geometry import)."""
    MESHCTL.clear()
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids = [b.Id for asm in ExtAPI.DataModel.GeoData.Assemblies for part in asm.Parts for b in part.Bodies]
    m = Model.Mesh.AddAutomaticMethod()
    m.Location = sel
    m.Method = MethodType.MultiZone
    m.Name = "MultiZone hex (SOLID186), swept along the span"
    fs = [face_info(f) for f in geo_faces()]
    root = [f["id"] for f in fs if f["n"][0] < -0.9]
    fz = Model.Mesh.AddSizing()
    s2 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s2.Ids = root
    fz.Location = s2
    fz.Name = "Section refinement (root face, swept)"
    # geometry units are mm: root edges whose length is a wall thickness (6 mm flange, 4 mm web)
    es = [edge_info(e) for e in geo_edges()]
    thick = [e["id"] for e in es if abs(e["c"][0]) < 1e-3 and min(abs(e["len"] - 6.0), abs(e["len"] - 4.0)) < 1e-3]
    ez = Model.Mesh.AddSizing()
    s3 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s3.Ids = thick
    ez.Location = s3
    ez.Type = SizingType.NumberOfDivisions
    ez.NumberOfDivisions = 2
    ez.Behavior = SizingBehavior.Hard
    ez.Name = "2 elements through each wall thickness"
    MESHCTL.update(method=m, face=fz, edge=ez, n_thick_edges=len(thick))
    return "mesh controls: %d thickness edges" % len(thick)


def mesh_at(level):
    name, glob, ref = level
    Model.Mesh.ElementSize = q(glob, "m")
    MESHCTL["face"].ElementSize = q(ref, "m")
    Model.Mesh.GenerateMesh()
    return "meshed %s (%g/%g mm): %d nodes" % (name, glob * 1000, ref * 1000, Model.Mesh.Nodes)


def geometry_mass():
    b = bodies()[0]
    out = {}
    try:
        out["volume_m3"] = float(b.Volume.ConvertUnit("m m m").Value)
    except Exception as e:
        PROBLEMS.append("volume: %s" % str(e)[:100])
    try:
        out["mass_kg"] = float(b.Mass.ConvertUnit("kg").Value)
    except Exception as e:
        PROBLEMS.append("mass: %s" % str(e)[:100])
    return out


def conv_step(level):
    refresh(CASES)
    lc, an, fix, pr, r = CASES[0]
    an.Solve(True)
    name, glob, ref = level
    d = read_case("conv_%s" % name.replace(" ", "_"), lc, an, r, False, False)
    results["convergence"].append({
        "level": name, "global_mm": glob * 1000, "refine_mm": ref * 1000,
        "nodes": d["nodes"], "elements": d["elements"],
        "tip_dy_mm": d["tip_dy_max_mm"], "sx_val_top_MPa": d.get("sx_val_top_MPa"),
        "sx_val_bot_MPa": d.get("sx_val_bot_MPa"), "sxy_val_NA_MPa": d.get("sxy_val_NA_MPa"),
        "sx_max_MPa": d["sx_max_MPa"], "eqv_max_MPa": d["eqv_max_MPa"], "Fy_root_N": d["Fy_root_N"]})
    return "conv %s: %d nodes, tip %.4f mm, state %s" % (name, d["nodes"], d["tip_dy_max_mm"], d["sol_state"])


def final_solve(tag, tapered):
    refresh(CASES)
    export_image(Model.Mesh, os.path.join(OUT, "%s_mesh.png" % tag), **SPAN)
    export_image(Model.Mesh, os.path.join(OUT, "%s_mesh_root.png" % tag), view=(-0.6, 0.5, 1.0),
                 frame=((0.05, 0.0, 0.0), 0.22), width=1000, height=470)
    for lc, an, fix, pr, r in CASES:
        an.Solve(True)
        results["cases"]["%s_%s" % (tag, lc)] = read_case("%s_%s" % (tag, lc), lc, an, r, tapered, True)
    return tag + " solved"


ExtAPI.DataModel.Project.New()
#%% split
CASES = setup(False, None, ["LC1", "LC2"])
results["material"] = material_props("Aluminum Alloy")
results["mass_constant"] = geometry_mass()
#%% split
mesh_controls()
#%% split
mesh_at(LEVELS[0])
#%% split
conv_step(LEVELS[0])
#%% split
mesh_at(LEVELS[1]) if len(LEVELS) > 1 else "skip"
#%% split
conv_step(LEVELS[1]) if len(LEVELS) > 1 else "skip"
#%% split
mesh_at(LEVELS[2]) if len(LEVELS) > 2 else "skip"
#%% split
conv_step(LEVELS[2]) if len(LEVELS) > 2 else "skip"
#%% split
mesh_at(LEVELS[3]) if len(LEVELS) > 3 else "skip"
#%% split
conv_step(LEVELS[3]) if len(LEVELS) > 3 else "skip"
#%% split
final_solve("constant", False)
#%% split
ExtAPI.DataModel.Project.New()
#%% split
CASES = setup(True, None, ["LC1", "LC2"])
results["mass_tapered"] = geometry_mass()
#%% split
mesh_controls()
#%% split
mesh_at(FINAL)
#%% split
final_solve("tapered", True)
#%% split
results["final_level"] = list(FINAL)
results["mesh_controls_thick_edges"] = MESHCTL.get("n_thick_edges")
save_json(os.path.join(OUT, "results_%s.json" % MODE), results)
json.dumps({"problems": PROBLEMS, "convergence": results["convergence"],
            "mass": [results.get("mass_constant"), results.get("mass_tapered")],
            "cases": dict((c, dict((k, v) for k, v in cv.items() if not isinstance(v, (list, dict)))) for c, cv in results["cases"].items())})
