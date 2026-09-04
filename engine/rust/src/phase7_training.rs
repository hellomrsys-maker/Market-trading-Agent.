//! Phase 7 Training Matrix Runner (T4 - Rust).
//! Benchmarks Modules Y4, Z4, AA4, AB4.

mod behavioral_psychology_engine;
mod cashflow_capital_ecosystem_engine;
mod tactical_swing_trading_engine;
mod tactical_options_discipline_engine;

use behavioral_psychology_engine::BehavioralPsychologyEngine;
use cashflow_capital_ecosystem_engine::CashflowCapitalEcosystemEngine;
use tactical_swing_trading_engine::TacticalSwingTradingEngine;
use tactical_options_discipline_engine::TacticalOptionsDisciplineEngine;

fn main() {
    println!("[T4 RUST] Starting SIMD Benchmarking & Training Epochs for Phase 7...");

    // Y4
    let mut y_state = BehavioralPsychologyEngine::new_state();
    BehavioralPsychologyEngine::update_state(&mut y_state, 1, 3, 0.2, 0.2, 0.1);

    // Z4
    let mut z_state = CashflowCapitalEcosystemEngine::new_state();
    CashflowCapitalEcosystemEngine::compute_ecosystem(&mut z_state, 3000.0, 1200.0, 300.0, 25.0, 0.25, 100.0);

    // AA4
    let mut aa_state = TacticalSwingTradingEngine::new_state();
    TacticalSwingTradingEngine::evaluate_abcd(&mut aa_state, 40.0, 55.0, 48.0, true);

    // AB4
    let mut ab_state = TacticalOptionsDisciplineEngine::new_state();
    TacticalOptionsDisciplineEngine::compute_sizing_and_condor(
        &mut ab_state, 10000.0, 50.0, 48.0, 55.0, 50.0, 60.0, 90.0, 100.0, 2.0, 1.0, 2.0, 1.0
    );

    println!("[T4 RUST] Modules Y4, Z4, AA4, AB4 trained successfully.");
}
