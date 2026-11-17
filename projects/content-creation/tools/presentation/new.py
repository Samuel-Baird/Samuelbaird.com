"""Create D:\\Videos\\<slug>\\ for a presentation project and a starter project.json.

    python tools/presentation/new.py <slug> [--root D:\\Videos]

Then copy the card contents in (layout below), fill in the camera/mic file names, and run
sync.py. See docs/types/presentation.md for the whole run.

    D:\\Videos\\<slug>\\
      source\\cam-a\\  source\\cam-b\\  source\\mic\\   camera cards and recorder takes, as copied
      images\\        slide images (renamed by content: 03_pct_trinity_agree.png ...)
      graphics\\      extra charts/photos for shorts (licences in graphics\\credits.json)
      exports\\       <slug>.mp4, shorts\\, thumbnails\\, publishing.md
      work\\          everything generated and cached (transcripts, cards, units, plates)
      project.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TEMPLATE = {
    "slug": "",
    "root": "",
    "takes": {
        "1": {"mic": "source/mic/<take>_Tr1.WAV",
              "cameras": {"A": {"file": "source/cam-a/<clip>.MP4", "face": [0.52, 0.37], "offset": None},
                          "B": {"file": "source/cam-b/<clip>.MP4", "face": [0.43, 0.33], "offset": None}}}
    },
    "longform": {"take": "1", "start": 0, "end": 0, "slides_dir": "images", "split_camera": "A",
                 "cuts": [], "plan": [], "output": "exports/<slug>.mp4"},
    "shorts_dir": "exports/shorts",
    "shorts": {},
    "caption_fixes": {"words": {}, "phrases": [], "insert": []},
    "thumbnails": []
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--root', default=r'D:\Videos')
    a = ap.parse_args()
    root = Path(a.root) / a.slug
    for sub in ('source/cam-a', 'source/cam-b', 'source/mic', 'images', 'graphics', 'exports/shorts',
                'exports/thumbnails', 'work'):
        (root / sub).mkdir(parents=True, exist_ok=True)
    pj = root / 'project.json'
    if not pj.exists():
        cfg = json.loads(json.dumps(TEMPLATE).replace('<slug>', a.slug))
        cfg['slug'], cfg['root'] = a.slug, root.as_posix()
        pj.write_text(json.dumps(cfg, indent=2) + '\n', encoding='utf-8')
    print(root)


if __name__ == '__main__':
    main()
