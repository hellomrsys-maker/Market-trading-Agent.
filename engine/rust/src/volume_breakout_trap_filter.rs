//! Module BC4 (Rust): Volume Spread Analysis & False Breakout / Trap Filter Engine.
//! SIMD-optimized evaluation of volume surges and Wyckoff Spring/Upthrust traps.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct VolumeBreakoutTrapState {
    pub breakout_volume: f64,
    pub sma20_volume: f64,
    pub volume_surge_ratio: f64,
    pub key_structural_level: f64,
    pub closing_price: f64,
    pub is_volume_confirmed: u32,
    pub is_wyckoff_trap: u32,
    pub trap_type_id: u32,
    pub _padding: [u8; 12],
}

impl VolumeBreakoutTrapState {
    pub fn audit(vol: f64, sma_vol: f64, key_level: f64, extreme_px: f64, close_px: f64, is_support: u32) -> Self {
        let surge = vol / sma_vol.max(1.0);
        let vol_confirmed = if surge >= 1.50 { 1 } else { 0 };

        let (is_trap, trap_id) = if is_support == 1 {
            let trap = if extreme_px < key_level && close_px >= key_level { 1 } else { 0 };
            (trap, if trap == 1 { 1 } else { 0 })
        } else {
            let trap = if extreme_px > key_level && close_px <= key_level { 1 } else { 0 };
            (trap, if trap == 1 { 2 } else { 0 })
        };

        Self {
            breakout_volume: vol,
            sma20_volume: sma_vol,
            volume_surge_ratio: surge,
            key_structural_level: key_level,
            closing_price: close_px,
            is_volume_confirmed: vol_confirmed,
            is_wyckoff_trap: is_trap,
            trap_type_id: trap_id,
            _padding: [0u8; 12],
        }
    }
}
