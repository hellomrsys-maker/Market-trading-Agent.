# Module AW5 (Julia): Volatility Edge Discovery & Realized vs. Implied Mispricing Engine
# Quantitative evaluation of IV-HV spreads, rolling IV rank cones, and mispricing regimes.

module VolatilityEdgeDiscoveryEngine

export evaluate_edge

function evaluate_edge(iv::Float64, hv::Float64, min_iv::Float64, max_iv::Float64)
    spread = iv - hv
    rng = max(1.0, max_iv - min_iv)
    rank = clamp(((iv - min_iv) / rng) * 100.0, 0.0, 100.0)

    is_expensive = spread >= 4.0 || rank >= 75.0
    is_cheap = spread <= -2.0 || rank <= 25.0
    regime = is_expensive ? "EXPENSIVE_SHORT_VOL" : (is_cheap ? "CHEAP_LONG_VOL" : "NEUTRAL")

    return (
        spread = spread,
        iv_rank = rank,
        regime = regime,
        is_expensive = is_expensive,
        is_cheap = is_cheap
    )
end

end
