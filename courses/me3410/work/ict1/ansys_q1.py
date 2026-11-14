# In-class tutorial Q1: round stepped shaft fixed at both walls, 3500 lb axial load at B (BEAM188 line
# bodies). Runs inside Mechanical with mech_common.py + test1/line_common.py. --var ASSETS, OUT.
# Units: in, lbf, psi. Material: ANSYS Structural Steel (as the handout says).
import math

AREA = {1: 0.8, 2: 0.5}                                   # in^2
JOINTS = {"W1": (0.0, 0.0), "D": (4.0, 0.0), "B": (10.0, 0.0), "F": (17.0, 0.0), "W2": (22.0, 0.0)}
MEMBERS = {"1a": ("W1", "D"), "1b": ("D", "B"), "2a": ("B", "F"), "2b": ("F", "W2")}
ELEM = {"1a": 1, "1b": 1, "2a": 2, "2b": 2}
P = 3500.0
R = {}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "q1_shaft.step"))
EDGE, BODY, VERT = map_line_model(JOINTS, MEMBERS, 22.0)
CS = {}
for e, a in AREA.items():
    c = (Model.CrossSections or Model.AddCrossSections()).AddCircularCrossSection()
    c.Radius = Quantity("%r [in]" % math.sqrt(a / math.pi))
    c.Name = "Element (%d): solid circle d = %.4f in (A = %g in^2)" % (e, 2 * math.sqrt(a / math.pi), a)
    CS[e] = c
for m, b in BODY.items():
    b.CrossSectionSelection = CS[ELEM[m]]
    b.Material = "Structural Steel"
    b.Name = "Element (%d) %s" % (ELEM[m], m[1:])
R["cs_area"] = dict((str(e), qval(c.Area, "in in")) for e, c in CS.items())
NS = dict((j, named_selection("POINT_%s" % j, VERT[j])) for j in JOINTS)
NSE = dict((e, named_selection("ELEMENT_%d" % e, [EDGE[m] for m in MEMBERS if ELEM[m] == e])) for e in AREA)
merge_joints(JOINTS, MEMBERS, EDGE, "0.001 [in]")
AN = Model.AddStaticStructuralAnalysis()
FS = {}
for j, lab in (("W1", "left"), ("W2", "right")):
    fs = AN.AddFixedSupport()
    fs.Location = NS[j]
    fs.Name = "Fixed %s wall" % lab
    FS[j] = fs
f = AN.AddForce()
f.Location = NS["B"]
f.DefineBy = LoadDefineBy.Components
f.XComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % P)]
f.Name = "3500 lb at B (+X)"
sol = AN.Solution
RES = {}
RES["ux"] = sol.AddDirectionalDeformation()
RES["ux"].NormalOrientation = NormalOrientationType.XAxis
RES["ux"].Name = "Directional deformation X (shaft axis)"
for j in ("D", "B", "F"):
    p_ = sol.AddDirectionalDeformation()
    p_.NormalOrientation = NormalOrientationType.XAxis
    p_.Location = NS[j]
    p_.Name = "ux at point %s" % j
    RES["ux_" + j] = p_
bt = sol.AddBeamTool()
for c in bt.Children:
    RES["bt_" + c.Name] = c
AXF = {}
for e in AREA:
    af = sol.AddDirectionalAxialForce()
    af.Location = NSE[e]
    af.Name = "Axial force, element (%d)" % e
    AXF[e] = af
for j in ("W1", "W2"):
    fr = sol.AddForceReaction()
    fr.BoundaryConditionSelection = FS[j]
    fr.Name = "Reaction, %s" % FS[j].Name.lower()
    RES["r" + j] = fr
"setup ok %s %s" % (EDGE, VERT)
#%% split
STUDY = []
for size in (5.0, 2.0, 1.0, 0.5):
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    STUDY.append({"size_in": size, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
                  "uB": qval(RES["ux_B"].Average, "in"), "R1": qval(RES["rW1"].XAxis, "lbf")})
R["mesh_study"] = STUDY
#%% split
Model.Mesh.ElementSize = Quantity("1 [in]")
Model.Mesh.GenerateMesh()
R["state"] = solve_retry(AN)
R["messages"] = messages()
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["u"] = dict((j, qval(RES["ux_" + j].Average, "in")) for j in ("D", "B", "F"))
R["ux_max"], R["ux_min"] = qval(RES["ux"].Maximum, "in"), qval(RES["ux"].Minimum, "in")
R["axial_lbf"] = dict((str(e), axial_signed(AXF[e], "lbf")) for e in AREA)
R["stress_psi"] = dict((str(e), R["axial_lbf"][str(e)] / R["cs_area"][str(e)]) for e in AREA)
R["beam_tool"] = dict((k[3:], {"max_psi": qval(o.Maximum, "psi"), "min_psi": qval(o.Minimum, "psi")})
                      for k, o in RES.items() if k.startswith("bt_"))
for j in ("W1", "W2"):
    R["r" + j] = {"x": qval(RES["r" + j].XAxis, "lbf"), "y": qval(RES["r" + j].YAxis, "lbf"),
                  "total": qval(RES["r" + j].Total, "lbf")}
"solved %s %s %s" % (R["state"], R["u"], R["stress_psi"])
#%% split
BIN = MechanicalUnitSystem.StandardBIN


def shot(obj, name):
    export_front_framed(obj, os.path.join(OUT, name), 11.0 * 0.0254, 30 * 0.0254, units=BIN)


shot(AN, "q1_model.png")
shot(Model.Mesh, "q1_mesh.png")
shot(RES["ux"], "q1_ux.png")
shot(RES["ux_B"], "q1_ux_B.png")
shot(RES["bt_Direct Stress"], "q1_direct_stress.png")
shot(RES["rW1"], "q1_r1.png")
shot(RES["rW2"], "q1_r2.png")
export_image(AN, os.path.join(OUT, "q1_model_iso.png"), view="iso", width=1400, height=800, units=BIN)
save_json(os.path.join(OUT, "q1_results.json"), R)
json.dumps(dict((k, R[k]) for k in ("state", "messages", "cs_area", "u", "axial_lbf", "stress_psi", "beam_tool", "rW1", "rW2", "mesh_study")))
