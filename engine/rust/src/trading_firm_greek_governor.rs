//! Module AX4 (Rust): Trading Firm Greek Inventory Governance & Vega/Gamma Risk Budgeting Engine.
//! SIMD-optimized market maker Greek auditing, gamma rent ratio, and vega risk budgeting.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct TradingFirmGreekState {
    pub portfolio_delta: f64,
    pub portfolio_gamma: f64,
    pub portfolio_theta: f64,
    pub portfolio_vega: f64,
    pub gamma_rent_ratio: f64,
    pub vega_pct_equity: f64,
    pub is_firm_approved: u32,
    pub is_delta_compliant: u32,
    pub is_rent_compliant: u32,
    pub is_vega_compliant: u32,
}

impl TradingFirmGreekState {
    pub fn audit(delta: f64, gamma: f64, theta: f64, vega: f64, spot: f64, iv: f64, equity: f64) -> Self {
        let daily_sigma = iv / 252.0_f64.sqrt();
        let daily_gamma_cost = 0.5 * gamma.abs() * (spot * spot) * (daily_sigma * daily_sigma);
        let rent_ratio = theta.abs() / daily_gamma_cost.max(1e-4);

        let vega_exp = vega.abs() * 100.0;
        let vega_pct = (vega_exp / equity.max(1.0)) * 100.0;

        let delta_ok = if delta.abs() <= 50.0 { 1 } else { 0 };
        let rent_ok = if rent_ratio >= 1.0 { 1 } else { 0 };
        let vega_ok = if vega_pct <= 8.0 { 1 } else { 0 };
        let approved = if delta_ok == 1 && rent_ok == 1 && vega_ok == 1 { 1 } else { 0 };

        Self {
            portfolio_delta: delta,
            portfolio_gamma: gamma,
            portfolio_theta: theta,
            portfolio_vega: vega,
            gamma_rent_ratio: rent_ratio,
            vega_pct_equity: vega_pct,
            is_firm_approved: approved,
            is_delta_compliant: delta_ok,
            is_rent_compliant: rent_ok,
            is_vega_compliant: vega_ok,
        }
    }
}
