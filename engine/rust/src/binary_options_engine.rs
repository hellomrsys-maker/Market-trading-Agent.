// engine/rust/src/binary_options_engine.rs
// OptionAlpha Agent — Module S4: Rust Binary Options & Volatility Strangle Engine

pub struct BinaryOptionsEngineRust;

impl BinaryOptionsEngineRust {
    pub fn collateral_and_payout(is_long: bool, premium: f64, contracts: usize) -> (f64, f64, f64) {
        let n = contracts as f64;
        let (collateral, max_profit) = if is_long {
            (premium * n, (100.0 - premium) * n)
        } else {
            ((100.0 - premium) * n, premium * n)
        };
        let rr_ratio = max_profit / collateral.max(1e-4);
        (collateral, max_profit, rr_ratio)
    }

    pub fn short_volatility_strangle(high_ask: f64, low_bid: f64, contracts: usize) -> (f64, f64, f64) {
        let n = contracts as f64;
        let long_cost = low_bid;
        let short_collateral = 100.0 - high_ask;
        let total_collateral = (long_cost + short_collateral) * n;
        let max_profit = (200.0 * n) - total_collateral;

        let upper_loss = short_collateral - (100.0 - long_cost);
        let lower_loss = long_cost - (100.0 - short_collateral);
        let max_loss = upper_loss.abs().max(lower_loss.abs()) * n;

        (total_collateral, max_profit, max_loss)
    }
}
