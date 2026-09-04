// engine/rust/src/risk_gate.rs
// OptionAlpha Agent — Rust SIMD 6 Synchronized Institutional Circuit Breakers
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;
use std::collections::HashMap;

pub const CONTRACT_MULTIPLIER: f64 = 100.0;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustRiskAssessment {
    #[pyo3(get)]
    pub is_allowed: bool,
    #[pyo3(get)]
    pub action: String,
    #[pyo3(get)]
    pub reason: String,
    #[pyo3(get)]
    pub adjusted_qty: i32,
    #[pyo3(get)]
    pub zero_bridge_status: String,
}

#[pyclass]
pub struct RustRiskGateEngine {
    pub max_daily_loss_dollars: f64,
    pub vix_circuit_breaker_threshold: f64,
    pub max_portfolio_positions: usize,
    pub max_sector_positions: usize,
    pub max_single_position_pct: f64,
}

#[pymethods]
impl RustRiskGateEngine {
    #[new]
    pub fn new(
        daily_loss: Option<f64>,
        vix_threshold: Option<f64>,
        max_positions: Option<usize>,
        max_sector: Option<usize>,
        max_pos_pct: Option<f64>,
    ) -> Self {
        Self {
            max_daily_loss_dollars: daily_loss.unwrap_or(2000.0),
            vix_circuit_breaker_threshold: vix_threshold.unwrap_or(35.0),
            max_portfolio_positions: max_positions.unwrap_or(6),
            max_sector_positions: max_sector.unwrap_or(3),
            max_single_position_pct: max_pos_pct.unwrap_or(0.20),
        }
    }

    /// Evaluates 6 Synchronized Circuit Breakers
    pub fn evaluate_order(
        &self,
        symbol: String,
        sector: String,
        order_cost_or_collateral: f64,
        account_equity: f64,
        daily_pnl: f64,
        current_vix: f64,
        active_position_count: usize,
        sector_position_count: usize,
        bid_ask_spread: f64,
        is_closing_order: bool,
    ) -> RustRiskAssessment {
        // Closing orders always permitted to reduce risk
        if is_closing_order {
            return RustRiskAssessment {
                is_allowed: true,
                action: "ALLOW_CLOSE".to_string(),
                reason: "Risk-reducing close order permitted unconditionally".to_string(),
                adjusted_qty: 1,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        // Breaker 1: Daily Loss Limit
        if daily_pnl <= -self.max_daily_loss_dollars.abs() {
            return RustRiskAssessment {
                is_allowed: false,
                action: "HALT_DAILY_LOSS".to_string(),
                reason: format!("Daily loss limit breached: ${:.2} <= -${:.2}", daily_pnl, self.max_daily_loss_dollars),
                adjusted_qty: 0,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        // Breaker 2: VIX Hard Circuit Breaker
        if current_vix >= self.vix_circuit_breaker_threshold {
            return RustRiskAssessment {
                is_allowed: false,
                action: "HALT_VIX_SPIKE".to_string(),
                reason: format!("VIX circuit breaker active: {:.1} >= {:.1}", current_vix, self.vix_circuit_breaker_threshold),
                adjusted_qty: 0,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        // Breaker 3: Max Position Capacity
        if active_position_count >= self.max_portfolio_positions {
            return RustRiskAssessment {
                is_allowed: false,
                action: "REJECT_CAPACITY".to_string(),
                reason: format!("Max portfolio positions reached: {}/{}", active_position_count, self.max_portfolio_positions),
                adjusted_qty: 0,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        // Breaker 4: Sector Concentration
        if sector_position_count >= self.max_sector_positions {
            return RustRiskAssessment {
                is_allowed: false,
                action: "REJECT_SECTOR_CONCENTRATION".to_string(),
                reason: format!("Max sector positions reached for {}: {}/{}", sector, sector_position_count, self.max_sector_positions),
                adjusted_qty: 0,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        // Breaker 5: Position Sizing Cap (Max 20% equity notional)
        let max_allowed_capital = account_equity * self.max_single_position_pct;
        if order_cost_or_collateral > max_allowed_capital {
            return RustRiskAssessment {
                is_allowed: false,
                action: "REJECT_POSITION_SIZE".to_string(),
                reason: format!("Position capital ${:.2} exceeds 20% equity cap ${:.2}", order_cost_or_collateral, max_allowed_capital),
                adjusted_qty: 0,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        // Breaker 6: Bid-Ask Spread Liquidity Gate
        if bid_ask_spread > 0.50 {
            return RustRiskAssessment {
                is_allowed: false,
                action: "REJECT_WIDE_SPREAD".to_string(),
                reason: format!("Bid-ask spread ${:.2} exceeds $0.50 liquidity limit", bid_ask_spread),
                adjusted_qty: 0,
                zero_bridge_status: "0_NS_SYNC".to_string(),
            };
        }

        RustRiskAssessment {
            is_allowed: true,
            action: "ALLOW_NEW_POSITION".to_string(),
            reason: "All 6 synchronized circuit breakers passed".to_string(),
            adjusted_qty: 1,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        }
    }
}
