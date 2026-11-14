# Mohr-Coulomb stress tool on the R20 model, on the live session after ansys_tail.py (globals persist).
# The limits must be the ultimate strengths (3 MPa tension, 40 MPa compression): the default "yield per material"
# limits are zero for concrete. Run: SCRIPT=ansys_mohr.py bash run_ansys.sh
for k in [k for k in list(AN.Solution.Children) if "Stress Tool" in k.Name]:
    k.Delete()
R["final_check"] = mesh_solve("final (rerun 2)", face=FINAL[0], edge=FINAL[1])
ST = AN.Solution.AddStressTool()
ST.Theory = SafetyTheoryType.MohrCoulombStress
ST.TensileLimitType = SafetyLimitType.UltimatePerMaterial
ST.CompressiveLimitType = SafetyLimitType.UltimatePerMaterial
ST.Name = "Stress Tool: Mohr-Coulomb (St = 3, Sc = 40 MPa)"
kids = list(ST.Children)
SF = kids[0] if kids else ST.AddSafetyFactor()
AN.Solution.EvaluateAllResults()
d = {"mode": "ultimate per material"}
d["sf_min"] = float(str(SF.Minimum).split()[0])
d["sf_max"] = float(str(SF.Maximum).split()[0])
d["img"] = shot(SF, "mohr_coulomb_sf.png", frame=FULL, true_scale=True)
d["img_hole"] = shot(SF, "mohr_coulomb_sf_hole.png", frame=HOLE_Z, true_scale=True)
d["img_fillet"] = shot(SF, "mohr_coulomb_sf_fillet.png", frame=FILLET_Z, true_scale=True)
R["mohr"] = d
R["adaptive"] = {}
save_json(os.path.join(OUT, "results.json"), R)
json.dumps(d)
