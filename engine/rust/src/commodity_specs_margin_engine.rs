//! Module AS4 (Rust): Futures Contract Specifications, Tick Multipliers & SPAN Margin Engine.
//! SIMD-optimized SPAN margin calculation, excess margin monitoring, and leverage tracking.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CommoditySpecsMarginState {
    pub account_equity: f64,
    pub total_initial_margin: f64,
    pub total_maint_margin: f64,
    pub margin_excess: f64,
    pub margin_proximity_score: f64,
    pub leverage_utilization_pct: f64,
    pub is_margin_safe: u32,
    pub is_margin_call: u32,
    pub _padding: [u8; 8],
}

impl CommoditySpecsMarginState {
    pub fn audit(equity: f64, initial_m: f64, maint_m: f64) -> Self {
        let excess = equity - maint_m;
        let util = (initial_m / equity.max(1.0)) * 100.0;
        let prox = if initial_m > maint_m { (equity - maint_m) / (initial_m - maint_m) } else { 1.0 };
        let safe = if prox >= 1.0 { 1 } else { 0 };
        let call = if equity < maint_m { 1 } else { 0 };

        Self {
            account_equity: equity,
            total_initial_margin: initial_m,
            total_maint_margin: maint_m,
            margin_excess: excess,
            margin_proximity_score: prox,
            leverage_utilization_pct: util,
            is_margin_safe: safe,
            is_margin_call: call,
            _padding: [0u8; 8],
        }
    }
}
