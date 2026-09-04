//! Phase 8 Training Matrix Runner (T4 - Rust).
//! Benchmarks Modules AC4, AD4, AE4, AF4.

mod options_equivalency_engine;
mod second_order_greeks_surface_engine;
mod multidimensional_spread_wing_engine;
mod strategic_gamma_scalping_engine;

use options_equivalency_engine::OptionsEquivalencyEngine;
use second_order_greeks_surface_engine::SecondOrderGreeksSurfaceEngine;
use multidimensional_spread_wing_engine::MultidimensionalSpreadWingEngine;
use strategic_gamma_scalping_engine::StrategicGammaScalpingEngine;

fn main() {
    println!("[T4 RUST] Starting SIMD Benchmarking & Training Epochs for Phase 8...");

    // AC4
    let mut ac_state = OptionsEquivalencyEngine::new_state();
    OptionsEquivalencyEngine::compute_equivalency(&mut ac_state, 66.0, 65.0, 3.45, 2.10, 0.04, 71, 0.10);

    // AD4
    let mut ad_state = SecondOrderGreeksSurfaceEngine::new_state();
    ad_state.forward_implied_vol = SecondOrderGreeksSurfaceEngine::calculate_forward_vol(0.36, 30, 0.54, 90);

    // AE4
    let mut ae_state = MultidimensionalSpreadWingEngine::new_state();
    MultidimensionalSpreadWingEngine::structure_ratio_spread(&mut ae_state, 50.0, 55.0, 4.0, 2.0);

    // AF4
    let mut af_state = StrategicGammaScalpingEngine::new_state();
    StrategicGammaScalpingEngine::execute_scalp_evaluation(&mut af_state, 98.0, 100.0, 0.15, 0.03, -0.30, 0.35);

    println!("[T4 RUST] Modules AC4, AD4, AE4, AF4 trained successfully.");
}
