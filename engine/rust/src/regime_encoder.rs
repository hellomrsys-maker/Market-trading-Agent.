// engine/rust/src/regime_encoder.rs
// OptionAlpha Agent — Rust SIMD 13-Feature Vector Tensor Encoder for Regime Transformer
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;
use std::collections::VecDeque;

#[pyclass]
pub struct RustRegimeEncoder {
    pub lookback_window: usize,
    pub n_features: usize,
    buffer: VecDeque<Vec<f64>>,
}

#[pymethods]
impl RustRegimeEncoder {
    #[new]
    pub fn new(lookback: Option<usize>, n_features: Option<usize>) -> Self {
        Self {
            lookback_window: lookback.unwrap_or(20),
            n_features: n_features.unwrap_or(13),
            buffer: VecDeque::new(),
        }
    }

    /// Pushes a 13-dim feature vector and maintains lookback tensor
    pub fn push_feature_vector(&mut self, vec: Vec<f64>) -> bool {
        if vec.len() == self.n_features {
            self.buffer.push_back(vec);
            while self.buffer.len() > self.lookback_window {
                self.buffer.pop_front();
            }
            self.buffer.len() == self.lookback_window
        } else {
            false
        }
    }

    /// Flattens the [20, 13] lookback window into a continuous SIMD tensor buffer for inference
    pub fn get_flattened_tensor(&self) -> Vec<f64> {
        let mut flat = Vec::with_capacity(self.lookback_window * self.n_features);
        for row in self.buffer.iter() {
            flat.extend_from_slice(row);
        }
        flat
    }

    pub fn is_ready(&self) -> bool {
        self.buffer.len() >= self.lookback_window
    }
}
