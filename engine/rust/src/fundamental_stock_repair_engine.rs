#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct FundamentalStockRepairState {
    pub pe_ratio: f64,
    pub peg_ratio: f64,
    pub debt_to_assets_ratio: f64,
    pub repair_long_strike: f64,
    pub repair_short_strike: f64,
    pub cash_reserve_pct: f64,
    pub sec_material_flag: u32,
    pub use_naked_over_spread: u32,
    pub is_repair_recommended: u32,
    pub padding: [u8; 4],
}

pub struct FundamentalStockRepairEngine;

impl FundamentalStockRepairEngine {
    pub fn evaluate_repair(
        price: f64,
        cost_basis: f64,
        vix: f64,
        cash_pct: f64
    ) -> FundamentalStockRepairState {
        let use_naked_over_spread = if vix >= 20.0 { 1 } else { 0 };
        let drop_pct = ((cost_basis - price) / cost_basis) * 100.0;
        let (is_repair_recommended, repair_long_strike, repair_short_strike) =
            if drop_pct >= 15.0 && drop_pct <= 25.0 {
                (1, price, price + ((cost_basis - price) / 2.0))
            } else {
                (0, 0.0, 0.0)
            };

        FundamentalStockRepairState {
            pe_ratio: 0.0,
            peg_ratio: 0.0,
            debt_to_assets_ratio: 0.0,
            repair_long_strike,
            repair_short_strike,
            cash_reserve_pct: cash_pct,
            sec_material_flag: 0,
            use_naked_over_spread,
            is_repair_recommended,
            padding: [0; 4],
        }
    }
}
