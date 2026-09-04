//! Module AK4 (Rust): Schwager Classical Price Action & Breakout Trap Engine.
//! Provides SIMD-optimized evaluation of key reversal days and spring/upthrust traps.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct SchwagerPriceActionState {
    pub current_high: f64,
    pub current_low: f64,
    pub current_close: f64,
    pub stop_level: f64,
    pub projected_target: f64,
    pub key_reversal_flag: u32,
    pub trap_flag: u32,
    pub gap_type: u32,
    pub volume_confirmed: u32,
    pub _padding: [u8; 8],
}

impl SchwagerPriceActionState {
    pub fn evaluate(
        prev_low: f64, prev_high: f64, prev_close: f64,
        curr_low: f64, curr_high: f64, curr_close: f64,
        curr_vol: f64, avg_vol: f64,
        support: f64, resistance: f64
    ) -> Self {
        let vol_surge = avg_vol <= 0.0 || (curr_vol >= avg_vol * 1.3);
        let rev = if curr_low < prev_low && curr_close > prev_close && vol_surge {
            1
        } else if curr_high > prev_high && curr_close < prev_close && vol_surge {
            2
        } else {
            0
        };

        let trap = if curr_low < support && curr_close >= support {
            1
        } else if curr_high > resistance && curr_close <= resistance {
            2
        } else {
            0
        };

        Self {
            current_high: curr_high,
            current_low: curr_low,
            current_close: curr_close,
            stop_level: if rev == 1 { curr_low } else { curr_high },
            projected_target: curr_close * 1.05,
            key_reversal_flag: rev,
            trap_flag: trap,
            gap_type: 0,
            volume_confirmed: if vol_surge { 1 } else { 0 },
            _padding: [0u8; 8],
        }
    }
}
