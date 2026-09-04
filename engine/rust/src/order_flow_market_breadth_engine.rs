#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct OrderFlowMarketBreadthState {
    pub mcclellan_oscillator: f64,
    pub mcclellan_summation: f64,
    pub arms_trin_ratio: f64,
    pub chaikin_money_flow: f64,
    pub option_order_flow_vol: f64,
    pub flow_normal_ratio: f64,
    pub is_unusual_flow_detected: u32,
    pub is_tko_breakout: u32,
    pub is_trin_extreme_fear: u32,
    pub padding: [u8; 4],
}

pub struct OrderFlowMarketBreadthEngine;

impl OrderFlowMarketBreadthEngine {
    pub fn audit_breadth(
        daily_vol: f64,
        avg_vol: f64,
        adv_issues: f64,
        dec_issues: f64,
        adv_vol: f64,
        dec_vol: f64
    ) -> OrderFlowMarketBreadthState {
        let flow_normal_ratio = daily_vol / avg_vol.max(1.0);
        let is_unusual_flow_detected = if flow_normal_ratio >= 5.0 { 1 } else { 0 };

        let ad_ratio = adv_issues / dec_issues.max(1.0);
        let vol_ratio = adv_vol / dec_vol.max(1.0);
        let arms_trin_ratio = ad_ratio / vol_ratio.max(0.001);
        let is_trin_extreme_fear = if arms_trin_ratio >= 1.50 { 1 } else { 0 };

        OrderFlowMarketBreadthState {
            mcclellan_oscillator: 0.0,
            mcclellan_summation: 0.0,
            arms_trin_ratio,
            chaikin_money_flow: 0.0,
            option_order_flow_vol: daily_vol,
            flow_normal_ratio,
            is_unusual_flow_detected,
            is_tko_breakout: 0,
            is_trin_extreme_fear,
            padding: [0; 4],
        }
    }
}
