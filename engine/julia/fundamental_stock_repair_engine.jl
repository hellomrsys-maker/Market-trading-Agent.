module FundamentalStockRepairEngineModule

export FundamentalStockRepairState, evaluate_repair

struct FundamentalStockRepairState
    pe_ratio::Float64
    peg_ratio::Float64
    debt_to_assets_ratio::Float64
    repair_long_strike::Float64
    repair_short_strike::Float64
    cash_reserve_pct::Float64
    sec_material_flag::UInt32
    use_naked_over_spread::UInt32
    is_repair_recommended::UInt32
    pad1::UInt32
end

function evaluate_repair(price::Float64, cost_basis::Float64, vix::Float64, cash_pct::Float64)
    use_naked = vix >= 20.0 ? UInt32(1) : UInt32(0)
    drop_pct = ((cost_basis - price) / cost_basis) * 100.0
    if drop_pct >= 15.0 && drop_pct <= 25.0
        return FundamentalStockRepairState(
            0.0, 0.0, 0.0, price, price + ((cost_basis - price) / 2.0),
            cash_pct, UInt32(0), use_naked, UInt32(1), UInt32(0)
        )
    else
        return FundamentalStockRepairState(
            0.0, 0.0, 0.0, 0.0, 0.0,
            cash_pct, UInt32(0), use_naked, UInt32(0), UInt32(0)
        )
    end
end

end
