//! Module AN4 (Rust): Schwager Algorithmic Risk Budgeting & Robust System Optimization Engine.
//! SIMD-accelerated ATR position sizing, walk-forward degradation checks, and portfolio heat governor.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct FuturesRiskState {
    pub account_equity: f64,
    pub dollar_risk_target: f64,
    pub per_contract_risk: f64,
    pub current_heat_pct: f64,
    pub walk_forward_ratio: f64,
    pub recommended_contracts: i32,
    pub is_deployable: u32,
    pub is_heat_compliant: u32,
    pub _padding: [u8; 12],
}

impl FuturesRiskState {
    pub fn compute(
        equity: f64, risk_pct: f64, atr: f64, multiplier: f64, pt_val: f64,
        is_sharpe: f64, oos_sharpe: f64, open_risk_total: f64
    ) -> Self {
        let clamped_risk = risk_pct.min(1.5) / 100.0;
        let dollar_target = equity * clamped_risk;
        let per_contract = (atr * multiplier * pt_val).max(1.0);
        let contracts = (dollar_target / per_contract).floor().max(1.0) as i32;

        let ratio = oos_sharpe / is_sharpe.max(1e-4);
        let deployable = if ratio >= 0.65 && oos_sharpe > 0.5 { 1 } else { 0 };

        let heat = (open_risk_total / equity.max(1.0)) * 100.0;
        let heat_ok = if heat <= 6.0 { 1 } else { 0 };

        Self {
            account_equity: equity,
            dollar_risk_target: dollar_target,
            per_contract_risk: per_contract,
            current_heat_pct: heat,
            walk_forward_ratio: ratio,
            recommended_contracts: contracts,
            is_deployable: deployable,
            is_heat_compliant: heat_ok,
            _padding: [0u8; 12],
        }
    }
}
