# HW 9 Q1, part 2: the same rotating part as a full 360-degree 3D solid (run after ansys_q1.py; Mechanical is
# left open between runs). the 90-degree wedge (two symmetry planes, frictionless) with frictionless hub end faces. A full 360-degree
# solid has a free rigid-body rotation about the axis; Weak Springs there gave unusable rigid-body drift. --var ASSETS, OUT.
import math
OMEGA = 100.0 * 2.0 * math.pi / 60.0
SIZES_3D = [8.0, 5.0, 3.5, 2.5, 1.75, 1.4]
NODE_LIMIT = 120000
PROBLEMS = []
NMM = MechanicalUnitSystem.StandardNMM
MAT = "Structural Steel"
R = json.loads(open(os.path.join(OUT, "q1_results.json")).read())
R["solid3d"] = {"convergence": []}
R["problems3d"] = PROBLEMS


def faces_mm():
    fs = [face_info(f) for f in geo_faces()]
    k = 1000.0 if max(abs(c) for f in fs for c in f["c"]) < 1.0 else 1.0
    for f in fs:
        f["c"] = [v * k for v in f["c"]]
        f["area"] *= k * k
    return fs


def read(d):
    d["state"] = str(AN3.Solution.ObjectState)
    d["td_max_mm"] = qval(RES3["td"].Maximum, "mm")
    d["eqv_max_MPa"] = qval(RES3["eqv"].Maximum, "MPa")
    d["eqv_min_MPa"] = qval(RES3["eqv"].Minimum, "MPa")
    d["eqv_bore_max_MPa"] = qval(RES3["eqv_bore"].Maximum, "MPa")
    d["ur_max_mm"] = qval(RES3["ur"].Maximum, "mm")
    d["ur_min_mm"] = qval(RES3["ur"].Minimum, "mm")
    d["uz_max_mm"] = qval(RES3["uz"].Maximum, "mm")
    d["uz_min_mm"] = qval(RES3["uz"].Minimum, "mm")
    return d


def shots(prefix, items, **kw):
    out = {}
    for key, obj in items:
        try:
            out[key] = export_image(obj, os.path.join(OUT, "%s%s.png" % (prefix, key)), **kw)
        except Exception as ex:
            PROBLEMS.append("image %s: %s" % (key, str(ex)[:120]))
    return out
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = NMM
import_geometry(os.path.join(ASSETS, "q1_3d_quarter.step"))
assign_material(MAT)
fs = faces_mm()
AHUB = math.pi * (13.0 ** 2 - 5.0 ** 2) / 4.0
hub_end = [f["id"] for f in fs if abs(abs(f["c"][2]) - 15.0) < 0.1 and abs(f["area"] - AHUB) < 2.0]
cut_y = [f["id"] for f in fs if abs(f["c"][1]) < 0.01 and abs(f["c"][2]) < 0.5 and f["area"] > 1000]   # plane y = 0
cut_x = [f["id"] for f in fs if abs(f["c"][0]) < 0.01 and abs(f["c"][2]) < 0.5 and f["area"] > 1000]   # plane x = 0
bore = [f["id"] for f in fs if abs(f["area"] - 2 * math.pi * 5.0 * 30.0 / 4.0) < 1.0]
if len(bore) != 1 or len(hub_end) != 2 or len(cut_y) != 1 or len(cut_x) != 1:
    raise Exception("hub end faces: %s in %s" % (hub_end, [(f["id"], [round(v, 1) for v in f["c"]], round(f["area"], 1)) for f in fs]))
R["solid3d"]["faces"] = {"hub_end": hub_end, "cut_y": cut_y, "cut_x": cut_x}
ns_bore = named_selection("BORE_FACE", bore)
ns_cy = named_selection("SYM_PLANE_Y0", cut_y)
ns_cx = named_selection("SYM_PLANE_X0", cut_x)
ns_hub = named_selection("HUB_END_FACES", hub_end)
AN3 = Model.AddStaticStructuralAnalysis()
FS3 = AN3.AddFrictionlessSupport()
FS3.Location = ns_hub
FS3.Name = "Frictionless support: hub top and bottom faces (z = +-15)"
FSY = AN3.AddFrictionlessSupport()
FSY.Location = ns_cy
FSY.Name = "Frictionless support: symmetry plane y = 0"
FSX = AN3.AddFrictionlessSupport()
FSX.Location = ns_cx
FSX.Name = "Frictionless support: symmetry plane x = 0"
RV3 = AN3.AddRotationalVelocity()
RV3.DefineBy = LoadDefineBy.Components
RV3.ZComponent.Output.DiscreteValues = [Quantity("%r [rad s^-1]" % OMEGA)]
RV3.Name = "Rotational velocity 100 rpm about Z"
sol = AN3.Solution
RES3 = {}
RES3["td"] = sol.AddTotalDeformation()
RES3["eqv"] = sol.AddEquivalentStress()
cs = Model.CoordinateSystems.AddCoordinateSystem()
cs.CoordinateSystemType = CoordinateSystemTypeEnum.Cylindrical
cs.Name = "Cylindrical (about Z)"
RES3["eqv_bore"] = sol.AddEquivalentStress()
RES3["eqv_bore"].Location = ns_bore
RES3["eqv_bore"].Name = "Equivalent stress on the bore (r = 5)"
RES3["ur"] = sol.AddDirectionalDeformation()
RES3["ur"].NormalOrientation = NormalOrientationType.XAxis
RES3["ur"].CoordinateSystem = cs
RES3["ur"].Name = "Radial deformation"
RES3["uz"] = sol.AddDirectionalDeformation()
RES3["uz"].NormalOrientation = NormalOrientationType.ZAxis
RES3["uz"].Name = "Axial deformation"
RES3["sr"] = sol.AddNormalStress()
RES3["sr"].NormalOrientation = NormalOrientationType.XAxis
RES3["sr"].CoordinateSystem = cs
RES3["sr"].Name = "Radial stress"
RES3["sh"] = sol.AddNormalStress()
RES3["sh"].NormalOrientation = NormalOrientationType.YAxis
RES3["sh"].CoordinateSystem = cs
RES3["sh"].Name = "Hoop stress"
"setup 3d: %s" % hub_end
#%% split
def mesh_solve_3d(size):
    try:
        Model.Mesh.ElementOrder = ElementOrder.Quadratic
    except Exception:                               # read-only after an earlier project in the session: Program Controlled is quadratic
        pass
    Model.Mesh.ElementSize = Quantity("%r [mm]" % size)
    Model.Mesh.GenerateMesh()
    d = {"size": size, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    if d["nodes"] > NODE_LIMIT:
        d["skipped"] = "over node limit"
        return d
    solve_retry(AN3)
    read(d)
    d["sr_max_MPa"] = qval(RES3["sr"].Maximum, "MPa")
    d["sr_min_MPa"] = qval(RES3["sr"].Minimum, "MPa")
    d["sh_max_MPa"] = qval(RES3["sh"].Maximum, "MPa")
    d["sh_min_MPa"] = qval(RES3["sh"].Minimum, "MPa")
    return d


for s in SIZES_3D:
    R["solid3d"]["convergence"].append(mesh_solve_3d(s))
    if R["solid3d"]["convergence"][-1].get("skipped"):
        break
ok = [c for c in R["solid3d"]["convergence"] if not c.get("skipped")]
fin = ok[-1]
if R["solid3d"]["convergence"][-1].get("skipped"):
    fin = mesh_solve_3d(fin["size"])
R["solid3d"]["final"] = fin
R["solid3d"]["images"] = {}
for key, obj in (("model", AN3), ("mesh", Model.Mesh), ("td", RES3["td"]), ("eqv", RES3["eqv"])):
    R["solid3d"]["images"].update(shots("s3d_iso_", [(key, obj)], view="iso", true_scale=True))
R["solid3d"]["images"].update(shots("s3d_", [("model", AN3), ("mesh", Model.Mesh), ("td", RES3["td"]), ("eqv", RES3["eqv"]),
                                             ("ur", RES3["ur"]), ("uz", RES3["uz"]), ("sr", RES3["sr"]), ("sh", RES3["sh"])],
                                   view="bottom", true_scale=True))
R["solid3d"]["states"] = dict((k, str(v.ObjectState)) for k, v in RES3.items())
R["solid3d"]["states"]["solution"] = str(AN3.Solution.ObjectState)
save_json(os.path.join(OUT, "q1_results.json"), R)
json.dumps({"conv": [(c["size"], c["nodes"], c.get("td_max_mm"), c.get("eqv_max_MPa"), c.get("state"), c.get("skipped")) for c in R["solid3d"]["convergence"]], "states": R["solid3d"]["states"],
            "problems": PROBLEMS})
