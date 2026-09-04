"""
cli/mcp_query.py
=================
OptionAlpha Agent — Direct MCP Server Query Tool

Usage:
    python -m cli.mcp_query account
    python -m cli.mcp_query positions
    python -m cli.mcp_query chain SPY
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mcp.mcp_integration import SyncMCPClient


def main():
    parser = argparse.ArgumentParser(description="Query Alpaca Model Context Protocol (MCP) Server")
    parser.add_argument("command", choices=["account", "positions", "chain"], help="MCP Query")
    parser.add_argument("--symbol", default="SPY", help="Symbol for chain query")
    args = parser.parse_args()

    client = SyncMCPClient()
    client.start()

    if not client.available:
        print("[!] Alpaca MCP Server not running (uvx / alpaca-mcp-server not installed)")
        return

    if args.command == "account":
        res = client.call_tool("get_account", {})
        print(res)
    elif args.command == "positions":
        res = client.call_tool("get_positions", {})
        print(res)
    elif args.command == "chain":
        res = client.call_tool("get_option_chain", {"symbol": args.symbol})
        print(res)

    client.stop()


if __name__ == "__main__":
    main()
