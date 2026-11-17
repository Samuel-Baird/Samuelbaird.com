# HW 4 Q2: truss in ANSYS Mechanical with link (truss) elements.
# Runs inside Mechanical with pipeline/mech_common.py. --var ASSETS, OUT, MATLIB.
import math

A_M2 = 15e-4
SIDE = math.sqrt(A_M2)            # square section with the same area
JOINTS = {1: (0.0, 0.0), 2: (1.5, 0.0), 3: (0.0, 1.0), 4: (1.5, 1.0)}
MEMBERS = {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (2, 4)}
PROBLEMS = []
R = {"problems": PROBLEMS}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
import_geometry(os.path.join(ASSETS, "truss.step"))
import_materials(MATLIB, ["Aluminum Alloy (E = 70 GPa, HW 4)"])
# GeoData units follow the STEP file here (m). Map each body (one member) by its edge midpoint.
gb = []
for asm in ExtAPI.DataModel.GeoData.Assemblies:
    for part in asm.Parts:
        for b in part.Bodies:
            gb.append(b)
scale = 1.0 if max(abs(c) for b in gb for e in b.Edges for c in e.Centroid) < 10 else 1000.0
MEMBER_EDGE = {}
MEMBER_BODY = {}
VERT = dict((j, []) for j in JOINTS)
for b in gb:
    e = b.Edges[0]
    cx, cy = e.Centroid[0] / scale, e.Centroid[1] / scale
    for m, (i, j) in MEMBERS.items():
        mx, my = (JOINTS[i][0] + JOINTS[j][0]) / 2, (JOINTS[i][1] + JOINTS[j][1]) / 2
        if abs(cx - mx) < 1e-3 and abs(cy - my) < 1e-3:
            MEMBER_EDGE[m] = e.Id
            MEMBER_BODY[m] = b.Id
    for v in b.Vertices:
        for jn, (jx, jy) in JOINTS.items():
            if abs(v.X / scale - jx) < 1e-3 and abs(v.Y / scale - jy) < 1e-3:
                VERT[jn].append(v.Id)
R["member_edge"] = MEMBER_EDGE
R["vertices"] = VERT
if len(MEMBER_EDGE) != 4:
    raise Exception("member mapping failed %s" % MEMBER_EDGE)
cs = (Model.CrossSections or Model.AddCrossSections()).AddRectangularCrossSection()
cs.Name = "Square %.2f mm (A = 15 cm^2)" % (SIDE * 1000)
cs.Width = Quantity("%r [m]" % SIDE)
cs.Height = Quantity("%r [m]" % SIDE)
for b in bodies():
    b.ModelType = PrototypeModelType.Link
    b.CrossSectionSelection = cs
    b.Material = "Aluminum Alloy (E = 70 GPa, HW 4)"
ns_mem = dict((m, named_selection("MEMBER_%d_%d%d" % ((m,) + MEMBERS[m]), [eid])) for m, eid in MEMBER_EDGE.items())
ns_j = dict((j, named_selection("JOINT_%d" % j, ids)) for j, ids in VERT.items())
ns_all = named_selection("ALL_MEMBERS", list(MEMBER_EDGE.values()))
# Connect the four member bodies at the joints: merge coincident nodes.
for prim, secs in ((1, (2, 4)), (3, (2, 4))):
    nm = Model.Mesh.AddNodeMerge()
    nm.MasterLocation = ns_mem[prim].Location
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids = [MEMBER_EDGE[s] for s in secs]
    nm.SlaveLocation = sel
    nm.ToleranceValue = Quantity("1e-5 [m]")
    nm.Name = "Node merge at joints (member %d with members %s)" % (prim, secs)
AN = Model.AddStaticStructuralAnalysis()
SUP = {}
for j in (1, 3):
    d = AN.AddDisplacement()
    d.Location = ns_j[j]
    d.XComponent.Output.DiscreteValues = [Quantity("0 [m]")]
    d.YComponent.Output.DiscreteValues = [Quantity("0 [m]")]
    d.ZComponent.Output.DiscreteValues = [Quantity("0 [m]")]
    d.Name = "Pin at joint %d (ux = uy = uz = 0)" % j
    SUP[j] = d
# Link elements take no loads or supports along their length, so the planar constraint
# (uz = 0) goes on the two free joints; joints 1 and 3 are already fully pinned.
ns_free = named_selection("FREE_JOINTS_2_4", VERT[2] + VERT[4])
dz = AN.AddDisplacement()
dz.Location = ns_free
dz.ZComponent.Output.DiscreteValues = [Quantity("0 [m]")]
dz.Name = "Planar truss: uz = 0 at joints 2 and 4"
f = AN.AddForce()
f.Location = ns_j[4]
f.DefineBy = LoadDefineBy.Components
f.YComponent.Output.DiscreteValues = [Quantity("-2000 [N]")]
f.Name = "2 kN at joint 4 (-Y)"
sol = AN.Solution
RES = {}
RES["td"] = sol.AddTotalDeformation()
RES["dx"] = sol.AddDirectionalDeformation()
RES["dx"].NormalOrientation = NormalOrientationType.XAxis
RES["dy"] = sol.AddDirectionalDeformation()
RES["dy"].NormalOrientation = NormalOrientationType.YAxis
for j in (2, 4):
    for ax, en in (("x", NormalOrientationType.XAxis), ("y", NormalOrientationType.YAxis)):
        rr = sol.AddDirectionalDeformation()
        rr.NormalOrientation = en
        rr.Location = ns_j[j]
        rr.Name = "u%s at joint %d" % (ax, j)
        RES["u%s%d" % (ax, j)] = rr
RES["axial"] = sol.AddDirectionalAxialForce()
RES["axial"].Name = "Axial force (all members)"
AXF = {}
for m in MEMBERS:
    af = sol.AddDirectionalAxialForce()
    af.Location = ns_mem[m]
    af.Name = "Axial force, member %d-%d" % MEMBERS[m]
    AXF[m] = af
for j in (1, 3):
    fr = sol.AddForceReaction()
    fr.BoundaryConditionSelection = SUP[j]
    fr.Name = "Reaction at joint %d" % j
    RES["r%d" % j] = fr
"setup ok %s %s" % (MEMBER_EDGE, VERT)
#%% split
Model.Mesh.ElementSize = Quantity("0.25 [m]")
Model.Mesh.GenerateMesh()
"meshed %d nodes %d elements" % (Model.Mesh.Nodes, Model.Mesh.Elements)
#%% split
AN.Solve(True)
sol.EvaluateAllResults()
R["state"] = str(sol.ObjectState)
R["messages"] = [m_.DisplayString for m_ in ExtAPI.Application.Messages if str(m_.Severity) in ("Error", "Warning")][-5:]
R["joints"] = {"2": {"x": qval(RES["ux2"].Average, "m"), "y": qval(RES["uy2"].Average, "m")},
               "4": {"x": qval(RES["ux4"].Average, "m"), "y": qval(RES["uy4"].Average, "m")}}
for j in (1, 3):
    R["r%d" % j] = {"x": qval(RES["r%d" % j].XAxis, "N"), "y": qval(RES["r%d" % j].YAxis, "N")}
def _axial(res):
    hi, lo = qval(res.Maximum, "N"), qval(res.Minimum, "N")
    return hi if abs(hi) >= abs(lo) else lo
R["axial_N"] = dict((str(m), _axial(AXF[m])) for m in MEMBERS)
R["stress_MPa"] = dict((str(m), R["axial_N"][str(m)] / A_M2 / 1e6) for m in MEMBERS)
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["model_type_note"] = ("Link/Truss (LINK180: two-node, axial-only element, the ANSYS equivalent of the hand-calculation "
                        "truss element); the four members are joined by node merge at the joints.")
V = dict(view="front", width=1000, height=640, units=MechanicalUnitSystem.StandardNMM, true_scale=False)
export_image(AN, os.path.join(OUT, "model.png"), **V)
for k in ("td", "dx", "dy", "axial"):
    export_image(RES[k], os.path.join(OUT, "%s.png" % k), **V)
export_image(RES["r1"], os.path.join(OUT, "r1.png"), **V)
export_image(RES["r3"], os.path.join(OUT, "r3.png"), **V)
save_json(os.path.join(OUT, "results.json"), R)
json.dumps(dict((k, R[k]) for k in ("state", "messages", "joints", "r1", "r3", "stress_MPa", "nodes")))
