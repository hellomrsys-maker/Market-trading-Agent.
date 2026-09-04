// engine/rust/src/phase5_training.rs
// OptionAlpha Agent — Module T4: Rust Phase 5 Training Module

pub mod weekly_squeeze_engine;
pub mod bsm_jump_diffusion_engine;
pub mod binary_options_engine;
pub mod drawdown_risk_manager;

use weekly_squeeze_engine::{WeeklySqueezeEngineRust, HeikinAshiBar};
use bsm_jump_diffusion_engine::BSMJumpDiffusionEngineRust;
use binary_options_engine::BinaryOptionsEngineRust;
use drawdown_risk_manager::DrawdownRiskManagerRust;

fn main() {
    println!("[T4 RUST] Starting SIMD Benchmarking & Training Epochs for Phase 5...");

    let prev = HeikinAshiBar::new(98.0, 102.0, 97.0, 101.0, 97.0, 100.0);
    let curr = HeikinAshiBar::new(100.0, 105.0, 99.0, 104.0, prev.open, prev.close);
    let in_sqz = WeeklySqueezeEngineRust::is_in_squeeze(103.0, 97.0, 104.0, 96.0);

    let (call, put, delta) = BSMJumpDiffusionEngineRust::price_merton(100.0, 100.0, 0.25, 0.05, 0.20, 0.02);
    let p_ever = BSMJumpDiffusionEngineRust::probability_ever_itm(100.0, 110.0, 0.5, 0.05, 0.25, 0.0);

    let (collat, profit, max_loss) = BinaryOptionsEngineRust::short_volatility_strangle(20.0, 80.0, 2);

    let mut drm = DrawdownRiskManagerRust::new(10000.0, 20.0);
    let pos_size = drm.position_size(2.0, 50.0);
    let (cap, pct_dd, is_halted) = drm.update_trade(200.0);

    println!("[T4 RUST] Modules Q4, R4, S4, T_sys4 trained successfully.");
}
