"""
mcp/mcp_integration.py
========================
OptionAlpha Agent — Alpaca MCP Server Integration

Alpaca's official MCP server allows an LLM (or our autonomous agent)
to interact with the trading account using structured tool calls
without needing raw REST API calls.

In OptionAlpha Agent, the MCP server is used for:
  1. Portfolio health queries ("What's my current P&L breakdown?")
  2. Option chain analysis ("Find the best CSP on NVDA for next month")
  3. Risk validation ("Do I have capacity to add another position?")
  4. Natural language trade logs (generates human-readable summaries)

Architecture:
  - The MCP server runs as a subprocess launched by this module
  - Communication uses the MCP stdio transport (JSON-RPC over stdin/stdout)
  - Our agent sends tool requests; the server returns structured responses
  - The self-developed AI decision layer interprets these responses

Tool set exposed by Alpaca MCP:
  - get_account       : account equity, buying power, positions
  - get_positions     : all open positions with current P&L
  - get_orders        : open/filled orders
  - get_option_chain  : option contracts for a symbol
  - place_order       : submit orders (we use this for MCP-driven trades)
  - get_bars          : historical OHLCV data

Usage:
    async with MCPSession() as mcp:
        result = await mcp.call_tool("get_account", {})
        print(result)
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from config.settings import get_alpaca_settings

_cfg = get_alpaca_settings()


class MCPSession:
    """
    Async context manager for the Alpaca MCP server subprocess.

    The MCP server is invoked as:
      uvx alpaca-mcp-server

    Environment variables are set to configure paper trading:
      ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

    JSON-RPC messages are exchanged over the process's
    stdin / stdout (MCP stdio transport).
    """

    MCP_CMD = ["uvx", "alpaca-mcp-server"]

    def __init__(self):
        self._proc:    Optional[asyncio.subprocess.Process] = None
        self._req_id:  int = 0
        self._pending: Dict[int, asyncio.Future] = {}
        self._reader_task: Optional[asyncio.Task] = None

    async def __aenter__(self) -> "MCPSession":
        await self.start()
        return self

    async def __aexit__(self, *_) -> None:
        await self.stop()

    # ─────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────
    async def start(self) -> None:
        env = {
            **os.environ,
            "ALPACA_API_KEY":    _cfg.api_key,
            "ALPACA_SECRET_KEY": _cfg.secret_key,
            "ALPACA_BASE_URL":   _cfg.base_url,
        }
        try:
            self._proc = await asyncio.create_subprocess_exec(
                *self.MCP_CMD,
                stdin  = asyncio.subprocess.PIPE,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
                env    = env,
            )
            # Send MCP initialise handshake
            await self._initialise()
            # Start background reader
            self._reader_task = asyncio.create_task(self._read_loop())
            logger.info("Alpaca MCP server started (PID {})", self._proc.pid)
        except FileNotFoundError:
            logger.warning("uvx not found — MCP server unavailable. "
                           "Install with: pip install uv && uv tool install alpaca-mcp-server")
            self._proc = None

    async def stop(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
        if self._proc:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._proc.kill()
            logger.info("Alpaca MCP server stopped")

    @property
    def available(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    # ─────────────────────────────────────────────────────────
    # MCP JSON-RPC protocol
    # ─────────────────────────────────────────────────────────
    async def _initialise(self) -> None:
        """Send MCP initialize request and await InitializeResult."""
        msg = {
            "jsonrpc": "2.0",
            "id":      0,
            "method":  "initialize",
            "params":  {
                "protocolVersion": "2024-11-05",
                "capabilities":    {},
                "clientInfo":      {"name": "OptionAlphaAgent", "version": "1.0.0"},
            },
        }
        await self._send_raw(msg)
        # Give server 2s to respond
        await asyncio.sleep(2.0)

    async def _send_raw(self, msg: Dict) -> None:
        if not self._proc or not self._proc.stdin:
            return
        payload = json.dumps(msg) + "\n"
        self._proc.stdin.write(payload.encode())
        await self._proc.stdin.drain()

    async def _read_loop(self) -> None:
        """Background task — reads JSON-RPC responses from MCP server."""
        if not self._proc or not self._proc.stdout:
            return
        async for line in self._proc.stdout:
            try:
                msg  = json.loads(line.decode().strip())
                req_id = msg.get("id")
                if req_id in self._pending:
                    fut = self._pending.pop(req_id)
                    if not fut.done():
                        fut.set_result(msg)
            except (json.JSONDecodeError, KeyError):
                pass

    # ─────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────
    async def call_tool(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """
        Call an Alpaca MCP tool and return the result.

        Example tools:
          "get_account"      → {} 
          "get_positions"    → {}
          "get_option_chain" → {"symbol": "SPY", "expiration_date": "2025-12-19"}
          "place_order"      → {"symbol": "SPY...", "qty": 1, "side": "sell", ...}
        """
        if not self.available:
            logger.debug("MCP: server unavailable — skipping tool call {}", tool_name)
            return None

        self._req_id += 1
        req_id = self._req_id

        msg = {
            "jsonrpc": "2.0",
            "id":      req_id,
            "method":  "tools/call",
            "params":  {"name": tool_name, "arguments": arguments},
        }

        loop = asyncio.get_event_loop()
        fut  = loop.create_future()
        self._pending[req_id] = fut

        await self._send_raw(msg)

        try:
            response = await asyncio.wait_for(fut, timeout=15.0)
            return response.get("result")
        except asyncio.TimeoutError:
            logger.warning("MCP tool {} timed out", tool_name)
            self._pending.pop(req_id, None)
            return None

    async def get_account_summary(self) -> str:
        """Returns a human-readable account summary via MCP."""
        result = await self.call_tool("get_account", {})
        if result:
            content = result.get("content", [{}])
            if content:
                return str(content[0].get("text", "No account data"))
        return "MCP unavailable"

    async def analyze_portfolio(self) -> str:
        """Returns positions analysis from MCP."""
        result = await self.call_tool("get_positions", {})
        if result:
            content = result.get("content", [{}])
            return str(content[0].get("text", "No positions")) if content else "No positions"
        return "MCP unavailable"

    async def query_option_chain(self, symbol: str) -> str:
        """Query option chain data via MCP."""
        result = await self.call_tool("get_option_chain", {"symbol": symbol})
        if result:
            content = result.get("content", [{}])
            return str(content[0].get("text", "")) if content else ""
        return ""


# ─────────────────────────────────────────────────────────────
# Synchronous wrapper for use in non-async code
# ─────────────────────────────────────────────────────────────

class SyncMCPClient:
    """Synchronous wrapper around MCPSession for use in the agent main loop."""

    def __init__(self):
        self._loop    = asyncio.new_event_loop()
        self._session: Optional[MCPSession] = None

    def start(self) -> None:
        self._session = MCPSession()
        self._loop.run_until_complete(self._session.start())

    def stop(self) -> None:
        if self._session:
            self._loop.run_until_complete(self._session.stop())
        self._loop.close()

    def call_tool(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        if not self._session:
            return None
        return self._loop.run_until_complete(self._session.call_tool(tool_name, arguments))

    def get_portfolio_summary(self) -> str:
        if not self._session:
            return "MCP not started"
        return self._loop.run_until_complete(self._session.analyze_portfolio())

    @property
    def available(self) -> bool:
        return self._session is not None and self._session.available
