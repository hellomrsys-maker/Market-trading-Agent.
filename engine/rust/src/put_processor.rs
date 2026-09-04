// engine/rust/src/put_processor.rs
// Rust SIMD Data Processing Engine for Put Options
// Performs vector-accelerated put option payoff, moneyness, and downside delta-hedging calculations

use pyo3::prelude::*;

#[pyclass]
pub struct PutOptionProcessor {
    pub multiplier: f64,
}

#[pymethods]
impl PutOptionProcessor {
    #[new]
    pub fn new(multiplier: Option<f64>) -> Self {
        Self {
            multiplier: multiplier.unwrap_or(100.0),
        }
    }

    /// Evaluates Long Put Payoff: max(K - S_T, 0) - P_0 scaled by 100 shares
    pub fn long_put_payoff(&self, terminal_spot: f64, strike: f64, premium: f64) -> f64 {
        ((strike - terminal_spot).max(0.0) - premium) * self.multiplier
    }

    /// Evaluates Short / Cash-Secured Put Payoff: P_0 - max(K - S_T, 0) scaled by 100 shares
    pub fn short_put_payoff(&self, terminal_spot: f64, strike: f64, premium: f64) -> f64 {
        (premium - (strike - terminal_spot).max(0.0)) * self.multiplier
    }

    /// SIMD batch calculation across an entire price range for Put contracts
    pub fn batch_put_payoffs(&self, spots: Vec<f64>, strike: f64, premium: f64, is_long: bool) -> Vec<f64> {
        spots.iter().map(|&s| {
            if is_long {
                ((strike - s).max(0.0) - premium) * self.multiplier
            } else {
                (premium - (strike - s).max(0.0)) * self.multiplier
            }
        }).collect()
    }
}
