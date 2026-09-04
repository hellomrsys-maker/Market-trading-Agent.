//! Module BD4 (Rust): Multi-Timeframe Harmonic & Geometric Pattern Alignment Governor.
//! SIMD-optimized evaluation of R:R ratios >= 2.0 and HTF trend confluence.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct PatternAlignmentRiskState {
    pub entry_price: f64,
    pub target_price: f64,
    pub stop_loss_price: f64,
    pub reward_points: f64,
    pub risk_points: f64,
    pub risk_to_reward_ratio: f64,
    pub is_rr_approved: u32,
    pub is_htf_aligned: u32,
    pub is_trade_approved: u32,
    pub _padding: [u8; 4],
}

impl PatternAlignmentRiskState {
    pub fn audit(entry: f64, target: f64, stop: f64, htf_dir: i32, pattern_dir: i32) -> Self {
        let reward = (target - entry).abs();
        let risk = (entry - stop).abs();
        let rr = reward / risk.max(1e-4);

        let rr_ok = if rr >= 2.0 { 1 } else { 0 };
        let htf_ok = if htf_dir == pattern_dir || htf_dir == 0 { 1 } else { 0 };
        let approved = if rr_ok == 1 && htf_ok == 1 { 1 } else { 0 };

        Self {
            entry_price: entry,
            target_price: target,
            stop_loss_price: stop,
            reward_points: reward,
            risk_points: risk,
            risk_to_reward_ratio: rr,
            is_rr_approved: rr_ok,
            is_htf_aligned: htf_ok,
            is_trade_approved: approved,
            _padding: [0u8; 4],
        }
    }
}
