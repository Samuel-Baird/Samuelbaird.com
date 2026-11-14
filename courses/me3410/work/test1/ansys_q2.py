# Test 1 Q2: roof truss, 20 x 40 mm members, Structural Steel, beam (BEAM188) line bodies joined
# at the joints. Runs inside Mechanical with mech_common.py + line_common.py. --var ASSETS, OUT.
# Units: m, N, Pa (MKS) for inputs; plots in mm / MPa.
JOINTS = {"A": (0.0, 0.0), "B": (1.5, 0.0), "C": (3.0, 0.0), "D": (4.5, 0.0), "E": (6.0, 0.0),
          "H": (1.5, 1.0), "G": (3.0, 2.0), "J": (4.5, 1.0)}
MEMBERS = dict((m, (m[0], m[1])) for m in
               ["AB", "BC", "CD", "DE", "AH", "HG", "GJ", "JE", "BH", "CG", "DJ", "HC", "CJ"])
LOADS = [("A", 17e3, "F1"), ("H", 32e3, "F2"), ("G", 17e3, "F1"), ("J", 32e3, "F2"), ("E", 25e3, "F3")]
AREA = 800e-6
R = {}
ExtAPI.DataModel.Project.New()
#%% split
Model = ExtAPI.DataModel.Project.Model
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
import_geometry(os.path.join(ASSETS, "q2_truss.step"))
EDGE, BODY, VERT = map_line_model(JOINTS, MEMBERS, 6.0)
cs = (Model.CrossSections or Model.AddCrossSections()).AddRectangularCrossSection()
cs.Name = "Rectangle 20 x 40 mm (A = 800 mm^2)"
cs.Width = Quantity("0.02 [m]")
cs.Height = Quantity("0.04 [m]")
for m, b in BODY.items():
    b.CrossSectionSelection = cs
    b.Material = "Structural Steel"
    b.Name = "Member %s-%s" % MEMBERS[m]
R["cs_area_m2"] = qval(cs.Area, "m m")
NS = dict((j, named_selection("JOINT_%s" % j, VERT[j])) for j in JOINTS)
NSM = dict((m, named_selection("MEMBER_%s" % m, [EDGE[m]])) for m in MEMBERS)
merge_joints(JOINTS, MEMBERS, EDGE, "1e-5 [m]")
AN = Model.AddStaticStructuralAnalysis()
roller = AN.AddDisplacement()
roller.Location = NS["A"]
roller.YComponent.Output.DiscreteValues = [Quantity("0 [m]")]
roller.ZComponent.Output.DiscreteValues = [Quantity("0 [m]")]
roller.Name = "Roller at A (uy = 0; ux free; uz = 0 keeps the truss planar)"
pin = AN.AddDisplacement()
pin.Location = NS["E"]
pin.XComponent.Output.DiscreteValues = [Quantity("0 [m]")]
pin.YComponent.Output.DiscreteValues = [Quantity("0 [m]")]
pin.ZComponent.Output.DiscreteValues = [Quantity("0 [m]")]
pin.Name = "Pin at E (ux = uy = uz = 0)"
rot = AN.AddFixedRotation()
rot.Location = NS["E"]
rot.RotationX = FixedOrFree.Fixed
rot.RotationY = FixedOrFree.Fixed
rot.RotationZ = FixedOrFree.Free
rot.Name = "Out-of-plane rotation at E fixed (rot Z free: in-plane pin)"
for j, p, lab in LOADS:
    f = AN.AddForce()
    f.Location = NS[j]
    f.DefineBy = LoadDefineBy.Components
    f.YComponent.Output.DiscreteValues = [Quantity("%r [N]" % (-p))]
    f.Name = "%s = %g kN at %s (-Y)" % (lab, p / 1e3, j)
sol = AN.Solution
RES = {}
for ax, en in (("x", NormalOrientationType.XAxis), ("y", NormalOrientationType.YAxis)):
    d = sol.AddDirectionalDeformation()
    d.NormalOrientation = en
    d.Name = "Directional deformation %s" % ax.upper()
    RES["d" + ax] = d
RES["td"] = sol.AddTotalDeformation()
JD = {}
for j in JOINTS:
    for ax, en in (("x", NormalOrientationType.XAxis), ("y", NormalOrientationType.YAxis)):
        p_ = sol.AddDirectionalDeformation()
        p_.NormalOrientation = en
        p_.Location = NS[j]
        p_.Name = "u%s at %s" % (ax, j)
        JD[j + ax] = p_
bt = sol.AddBeamTool()
for c in bt.Children:
    RES["bt_" + c.Name] = c
RES["axial"] = sol.AddDirectionalAxialForce()
RES["axial"].Name = "Axial force (all members)"
AXF = {}
for m in MEMBERS:
    af = sol.AddDirectionalAxialForce()
    af.Location = NSM[m]
    af.Name = "Axial force, member %s-%s" % MEMBERS[m]
    AXF[m] = af
RES["rA"] = sol.AddForceReaction()
RES["rA"].BoundaryConditionSelection = roller
RES["rA"].Name = "Reaction at roller A"
RES["rE"] = sol.AddForceReaction()
RES["rE"].BoundaryConditionSelection = pin
RES["rE"].Name = "Reaction at pin E"
"setup ok %s" % EDGE
#%% split
STUDY = []
for size in (0.5, 0.25, 0.1):
    Model.Mesh.ElementSize = Quantity("%r [m]" % size)
    Model.Mesh.GenerateMesh()
    solve_retry(AN)
    STUDY.append({"size_m": size, "elements": Model.Mesh.Elements, "nodes": Model.Mesh.Nodes,
                  "uyG": qval(JD["Gy"].Average, "m"), "F_CG": axial_signed(AXF["CG"], "N")})
R["mesh_study"] = STUDY
#%% split
Model.Mesh.ElementSize = Quantity("0.1 [m]")
Model.Mesh.GenerateMesh()
R["state"] = solve_retry(AN)
R["messages"] = messages()
R["nodes"], R["elements"] = Model.Mesh.Nodes, Model.Mesh.Elements
R["joints_mm"] = dict((j, {"x": qval(JD[j + "x"].Average, "mm"), "y": qval(JD[j + "y"].Average, "mm")}) for j in JOINTS)
R["dx_mm"] = {"max": qval(RES["dx"].Maximum, "mm"), "min": qval(RES["dx"].Minimum, "mm")}
R["dy_mm"] = {"max": qval(RES["dy"].Maximum, "mm"), "min": qval(RES["dy"].Minimum, "mm")}
R["axial_N"] = dict((m, axial_signed(AXF[m], "N")) for m in MEMBERS)
R["stress_MPa"] = dict((m, R["axial_N"][m] / AREA / 1e6) for m in MEMBERS)
R["beam_tool_MPa"] = dict((k[3:], {"max": qval(o.Maximum, "MPa"), "min": qval(o.Minimum, "MPa")})
                          for k, o in RES.items() if k.startswith("bt_"))
for k in ("rA", "rE"):
    R[k] = {"x": qval(RES[k].XAxis, "N"), "y": qval(RES[k].YAxis, "N"), "z": qval(RES[k].ZAxis, "N")}
"solved %s %s %s" % (R["state"], R["rA"], R["rE"])
#%% split
V = dict(view="front", width=1500, height=640)
export_image(AN, os.path.join(OUT, "q2_model.png"), **V)
export_image(Model.Mesh, os.path.join(OUT, "q2_mesh.png"), **V)
for k in ("dx", "dy", "td", "axial", "bt_Direct Stress"):
    export_image(RES[k], os.path.join(OUT, "q2_%s.png" % k.replace(" ", "_").lower()), **V)
export_image(RES["rA"], os.path.join(OUT, "q2_rA.png"), **V)
export_image(RES["rE"], os.path.join(OUT, "q2_rE.png"), **V)
save_json(os.path.join(OUT, "q2_results.json"), R)
json.dumps(dict((k, R[k]) for k in ("state", "messages", "rA", "rE", "axial_N", "beam_tool_MPa", "mesh_study", "dy_mm")))
