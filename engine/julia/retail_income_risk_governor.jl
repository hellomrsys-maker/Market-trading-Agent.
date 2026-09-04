# Module AR5 (Julia): Disciplined Capital Allocation, Sizing & Anti-Gambling Risk Governor Engine
# Precision auditing of portfolio cash buffers, 5% symbol limits, and earnings safety windows.

module RetailIncomeRiskGovernor

export audit_trade

function audit_trade(equity::Float64, free_cash::Float64, proposed_collateral::Float64, existing_collateral::Float64, days_earnings::Int)
    max_alloc = equity * 0.05
    total_exp = existing_collateral + proposed_collateral
    symbol_ok = total_exp <= max_alloc

    rem_cash = free_cash - proposed_collateral
    cash_pct = (rem_cash / max(1.0, equity)) * 100.0
    cash_ok = cash_pct >= 25.0

    earnings_ok = days_earnings >= 14
    approved = symbol_ok && cash_ok && earnings_ok

    return (
        is_approved = approved,
        cash_pct = cash_pct,
        max_allowed = max_alloc
    )
end

end
