//! Module AT4 (Rust): Commodity Physical Delivery Risk, First Notice Day (FND) & Roll Governor Engine.
//! SIMD-optimized delivery risk assessment and volume roll transition logic.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct DeliveryRollState {
    pub front_month_volume: f64,
    pub next_month_volume: f64,
    pub days_to_fnd: i32,
    pub days_to_ltd: i32,
    pub is_physical_delivery: u32,
    pub is_volume_crossover: u32,
    pub is_fnd_danger: u32,
    pub roll_directive_action: u32,
    pub _padding: [u8; 24],
}

impl DeliveryRollState {
    pub fn evaluate(is_physical: u32, days_fnd: i32, days_ltd: i32, vol_m1: f64, vol_m2: f64) -> Self {
        let vol_cross = if vol_m2 > vol_m1 { 1 } else { 0 };
        let fnd_danger = if is_physical == 1 && days_fnd <= 5 { 1 } else { 0 };

        let action = if is_physical == 1 && days_fnd <= 1 {
            2
        } else if fnd_danger == 1 || vol_cross == 1 {
            1
        } else {
            0
        };

        Self {
            front_month_volume: vol_m1,
            next_month_volume: vol_m2,
            days_to_fnd: days_fnd,
            days_to_ltd: days_ltd,
            is_physical_delivery: is_physical,
            is_volume_crossover: vol_cross,
            is_fnd_danger: fnd_danger,
            roll_directive_action: action,
            _padding: [0u8; 24],
        }
    }
}
