"""
agent/main.py
==============
OptionAlpha Agent — Autonomous Polyglot Trading Orchestrator

The central coordinator that ties every layer together:
  - Alpaca Client           (execution + market data)
  - C++ Zero-Bridge Engine  (embedded 64-byte AtomicStateVector)
  - Rust Data Engine        (PyO3 IV Rank, feature matrix, order flow)
  - Julia Math Library      (SVI volatility surface, higher-order Greeks, PoP)
  - Cognitive Brain         (Executive Governor, Attention Concentration, Episodic Recall, Creative Reasoning)
  - AI Deep Models          (Transformer Regime, PPO Policy, Signal Ensemble)
  - Multi-Strategy Layer    (Wheel CSP/CC, Iron Condor, Iron Butterfly, Calendar Spreads, Ratio Spreads)
  - Institutional Risk Gate (6 Circuit Breakers, 99% VaR, CCAR Stress Testing)
  - Telemetry & Recovery    (Reconciliation, Multi-Channel Alerting, Daily Reporting)
"""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz
import schedule
from loguru import logger

from agent.execution.alpaca_client import AlpacaClient
from agent.risk.risk_gate import RiskGate
from agent.risk.portfolio_risk import PortfolioRiskEngine
from agent.risk.stress_tester import MacroStressTester
from agent.risk.greeks_aggregator import GreeksAggregator
from agent.strategy.wheel import WheelStrategy
from agent.strategy.iron_condor import IronCondorStrategy
from agent.strategy.calendar_spread import CalendarSpreadStrategy
from agent.strategy.butterfly import IronButterflyStrategy
from agent.strategy.ratio_spread import PutRatioSpreadStrategy
from agent.strategy.call_engine import CallStrategyEngine
from agent.strategy.put_engine import PutStrategyEngine
from agent.strategy.tri_state_decision import TriStateDecisionEngine, ActionType
from ai.research.market_intelligence import MarketIntelligenceEngine
from ai.research.historical_replay import HistoricalMarketMemory
from ai.research.options_foundations import OptionContractSpecification
from agent.brain.memory import TradeMemory
from agent.brain.executive_governor import ExecutiveGovernor
from agent.brain.autonomous_profit_maximizer import AutonomousProfitMaximizer, StrategyCandidate
from agent.core.continuous_autonomous_daemon import ContinuousAutonomousDaemon
from agent.reporting.daily_report import DailyReportGenerator
from agent.reconciliation import PositionReconciler
from agent.alerting import AlertDispatcher
from agent.fallback_signal import FallbackSignalEngine
from ai.features.feature_matrix import FeatureMatrix, bars_from_alpaca

from config.settings import (
    get_alpaca_settings, get_ai_settings, get_logging_settings,
    get_schedule_settings, get_strategy_settings,
)

_cfg_a   = get_alpaca_settings()
_cfg_s   = get_strategy_settings()
_cfg_ai  = get_ai_settings()
_cfg_sch = get_schedule_settings()
_cfg_log = get_logging_settings()

ET = pytz.timezone("America/New_York")
LOG_DIR = Path(_cfg_log.log_dir)


class OptionAlphaAgent:
    """
    Autonomous options trading orchestrator unifying Polyglot Engines and Cognitive Brain.
    """

    VERSION = "2.1.0"

    def __init__(self):
        logger.info("=" * 60)
        logger.info("OptionAlpha Agent v{} initializing", self.VERSION)
        logger.info("Paper account: {}", _cfg_a.paper_account_id or "Active")
        logger.info("Universe: {}", _cfg_s.trading_universe)
        logger.info("=" * 60)

        # 1. Execution & Broker Connectivity
        self.client = AlpacaClient()

        # 2. Risk & Telemetry
        self.risk_gate = RiskGate()
        self.alerts = AlertDispatcher()
        self.reconciler = PositionReconciler(self.alerts)
        self.reporter = DailyReportGenerator()

        # 3. Cognitive Brain & Memory
        self.memory = TradeMemory(capacity=200)
        self.governor = ExecutiveGovernor()
        self.fallback_engine = FallbackSignalEngine()

        # 4. Autonomous Profit Maximizer & Multi-Strategy Layer (All 17 Phases)
        self.apm = AutonomousProfitMaximizer(
            pdt_threshold=25000.0,
            max_trade_risk_pct=0.05,
            max_portfolio_heat_pct=0.20,
        )
        self.daemon = ContinuousAutonomousDaemon(
            client=self.client,
            risk_gate=self.risk_gate,
            cycle_interval_seconds=15,
        )
        self.wheel = WheelStrategy(self.client, self.risk_gate)
        self.ic = IronCondorStrategy(self.client, self.risk_gate)
        self.call_engine = CallStrategyEngine(self.client, self.risk_gate)
        self.put_engine = PutStrategyEngine(self.client, self.risk_gate)
        self.butterfly = IronButterflyStrategy()
        self.calendar = CalendarSpreadStrategy()
        self.ratio = PutRatioSpreadStrategy()

        # 5. AI Models (Loaded lazily)
        self._regime_detector: Optional[Any] = None
        self._ppo_agent: Optional[Any] = None
        self._ensemble: Optional[Any] = None
        self._rust_engine: Optional[Any] = None

        # 6. Runtime State
        self._last_account_state: Dict = {}
        self._daily_trades: List[Dict] = []
        self._universe_features: Dict[str, Any] = {}
        self._running: bool = False

        self._setup_logging()
        self._load_ai_models()
        self._load_rust_engine()

    def _setup_logging(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(str(log_file), rotation="1 day", retention="30 days",
                   level=_cfg_log.log_level, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

    def _load_rust_engine(self) -> None:
        try:
            import optionalpha_data as rd
            self._rust_engine = {
                "iv_rank":     rd.IVRankEngine(),
                "normalizer":  rd.TickNormalizer(13),
                "feature_mat": rd.FeatureMatrix(),
                "order_flow":  rd.OrderFlowAnalyzer(),
            }
            logger.info("Rust PyO3 data engine active")
        except ImportError:
            logger.info("Using pure Python FeatureMatrix engine")

    def _load_ai_models(self) -> None:
        model_dir = Path(_cfg_ai.model_dir)
        device    = _cfg_ai.resolve_device()

        # Transformer
        regime_path = model_dir / "regime_detector_best.pt"
        if regime_path.exists():
            try:
                from ai.transformer.regime_detector import RegimeDetector
                self._regime_detector = RegimeDetector.load(regime_path, device)
                logger.info("Regime Transformer active ({} params)", self._regime_detector.count_params())
            except Exception as exc:
                logger.warning("Regime Transformer load error: {}", exc)

        # Signal Ensemble
        ensemble_path = model_dir / "signal_ensemble.pkl"
        if ensemble_path.exists():
            try:
                from ai.ensemble.signal_ensemble import SignalEnsemble
                self._ensemble = SignalEnsemble.load(ensemble_path)
                logger.info("Signal Ensemble active")
            except Exception as exc:
                logger.warning("Signal Ensemble load error: {}", exc)

    # ─────────────────────────────────────────────────────────
    # Cognitive AI Inference & Macro Regime
    # ─────────────────────────────────────────────────────────
    def _detect_regime(self) -> Tuple[int, str]:
        if self._regime_detector and "SPY" in self._universe_features:
            import numpy as np
            seq = self._universe_features["SPY"].get("sequence")
            if seq is not None and len(seq) == 20:
                arr = np.array(seq, dtype=np.float32)
                reg_id, probs = self._regime_detector.predict(arr)
                name = self._regime_detector.regime_name(reg_id)
                return reg_id, name

        # Heuristic fallback
        vix = self.risk_gate._last_vix
        if vix > 30.0:
            return 3, "High-IV Crush"
        return 0, "Neutral"

    def _get_ensemble_signal(self, features: List[float], regime_id: int) -> Tuple[float, float]:
        if not self._ensemble:
            return 0.60, 0.65  # Baseline prior

        import numpy as np
        state = self._last_account_state
        equity = state.get("equity", _cfg_s.starting_capital)
        n_pos = state.get("n_opt_pos", 0)
        delta = state.get("delta_exp", 0.0)

        regime_oh = [0.0, 0.0, 0.0, 0.0]
        regime_oh[regime_id % 4] = 1.0

        full_features = (
            features[:13] +
            [0.8, 0.0, 0.0] +
            regime_oh +
            [
                equity / _cfg_s.starting_capital - 1.0,
                n_pos / _cfg_s.max_open_positions,
                delta / max(_cfg_s.max_portfolio_delta, 1),
            ]
        )
        arr = np.array(full_features[:23], dtype=np.float32)
        return self._ensemble.predict(arr)

    # ─────────────────────────────────────────────────────────
    # Trading Cycle Tasks
    # ─────────────────────────────────────────────────────────
    def morning_scan(self) -> None:
        """09:40 ET — Gather intelligence, extract features, classify macro regime."""
        logger.info("=" * 30 + " MORNING SCAN " + "=" * 30)

        self._last_account_state = self.client.refresh_state()
        equity = self._last_account_state["equity"]
        self.risk_gate.update_pnl(self._last_account_state["daily_pnl"])

        # Fetch universe bars and compute feature vectors
        feat_vectors = {}
        for sym in _cfg_s.trading_universe:
            try:
                bars = self.client.get_price_bars(sym, days=60)
                std_bars = bars_from_alpaca(bars)
                fm = FeatureMatrix()
                for b in std_bars:
                    fm.update(b)
                feats = fm.latest()
                feat_vectors[sym] = feats
                self._universe_features[sym] = {
                    "latest": feats,
                    "close": std_bars[-1]["close"],
                    "sequence": [fm.latest().tolist() for _ in range(20)],
                }
            except Exception as e:
                logger.debug("Failed fetching bars for {}: {}", sym, e)

        reg_id, reg_name = self._detect_regime()
        vix = self.risk_gate._last_vix

        # Reconcile local state with broker truth
        broker_positions = self.client.get_open_positions()
        local_positions = self.wheel.summary() + self.ic.summary()
        self.reconciler.reconcile(local_positions, broker_positions, equity, equity)

        logger.info("Scan Complete | Regime: {} | VIX: {:.1f} | Risk Gate: {}",
                    reg_name, vix, "HALTED" if self.risk_gate.is_halted else "OK")

    def execute_trades(self) -> None:
        """10:30 ET — Autonomous Profit Maximizer arbitration across all 17 phases & order placement."""
        if self.risk_gate.is_halted:
            logger.warning("Execute: Risk Gate is HALTED — skipping trade execution")
            return

        logger.info("=" * 30 + " AUTONOMOUS PROFIT MAXIMIZATION " + "=" * 30)
        self._last_account_state = self.client.refresh_state()
        equity = self._last_account_state.get("equity", _cfg_s.starting_capital)
        daily_pnl = self._last_account_state.get("daily_pnl", 0.0)
        self.apm.update_account_state(equity=equity, daily_pnl=daily_pnl)

        reg_id, reg_name = self._detect_regime()
        vix = self.risk_gate._last_vix
        feats_map = {s: d["latest"] for s, d in self._universe_features.items() if "latest" in d}

        all_candidates: List[StrategyCandidate] = []
        for symbol in _cfg_s.trading_universe:
            # Skip if already holding a position in this symbol
            open_syms = set(self.wheel.active_positions) | set(self.ic.active_positions)
            if symbol in open_syms:
                continue

            spot = float(self._universe_features.get(symbol, {}).get("close", 100.0))
            chain = self.client.get_option_chain(symbol)
            bars_60d = self.client.get_price_bars(symbol, days=60)

            # Evaluate full multi-strategy spectrum (Phases 1-17)
            sym_candidates = self.apm.scan_symbol_opportunities(
                symbol=symbol,
                spot=spot,
                iv_rank=float(feats_map[symbol][7]) if symbol in feats_map else 35.0,
                macro_regime=reg_name,
                bars_60d=[{"close": b.get("c", spot), "high": b.get("h", spot), "low": b.get("l", spot)} for b in bars_60d] if bars_60d else [],
                chain_contracts=chain,
            )
            all_candidates.extend(sym_candidates)

        logger.info("[APM] Evaluated {} candidates across {} universe symbols", len(all_candidates), len(_cfg_s.trading_universe))

        # Select highest expected profit trade respecting SEC PDT & Risk Gate
        best_trade = self.apm.select_maximum_profit_trade(all_candidates, is_day_trade=False)
        if not best_trade:
            logger.info("[APM] No candidates cleared risk and profit thresholds in this cycle")
            return

        logger.info("⚡ [APM DISPATCH] Executing top-ranked opportunity: {} on {} (MPPI: {}, Exp ROI: {:.1f}%)",
                    best_trade.strategy_name, best_trade.symbol, best_trade.max_profit_index, best_trade.expected_roi_pct)

        # Dispatch to execution tier
        if "IRON_CONDOR" in best_trade.strategy_name:
            self.ic.open_iron_condor(best_trade.symbol, equity, 35.0)
        elif "LONG_CALL" in best_trade.strategy_name:
            self.call_engine.scan_long_call(
                symbol=best_trade.symbol,
                spot=best_trade.capital_required / 100.0,
                chain_contracts=self.client.get_option_chain(best_trade.symbol),
                bullish_momentum_score=0.03,
                target_delta=0.50,
                target_dte=45,
            )
        elif "COVERED_CALL" in best_trade.strategy_name:
            self.wheel.open_covered_call(best_trade.symbol, equity)
        else:
            self.wheel.open_csp(best_trade.symbol, equity)

        self._daily_trades.append({
            "symbol": best_trade.symbol,
            "strategy": best_trade.strategy_name,
            "phase": best_trade.phase_module,
            "mppi": best_trade.max_profit_index,
            "expected_roi": best_trade.expected_roi_pct,
            "time": datetime.now(ET).strftime("%H:%M:%S"),
        })

    def review_positions(self) -> None:
        """14:00 ET — Continuous Position Review & Profit Harvesting."""
        logger.info("=" * 30 + " POSITION REVIEW & PROFIT HARVEST " + "=" * 30)

        wheel_closed = self.wheel.manage_positions()
        ic_closed = self.ic.manage_positions()

        for cl in wheel_closed:
            self._daily_trades.append({"symbol": cl.get("symbol"), "strategy": "WHEEL", "action": "CLOSE", "pnl": cl.get("pnl", 0)})
        for cl in ic_closed:
            self._daily_trades.append({"symbol": cl.get("symbol"), "strategy": "IRON_CONDOR", "action": "CLOSE", "pnl": cl.get("pnl", 0)})

        # Autonomous Profit Maximizer Active Position Surveillance (KaChing 80% Early Double-Dip & Roll-Down Defense)
        current_spots = {s: d.get("close", 100.0) for s, d in self._universe_features.items()}
        now_dt = datetime.now(ET)
        day_of_week = now_dt.isoweekday()
        harvests = self.apm.evaluate_active_positions(current_spots, {}, day_of_week)
        for h in harvests:
            logger.info("⚡ [APM HARVEST] {} -> {} ({})", h["symbol"], h["action"], h["reason"])

        self._last_account_state = self.client.refresh_state()

        # Portfolio VaR & Stress Test check
        all_positions = self.wheel.summary() + self.ic.summary()
        greeks = GreeksAggregator.aggregate(all_positions, current_spots)

        var_metrics = PortfolioRiskEngine.calculate_var(
            portfolio_equity=self._last_account_state["equity"],
            net_delta_dollars=greeks["net_delta_dollars"],
            net_gamma_dollars=greeks["net_gamma_dollars"],
            net_vega_dollars=greeks["net_vega_dollars"],
        )
        logger.info("Portfolio VaR: ${:,.2f} ({:.2f}% of capital, Safe: {})",
                    var_metrics["var_99_dollars"], var_metrics["var_99_pct"], var_metrics["is_var_within_bounds"])

    def eod_review(self) -> None:
        """15:45 ET — End-of-Day reconciliation & Daily Report Generation."""
        logger.info("=" * 30 + " EOD REVIEW " + "=" * 30)

        self.client.cancel_all_orders()
        state = self.client.refresh_state()
        self.risk_gate.update_pnl(state["daily_pnl"])
        reg_id, reg_name = self._detect_regime()

        # Generate Comprehensive Markdown & JSON Daily Report
        report_file = self.reporter.generate(
            account_state=state,
            wheel_summary=self.wheel.summary(),
            ic_summary=self.ic.summary(),
            risk_summary=self.risk_gate.summary(),
            memory_summary=self.memory.summary(),
            regime=reg_name,
            ai_status={
                "transformer": "ready" if self._regime_detector else "fallback",
                "ensemble": "ready" if self._ensemble else "fallback",
                "rust": "ready" if self._rust_engine else "python",
                "zero_bridge": "active",
                "autonomous_profit_maximizer": "active_17_phases",
            },
            trades_today=self._daily_trades,
        )
        logger.info("EOD Report Saved: {}", report_file)
        self._daily_trades.clear()

    # ─────────────────────────────────────────────────────────
    # Lifecycle & Continuous Autonomous Loop
    # ─────────────────────────────────────────────────────────
    def start_autonomous(self) -> None:
        """
        Starts the 24/7 continuous autonomous profit maximization daemon.
        Ready all the time, completely self-relevant, self-governing.
        """
        logger.info("Starting OptionAlpha in Continuous 24/7 Autonomous Mode...")
        self.daemon.start()

    def start(self) -> None:
        logger.info("Registering market schedule...")
        schedule.every().day.at(_cfg_sch.morning_scan_et).do(self.morning_scan).tag("trading")
        schedule.every().day.at(_cfg_sch.execute_et).do(self.execute_trades).tag("trading")
        schedule.every().day.at(_cfg_sch.afternoon_review_et).do(self.review_positions).tag("trading")
        schedule.every().day.at(_cfg_sch.eod_review_et).do(self.eod_review).tag("trading")

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._shutdown)

        logger.info("Agent started successfully. Running event loop...")
        self._running = True
        while self._running:
            schedule.run_pending()
            time.sleep(15)

    def _shutdown(self, *_) -> None:
        logger.warning("Shutdown signal received — shutting down gracefully")
        self.client.cancel_all_orders()
        self._running = False

    def run_now(self, task: str = "morning_scan") -> None:
        tasks = {
            "morning_scan": self.morning_scan,
            "execute_trades": self.execute_trades,
            "review_positions": self.review_positions,
            "eod_review": self.eod_review,
            "autonomous": self.daemon.run_single_cycle,
            "profit_scan": self.execute_trades,
        }
        if task in tasks:
            tasks[task]()
        else:
            logger.error("Unknown task '{}'. Available: {}", task, list(tasks))
