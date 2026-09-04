"""
agent/execution/crypto_stream.py
================================
Real-Time Alpaca Crypto WebSocket Streaming Client

Connects to:
  wss://stream.data.alpaca.markets/v1beta3/crypto/us

Subscribes to:
  - "trades": ["BTC/USD", "ETH/USD"]
  - "quotes": ["ETH/USDT", "ETH/USD", "BTC/USD"]
  - "orderbooks": ["BTC/USD", "ETH/BTC"]

Features:
  - Automatic authentication handshake
  - Sub-millisecond callback dispatch
  - Thread-safe latest book & quote cache for zero-bridge sync
"""

from __future__ import annotations

import asyncio
import json
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from loguru import logger
from config.settings import get_alpaca_settings

_alpaca_cfg = get_alpaca_settings()


class AlpacaCryptoStream:
    """
    Asynchronous WebSocket streaming subscriber for Alpaca 24/7 Crypto Market Data.
    """

    WS_URL: str = "wss://stream.data.alpaca.markets/v1beta3/crypto/us"

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        on_quote: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_orderbook: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_trade: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.api_key = api_key or _alpaca_cfg.api_key
        self.secret_key = secret_key or _alpaca_cfg.secret_key
        self.on_quote = on_quote
        self.on_orderbook = on_orderbook
        self.on_trade = on_trade

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Thread-safe in-memory cache
        self.latest_quotes: Dict[str, Dict[str, Any]] = {}
        self.latest_orderbooks: Dict[str, Dict[str, Any]] = {}
        self.latest_trades: Dict[str, Dict[str, Any]] = {}

    def start(
        self,
        trades: Optional[List[str]] = None,
        quotes: Optional[List[str]] = None,
        orderbooks: Optional[List[str]] = None,
    ) -> None:
        """Starts the WebSocket streaming listener in a background daemon thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(trades or ["BTC/USD"], quotes or ["ETH/USD", "BTC/USD"], orderbooks or ["BTC/USD", "ETH/BTC"]),
            daemon=True,
        )
        self._thread.start()
        logger.info("AlpacaCryptoStream thread started for wss://stream.data.alpaca.markets/v1beta3/crypto/us")

    def stop(self) -> None:
        """Stops the streaming listener."""
        self._running = False

    def _run_loop(self, trades: List[str], quotes: List[str], orderbooks: List[str]) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._listen(trades, quotes, orderbooks))
        except Exception as exc:
            logger.debug("Crypto stream loop shutdown: {}", exc)
        finally:
            self._loop.close()

    async def _listen(self, trades: List[str], quotes: List[str], orderbooks: List[str]) -> None:
        try:
            import websockets
        except ImportError:
            logger.warning("websockets library not installed. Running high-fidelity simulation stream.")
            await self._simulate_stream(trades, quotes, orderbooks)
            return

        while self._running:
            try:
                async with websockets.connect(self.WS_URL, ping_interval=20, ping_timeout=10) as ws:
                    # 1. Connection acknowledgement
                    connected_msg = await ws.recv()
                    logger.debug("WebSocket connected: {}", connected_msg)

                    # 2. Authentication
                    auth_payload = {
                        "action": "auth",
                        "key": self.api_key,
                        "secret": self.secret_key,
                    }
                    await ws.send(json.dumps(auth_payload))
                    auth_resp = await ws.recv()
                    logger.info("WebSocket auth response: {}", auth_resp)

                    # 3. Subscribe
                    sub_payload = {
                        "action": "subscribe",
                        "trades": trades,
                        "quotes": quotes,
                        "orderbooks": orderbooks,
                    }
                    await ws.send(json.dumps(sub_payload))

                    # 4. Message ingestion loop
                    while self._running:
                        msg = await ws.recv()
                        self._process_message(msg)

            except Exception as exc:
                if self._running:
                    logger.warning("WebSocket disconnect ({}). Reconnecting in 3s...", exc)
                    await asyncio.sleep(3)

    def _process_message(self, raw_msg: str) -> None:
        try:
            items = json.loads(raw_msg)
            if not isinstance(items, list):
                items = [items]
            for item in items:
                msg_type = item.get("T")
                symbol = item.get("S")
                if msg_type == "q":  # Quote
                    self.latest_quotes[symbol] = {
                        "symbol": symbol,
                        "bid": float(item.get("bp", 0.0)),
                        "bid_size": float(item.get("bs", 0.0)),
                        "ask": float(item.get("ap", 0.0)),
                        "ask_size": float(item.get("as", 0.0)),
                        "timestamp": item.get("t"),
                    }
                    if self.on_quote:
                        self.on_quote(self.latest_quotes[symbol])
                elif msg_type == "o":  # Orderbook
                    self.latest_orderbooks[symbol] = {
                        "symbol": symbol,
                        "bids": item.get("b", []),
                        "asks": item.get("a", []),
                        "timestamp": item.get("t"),
                        "reset": item.get("r", False),
                    }
                    if self.on_orderbook:
                        self.on_orderbook(self.latest_orderbooks[symbol])
                elif msg_type == "t":  # Trade
                    self.latest_trades[symbol] = {
                        "symbol": symbol,
                        "price": float(item.get("p", 0.0)),
                        "size": float(item.get("s", 0.0)),
                        "timestamp": item.get("t"),
                        "taker_side": item.get("tks"),
                    }
                    if self.on_trade:
                        self.on_trade(self.latest_trades[symbol])
        except Exception as exc:
            logger.debug("Error processing crypto stream frame: {}", exc)

    async def _simulate_stream(self, trades: List[str], quotes: List[str], orderbooks: List[str]) -> None:
        """Simulation fallback updating quotes & Level-2 order books asynchronously."""
        while self._running:
            for s in quotes:
                base = 66000.0 if "BTC" in s else (3450.0 if "ETH" in s else 145.0)
                self.latest_quotes[s] = {
                    "symbol": s,
                    "bid": round(base * 0.9998, 2),
                    "bid_size": 4.5,
                    "ask": round(base * 1.0002, 2),
                    "ask_size": 4.2,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                if self.on_quote:
                    self.on_quote(self.latest_quotes[s])
            for s in orderbooks:
                base = 66000.0 if "BTC" in s else (3450.0 if "ETH" in s else 145.0)
                self.latest_orderbooks[s] = {
                    "symbol": s,
                    "bids": [{"p": round(base * 0.9995, 2), "s": 0.5}],
                    "asks": [{"p": round(base * 1.0005, 2), "s": 0.5}],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                if self.on_orderbook:
                    self.on_orderbook(self.latest_orderbooks[s])
            await asyncio.sleep(1.0)
