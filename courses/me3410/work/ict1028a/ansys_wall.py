# Re-shoot the wall-corner close-up on the final mesh (live session; globals from ansys.py persist).
WALL_Z = ((0.009, 0.007), 0.026)
_d = mesh_solve("final again", face=1.25)
shot(RES["eqv"], "von_mises_wall_zoom.png", frame=WALL_Z, true_scale=True)
shot(RES["eqv_wall"], "von_mises_wall_edge.png", frame=WALL_Z, true_scale=True)
"%.3f %.3f %d" % (_d["eqv_fillet_max"], _d["eqv_wall_max"], _d["elements"])
