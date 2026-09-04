"""
web/api.py
===========
OptionAlpha Agent — FastAPI REST Backend

Serves the live dashboard data and static web files.
The agent writes state into a shared in-memory store (AgentStateStore)
which this API reads. No database required — pure in-process.

Endpoints:
    GET  /                   → index.html (dashboard)
    GET  /api/status         → full agent snapshot (JSON)
    GET  /api/positions      → open positions list
    GET  /api/risk           → risk gate state
    GET  /api/history        → equity curve time-series
    GET  /api/ai_status      → AI model status flags
    POST /api/command        → manual agent commands (task triggers)

Static files (index.html, styles.css, app.js) are served from ./web/.
"""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel

# ─────────────────────────────────────────────────────────────
# Shared state store (written by agent, read by API)
# ─────────────────────────────────────────────────────────────

ET = pytz.timezone("America/New_York")
WEB_DIR = Path(__file__).parent      # web/ directory


class EquityPoint(BaseModel):
    timestamp: str
    equity:    float
    daily_pnl: float


class AgentStateStore:
    """
    Thread-safe (GIL-protected) in-memory state store.
    The agent's main loop writes here; the API reads.
    Persistent fallback: reads dashboard_data.json written by EOD hook.
    """

    def __init__(self, log_dir: Path):
        self.log_dir        = Path(log_dir)
        self._equity:       float = 100_000.0
        self._daily_pnl:    float = 0.0
        self._n_positions:  int   = 0
        self._delta_exp:    float = 0.0
        self._regime:       str   = "Neutral"
        self._regime_id:    int   = 0
        self._regime_probs: List[float] = [1.0, 0.0, 0.0, 0.0]
        self._halted:       bool  = False
        self._halt_reason:  str   = ""
        self._vix:          float = 15.0
        self._wheel_pos:    List[Dict] = []
        self._ic_pos:       List[Dict] = []
        self._risk_summary: Dict  = {}
        self._ai_status:    Dict  = {
            "ppo": "loading", "regime": "loading", "ensemble": "loading",
            "rust": "loading", "cpp": "loading", "julia": "loading",
        }
        self._equity_history: Deque[EquityPoint] = deque(maxlen=500)
        self._last_updated:   float = 0.0

        # Attempt to load persisted data from disk
        self._load_from_disk()

    def update(
        self,
        equity:      float,
        daily_pnl:   float,
        n_positions: int,
        delta_exp:   float,
        regime:      str,
        regime_id:   int,
        halted:      bool,
        vix:         float,
        wheel_pos:   List[Dict],
        ic_pos:      List[Dict],
        risk_summary:Dict,
        ai_status:   Dict,
    ) -> None:
        """Called by agent.main each trading cycle."""
        self._equity        = equity
        self._daily_pnl     = daily_pnl
        self._n_positions   = n_positions
        self._delta_exp     = delta_exp
        self._regime        = regime
        self._regime_id     = regime_id
        self._halted        = halted
        self._vix           = vix
        self._wheel_pos     = wheel_pos
        self._ic_pos        = ic_pos
        self._risk_summary  = risk_summary
        self._ai_status     = ai_status
        self._last_updated  = time.time()

        ts = datetime.now(ET).isoformat()
        self._equity_history.append(EquityPoint(timestamp=ts, equity=equity, daily_pnl=daily_pnl))

    def snapshot(self) -> Dict[str, Any]:
        return {
            "timestamp":    datetime.now(ET).isoformat(),
            "equity":       self._equity,
            "daily_pnl":    self._daily_pnl,
            "n_positions":  self._n_positions,
            "delta_exp":    self._delta_exp,
            "regime":       self._regime,
            "regime_id":    self._regime_id,
            "halted":       self._halted,
            "halt_reason":  self._halt_reason,
            "vix":          self._vix,
            "wheel_pos":    self._wheel_pos,
            "ic_pos":       self._ic_pos,
            "risk":         self._risk_summary,
            "ai_status":    self._ai_status,
            "data_age_s":   time.time() - self._last_updated if self._last_updated else 9999,
        }

    def set_ai_status(self, component: str, status: str) -> None:
        """status: 'ready' | 'loading' | 'offline'"""
        self._ai_status[component] = status

    def _load_from_disk(self) -> None:
        """Bootstrap state from the last persisted JSON snapshot."""
        snap_file = self.log_dir / "dashboard_data.json"
        if not snap_file.exists():
            return
        try:
            data = json.loads(snap_file.read_text())
            if isinstance(data, list) and data:
                last = data[-1]
                self._equity      = last.get("equity",      100_000.0)
                self._daily_pnl   = last.get("daily_pnl",   0.0)
                self._n_positions = last.get("n_positions",  0)
                self._wheel_pos   = last.get("wheel_pos",    [])
                self._ic_pos      = last.get("ic_pos",       [])
                self._risk_summary= last.get("risk",         {})
                logger.info("Web API: loaded last state from {}", snap_file)
        except Exception as exc:
            logger.warning("Web API: failed to load persisted state: {}", exc)


# ─────────────────────────────────────────────────────────────
# Singleton store — shared with agent via import
# ─────────────────────────────────────────────────────────────

_LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "logs"
state_store = AgentStateStore(_LOG_DIR)


# ─────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "OptionAlpha Agent API",
    description = "Live dashboard and control API for the autonomous options trading agent",
    version     = "1.0.0",
    docs_url    = "/api/docs",
    redoc_url   = None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ─────────────────────────────────────────────────────────────
# API routes
# ─────────────────────────────────────────────────────────────

@app.get("/api/status", summary="Full agent snapshot")
async def get_status() -> JSONResponse:
    """Returns the complete live agent state as JSON."""
    return JSONResponse(content=state_store.snapshot())


@app.get("/api/positions", summary="Open positions")
async def get_positions() -> JSONResponse:
    snap = state_store.snapshot()
    return JSONResponse(content={
        "wheel": snap["wheel_pos"],
        "ic":    snap["ic_pos"],
        "total": len(snap["wheel_pos"]) + len(snap["ic_pos"]),
    })


@app.get("/api/risk", summary="Risk gate state")
async def get_risk() -> JSONResponse:
    return JSONResponse(content=state_store._risk_summary)


@app.get("/api/history", summary="Equity curve time-series")
async def get_history(limit: int = 200) -> JSONResponse:
    history = list(state_store._equity_history)[-limit:]
    return JSONResponse(content=[p.model_dump() for p in history])


@app.get("/api/ai_status", summary="AI model component status")
async def get_ai_status() -> JSONResponse:
    return JSONResponse(content=state_store._ai_status)


@app.get("/api/health", summary="API health check")
async def health() -> JSONResponse:
    age = time.time() - state_store._last_updated if state_store._last_updated else 9999
    healthy = age < 120   # data < 2 min old
    return JSONResponse(
        content={"status": "healthy" if healthy else "stale", "data_age_s": age},
        status_code=200 if healthy else 503,
    )

# ─────────────────────────────────────────────────────────────
# Live trade history endpoint
# ─────────────────────────────────────────────────────────────
@app.get("/api/trade_history", summary="Live trade history (recent trades)")
async def get_trade_history(limit: int = 200) -> JSONResponse:
    """Return recent trades recorded by the agent's TradeMemory.
    The limit parameter caps the number of trades returned (default 200)."""
    try:
        from run_agent import _agent_instance
        if _agent_instance is None:
            # Agent not yet running; return empty list
            return JSONResponse(content=[])
        trades = _agent_instance.memory.recent(limit)
        # Convert dataclass objects to plain dicts, drop internal fields
        data = [asdict(t) for t in trades]
        for d in data:
            d.pop("was_profitable", None)
        return JSONResponse(content=data)
    except ImportError:
        raise HTTPException(status_code=503, detail="Agent module unavailable")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# Live Performance / Win-Rate Analytics endpoint
# ─────────────────────────────────────────────────────────────

@app.get("/api/performance", summary="Live win-rate and profit analytics")
async def get_performance() -> JSONResponse:
    """
    Returns real-time win rate, P&L stats, and per-strategy breakdowns
    computed directly from the agent's TradeMemory (persisted to disk).
    Safe to call even before any trade is closed.
    """
    try:
        from run_agent import _agent_instance
        if _agent_instance is not None:
            mem = _agent_instance.memory
            snap = state_store.snapshot()
            equity = snap.get("equity", 100_000.0)
            starting = 100_000.0
            total_return_pct = round((equity / starting - 1.0) * 100, 4)
            return JSONResponse(content={
                "total_trades":      len(mem),
                "win_rate_pct":      round(mem.win_rate(20) * 100, 2),
                "avg_pnl_pct":       round(mem.avg_pnl_pct(10) * 100, 4),
                "equity":            equity,
                "total_return_pct":  total_return_pct,
                "daily_pnl":         snap.get("daily_pnl", 0.0),
                "strategy_stats":    mem.strategy_stats(),
                "recent_5":          [
                    {
                        "symbol":   r.symbol,
                        "strategy": r.strategy,
                        "pnl":      round(r.pnl, 2),
                        "pnl_pct":  round(r.pnl_pct * 100, 2),
                        "win":      r.was_profitable,
                        "reason":   r.close_reason,
                        "closed":   r.closed_at,
                    }
                    for r in mem.recent(5)
                ],
                "days_since_last_trade": mem.days_since_last_trade(),
            })
    except ImportError:
        pass
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Agent not running — return stub from disk-persisted state_store
    snap = state_store.snapshot()
    equity = snap.get("equity", 100_000.0)
    return JSONResponse(content={
        "total_trades":      0,
        "win_rate_pct":      50.0,
        "avg_pnl_pct":       0.0,
        "equity":            equity,
        "total_return_pct":  round((equity / 100_000.0 - 1.0) * 100, 4),
        "daily_pnl":         snap.get("daily_pnl", 0.0),
        "strategy_stats":    {},
        "recent_5":          [],
        "days_since_last_trade": 999,
    })


@app.get("/api/regime", summary="Detected market regime and AI confidence")
async def get_regime() -> JSONResponse:
    """Returns current macro regime, VIX, and AI model confidence scores."""
    snap = state_store.snapshot()
    return JSONResponse(content={
        "regime":       snap.get("regime", "Neutral"),
        "regime_id":    snap.get("regime_id", 0),
        "vix":          snap.get("vix", 15.0),
        "ai_status":    snap.get("ai_status", {}),
        "halted":       snap.get("halted", False),
        "halt_reason":  snap.get("halt_reason", ""),
        "data_age_s":   snap.get("data_age_s", 9999),
    })


# ─────────────────────────────────────────────────────────────
# Manual command endpoint (POST)
# ─────────────────────────────────────────────────────────────

class CommandRequest(BaseModel):
    command: str   # "morning_scan" | "execute_trades" | "review_positions" | "eod_review"
    args:    Dict  = {}


@app.post("/api/command", summary="Trigger an agent task manually")
async def run_command(req: CommandRequest) -> JSONResponse:
    """
    Trigger agent tasks on-demand. Useful for testing and demos.
    The agent instance must be running in the same process.
    """
    valid = {"morning_scan", "execute_trades", "review_positions", "eod_review"}
    if req.command not in valid:
        raise HTTPException(status_code=400, detail=f"Unknown command. Valid: {valid}")

    try:
        # Import the running agent instance (set by run_agent.py)
        from run_agent import _agent_instance
        if _agent_instance is None:
            raise HTTPException(status_code=503, detail="Agent not running")
        _agent_instance.run_now(req.command)
        return JSONResponse(content={"status": "ok", "command": req.command})
    except ImportError:
        raise HTTPException(status_code=503, detail="Agent module unavailable")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# Static files — serve dashboard
# ─────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_dashboard() -> FileResponse:
    """Serve the main dashboard HTML."""
    index = WEB_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(str(index))


# Mount static assets (CSS, JS) — only if the web directory exists
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# Also serve files at root level for direct <link href="styles.css"> references
for static_file in ["styles.css", "app.js"]:
    _path = WEB_DIR / static_file
    if _path.exists():
        @app.get(f"/{static_file}", include_in_schema=False)
        async def _serve_static(f=_path) -> FileResponse:
            return FileResponse(str(f))
