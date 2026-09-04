"""
cli/agent_cli.py
=================
OptionAlpha Agent — Interactive Terminal Control CLI

Usage:
    python -m cli.agent_cli status
    python -m cli.agent_cli positions
    python -m cli.agent_cli risk
    python -m cli.agent_cli halt
    python -m cli.agent_cli resume
    python -m cli.agent_cli scan
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

API_URL = "http://127.0.0.1:8080/api"


def _api_get(endpoint: str) -> dict:
    try:
        req = urllib.request.Request(f"{API_URL}/{endpoint}", headers={"User-Agent": "OptionAlpha-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Agent API unavailable on {API_URL}: {e}"}


def main():
    parser = argparse.ArgumentParser(description="OptionAlpha Agent Terminal Management CLI")
    parser.add_argument("command", choices=["status", "positions", "risk", "halt", "resume", "scan"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "status":
        data = _api_get("status")
        print("\n=== OPTIONALPHA AGENT STATUS ===")
        print(f"Equity:      ${data.get('equity', 0):,.2f}")
        print(f"Daily P&L:   ${data.get('daily_pnl', 0):+,.2f}")
        print(f"Positions:   {data.get('n_positions', 0)}")
        print(f"Regime:      {data.get('regime', 'Unknown')}")
        print(f"Halted:      {data.get('halted', False)}")
        print(f"Data Age:    {data.get('data_age_s', 0):.1f}s")
        print("================================\n")

    elif args.command == "positions":
        data = _api_get("positions")
        print("\n=== OPEN POSITIONS ===")
        print(json.dumps(data, indent=2))
        print("======================\n")

    elif args.command == "risk":
        data = _api_get("risk")
        print("\n=== RISK GATE STATE ===")
        print(json.dumps(data, indent=2))
        print("=======================\n")

    elif args.command in ["halt", "resume"]:
        print(f"Signal sent: {args.command}")


if __name__ == "__main__":
    main()
