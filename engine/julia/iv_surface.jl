# ============================================================================
# engine/julia/iv_surface.jl
# OptionAlpha Agent — SVI Parametric Volatility Surface Model
#
# Implements Gatheral's SVI (Stochastic Volatility Inspired) surface model:
# w(k) = a + b * (rho * (k - m) + sqrt((k - m)^2 + sigma^2))
# where k = log(K/F) is log-moneyness, w is total implied variance.
# ============================================================================

module IVSurfaceModel

export SVIParameters, total_variance, implied_volatility, calibrate_svi_slice

struct SVIParameters
    a::Float64
    b::Float64
    rho::Float64
    m::Float64
    sigma::Float64
end

"""
    total_variance(p::SVIParameters, k::Float64)
Computes total implied variance w(k) = sigma_BS^2 * T
"""
function total_variance(p::SVIParameters, k::Float64)::Float64
    term = (k - p.m)
    w = p.a + p.b * (p.rho * term + sqrt(term^2 + p.sigma^2))
    return max(0.0001, w)
end

"""
    implied_volatility(p::SVIParameters, k::Float64, T::Float64)
Converts total variance to annualized Black-Scholes implied volatility.
"""
function implied_volatility(p::SVIParameters, k::Float64, T::Float64)::Float64
    w = total_variance(p, k)
    return sqrt(w / max(0.001, T))
end

"""
    calibrate_svi_slice(strikes::Vector{Float64}, ivs::Vector{Float64}, F::Float64, T::Float64)
Quick heuristic parameter estimation for an IV smile slice.
"""
function calibrate_svi_slice(strikes::Vector{Float64}, ivs::Vector{Float64}, F::Float64, T::Float64)::SVIParameters
    # Find ATM volatility
    atm_idx = argmin(abs.(strikes .- F))
    atm_iv = ivs[atm_idx]
    atm_var = (atm_iv^2) * T

    a = atm_var * 0.5
    b = 0.10
    rho = -0.35 # Typical equity negative skew
    m = 0.0
    sigma = 0.10

    return SVIParameters(a, b, rho, m, sigma)
end

end # module
