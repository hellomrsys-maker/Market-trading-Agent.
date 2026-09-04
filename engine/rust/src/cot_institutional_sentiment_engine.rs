//! Module AM4 (Rust): COT Institutional Positioning & Sentiment Engine.
//! SIMD-optimized evaluation of COT percentile indexes and price/OI volume flow.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CotSentimentState {
    pub current_net_position: f64,
    pub min_net_3yr: f64,
    pub max_net_3yr: f64,
    pub cot_index_pct: f64,
    pub price_change: f64,
    pub open_interest_change: f64,
    pub institutional_bias: u32,
    pub is_extreme_signal: u32,
    pub _padding: [u8; 8],
}

impl CotSentimentState {
    pub fn evaluate(current_net: f64, min_net: f64, max_net: f64, p_change: f64, oi_change: f64) -> Self {
        let rng = (max_net - min_net).max(1.0);
        let idx = ((current_net - min_net) / rng * 100.0).max(0.0).min(100.0);
        let extreme = if idx >= 90.0 || idx <= 10.0 { 1 } else { 0 };

        let bias = if p_change > 0.0 && oi_change > 0.0 {
            1
        } else if p_change > 0.0 && oi_change <= 0.0 {
            2
        } else if p_change < 0.0 && oi_change > 0.0 {
            3
        } else {
            4
        };

        Self {
            current_net_position: current_net,
            min_net_3yr: min_net,
            max_net_3yr: max_net,
            cot_index_pct: idx,
            price_change: p_change,
            open_interest_change: oi_change,
            institutional_bias: bias,
            is_extreme_signal: extreme,
            _padding: [0u8; 8],
        }
    }
}
