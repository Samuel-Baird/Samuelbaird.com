# Fonts

Static weight instances generated (with fontTools `varLib.instancer`) from
the Google Fonts variable masters, so matplotlib can select weights. All
three families are licensed under the SIL Open Font License 1.1:

| Family | Role here | Stand-in for (Deseret News brand guide) | Source |
| --- | --- | --- | --- |
| Newsreader (opsz 36 / 16) | serif display titles, serif text | Poynter Old Style | https://github.com/google/fonts/tree/main/ofl/newsreader |
| Libre Franklin | labels, deks, footers | Benton Sans | https://github.com/google/fonts/tree/main/ofl/librefranklin |
| Oswald | condensed hero numerals | Benton Sans Extra Compressed | https://github.com/google/fonts/tree/main/ofl/oswald |

Regenerate an instance, e.g.:

```python
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
inst = instancer.instantiateVariableFont(TTFont("LibreFranklin[wght].ttf"), {"wght": 700}, updateFontNames=False)
inst.save("LibreFranklin-Bold.ttf")
```

(For Newsreader pass `updateFontNames=False` and set the name records by
hand; its STAT table has no axis value for opsz 36, so automatic renaming
fails.)
