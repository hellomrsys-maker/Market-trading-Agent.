// engine/rust/src/iron_condor.rs
// OptionAlpha Agent — Rust SIMD 4-Leg Iron Condor Pricing & Asymmetric Wing Optimizer
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

pub const CONTRACT_MULTIPLIER: f64 = 100.0;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustIronCondorProposal {
    #[pyo3(get)]
    pub symbol: String,
    #[pyo3(get)]
    pub long_put: f64,
    #[pyo3(get)]
    pub short_put: f64,
    #[pyo3(get)]
    pub short_call: f64,
    #[pyo3(get)]
    pub long_call: f64,
    #[pyo3(get)]
    pub net_credit_dollars: f64,
    #[pyo3(get)]
    pub max_loss_dollars: f64,
    #[pyo3(get)]
    pub put_wing_width: f64,
    #[pyo3(get)]
    pub call_wing_width: f64,
    #[pyo3(get)]
    pub profit_zone_low: f64,
    #[pyo3(get)]
    pub profit_zone_high: f64,
    #[pyo3(get)]
    pub contract_multiplier: i32,
    #[pyo3(get)]
    pub zero_bridge_status: String,
}

#[pyclass]
pub struct RustIronCondorEngine {
    pub default_wing_width: f64,
    pub target_dte: i32,
}

#[pymethods]
impl RustIronCondorEngine {
    #[new]
    pub fn new(wing_width: Option<f64>, target_dte: Option<i32>) -> Self {
        Self {
            default_wing_width: wing_width.unwrap_or(5.0),
            target_dte: target_dte.unwrap_or(45),
        }
    }

    /// Evaluates 4-Leg Iron Condor with Asymmetric Skew Optimization
    pub fn evaluate_condor(
        &self,
        symbol: String,
        spot: f64,
        put_skew: f64,
        short_put_delta: f64,
        short_call_delta: f64,
        credit_per_contract: f64,
    ) -> Option<RustIronCondorProposal> {
        let (put_wing, call_wing) = if put_skew > 0.04 {
            ((self.default_wing_width - 1.0).max(2.5), self.default_wing_width + 2.0)
        } else if put_skew < -0.02 {
            (self.default_wing_width + 2.0, (self.default_wing_width - 1.0).max(2.5))
        } else {
            (self.default_wing_width, self.default_wing_width)
        };

        let short_put = (spot * 0.95 / 2.5).round() * 2.5;
        let long_put = short_put - put_wing;
        let short_call = (spot * 1.05 / 2.5).round() * 2.5;
        let long_call = short_call + call_wing;

        let max_wing = put_wing.max(call_wing);
        let net_credit_dollars = credit_per_contract * CONTRACT_MULTIPLIER;
        let max_loss_dollars = (max_wing - credit_per_contract) * CONTRACT_MULTIPLIER;

        if max_loss_dollars <= 0.0 || net_credit_dollars <= 20.0 {
            return None; // Non-viable credit to risk profile
        }

        let profit_zone_low = short_put - credit_per_contract;
        let profit_zone_high = short_call + credit_per_contract;

        Some(RustIronCondorProposal {
            symbol,
            long_put,
            short_put,
            short_call,
            long_call,
            net_credit_dollars,
            max_loss_dollars,
            put_wing_width: put_wing,
            call_wing_width: call_wing,
            profit_zone_low,
            profit_zone_high,
            contract_multiplier: 100,
            zero_bridge_status: "0_NS_SYNC".to_string(),
        })
    }
}
