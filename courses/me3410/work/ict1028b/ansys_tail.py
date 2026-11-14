# Follow-up on the live session (globals from ansys.py persist): rebuild the R20 model on the final mesh,
# re-shoot the full-model plots with the legend clear of the part, and run the Mohr-Coulomb stress tool.
# Run: SCRIPT=ansys_tail.py bash run_ansys.sh, then SCRIPT=ansys_mohr.py (its stress tool here had zero limits).
FULL = ((0.17, 0.1), 0.56)


def stress_tool():
    """Mohr-Coulomb stress tool (brittle concrete: tensile 3 MPa, compressive 40 MPa)."""
    d = {}
    try:
        st = AN.Solution.AddStressTool()
        st.Theory = SafetyTheoryType.MohrCoulombStress
        st.Name = "Stress Tool: Mohr-Coulomb (St = 3, Sc = 40 MPa)"
        kids = list(st.Children)
        sf = kids[0] if kids else st.AddSafetyFactor()
        AN.Solution.EvaluateAllResults()
        d["sf_min"] = float(str(sf.Minimum).split()[0])
        d["sf_max"] = float(str(sf.Maximum).split()[0])
        d["img"] = shot(sf, "mohr_coulomb_sf.png", frame=FULL, true_scale=True)
        d["img_hole"] = shot(sf, "mohr_coulomb_sf_hole.png", frame=HOLE_Z, true_scale=True)
        d["img_fillet"] = shot(sf, "mohr_coulomb_sf_fillet.png", frame=FILLET_Z, true_scale=True)
        R["mohr"] = d
    except Exception as ex:
        PROBLEMS.append("stress tool: %s" % str(ex)[:200])
    return d
ExtAPI.DataModel.Project.New()
#%% split
setup("block_R20.step")
#%% split
R["final_check"] = mesh_solve("final (rerun)", face=FINAL[0], edge=FINAL[1])
I = R["images"]
I["model"] = shot(AN, "model.png", frame=FULL)
I["mesh"] = shot(Model.Mesh, "mesh.png", frame=FULL)
I["deformed"] = shot(RES["td"], "deformed_vs_undeformed.png", frame=FULL, wire=True)
for k in ("td", "dy", "dx", "eqv", "sx", "sy", "sxy", "sz", "s1", "s3"):
    I[k] = shot(RES[k], "%s.png" % k, frame=FULL, true_scale=True)
I["fr"] = shot(RES["fr"], "reaction_force.png", frame=FULL)
"rerun: %s" % short(R["final_check"])
#%% split
stress_tool()
save_json(os.path.join(OUT, "results.json"), R)
"mohr %s problems %s" % (R.get("mohr"), PROBLEMS[-3:])
#%% split
# Adaptive refinement: the first try stayed UnderDefined; drop the path-scoped results (already captured) first.
for k in [k for k in RES if k.endswith("_h50") or k.endswith("_v100")]:
    RES.pop(k).Delete()
R["adaptive"] = {}
adaptive("hole_2", "eqv_hole", 2.0)
#%% split
save_json(os.path.join(OUT, "results.json"), R)
json.dumps(dict((k, v) for k, v in R["adaptive"]["hole_2"].items() if k in ("state", "elements", "nodes", "eqv_hole_max", "s3_hole_min", "s1_hole_max", "dy_min", "last_change_pct", "error")))
