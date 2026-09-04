"""
tests/test_streaming_and_hud.py
===============================
Unit tests for AlpacaStreamListener and TerminalHUD.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.execution.stream_listener import AlpacaStreamListener
from cli.hud_dashboard import TerminalHUD


class TestStreamListener:
    def test_trade_update_parsing(self):
        received = []
        listener = AlpacaStreamListener(on_trade_update=lambda msg: received.append(msg))
        raw = {
            "event": "fill",
            "qty": 1,
            "price": 3.45,
            "order": {"id": "ORD_123", "symbol": "SPY250620P00480000", "side": "sell"},
        }
        res = listener.handle_trade_update_message(raw)
        assert res["event"] == "fill"
        assert res["filled_price"] == 3.45
        assert len(received) == 1

    def test_quote_message_handling(self):
        quotes = []
        listener = AlpacaStreamListener(on_quote_update=lambda sym, b, a: quotes.append((sym, b, a)))
        listener.handle_quote_message("SPY", 499.50, 499.60)
        assert len(quotes) == 1
        assert quotes[0] == ("SPY", 499.50, 499.60)


class TestTerminalHUD:
    def test_hud_rendering(self):
        hud = TerminalHUD()
        frame = hud.render_frame()
        assert "OPTIONALPHA AUTONOMOUS AGENT" in frame
        assert "EQUITY:" in frame
        assert "PORTFOLIO DOLLAR GREEKS" in frame
        assert "CIRCUIT BREAKERS" in frame
