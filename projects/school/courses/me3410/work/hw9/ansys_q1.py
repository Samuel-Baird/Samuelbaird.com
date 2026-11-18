# HW 9 Q1: rotating steel part at 100 rpm, 2D axisymmetric vs full 3D. Runs inside Mechanical with
# pipeline/mech_common.py and work/test1/line_common.py (solve_retry). --var ASSETS, OUT.
import math
OMEGA = 100.0 * 2.0 * math.pi / 60.0          # rad/s
SIZES_2D = [4.0, 2.0, 1.4, 1.0, 0.5]               # mm
SIZES_3D = [8.0, 5.0, 3.5, 2.5]
NODE_LIMIT = 120000
PROBLEMS = []
R = {"omega": OMEGA, "axisym": {"convergence": []}, "solid3d": {"convergence": []}, "problems": PROBLEMS}
NMM = MechanicalUnitSystem.StandardNMM
MAT = "Structural Steel"


def mm_scale(items):
    return 1000.0 if max(abs(c) for it in items for c in it["c"]) < 1.0 else 1.0


def edges_mm():
    es = [edge_info(e) for e in geo_edges()]
    k = mm_scale(es)
    for e in es:
        e["c"] = [v * k for v in e["c"]]
        e["len"] *= k
    return es


def faces_mm():
    fs = [face_info(f) for f in geo_faces()]
    k = mm_scale(fs)
    for f in fs:
        f["c"] = [v * k for v in f["c"]]
        f["area"] *= k * k
    return fs


def omega_quantity():
    return Quantity("%r [rad s^-1]" % OMEGA)


def read(d, AN, RES):
    d["state"] = str(AN.Solution.ObjectState)
    d["td_max_mm"] = qval(RES["td"].Maximum, "mm")
    d["eqv_max_MPa"] = qval(RES["eqv"].Maximum, "MPa")
    d["eqv_min_MPa"] = qval(RES["eqv"].Minimum, "MPa")
    d["eqv_bore_max_MPa"] = qval(RES["eqv_bore"].Maximum, "MPa")
    d["ur_max_mm"] = qval(RES["ur"].Maximum, "mm")
    d["ur_min_mm"] = qval(RES["ur"].Minimum, "mm")
    d["uz_max_mm"] = qval(RES["uz"].Maximum, "mm")
    d["uz_min_mm"] = qval(RES["uz"].Minimum, "mm")
    return d


def shots(prefix, items, view, **kw):
    out = {}
    for key, obj in items:
        try:
            out[key] = export_image(obj, os.path.join(OUT, "%s%s.png" % (prefix, key)), view=view, **kw)
        except Exception as ex:
            PROBLEMS.append("image %s: %s" % (key, str(ex)[:120]))
    return out
ExtAPI.DataModel.Project.New()
#%% split
# ---------------------------------------------------------------- 2D axisymmetric
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = NMM
import_geometry(os.path.join(ASSETS, "q1_axisym.step"), two_d=True)
Model.Geometry.Model2DBehavior = Model2DBehavior.AxiSymmetric
assign_material(MAT)
es = edges_mm()
hub_end = [e["id"] for e in es if abs(abs(e["c"][1]) - 15.0) < 0.1 and abs(e["len"] - 8.0) < 0.1]
rim_end = [e["id"] for e in es if abs(abs(e["c"][1]) - 25.0) < 0.1 and abs(e["len"] - 16.0) < 0.1]
bore = [e["id"] for e in es if abs(e["c"][0] - 5.0) < 0.05 and abs(e["len"] - 30.0) < 0.1]
if len(hub_end) != 2 or len(rim_end) != 2 or len(bore) != 1:
    raise Exception("edge classification failed: %s" % [(e["id"], [round(v, 2) for v in e["c"]], round(e["len"], 2)) for e in es])
R["axisym"]["edges"] = {"hub_end": hub_end, "rim_end": rim_end}
ns_hub = named_selection("HUB_END_EDGES", hub_end)
ns_rim = named_selection("RIM_END_EDGES", rim_end)
ns_bore = named_selection("BORE_EDGE", bore)
AN2 = Model.AddStaticStructuralAnalysis()
FS_HUB = AN2.AddFrictionlessSupport()
FS_HUB.Location = ns_hub
FS_HUB.Name = "Frictionless support: hub top and bottom edges (z = +-15)"
FS_RIM = AN2.AddFrictionlessSupport()
FS_RIM.Location = ns_rim
FS_RIM.Name = "Variant: frictionless support on rim top and bottom edges (z = +-25)"
FS_RIM.Suppressed = True
RV2 = AN2.AddRotationalVelocity()
RV2.DefineBy = LoadDefineBy.Components
RV2.YComponent.Output.DiscreteValues = [omega_quantity()]     # the axis of a 2D axisymmetric model is global Y
RV2.Name = "Rotational velocity 100 rpm about the axis"
sol = AN2.Solution
RES2 = {}
RES2["td"] = sol.AddTotalDeformation()
RES2["eqv"] = sol.AddEquivalentStress()
RES2["eqv_bore"] = sol.AddEquivalentStress()
RES2["eqv_bore"].Location = ns_bore
RES2["eqv_bore"].Name = "Equivalent stress on the bore (r = 5)"
RES2["ur"] = sol.AddDirectionalDeformation()
RES2["ur"].NormalOrientation = NormalOrientationType.XAxis
RES2["ur"].Name = "Radial deformation"
RES2["uz"] = sol.AddDirectionalDeformation()
RES2["uz"].NormalOrientation = NormalOrientationType.YAxis
RES2["uz"].Name = "Axial deformation"
RES2["sr"] = sol.AddNormalStress()
RES2["sr"].NormalOrientation = NormalOrientationType.XAxis
RES2["sr"].Name = "Radial stress"
RES2["sh"] = sol.AddNormalStress()
RES2["sh"].NormalOrientation = NormalOrientationType.ZAxis
RES2["sh"].Name = "Hoop stress"
"setup axisym: hub_end %s rim_end %s" % (hub_end, rim_end)
#%% split
def mesh_solve_2d(size):
    try:
        Model.Mesh.ElementOrder = ElementOrder.Quadratic
    except Exception:                               # read-only after an earlier project in the session: Program Controlled is quadratic
        pass
    Model.Mesh.ElementSize = Quantity("%r [mm]" % size)
    Model.Mesh.GenerateMesh()
    d = {"size": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    solve_retry(AN2)
    read(d, AN2, RES2)
    d["sr_max_MPa"] = qval(RES2["sr"].Maximum, "MPa")
    d["sr_min_MPa"] = qval(RES2["sr"].Minimum, "MPa")
    d["sh_max_MPa"] = qval(RES2["sh"].Maximum, "MPa")
    d["sh_min_MPa"] = qval(RES2["sh"].Minimum, "MPa")
    return d


for s in SIZES_2D:
    R["axisym"]["convergence"].append(mesh_solve_2d(s))
R["axisym"]["final"] = R["axisym"]["convergence"][-1]
V = dict(view="front", width=1100, height=760)
R["axisym"]["images"] = {}
R["axisym"]["images"].update(shots("axi_", [("model", AN2), ("mesh", Model.Mesh), ("td", RES2["td"]), ("eqv", RES2["eqv"]),
                                             ("ur", RES2["ur"]), ("uz", RES2["uz"]), ("sr", RES2["sr"]), ("sh", RES2["sh"])], **V))
# variant: also hold the rim ends
FS_RIM.Suppressed = False
R["axisym"]["variant_rim"] = mesh_solve_2d(R["axisym"]["final"]["size"])
R["axisym"]["variant_rim"]["images"] = shots("axiv_", [("eqv", RES2["eqv"]), ("td", RES2["td"])], **V)
FS_RIM.Suppressed = True
save_json(os.path.join(OUT, "q1_results.json"), R)
json.dumps({"conv": [(c["size"], c["nodes"], c["td_max_mm"], c["eqv_max_MPa"]) for c in R["axisym"]["convergence"]],
            "variant": (R["axisym"]["variant_rim"]["td_max_mm"], R["axisym"]["variant_rim"]["eqv_max_MPa"]), "problems": PROBLEMS})
