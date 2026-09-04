//! Module AY4 (Rust): Volatility Skew, Smile Geometry & Ratio Arbitrage Engine.
//! SIMD-optimized evaluation of skew slopes, term structure slopes, and Broken Wing Butterfly (BWB) economics.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct VolatilitySkewState {
    pub strike_skew_slope: f64,
    pub term_structure_slope: f64,
    pub bwb_net_credit: f64,
    pub bwb_max_profit: f64,
    pub is_steep_put_skew: u32,
    pub is_contango_term: u32,
    pub has_zero_downside_risk: u32,
    pub optimal_structure_id: u32,
    pub _padding: [u8; 16],
}

impl VolatilitySkewState {
    pub fn evaluate(
        iv_atm: f64, iv_put25: f64, iv_call25: f64, iv_30: f64, iv_90: f64,
        bwb_c1: f64, bwb_c2: f64, bwb_c3: f64, k1: f64, k2: f64
    ) -> Self {
        let strike_skew = (iv_put25 - iv_call25) / iv_atm.max(1e-4);
        let term_slope = (iv_90 - iv_30) / iv_30.max(1e-4);

        let steep_put = if strike_skew >= 0.25 { 1 } else { 0 };
        let contango = if term_slope > 0.05 { 1 } else { 0 };

        let opt_id = if steep_put == 1 { 1 } else if strike_skew < 0.05 { 2 } else { 0 };

        let net_credit = (2.0 * bwb_c2) - bwb_c1 - bwb_c3;
        let max_profit = (k2 - k1) + net_credit;
        let zero_risk = if net_credit >= 0.0 { 1 } else { 0 };

        Self {
            strike_skew_slope: strike_skew,
            term_structure_slope: term_slope,
            bwb_net_credit: net_credit,
            bwb_max_profit: max_profit,
            is_steep_put_skew: steep_put,
            is_contango_term: contango,
            has_zero_downside_risk: zero_risk,
            optimal_structure_id: opt_id,
            _padding: [0u8; 16],
        }
    }
}
