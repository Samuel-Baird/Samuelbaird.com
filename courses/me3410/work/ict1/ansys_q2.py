# In-class tutorial Q2: two-bar truss, 36 in members at 60 deg, pins at both supports, 200 lb down at
# apex A. A = 2.3 in^2 (square section), E = 10x10^6 psi. BEAM188 line bodies joined at A.
# Runs inside Mechanical with mech_common.py + test1/line_common.py. --var ASSETS, OUT. Units: in, lbf, psi.
import math

S60 = math.sin(math.radians(60))
JOINTS = {"1": (0.0, 0.0), "A": (18.0, 36.0 * S60), "2": (36.0, 0.0)}
MEMBERS = {"1A": ("1", "A"), "A2": ("A", "2")}
AREA = 2.3
P = 200.0
MAT = "Aluminum (E = 10e6 psi, tutorial Q2)"
R = {}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "q2_truss.step"))
import_materials(os.path.join(ASSETS, "ict1_materials.xml"), [MAT])
EDGE, BODY, VERT = map_line_model(JOINTS, MEMBERS, 36.0)
side = math.sqrt(AREA)
cs = (Model.CrossSections or Model.AddCrossSections()).AddRectangularCrossSection()
cs.Name = "Square %.4f x %.4f in (A = 2.3 in^2)" % (side, side)
cs.Width = Quantity("%r [in]" % side)
cs.Height = Quantity("%r [in]" % side)
for m, b in BODY.items():
    b.CrossSectionSelection = cs
    b.Material = MAT
    b.Name = "Element (%d) %s-%s" % ((1 if m == "1A" else 2,) + MEMBERS[m])
R["cs_area"] = qval(cs.Area, "in in")
NS = dict((j, named_selection("JOINT_%s" % j, VERT[j])) for j in JOINTS)
NSM = dict((m, named_selection("MEMBER_%s" % m, [EDGE[m]])) for m in MEMBERS)
merge_joints(JOINTS, MEMBERS, EDGE, "0.001 [in]")
AN = Model.AddStaticStructuralAnalysis()
PIN = {}
for j in ("1", "2"):
    d = AN.AddDisplacement()
    d.Location = NS[j]
    for c in ("XComponent", "YComponent", "ZComponent"):
        getattr(d, c).Output.DiscreteValues = [Quantity("0 [in]")]
    d.Name = "Pin at support %s (ux = uy = uz = 0)" % j
    PIN[j] = d
    rot = AN.AddFixedRotation()
    rot.Location = NS[j]
    rot.RotationX = FixedOrFree.Fixed
    rot.RotationY = FixedOrFree.Fixed
    rot.RotationZ = FixedOrFree.Free
    rot.Name = "Out-of-plane rotations fixed at %s (rot Z free: in-plane pin)" % j
f = AN.AddForce()
f.Location = NS["A"]
f.DefineBy = LoadDefineBy.Components
f.YComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % (-P))]
f.Name = "200 lb at A (-Y)"
sol = AN.Solution
RES = {}
for ax, en in (("x", NormalOrientationType.XAxis), ("y", NormalOrientationType.YAxis)):
    d = sol.AddDirectionalDeformation()
    d.NormalOrientation = en
    d.Name = "Directional deformation %s" % ax.upper()
    RES["d" + ax] = d
    p_ = sol.AddDirectionalDeformation()
    p_.NormalOrientation = en
    p_.Location = NS["A"]
    p_.Name = "u%s at A" % ax
    RES["uA" + ax] = p_
RES["td"] = sol.AddTotalDeformation()
bt = sol.AddBeamTool()
for c in bt.Children:
    RES["bt_" + c.Name] = c
RES["axial"] = sol.AddDirectionalAxialForce()
RES["axial"].Name = "Axial force (both members)"
AXF = {}
for m in MEMBERS:
    af = sol.AddDirectionalAxialForce()
    af.Location = NSM[m]
    af.Name = "Axial force, member %s-%s" % MEMBERS[m]
    AXF[m] = af
for j in ("1", "2"):
    fr = sol.AddForceReaction()
    fr.BoundaryConditionSelection = PIN[j]
    fr.Name = "Reaction at support %s" % j
    RES["r" + j] = fr
"setup ok %s %s" % (EDGE, VERT)
#%% split
STUDY = []
for size in (12.0, 6.0, 2.0, 1.0):
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    STUDY.append({"size_in": size, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
                  "uAy": qval(RES["uAy"].Average, "in"), "F1A": axial_signed(AXF["1A"], "lbf")})
R["mesh_study"] = STUDY
#%% split
Model.Mesh.ElementSize = Quantity("2 [in]")
Model.Mesh.GenerateMesh()
R["state"] = solve_retry(AN)
R["messages"] = messages()
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["uA"] = {"x": qval(RES["uAx"].Average, "in"), "y": qval(RES["uAy"].Average, "in")}
R["td_max"] = qval(RES["td"].Maximum, "in")
R["axial_lbf"] = dict((m, axial_signed(AXF[m], "lbf")) for m in MEMBERS)
R["stress_psi"] = dict((m, R["axial_lbf"][m] / R["cs_area"]) for m in MEMBERS)
R["beam_tool"] = dict((k[3:], {"max_psi": qval(o.Maximum, "psi"), "min_psi": qval(o.Minimum, "psi")})
                      for k, o in RES.items() if k.startswith("bt_"))
for j in ("1", "2"):
    R["r" + j] = {"x": qval(RES["r" + j].XAxis, "lbf"), "y": qval(RES["r" + j].YAxis, "lbf"),
                  "z": qval(RES["r" + j].ZAxis, "lbf")}
"solved %s %s %s %s" % (R["state"], R["uA"], R["r1"], R["r2"])
#%% split
BIN = MechanicalUnitSystem.StandardBIN
V = dict(view="front", width=1200, height=900, units=BIN)
export_image(AN, os.path.join(OUT, "q2_model.png"), **V)
export_image(Model.Mesh, os.path.join(OUT, "q2_mesh.png"), **V)
for k in ("dy", "td", "axial", "bt_Direct Stress", "r1", "r2"):
    export_image(RES[k], os.path.join(OUT, "q2_%s.png" % k.replace(" ", "_").lower()), **V)
save_json(os.path.join(OUT, "q2_results.json"), R)
json.dumps(dict((k, R[k]) for k in ("state", "messages", "cs_area", "uA", "axial_lbf", "stress_psi", "beam_tool", "r1", "r2", "mesh_study")))
