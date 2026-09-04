//! Module AU4 (Rust): Agricultural & Energy Seasonality Cycles & Weather Premium Engine.
//! SIMD-optimized evaluation of seasonal tendency indices and old-crop/new-crop spreads.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CommoditySeasonalityState {
    pub base_seasonal_score: f64,
    pub weather_shock_severity: f64,
    pub adjusted_seasonal_score: f64,
    pub old_crop_price: f64,
    pub new_crop_price: f64,
    pub crop_spread_value: f64,
    pub is_inverted_market: u32,
    pub seasonal_regime: u32,
    pub _padding: [u8; 8],
}

impl CommoditySeasonalityState {
    pub fn evaluate(base_score: f64, weather_severity: f64, old_crop: f64, new_crop: f64) -> Self {
        let adj = (base_score + (weather_severity * 0.5)).max(-1.0).min(1.0);
        let spread = old_crop - new_crop;
        let inverted = if spread > 0.0 { 1 } else { 0 };

        let regime = if adj >= 0.5 {
            1
        } else if adj <= -0.5 {
            2
        } else {
            0
        };

        Self {
            base_seasonal_score: base_score,
            weather_shock_severity: weather_severity,
            adjusted_seasonal_score: adj,
            old_crop_price: old_crop,
            new_crop_price: new_crop,
            crop_spread_value: spread,
            is_inverted_market: inverted,
            seasonal_regime: regime,
            _padding: [0u8; 8],
        }
    }
}
