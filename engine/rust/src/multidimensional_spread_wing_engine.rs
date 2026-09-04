//! Module AE4 (Rust): Multi-Dimensional Spread, Ratio & Wing Engine.
//! High-speed SIMD ratio spread, backspread, and wing structuring.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct MultidimensionalSpreadWingState {
    pub long_strike_k1: f32,
    pub short_strike_k2: f32,
    pub upper_strike_k3: f32,
    pub net_cash_flow: f32,
    pub max_profit_potential: f32,
    pub max_loss_risk: f32,
    pub upside_breakeven: f32,
    pub downside_breakeven: f32,
    pub butterfly_escape_strike: f32,
    pub spread_archetype_id: u32,
    pub is_credit_spread: u32,
    pub escape_viable_flag: u32,
    pub _padding: [u8; 16],
}

pub struct MultidimensionalSpreadWingEngine;

impl MultidimensionalSpreadWingEngine {
    pub fn new_state() -> MultidimensionalSpreadWingState {
        MultidimensionalSpreadWingState {
            long_strike_k1: 0.0,
            short_strike_k2: 0.0,
            upper_strike_k3: 0.0,
            net_cash_flow: 0.0,
            max_profit_potential: 0.0,
            max_loss_risk: 0.0,
            upside_breakeven: 0.0,
            downside_breakeven: 0.0,
            butterfly_escape_strike: 0.0,
            spread_archetype_id: 0,
            is_credit_spread: 0,
            escape_viable_flag: 1,
            _padding: [0; 16],
        }
    }

    pub fn structure_ratio_spread(
        state: &mut MultidimensionalSpreadWingState,
        k1: f32, k2: f32, prem_long: f32, prem_short: f32
    ) {
        state.long_strike_k1 = k1;
        state.short_strike_k2 = k2;
        state.net_cash_flow = (2.0 * prem_short) - prem_long;
        let strike_diff = k2 - k1;
        state.max_profit_potential = strike_diff + state.net_cash_flow;
        state.upside_breakeven = k2 + state.max_profit_potential;
        state.butterfly_escape_strike = k2 + strike_diff;

        state.spread_archetype_id = 0;
        state.is_credit_spread = if state.net_cash_flow >= 0.0 { 1 } else { 0 };
        state.escape_viable_flag = 1;
    }
}
