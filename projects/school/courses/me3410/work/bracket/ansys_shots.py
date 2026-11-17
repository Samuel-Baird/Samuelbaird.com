# Re-shoot all images on the final mesh (live session; globals from ansys.py / ansys_tail.py persist).
# Run: SCRIPT=ansys_shots.py bash run_ansys.sh
ISO = "iso"
BACK = "back_iso"
FULL = ((0.030, 0.052, 0.025), 0.26)   # whole part: focal point (m), scene width (m)
def view_export(obj, path, view="iso", frame=None, true_scale=False, wire=False, width=1400, height=800):
    """Named view (iso / back_iso / bottom ...), optionally re-centred on frame = ((x, y, z) m, scene width m).
    A custom ViewVector does not take in batch mode (the camera stays on its last orientation), so the back view
    is the iso view rotated about the screen Y axis."""
    prev = ExtAPI.Application.ActiveUnitSystem
    ExtAPI.Application.ActiveUnitSystem = NMM
    G = Ansys.Mechanical.DataModel.MechanicalEnums.Graphics
    rp = Graphics.ViewOptions.ResultPreference
    rp.ExtraModelDisplay = G.ExtraModelDisplay.UndeformedWireframe if wire else G.ExtraModelDisplay.NoWireframe
    rp.DeformationScaling = G.DeformationScaling.True if true_scale else G.DeformationScaling.Auto
    try:
        obj.Activate()
        cam = Graphics.Camera
        names = {"iso": ViewOrientationType.Iso, "back_iso": ViewOrientationType.Iso,
                 "bottom": ViewOrientationType.Bottom, "front": ViewOrientationType.Front, "back": ViewOrientationType.Back}
        cam.SetSpecificViewOrientation(names[view])
        cam.SetFit()
        if view == "back_iso":
            cam.Rotate(180.0, CameraAxisType.ScreenY)
            cam.SetFit()
        if frame is None and view in ("iso", "back_iso"):
            frame = FULL
        if frame:
            cam.FocalPoint = Ansys.Mechanical.Graphics.Point(list(frame[0]), "m")
            cam.SceneWidth = Quantity("%r [m]" % frame[1])
            cam.SceneHeight = Quantity("%r [m]" % (frame[1] * height / float(width)))
        st = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        st.Width, st.Height = width, height
        st.Resolution = GraphicsResolutionType.EnhancedResolution
        st.Background = GraphicsBackgroundType.White
        st.CurrentGraphicsDisplay = False
        Graphics.ExportImage(path, GraphicsImageExportFormat.PNG, st)
        return path
    finally:
        ExtAPI.Application.ActiveUnitSystem = prev


def shots(tag, items):
    out = {}
    for key, obj, view, kw in items:
        try:
            out[key] = view_export(obj, os.path.join(OUT, "%s%s.png" % (tag, key)), view=view, **kw)
        except Exception as ex:
            PROBLEMS.append("image %s: %s" % (key, str(ex)[:120]))
    return out
#%% split
_f = mesh_solve_local(2.5, 0.5)
"remeshed: %d nodes, fillet %.2f, td %.5f" % (_f["nodes"], _f["eqv_fillet_max"], _f["td_max"])
#%% split
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
"images: %d; problems %s" % (len(I), PROBLEMS)
