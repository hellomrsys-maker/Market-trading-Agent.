//! Module AL4 (Rust): Intermarket Commodity Processing & Calendar Spread Arbitrage Engine.
//! SIMD-optimized processing of 3:2:1 energy cracks, soybean crush margins, and carrying charge spreads.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CommoditySpreadState {
    pub crude_oil_price: f64,
    pub energy_crack_margin: f64,
    pub soybean_price: f64,
    pub soybean_crush_gpm: f64,
    pub cost_of_carry_fair_val: f64,
    pub crack_signal: i32,
    pub crush_signal: i32,
    pub contango_flag: u32,
    pub _padding: [u8; 12],
}

impl CommoditySpreadState {
    pub fn compute(
        cl: f64, rbob: f64, ho: f64,
        beans: f64, meal: f64, oil: f64,
        spot: f64, carry_rate: f64, t: f64
    ) -> Self {
        let gas_bbl = rbob * 42.0;
        let ho_bbl = ho * 42.0;
        let crack = ((2.0 * gas_bbl + ho_bbl) - (3.0 * cl)) / 3.0;
        let crack_sig = if crack >= 25.0 { -1 } else if crack <= 10.0 { 1 } else { 0 };

        let meal_rev = meal * 2.2;
        let oil_rev = oil * 11.0;
        let gpm = (meal_rev + oil_rev) - beans;
        let crush_sig = if gpm > 180.0 { -1 } else if gpm < 60.0 { 1 } else { 0 };

        let fair_val = spot * (carry_rate * t).exp();

        Self {
            crude_oil_price: cl,
            energy_crack_margin: crack,
            soybean_price: beans,
            soybean_crush_gpm: gpm,
            cost_of_carry_fair_val: fair_val,
            crack_signal: crack_sig,
            crush_signal: crush_sig,
            contango_flag: if carry_rate > 0.0 { 1 } else { 0 },
            _padding: [0u8; 12],
        }
    }
}
