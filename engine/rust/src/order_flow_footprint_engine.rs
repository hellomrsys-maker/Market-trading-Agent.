// engine/rust/src/order_flow_footprint_engine.rs
// OptionAlpha Agent — Module I4: Rust SIMD Order Flow Footprint & Tick Streamer

use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
pub struct RustOrderFlowFootprintEngine {
    pub cumulative_delta: f64,
    pub cumulative_volume: f64,
}

#[pymethods]
impl RustOrderFlowFootprintEngine {
    #[new]
    pub fn new() -> Self {
        Self {
            cumulative_delta: 0.0,
            cumulative_volume: 0.0,
        }
    }

    pub fn batch_aggregate_deltas(
        &mut self,
        asks: Vec<f64>,
        bids: Vec<f64>,
        prices: Vec<f64>,
    ) -> HashMap<String, f64> {
        let mut bar_ask_sum = 0.0;
        let mut bar_bid_sum = 0.0;
        let mut max_vol = 0.0;
        let mut vpoc = 0.0;

        for i in 0..asks.len() {
            let ask = asks[i];
            let bid = bids[i];
            let level_vol = ask + bid;
            bar_ask_sum += ask;
            bar_bid_sum += bid;

            if level_vol > max_vol {
                max_vol = level_vol;
                vpoc = prices.get(i).cloned().unwrap_or(0.0);
            }
        }

        let delta = bar_ask_sum - bar_bid_sum;
        self.cumulative_delta += delta;
        self.cumulative_volume += bar_ask_sum + bar_bid_sum;

        let mut res = HashMap::new();
        res.insert("bar_delta".to_string(), delta);
        res.insert("cumulative_delta".to_string(), self.cumulative_delta);
        res.insert("vpoc".to_string(), vpoc);
        res.insert(
            "cum_delta_pct".to_string(),
            (self.cumulative_delta / self.cumulative_volume.max(1.0)) * 100.0,
        );
        res
    }
}
