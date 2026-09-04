"""
agent/reporting/daily_report.py
================================
OptionAlpha Agent — Daily P&L Report Generator

Called by the EOD task (15:45 ET) each trading day.
Writes two output files:
  data/logs/reports/YYYY-MM-DD.md    — human-readable Markdown report
  data/logs/reports/YYYY-MM-DD.json  — machine-readable JSON for analytics

Report sections:
  1. Account Summary       — equity, P&L, returns since inception
  2. Trade Activity        — trades opened/closed today
  3. Active Positions      — all open Wheel + IC positions
  4. Risk Snapshot         — circuit breaker state, Greeks exposure
  5. AI Brain Stats        — regime detected, ensemble confidence
  6. Memory Stats          — win rate, strategy performance
  7. Cumulative Stats      — total trades, total P&L, Sharpe (rolling)
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

REPORT_DIR = Path("data/logs/reports")
HISTORY_FILE = Path("data/logs/dashboard_data.json")
STARTING_CAPITAL = 100_000.0


class DailyReportGenerator:
    """
    Generates end-of-day P&L and activity reports.
    Reads live state from the agent components passed at construction.
    """

    def __init__(self):
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────
    # Main entry point
    # ─────────────────────────────────────────────────────────
    def generate(
        self,
        account_state:  Dict[str, Any],
        wheel_summary:  List[Dict],
        ic_summary:     List[Dict],
        risk_summary:   Dict[str, Any],
        memory_summary: Dict[str, Any],
        regime:         str,
        ai_status:      Dict[str, str],
        trades_today:   Optional[List[Dict]] = None,
    ) -> Path:
        """
        Build and save the daily report. Returns path to the Markdown file.
        """
        today     = date.today()
        report_md = REPORT_DIR / f"{today}.md"
        report_js = REPORT_DIR / f"{today}.json"
        trades_today = trades_today or []

        equity     = account_state.get("equity",    STARTING_CAPITAL)
        daily_pnl  = account_state.get("daily_pnl", 0.0)
        total_ret  = (equity / STARTING_CAPITAL - 1.0) * 100
        n_pos      = account_state.get("n_opt_pos",  0)

        # ── JSON payload ─────────────────────────────────────
        payload = {
            "date":           str(today),
            "timestamp":      datetime.now().isoformat(),
            "account":        account_state,
            "daily_pnl":      daily_pnl,
            "total_return_pct": round(total_ret, 3),
            "n_positions":    n_pos,
            "wheel_positions":wheel_summary,
            "ic_positions":   ic_summary,
            "risk":           risk_summary,
            "memory":         memory_summary,
            "regime":         regime,
            "ai_status":      ai_status,
            "trades_today":   trades_today,
            "cumulative_stats":self._cumulative_stats(equity, daily_pnl),
        }
        report_js.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        # ── Markdown report ───────────────────────────────────
        md = self._build_markdown(payload)
        report_md.write_text(md, encoding="utf-8")

        logger.info("Daily report saved -> {}", report_md)
        self._append_to_history(payload)

        # Export live dashboard state for GitHub Pages and local UI
        dashboard_payload = {
            "equity": equity,
            "starting_capital": STARTING_CAPITAL,
            "daily_pnl": daily_pnl,
            "daily_pnl_pct": round(daily_pnl / STARTING_CAPITAL, 6) if STARTING_CAPITAL else 0.0,
            "total_return_pct": round(total_ret, 3),
            "n_positions": n_pos,
            "delta_exp": account_state.get("delta_exp", 0.0),
            "regime": regime,
            "regime_id": 0,
            "regime_probs": [0.70, 0.15, 0.10, 0.05],
            "halted": risk_summary.get("halted", False) if isinstance(risk_summary, dict) else False,
            "vix": 15.0,
            "wheel_pos": wheel_summary,
            "ic_pos": ic_summary,
            "risk": {
                "daily_pnl": daily_pnl,
                "daily_loss_limit": 2000.0,
                "position_count": n_pos,
                "max_positions": 10,
                "delta_exp": account_state.get("delta_exp", 0.0),
                "halted": False,
            },
            "ai_status": ai_status,
            "trades_today": trades_today,
            "last_updated": datetime.now().isoformat(),
        }
        for target in [Path("docs/dashboard_data.json"), Path("web/dashboard_data.json")]:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(dashboard_payload, indent=2), encoding="utf-8")
            except Exception as e:
                logger.debug("Could not write {}: {}", target, e)

        return report_md

    # ─────────────────────────────────────────────────────────
    # Markdown builder
    # ─────────────────────────────────────────────────────────
    def _build_markdown(self, d: Dict) -> str:
        today     = d["date"]
        equity    = d["account"].get("equity", STARTING_CAPITAL)
        daily_pnl = d["daily_pnl"]
        total_ret = d["total_return_pct"]
        pnl_sign  = "+" if daily_pnl >= 0 else ""
        ret_sign  = "+" if total_ret >= 0 else ""
        regime    = d["regime"]
        cum       = d["cumulative_stats"]

        lines: List[str] = []

        # ── Header ───────────────────────────────────────────
        lines += [
            f"# OptionAlpha Agent — Daily Report",
            f"**Date:** {today}  |  **Regime:** {regime}  |  **Paper Trading**",
            "",
            "---",
            "",
        ]

        # ── 1. Account Summary ────────────────────────────────
        lines += [
            "## 1. Account Summary",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Portfolio Equity | **${equity:,.2f}** |",
            f"| Daily P&L | **{pnl_sign}${daily_pnl:,.2f}** |",
            f"| Total Return | **{ret_sign}{total_ret:.2f}%** |",
            f"| Starting Capital | ${STARTING_CAPITAL:,.0f} |",
            f"| Open Positions | {d['n_positions']} |",
            "",
        ]

        # ── 2. Trade Activity ─────────────────────────────────
        trades = d.get("trades_today", [])
        lines += ["## 2. Trade Activity Today", ""]
        if trades:
            lines += [
                "| Symbol | Strategy | Action | Strike | Premium | P&L |",
                "|---|---|---|---|---|---|",
            ]
            for t in trades:
                pnl_s = f"${t.get('pnl', 0):+,.2f}" if "pnl" in t else "—"
                lines.append(
                    f"| {t.get('symbol','—')} | {t.get('strategy','—')} | "
                    f"{t.get('action','—')} | {t.get('strike','—')} | "
                    f"${t.get('premium', 0):,.2f} | {pnl_s} |"
                )
            lines.append("")
        else:
            lines += ["> No trades executed today.", ""]

        # ── 3. Active Positions ───────────────────────────────
        lines += ["## 3. Active Positions", ""]
        wheel = d.get("wheel_positions", [])
        ic    = d.get("ic_positions", [])

        if wheel:
            lines += ["### Wheel Strategy", "",
                      "| Symbol | Stage | Strike | Expiry | DTE | Premium |",
                      "|---|---|---|---|---|---|"]
            for p in wheel:
                lines.append(
                    f"| {p.get('symbol','—')} | {p.get('stage','—')} | "
                    f"${p.get('strike',0):,.0f} | {p.get('expiry','—')} | "
                    f"{p.get('dte','—')}d | ${p.get('premium',0):,.2f} |"
                )
            lines.append("")

        if ic:
            lines += ["### Iron Condors", "",
                      "| Symbol | DTE | Credit | Max Loss | Wing | PoP Range |",
                      "|---|---|---|---|---|---|"]
            for p in ic:
                lines.append(
                    f"| {p.get('symbol','—')} | {p.get('dte','—')}d | "
                    f"${p.get('credit',0):,.2f} | ${p.get('max_loss',0):,.2f} | "
                    f"${p.get('wing_width',0):.0f} | "
                    f"[{p.get('be_lower',0):.0f} – {p.get('be_upper',0):.0f}] |"
                )
            lines.append("")

        if not wheel and not ic:
            lines += ["> No open positions.", ""]

        # ── 4. Risk Snapshot ──────────────────────────────────
        risk  = d.get("risk", {})
        lines += [
            "## 4. Risk Snapshot",
            "",
            f"| Check | Status |",
            f"|---|---|",
            f"| Circuit Breaker | {'🔴 ACTIVE' if risk.get('halted') else '🟢 OFF'} |",
            f"| Daily P&L | ${risk.get('daily_pnl', 0):+,.0f} / limit -${risk.get('daily_loss_limit', 2000):,.0f} |",
            f"| Open Positions | {risk.get('position_count', 0)} / {risk.get('max_positions', 10)} |",
            f"| VIX Estimate | {risk.get('vix', 0):.1f} (threshold: {risk.get('vix_threshold', 35):.0f}) |",
            "",
        ]

        # ── 5. AI Brain Stats ─────────────────────────────────
        ai = d.get("ai_status", {})
        lines += [
            "## 5. AI Brain Status",
            "",
            f"| Component | Status |",
            f"|---|---|",
        ]
        for comp, status in ai.items():
            icon = "✅" if status == "ready" else "⏳" if status == "loading" else "❌"
            lines.append(f"| {comp} | {icon} {status} |")
        lines += ["", f"**Detected Regime:** {regime}", ""]

        # ── 6. Memory Stats ───────────────────────────────────
        mem   = d.get("memory", {})
        lines += [
            "## 6. Trade Memory Stats",
            "",
            f"- **Total trades recorded:** {mem.get('total_trades', 0)}",
            f"- **Win rate (last 20):** {mem.get('win_rate_20', 0.5):.1%}",
            f"- **Avg P&L % (last 10):** {mem.get('avg_pnl_pct_10', 0):.2%}",
            "",
        ]
        strat_stats = mem.get("strategy_stats", {})
        if strat_stats:
            lines += ["### By Strategy", "",
                      "| Strategy | Trades | Win Rate | Avg P&L% |",
                      "|---|---|---|---|"]
            for strat, s in strat_stats.items():
                lines.append(
                    f"| {strat} | {s.get('count',0)} | "
                    f"{s.get('win_rate',0):.1%} | {s.get('avg_pnl_pct',0):.2%} |"
                )
            lines.append("")

        # ── 7. Cumulative Stats ───────────────────────────────
        lines += [
            "## 7. Cumulative Performance",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Trading Days | {cum.get('trading_days', 0)} |",
            f"| Cumulative P&L | ${cum.get('cumulative_pnl', 0):+,.2f} |",
            f"| Max Drawdown | {cum.get('max_drawdown_pct', 0):.2f}% |",
            f"| Sharpe (rolling) | {cum.get('sharpe', 0):.3f} |",
            f"| Winning Days | {cum.get('winning_days', 0)} |",
            "",
            "---",
            f"*Generated by OptionAlpha Agent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}*",
            "*Paper trading — no real capital at risk*",
        ]

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────
    # Cumulative stats from history
    # ─────────────────────────────────────────────────────────
    def _cumulative_stats(self, current_equity: float, today_pnl: float) -> Dict:
        """Compute rolling stats from the persisted equity history."""
        history = self._load_history()
        if not history:
            return {
                "trading_days": 1,
                "cumulative_pnl": today_pnl,
                "max_drawdown_pct": 0.0,
                "sharpe": 0.0,
                "winning_days": 1 if today_pnl > 0 else 0,
            }

        daily_pnls = [h.get("daily_pnl", 0.0) for h in history] + [today_pnl]
        equities   = [h.get("equity", STARTING_CAPITAL) for h in history] + [current_equity]

        # Max drawdown
        peak   = STARTING_CAPITAL
        max_dd = 0.0
        for eq in equities:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > max_dd:
                max_dd = dd

        # Sharpe (annualised, risk-free = 5%)
        import numpy as np
        returns = np.diff(equities) / np.array(equities[:-1]) if len(equities) > 1 else np.array([0.0])
        rf_daily = 0.05 / 252
        excess   = returns - rf_daily
        sharpe   = float(excess.mean() / (excess.std() + 1e-8) * math.sqrt(252)) if len(excess) > 1 else 0.0

        return {
            "trading_days":     len(daily_pnls),
            "cumulative_pnl":   round(current_equity - STARTING_CAPITAL, 2),
            "max_drawdown_pct": round(max_dd, 3),
            "sharpe":           round(sharpe, 4),
            "winning_days":     sum(1 for p in daily_pnls if p > 0),
        }

    # ─────────────────────────────────────────────────────────
    # History helpers
    # ─────────────────────────────────────────────────────────
    def _load_history(self) -> List[Dict]:
        if not HISTORY_FILE.exists():
            return []
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _append_to_history(self, payload: Dict) -> None:
        history = self._load_history()
        # Store minimal snapshot (avoid bloating the file)
        history.append({
            "date":      payload["date"],
            "equity":    payload["account"].get("equity", STARTING_CAPITAL),
            "daily_pnl": payload["daily_pnl"],
            "n_positions":payload["n_positions"],
            "regime":    payload["regime"],
        })
        # Keep max 504 entries (~2 years)
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(history[-504:], indent=2), encoding="utf-8")
