//! Module AO4 (Rust): Cash-Secured Put (CSP) Ladder & Acquisition Basis Optimizer Engine.
//! SIMD-optimized evaluation of CSP discounted cost basis, annualized ROC %, and POP.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CashSecuredPutState {
    pub spot_price: f64,
    pub strike_price: f64,
    pub premium_received: f64,
    pub effective_cost_basis: f64,
    pub annualized_roc_pct: f64,
    pub put_delta: f64,
    pub pop_estimate_pct: u32,
    pub is_optimal_setup: u32,
    pub _padding: [u8; 8],
}

impl CashSecuredPutState {
    pub fn evaluate(spot: f64, strike: f64, premium: f64, dte: f64, delta: f64) -> Self {
        let basis = strike - premium;
        let collateral = strike * 100.0;
        let trade_roc = (premium * 100.0 / collateral) * 100.0;
        let ann_roc = trade_roc * (365.0 / dte.max(1.0));
        let abs_d = delta.abs();
        let pop = ((1.0 - abs_d) * 100.0) as u32;
        let optimal = if abs_d >= 0.20 && abs_d <= 0.30 && dte >= 30.0 && dte <= 45.0 { 1 } else { 0 };

        Self {
            spot_price: spot,
            strike_price: strike,
            premium_received: premium,
            effective_cost_basis: basis,
            annualized_roc_pct: ann_roc,
            put_delta: delta,
            pop_estimate_pct: pop,
            is_optimal_setup: optimal,
            _padding: [0u8; 8],
        }
    }
}
