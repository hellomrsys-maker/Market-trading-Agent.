// engine/rust/src/ratio_spread.rs
// OptionAlpha Agent — Rust SIMD Put Ratio Spread (1x2) Zero-Cost Volatility Capture Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

pub const CONTRACT_MULTIPLIER: f64 = 100.0;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustRatioSpreadProposal {
    #[pyo3(get)]
    pub symbol: String,
    #[pyo3(get)]
    pub long_strike: f64,
    #[pyo3(get)]
    pub short_strike: f64,
    #[pyo3(get)]
    pub net_credit_or_debit_dollars: f64,
    #[pyo3(get)]
    pub max_profit_dollars: f64,
    #[pyo3(get)]
    pub breakeven_lower: f64,
    #[pyo3(get)]
    pub dte: i32,
    #[pyo3(get)]
    pub confidence: f64,
    #[pyo3(get)]
    pub contract_multiplier: i32,
    #[pyo3(get)]
    pub zero_bridge_status: String,
}

#[pyclass]
pub struct RustRatioSpreadEngine {
    pub target_dte: i32,
}

#[pymethods]
impl RustRatioSpreadEngine {
    #[new]
    pub fn new(target_dte: Option<i32>) -> Self {
        Self {
            target_dte: target_dte.unwrap_or(45),
        }
    }

    /// Evaluates 1x2 Put Ratio Spread (Buy 1 ATM Put + Sell 2 OTM Puts)
    pub fn evaluate(
        &self,
        symbol: String,
        spot: f64,
        put_skew_25d: f64,
        long_put_ask: f64,
        short_put_bid: f64,
    ) -> Option<RustRatioSpreadProposal> {
        if put_skew_25d < 1.35 {
            return None; // Requires steep put skew >= 1.35
        }

        let long_strike = (spot / 2.5).round() * 2.5;
        let short_strike = (spot * 0.94 / 2.5).round() * 2.5;

        // 1 Long Put @ Ask, 2 Short Puts @ Bid
        let net_cash = (2.0 * short_put_bid) - long_put_ask;
        let net_cash_dollars = net_cash * CONTRACT_MULTIPLIER;

        let strike_spread = long_strike - short_strike;
        let max_profit_dollars = (strike_spread + net_cash) * CONTRACT_MULTIPLIER;
        let breakeven_lower = short_strike - strike_spread - net_cash;

        let confidence = (0.70 + (put_skew_25d - 1.0) * 0.40).min(0.95);

        Some(RustRatioSpreadProposal {
            symbol,
            long_strike,
            short_strike,
            net_credit_or_debit_dollars: net_cash_dollars,
            max_profit_dollars,
            breakeven_lower,
            dte: self.target_dte,
            confidence,
            contract_multiplier: 100,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        })
    }
}
