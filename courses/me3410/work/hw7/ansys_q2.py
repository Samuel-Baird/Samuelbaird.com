# HW 7 Q2: spherical pressure vessel, 2D axisymmetric quarter model, four materials.
# Runs inside Mechanical with pipeline/mech_common.py. --var ASSETS, OUT, MATLIB.
import math
P_IN = 4000.0                     # psi
RI, RO = 37.5, 39.5               # in
MATS = ["E-Glass", "S-Glass", "Kevlar 49 (handout)", "Carbon Fiber 230 GPa (isotropic)"]
SIZES = [0.5, 0.25, 0.125, 0.0625]
FINAL = 0.125
PROBLEMS = []
R = {"convergence": [], "materials": {}, "problems": PROBLEMS}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "q2_sphere_axisym.step"), two_d=True)
Model.Geometry.Model2DBehavior = Model2DBehavior.AxiSymmetric
import_materials(MATLIB, MATS)
es = [edge_info(e) for e in geo_edges()]
# GeoData lengths are in mm (even for an inch STEP). Arcs are identified by length.
MM = 25.4
inner = [e["id"] for e in es if abs(e["len"] - math.pi / 2 * RI * MM) < 2]
outer = [e["id"] for e in es if abs(e["len"] - math.pi / 2 * RO * MM) < 2]
bottom = [e["id"] for e in es if abs(e["c"][1]) < 1e-6]
axis = [e["id"] for e in es if abs(e["c"][0]) < 1e-6]
R["edges"] = {"inner": inner, "outer": outer, "bottom": bottom, "axis": axis, "all": es}
ns_in = named_selection("INNER_SURFACE", inner)
ns_out = named_selection("OUTER_SURFACE", outer)
ns_bot = named_selection("EQUATOR_SYMMETRY", bottom)
ns_ax = named_selection("AXIS_SYMMETRY", axis)
cs = Model.CoordinateSystems.AddCoordinateSystem()
cs.Name = "Spherical-radial (cylindrical about Z)"
cs.CoordinateSystemType = CoordinateSystemTypeEnum.Cylindrical
AN = Model.AddStaticStructuralAnalysis()
fs1 = AN.AddFrictionlessSupport()
fs1.Location = ns_bot
fs1.Name = "Frictionless support (equator symmetry, uy = 0)"
fs2 = AN.AddFrictionlessSupport()
fs2.Location = ns_ax
fs2.Name = "Frictionless support (axis, ux = 0)"
pr = AN.AddPressure()
pr.Location = ns_in
pr.Magnitude.Output.DiscreteValues = [Quantity("%r [psi]" % P_IN)]
pr.Name = "Internal pressure 4000 psi"
sol = AN.Solution
RES = {}
RES["ur"] = sol.AddDirectionalDeformation()
RES["ur"].NormalOrientation = NormalOrientationType.XAxis
RES["ur"].CoordinateSystem = cs
RES["ur"].Name = "Radial deformation"
RES["sr"] = sol.AddNormalStress()
RES["sr"].NormalOrientation = NormalOrientationType.XAxis
RES["sr"].CoordinateSystem = cs
RES["sr"].Name = "Radial stress"
RES["sh"] = sol.AddNormalStress()
RES["sh"].NormalOrientation = NormalOrientationType.ZAxis
RES["sh"].Name = "Hoop stress (circumferential, Z)"
RES["sm"] = sol.AddNormalStress()
RES["sm"].NormalOrientation = NormalOrientationType.YAxis
RES["sm"].CoordinateSystem = cs
RES["sm"].Name = "Meridional stress"
RES["td"] = sol.AddTotalDeformation()
RES["eqv"] = sol.AddEquivalentStress()
RES["ur_in"] = sol.AddDirectionalDeformation()
RES["ur_in"].NormalOrientation = NormalOrientationType.XAxis
RES["ur_in"].CoordinateSystem = cs
RES["ur_in"].Location = ns_in
RES["ur_in"].Name = "Radial deformation, inner surface"
RES["fr"] = sol.AddForceReaction()
RES["fr"].BoundaryConditionSelection = fs1
for b in bodies():
    b.Material = MATS[0]
if not (inner and outer and bottom and axis):
    raise Exception("edge classification failed: %s" % es)
"setup ok: inner %s outer %s bottom %s axis %s" % (inner, outer, bottom, axis)


def mesh_at(size):
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    Model.Mesh.GenerateMesh()
    return Model.Mesh.Nodes


def read(tag, images):
    AN.Solve(True)
    sol.EvaluateAllResults()
    d = {"state": str(sol.ObjectState), "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    d["ur_max_in"] = qval(RES["ur"].Maximum, "in")
    d["ur_min_in"] = qval(RES["ur"].Minimum, "in")
    d["ur_inner_avg_in"] = qval(RES["ur_in"].Average, "in")
    d["sr_min_psi"] = qval(RES["sr"].Minimum, "psi")
    d["sr_max_psi"] = qval(RES["sr"].Maximum, "psi")
    d["sh_max_psi"] = qval(RES["sh"].Maximum, "psi")
    d["sh_min_psi"] = qval(RES["sh"].Minimum, "psi")
    d["sm_max_psi"] = qval(RES["sm"].Maximum, "psi")
    d["eqv_max_psi"] = qval(RES["eqv"].Maximum, "psi")
    d["Fy_eq_lbf"] = qval(RES["fr"].YAxis, "lbf")
    if images:
        V = dict(view="front", width=1000, height=640, units=MechanicalUnitSystem.StandardBIN)
        d["images"] = {}
        for k in ("ur", "sr", "sh", "sm", "eqv"):
            d["images"][k] = export_image(RES[k], os.path.join(OUT, "q2_%s_%s.png" % (tag, k)), **V)
    return d
#%% split
mesh_at(SIZES[0])
#%% split
R["convergence"].append(dict(size_in=SIZES[0], **read("c0", False)))
mesh_at(SIZES[1])
#%% split
R["convergence"].append(dict(size_in=SIZES[1], **read("c1", False)))
mesh_at(SIZES[2])
#%% split
R["convergence"].append(dict(size_in=SIZES[2], **read("c2", False)))
mesh_at(SIZES[3])
#%% split
R["convergence"].append(dict(size_in=SIZES[3], **read("c3", False)))
mesh_at(FINAL)
#%% split
V = dict(view="front", width=1000, height=640, units=MechanicalUnitSystem.StandardBIN)
export_image(AN, os.path.join(OUT, "q2_model.png"), **V)
export_image(Model.Mesh, os.path.join(OUT, "q2_mesh.png"), **V)
for name in MATS:
    for b in bodies():
        b.Material = name
    tag = name.split()[0].replace("-", "").lower()
    R["materials"][name] = read(tag, name.startswith("Kevlar") or name.startswith("Carbon"))
R["final_size_in"] = FINAL
save_json(os.path.join(OUT, "q2_results.json"), R)
json.dumps({"conv": [(c["size_in"], c["nodes"], round(c["ur_max_in"], 6)) for c in R["convergence"]],
            "mats": dict((k, (round(v["ur_max_in"], 5), round(v["sh_max_psi"]), round(v["sr_min_psi"]), v["state"])) for k, v in R["materials"].items()),
            "problems": PROBLEMS})
