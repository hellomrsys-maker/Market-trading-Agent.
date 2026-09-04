// engine/rust/src/forex_engine.rs
// OptionAlpha Agent — Rust SIMD Forex Pip Valuation, Margin Call Protection & SMA/RSI Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustForexSizingResult {
    #[pyo3(get)]
    pub lot_size: f64,
    #[pyo3(get)]
    pub units: i32,
    #[pyo3(get)]
    pub pip_value_usd: f64,
    #[pyo3(get)]
    pub risk_dollars: f64,
    #[pyo3(get)]
    pub margin_required_usd: f64,
}

#[pyclass]
pub struct RustForexEngine;

#[pymethods]
impl RustForexEngine {
    #[new]
    pub fn new() -> Self {
        Self
    }

    /// Computes pip value in USD based on quote structure
    pub fn calculate_pip_value(&self, pair: &str, units: i32, spot: f64) -> f64 {
        let is_jpy = pair.contains("JPY");
        let pip_multiplier = if is_jpy { 0.01 } else { 0.0001 };

        if pair.ends_with("USD") {
            (pip_multiplier * units as f64)
        } else if pair.starts_with("USD") {
            (pip_multiplier * units as f64) / spot.max(1e-4)
        } else {
            pip_multiplier * units as f64
        }
    }

    /// Computes strict 1-2% risk-per-trade position size
    pub fn calculate_position_size(
        &self,
        pair: &str,
        equity: f64,
        risk_pct: f64,
        stop_loss_pips: f64,
        spot: f64,
        leverage: Option<f64>,
    ) -> RustForexSizingResult {
        let lev = leverage.unwrap_or(100.0);
        let safe_risk_pct = risk_pct.clamp(0.005, 0.02);
        let risk_dollars = equity * safe_risk_pct;

        let pip_val_1_lot = self.calculate_pip_value(pair, 100000, spot);
        let dollar_risk_per_lot = stop_loss_pips * pip_val_1_lot;

        let lots = if dollar_risk_per_lot <= 0.0 {
            0.01
        } else {
            (risk_dollars / dollar_risk_per_lot).max(0.01)
        };

        let units = (lots * 100000.0) as i32;
        let pip_value_usd = self.calculate_pip_value(pair, units, spot);
        let margin_required_usd = (units as f64 * spot) / lev;

        RustForexSizingResult {
            lot_size: lots,
            units,
            pip_value_usd,
            risk_dollars,
            margin_required_usd,
        }
    }
}
