// engine/rust/src/butterfly.rs
// OptionAlpha Agent — Rust SIMD Iron Butterfly (Pinning & High-IV Volatility Crush) Strategy Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

pub const CONTRACT_MULTIPLIER: f64 = 100.0;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustIronButterflyProposal {
    #[pyo3(get)]
    pub symbol: String,
    #[pyo3(get)]
    pub atm_strike: f64,
    #[pyo3(get)]
    pub lower_wing: f64,
    #[pyo3(get)]
    pub upper_wing: f64,
    #[pyo3(get)]
    pub net_credit_dollars: f64,
    #[pyo3(get)]
    pub max_profit_dollars: f64,
    #[pyo3(get)]
    pub max_loss_dollars: f64,
    #[pyo3(get)]
    pub breakeven_lower: f64,
    #[pyo3(get)]
    pub breakeven_upper: f64,
    #[pyo3(get)]
    pub confidence: f64,
    #[pyo3(get)]
    pub contract_multiplier: i32,
    #[pyo3(get)]
    pub zero_bridge_status: String,
}

#[pyclass]
pub struct RustIronButterflyEngine {
    pub wing_width: f64,
    pub target_dte: i32,
}

#[pymethods]
impl RustIronButterflyEngine {
    #[new]
    pub fn new(wing_width: Option<f64>, target_dte: Option<i32>) -> Self {
        Self {
            wing_width: wing_width.unwrap_or(10.0),
            target_dte: target_dte.unwrap_or(30),
        }
    }

    /// Evaluates ATM Iron Butterfly when IV Rank >= 50.0 and mean-reverting pin is expected
    pub fn evaluate(
        &self,
        symbol: String,
        spot: f64,
        iv_rank: f64,
        call_credit: f64,
        put_credit: f64,
    ) -> Option<RustIronButterflyProposal> {
        if iv_rank < 50.0 {
            return None; // Iron Butterflies require rich IV Rank >= 50%
        }

        let atm_strike = (spot / 2.5).round() * 2.5;
        let lower_wing = atm_strike - self.wing_width;
        let upper_wing = atm_strike + self.wing_width;

        let total_credit = call_credit + put_credit;
        let net_credit_dollars = total_credit * CONTRACT_MULTIPLIER;
        let max_loss_dollars = (self.wing_width - total_credit) * CONTRACT_MULTIPLIER;

        if max_loss_dollars <= 0.0 || net_credit_dollars <= 50.0 {
            return None;
        }

        let breakeven_lower = atm_strike - total_credit;
        let breakeven_upper = atm_strike + total_credit;
        let confidence = (0.70 + (iv_rank / 100.0) * 0.25).min(0.95);

        Some(RustIronButterflyProposal {
            symbol,
            atm_strike,
            lower_wing,
            upper_wing,
            net_credit_dollars,
            max_profit_dollars: net_credit_dollars,
            max_loss_dollars,
            breakeven_lower,
            breakeven_upper,
            confidence,
            contract_multiplier: 100,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        })
    }
}
