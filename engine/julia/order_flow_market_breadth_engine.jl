module OrderFlowMarketBreadthEngineModule

export OrderFlowMarketBreadthState, audit_breadth

struct OrderFlowMarketBreadthState
    mcclellan_oscillator::Float64
    mcclellan_summation::Float64
    arms_trin_ratio::Float64
    chaikin_money_flow::Float64
    option_order_flow_vol::Float64
    flow_normal_ratio::Float64
    is_unusual_flow_detected::UInt32
    is_tko_breakout::UInt32
    is_trin_extreme_fear::UInt32
    pad1::UInt32
end

function audit_breadth(daily_vol::Float64, avg_vol::Float64, adv_issues::Float64, dec_issues::Float64, adv_vol::Float64, dec_vol::Float64)
    flow_ratio = daily_vol / max(1.0, avg_vol)
    is_unusual = flow_ratio >= 5.0 ? UInt32(1) : UInt32(0)
    ad_ratio = adv_issues / max(1.0, dec_issues)
    vol_ratio = adv_vol / max(1.0, dec_vol)
    trin = ad_ratio / max(0.001, vol_ratio)
    is_extreme_fear = trin >= 1.50 ? UInt32(1) : UInt32(0)

    return OrderFlowMarketBreadthState(
        0.0, 0.0, trin, 0.0, daily_vol, flow_ratio,
        is_unusual, UInt32(0), is_extreme_fear, UInt32(0)
    )
end

end
