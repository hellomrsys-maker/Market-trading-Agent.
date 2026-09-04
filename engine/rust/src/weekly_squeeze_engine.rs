// engine/rust/src/weekly_squeeze_engine.rs
// OptionAlpha Agent — Module Q4: Rust Weekly Squeeze & Heikin Ashi Engine

#[derive(Debug, Clone, Copy)]
pub struct HeikinAshiBar {
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
    pub is_strong_bull: bool,
    pub is_strong_bear: bool,
}

impl HeikinAshiBar {
    pub fn new(o: f64, h: f64, l: f64, c: f64, prev_o: f64, prev_c: f64) -> Self {
        let ha_open = (prev_o + prev_c) / 2.0;
        let ha_close = (o + h + l + c) / 4.0;
        let ha_high = h.max(ha_open.max(ha_close));
        let ha_low = l.min(ha_open.min(ha_close));
        let is_strong_bull = (ha_close > ha_open) && ((ha_low - ha_open).abs() < 1e-4);
        let is_strong_bear = (ha_close < ha_open) && ((ha_high - ha_open).abs() < 1e-4);

        Self {
            open: ha_open,
            high: ha_high,
            low: ha_low,
            close: ha_close,
            is_strong_bull,
            is_strong_bear,
        }
    }
}

pub struct WeeklySqueezeEngineRust;

impl WeeklySqueezeEngineRust {
    pub fn is_in_squeeze(bb_u: f64, bb_l: f64, kc_u: f64, kc_l: f64) -> bool {
        (bb_u < kc_u) && (bb_l > kc_l)
    }

    pub fn midpoint_entry(o: f64, c: f64) -> f64 {
        (o + c) / 2.0
    }
}
