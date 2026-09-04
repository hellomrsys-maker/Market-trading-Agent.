# engine/julia/psychology_dynamics.jl
# OptionAlpha Agent — Julia Quantitative Trading Psychology Dynamics & Drawdown Sizing
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Statistics

struct PsychoState
    consecutive_wins::Int
    consecutive_losses::Int
    current_drawdown_pct::Float64
    base_risk_pct::Float64
end

function compute_disciplined_position_scale(p::PsychoState)
    scale = 1.0
    
    # Revenge trading damper (Mark Douglas Part II & IV)
    if p.consecutive_losses >= 3 || p.current_drawdown_pct > 0.05
        scale *= 0.50
    end
    
    # Overconfidence damper
    if p.consecutive_wins >= 4
        scale *= 0.75
    end
    
    effective_risk_pct = p.base_risk_pct * scale
    return (
        scale_multiplier = scale,
        effective_risk_pct = effective_risk_pct,
        state = scale < 1.0 ? :DEFENSIVE_DISCIPLINE : :OPTIMAL_FLOW
    )
end
