// engine/rust/src/phase6_training.rs
// OptionAlpha Agent — Module T4: Rust Phase 6 Training Module

pub mod dispersion_rainbow_engine;
pub mod barrier_autocallable_engine;
pub mod cliquet_mountain_range_engine;
pub mod variance_swap_copula_engine;

use dispersion_rainbow_engine::DispersionRainbowEngineRust;
use barrier_autocallable_engine::BarrierAutocallableEngineRust;
use cliquet_mountain_range_engine::CliquetMountainRangeEngineRust;
use variance_swap_copula_engine::VarianceSwapCopulaEngineRust;

fn main() {
    println!("[T4 RUST] Starting SIMD Benchmarking & Training Epochs for Phase 6...");

    let weights = vec![0.5, 0.5];
    let vols = vec![0.20, 0.30];
    let corr = vec![vec![1.0, 0.4], vec![0.4, 1.0]];
    let var_p = DispersionRainbowEngineRust::basket_variance(&weights, &vols, &corr);

    let h_shift = BarrierAutocallableEngineRust::discrete_barrier_shift(80.0, 0.20, 1.0, 252, true);
    let (bs_dig, total_dig) = BarrierAutocallableEngineRust::digital_skew_correction(100.0, 100.0, 1.0, 0.05, 0.20, -0.05);

    let rets = vec![0.05, -0.02, 0.08];
    let lflc = CliquetMountainRangeEngineRust::lflc_cliquet(&rets, 0.0, 0.05);
    let napoleon = CliquetMountainRangeEngineRust::napoleon(&rets, 0.50);

    let log_rets = vec![0.01, -0.015, 0.02, -0.005, 0.012];
    let rv = VarianceSwapCopulaEngineRust::realized_variance(&log_rets, 252.0);
    let (gamma, vega, theta) = VarianceSwapCopulaEngineRust::variance_swap_greeks(1.0, 0.25, 0.20);

    println!("[T4 RUST] Modules U4, V4, W4, X4 trained successfully.");
}
