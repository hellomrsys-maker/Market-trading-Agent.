// engine/rust/src/option_buying_rules_engine.rs
// OptionAlpha Agent — Module J4: Rust SIMD Option Buying Trigger & Milestone Engine

use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
pub struct RustOptionBuyingRulesEngine {}

#[pymethods]
impl RustOptionBuyingRulesEngine {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    pub fn batch_evaluate_milestones(
        &self,
        entries: Vec<f64>,
        currents: Vec<f64>,
        t1s: Vec<f64>,
        t2s: Vec<f64>,
        initial_sls: Vec<f64>,
    ) -> Vec<f64> {
        let mut stops = Vec::with_capacity(entries.len());
        for i in 0..entries.len() {
            let entry = entries[i];
            let cur = currents[i];
            let t1 = t1s[i];
            let t2 = t2s[i];
            let init_sl = initial_sls[i];

            let active_sl = if cur >= t2 {
                t1
            } else if cur >= t1 {
                entry
            } else {
                init_sl
            };
            stops.push(active_sl);
        }
        stops
    }
}
