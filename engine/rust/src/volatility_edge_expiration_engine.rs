//! Module AI4 (Rust): Institutional Volatility Edge & Expiration Microstructure Engine.
//! High-speed SIMD strike pinning and Greek budget assessment.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct VolatilityEdgeState {
    pub spot_price: f64,
    pub target_pin_strike: f64,
    pub dte_days: f64,
    pub pinning_gravitational_score: f64,
    pub portfolio_vega: f64,
    pub portfolio_theta: f64,
    pub vega_theta_ratio: f64,
    pub is_pinning_candidate: u32,
    pub risk_budget_balanced: u32,
}

impl VolatilityEdgeState {
    pub fn evaluate(spot: f64, strike: f64, dte: f64, oi: i32, vega: f64, theta: f64) -> Self {
        let dist = (spot - strike).abs();
        let t_factor = (-dte.max(0.01) * 2.0).exp();
        let pull = (oi as f64 / (dist * dist + 1.0)) * t_factor;
        let is_pin = if dist < 2.0 && dte <= 1.0 && oi > 5000 { 1 } else { 0 };

        let ratio = vega.abs() / theta.abs().max(1e-4);
        let balanced = if ratio <= 3.5 { 1 } else { 0 };

        Self {
            spot_price: spot,
            target_pin_strike: strike,
            dte_days: dte,
            pinning_gravitational_score: pull,
            portfolio_vega: vega,
            portfolio_theta: theta,
            vega_theta_ratio: ratio,
            is_pinning_candidate: is_pin,
            risk_budget_balanced: balanced,
        }
    }
}
