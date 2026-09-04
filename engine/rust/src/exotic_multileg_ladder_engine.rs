#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct ExoticMultiLegLadderState {
    pub strike_rung1: f64,
    pub strike_rung2: f64,
    pub strike_rung3: f64,
    pub strike_rung4: f64,
    pub lambda_elasticity: f64,
    pub net_package_premium: f64,
    pub max_sweet_spot_profit: f64,
    pub strategy_archetype: u16,
    pub call_legs_count: u8,
    pub put_legs_count: u8,
    pub _padding: [u8; 4],
}

impl ExoticMultiLegLadderState {
    pub fn new_strip(spot: f64, atm: f64, call_prem: f64, put_prem: f64) -> Self {
        let total_prem = (2.0 * put_prem) + call_prem;
        let delta = (1.0 * 0.50) + (2.0 * (-0.50));
        let lam = if total_prem > 0.001 { (delta * spot) / total_prem } else { 0.0 };

        Self {
            strike_rung1: atm,
            strike_rung2: atm,
            strike_rung3: atm,
            strike_rung4: 0.0,
            lambda_elasticity: lam,
            net_package_premium: total_prem,
            max_sweet_spot_profit: 999999.0,
            strategy_archetype: 1,
            call_legs_count: 1,
            put_legs_count: 2,
            _padding: [0; 4],
        }
    }
}
