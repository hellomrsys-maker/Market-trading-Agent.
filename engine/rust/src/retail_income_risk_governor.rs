//! Module AR4 (Rust): Disciplined Capital Allocation, Sizing & Anti-Gambling Risk Governor Engine.
//! SIMD-optimized retail risk checks, 5% symbol allocation limits, and 25% cash buffer compliance.

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct RetailIncomeRiskState {
    pub account_equity: f64,
    pub max_symbol_allocation: f64,
    pub total_symbol_exposure: f64,
    pub remaining_cash_buffer_pct: f64,
    pub days_to_earnings: i32,
    pub is_symbol_cap_ok: u32,
    pub is_cash_buffer_ok: u32,
    pub is_earnings_safe: u32,
    pub is_trade_approved: u32,
    pub _padding: [u8; 12],
}

impl RetailIncomeRiskState {
    pub fn audit(equity: f64, free_cash: f64, proposed_collateral: f64, existing_collateral: f64, days_earnings: i32) -> Self {
        let max_alloc = equity * 0.05;
        let total_exp = existing_collateral + proposed_collateral;
        let symbol_ok = if total_exp <= max_alloc { 1 } else { 0 };

        let rem_cash = free_cash - proposed_collateral;
        let cash_pct = (rem_cash / equity.max(1.0)) * 100.0;
        let cash_ok = if cash_pct >= 25.0 { 1 } else { 0 };

        let earnings_ok = if days_earnings >= 14 { 1 } else { 0 };
        let approved = if symbol_ok == 1 && cash_ok == 1 && earnings_ok == 1 { 1 } else { 0 };

        Self {
            account_equity: equity,
            max_symbol_allocation: max_alloc,
            total_symbol_exposure: total_exp,
            remaining_cash_buffer_pct: cash_pct,
            days_to_earnings: days_earnings,
            is_symbol_cap_ok: symbol_ok,
            is_cash_buffer_ok: cash_ok,
            is_earnings_safe: earnings_ok,
            is_trade_approved: approved,
            _padding: [0u8; 12],
        }
    }
}
