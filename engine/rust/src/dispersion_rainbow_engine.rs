// engine/rust/src/dispersion_rainbow_engine.rs
// OptionAlpha Agent — Module U4: Rust Dispersion, Rainbow & Basket Engine

pub struct DispersionRainbowEngineRust;

impl DispersionRainbowEngineRust {
    pub fn basket_variance(weights: &[f64], vols: &[f64], corr: &[Vec<f64>]) -> f64 {
        let n = weights.len();
        let mut var = 0.0;
        for i in 0..n {
            for j in 0..n {
                var += weights[i] * weights[j] * vols[i] * vols[j] * corr[i][j];
            }
        }
        var.max(1e-6)
    }

    pub fn rainbow_payoff(returns: &mut [f64], weights_descending: &[f64]) -> f64 {
        returns.sort_by(|a, b| b.partial_cmp(a).unwrap());
        let mut payoff = 0.0;
        let n = returns.len().min(weights_descending.len());
        for i in 0..n {
            payoff += weights_descending[i] * returns[i];
        }
        payoff.max(0.0)
    }

    pub fn icbc_vs_cbc(rets: &[f64], cap: f64) -> (f64, f64, f64) {
        let n = rets.len() as f64;
        let sum_capped: f64 = rets.iter().map(|&r| r.min(cap)).sum();
        let sum_raw: f64 = rets.iter().sum();

        let icbc = (sum_capped / n).max(0.0);
        let cbc = (sum_raw / n).min(cap).max(0.0);
        (icbc, cbc, cbc - icbc)
    }
}
