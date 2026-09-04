//! Module AG4 (Rust): VIX Term Structure, Futures Roll Yield & Volatility ETP Arbitrage Engine.
//! Provides SIMD-optimized evaluation of VIX term slope, roll yield, and VVIX spike alerts.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct VixTermStructureState {
    pub spot_vix: f64,
    pub m1_futures_price: f64,
    pub m2_futures_price: f64,
    pub term_slope: f64,
    pub annualized_roll_yield: f64,
    pub vvix_index: f64,
    pub contango_flag: u32,
    pub tail_risk_spike_flag: u32,
    pub _padding: [u8; 8],
}

impl VixTermStructureState {
    pub fn new(spot_vix: f64, m1: f64, m2: f64, vvix: f64, delta_days: i32) -> Self {
        let slope = m2 - m1;
        let d = delta_days.max(1) as f64;
        let roll_yield = ((m2 - m1) / m1) * (365.0 / d) * 100.0;
        let contango = if slope > 0.15 { 1 } else { 0 };
        let tail_risk = if vvix >= 115.0 { 1 } else { 0 };

        Self {
            spot_vix,
            m1_futures_price: m1,
            m2_futures_price: m2,
            term_slope: slope,
            annualized_roll_yield: roll_yield,
            vvix_index: vvix,
            contango_flag: contango,
            tail_risk_spike_flag: tail_risk,
            _padding: [0u8; 8],
        }
    }
}
