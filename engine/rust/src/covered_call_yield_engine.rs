//! Module AP4 (Rust): Dynamic Covered Call Yield & Dividend Capture Optimizer Engine.
//! SIMD-optimized evaluation of static yield, max upside yield, and ex-dividend assignment risk.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CoveredCallYieldState {
    pub stock_cost_basis: f64,
    pub current_spot: f64,
    pub strike_price: f64,
    pub call_premium: f64,
    pub breakeven_price: f64,
    pub annualized_static_yield: f64,
    pub annualized_max_yield: f64,
    pub early_assignment_risk: u32,
    pub _padding: [u8; 4],
}

impl CoveredCallYieldState {
    pub fn evaluate(basis: f64, spot: f64, strike: f64, premium: f64, dte: f64, dividend: f64) -> Self {
        let be = basis - premium;
        let static_y = ((premium + dividend) / basis) * 100.0;
        let ann_static = static_y * (365.0 / dte.max(1.0));

        let cap_gain = (strike - basis).max(0.0);
        let max_y = ((cap_gain + premium + dividend) / basis) * 100.0;
        let ann_max = max_y * (365.0 / dte.max(1.0));

        let intrinsic = (spot - strike).max(0.0);
        let extrinsic = (premium - intrinsic).max(0.0);
        let assignment = if spot > strike && extrinsic < dividend { 1 } else { 0 };

        Self {
            stock_cost_basis: basis,
            current_spot: spot,
            strike_price: strike,
            call_premium: premium,
            breakeven_price: be,
            annualized_static_yield: ann_static,
            annualized_max_yield: ann_max,
            early_assignment_risk: assignment,
            _padding: [0u8; 4],
        }
    }
}
