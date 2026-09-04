//! Module BH4 (Rust): Structured Options, Collars & Binary Box Arbitrage Engine.
//! SIMD-optimized costless collars, Long Box risk-free arbitrage, and binary fixed return payouts.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct StructuredCollarBoxState {
    pub net_collar_premium: f64,
    pub max_upside_profit: f64,
    pub max_downside_risk: f64,
    pub box_risk_free_profit: f64,
    pub binary_net_payout: f64,
    pub is_costless_collar: u32,
    pub is_box_profitable: u32,
    pub is_binary_itm: u32,
    pub _padding: [u8; 16],
}

impl StructuredCollarBoxState {
    pub fn evaluate(
        basis: f64, call_k: f64, call_prem: f64, put_k: f64, put_prem: f64,
        box_k1: f64, box_k2: f64, box_debit: f64,
        bet: f64, payout_pct: f64, itm: u32
    ) -> Self {
        let net_collar = call_prem - put_prem;
        let is_costless = if net_collar >= 0.0 { 1 } else { 0 };
        let max_up = (call_k - basis) + net_collar;
        let max_down = (basis - put_k) - net_collar;

        let box_profit = (box_k2 - box_k1) - box_debit;
        let box_profitable = if box_profit > 0.0 { 1 } else { 0 };

        let bin_payout = if itm == 1 { bet * (payout_pct / 100.0) } else { -bet * 0.90 };

        Self {
            net_collar_premium: net_collar,
            max_upside_profit: max_up,
            max_downside_risk: max_down,
            box_risk_free_profit: box_profit,
            binary_net_payout: bin_payout,
            is_costless_collar: is_costless,
            is_box_profitable: box_profitable,
            is_binary_itm: itm,
            _padding: [0u8; 16],
        }
    }
}
