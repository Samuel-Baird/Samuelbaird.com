# Test 1 Q3: simply supported 4 x 4 x 1/2 in box beam, two 500 lb loads, Structural Steel (BEAM188).
# Runs inside Mechanical with mech_common.py + line_common.py. --var ASSETS, OUT. Units: in, lbf, psi.
JOINTS = {"L": (0.0, 0.0), "P1": (16.0, 0.0), "M": (22.0, 0.0), "P2": (28.0, 0.0), "Rt": (44.0, 0.0)}
MEMBERS = {"s1": ("L", "P1"), "s2": ("P1", "M"), "s3": ("M", "P2"), "s4": ("P2", "Rt")}
P = 500.0
R = {}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardBIN
import_geometry(os.path.join(ASSETS, "q3_beam.step"))
EDGE, BODY, VERT = map_line_model(JOINTS, MEMBERS, 44.0)
cs = (Model.CrossSections or Model.AddCrossSections()).AddHollowRectangularCrossSection()
cs.Name = "Square tube 4 x 4 in, 1/2 in wall"
cs.Width1 = Quantity("4 [in]")
cs.Width2 = Quantity("4 [in]")
for t in ("Thick1", "Thick2", "Thick3", "Thick4"):
    setattr(cs, t, Quantity("0.5 [in]"))
for m, b in BODY.items():
    b.CrossSectionSelection = cs
    b.Material = "Structural Steel"
R["cs"] = {"A_in2": qval(cs.Area, "in in"), "IYY_in4": qval(cs.IYY, "in in in in"), "IZZ_in4": qval(cs.IZZ, "in in in in")}
NS = dict((j, named_selection("POINT_%s" % j, VERT[j])) for j in JOINTS)
NS_BEAM = named_selection("BEAM", [EDGE[m] for m in sorted(MEMBERS)])
merge_joints(JOINTS, MEMBERS, EDGE, "0.001 [in]")
AN = Model.AddStaticStructuralAnalysis()
pin = AN.AddDisplacement()
pin.Location = NS["L"]
for c in ("XComponent", "YComponent", "ZComponent"):
    getattr(pin, c).Output.DiscreteValues = [Quantity("0 [in]")]
pin.Name = "Pin at left support (ux = uy = uz = 0)"
rot = AN.AddFixedRotation()
rot.Location = NS["L"]
rot.RotationX = FixedOrFree.Fixed
rot.RotationY = FixedOrFree.Free
rot.RotationZ = FixedOrFree.Free
rot.Name = "Twist about the beam axis fixed at the pin (bending rotations free)"
roller = AN.AddDisplacement()
roller.Location = NS["Rt"]
roller.YComponent.Output.DiscreteValues = [Quantity("0 [in]")]
roller.ZComponent.Output.DiscreteValues = [Quantity("0 [in]")]
roller.Name = "Roller at right support (uy = uz = 0; ux free)"
for j in ("P1", "P2"):
    f = AN.AddForce()
    f.Location = NS[j]
    f.DefineBy = LoadDefineBy.Components
    f.YComponent.Output.DiscreteValues = [Quantity("%r [lbf]" % (-P))]
    f.Name = "P = 500 lb at x = %g in (-Y)" % JOINTS[j][0]
sol = AN.Solution
RES = {}
RES["dy"] = sol.AddDirectionalDeformation()
RES["dy"].NormalOrientation = NormalOrientationType.YAxis
RES["dy"].Name = "Directional deformation Y (vertical deflection)"
for j in ("P1", "M"):
    p_ = sol.AddDirectionalDeformation()
    p_.NormalOrientation = NormalOrientationType.YAxis
    p_.Location = NS[j]
    p_.Name = "uy at %s" % j
    RES["uy_" + j] = p_
bt = sol.AddBeamTool()
for c in bt.Children:
    RES["bt_" + c.Name] = c
o = bt.AddMaximumBendingStress()
RES["bt_" + o.Name] = o
RES["sf"] = sol.AddTotalShearForce()
RES["bm"] = sol.AddTotalBendingMoment()
RES["rL"] = sol.AddForceReaction()
RES["rL"].BoundaryConditionSelection = pin
RES["rL"].Name = "Reaction at the pin (left)"
RES["rR"] = sol.AddForceReaction()
RES["rR"].BoundaryConditionSelection = roller
RES["rR"].Name = "Reaction at the roller (right)"
"setup ok %s %s" % (EDGE, R["cs"])
#%% split
STUDY = []
for size in (4.0, 2.0, 1.0, 0.5):
    Model.Mesh.ElementSize = Quantity("%r [in]" % size)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    STUDY.append({"size_in": size, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
                  "uy_mid": qval(RES["uy_M"].Average, "in"),
                  "sb_max": qval(RES["bt_Maximum Bending Stress"].Maximum, "psi")})
R["mesh_study"] = STUDY
#%% split
Model.Mesh.ElementSize = Quantity("1 [in]")
Model.Mesh.GenerateMesh()
R["state"] = solve_retry(AN)
R["messages"] = messages()
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["uy"] = dict((j, qval(RES["uy_" + j].Average, "in")) for j in ("P1", "M"))
R["dy"] = {"max": qval(RES["dy"].Maximum, "in"), "min": qval(RES["dy"].Minimum, "in")}
R["beam_tool_psi"] = dict((k[3:], {"max": qval(o.Maximum, "psi"), "min": qval(o.Minimum, "psi")})
                          for k, o in RES.items() if k.startswith("bt_"))
R["sf_max_lbf"], R["bm_max_lbfin"] = qval(RES["sf"].Maximum, "lbf"), qval(RES["bm"].Maximum, "lbf in")
for k in ("rL", "rR"):
    R[k] = {"x": qval(RES[k].XAxis, "lbf"), "y": qval(RES[k].YAxis, "lbf"), "z": qval(RES[k].ZAxis, "lbf")}
"solved %s %s %s" % (R["state"], R["rL"], R["rR"])
#%% split
# Shear-moment diagram along the beam axis. It must be scoped to an edge path, and it is added
# after the solve: an unscoped diagram leaves the solution UnderDefined and the solve fails.
cg = Model.ConstructionGeometry or Model.AddConstructionGeometry()
path = cg.AddPath()
path.PathType = PathScopingType.Edge
path.Location = NS_BEAM
path.Name = "Beam axis path"
smd = sol.AddShearMomentDiagramMZ()
smd.Path = path
smd.Name = "Shear-Moment Diagram (beam axis path)"
sol.EvaluateAllResults()
pdat = smd.PlotData
# PlotData is in SI and in the path's local axes (bending shows up as SFZ / MY / UZ here).
R["smd"] = dict((str(k), [float(v) for v in pdat[k]]) for k in ("X Coordinate", "SFY", "SFZ", "MY", "MZ", "UY", "UZ"))
R["smd_state"] = str(smd.ObjectState)
"smd %s %d points" % (R["smd_state"], len(R["smd"]["X Coordinate"]))
#%% split
BIN = MechanicalUnitSystem.StandardBIN
V = dict(view="front", width=1400, height=520, units=BIN)
# Undeformed views: zoom on the 44 in beam (SetFit leaves it small). Contours keep the fitted view.
for obj, nm in ((AN, "q3_model.png"), (Model.Mesh, "q3_mesh.png"), (RES["rL"], "q3_rl.png"), (RES["rR"], "q3_rr.png")):
    export_front_framed(obj, os.path.join(OUT, nm), 22 * 0.0254, 54 * 0.0254, units=BIN)
for k in ("dy", "sf", "bm", "bt_Maximum Combined Stress", "bt_Maximum Bending Stress", "bt_Direct Stress"):
    export_image(RES[k], os.path.join(OUT, "q3_%s.png" % k.replace(" ", "_").lower()), **V)
export_image(RES["dy"], os.path.join(OUT, "q3_dy_iso.png"), view="iso", width=1400, height=800, units=BIN)
save_json(os.path.join(OUT, "q3_results.json"), R)
json.dumps(dict((k, R.get(k)) for k in ("state", "messages", "cs", "rL", "rR", "uy", "beam_tool_psi", "sf_max_lbf", "bm_max_lbfin", "mesh_study", "smd_state")))
