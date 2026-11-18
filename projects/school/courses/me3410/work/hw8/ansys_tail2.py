# Second continuation (globals persist): radial paths across flange 1, between two bolt holes (45 deg), on the fixed
# face and 2, 5 and 10 mm inside it, to see the stress the in-plane restraint of the face causes away from its edges.
# Also the radial / hoop / axial normal stresses on the face path. Run: SCRIPT=ansys_tail2.py bash run_ansys.sh
c45 = math.cos(math.radians(45.0))
FACE = {}
for dz in (0.02, 2.0, 5.0, 10.0):
    k = "face_%g" % dz
    FACE[k] = dz
    P[k] = add_path("Flange 1, r = 26..49 at 45 deg, z = %g" % dz, (26.0 * c45, 26.0 * c45, dz), (49.0 * c45, 49.0 * c45, dz), 47)
    RP["eqv_" + k] = path_result(ST.Solution, "AddEquivalentStress", P[k], "Equivalent stress: " + P[k].Name)
RP["sz_face_0.02"] = path_result(ST.Solution, "AddNormalStress", P["face_0.02"], "Normal stress Z on the fixed face",
                                 NormalOrientationType.ZAxis)
RP["s1_face_0.02"] = path_result(ST.Solution, "AddMaximumPrincipalStress", P["face_0.02"], "Max principal on the fixed face")
RP["s3_face_0.02"] = path_result(ST.Solution, "AddMinimumPrincipalStress", P["face_0.02"], "Min principal on the fixed face")
solve_retry(ST)
R["final"] = read_paths(R["final"])
for k in list(FACE.keys()):
    R["profiles"]["eqv_" + k] = plot_data(RP["eqv_" + k])
for k in ("sz_face_0.02", "s1_face_0.02", "s3_face_0.02"):
    R["profiles"][k] = plot_data(RP[k])
save_json(os.path.join(OUT, "results.json"), R)
"; ".join("%s %.1f..%.1f" % (k, R["final"].get("eqv_" + k + "_min") or 0, R["final"].get("eqv_" + k + "_max") or 0)
          for k in FACE) + "; problems %s" % PROBLEMS
