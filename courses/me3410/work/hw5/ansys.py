# HW 5: W16x31 beam in ANSYS Mechanical with beam elements (BEAM188 line body).
# Runs inside Mechanical with pipeline/mech_common.py. --var ASSETS, OUT.
# Units: US customary (in, lbf, psi) for inputs and results.
import math

D, BF = 15.88, 5.525           # in: given depth; W16x31 flange width (AISC)
A_GIVEN, I_GIVEN = 9.12, 375.0  # in^2, in^4 (handout)
L1, L2, XP = 120.0, 60.0, 150.0
W = 1000.0 / 12.0               # lbf/in
P = 500.0


def isec(tf, tw):
    hw = D - 2 * tf
    return 2 * BF * tf + hw * tw, (BF * D ** 3 - (BF - tw) * hw ** 3) / 12.0


# Fillet-free I-section with the handout's depth, the AISC flange width, and the handout's A and I:
# solve the two equations A(tf, tw) = 9.12 and I(tf, tw) = 375 for tf and tw (2x2 Newton).
tf, tw = 0.44, 0.275
for _ in range(50):
    a0, i0 = isec(tf, tw)
    h = 1e-7
    a1, i1 = isec(tf + h, tw)
    a2, i2 = isec(tf, tw + h)
    J11, J12, J21, J22 = (a1 - a0) / h, (a2 - a0) / h, (i1 - i0) / h, (i2 - i0) / h
    r1, r2 = A_GIVEN - a0, I_GIVEN - i0
    det = J11 * J22 - J12 * J21
    tf += (r1 * J22 - J12 * r2) / det
    tw += (J11 * r2 - J21 * r1) / det
SEC = {"tf": tf, "tw": tw, "A": isec(tf, tw)[0], "I": isec(tf, tw)[1], "d": D, "bf": BF}
PROBLEMS = []
R = {"problems": PROBLEMS, "section": SEC}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "beam.step"))
import_materials(os.path.join(ASSETS, "hw5_materials.xml"), ["Structural Steel (E = 29e6 psi, HW 5)"])
gb = []
for asm in ExtAPI.DataModel.GeoData.Assemblies:
    for part in asm.Parts:
        for b in part.Bodies:
            gb.append(b)
verts = [v for b in gb for v in b.Vertices]
edges = [e for b in gb for e in b.Edges]
xmax = max(v.X for v in verts)
VX = {}
for v in verts:
    s = v.X / xmax * 180.0
    for xin in (0.0, L1, XP, 180.0):
        if abs(s - xin) < 1e-3:
            VX[xin] = v.Id
EDGE_AT = lambda xc: [e.Id for e in edges if abs(e.Centroid[0] / xmax * 180.0 - xc) < 1e-3]  # noqa: E731
EDGE_SPAN = EDGE_AT(L1 / 2)
EDGE_2A, EDGE_2B = EDGE_AT(135.0), EDGE_AT(165.0)
R["vertices"], R["span_edge"], R["n_edges"] = dict((str(k), v) for k, v in VX.items()), EDGE_SPAN, len(edges)
if len(VX) != 4 or len(EDGE_SPAN) != 1:
    raise Exception("mapping failed %s %s" % (VX, EDGE_SPAN))
cs = (Model.CrossSections or Model.AddCrossSections()).AddICrossSection()
cs.Name = "W16x31 (equivalent I: d 15.88, bf 5.525, tf %.4f, tw %.4f in)" % (tf, tw)
cs.Width1 = Quantity("%r [in]" % BF)
cs.Width2 = Quantity("%r [in]" % BF)
cs.Width3 = Quantity("%r [in]" % D)
cs.Thick1 = Quantity("%r [in]" % tf)
cs.Thick2 = Quantity("%r [in]" % tf)
cs.Thick3 = Quantity("%r [in]" % tw)
R["cs_ansys"] = {"A_in2": qval(cs.Area, "in in"), "IYY_in4": qval(cs.IYY, "in in in in"),
                 "IZZ_in4": qval(cs.IZZ, "in in in in")}
for b in bodies():
    b.CrossSectionSelection = cs
    b.Material = "Structural Steel (E = 29e6 psi, HW 5)"
ns = dict((k, named_selection(n, [VX[k]])) for k, n in ((0.0, "NODE_1_WALL"), (L1, "NODE_2_ROLLER"),
                                                         (XP, "LOAD_500LB"), (180.0, "NODE_3_TIP")))
ns_span = named_selection("ELEMENT_1_UDL", EDGE_SPAN)
ns_beam = named_selection("BEAM", [e.Id for e in edges])
# Mechanical imports each edge as its own line body; join them at x = 120 in and x = 150 in by
# merging coincident nodes so the three bodies act as one continuous beam.
for prim, sec, lab in ((EDGE_SPAN, EDGE_2A, "node 2 (x = 10 ft)"), (EDGE_2A, EDGE_2B, "load point (x = 12.5 ft)")):
    nm = Model.Mesh.AddNodeMerge()
    s1 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s1.Ids = prim
    s2 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s2.Ids = sec
    nm.MasterLocation = s1
    nm.SlaveLocation = s2
    nm.ToleranceValue = Quantity("0.001 [in]")
    nm.Name = "Node merge at %s" % lab
AN = Model.AddStaticStructuralAnalysis()
fx = AN.AddFixedSupport()
fx.Location = ns[0.0]
fx.Name = "Fixed support (wall) at node 1"
rl = AN.AddDisplacement()
rl.Location = ns[L1]
rl.YComponent.Output.DiscreteValues = [Quantity("0 [in]")]
rl.Name = "Roller at node 2 (uy = 0)"
lp = AN.AddLinePressure()
lp.Location = ns_span
lp.DefineBy = LoadDefineBy.Components
lp.YComponent.Output.DiscreteValues = [Quantity("%r [lbf in^-1]" % (-W))]
lp.Name = "1000 lb/ft on element 1 (-Y)"
f = AN.AddForce()
f.Location = ns[XP]
f.DefineBy = LoadDefineBy.Components
f.YComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % (-P))]
f.Name = "500 lb at mid-element 2 (-Y)"
sol = AN.Solution
RES = {}
RES["td"] = sol.AddTotalDeformation()
RES["dy"] = sol.AddDirectionalDeformation()
RES["dy"].NormalOrientation = NormalOrientationType.YAxis
for k, lab in ((L1, "node 2"), (XP, "load point"), (180.0, "node 3 (tip)")):
    p_ = sol.AddDirectionalDeformation()
    p_.NormalOrientation = NormalOrientationType.YAxis
    p_.Location = ns[k]
    p_.Name = "uy at %s" % lab
    RES["uy_%g" % k] = p_
bt = sol.AddBeamTool()
RES["bt"] = bt
for c in bt.Children:
    RES["bt_" + c.Name] = c
bt_added = []
for nm in ("AddMaximumBendingStress", "AddMinimumBendingStress"):
    if hasattr(bt, nm):
        o = getattr(bt, nm)()
        RES["bt_" + o.Name] = o
        bt_added.append(o.Name)
R["beam_tool_children"] = [c.Name for c in bt.Children]
RES["fr1"] = sol.AddForceReaction()
RES["fr1"].BoundaryConditionSelection = fx
RES["fr1"].Name = "Force reaction, wall (node 1)"
RES["mr1"] = sol.AddMomentReaction()
RES["mr1"].BoundaryConditionSelection = fx
RES["mr1"].Name = "Moment reaction, wall (node 1)"
RES["fr2"] = sol.AddForceReaction()
RES["fr2"].BoundaryConditionSelection = rl
RES["fr2"].Name = "Force reaction, roller (node 2)"
RES["bm"] = sol.AddTotalBendingMoment()
RES["sf"] = sol.AddTotalShearForce()
RES["bm"].Name = "Total bending moment"
RES["sf"].Name = "Total shear force"
"setup ok %s cs %s" % (VX, R["cs_ansys"])
#%% split
MESH_STUDY = []
FINAL_SIZE = 3.0  # in: converged size from the study (60 elements)


def solve_at(size_in):
    Model.Mesh.ElementSize = Quantity("%r [in]" % size_in)
    Model.Mesh.GenerateMesh()
    AN.Solve(True)
    sol.EvaluateAllResults()
    return {"size_in": size_in, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
            "tip_in": qval(RES["uy_180"].Average, "in"), "uy_min_in": qval(RES["dy"].Minimum, "in"),
            "R1_lbf": qval(RES["fr1"].YAxis, "lbf"), "R2_lbf": qval(RES["fr2"].YAxis, "lbf"),
            "M1_lbfin": qval(RES["mr1"].ZAxis, "lbf in")}


for s_ in (60.0, 30.0, 15.0, 7.5, 3.0):
    MESH_STUDY.append(solve_at(s_))
R["mesh_study"] = MESH_STUDY
"study %s" % MESH_STUDY
#%% split
Model.Mesh.ElementSize = Quantity("%r [in]" % FINAL_SIZE)
Model.Mesh.GenerateMesh()
AN.Solve(True)
sol.EvaluateAllResults()
R["state"] = str(sol.ObjectState)
R["messages"] = [m_.DisplayString for m_ in ExtAPI.Application.Messages if str(m_.Severity) in ("Error", "Warning")][-6:]
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["td_max_in"] = qval(RES["td"].Maximum, "in")
R["dy_max_in"], R["dy_min_in"] = qval(RES["dy"].Maximum, "in"), qval(RES["dy"].Minimum, "in")
R["uy"] = dict((str(k), qval(RES["uy_%g" % k].Average, "in")) for k in (L1, XP, 180.0))
R["beam_tool"] = {}
for k, o in RES.items():
    if k.startswith("bt_"):
        R["beam_tool"][o.Name] = {"max_psi": qval(o.Maximum, "psi"), "min_psi": qval(o.Minimum, "psi")}
R["reactions"] = {"R1": {"x": qval(RES["fr1"].XAxis, "lbf"), "y": qval(RES["fr1"].YAxis, "lbf"),
                         "total": qval(RES["fr1"].Total, "lbf")},
                  "M1": {"z": qval(RES["mr1"].ZAxis, "lbf in"), "total": qval(RES["mr1"].Total, "lbf in")},
                  "R2": {"x": qval(RES["fr2"].XAxis, "lbf"), "y": qval(RES["fr2"].YAxis, "lbf"),
                         "total": qval(RES["fr2"].Total, "lbf")}}
R["bm_max_lbfin"], R["sf_max_lbf"] = qval(RES["bm"].Maximum, "lbf in"), qval(RES["sf"].Maximum, "lbf")
"solved %s %s" % (R["state"], R["reactions"])
#%% split
BIN = MechanicalUnitSystem.StandardBIN
V = dict(view="front", width=1400, height=560, units=BIN)
export_image(AN, os.path.join(OUT, "model.png"), **V)
export_image(Model.Mesh, os.path.join(OUT, "mesh.png"), **V)
for k in ("td", "dy", "bm", "sf"):
    export_image(RES[k], os.path.join(OUT, "%s.png" % k), **V)
for k, o in RES.items():
    if k.startswith("bt_"):
        export_image(o, os.path.join(OUT, "bt_%s.png" % o.Name.replace(" ", "_").lower()), **V)
export_image(RES["fr1"], os.path.join(OUT, "r1.png"), **V)
export_image(RES["mr1"], os.path.join(OUT, "m1.png"), **V)
export_image(RES["fr2"], os.path.join(OUT, "r2.png"), **V)
export_image(RES["td"], os.path.join(OUT, "td_iso.png"), view="iso", width=1400, height=800, units=BIN)
#%% split
# Euler-Bernoulli check: a copy of the analysis whose beam section is re-declared in APDL with the
# same I-section dimensions plus SECCONTROL transverse shear stiffness ~1e6 x the real kGA, so
# BEAM188's shear deformation vanishes and the model matches the hand (Euler-Bernoulli) theory.
AN2 = AN.Duplicate()
AN2.Name = "Static Structural (shear-rigid check)"
cmd = AN2.AddCommandSnippet()
cmd.Name = "SECCONTROL: shear-rigid section"
cmd.Input = chr(10).join([
    "/prep7",
    "*get,nsechw5,secp,0,num,max",   # one section per line body (three bodies here)
    "*do,sidhw5,1,nsechw5",
    "sectype,sidhw5,beam,i",
    "secoffset,cent",
    "secdata,%r,%r,%r,%r,%r,%r" % (BF, BF, D, tf, tf, tw),
    "seccontrol,1e12,1e12",
    "*enddo",
    "/solu"])
"dup ok"
#%% split
AN2.Solve(True)
s2 = AN2.Solution
s2.EvaluateAllResults()
def _by(name):
    return [c for c in s2.Children if c.Name == name][0]
R["eb_state"] = str(s2.ObjectState)
R["eb"] = {"tip_in": qval(_by("uy at node 3 (tip)").Average, "in"), "uy150_in": qval(_by("uy at load point").Average, "in"),
           "dy_min_in": qval([c for c in s2.Children if c.Name == RES["dy"].Name][0].Minimum, "in"),
           "R1_lbf": qval(_by("Force reaction, wall (node 1)").YAxis, "lbf"),
           "M1_lbfin": qval(_by("Moment reaction, wall (node 1)").ZAxis, "lbf in"),
           "R2_lbf": qval(_by("Force reaction, roller (node 2)").YAxis, "lbf"),
           "bm_max_lbfin": qval(_by("Total bending moment").Maximum, "lbf in")}
bt2 = [c for c in s2.Children if c.Name == RES["bt"].Name][0]
for c in bt2.Children:
    if c.Name == "Maximum Bending Stress":
        R["eb"]["sb_max_psi"] = qval(c.Maximum, "psi")
R["eb_messages"] = [m_.DisplayString for m_ in ExtAPI.Application.Messages if str(m_.Severity) == "Error"][-4:]
export_image(AN2, os.path.join(OUT, "eb_model.png"), **V)
save_json(os.path.join(OUT, "results.json"), R)
json.dumps(dict((k, R.get(k)) for k in ("state", "problems", "uy", "reactions", "td_max_in", "dy_min_in", "eb_state", "eb", "eb_messages")))
