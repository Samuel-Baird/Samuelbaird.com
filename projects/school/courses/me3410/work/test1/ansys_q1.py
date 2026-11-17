# Test 1 Q1: stepped shaft fixed at both ends, axial loads at nodes 2 and 3 (BEAM188 line bodies).
# Runs inside Mechanical with mech_common.py + line_common.py. --var ASSETS, OUT. Units: in, lbf, psi.
import math

AREA = {1: 0.75, 2: 0.5, 3: 1.0}                      # in^2
JOINTS = {"1": (0.0, 0.0), "1m": (6.0, 0.0), "2": (12.0, 0.0), "3": (21.0, 0.0), "4": (29.0, 0.0)}
MEMBERS = {"1a": ("1", "1m"), "1b": ("1m", "2"), "2": ("2", "3"), "3": ("3", "4")}
ELEM = {"1a": 1, "1b": 1, "2": 2, "3": 3}
MAT = "Shaft (E = 10.6e6 psi, Test 1 Q1)"
R = {}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "q1_shaft.step"))
import_materials(os.path.join(ASSETS, "test1_materials.xml"), [MAT])
EDGE, BODY, VERT = map_line_model(JOINTS, MEMBERS, 29.0)
CS = {}
for e, a in AREA.items():
    c = (Model.CrossSections or Model.AddCrossSections()).AddCircularCrossSection()
    c.Radius = Quantity("%r [in]" % math.sqrt(a / math.pi))
    c.Name = "Element (%d): solid circle d = %.4f in (A = %g in^2)" % (e, 2 * math.sqrt(a / math.pi), a)
    CS[e] = c
for m, b in BODY.items():
    b.CrossSectionSelection = CS[ELEM[m]]
    b.Material = MAT
    b.Name = "Element (%d)%s" % (ELEM[m], {"1a": " left half", "1b": " right half"}.get(m, ""))
R["cs_area"] = dict((str(e), qval(c.Area, "in in")) for e, c in CS.items())
NS = dict((j, named_selection("NODE_%s" % j, VERT[j])) for j in JOINTS)
NSE = dict((e, named_selection("ELEMENT_%d" % e, [EDGE[m] for m in MEMBERS if ELEM[m] == e])) for e in AREA)
merge_joints(JOINTS, MEMBERS, EDGE, "0.001 [in]")
AN = Model.AddStaticStructuralAnalysis()
FS = {}
for j in ("1", "4"):
    fs = AN.AddFixedSupport()
    fs.Location = NS[j]
    fs.Name = "Fixed wall at node %s" % j
    FS[j] = fs
for j, p in (("2", 4000.0), ("3", 1500.0)):
    f = AN.AddForce()
    f.Location = NS[j]
    f.DefineBy = LoadDefineBy.Components
    f.XComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % p)]
    f.Name = "%g lb at node %s (+X)" % (p, j)
sol = AN.Solution
RES = {}
RES["ux"] = sol.AddDirectionalDeformation()
RES["ux"].NormalOrientation = NormalOrientationType.XAxis
RES["ux"].Name = "Directional deformation X (shaft axis)"
for j in ("1m", "2", "3"):
    p_ = sol.AddDirectionalDeformation()
    p_.NormalOrientation = NormalOrientationType.XAxis
    p_.Location = NS[j]
    p_.Name = "ux at node %s" % j
    RES["ux_" + j] = p_
bt = sol.AddBeamTool()
RES["bt"] = bt
for c in bt.Children:
    RES["bt_" + c.Name] = c
AXF = {}
for e in AREA:
    af = sol.AddDirectionalAxialForce()
    af.Location = NSE[e]
    af.Name = "Axial force, element (%d)" % e
    AXF[e] = af
for j in ("1", "4"):
    fr = sol.AddForceReaction()
    fr.BoundaryConditionSelection = FS[j]
    fr.Name = "Reaction at node %s" % j
    RES["r" + j] = fr
"setup ok %s %s" % (EDGE, VERT)
#%% split
STUDY = []
for size in (6.0, 3.0, 1.0, 0.5):
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    STUDY.append({"size_in": size, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
                  "u2": qval(RES["ux_2"].Average, "in"), "u3": qval(RES["ux_3"].Average, "in"),
                  "R1": qval(RES["r1"].XAxis, "lbf")})
R["mesh_study"] = STUDY
#%% split
Model.Mesh.ElementSize = Quantity("1 [in]")
Model.Mesh.GenerateMesh()
solve_retry(AN)
R["state"] = str(sol.ObjectState)
R["messages"] = messages()
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["u"] = dict((j, qval(RES["ux_" + j].Average, "in")) for j in ("1m", "2", "3"))
R["ux_max"], R["ux_min"] = qval(RES["ux"].Maximum, "in"), qval(RES["ux"].Minimum, "in")
R["axial_lbf"] = dict((str(e), axial_signed(AXF[e], "lbf")) for e in AREA)
R["stress_psi"] = dict((str(e), R["axial_lbf"][str(e)] / AREA[e]) for e in AREA)
R["beam_tool"] = dict((o.Name, {"max_psi": qval(o.Maximum, "psi"), "min_psi": qval(o.Minimum, "psi")})
                      for k, o in RES.items() if k.startswith("bt_"))
R["r1"] = {"x": qval(RES["r1"].XAxis, "lbf"), "y": qval(RES["r1"].YAxis, "lbf"), "total": qval(RES["r1"].Total, "lbf")}
R["r4"] = {"x": qval(RES["r4"].XAxis, "lbf"), "y": qval(RES["r4"].YAxis, "lbf"), "total": qval(RES["r4"].Total, "lbf")}
"solved %s %s %s" % (R["state"], R["u"], R["stress_psi"])
#%% split
BIN = MechanicalUnitSystem.StandardBIN
# Front view zoomed on the 29 in shaft (SetFit leaves it tiny): focal point mid-length, 40 in wide so the reaction arrows show.
def shot(obj, name):
    export_front_framed(obj, os.path.join(OUT, name), 14.5 * 0.0254, 40 * 0.0254, units=BIN)


shot(AN, "q1_model.png")
shot(Model.Mesh, "q1_mesh.png")
shot(RES["ux"], "q1_ux.png")
shot(RES["bt_Direct Stress"], "q1_direct_stress.png")
shot(RES["r1"], "q1_r1.png")
shot(RES["r4"], "q1_r4.png")
export_image(RES["ux"], os.path.join(OUT, "q1_ux_iso.png"), view="iso", width=1400, height=800, units=BIN)
save_json(os.path.join(OUT, "q1_results.json"), R)
json.dumps(dict((k, R[k]) for k in ("state", "messages", "u", "axial_lbf", "stress_psi", "beam_tool", "r1", "r4", "mesh_study")))
