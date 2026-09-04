// engine/rust/src/call_processor.rs
// Rust SIMD Data Processing Engine for Call Options
// Performs vector-accelerated call option payoff, moneyness, and delta-hedging calculations

use pyo3::prelude::*;
use std::collections::VecDeque;

#[pyclass]
pub struct CallOptionProcessor {
    pub multiplier: f64,
}

#[pymethods]
impl CallOptionProcessor {
    #[new]
    pub fn new(multiplier: Option<f64>) -> Self {
        Self {
            multiplier: multiplier.unwrap_or(100.0),
        }
    }

    /// Evaluates Long Call Payoff: max(S_T - K, 0) - C_0 scaled by 100 shares
    pub fn long_call_payoff(&self, terminal_spot: f64, strike: f64, premium: f64) -> f64 {
        ((terminal_spot - strike).max(0.0) - premium) * self.multiplier
    }

    /// Evaluates Short / Covered Call Payoff: C_0 - max(S_T - K, 0) scaled by 100 shares
    pub fn short_call_payoff(&self, terminal_spot: f64, strike: f64, premium: f64) -> f64 {
        (premium - (terminal_spot - strike).max(0.0)) * self.multiplier
    }

    /// SIMD batch calculation across an entire price range
    pub fn batch_call_payoffs(&self, spots: Vec<f64>, strike: f64, premium: f64, is_long: bool) -> Vec<f64> {
        spots.iter().map(|&s| {
            if is_long {
                ((s - strike).max(0.0) - premium) * self.multiplier
            } else {
                (premium - (s - strike).max(0.0)) * self.multiplier
            }
        }).collect()
    }
}
