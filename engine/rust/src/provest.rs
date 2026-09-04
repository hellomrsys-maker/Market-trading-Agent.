// engine/rust/src/provest.rs
// OptionAlpha Agent — Rust SIMD PROVEST Option Trading Calculation Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustPROVESTResult {
    #[pyo3(get)]
    pub rel_vol_rank: i32, // Decile 1 to 10
    #[pyo3(get)]
    pub target_dte: i32,
    #[pyo3(get)]
    pub primary_strategy: String,
    #[pyo3(get)]
    pub is_favorable: bool,
    #[pyo3(get)]
    pub composite_score: f64,
}

#[pyclass]
pub struct RustPROVESTEngine;

#[pymethods]
impl RustPROVESTEngine {
    #[new]
    pub fn new() -> Self {
        Self
    }

    /// Computes 24-month relative volatility ranking across deciles (1–10)
    pub fn compute_relative_vol_rank(&self, mut iv_history: Vec<f64>, current_iv: f64) -> i32 {
        if iv_history.is_empty() {
            return 5;
        }
        iv_history.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
        let count = iv_history.iter().filter(|&&x| x <= current_iv).count();
        let percentile = count as f64 / iv_history.len() as f64;
        let decile = (percentile * 10.0).ceil() as i32;
        decile.clamp(1, 10)
    }

    /// Evaluates optimal strategy mapping based on PROVEST Decile and Directional Bias
    pub fn evaluate_strategy_mapping(
        &self,
        rel_vol_rank: i32,
        is_bullish: bool,
        is_bearish: bool,
        vrp: f64,
    ) -> RustPROVESTResult {
        let (target_dte, primary_strategy) = if is_bullish {
            if rel_vol_rank <= 4 {
                (45, "LONG_CALL_DEEP_ITM")
            } else {
                (30, "BULL_PUT_CREDIT_SPREAD")
            }
        } else if is_bearish {
            if rel_vol_rank <= 4 {
                (45, "LONG_PUT_DEEP_ITM")
            } else {
                (30, "PUT_RATIO_SPREAD_1X2")
            }
        } else {
            // Neutral
            if rel_vol_rank <= 3 {
                (45, "CALENDAR_SPREAD")
            } else if rel_vol_rank >= 7 {
                (30, "IRON_CONDOR")
            } else {
                (30, "WHEEL_CSP")
            }
        };

        let score = (0.50 + vrp * 2.0 + (rel_vol_rank as f64 - 5.0) * 0.04).clamp(0.10, 0.98);
        let is_favorable = score >= 0.55;

        RustPROVESTResult {
            rel_vol_rank,
            target_dte,
            primary_strategy: primary_strategy.to_string(),
            is_favorable,
            composite_score: score,
        }
    }
}
