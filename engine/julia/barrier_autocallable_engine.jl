# engine/julia/barrier_autocallable_engine.jl
# OptionAlpha Agent — Module V5: Julia Barrier, Digital & Autocallable Engine

module BarrierAutocallableEngineJulia

using SpecialFunctions

export discrete_barrier_shift, digital_skew_correction

function normal_cdf(z::Float64)
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
end

function normal_pdf(z::Float64)
    return (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * z * z)
end

function discrete_barrier_shift(barrier::Float64, sigma::Float64, t_years::Float64, num_obs::Int, is_short::Bool)
    if num_obs == 0
        return barrier
    end
    dt = t_years / Float64(num_obs)
    factor = 0.5826 * sigma * sqrt(dt)
    return barrier * exp(is_short ? factor : -factor)
end

function digital_skew_correction(s::Float64, x::Float64, t::Float64, r::Float64, sigma::Float64, skew::Float64)
    sqrt_t = sqrt(max(1e-6, t))
    d1 = (log(s / x) + (r + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    vega = s * normal_pdf(d1) * sqrt_t
    bs_dig = exp(-r * t) * normal_cdf(d2)
    total_dig = bs_dig + vega * abs(skew)

    return (bs_digital=bs_dig, total_digital=total_dig)
end

end # module
