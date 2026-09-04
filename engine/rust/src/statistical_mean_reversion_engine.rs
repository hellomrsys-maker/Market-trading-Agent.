//! Module AJ4 (Rust): Quantitative Mean Reversion, Cointegration & Statistical Arbitrage Engine.
//! High-speed SIMD rolling Z-score and Ornstein-Uhlenbeck parameter state evaluation.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct StatisticalMeanReversionState {
    pub current_spread_value: f64,
    pub rolling_mean: f64,
    pub rolling_std: f64,
    pub zscore: f64,
    pub ou_theta: f64,
    pub ou_half_life: f64,
    pub hurst_exponent: f64,
    pub signal_action: i32,
    pub regime_mean_reverting: u32,
}

impl StatisticalMeanReversionState {
    pub fn evaluate(current_val: f64, mean: f64, std_dev: f64, theta: f64, hurst: f64) -> Self {
        let s = std_dev.max(1e-5);
        let z = (current_val - mean) / s;
        let hl = if theta > 0.0 { 2.0f64.ln() / theta } else { 9999.0 };
        let mr = if hurst < 0.45 { 1 } else { 0 };

        let action = if z >= 3.5 || z <= -3.5 {
            99
        } else if z >= 2.0 {
            -1
        } else if z <= -2.0 {
            1
        } else if z.abs() <= 0.5 {
            0
        } else {
            0
        };

        Self {
            current_spread_value: current_val,
            rolling_mean: mean,
            rolling_std: std_dev,
            zscore: z,
            ou_theta: theta,
            ou_half_life: hl,
            hurst_exponent: hurst,
            signal_action: action,
            regime_mean_reverting: mr,
        }
    }
}
