module CrossMarketPdtEngineModule

export CrossMarketPdtState, audit_compliance

struct CrossMarketPdtState
    account_equity::Float64
    margin_borrowed::Float64
    forex_leverage::Float64
    futures_tick_value::Float64
    max_risk_per_trade::Float64
    current_drawdown_pct::Float64
    round_trips_5d::Int32
    pdt_restricted::Bool
end

function audit_compliance(state::CrossMarketPdtState, is_day_trade::Bool, proposed_risk::Float64)::Bool
    if state.current_drawdown_pct >= 0.10 return false end
    if proposed_risk > (state.account_equity * 0.05) return false end
    if state.account_equity < 25000.0 && is_day_trade && state.round_trips_5d >= 3
        return false
    end
    return true
end

end
