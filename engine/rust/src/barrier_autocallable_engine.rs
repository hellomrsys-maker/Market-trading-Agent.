// engine/rust/src/barrier_autocallable_engine.rs
// OptionAlpha Agent — Module V4: Rust Barrier, Digital & Autocallable Engine

pub struct BarrierAutocallableEngineRust;

impl BarrierAutocallableEngineRust {
    pub fn discrete_barrier_shift(barrier: f64, sigma: f64, t_years: f64, num_obs: usize, is_short: bool) -> f64 {
        if num_obs == 0 { return barrier; }
        let dt = t_years / (num_obs as f64);
        let factor = 0.5826 * sigma * dt.sqrt();
        barrier * if is_short { factor.exp() } else { (-factor).exp() }
    }

    pub fn normal_cdf(z: f64) -> f64 {
        0.5 * (1.0 + Self::erf(z / std::f64::consts::SQRT_2))
    }

    fn erf(z: f64) -> f64 {
        let t = 1.0 / (1.0 + 0.5 * z.abs());
        let ans = 1.0 - t * (-z * z - 1.26551223 +
                t * (1.00002368 +
                t * (0.37409196 +
                t * (0.09678418 +
                t * (-0.18628806 +
                t * (0.27886807 +
                t * (-1.13520398 +
                t * (1.48851587 +
                t * (-0.82215223 +
                t * 0.17087277))))))))).exp();
        if z >= 0.0 { ans } else { -ans }
    }

    pub fn digital_skew_correction(s: f64, x: f64, t: f64, r: f64, sigma: f64, skew: f64) -> (f64, f64) {
        let sqrt_t = t.max(1e-6).sqrt();
        let d1 = ((s / x).ln() + (r + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
        let d2 = d1 - sigma * sqrt_t;

        let phi_d1 = (1.0 / (2.0 * std::f64::consts::PI).sqrt()) * (-0.5 * d1 * d1).exp();
        let vega = s * phi_d1 * sqrt_t;
        let bs_dig = (-r * t).exp() * Self::normal_cdf(d2);
        let total_dig = bs_dig + vega * skew.abs();

        (bs_dig, total_dig)
    }
}
