//! Module AW4 (Rust): Volatility Edge Discovery & Realized vs. Implied Mispricing Engine.
//! SIMD-optimized evaluation of IV vs HV spreads, 52-week IV rank percentiles, and mispricing regimes.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct VolatilityEdgeDiscoveryState {
    pub iv_30d: f64,
    pub hv_30d: f64,
    pub vol_spread: f64,
    pub iv_rank_pct: f64,
    pub is_expensive_edge: u32,
    pub is_cheap_edge: u32,
    pub edge_regime_flag: u32,
    pub _padding: [u8; 20],
}

impl VolatilityEdgeDiscoveryState {
    pub fn evaluate(iv: f64, hv: f64, min_iv: f64, max_iv: f64) -> Self {
        let spread = iv - hv;
        let rng = (max_iv - min_iv).max(1.0);
        let rank = (((iv - min_iv) / rng) * 100.0).max(0.0).min(100.0);

        let expensive = if spread >= 4.0 || rank >= 75.0 { 1 } else { 0 };
        let cheap = if spread <= -2.0 || rank <= 25.0 { 1 } else { 0 };

        let regime = if expensive == 1 { 1 } else if cheap == 1 { 2 } else { 0 };

        Self {
            iv_30d: iv,
            hv_30d: hv,
            vol_spread: spread,
            iv_rank_pct: rank,
            is_expensive_edge: expensive,
            is_cheap_edge: cheap,
            edge_regime_flag: regime,
            _padding: [0u8; 20],
        }
    }
}
