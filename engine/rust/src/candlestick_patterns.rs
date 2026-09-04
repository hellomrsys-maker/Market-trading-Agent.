// engine/rust/src/candlestick_patterns.rs
// OptionAlpha Agent — Rust SIMD Candlestick & Multi-Bar Reversal Pattern Recognition Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustCandlePatternResult {
    #[pyo3(get)]
    pub pattern: String,
    #[pyo3(get)]
    pub is_bullish: bool,
    #[pyo3(get)]
    pub is_bearish: bool,
    #[pyo3(get)]
    pub confidence: f64,
    #[pyo3(get)]
    pub stop_loss: f64,
}

#[pyclass]
pub struct RustCandleEngine;

#[pymethods]
impl RustCandleEngine {
    #[new]
    pub fn new() -> Self {
        Self
    }

    /// Evaluates multi-bar patterns (Morning Star, Evening Star, Engulfing, Tweezers)
    pub fn evaluate_3_bars(
        &self,
        o1: f64, h1: f64, l1: f64, c1: f64,
        o2: f64, h2: f64, l2: f64, c2: f64,
        o3: f64, h3: f64, l3: f64, c3: f64,
    ) -> Option<RustCandlePatternResult> {
        let b1_bull = c1 > o1;
        let b1_body = (c1 - o1).abs();

        let b2_body = (c2 - o2).abs();
        let b3_bull = c3 > o3;
        let b3_range = (h3 - l3).max(1e-5);
        let b3_lower_wick = if b3_bull { o3 - l3 } else { c3 - l3 };

        // 1. Morning Star (Bullish)
        if !b1_bull && b2_body < b1_body * 0.35 && b3_bull && c3 >= o1 - (b1_body * 0.40) {
            let stop = l1.min(l2).min(l3) - 1.50;
            return Some(RustCandlePatternResult {
                pattern: "BULLISH_MORNING_STAR".to_string(),
                is_bullish: true,
                is_bearish: false,
                confidence: 0.90,
                stop_loss: stop,
            });
        }

        // 2. Evening Star (Bearish)
        if b1_bull && b2_body < b1_body * 0.35 && !b3_bull && c3 <= o1 + (b1_body * 0.40) {
            let stop = h1.max(h2).max(h3) + 1.50;
            return Some(RustCandlePatternResult {
                pattern: "BEARISH_EVENING_STAR".to_string(),
                is_bullish: false,
                is_bearish: true,
                confidence: 0.90,
                stop_loss: stop,
            });
        }

        // 3. Bullish Engulfing
        if !(c2 > o2) && b3_bull && o3 <= c2 && c3 >= o2 {
            let stop = l2.min(l3) - 1.00;
            return Some(RustCandlePatternResult {
                pattern: "BULLISH_ENGULFING".to_string(),
                is_bullish: true,
                is_bearish: false,
                confidence: 0.88,
                stop_loss: stop,
            });
        }

        // 4. Bearish Engulfing
        if (c2 > o2) && !b3_bull && o3 >= c2 && c3 <= o2 {
            let stop = h2.max(h3) + 1.00;
            return Some(RustCandlePatternResult {
                pattern: "BEARISH_ENGULFING".to_string(),
                is_bullish: false,
                is_bearish: true,
                confidence: 0.88,
                stop_loss: stop,
            });
        }

        None
    }
}
