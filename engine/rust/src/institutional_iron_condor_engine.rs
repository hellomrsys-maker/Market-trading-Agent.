#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct InstitutionalIronCondorState {
    pub expected_price_gbm: f64,
    pub net_premium_credit: f64,
    pub max_risk_capital: f64,
    pub portfolio_delta: f64,
    pub portfolio_gamma: f64,
    pub portfolio_theta: f64,
    pub archetype_id: u32,
    pub dte: u16,
    pub is_iv_crush_target: u8,
    pub is_martingale_valid: u8,
    pub padding: [u8; 8],
}

pub struct InstitutionalIronCondorEngine;

impl InstitutionalIronCondorEngine {
    pub fn configure_archetype(
        archetype_id: u32,
        spot: f64,
        drift: f64,
        _sigma: f64,
        time_years: f64
    ) -> InstitutionalIronCondorState {
        let expected_price_gbm = spot * (drift * time_years).exp();
        let is_martingale_valid = if (expected_price_gbm - spot).abs() < 1.0 { 1 } else { 0 };
        let is_iv_crush_target = if archetype_id == 2 { 1 } else { 0 };

        InstitutionalIronCondorState {
            expected_price_gbm,
            net_premium_credit: 0.0,
            max_risk_capital: 0.0,
            portfolio_delta: 0.0,
            portfolio_gamma: 0.0,
            portfolio_theta: 0.0,
            archetype_id,
            dte: 30,
            is_iv_crush_target,
            is_martingale_valid,
            padding: [0; 8],
        }
    }
}
