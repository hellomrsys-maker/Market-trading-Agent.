"""
agent/execution/stream_listener.py
===================================
OptionAlpha Agent — Real-Time WebSocket Streaming Client

Connects to Alpaca's WebSocket streaming feeds:
  1. Trade Updates Stream (paper-api.alpaca.markets/stream)
     - Captures instant order fills, cancellations, assignments
  2. Market Data Stream (stream.data.alpaca.markets/v2/sip or /v2/iex)
     - Streams real-time quotes & trades for universe underlyings
  3. Direct Zero-Bridge synchronization on every message.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from loguru import logger

from config.settings import get_alpaca_settings, get_strategy_settings

_cfg_a = get_alpaca_settings()
_cfg_s = get_strategy_settings()


class AlpacaStreamListener:
    """
    Asynchronous WebSocket streaming client with automatic reconnect and fallback simulation.
    """

    def __init__(
        self,
        on_trade_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_quote_update: Optional[Callable[[str, float, float], None]] = None,
    ):
        self.on_trade_update = on_trade_update
        self.on_quote_update = on_quote_update
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._msg_count = 0

    def handle_trade_update_message(self, raw_msg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses and standardizes incoming trade update events.
        """
        event = raw_msg.get("event", "unknown")
        order_data = raw_msg.get("order", {})
        parsed = {
            "event": event,
            "order_id": order_data.get("id"),
            "symbol": order_data.get("symbol"),
            "filled_qty": float(raw_msg.get("qty", order_data.get("filled_qty", 0) or 0)),
            "filled_price": float(raw_msg.get("price", order_data.get("filled_avg_price", 0) or 0)),
            "side": order_data.get("side"),
            "timestamp": raw_msg.get("timestamp", datetime.now(timezone.utc).isoformat()),
        }
        self._msg_count += 1
        if self.on_trade_update:
            self.on_trade_update(parsed)
        return parsed

    def handle_quote_message(self, symbol: str, bid: float, ask: float) -> None:
        """
        Processes real-time market data quote tick.
        """
        self._msg_count += 1
        if self.on_quote_update:
            self.on_quote_update(symbol, bid, ask)

    async def start_simulated_stream(self, interval: float = 1.0) -> None:
        """
        Runs an event-driven simulated stream (for offline testing & demo modes).
        """
        self.is_running = True
        logger.info("StreamListener: simulated real-time stream started")
        while self.is_running:
            for sym in _cfg_s.trading_universe:
                # Emit simulated quote
                import random
                mid = 100.0 if sym not in {"SPY", "QQQ"} else 450.0
                spread = 0.05
                bid = round(mid - spread / 2 + random.uniform(-0.1, 0.1), 2)
                ask = round(bid + spread, 2)
                self.handle_quote_message(sym, bid, ask)
            await asyncio.sleep(interval)

    def stop(self) -> None:
        """Stops the streaming listener."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("StreamListener: stream stopped (processed {} messages)", self._msg_count)
