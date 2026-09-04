// engine/rust/src/stop_loss_management_engine.rs
// OptionAlpha Agent — Module K4: Rust SIMD Stop Loss Level Aggregator

use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
pub struct RustStopLossManagementEngine {}

#[pymethods]
impl RustStopLossManagementEngine {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    pub fn batch_check_stop_breaches(
        &self,
        current_prices: Vec<f64>,
        stop_levels: Vec<f64>,
        is_longs: Vec<bool>,
    ) -> Vec<bool> {
        let mut breaches = Vec::with_capacity(current_prices.len());
        for i in 0..current_prices.len() {
            let p = current_prices[i];
            let s = stop_levels[i];
            let is_long = is_longs[i];
            let breached = if is_long { p <= s } else { p >= s };
            breaches.push(breached);
        }
        breaches
    }
}
