// engine/rust/src/psychological_governor.rs
// OptionAlpha Agent — Rust SIMD Disciplined Trader Psychological Tilt & Loss Predefinition Engine
// Polyglot Pillar 1: Rust SIMD Data Processing

use pyo3::prelude::*;

#[derive(Clone, Debug)]
#[pyclass]
pub struct RustPsychologicalResult {
    #[pyo3(get)]
    pub is_approved: bool,
    #[pyo3(get)]
    pub state_of_mind: String,
    #[pyo3(get)]
    pub sizing_factor: f64,
    #[pyo3(get)]
    pub stop_loss: f64,
}

#[pyclass]
pub struct RustPsychologicalGovernor {
    pub max_consecutive_losses: i32,
    pub max_risk_pct: f64,
}

#[pymethods]
impl RustPsychologicalGovernor {
    #[new]
    pub fn new(max_consecutive_losses: Option<i32>, max_risk_pct: Option<f64>) -> Self {
        Self {
            max_consecutive_losses: max_consecutive_losses.unwrap_or(3),
            max_risk_pct: max_risk_pct.unwrap_or(0.02),
        }
    }

    /// Evaluates trade intent against Mark Douglas' 2 Rules & Revenge Trading Protections
    pub fn audit_trade(
        &self,
        stop_loss: f64,
        equity: f64,
        risk_dollars: f64,
        consecutive_wins: i32,
        consecutive_losses: i32,
    ) -> RustPsychologicalResult {
        if stop_loss <= 0.0 {
            return RustPsychologicalResult {
                is_approved: false,
                state_of_mind: "RULE_1_VIOLATION_NO_STOP".to_string(),
                sizing_factor: 0.0,
                stop_loss: 0.0,
            };
        }

        let max_allowed_risk = equity * self.max_risk_pct;
        let mut sizing_factor = if risk_dollars > max_allowed_risk {
            (max_allowed_risk / risk_dollars).clamp(0.10, 1.0)
        } else {
            1.0
        };

        let mut state = "OBJECTIVE_FLOW".to_string();

        if consecutive_losses >= self.max_consecutive_losses {
            sizing_factor *= 0.50; // Drawdown cooling
            state = "REVENGE_TRADING_SUPPRESSION".to_string();
        } else if consecutive_wins >= 4 {
            sizing_factor *= 0.75; // Euphoria protection
            state = "EUPHORIA_PREVENTION".to_string();
        }

        RustPsychologicalResult {
            is_approved: true,
            state_of_mind: state,
            sizing_factor,
            stop_loss,
        }
    }
}
