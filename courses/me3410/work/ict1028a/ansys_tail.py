# Continuation of ansys.py on the live Mechanical session (globals from the earlier run persist).
for c in [c for c in AN.Solution.Children if 'Fatigue' in str(c.GetType())]:
    c.Delete()
def fatigue(tag, ratio=None, theory="NoneStress"):
    ft = AN.Solution.AddFatigueTool()
    ft.AnalysisType = FatigueToolAnalysisType.StressLife
    ft.StressComponent = FatigueStressComponentType.FatigueToolVon_Mises
    if ratio is None:
        ft.LoadingType = FatigueLoadType.FullyReversed
    else:
        ft.LoadingType = FatigueLoadType.Ratio
        ft.LoadingRatio = ratio
    ft.MeanStressTheory = getattr(Ansys.Mechanical.DataModel.Enums.MeanStressTheoryType, theory)
    ft.Name = "Fatigue Tool (%s)" % tag
    life = ft.AddLife()
    sf = ft.AddSafetyFactor()
    try:
        sf.DesignLife = Quantity("1e6 [cycles]")
    except Exception:
        try:
            sf.DesignLife = 1e6
        except Exception as ex:
            PROBLEMS.append("DesignLife: %s" % str(ex)[:100])
    AN.Solution.EvaluateAllResults()
    d = {"ratio": -1.0 if ratio is None else ratio, "theory": str(ft.MeanStressTheory)}
    for k, o in (("life", life), ("sf", sf)):
        try:
            d[k + "_min"] = float(str(o.Minimum).split()[0])
            d[k + "_max"] = float(str(o.Maximum).split()[0])
        except Exception as ex:
            PROBLEMS.append("fatigue %s %s: %s" % (tag, k, str(ex)[:100]))
    try:
        d["design_life"] = str(sf.DesignLife)
    except Exception:
        pass
    d["img_life"] = shot(life, "fatigue_%s_life.png" % tag)
    d["img_sf"] = shot(sf, "fatigue_%s_sf.png" % tag)
    d["img_sf_zoom"] = shot(sf, "fatigue_%s_sf_zoom.png" % tag, frame=FILLET_Z)
    R["fatigue"][tag] = d
    return "%s: %s" % (tag, dict((k, v) for k, v in d.items() if not k.startswith("img")))
#%% split
fatigue("R-1")
#%% split
fatigue("R-0.5_goodman", ratio=-0.5, theory="Goodman")
#%% split
save_json(os.path.join(OUT, "results.json"), R)
#%% split
adaptive("fillet_5", "eqv_fillet", 5.0)
#%% split
adaptive("fillet_1", "eqv_fillet", 1.0)
#%% split
save_json(os.path.join(OUT, "results.json"), R)
json.dumps({"adaptive": dict((t, dict((k, v) for k, v in d.items() if k != "history" and not k.startswith("img")))
                             for t, d in R["adaptive"].items()), "fatigue": R["fatigue"], "problems": PROBLEMS})
