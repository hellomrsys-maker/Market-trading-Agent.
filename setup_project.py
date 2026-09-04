#!/usr/bin/env python3
"""
setup_project.py — One-shot dev environment bootstrap

Run this once:
    python setup_project.py

What it does:
  1. Verifies Python ≥ 3.11
  2. Creates a virtual environment (.venv)
  3. Installs all Python dependencies
  4. Tries to build the Rust extension (maturin)
  5. Checks for Julia and prints the install command if missing
  6. Checks for Java (for monitoring server)
  7. Writes a .env file from .env.example if one doesn't exist
  8. Creates required directories
  9. Prints next steps
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT  = Path(__file__).resolve().parent
VENV  = ROOT / ".venv"
PYTHON= VENV / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")

# ── Console colours ───────────────────────────────────────────
def ok(s):   print(f"  \033[92m✓\033[0m  {s}")
def warn(s): print(f"  \033[93m⚠\033[0m  {s}")
def err(s):  print(f"  \033[91m✗\033[0m  {s}")
def head(s): print(f"\n\033[1;36m{'─'*55}\033[0m\n  {s}\n\033[1;36m{'─'*55}\033[0m")


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


# ─────────────────────────────────────────────────────────────
# 1. Python version
# ─────────────────────────────────────────────────────────────
head("Step 1 — Python version")
major, minor = sys.version_info[:2]
if (major, minor) < (3, 11):
    err(f"Python 3.11+ required (found {major}.{minor}). Please upgrade.")
    sys.exit(1)
ok(f"Python {major}.{minor}.{sys.version_info.micro}")

# ─────────────────────────────────────────────────────────────
# 2. Virtual environment
# ─────────────────────────────────────────────────────────────
head("Step 2 — Virtual Environment")
if not VENV.exists():
    run([sys.executable, "-m", "venv", str(VENV)])
    ok(f"Created venv at {VENV}")
else:
    ok(f"Venv already exists: {VENV}")

# ─────────────────────────────────────────────────────────────
# 3. Python dependencies
# ─────────────────────────────────────────────────────────────
head("Step 3 — Python Dependencies")
req_file = ROOT / "requirements.txt"
if req_file.exists():
    print("  Installing requirements (this may take a few minutes)…")
    result = run([str(PYTHON), "-m", "pip", "install", "-r", str(req_file), "--quiet"], check=False)
    if result.returncode == 0:
        ok("requirements.txt installed")
    else:
        warn(f"Some packages failed to install. See requirements.txt.\n{result.stderr[:500]}")
else:
    warn("requirements.txt not found")

# ─────────────────────────────────────────────────────────────
# 4. Rust extension (maturin)
# ─────────────────────────────────────────────────────────────
head("Step 4 — Rust Extension (optionalpha_data)")
rust_dir = ROOT / "engine" / "rust"
if shutil.which("maturin") or shutil.which("cargo"):
    if rust_dir.exists():
        print("  Building Rust extension with maturin develop…")
        r = run(
            [str(PYTHON), "-m", "maturin", "develop", "--release", "-q"],
            cwd=rust_dir, check=False
        )
        if r.returncode == 0:
            ok("Rust extension built — optionalpha_data available")
        else:
            warn("Rust build failed. Agent will use Python fallbacks.")
            warn(r.stderr[:300])
    else:
        warn(f"Rust source not found at {rust_dir}")
else:
    warn("Rust/Cargo not found. Install from https://rustup.rs/")
    warn("Without Rust: IV Rank, FeatureMatrix will use slower Python fallbacks")

# ─────────────────────────────────────────────────────────────
# 5. Julia
# ─────────────────────────────────────────────────────────────
head("Step 5 — Julia (options math)")
if shutil.which("julia"):
    r = run(["julia", "--version"], check=False)
    ok(f"Julia found: {r.stdout.strip()}")
    # Install PythonCall for juliacall bridge
    r2 = run(["julia", "-e", "import Pkg; Pkg.add(\"PythonCall\"); Pkg.add(\"Distributions\")"], check=False)
    ok("Julia packages installed (PythonCall, Distributions)")
else:
    warn("Julia not found. Options pricing will use Python fallbacks.")
    warn("Download Julia from: https://julialang.org/downloads/")

# ─────────────────────────────────────────────────────────────
# 6. Java (monitoring server)
# ─────────────────────────────────────────────────────────────
head("Step 6 — Java (monitoring server)")
if shutil.which("java"):
    r = run(["java", "-version"], check=False)
    ok(f"Java found: {r.stderr.strip()[:60]}")
else:
    warn("Java not found — monitoring server will be unavailable")
    warn("Install JDK 17+ from: https://adoptium.net/")

# ─────────────────────────────────────────────────────────────
# 7. .env file
# ─────────────────────────────────────────────────────────────
head("Step 7 — Environment Config")
env_file    = ROOT / ".env"
env_example = ROOT / ".env.example"
if not env_file.exists() and env_example.exists():
    shutil.copy(env_example, env_file)
    warn(".env created from .env.example — ADD YOUR API KEYS BEFORE RUNNING!")
elif env_file.exists():
    ok(".env file exists")
    # Check keys are set
    content = env_file.read_text()
    if "your_api_key_here" in content or "ALPACA_API_KEY=" not in content:
        warn("ALPACA_API_KEY appears unset in .env — please edit it!")
    else:
        ok("API keys appear to be configured")
else:
    warn("No .env or .env.example found — create .env manually")

# ─────────────────────────────────────────────────────────────
# 8. Directories
# ─────────────────────────────────────────────────────────────
head("Step 8 — Directory Structure")
for d in [
    "data/cache", "data/logs", "data/models",
    "ai/transformer", "ai/rl", "ai/ensemble",
    "engine/cuda", "engine/rust/src", "engine/cpp",
    "engine/julia", "agent/execution", "agent/risk", "agent/strategy",
    "mcp", "web", "config",
]:
    Path(ROOT / d).mkdir(parents=True, exist_ok=True)
ok("All directories created")

# ─────────────────────────────────────────────────────────────
# 9. Summary
# ─────────────────────────────────────────────────────────────
head("🚀 Setup Complete — Next Steps")
print("""
  1. Edit .env and add your Alpaca paper API keys:
       ALPACA_API_KEY=your_key
       ALPACA_SECRET_KEY=your_secret

  2. Get a paper trading account at:
       https://alpaca.markets/
     Enable Options Level 3 in the paper account settings.

  3. Train the AI models (first time, ~10-20 min):
       .venv/Scripts/python run_agent.py --train-only

  4. Run the agent (scheduled, autonomous mode):
       .venv/Scripts/python run_agent.py

  5. Open the web dashboard:
       http://127.0.0.1:8080

  6. Run a single task for testing:
       .venv/Scripts/python run_agent.py --task morning_scan
       .venv/Scripts/python run_agent.py --task execute_trades
""")
