"""
run_agent.py
=============
OptionAlpha Agent — Entry Point

Usage:
    # Copy and configure environment
    cp .env.example .env
    # Edit .env with Alpaca paper API keys

    # Bootstrap (run once — installs deps, builds Rust extension)
    python setup_project.py

    # Train AI models first (one-time, ~10-20 min)
    python run_agent.py --train-only

    # Run agent in live scheduled mode
    python run_agent.py

    # Run a single task immediately (testing)
    python run_agent.py --task morning_scan
    python run_agent.py --task execute_trades
    python run_agent.py --task review_positions
    python run_agent.py --task eod_review

    # Dashboard only (no trading)
    python run_agent.py --dashboard-only

    # Skip MCP server startup
    python run_agent.py --no-mcp
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Project root on PYTHONPATH ─────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# ── Globally accessible agent instance (used by web/api.py) ─
_agent_instance = None   # type: ignore[assignment]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="OptionAlpha Agent — Autonomous Options Trading Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--task", choices=[
        "morning_scan", "execute_trades",
        "review_positions", "eod_review", "ai_training",
        "autonomous", "profit_scan",
    ], help="Run a single task immediately, then exit")
    p.add_argument("--train-only",      action="store_true", help="Train AI and exit")
    p.add_argument("--dashboard-only",  action="store_true", help="Serve dashboard only (no trading)")
    p.add_argument("--no-mcp",          action="store_true", help="Disable MCP server")
    p.add_argument("--port",            type=int, default=8080, help="Dashboard port (default 8080)")
    p.add_argument("--autonomous",      action="store_true", help="Run 24/7 continuous autonomous profit maximization loop")
    p.add_argument("--collect-data",    action="store_true", help="Run data collector and exit")
    return p.parse_args()


def start_dashboard(port: int) -> None:
    """Launch FastAPI + uvicorn in a daemon thread."""
    try:
        import uvicorn
        from web.api import app

        config = uvicorn.Config(
            app       = app,
            host      = "127.0.0.1",
            port      = port,
            log_level = "warning",
        )
        server = uvicorn.Server(config)

        t = threading.Thread(target=server.run, daemon=True)
        t.start()
        time.sleep(1.0)   # wait for server bind
        print(f"  [+] Dashboard  -> http://127.0.0.1:{port}")
        print(f"  [+] API docs   -> http://127.0.0.1:{port}/api/docs")
    except ImportError:
        print("  [!] uvicorn not installed — dashboard unavailable")
        print("     Install with: pip install uvicorn[standard]")


def start_mcp() -> None:
    """Attempt to start the Alpaca MCP server."""
    try:
        from mcp.mcp_integration import SyncMCPClient
        mcp = SyncMCPClient()
        mcp.start()
        if mcp.available:
            print("  [+] Alpaca MCP -> running")
        else:
            print("  [!] Alpaca MCP -> unavailable (uvx/alpaca-mcp-server not found)")
    except Exception as exc:
        print(f"  [!] MCP startup skipped: {exc}")


def main() -> None:
    global _agent_instance
    args = parse_args()

    from loguru import logger

    # ── Data collection only ──────────────────────────────────
    if args.collect_data:
        from data.collector import DataCollector
        dc = DataCollector()
        dc.collect_all()
        print("Data collection complete.")
        return

    # ── Dashboard only ────────────────────────────────────────
    if args.dashboard_only:
        start_dashboard(args.port)
        print("\nDashboard running. Press Ctrl+C to stop.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        return

    # ── Agent startup ─────────────────────────────────────────
    from agent.main import OptionAlphaAgent
    agent = OptionAlphaAgent()
    _agent_instance = agent

    # Start supporting services
    if not args.no_mcp:
        start_mcp()
    start_dashboard(args.port)

    # ── Train only ────────────────────────────────────────────
    if args.train_only:
        print("\n  Training all AI models (this may take 10-20 min)...\n")
        agent._run_ai_training()
        print("\n✅ Training complete. Run `python run_agent.py` to start trading.\n")
        return

    # ── Single task ───────────────────────────────────────────
    if args.task:
        print(f"\n  Running task: {args.task}\n")
        agent.run_now(args.task)
        return

    # ── Live autonomous / scheduled mode ──────────────────────
    print("\n" + "═" * 60)
    print("  OptionAlpha Agent — LIVE (Paper Trading Mode)")
    print("  Autonomous Profit Maximizer: ACTIVE (All 17 Phases)")
    print("  Ctrl+C to stop gracefully")
    print("═" * 60 + "\n")
    if args.autonomous:
        agent.start_autonomous()
    else:
        agent.start()   # blocks until SIGINT


if __name__ == "__main__":
    main()
