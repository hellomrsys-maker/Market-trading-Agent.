// engine/rust/src/bsm_jump_diffusion_engine.rs
// OptionAlpha Agent — Module R4: Rust BSM & Jump-Diffusion Engine

pub struct BSMJumpDiffusionEngineRust;

impl BSMJumpDiffusionEngineRust {
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

    pub fn price_merton(s: f64, x: f64, t: f64, r: f64, sigma: f64, q: f64) -> (f64, f64, f64) {
        let sqrt_t = t.max(1e-6).sqrt();
        let d1 = ((s / x).ln() + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
        let d2 = d1 - sigma * sqrt_t;

        let nd1 = Self::normal_cdf(d1);
        let nd2 = Self::normal_cdf(d2);
        let exp_qt = (-q * t).exp();
        let exp_rt = (-r * t).exp();

        let call = s * exp_qt * nd1 - x * exp_rt * nd2;
        let put = x * exp_rt * Self::normal_cdf(-d2) - s * exp_qt * Self::normal_cdf(-d1);
        let delta_call = exp_qt * nd1;

        (call, put, delta_call)
    }

    pub fn probability_ever_itm(s: f64, x: f64, t: f64, r: f64, sigma: f64, q: f64) -> f64 {
        if s >= x { return 1.0; }
        let sqrt_t = t.max(1e-6).sqrt();
        let d2 = ((s / x).ln() + (r - q - 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
        let b = (1.0 / sigma) * (x / s).ln();
        let a = (1.0 / sigma) * (r - q - 0.5 * sigma * sigma);

        let p_ever = Self::normal_cdf(d2) + (2.0 * a * b).exp() * Self::normal_cdf(d2 - 2.0 * a * sqrt_t);
        p_ever.min(1.0).max(0.0)
    }
}
