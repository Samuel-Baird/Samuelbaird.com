"""Build the held-out data the benchmark's pipeline arm may see: Church glossary evidence and translation memory
with the test conference (default 2026-04) left out.

    mcp/.venv/Scripts/python bench/heldout.py [2026-04]

Writes bench/heldout/data/glossary/{es,pt}.json (point URIM_GLOSSARY_DIR at it) and seeds bench/home-pipeline's
translation memory from the Church's exact-aligned paragraphs minus that conference.
"""
import os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
URIM = HERE.parent
EXCL = sys.argv[1] if len(sys.argv) > 1 else "2026-04"
DATA = HERE / "heldout" / "data"
DATA.mkdir(parents=True, exist_ok=True)
shutil.copy(URIM / "data" / "english_first.json", DATA / "english_first.json")   # English-side only, no translations
os.environ["URIM_DATA"], os.environ["URIM_EXCLUDE"] = str(DATA), EXCL
sys.path.insert(0, str(URIM))
from pipeline import attest, build            # noqa: E402  (read the env vars at import)

attest.run()
build.glossary(build.load()[0])
print("seeding translation memory without", EXCL)
env = dict(os.environ, URIM_HOME=str(HERE / "home-pipeline"))
py = URIM / "mcp" / ".venv" / "Scripts" / "python.exe"
subprocess.run([str(py), "-m", "urim_translate", "seed-tm", f"--exclude={EXCL}"], cwd=URIM / "mcp", env=env, check=True)
