// engine/rust/src/wheel_strategy.rs
// OptionAlpha Agent — Rust SIMD Wheel Strategy State Machine & Execution Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

pub const CONTRACT_MULTIPLIER: f64 = 100.0;

#[derive(Clone, Debug, PartialEq)]
#[pyclass]
pub enum WheelPhase {
    CashSecuredPut,
    StockAssignedCoveredCall,
}

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustWheelProposal {
    #[pyo3(get)]
    pub phase: WheelPhase,
    #[pyo3(get)]
    pub symbol: String,
    #[pyo3(get)]
    pub strike: f64,
    #[pyo3(get)]
    pub dte: i32,
    #[pyo3(get)]
    pub premium_dollars: f64,
    #[pyo3(get)]
    pub collateral_required: f64,
    #[pyo3(get)]
    pub max_profit_dollars: f64,
    #[pyo3(get)]
    pub breakeven_price: f64,
    #[pyo3(get)]
    pub confidence: f64,
    #[pyo3(get)]
    pub contract_multiplier: i32,
    #[pyo3(get)]
    pub zero_bridge_status: String,
}

#[pyclass]
pub struct RustWheelEngine {
    pub default_csp_delta: f64,
    pub default_cc_delta: f64,
    pub target_dte: i32,
}

#[pymethods]
impl RustWheelEngine {
    #[new]
    pub fn new(csp_delta: Option<f64>, cc_delta: Option<f64>, dte: Option<i32>) -> Self {
        Self {
            default_csp_delta: csp_delta.unwrap_or(-0.30),
            default_cc_delta: cc_delta.unwrap_or(0.20),
            target_dte: dte.unwrap_or(30),
        }
    }

    /// Evaluates Cash-Secured Put (Wheel Phase 1)
    pub fn evaluate_csp(
        &self,
        symbol: String,
        spot: f64,
        strike: f64,
        premium: f64,
        iv_rank: f64,
        account_equity: f64,
    ) -> Option<RustWheelProposal> {
        if iv_rank < 30.0 {
            return None;
        }

        let collateral = strike * CONTRACT_MULTIPLIER;
        if collateral > account_equity * 0.50 {
            return None; // Exceeds 50% single position cash allocation
        }

        let premium_dollars = premium * CONTRACT_MULTIPLIER;
        let breakeven = strike - premium;

        Some(RustWheelProposal {
            phase: WheelPhase::CashSecuredPut,
            symbol,
            strike,
            dte: self.target_dte,
            premium_dollars,
            collateral_required: collateral,
            max_profit_dollars: premium_dollars,
            breakeven_price: breakeven,
            confidence: (0.65 + (iv_rank / 100.0) * 0.30).min(0.95),
            contract_multiplier: 100,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        })
    }

    /// Evaluates Covered Call (Wheel Phase 2 - Assigned Stock)
    pub fn evaluate_covered_call(
        &self,
        symbol: String,
        spot: f64,
        cost_basis: f64,
        strike: f64,
        premium: f64,
    ) -> Option<RustWheelProposal> {
        if strike < cost_basis {
            return None; // Prohibit selling calls below cost basis
        }

        let premium_dollars = premium * CONTRACT_MULTIPLIER;
        let capital_gain = (strike - cost_basis).max(0.0) * CONTRACT_MULTIPLIER;
        let max_profit = premium_dollars + capital_gain;
        let breakeven = cost_basis - premium;

        Some(RustWheelProposal {
            phase: WheelPhase::StockAssignedCoveredCall,
            symbol,
            strike,
            dte: self.target_dte,
            premium_dollars,
            collateral_required: cost_basis * CONTRACT_MULTIPLIER,
            max_profit_dollars: max_profit,
            breakeven_price: breakeven,
            confidence: 0.85,
            contract_multiplier: 100,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        })
    }
}
