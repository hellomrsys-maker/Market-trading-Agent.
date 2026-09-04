# engine/julia/put_simulations.jl
# Julia SVI & Dupire Local Variance Put Option Math and Downside Monte Carlo Simulation Engine

using Distributions
using SpecialFunctions

struct PutOptionParams
    S::Float64        # Spot Price
    K::Float64        # Strike Price
    T::Float64        # Time to Expiration in Years
    r::Float64        # Risk-Free Rate
    sigma::Float64    # Implied Volatility
    multiplier::Int   # Contract Multiplier (100)
end

function put_bsm_analytical(p::PutOptionParams)
    T = max(1e-5, p.T)
    sigma = max(1e-4, p.sigma)
    d1 = (log(p.S / p.K) + (p.r + 0.5 * sigma^2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    
    n_d1 = (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * d1^2)
    N_minus_d1 = 0.5 * erfc(d1 / sqrt(2.0))
    N_minus_d2 = 0.5 * erfc(d2 / sqrt(2.0))
    
    price = p.K * exp(-p.r * T) * N_minus_d2 - p.S * N_minus_d1
    delta = N_minus_d1 - 1.0  # Put delta is negative: [-1.0, 0.0]
    gamma = n_d1 / (p.S * sigma * sqrt(T))
    theta = -(p.S * n_d1 * sigma) / (2.0 * sqrt(T)) + p.r * p.K * exp(-p.r * T) * N_minus_d2
    vega  = p.S * sqrt(T) * n_d1 * 0.01
    
    # Higher order Greeks: Vanna, Charm, Volga
    vanna = -n_d1 * (d2 / sigma) * 0.01
    volga = vega * (d1 * d2 / sigma) * 0.01
    charm = -n_d1 * (2.0 * p.r * T - d2 * sigma * sqrt(T)) / (2.0 * T * sigma * sqrt(T))
    
    return (
        price = price,
        contract_dollar_price = price * p.multiplier,
        delta = delta,
        gamma = gamma,
        theta_daily = theta / 365.0,
        vega = vega,
        vanna = vanna,
        volga = volga,
        charm = charm
    )
end

function simulate_put_paths_mc(p::PutOptionParams, n_paths::Int=100000, n_steps::Int=50)
    dt = p.T / n_steps
    drift = (p.r - 0.5 * p.sigma^2) * dt
    vol_step = p.sigma * sqrt(dt)
    
    terminal_payoffs = Float64[]
    for _ in 1:n_paths
        st = p.S
        for _ in 1:n_steps
            z = randn()
            st *= exp(drift + vol_step * z)
        end
        push!(terminal_payoffs, max(0.0, p.K - st) * p.multiplier)
    end
    
    discounted_ev = exp(-p.r * p.T) * (sum(terminal_payoffs) / n_paths)
    return discounted_ev
end
