# engine/julia/calendar_simulations.jl
# OptionAlpha Agent — Julia Quantitative Calendar Spread Theta Differential & Term Structure PDE
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using SpecialFunctions

struct CalendarSpreadParams
    spot::Float64
    strike::Float64
    t_near::Float64
    t_far::Float64
    iv_near::Float64
    iv_far::Float64
    r::Float64
    net_debit::Float64
    multiplier::Int
end

function compute_calendar_theta_differential(p::CalendarSpreadParams)
    # BSM analytical theta for near and far legs
    d1_near = (log(p.spot / p.strike) + (p.r + 0.5 * p.iv_near^2) * p.t_near) / (p.iv_near * sqrt(p.t_near))
    d2_near = d1_near - p.iv_near * sqrt(p.t_near)
    n_d1_near = (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * d1_near^2)
    theta_near = (-(p.spot * n_d1_near * p.iv_near) / (2.0 * sqrt(p.t_near)) - p.r * p.strike * exp(-p.r * p.t_near) * 0.5 * erfc(-d2_near / sqrt(2.0))) / 365.0
    
    d1_far = (log(p.spot / p.strike) + (p.r + 0.5 * p.iv_far^2) * p.t_far) / (p.iv_far * sqrt(p.t_far))
    d2_far = d1_far - p.iv_far * sqrt(p.t_far)
    n_d1_far = (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * d1_far^2)
    theta_far = (-(p.spot * n_d1_far * p.iv_far) / (2.0 * sqrt(p.t_far)) - p.r * p.strike * exp(-p.r * p.t_far) * 0.5 * erfc(-d2_far / sqrt(2.0))) / 365.0
    
    # Net daily theta collected (Short near leg theta decays faster than long far leg)
    net_daily_theta = (abs(theta_near) - abs(theta_far)) * p.multiplier
    
    return (
        near_leg_theta_daily = theta_near,
        far_leg_theta_daily = theta_far,
        net_theta_daily_dollars = net_daily_theta,
        is_positive_theta_capture = net_daily_theta > 0.0
    )
end
