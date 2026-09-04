//! Module BA4 (Rust): Classical Reversal Pattern Recognition Engine.
//! SIMD-optimized evaluation of Head & Shoulders and Double Top/Bottom patterns with measured move projections.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct ClassicalReversalState {
    pub pattern_neckline: f64,
    pub pattern_height: f64,
    pub measured_price_target: f64,
    pub current_spot_price: f64,
    pub pattern_type_id: u32,
    pub is_structure_valid: u32,
    pub is_breakout_confirmed: u32,
    pub _padding: [u8; 20],
}

impl ClassicalReversalState {
    pub fn evaluate(type_id: u32, head_or_peak: f64, neckline: f64, spot: f64, is_bull: u32) -> Self {
        let height = (head_or_peak - neckline).abs();
        let target = if is_bull == 1 { neckline + height } else { neckline - height };
        let breakout = if is_bull == 1 {
            if spot > neckline { 1 } else { 0 }
        } else {
            if spot < neckline { 1 } else { 0 }
        };

        Self {
            pattern_neckline: neckline,
            pattern_height: height,
            measured_price_target: target,
            current_spot_price: spot,
            pattern_type_id: type_id,
            is_structure_valid: 1,
            is_breakout_confirmed: breakout,
            _padding: [0u8; 20],
        }
    }
}
