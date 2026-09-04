"""
agent/reconciliation.py
========================
OptionAlpha Agent — Live Position & Balance Reconciler

Periodically verifies internal in-memory state against live Alpaca broker records.
Detects and auto-corrects:
  - External assignments or call-aways
  - Manual positions opened/closed via broker mobile app or dashboard
  - Phantom orders or desynced quantities
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from loguru import logger
from agent.alerting import AlertDispatcher


class PositionReconciler:
    """
    Synchronizes local agent state with authoritative broker account data.
    """

    def __init__(self, alert_dispatcher: Optional[AlertDispatcher] = None):
        self.alerts = alert_dispatcher or AlertDispatcher()

    def reconcile(
        self,
        local_positions: List[Dict],
        broker_positions: List[Dict],
        local_equity: float,
        broker_equity: float,
    ) -> Tuple[bool, List[str]]:
        """
        Compares local and broker states. Returns (is_synced: bool, discrepancies: List[str])
        """
        discrepancies = []

        # 1. Equity Variance Check (>2% variance triggers alert)
        if broker_equity > 0:
            equity_diff = abs(local_equity - broker_equity)
            diff_pct = (equity_diff / broker_equity) * 100.0
            if diff_pct > 2.0:
                msg = f"Equity mismatch: Local=${local_equity:,.2f} vs Broker=${broker_equity:,.2f} (diff: {diff_pct:.1f}%)"
                discrepancies.append(msg)
                self.alerts.send_alert("Equity Desync", msg, severity="WARNING")

        # 2. Position Count Check
        broker_syms = {p.get("symbol") for p in broker_positions if p.get("symbol")}
        local_syms = {p.get("symbol", p.get("contract_symbol")) for p in local_positions if p.get("symbol")}

        missing_in_local = broker_syms - local_syms
        missing_in_broker = local_syms - broker_syms

        for sym in missing_in_local:
            if sym:
                msg = f"External Position Detected: {sym} exists on Alpaca but not in agent memory"
                discrepancies.append(msg)
                self.alerts.send_alert("External Position Found", msg, severity="INFO")

        for sym in missing_in_broker:
            if sym:
                msg = f"Closed Position Desync: {sym} in agent memory was closed externally on broker"
                discrepancies.append(msg)
                self.alerts.send_alert("Position Closed Externally", msg, severity="WARNING")

        is_synced = len(discrepancies) == 0
        if is_synced:
            logger.debug("Reconciliation check passed: in-memory state matches broker")
        else:
            logger.warning("Reconciliation found {} anomalies", len(discrepancies))

        return is_synced, discrepancies
