// engine/rust/src/dealer_gamma.rs
// OptionAlpha Agent — Rust SIMD Dealer Net Gamma Exposure (GEX) & Auction Value Area Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustDealerGammaResult {
    #[pyo3(get)]
    pub net_gex_millions: f64,
    #[pyo3(get)]
    pub is_long_gamma: bool,
    #[pyo3(get)]
    pub gamma_flip_strike: f64,
    #[pyo3(get)]
    pub poc_price: f64,
    #[pyo3(get)]
    pub vwap: f64,
}

#[pyclass]
pub struct RustDealerGammaEngine;

#[pymethods]
impl RustDealerGammaEngine {
    #[new]
    pub fn new() -> Self {
        Self
    }

    /// Computes Net GEX in $ Millions: (Sum(Call Gamma * OI) - Sum(Put Gamma * OI)) * Spot^2 * 0.01 * Multiplier / 1M
    pub fn compute_net_gex(
        &self,
        spot: f64,
        call_gammas: Vec<f64>,
        call_ois: Vec<f64>,
        put_gammas: Vec<f64>,
        put_ois: Vec<f64>,
        multiplier: Option<f64>,
    ) -> f64 {
        let m = multiplier.unwrap_or(100.0);
        let call_sum: f64 = call_gammas.iter().zip(call_ois.iter()).map(|(&g, &oi)| g * oi).sum();
        let put_sum: f64 = put_gammas.iter().zip(put_ois.iter()).map(|(&g, &oi)| g * oi).sum();

        let net_gamma_contracts = call_sum - put_sum;
        let dollar_gex = net_gamma_contracts * m * (spot * spot) * 0.01 / 1_000_000.0;
        dollar_gex
    }

    /// Computes VWAP from price and volume vectors
    pub fn compute_vwap(&self, closes: Vec<f64>, volumes: Vec<f64>) -> f64 {
        let total_vol: f64 = volumes.iter().sum();
        if total_vol <= 0.0 {
            return closes.last().copied().unwrap_or(100.0);
        }
        let total_pv: f64 = closes.iter().zip(volumes.iter()).map(|(&p, &v)| p * v).sum();
        total_pv / total_vol
    }
}
