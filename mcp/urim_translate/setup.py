"""First-run setup: Argos en->pt/es packages, Ollama and its model. Idempotent; every step is skipped once done.

Runs automatically in the background the first time the server starts (marker file `setup.json` in URIM_HOME), or by
hand with `python -m urim_translate setup`. Set URIM_AUTO_SETUP=0 to turn the automatic run off.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

from . import config

MARKER = config.HOME / "setup.json"


def log(msg):
    print(f"[urim setup] {msg}", file=sys.stderr, flush=True)


def argos():
    try:
        import argostranslate.package as pkg
    except ImportError:
        log("argostranslate is not installed: pip install -e 'mcp[argos]'")
        return False
    try:
        import ctranslate2  # noqa: F401  (Argos' engine; some machines block its DLL)
    except Exception as e:
        log(f"Argos cannot run here ({type(e).__name__}: {e}); skipping it, Ollama will translate everything")
        return False
    have = {(p.from_code, p.to_code) for p in pkg.get_installed_packages()}
    need = [("en", config.ARGOS_CODE[l]) for l in config.UI_LANGS]
    if all(n in have for n in need):
        return True
    log("updating the Argos package index")
    pkg.update_package_index()
    for p in pkg.get_available_packages():
        if (p.from_code, p.to_code) in need and (p.from_code, p.to_code) not in have:
            log(f"installing Argos {p.from_code}->{p.to_code} (about 100 MB)")
            pkg.install_from_path(p.download())
    return True


def ollama_exe():
    exe = shutil.which("ollama")
    if exe:
        return exe
    for p in (Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe", Path("/usr/local/bin/ollama")):
        if p.exists():
            return str(p)
    return None


def ollama_install():
    if ollama_exe():
        return True
    if sys.platform == "win32" and shutil.which("winget"):
        log("installing Ollama with winget")
        subprocess.run(["winget", "install", "-e", "--id", "Ollama.Ollama", "--silent",
                        "--accept-package-agreements", "--accept-source-agreements"], check=False)
    elif sys.platform == "darwin" and shutil.which("brew"):
        log("installing Ollama with Homebrew")
        subprocess.run(["brew", "install", "ollama"], check=False)
    elif sys.platform.startswith("linux"):
        log("installing Ollama with its install script")
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=False)
    return bool(ollama_exe())


def ollama_up():
    try:
        httpx.get(config.OLLAMA_URL.rstrip("/") + "/api/tags", timeout=2).raise_for_status()
        return True
    except Exception:
        return False


def ollama_pull():
    exe = ollama_exe()
    if not exe:
        log("Ollama is not installed (install it from https://ollama.com), then run: python -m urim_translate setup")
        return False
    if not ollama_up():
        log("starting the Ollama service")
        subprocess.Popen([exe, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            if ollama_up():
                break
            time.sleep(1)
    if not ollama_up():
        log("the Ollama service did not start")
        return False
    tags = httpx.get(config.OLLAMA_URL.rstrip("/") + "/api/tags", timeout=5).json().get("models", [])
    if any(m["name"] in (config.OLLAMA_MODEL, config.OLLAMA_MODEL + ":latest") for m in tags):
        return True
    log(f"pulling {config.OLLAMA_MODEL} (a few GB)")
    return subprocess.run([exe, "pull", config.OLLAMA_MODEL]).returncode == 0


def run(force=False):
    if MARKER.exists() and not force:
        return json.loads(MARKER.read_text())
    state = {"argos": argos(), "ollama": ollama_install()}
    state["model"] = state["ollama"] and ollama_pull()
    log(f"done: {state}")
    if state["ollama"] and state["model"]:          # Argos is optional (it can be blocked by the OS); no marker on a partial setup so the next start retries
        config.HOME.mkdir(parents=True, exist_ok=True)
        MARKER.write_text(json.dumps(state))
    return state


def auto():
    """Called when the server starts: background first-run setup unless it already happened or is turned off."""
    import threading
    if MARKER.exists() or os.environ.get("URIM_AUTO_SETUP", "1") == "0":
        return
    threading.Thread(target=run, daemon=True, name="urim-setup").start()
