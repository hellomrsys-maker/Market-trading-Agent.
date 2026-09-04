# ============================================================================
# engine/julia/greeks_surface.jl
# OptionAlpha Agent — Higher-Order Greeks on IV Surface
#
# Computes higher-order sensitivities:
# - Vanna (dDelta/dVol)
# - Charm (dDelta/dTime)
# - Volga (dVega/dVol)
# ============================================================================

module SurfaceGreeks

using Distributions

export HigherOrderGreeks, compute_surface_greeks

struct HigherOrderGreeks
    delta::Float64
    gamma::Float64
    vega::Float64
    theta::Float64
    vanna::Float64
    charm::Float64
    volga::Float64
end

function compute_surface_greeks(
    spot::Float64,
    strike::Float64,
    T::Float64,
    iv::Float64,
    r::Float64 = 0.05,
    is_call::Bool = true
)::HigherOrderGreeks
    T = max(0.001, T)
    sigma = max(0.01, iv)

    d1 = (log(spot / strike) + (r + 0.5 * sigma^2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    dist = Normal(0, 1)
    pdf_d1 = pdf(dist, d1)
    cdf_d1 = cdf(dist, d1)
    cdf_d2 = cdf(dist, d2)

    if is_call
        delta = cdf_d1
        theta = (-spot * pdf_d1 * sigma / (2 * sqrt(T)) - r * strike * exp(-r * T) * cdf_d2) / 365.0
    else
        delta = cdf_d1 - 1.0
        theta = (-spot * pdf_d1 * sigma / (2 * sqrt(T)) + r * strike * exp(-r * T) * cdf(dist, -d2)) / 365.0
    end

    gamma = pdf_d1 / (spot * sigma * sqrt(T))
    vega = (spot * sqrt(T) * pdf_d1) / 100.0

    # Higher Order Greeks
    vanna = (-pdf_d1 * d2 / sigma) / 100.0
    charm = is_call ? 
        (-pdf_d1 * (2*r*T - d2*sigma*sqrt(T)) / (2*T*sigma*sqrt(T))) / 365.0 :
        (-pdf_d1 * (2*r*T - d2*sigma*sqrt(T)) / (2*T*sigma*sqrt(T))) / 365.0
    volga = (vega * d1 * d2 / sigma) / 100.0

    return HigherOrderGreeks(delta, gamma, vega, theta, vanna, charm, volga)
end

end # module
