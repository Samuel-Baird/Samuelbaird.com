# In-class tutorial Q3: overhanging W14x68 steel beam ABC, pin at A, roller at B, P = 50 kips down at
# the free end C. L = 180 in, a = 48 in, I = 722 in^4, E = 29x10^6 psi. BEAM188 line bodies.
# Runs inside Mechanical with mech_common.py + test1/line_common.py. --var ASSETS, OUT. Units: in, lbf, psi.
import math

D, BF = 14.0, 10.0              # in: W14x68 depth and flange width (AISC)
A_GIVEN, I_GIVEN = 20.0, 722.0  # in^2 (AISC), in^4 (handout)
L, a, P = 180.0, 48.0, 50000.0
XPK = L / math.sqrt(3)
JOINTS = {"A": (0.0, 0.0), "K": (XPK, 0.0), "B": (L, 0.0), "C": (L + a, 0.0)}
MEMBERS = {"s1": ("A", "K"), "s2": ("K", "B"), "s3": ("B", "C")}
MAT = "Steel (E = 29e6 psi, tutorial Q3)"


def isec(tf, tw):
    hw = D - 2 * tf
    return 2 * BF * tf + hw * tw, (BF * D ** 3 - (BF - tw) * hw ** 3) / 12.0


# Fillet-free I-section with the W14x68 depth and flange width whose A and I equal 20.0 in^2 and
# 722 in^4: solve A(tf, tw) = 20.0 and I(tf, tw) = 722 for tf and tw (2x2 Newton), as in HW 5.
tf, tw = 0.72, 0.415
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
R = {"section": SEC}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "q3_beam.step"))
import_materials(os.path.join(ASSETS, "ict1_materials.xml"), [MAT])
EDGE, BODY, VERT = map_line_model(JOINTS, MEMBERS, L + a)
cs = (Model.CrossSections or Model.AddCrossSections()).AddICrossSection()
cs.Name = "W14x68 (equivalent I: d 14.0, bf 10.0, tf %.4f, tw %.4f in)" % (tf, tw)
cs.Width1 = Quantity("%r [in]" % BF)
cs.Width2 = Quantity("%r [in]" % BF)
cs.Width3 = Quantity("%r [in]" % D)
cs.Thick1 = Quantity("%r [in]" % tf)
cs.Thick2 = Quantity("%r [in]" % tf)
cs.Thick3 = Quantity("%r [in]" % tw)
for m, b in BODY.items():
    b.CrossSectionSelection = cs
    b.Material = MAT
    b.Name = {"s1": "Span AB (A to x = L/sqrt3)", "s2": "Span AB (x = L/sqrt3 to B)", "s3": "Overhang BC"}[m]
R["cs_ansys"] = {"A_in2": qval(cs.Area, "in in"), "IYY_in4": qval(cs.IYY, "in in in in"),
                 "IZZ_in4": qval(cs.IZZ, "in in in in")}
NS = dict((j, named_selection("POINT_%s" % j, VERT[j])) for j in JOINTS)
NS_BEAM = named_selection("BEAM", [EDGE[m] for m in sorted(MEMBERS)])
merge_joints(JOINTS, MEMBERS, EDGE, "0.001 [in]")
AN = Model.AddStaticStructuralAnalysis()
pin = AN.AddDisplacement()
pin.Location = NS["A"]
for c in ("XComponent", "YComponent", "ZComponent"):
    getattr(pin, c).Output.DiscreteValues = [Quantity("0 [in]")]
pin.Name = "Pin at A (ux = uy = uz = 0)"
rot = AN.AddFixedRotation()
rot.Location = NS["A"]
rot.RotationX = FixedOrFree.Fixed
rot.RotationY = FixedOrFree.Free
rot.RotationZ = FixedOrFree.Free
rot.Name = "Twist about the beam axis fixed at A (bending rotations free)"
roller = AN.AddDisplacement()
roller.Location = NS["B"]
roller.YComponent.Output.DiscreteValues = [Quantity("0 [in]")]
roller.ZComponent.Output.DiscreteValues = [Quantity("0 [in]")]
roller.Name = "Roller at B (uy = uz = 0; ux free)"
f = AN.AddForce()
f.Location = NS["C"]
f.DefineBy = LoadDefineBy.Components
f.YComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % (-P))]
f.Name = "P = 50 kips at C (-Y)"
sol = AN.Solution
RES = {}
RES["dy"] = sol.AddDirectionalDeformation()
RES["dy"].NormalOrientation = NormalOrientationType.YAxis
RES["dy"].Name = "Directional deformation Y (vertical deflection)"
for j in ("K", "C"):
    p_ = sol.AddDirectionalDeformation()
    p_.NormalOrientation = NormalOrientationType.YAxis
    p_.Location = NS[j]
    p_.Name = "uy at %s" % {"K": "x = L/sqrt3 (span AB)", "C": "C (free end)"}[j]
    RES["uy_" + j] = p_
RES["bt"] = sol.AddBeamTool()
for c in RES["bt"].Children:
    RES["bt_" + c.Name] = c
o = RES["bt"].AddMaximumBendingStress()
RES["bt_" + o.Name] = o
RES["sf"] = sol.AddTotalShearForce()
RES["sf"].Name = "Total shear force"
RES["bm"] = sol.AddTotalBendingMoment()
RES["bm"].Name = "Total bending moment"
RES["rA"] = sol.AddForceReaction()
RES["rA"].BoundaryConditionSelection = pin
RES["rA"].Name = "Reaction at pin A"
RES["rB"] = sol.AddForceReaction()
RES["rB"].BoundaryConditionSelection = roller
RES["rB"].Name = "Reaction at roller B"
"setup ok %s %s %s" % (EDGE, R["cs_ansys"], SEC)
#%% split
STUDY = []
for size in (24.0, 12.0, 4.0, 2.0):
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    STUDY.append({"size_in": size, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
                  "uyC": qval(RES["uy_C"].Average, "in"), "uyK": qval(RES["uy_K"].Average, "in"),
                  "sb_max": qval(RES["bt_Maximum Bending Stress"].Maximum, "psi")})
R["mesh_study"] = STUDY
#%% split
Model.Mesh.ElementSize = Quantity("2 [in]")
Model.Mesh.GenerateMesh()
R["state"] = solve_retry(AN)
R["messages"] = messages()
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["uy"] = dict((j, qval(RES["uy_" + j].Average, "in")) for j in ("K", "C"))
R["dy"] = {"max": qval(RES["dy"].Maximum, "in"), "min": qval(RES["dy"].Minimum, "in")}
R["beam_tool_psi"] = dict((k[3:], {"max": qval(o.Maximum, "psi"), "min": qval(o.Minimum, "psi")})
                          for k, o in RES.items() if k.startswith("bt_"))
R["sf_max_lbf"], R["bm_max_lbfin"] = qval(RES["sf"].Maximum, "lbf"), qval(RES["bm"].Maximum, "lbf in")
for k in ("rA", "rB"):
    R[k] = {"x": qval(RES[k].XAxis, "lbf"), "y": qval(RES[k].YAxis, "lbf"), "z": qval(RES[k].ZAxis, "lbf")}
"solved %s %s %s %s" % (R["state"], R["rA"], R["rB"], R["uy"])
#%% split
# Shear-moment diagram along the beam axis: scoped to an edge path and added after the solve
# (an unscoped diagram leaves the solution UnderDefined and the solve fails).
cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
path = cg.AddPath()
path.PathType = PathScopingType.Edge
path.Location = NS_BEAM
path.Name = "Beam axis path A-C"
smd = sol.AddShearMomentDiagramMZ()
smd.Path = path
smd.Name = "Shear-Moment Diagram (beam axis A-C)"
sol.EvaluateAllResults()
pdat = smd.PlotData
R["smd"] = dict((str(k), [float(v) for v in pdat[k]]) for k in ("X Coordinate", "SFY", "SFZ", "MY", "MZ", "UY", "UZ"))
R["smd_state"] = str(smd.ObjectState)
RES["smd"] = smd
"smd %s %d points" % (R["smd_state"], len(R["smd"]["X Coordinate"]))
#%% split
BIN = MechanicalUnitSystem.StandardBIN
V = dict(view="front", width=1400, height=520, units=BIN)
for obj, nm in ((AN, "q3_model.png"), (Model.Mesh, "q3_mesh.png"), (RES["rA"], "q3_ra.png"), (RES["rB"], "q3_rb.png")):
    export_front_framed(obj, os.path.join(OUT, nm), 114 * 0.0254, 260 * 0.0254, units=BIN)
for k in ("dy", "sf", "bm", "smd", "bt_Maximum Combined Stress", "bt_Maximum Bending Stress", "bt_Direct Stress"):
    export_image(RES[k], os.path.join(OUT, "q3_%s.png" % k.replace(" ", "_").lower()), **V)
export_image(RES["dy"], os.path.join(OUT, "q3_dy_iso.png"), view="iso", width=1400, height=800, units=BIN)
save_json(os.path.join(OUT, "q3_results.json"), R)
"images ok"
#%% split
# Euler-Bernoulli check: a copy of the analysis whose beam sections are re-declared in APDL with the
# same I-section plus SECCONTROL transverse shear stiffness ~1e6 x the real kGA, so BEAM188's shear
# deformation vanishes and the model matches the hand (Euler-Bernoulli) theory.
AN2 = AN.Duplicate()
AN2.Name = "Static Structural (shear-rigid check)"
cmd = AN2.AddCommandSnippet()
cmd.Name = "SECCONTROL: shear-rigid section"
cmd.Input = chr(10).join([
    "/prep7",
    "*get,nsecict,secp,0,num,max",
    "*do,sidict,1,nsecict",
    "sectype,sidict,beam,i",
    "secoffset,cent",
    "secdata,%r,%r,%r,%r,%r,%r" % (BF, BF, D, tf, tf, tw),
    "seccontrol,1e12,1e12",
    "*enddo",
    "/solu"])
"dup ok"
#%% split
import time
for k_ in range(4):
    AN2.Solve(True)
    if str(AN2.Solution.ObjectState) != "SolveFailed":
        break
    time.sleep(8 * (k_ + 1))
s2 = AN2.Solution
s2.EvaluateAllResults()


def _by(name):
    return [c for c in s2.Children if c.Name == name][0]


R["eb_state"] = str(s2.ObjectState)
R["eb"] = {"uyC": qval(_by(RES["uy_C"].Name).Average, "in"), "uyK": qval(_by(RES["uy_K"].Name).Average, "in"),
           "dy_max": qval(_by(RES["dy"].Name).Maximum, "in"), "dy_min": qval(_by(RES["dy"].Name).Minimum, "in"),
           "rAy": qval(_by("Reaction at pin A").YAxis, "lbf"), "rBy": qval(_by("Reaction at roller B").YAxis, "lbf")}
R["eb_messages"] = [m_.DisplayString for m_ in ExtAPI.Application.Messages if str(m_.Severity) == "Error"][-4:]
save_json(os.path.join(OUT, "q3_results.json"), R)
json.dumps(dict((k, R.get(k)) for k in ("state", "messages", "section", "cs_ansys", "rA", "rB", "uy", "dy", "beam_tool_psi",
                                        "sf_max_lbf", "bm_max_lbfin", "mesh_study", "smd_state", "eb_state", "eb", "eb_messages")))
