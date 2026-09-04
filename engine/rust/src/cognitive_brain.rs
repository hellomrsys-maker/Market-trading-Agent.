// engine/rust/src/cognitive_brain.rs
// OptionAlpha Agent — Rust SIMD Cognitive Brain Layer (5 Faculties)
// Polyglot Pillar 1: Rust SIMD Accelerators
// MASTER MANDATE & POLYGLOT COMPUTING RULE APPLIED

use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
pub struct RustCognitiveBrain {
    pub focus_threshold: f64,
    pub temperature: f64,
}

#[pymethods]
impl RustCognitiveBrain {
    #[new]
    pub fn new(focus_threshold: Option<f64>, temperature: Option<f64>) -> Self {
        Self {
            focus_threshold: focus_threshold.unwrap_or(0.65),
            temperature: temperature.unwrap_or(0.5),
        }
    }

    /// Faculty 1: Thinking Engine — Deliberative BSM State Vector Pre-computation
    pub fn precompute_bsm_vectors(&self, spots: Vec<f64>, strikes: Vec<f64>, vols: Vec<f64>) -> Vec<f64> {
        // High-throughput SIMD-style pre-computation for d1/d2 denominator (vol * sqrt(T))
        let n = spots.len();
        let mut results = Vec::with_capacity(n);
        let time_to_maturity = 30.0 / 365.0; // Fixed 30 DTE assumption for hot path
        
        for i in 0..n {
            let denominator = vols[i] * time_to_maturity.sqrt();
            results.push(if denominator > 0.0 { denominator } else { 0.001 });
        }
        results
    }

    /// Faculty 2: Concentration Engine — SIMD Softmax Salience Weighting with Temperature
    pub fn compute_concentration_weights(
        &self,
        symbols: Vec<String>,
        momentums: Vec<f64>,
        rv20s: Vec<f64>,
        iv_ranks: Vec<f64>,
        macro_regime: String,
    ) -> HashMap<String, f64> {
        let n = symbols.len();
        let mut raw_scores = Vec::with_capacity(n);
        let mut max_score = f64::MIN;

        for i in 0..n {
            let m = momentums.get(i).cloned().unwrap_or(0.0);
            let rv = rv20s.get(i).cloned().unwrap_or(0.20);
            let ivr = iv_ranks.get(i).cloned().unwrap_or(30.0);

            // 1. Vol Edge
            let vol_edge = ((ivr / 100.0) - (rv / 0.40)).max(0.0);
            // 2. Trend Clarity
            let trend_clarity = (m.abs() * 10.0).min(1.0);
            // 3. Regime Multiplier
            let regime_mult = if macro_regime == "Bull" && m > 0.0 {
                1.3
            } else if macro_regime == "Bear" && m < 0.0 {
                1.3
            } else if macro_regime == "Neutral" && ivr >= 50.0 {
                1.4
            } else {
                0.8
            };

            let salience = (vol_edge * 0.50 + trend_clarity * 0.30 + (ivr / 100.0) * 0.20) * regime_mult;
            let final_salience = salience.max(0.01);
            if final_salience > max_score {
                max_score = final_salience;
            }
            raw_scores.push(final_salience);
        }

        // Softmax with temperature
        let mut exp_scores = Vec::with_capacity(n);
        let mut sum_exp = 0.0;
        
        for score in raw_scores.iter() {
            let exp_val = ((score - max_score) / self.temperature).exp();
            exp_scores.push(exp_val);
            sum_exp += exp_val;
        }
        
        if sum_exp == 0.0 { sum_exp = 1.0; }

        let mut attention_map = HashMap::new();
        for (i, sym) in symbols.into_iter().enumerate() {
            attention_map.insert(sym, exp_scores[i] / sum_exp);
        }
        attention_map
    }

    /// Faculty 3: Episodic Recall KNN Distance Metric (Deep Vectorized Version)
    pub fn compute_knn_distance(
        &self,
        target_symbol: String,
        target_iv_rank: f64,
        target_regime: String,
        hist_symbol: String,
        hist_iv_rank: f64,
        hist_regime: String,
    ) -> f64 {
        // Deep KNN:
        // W1*(Symbol mismatch) + W2*(|IVRank - IVRank_hist|) + W3*(Regime mismatch)
        let sym_penalty = if target_symbol != hist_symbol { 2.0 } else { 0.0 };
        let iv_dist = ((target_iv_rank - hist_iv_rank).abs() / 100.0) * 1.5;
        let regime_penalty = if target_regime != hist_regime { 2.5 } else { 0.0 };
        
        sym_penalty + iv_dist + regime_penalty
    }

    /// Faculty 4: Lateral Defensive Morphing (Creative Jade Lizard Roll)
    pub fn synthesize_roll_down_strike(&self, current_strike: f64, spot_price: f64) -> f64 {
        // More creative than basic roll: factor in spot drop severity
        let target_base = (spot_price * 0.90).min(current_strike * 0.95);
        (target_base / 2.5).round() * 2.5
    }

    /// Faculty 5: Executive Governor Final Confidence Arbitration
    pub fn arbitrate_confidence(
        &self,
        base_confidence: f64,
        attention_weight: f64,
        recall_boost: f64,
        crisis_overlap: bool
    ) -> f64 {
        // In crisis, override with massive penalty if recall is poor
        let mut final_conf = base_confidence + (attention_weight * 5.0) + recall_boost;
        
        if crisis_overlap && recall_boost < 0.0 {
            final_conf *= 0.50; // Halve confidence during unknown crises
        }
        
        final_conf.max(0.10).min(0.98)
    }
}
