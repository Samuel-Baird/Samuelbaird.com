# Continuation of ansys.py on the live Mechanical session (globals persist): the fillet peak was still rising
# at a 2.5 / 1.25 mm mesh, so refine the fillet and hole further at a 2.5 mm global size, add an adaptive
# (Convergence) check on the fillet, and redo the final results and images on the finest mesh.
# Run: SCRIPT=ansys_tail.py bash run_ansys.sh
LOCAL = [0.8, 0.5, 0.35]
FILLET_Z = ((0.050, 0.016, 0.014), 0.045)
R["local"] = []


def mesh_solve_local(glob, loc):
    Model = ExtAPI.DataModel.Project.Model
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity("%r [mm]" % glob)
    SIZ.ElementSize = Quantity("%r [mm]" % loc)
    Model.Mesh.GenerateMesh()
    d = {"size": glob, "local": loc, "nodes": Model.Mesh.Nodes, "elements": Model.Mesh.Elements}
    if d["nodes"] > NODE_LIMIT:
        d["skipped"] = "over node limit"
        return d
    solve_retry(AN)
    return read(d)
#%% split
for s in LOCAL:
    R["local"].append(mesh_solve_local(2.5, s))
    if R["local"][-1].get("skipped"):
        break
", ".join("%g mm: %d nodes, fillet %.2f base %.1f back %.2f td %.5f %s" % (
    c["local"], c["nodes"], c.get("eqv_fillet_max", 0), c.get("eqv_base_max", 0), c.get("sy_back_max", 0),
    c.get("td_max", 0), c.get("max_loc")) for c in R["local"])
#%% split
fin = [c for c in R["local"] if not c.get("skipped")][-1]
if R["local"][-1].get("skipped"):
    fin = mesh_solve_local(2.5, fin["local"])
R["final"] = fin
for k in ("sy_back", "sy_thick", "sy_side"):
    R["final"][k + "_profile"] = plot_data(RES[k])
I = {}
I.update(shots("", [
    ("model", AN, ISO, {}), ("bc_fixed", FIX, ISO, {}), ("bc_bearing", BEAR, ISO, {}), ("bc_force_z", FZL, ISO, {}),
    ("mesh", Model.Mesh, ISO, {}), ("mesh_back", Model.Mesh, BACK, {}),
    ("deformed", RES["td"], ISO, {"wire": True}),
    ("td", RES["td"], ISO, {}), ("dx", RES["dx"], ISO, {}), ("dy", RES["dy"], ISO, {}), ("dz", RES["dz"], ISO, {}),
    ("eqv", RES["eqv"], ISO, {"true_scale": True}), ("eqv_back", RES["eqv"], BACK, {"true_scale": True}),
    ("eqv_fillet", RES["eqv_fillet"], ISO, {"true_scale": True}),
    ("eqv_bearing", RES["eqv_bearing"], ISO, {"true_scale": True}),
    ("eqv_base", RES["eqv_base"], "bottom", {"true_scale": True}),
    ("fr", RES["fr"], ISO, {}), ("mr", RES["mr"], ISO, {}),
]))
for key, obj in (("mesh_fillet_zoom", Model.Mesh), ("eqv_fillet_zoom", RES["eqv"])):
    try:
        I[key] = view_export(obj, os.path.join(OUT, key + ".png"), view=ISO, frame=FILLET_Z, true_scale=True)
    except Exception as ex:
        PROBLEMS.append("image %s: %s" % (key, str(ex)[:120]))
R["images"] = I
save_json(os.path.join(OUT, "results.json"), R)
"final: %s; problems %s" % (dict((k, v) for k, v in R["final"].items() if not k.endswith("profile")), PROBLEMS)
#%% split
# Adaptive check: Convergence object on the fillet von Mises, from the 5 mm mesh with no local sizing.
Model.Mesh.ElementSize = Quantity("5 [mm]")
SIZ.Suppressed = True
conv = RES["eqv_fillet"].AddConvergence()
conv.Type = ConvergenceType.Maximum
conv.AllowableChange = 2.0
AN.Solution.MaximumRefinementLoops = 5
AN.Solution.RefinementDepth = 1
d = {"start": 5.0, "allowable_pct": 2.0, "loops_max": 5}
try:
    Model.Mesh.GenerateMesh()
    d["start_nodes"] = Model.Mesh.Nodes
    solve_retry(AN)
    read(d)
    d["nodes"] = Model.Mesh.Nodes
    try:
        d["last_change_pct"] = float(str(conv.LastChange).split()[0])
    except Exception:
        d["last_change_pct"] = None
    try:
        d["history"] = [(str(x.Caption), str(x.StringValue)) for x in conv.VisibleProperties]
    except Exception:
        pass
except Exception as ex:
    d["error"] = str(ex)[:300]
conv.Delete()
AN.Solution.MaximumRefinementLoops = 1
SIZ.Suppressed = False
R["adaptive"] = d
save_json(os.path.join(OUT, "results.json"), R)
json.dumps({"adaptive": dict((k, v) for k, v in d.items() if k != "history"), "problems": PROBLEMS})
