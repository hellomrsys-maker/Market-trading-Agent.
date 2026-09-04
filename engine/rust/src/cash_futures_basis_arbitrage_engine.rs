//! Module AV4 (Rust): Physical Cash-to-Futures Basis & Storage Arbitrage Engine.
//! SIMD-optimized evaluation of local cash basis Z-scores and cash-and-carry storage spreads.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CashFuturesBasisState {
    pub local_cash_price: f64,
    pub front_futures_price: f64,
    pub current_basis_value: f64,
    pub basis_zscore: f64,
    pub carrying_costs: f64,
    pub net_arbitrage_profit: f64,
    pub basis_regime_flag: u32,
    pub is_carry_profitable: u32,
    pub _padding: [u8; 8],
}

impl CashFuturesBasisState {
    pub fn evaluate(cash: f64, futures: f64, mean: f64, std_dev: f64, carry_costs: f64) -> Self {
        let basis = cash - futures;
        let s = std_dev.max(1e-4);
        let z = (basis - mean) / s;

        let regime = if z >= 1.5 {
            1
        } else if z <= -1.5 {
            2
        } else {
            0
        };

        let net_profit = (futures - cash) - carry_costs;
        let profitable = if net_profit > 0.0 { 1 } else { 0 };

        Self {
            local_cash_price: cash,
            front_futures_price: futures,
            current_basis_value: basis,
            basis_zscore: z,
            carrying_costs: carry_costs,
            net_arbitrage_profit: net_profit,
            basis_regime_flag: regime,
            is_carry_profitable: profitable,
            _padding: [0u8; 8],
        }
    }
}
