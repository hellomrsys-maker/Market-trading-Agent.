module InstitutionalIronCondorEngineModule

export InstitutionalIronCondorState, configure_archetype

struct InstitutionalIronCondorState
    expected_price_gbm::Float64
    net_premium_credit::Float64
    max_risk_capital::Float64
    portfolio_delta::Float64
    portfolio_gamma::Float64
    portfolio_theta::Float64
    archetype_id::UInt32
    dte::UInt16
    is_iv_crush_target::UInt8
    is_martingale_valid::UInt8
    pad1::UInt64
end

function configure_archetype(archetype_id::Integer, spot::Float64, drift::Float64, sigma::Float64, time_years::Float64)
    expected_price = spot * exp(drift * time_years)
    is_martingale = abs(expected_price - spot) < 1.0 ? UInt8(1) : UInt8(0)
    is_iv_crush = archetype_id == 2 ? UInt8(1) : UInt8(0)

    return InstitutionalIronCondorState(
        expected_price, 0.0, 0.0, 0.0, 0.0, 0.0,
        UInt32(archetype_id), UInt16(30), is_iv_crush, is_martingale, UInt64(0)
    )
end

end
