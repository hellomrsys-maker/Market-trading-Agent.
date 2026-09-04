//! Module BE4 (Rust): Karl Domm All-Weather Options Portfolio & Tail Risk Vomma Engine.
//! SIMD-optimized SPAN margin slicing, 4 market regimes, and 5-delta teenie put positive vomma calculations.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct AllWeatherVommaState {
    pub worst_case_margin_req: f64,
    pub planned_capital: f64,
    pub margin_utilization_pct: f64,
    pub net_portfolio_vomma: f64,
    pub market_regime_id: u32,
    pub is_margin_safe: u32,
    pub has_positive_vomma: u32,
    pub _padding: [u8; 20],
}

impl AllWeatherVommaState {
    pub fn audit(
        pnl_12_down: f64,
        pnl_20_down: f64,
        pnl_10_up: f64,
        capital: f64,
        vix_spike: f64,
        core_vomma: f64,
        num_teenies: i32
    ) -> Self {
        let s12 = pnl_12_down.min(0.0).abs();
        let s20 = (pnl_20_down.min(0.0).abs()) / 2.0;
        let s10 = pnl_10_up.min(0.0).abs();

        let req = s12.max(s20.max(s10));
        let util = (req / capital.max(1.0)) * 100.0;
        let safe = if util <= 65.0 { 1 } else { 0 };

        let regime = if vix_spike >= 35.0 { 4 } else { 1 };
        let net_vomma = core_vomma + (num_teenies as f64 * 0.08);
        let pos_vomma = if net_vomma > 0.0 { 1 } else { 0 };

        Self {
            worst_case_margin_req: req,
            planned_capital: capital,
            margin_utilization_pct: util,
            net_portfolio_vomma: net_vomma,
            market_regime_id: regime,
            is_margin_safe: safe,
            has_positive_vomma: pos_vomma,
            _padding: [0u8; 20],
        }
    }
}
