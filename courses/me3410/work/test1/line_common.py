# Line-body helpers that run INSIDE Mechanical (IronPython: no f-strings). Prepended by
# scripts/mech.py after pipeline/mech_common.py: --lib ../../pipeline/mech_common.py --lib line_common.py


def geo_bodies():
    out = []
    for asm in ExtAPI.DataModel.GeoData.Assemblies:
        for part in asm.Parts:
            for b in part.Bodies:
                out.append(b)
    return out


def map_line_model(joints, members, xmax, tol=1e-3):
    """joints {name: (x, y)} and members {name: (j1, j2)} in model length units; xmax is the largest
    joint x. Returns (edge id per member, tree body per member, vertex ids per joint)."""
    gb = geo_bodies()
    xm = max(v.X for b in gb for v in b.Vertices)
    f = xmax / xm
    tree = dict((tb.GetGeoBody().Id, tb) for tb in bodies())
    edge, body, verts = {}, {}, dict((j, []) for j in joints)
    for b in gb:
        for e in b.Edges:
            cx, cy = e.Centroid[0] * f, e.Centroid[1] * f
            for m, (i, j) in members.items():
                mx, my = (joints[i][0] + joints[j][0]) / 2.0, (joints[i][1] + joints[j][1]) / 2.0
                if abs(cx - mx) < tol and abs(cy - my) < tol:
                    edge[m] = e.Id
                    body[m] = tree[b.Id]
        for v in b.Vertices:
            for jn, (jx, jy) in joints.items():
                if abs(v.X * f - jx) < tol and abs(v.Y * f - jy) < tol:
                    verts[jn].append(v.Id)
    if len(edge) != len(members) or any(not v for v in verts.values()):
        raise Exception("line model mapping failed: edges %s verts %s" % (edge, verts))
    return edge, body, verts


def merge_joints(joints, members, edge, tol_q):
    """One node merge per joint where two or more members meet: the first member is the master."""
    out = []
    for jn in sorted(joints):
        ms = [m for m in sorted(members) if jn in members[m]]
        if len(ms) < 2:
            continue
        nm = Model.Mesh.AddNodeMerge()
        s1 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        s1.Ids = [edge[ms[0]]]
        s2 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        s2.Ids = [edge[m] for m in ms[1:]]
        nm.MasterLocation = s1
        nm.SlaveLocation = s2
        nm.ToleranceValue = Quantity(tol_q)
        nm.Name = "Node merge at joint %s (%s)" % (jn, ", ".join(ms))
        out.append(nm)
    return out


def sel(ids):
    s = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s.Ids = list(ids)
    return s


def axial_signed(res, unit):
    hi, lo = qval(res.Maximum, unit), qval(res.Minimum, unit)
    return hi if abs(hi) >= abs(lo) else lo


def solve_retry(an, tries=4):
    """Solve and evaluate; the Student license sometimes denies a solve that starts right after the
    previous one checked its license back in, so wait and retry."""
    import time
    for k in range(tries):
        an.Solve(True)
        if str(an.Solution.ObjectState) != "SolveFailed":
            break
        time.sleep(8 * (k + 1))
        an.Solution.ClearGeneratedData()
    an.Solution.EvaluateAllResults()
    return str(an.Solution.ObjectState)


def export_front_framed(obj, path, center_m, width_m, width=1400, height=520, units=None):
    """Front view, then zoom on (center_m [m], scene width_m [m]): SetFit on a short line body
    leaves it tiny in the middle of the window."""
    prev = ExtAPI.Application.ActiveUnitSystem
    ExtAPI.Application.ActiveUnitSystem = units or MechanicalUnitSystem.StandardNMM
    G = Ansys.Mechanical.DataModel.MechanicalEnums.Graphics
    Graphics.ViewOptions.ResultPreference.ExtraModelDisplay = G.ExtraModelDisplay.NoWireframe
    try:
        obj.Activate()
        cam = Graphics.Camera
        cam.SetSpecificViewOrientation(ViewOrientationType.Front)
        cam.SetFit()
        cam.FocalPoint = Ansys.Mechanical.Graphics.Point([center_m, 0.0, 0.0], "m")
        cam.SceneWidth = Quantity("%r [m]" % width_m)
        s = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        s.Width, s.Height = width, height
        s.Resolution = GraphicsResolutionType.EnhancedResolution
        s.Background = GraphicsBackgroundType.White
        s.CurrentGraphicsDisplay = False
        Graphics.ExportImage(path, GraphicsImageExportFormat.PNG, s)
    finally:
        ExtAPI.Application.ActiveUnitSystem = prev
    return path


def messages(n=6):
    return [m_.DisplayString for m_ in ExtAPI.Application.Messages if str(m_.Severity) in ("Error", "Warning")][-n:]
