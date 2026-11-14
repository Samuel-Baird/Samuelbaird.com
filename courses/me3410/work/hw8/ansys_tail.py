# Continuation of ansys.py on the live Mechanical session (globals persist): the leg maximum sits on the sharp
# pipe-to-flange corner, so add von Mises paths along the outside of each leg starting at that corner, re-solve on
# the final mesh, and save the profiles. Run: SCRIPT=ansys_tail.py bash run_ansys.sh
LEGS = {
    # leg 1 outside surface (z from the flange face 20 to the bend start 100), bottom (y = -30) and top (y = +30)
    "leg1_bot": ("Leg 1 outside, y = -30, from the flange (z = 20..100)", (0.0, -29.95, 20.0), (0.0, -29.95, 100.0)),
    "leg1_top": ("Leg 1 outside, y = +30, from the flange (z = 20..100)", (0.0, 29.95, 20.0), (0.0, 29.95, 100.0)),
    # leg 2 outside surface (y from the flange face 150 down to the bend start 70), outer (z = 200) and inner (z = 140)
    "leg2_out": ("Leg 2 outside, z = 200, from the flange (y = 150..70)", (0.0, 150.0, 199.95), (0.0, 70.0, 199.95)),
    "leg2_in": ("Leg 2 outside, z = 140, from the flange (y = 150..70)", (0.0, 150.0, 140.05), (0.0, 70.0, 140.05)),
}
for k, (nm, p0, p1) in LEGS.items():
    P[k] = add_path(nm, p0, p1, 81)
    RP["eqv_" + k] = path_result(ST.Solution, "AddEquivalentStress", P[k], "Equivalent stress: " + nm)
solve_retry(ST)
R["final"] = read_paths(R["final"])
for k in LEGS:
    R["profiles"]["eqv_" + k] = plot_data(RP["eqv_" + k])
save_json(os.path.join(OUT, "results.json"), R)
"; ".join("%s %.1f" % (k, R["final"].get("eqv_" + k + "_max") or 0) for k in LEGS) + "; problems %s" % PROBLEMS
