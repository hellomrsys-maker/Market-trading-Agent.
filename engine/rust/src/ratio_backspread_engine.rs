#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct RatioBackspreadState {
    pub short_strike: f64,
    pub long_strike: f64,
    pub net_debit_credit: f64,
    pub max_loss_point: f64,
    pub upper_bep: f64,
    pub lower_bep: f64,
    pub implied_volatility: f64,
    pub ratio_short: u16,
    pub ratio_long: u16,
    pub is_call_spread: u8,
    pub _padding: [u8; 3],
}

impl RatioBackspreadState {
    pub fn new_call_backspread(atm: f64, otm: f64, short_prem: f64, long_prem: f64) -> Self {
        let net_flow = (2.0 * long_prem) - short_prem;
        let max_loss = (otm - atm).abs() + net_flow;
        let upper_bep = otm + max_loss;
        let lower_bep = atm + if net_flow < 0.0 { net_flow } else { 0.0 };

        Self {
            short_strike: atm,
            long_strike: otm,
            net_debit_credit: net_flow,
            max_loss_point: max_loss,
            upper_bep,
            lower_bep,
            implied_volatility: 0.30,
            ratio_short: 1,
            ratio_long: 2,
            is_call_spread: 1,
            _padding: [0; 3],
        }
    }
}
