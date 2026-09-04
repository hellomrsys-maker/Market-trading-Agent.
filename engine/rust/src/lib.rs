/*!
 * engine/rust/src/lib.rs
 * =======================
 * OptionAlpha Agent — Comprehensive Rust SIMD Polyglot Data Processing & Cognitive Engine
 *
 * This module is compiled as a PyO3 extension (.pyd / .so).
 * It provides Python with:
 *
 *  1. `DataPipeline`               — async market data ingestion from Alpaca WebSocket feed
 *  2. `FeatureMatrix`              — zero-copy feature computation (returns NumPy arrays)
 *  3. `IVRankEngine`               — rolling IV-Rank calculator (52-week window)
 *  4. `TickNormalizer`             — normalise raw price/IV ticks into ML-ready tensors
 *  5. `OrderFlowAnalyzer`          — detect unusual options order flow (gamma squeeze signals)
 *  6. `CallOptionProcessor`        — SIMD call option payoff and multiplier scaling
 *  7. `PutOptionProcessor`         — SIMD put option payoff and multiplier scaling
 *  8. `RustTriStateEngine`         — sub-microsecond TriState decision synthesis
 *  9. `RustCognitiveBrain`         — SIMD Softmax concentration & KNN recall distance
 * 10. `RustWheelEngine`            — SIMD Wheel (CSP + Covered Call) lifecycle state machine
 * 11. `RustIronCondorEngine`       — SIMD 4-leg Iron Condor asymmetric wing optimizer
 * 12. `RustRiskGateEngine`         — SIMD 6 synchronized institutional circuit breakers
 * 13. `RustRegimeEncoder`          — SIMD 13-feature tensor encoder for Regime Transformer
 * 14. `RustIronButterflyEngine`    — SIMD Iron Butterfly volatility crush optimizer
 * 15. `RustCalendarEngine`         — SIMD Calendar spread term structure engine
 * 16. `RustRatioSpreadEngine`      — SIMD 1x2 Put Ratio Spread downside skew engine
 * 17. `RustPROVESTEngine`          — SIMD 24-Month Relative Volatility Decile & PROVEST engine
 * 18. `RustCandleEngine`           — SIMD Candlestick (Morning Star, Engulfing, Tweezers) recognizer
 * 19. `RustDealerGammaEngine`      — SIMD Dealer Net GEX & VWAP Equilibrium calculator
 * 20. `RustPsychologicalGovernor`  — SIMD Disciplined Trader Emotional Tilt & Loss Predefinition
 * 21. `RustMarketProfileEngine`    — SIMD Dalton Market Profile Value Area & Open-Drive Classifier
 * 22. `RustForexEngine`            — SIMD Forex Pip Valuation & Margin Call Protection Engine
 */

pub mod call_processor;
pub mod put_processor;
pub mod tri_state;
pub mod cognitive_brain;
pub mod wheel_strategy;
pub mod iron_condor;
pub mod risk_gate;
pub mod regime_encoder;
pub mod butterfly;
pub mod calendar_spread;
pub mod ratio_spread;
pub mod provest;
pub mod candlestick_patterns;
pub mod dealer_gamma;
pub mod psychological_governor;
pub mod market_profile;
pub mod forex_engine;

pub use call_processor::CallOptionProcessor;
pub use put_processor::PutOptionProcessor;
pub use tri_state::{RustTriStateEngine, RustTriStateDecision, RustActionType};
pub use cognitive_brain::RustCognitiveBrain;
pub use wheel_strategy::{RustWheelEngine, RustWheelProposal, WheelPhase};
pub use iron_condor::{RustIronCondorEngine, RustIronCondorProposal};
pub use risk_gate::{RustRiskGateEngine, RustRiskAssessment};
pub use regime_encoder::RustRegimeEncoder;
pub use butterfly::{RustIronButterflyEngine, RustIronButterflyProposal};
pub use calendar_spread::{RustCalendarEngine, RustCalendarProposal};
pub use ratio_spread::{RustRatioSpreadEngine, RustRatioSpreadProposal};
pub use provest::{RustPROVESTEngine, RustPROVESTResult};
pub use candlestick_patterns::{RustCandleEngine, RustCandlePatternResult};
pub use dealer_gamma::{RustDealerGammaEngine, RustDealerGammaResult};
pub use psychological_governor::{RustPsychologicalGovernor, RustPsychologicalResult};
pub use market_profile::{RustMarketProfileEngine, RustMarketProfileResult};
pub use forex_engine::{RustForexEngine, RustForexSizingResult};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyFloat};
use pyo3::exceptions::PyValueError;
use std::collections::{VecDeque, HashMap};
use std::sync::{Arc, Mutex};
use chrono::{DateTime, Utc};

// ─────────────────────────────────────────────────────────────
// IV Rank Calculator
// ─────────────────────────────────────────────────────────────
#[pyclass]
pub struct IVRankEngine {
    windows: HashMap<String, VecDeque<(i64, f64)>>,
    window_secs: i64,
}

#[pymethods]
impl IVRankEngine {
    #[new]
    #[pyo3(signature = (window_days = 252))]
    pub fn new(window_days: u32) -> Self {
        Self {
            windows: HashMap::new(),
            window_secs: (window_days as i64) * 86_400,
        }
    }

    pub fn push(&mut self, symbol: &str, iv: f64, timestamp_secs: i64) -> f64 {
        let window = self.windows.entry(symbol.to_string()).or_default();
        let cutoff = timestamp_secs - self.window_secs;
        while window.front().map_or(false, |&(ts, _)| ts < cutoff) {
            window.pop_front();
        }
        window.push_back((timestamp_secs, iv));

        let (mut hi, mut lo) = (f64::NEG_INFINITY, f64::INFINITY);
        for &(_, v) in window.iter() {
            if v > hi { hi = v; }
            if v < lo { lo = v; }
        }
        if (hi - lo).abs() < 1e-10 { return 50.0; }
        ((iv - lo) / (hi - lo) * 100.0).clamp(0.0, 100.0)
    }

    pub fn current_rank(&self, symbol: &str) -> Option<f64> {
        let window = self.windows.get(symbol)?;
        if window.is_empty() { return None; }
        let iv = window.back()?.1;
        let (mut hi, mut lo) = (f64::NEG_INFINITY, f64::INFINITY);
        for &(_, v) in window.iter() {
            if v > hi { hi = v; }
            if v < lo { lo = v; }
        }
        if (hi - lo).abs() < 1e-10 { return Some(50.0); }
        Some(((iv - lo) / (hi - lo) * 100.0).clamp(0.0, 100.0))
    }

    pub fn symbol_count(&self) -> usize { self.windows.len() }
}

// ─────────────────────────────────────────────────────────────
// Tick Normalizer
// ─────────────────────────────────────────────────────────────
#[pyclass]
pub struct TickNormalizer {
    means: Vec<f64>,
    variances: Vec<f64>,
    counts: Vec<u64>,
    n_features: usize,
}

#[pymethods]
impl TickNormalizer {
    #[new]
    pub fn new(n_features: usize) -> Self {
        Self {
            means:     vec![0.0; n_features],
            variances: vec![1.0; n_features],
            counts:    vec![0u64; n_features],
            n_features,
        }
    }

    pub fn update(&mut self, raw: Vec<f64>) -> PyResult<()> {
        if raw.len() != self.n_features {
            return Err(PyValueError::new_err(format!(
                "Expected {} features, got {}", self.n_features, raw.len()
            )));
        }
        for (i, &x) in raw.iter().enumerate() {
            self.counts[i] += 1;
            let n = self.counts[i] as f64;
            let delta  = x - self.means[i];
            self.means[i] += delta / n;
            let delta2 = x - self.means[i];
            self.variances[i] += (delta * delta2 - self.variances[i]) / n;
        }
        Ok(())
    }

    pub fn normalize(&self, raw: Vec<f64>) -> PyResult<Vec<f64>> {
        if raw.len() != self.n_features {
            return Err(PyValueError::new_err("Feature length mismatch"));
        }
        Ok(raw.iter().enumerate().map(|(i, &x)| {
            let std = self.variances[i].sqrt().max(1e-8);
            (x - self.means[i]) / std
        }).collect())
    }

    pub fn reset(&mut self) {
        self.means     = vec![0.0; self.n_features];
        self.variances = vec![1.0; self.n_features];
        self.counts    = vec![0u64; self.n_features];
    }
}

// ─────────────────────────────────────────────────────────────
// Feature Matrix Builder
// ─────────────────────────────────────────────────────────────
#[derive(Clone)]
struct Bar {
    timestamp: i64,
    open: f64, high: f64, low: f64, close: f64,
    volume: f64, iv: f64, iv_rank: f64,
    delta: f64, gamma: f64, theta: f64, vega: f64,
}

#[pyclass]
pub struct FeatureMatrix {
    bars: HashMap<String, VecDeque<Bar>>,
    max_bars: usize,
}

#[pymethods]
impl FeatureMatrix {
    #[new]
    #[pyo3(signature = (max_bars = 504))]
    pub fn new(max_bars: usize) -> Self {
        Self { bars: HashMap::new(), max_bars }
    }

    pub fn push_bar(
        &mut self, symbol: &str,
        timestamp: i64, open: f64, high: f64, low: f64, close: f64, volume: f64,
        iv: f64, iv_rank: f64, delta: f64, gamma: f64, theta: f64, vega: f64,
    ) {
        let deq = self.bars.entry(symbol.to_string()).or_default();
        deq.push_back(Bar { timestamp, open, high, low, close, volume, iv, iv_rank, delta, gamma, theta, vega });
        while deq.len() > self.max_bars { deq.pop_front(); }
    }

    pub fn features(&self, symbol: &str) -> PyResult<Vec<f64>> {
        let deq = self.bars.get(symbol)
            .ok_or_else(|| PyValueError::new_err(format!("No bars for {symbol}")))?;

        let n = deq.len();
        if n < 21 {
            return Err(PyValueError::new_err("Need at least 21 bars"));
        }
        let bars: Vec<&Bar> = deq.iter().collect();
        let last = bars[n - 1];

        let close_ret = |lag: usize| -> f64 {
            if n <= lag { return 0.0; }
            (last.close / bars[n - 1 - lag].close).ln()
        };

        let sma = |period: usize| -> f64 {
            let slice = &bars[(n.saturating_sub(period))..n];
            slice.iter().map(|b| b.close).sum::<f64>() / slice.len() as f64
        };

        let realised_vol = |period: usize| -> f64 {
            let slice = &bars[(n.saturating_sub(period + 1))..n];
            if slice.len() < 2 { return 0.0; }
            let rets: Vec<f64> = slice.windows(2)
                .map(|w| (w[1].close / w[0].close).ln())
                .collect();
            let mean = rets.iter().sum::<f64>() / rets.len() as f64;
            let var  = rets.iter().map(|r| (r - mean).powi(2)).sum::<f64>() / rets.len() as f64;
            var.sqrt() * (252.0f64).sqrt()
        };

        let avg_greek = |f: fn(&Bar) -> f64, period: usize| -> f64 {
            let slice = &bars[(n.saturating_sub(period))..n];
            slice.iter().map(|b| f(b)).sum::<f64>() / slice.len() as f64
        };

        let vol_ratio = {
            let recent = bars[(n.saturating_sub(5))..n].iter().map(|b| b.volume).sum::<f64>() / 5.0;
            let avg20  = bars[(n.saturating_sub(20))..n].iter().map(|b| b.volume).sum::<f64>() / 20.0;
            if avg20.abs() < 1e-10 { 1.0 } else { recent / avg20 }
        };

        Ok(vec![
            close_ret(1), close_ret(5), close_ret(20),
            last.close / sma(20) - 1.0,
            last.close / sma(50).max(1e-10) - 1.0,
            realised_vol(20),
            last.iv, last.iv_rank,
            avg_greek(|b| b.delta, 5),
            avg_greek(|b| b.gamma, 5),
            avg_greek(|b| b.theta, 5),
            avg_greek(|b| b.vega, 5),
            vol_ratio,
        ])
    }

    pub fn bar_count(&self, symbol: &str) -> usize {
        self.bars.get(symbol).map(|d| d.len()).unwrap_or(0)
    }
}

// ─────────────────────────────────────────────────────────────
// Order Flow Analyser
// ─────────────────────────────────────────────────────────────
#[pyclass]
pub struct OrderFlowAnalyzer {
    call_volumes: HashMap<String, VecDeque<f64>>,
    put_volumes:  HashMap<String, VecDeque<f64>>,
    window: usize,
}

#[pymethods]
impl OrderFlowAnalyzer {
    #[new]
    #[pyo3(signature = (window = 20))]
    pub fn new(window: usize) -> Self {
        Self {
            call_volumes: HashMap::new(),
            put_volumes:  HashMap::new(),
            window,
        }
    }

    pub fn push_volume(&mut self, symbol: &str, call_vol: f64, put_vol: f64) {
        for (map, v) in [(&mut self.call_volumes, call_vol), (&mut self.put_volumes, put_vol)] {
            let d = map.entry(symbol.to_string()).or_default();
            d.push_back(v);
            if d.len() > self.window { d.pop_front(); }
        }
    }

    pub fn put_call_ratio(&self, symbol: &str) -> f64 {
        let sum = |map: &HashMap<String, VecDeque<f64>>| -> f64 {
            map.get(symbol).map(|d| d.iter().sum::<f64>()).unwrap_or(0.0)
        };
        let calls = sum(&self.call_volumes).max(1e-10);
        sum(&self.put_volumes) / calls
    }

    pub fn is_volume_spike(&self, symbol: &str) -> bool {
        let check = |map: &HashMap<String, VecDeque<f64>>| -> bool {
            let d = map.get(symbol)?;
            if d.len() < 5 { return None; }
            let last = *d.back()?;
            let mean: f64 = d.iter().sum::<f64>() / d.len() as f64;
            let std:  f64 = {
                let var = d.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / d.len() as f64;
                var.sqrt()
            };
            Some(last > mean + 3.0 * std)
        };
        check(&self.call_volumes).unwrap_or(false) || check(&self.put_volumes).unwrap_or(false)
    }
}

// ─────────────────────────────────────────────────────────────
// PyO3 Module Registration
// ─────────────────────────────────────────────────────────────
#[pymodule]
fn optionalpha_data(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<IVRankEngine>()?;
    m.add_class::<TickNormalizer>()?;
    m.add_class::<FeatureMatrix>()?;
    m.add_class::<OrderFlowAnalyzer>()?;
    m.add_class::<CallOptionProcessor>()?;
    m.add_class::<PutOptionProcessor>()?;
    m.add_class::<RustTriStateEngine>()?;
    m.add_class::<RustCognitiveBrain>()?;
    m.add_class::<RustWheelEngine>()?;
    m.add_class::<RustIronCondorEngine>()?;
    m.add_class::<RustRiskGateEngine>()?;
    m.add_class::<RustRegimeEncoder>()?;
    m.add_class::<RustIronButterflyEngine>()?;
    m.add_class::<RustCalendarEngine>()?;
    m.add_class::<RustRatioSpreadEngine>()?;
    m.add_class::<RustPROVESTEngine>()?;
    m.add_class::<RustCandleEngine>()?;
    m.add_class::<RustDealerGammaEngine>()?;
    m.add_class::<RustPsychologicalGovernor>()?;
    m.add_class::<RustMarketProfileEngine>()?;
    m.add_class::<RustForexEngine>()?;
    Ok(())
}
