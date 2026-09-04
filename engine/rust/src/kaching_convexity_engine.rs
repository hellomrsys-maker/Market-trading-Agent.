#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct KaChingConvexityState {
    pub long_put_strike: f64,
    pub short_put_strike: f64,
    pub long_put_delta: f64,
    pub short_put_delta: f64,
    pub net_weekly_premium: f64,
    pub cumulative_cash_collected: f64,
    pub days_to_earnings: u32,
    pub roll_count: u16,
    pub double_dip_active: u8,
    pub is_supersized: u8,
    pub status_flags: u8,
    pub _padding: [u8; 7],
}

impl KaChingConvexityState {
    pub fn new(spot: f64, iv: f64, dte: u32) -> Self {
        let long_delta = if iv > 0.35 { 0.38 } else { 0.25 };
        let long_strike = spot * (1.0 - if long_delta == 0.25 { 0.08 } else { 0.05 });
        let short_delta = if spot >= long_strike { 0.50 } else { 0.40 };
        let short_strike = spot;
        let initial_premium = spot * 0.018 * (1.0 + iv);

        Self {
            long_put_strike: long_strike,
            short_put_strike: short_strike,
            long_put_delta: long_delta,
            short_put_delta: short_delta,
            net_weekly_premium: initial_premium,
            cumulative_cash_collected: initial_premium,
            days_to_earnings: dte,
            roll_count: 0,
            double_dip_active: 0,
            is_supersized: 0,
            status_flags: 1,
            _padding: [0; 7],
        }
    }
}
