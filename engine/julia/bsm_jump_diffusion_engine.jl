# engine/julia/bsm_jump_diffusion_engine.jl
# OptionAlpha Agent — Module R5: Julia BSM & Jump-Diffusion Engine

module BSMJumpDiffusionEngineJulia

using SpecialFunctions

export price_merton_bsm, probability_ever_itm

function normal_cdf(z::Float64)
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
end

function price_merton_bsm(s::Float64, x::Float64, t::Float64, r::Float64, sigma::Float64, q::Float64)
    sqrt_t = sqrt(max(1e-6, t))
    d1 = (log(s / x) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    nd1 = normal_cdf(d1)
    nd2 = normal_cdf(d2)
    exp_qt = exp(-q * t)
    exp_rt = exp(-r * t)

    call = s * exp_qt * nd1 - x * exp_rt * nd2
    put = x * exp_rt * normal_cdf(-d2) - s * exp_qt * normal_cdf(-d1)
    delta_call = exp_qt * nd1
    elasticity = (s * delta_call) / max(1e-4, call)

    return (call=call, put=put, d1=d1, d2=d2, delta=delta_call, elasticity=elasticity)
end

function probability_ever_itm(s::Float64, x::Float64, t::Float64, r::Float64, sigma::Float64, q::Float64)
    if s >= x
        return 1.0
    end
    sqrt_t = sqrt(max(1e-6, t))
    d2 = (log(s / x) + (r - q - 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
    b = (1.0 / sigma) * log(x / s)
    a = (1.0 / sigma) * (r - q - 0.5 * sigma * sigma)

    p_ever = normal_cdf(d2) + exp(2.0 * a * b) * normal_cdf(d2 - 2.0 * a * sqrt_t)
    return min(1.0, max(0.0, p_ever))
end

end # module
