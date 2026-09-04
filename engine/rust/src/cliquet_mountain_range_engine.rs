// engine/rust/src/cliquet_mountain_range_engine.rs
// OptionAlpha Agent — Module W4: Rust Cliquet, Napoleon & Mountain Range Engine

pub struct CliquetMountainRangeEngineRust;

impl CliquetMountainRangeEngineRust {
    pub fn lflc_cliquet(returns: &[f64], local_floor: f64, local_cap: f64) -> f64 {
        returns.iter().map(|&r| r.max(local_floor).min(local_cap)).sum()
    }

    pub fn gflc_cliquet(returns: &[f64], local_floor: f64, local_cap: f64, global_floor: f64, global_cap: f64) -> f64 {
        let raw = Self::lflc_cliquet(returns, local_floor, local_cap);
        raw.max(global_floor).min(global_cap)
    }

    pub fn napoleon(returns: &[f64], max_coupon: f64) -> f64 {
        let worst = returns.iter().cloned().fold(f64::INFINITY, f64::min);
        (max_coupon + worst).max(0.0)
    }

    pub fn everest(returns: &[f64], coupon: f64) -> f64 {
        let worst = returns.iter().cloned().fold(f64::INFINITY, f64::min);
        coupon + worst
    }
}
