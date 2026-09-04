// engine/rust/src/calendar_spread.rs
// OptionAlpha Agent — Rust SIMD Time-Decay Calendar Spread Strategy Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

pub const CONTRACT_MULTIPLIER: f64 = 100.0;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustCalendarProposal {
    #[pyo3(get)]
    pub symbol: String,
    #[pyo3(get)]
    pub strike: f64,
    #[pyo3(get)]
    pub near_dte: i32,
    #[pyo3(get)]
    pub far_dte: i32,
    #[pyo3(get)]
    pub net_debit_dollars: f64,
    #[pyo3(get)]
    pub max_loss_dollars: f64,
    #[pyo3(get)]
    pub confidence: f64,
    #[pyo3(get)]
    pub contract_multiplier: i32,
    #[pyo3(get)]
    pub zero_bridge_status: String,
}

#[pyclass]
pub struct RustCalendarEngine {
    pub near_dte: i32,
    pub far_dte: i32,
}

#[pymethods]
impl RustCalendarEngine {
    #[new]
    pub fn new(near_dte: Option<i32>, far_dte: Option<i32>) -> Self {
        Self {
            near_dte: near_dte.unwrap_or(14),
            far_dte: far_dte.unwrap_or(45),
        }
    }

    /// Evaluates Calendar Spread during term backwardation (Near IV > Far IV)
    pub fn evaluate(
        &self,
        symbol: String,
        spot: f64,
        near_iv: f64,
        far_iv: f64,
        near_bid: f64,
        far_ask: f64,
    ) -> Option<RustCalendarProposal> {
        let term_spread = near_iv - far_iv;
        if term_spread < 0.02 {
            return None; // Requires term backwardation >= 2.0%
        }

        let strike = (spot / 2.5).round() * 2.5;
        let net_debit = far_ask - near_bid;
        if net_debit <= 0.20 {
            return None;
        }

        let net_debit_dollars = net_debit * CONTRACT_MULTIPLIER;
        let max_loss_dollars = net_debit_dollars;
        let confidence = (0.65 + term_spread * 5.0).min(0.95);

        Some(RustCalendarProposal {
            symbol,
            strike,
            near_dte: self.near_dte,
            far_dte: self.far_dte,
            net_debit_dollars,
            max_loss_dollars,
            confidence,
            contract_multiplier: 100,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        })
    }
}
