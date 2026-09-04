//! Module BG4 (Rust): Forex Microstructure, Bladerunner 20-EMA & Carry Trade Engine.
//! SIMD-optimized Bladerunner 20-EMA price action, rollover carry yield, and Kelly sizing.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct BladerunnerCarryState {
    pub spot_price: f64,
    pub ema_20_level: f64,
    pub daily_carry_interest: f64,
    pub optimal_kelly_allocation: f64,
    pub polarity_is_above_ema: u32,
    pub trade_signal_action: u32,
    pub is_positive_carry: u32,
    pub _padding: [u8; 20],
}

impl BladerunnerCarryState {
    pub fn evaluate(
        spot: f64, ema20: f64, rejected: u32, confirmed: u32,
        rate_long: f64, rate_short: f64, units: f64,
        win_prob: f64, win_loss: f64
    ) -> Self {
        let above = if spot > ema20 { 1 } else { 0 };

        let action = if above == 1 && rejected == 1 && confirmed == 1 {
            1 // Buy
        } else if above == 0 && rejected == 1 && confirmed == 1 {
            2 // Sell
        } else {
            0 // Wait
        };

        let diff = (rate_long - rate_short) / 100.0;
        let daily_int = (diff * units) / 365.0;
        let pos_carry = if daily_int > 0.0 { 1 } else { 0 };

        let w = win_prob.max(0.01).min(0.99);
        let r = win_loss.max(0.01);
        let k = w - ((1.0 - w) / r);
        let alloc = k.max(0.0).min(0.25);

        Self {
            spot_price: spot,
            ema_20_level: ema20,
            daily_carry_interest: daily_int,
            optimal_kelly_allocation: alloc,
            polarity_is_above_ema: above,
            trade_signal_action: action,
            is_positive_carry: pos_carry,
            _padding: [0u8; 20],
        }
    }
}
