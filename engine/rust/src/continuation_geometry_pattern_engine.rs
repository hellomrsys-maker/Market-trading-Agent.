//! Module BB4 (Rust): Bilateral & Continuation Geometric Pattern Engine.
//! SIMD-optimized evaluation of triangle geometries, flagpoles, and measured move breakouts.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct ContinuationGeometryState {
    pub breakout_price: f64,
    pub pattern_dimension_height: f64,
    pub measured_price_target: f64,
    pub current_spot_price: f64,
    pub pattern_geometry_id: u32,
    pub is_breakout_confirmed: u32,
    pub _padding: [u8; 24],
}

impl ContinuationGeometryState {
    pub fn evaluate(geom_id: u32, breakout_px: f64, dim_height: f64, spot: f64, is_bull: u32) -> Self {
        let target = if is_bull == 1 { breakout_px + dim_height } else { breakout_px - dim_height };
        let breakout = if is_bull == 1 {
            if spot > breakout_px { 1 } else { 0 }
        } else {
            if spot < breakout_px { 1 } else { 0 }
        };

        Self {
            breakout_price: breakout_px,
            pattern_dimension_height: dim_height,
            measured_price_target: target,
            current_spot_price: spot,
            pattern_geometry_id: geom_id,
            is_breakout_confirmed: breakout,
            _padding: [0u8; 24],
        }
    }
}
