// engine/rust/src/variance_swap_copula_engine.rs
// OptionAlpha Agent — Module X4: Rust Volatility Derivatives & Copula Engine

pub struct VarianceSwapCopulaEngineRust;

impl VarianceSwapCopulaEngineRust {
    pub fn realized_variance(log_returns: &[f64], annualization_factor: f64) -> f64 {
        if log_returns.is_empty() { return 0.0; }
        let sum_sq: f64 = log_returns.iter().map(|&r| r * r).sum();
        (annualization_factor / log_returns.len() as f64) * sum_sq
    }

    pub fn variance_swap_greeks(t_years: f64, time_elapsed: f64, current_sigma: f64) -> (f64, f64, f64) {
        let t_rem = (t_years - time_elapsed).max(1e-4);
        let t_safe = t_years.max(1e-4);

        let cash_gamma = 2.0 / t_safe;
        let vega = (2.0 / t_safe) * current_sigma * t_rem;
        let theta = - (1.0 / t_safe) * current_sigma * current_sigma;

        (cash_gamma, vega, theta)
    }
}
