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
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = q(size, "m")
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
        d["images"] = imgs
    return d


PROBLEMS = []
results = {"material": None, "cases": {}, "convergence": [], "problems": PROBLEMS}
SIZES = [0.015, 0.010, 0.0075, 0.005] if MODE == "full" else [0.012]
FINAL = SIZES[-1]


def mesh_at(size):
    Model.Mesh.ElementSize = q(size, "m")
    Model.Mesh.GenerateMesh()
    return "meshed %g mm: %d nodes" % (size * 1000, Model.Mesh.Nodes)


def conv_step(size):
    refresh(CASES)
    lc, an, fix, pr, r = CASES[0]
    an.Solve(True)
    d = read_case("conv_%g" % (size * 1000), lc, an, r, False, False)
    results["convergence"].append({
        "size_mm": size * 1000, "nodes": d["nodes"], "elements": d["elements"],
        "tip_dy_mm": d["tip_dy_max_mm"], "sx_val_top_MPa": d.get("sx_val_top_MPa"),
        "sxy_val_NA_MPa": d.get("sxy_val_NA_MPa"), "Fy_root_N": d["Fy_root_N"]})
    return "conv %g mm: tip %.4f mm, state %s" % (size * 1000, d["tip_dy_max_mm"], d["sol_state"])


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
CASES = setup(False, SIZES[0], ["LC1", "LC2"])
results["material"] = material_props("Aluminum Alloy")
mesh_at(SIZES[0])
#%% split
conv_step(SIZES[0])
#%% split
mesh_at(SIZES[1]) if len(SIZES) > 1 else "skip"
#%% split
conv_step(SIZES[1]) if len(SIZES) > 1 else "skip"
#%% split
mesh_at(SIZES[2]) if len(SIZES) > 2 else "skip"
#%% split
conv_step(SIZES[2]) if len(SIZES) > 2 else "skip"
#%% split
mesh_at(SIZES[3]) if len(SIZES) > 3 else "skip"
#%% split
conv_step(SIZES[3]) if len(SIZES) > 3 else "skip"
#%% split
final_solve("constant", False)
#%% split
ExtAPI.DataModel.Project.New()
#%% split
CASES = setup(True, FINAL, ["LC1", "LC2"])
mesh_at(FINAL)
#%% split
final_solve("tapered", True)
#%% split
results["final_size_mm"] = FINAL * 1000
save_json(os.path.join(OUT, "results_%s.json" % MODE), results)
json.dumps({"problems": PROBLEMS, "convergence": results["convergence"],
            "cases": dict((c, dict((k, v) for k, v in cv.items() if not isinstance(v, (list, dict)))) for c, cv in results["cases"].items())})
