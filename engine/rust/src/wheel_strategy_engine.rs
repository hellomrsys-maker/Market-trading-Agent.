//! Module AQ4 (Rust): The Wheel Strategy Lifecycle & Dynamic State Machine Engine.
//! SIMD-optimized state machine transitions and net cost-basis amortization.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct WheelStrategyState {
    pub spot_price: f64,
    pub shares_cost_basis: f64,
    pub total_accumulated_income: f64,
    pub true_net_cost_basis: f64,
    pub active_strike_price: f64,
    pub profit_captured_pct: f64,
    pub current_wheel_state: u32,
    pub is_50pct_profit_hit: u32,
    pub _padding: [u8; 8],
}

impl WheelStrategyState {
    pub fn track(
        state_id: u32, spot: f64, cost_basis: f64,
        put_prem: f64, call_prem: f64, dividends: f64,
        strike: f64, orig_prem: f64, curr_prem: f64
    ) -> Self {
        let total_inc = put_prem + call_prem + dividends;
        let true_basis = cost_basis - total_inc;
        let profit = orig_prem - curr_prem;
        let profit_pct = if orig_prem > 0.0 { (profit / orig_prem) * 100.0 } else { 0.0 };
        let hit_50 = if profit_pct >= 50.0 { 1 } else { 0 };

        Self {
            spot_price: spot,
            shares_cost_basis: cost_basis,
            total_accumulated_income: total_inc,
            true_net_cost_basis: true_basis,
            active_strike_price: strike,
            profit_captured_pct: profit_pct,
            current_wheel_state: state_id,
            is_50pct_profit_hit: hit_50,
            _padding: [0u8; 8],
        }
    }
}
