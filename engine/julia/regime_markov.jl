# engine/julia/regime_markov.jl
# OptionAlpha Agent — Julia Quantitative Continuous Markov Regime Switching Matrix & Transition Dynamics
# Polyglot Pillar 2: Julia Quantitative Mathematics

using LinearAlgebra
using Distributions

# 4 Regimes: 1 = Neutral, 2 = Bull Trend, 3 = Bear Trend, 4 = High-IV Crisis
struct MarkovRegimeModel
    transition_matrix::Matrix{Float64} # 4x4 stochastic matrix
    regime_names::Vector{String}
end

function default_markov_regime_model()
    # High persistence across regimes with calibrated crisis transition probabilities
    P = [
        0.85  0.08  0.05  0.02;  # Neutral
        0.10  0.82  0.06  0.02;  # Bull Trend
        0.08  0.04  0.80  0.08;  # Bear Trend
        0.05  0.05  0.15  0.75   # High-IV Crisis
    ]
    return MarkovRegimeModel(P, ["Neutral", "Bull Trend", "Bear Trend", "High-IV Crisis"])
end

function compute_n_step_regime_forecast(model::MarkovRegimeModel, current_regime_idx::Int, steps::Int=5)
    # P_n = P^n
    P_n = model.transition_matrix^steps
    forecast_probs = P_n[current_regime_idx, :]
    return (
        steps = steps,
        probabilities = forecast_probs,
        most_likely_future_regime = model.regime_names[argmax(forecast_probs)]
    )
end
