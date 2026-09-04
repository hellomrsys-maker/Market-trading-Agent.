#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CrossMarketPdtState {
    pub account_equity: f64,
    pub margin_borrowed: f64,
    pub forex_leverage_ratio: f64,
    pub futures_tick_value: f64,
    pub max_risk_per_trade: f64,
    pub current_drawdown_pct: f64,
    pub round_trips_5d: u32,
    pub asset_class_id: u16,
    pub pdt_restricted: u8,
    pub circuit_breaker_tripped: u8,
    pub _padding: [u8; 8],
}

impl CrossMarketPdtState {
    pub fn new(equity: f64) -> Self {
        Self {
            account_equity: equity,
            margin_borrowed: 0.0,
            forex_leverage_ratio: 100.0,
            futures_tick_value: 12.50,
            max_risk_per_trade: equity * 0.03,
            current_drawdown_pct: 0.0,
            round_trips_5d: 0,
            asset_class_id: 1,
            pdt_restricted: 0,
            circuit_breaker_tripped: 0,
            _padding: [0; 8],
        }
    }
}
