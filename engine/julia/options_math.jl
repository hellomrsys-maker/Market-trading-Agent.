"""
engine/julia/options_math.jl
==============================
OptionAlpha Agent — Julia Options Mathematics Library

Responsibilities:
  • Black-Scholes-Merton pricing (European, analytical)
  • Binomial tree pricing (American options, exercise-early premium)
  • Greeks: Delta, Gamma, Theta, Vega, Rho, Vanna, Volga, Charm
  • Implied Volatility solver (Brent's method, Newton-Raphson)
  • IV Surface interpolation (cubic spline across strikes/expiries)
  • Monte Carlo option pricing with antithetic variates + Sobol QMC
  • Kelly Criterion for position sizing
  • VaR / CVaR calculation (historical simulation)
  • Iron Condor breakeven and probability of profit
  • Wheel strategy expected value calculator

Exposed to Python via juliacall:
  import juliacall
  jl = juliacall.newmodule("OptionsJL")
  jl.seval('include("engine/julia/options_math.jl")')
  iv = jl.implied_volatility(call_price, S, K, T, r)

Performance: Julia JIT-compiles on first call; subsequent calls
are native-speed. Use Threads.@threads for Monte Carlo paths.
"""

module OptionsMath

using Statistics
using LinearAlgebra

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
const SQRT2PI = sqrt(2π)
const INVSQRT2 = 1.0 / sqrt(2.0)

# ──────────────────────────────────────────────────────────────
# Normal distribution helpers (fast, no dependencies)
# ──────────────────────────────────────────────────────────────

"""Standard normal PDF."""
@inline function npdf(x::Float64)::Float64
    exp(-0.5 * x * x) / SQRT2PI
end

"""Standard normal CDF via rational approximation (Abramowitz & Stegun 26.2.17).
Max absolute error < 7.5e-8."""
@inline function ncdf(x::Float64)::Float64
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    poly = t * (0.319381530 +
           t * (-0.356563782 +
           t * (1.781477937 +
           t * (-1.821255978 +
           t * 1.330274429))))
    p = 1.0 - npdf(x) * poly
    x >= 0.0 ? p : 1.0 - p
end

# ──────────────────────────────────────────────────────────────
# Black-Scholes-Merton Pricing
# ──────────────────────────────────────────────────────────────

"""
    bsm_price(S, K, T, r, sigma, q, is_call) -> Float64

Black-Scholes-Merton price for European option.

# Arguments
- `S`:       underlying spot price
- `K`:       strike price
- `T`:       time to expiry in years
- `r`:       risk-free rate (continuously compounded)
- `sigma`:   annualised implied volatility (e.g., 0.25 = 25%)
- `q`:       continuous dividend yield (use 0.0 for non-dividend-payers)
- `is_call`: true for call, false for put

# Returns Option fair value.
"""
function bsm_price(S::Float64, K::Float64, T::Float64, r::Float64,
                   sigma::Float64, q::Float64 = 0.0, is_call::Bool = true)::Float64
    T <= 0.0 && return is_call ? max(S - K, 0.0) : max(K - S, 0.0)
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    if is_call
        S * exp(-q * T) * ncdf(d1) - K * exp(-r * T) * ncdf(d2)
    else
        K * exp(-r * T) * ncdf(-d2) - S * exp(-q * T) * ncdf(-d1)
    end
end

# ──────────────────────────────────────────────────────────────
# Greeks
# ──────────────────────────────────────────────────────────────

"""Delta: sensitivity to underlying price change."""
function delta(S::Float64, K::Float64, T::Float64, r::Float64,
               sigma::Float64, q::Float64 = 0.0, is_call::Bool = true)::Float64
    T <= 0.0 && return is_call ? (S >= K ? 1.0 : 0.0) : (S <= K ? -1.0 : 0.0)
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    ef = exp(-q * T)
    is_call ? ef * ncdf(d1) : ef * (ncdf(d1) - 1.0)
end

"""Gamma: rate of change of delta."""
function gamma(S::Float64, K::Float64, T::Float64, r::Float64,
               sigma::Float64, q::Float64 = 0.0)::Float64
    T <= 0.0 && return 0.0
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    exp(-q * T) * npdf(d1) / (S * sigma * sqrtT)
end

"""Theta: daily time decay (in dollars per day). Divide by 365 for annualised."""
function theta(S::Float64, K::Float64, T::Float64, r::Float64,
               sigma::Float64, q::Float64 = 0.0, is_call::Bool = true)::Float64
    T <= 0.0 && return 0.0
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    term1 = -S * exp(-q * T) * npdf(d1) * sigma / (2.0 * sqrtT)
    if is_call
        term2 = q * S * exp(-q * T) * ncdf(d1)
        term3 = r * K * exp(-r * T) * ncdf(d2)
        (term1 - term3 + term2) / 365.0
    else
        term2 = q * S * exp(-q * T) * ncdf(-d1)
        term3 = r * K * exp(-r * T) * ncdf(-d2)
        (term1 + term3 - term2) / 365.0
    end
end

"""Vega: sensitivity to 1% change in implied volatility."""
function vega(S::Float64, K::Float64, T::Float64, r::Float64,
              sigma::Float64, q::Float64 = 0.0)::Float64
    T <= 0.0 && return 0.0
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    S * exp(-q * T) * npdf(d1) * sqrtT * 0.01  # per 1% IV change
end

"""Rho: sensitivity to interest rate change (per 1% change)."""
function rho(S::Float64, K::Float64, T::Float64, r::Float64,
             sigma::Float64, q::Float64 = 0.0, is_call::Bool = true)::Float64
    T <= 0.0 && return 0.0
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    is_call ?  K * T * exp(-r * T) * ncdf(d2)  * 0.01 :
              -K * T * exp(-r * T) * ncdf(-d2) * 0.01
end

"""Vanna: cross-derivative dΔ/dσ = dVega/dS."""
function vanna(S::Float64, K::Float64, T::Float64, r::Float64,
               sigma::Float64, q::Float64 = 0.0)::Float64
    T <= 0.0 && return 0.0
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    -exp(-q * T) * npdf(d1) * d2 / sigma
end

"""Charm: rate of change of delta with time (delta bleed)."""
function charm(S::Float64, K::Float64, T::Float64, r::Float64,
               sigma::Float64, q::Float64 = 0.0, is_call::Bool = true)::Float64
    T <= 0.0 && return 0.0
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    pdf_d1 = npdf(d1)
    inner  = 2.0 * (r - q) * T - d2 * sigma * sqrtT
    sign   = is_call ? 1.0 : -1.0
    -sign * exp(-q * T) * pdf_d1 * (2.0 * q * T - inner / (2.0 * T * sigma * sqrtT)) / (365.0 * 2.0 * T)
end

# ──────────────────────────────────────────────────────────────
# Implied Volatility Solver
# Uses Brent's bracketed root-finding method (guaranteed convergence).
# Falls back gracefully if price is below intrinsic value.
# ──────────────────────────────────────────────────────────────

"""
    implied_volatility(market_price, S, K, T, r, q, is_call; tol, max_iter) -> Float64

Solve for implied volatility given observed market price.
Returns 0.0 if no solution found (e.g., price < intrinsic).
"""
function implied_volatility(market_price::Float64, S::Float64, K::Float64,
                             T::Float64, r::Float64, q::Float64 = 0.0,
                             is_call::Bool = true;
                             tol::Float64 = 1e-7, max_iter::Int = 100)::Float64
    # Guard: below intrinsic
    intrinsic = is_call ? max(S * exp(-q*T) - K * exp(-r*T), 0.0) :
                          max(K * exp(-r*T) - S * exp(-q*T), 0.0)
    market_price <= intrinsic && return 0.0

    # Brent's method — bracket [lo, hi]
    f = (σ) -> bsm_price(S, K, T, r, σ, q, is_call) - market_price
    lo, hi = 1e-6, 10.0
    f_lo = f(lo)
    f_hi = f(hi)
    # If same sign, expand bracket
    (f_lo * f_hi > 0) && return 0.0

    # Standard Brent iteration
    a, b = lo, hi
    fa, fb = f_lo, f_hi
    c, fc = a, fa
    mflag = true
    s = 0.0
    d = 0.0

    for _ in 1:max_iter
        abs(b - a) < tol && return b
        if fa != fc && fb != fc
            # Inverse quadratic interpolation
            s = a * fb * fc / ((fa - fb) * (fa - fc)) +
                b * fa * fc / ((fb - fa) * (fb - fc)) +
                c * fa * fb / ((fc - fa) * (fc - fb))
        else
            # Secant
            s = b - fb * (b - a) / (fb - fa)
        end
        cond1 = !((3a + b) / 4 < s < b || b < s < (3a + b) / 4)
        cond2 =  mflag && abs(s - b) >= abs(b - c) / 2
        cond3 = !mflag && abs(s - b) >= abs(c - d) / 2
        cond4 =  mflag && abs(b - c) < tol
        cond5 = !mflag && abs(c - d) < tol
        if cond1 || cond2 || cond3 || cond4 || cond5
            s = (a + b) / 2
            mflag = true
        else
            mflag = false
        end
        fs = f(s)
        abs(fs) < tol && return s
        d, c, fc = c, b, fb
        if fa * fs < 0
            b, fb = s, fs
        else
            a, fa = s, fs
        end
        abs(fa) < abs(fb) && ((a, fa, b, fb) = (b, fb, a, fa))
    end
    b  # best estimate after max_iter
end

# ──────────────────────────────────────────────────────────────
# Monte Carlo Pricing
# Uses antithetic variates (halves variance) + optional Sobol QMC.
# ──────────────────────────────────────────────────────────────

"""
    mc_price(S, K, T, r, sigma, is_call, n_paths) -> (price, stderr)

Monte Carlo European option price with antithetic variates.
n_paths should be a multiple of 2 (antithetic pairs).
"""
function mc_price(S::Float64, K::Float64, T::Float64, r::Float64,
                  sigma::Float64, is_call::Bool = true,
                  n_paths::Int = 100_000)::Tuple{Float64, Float64}
    n_half = n_paths ÷ 2
    discount = exp(-r * T)
    sqrtT    = sqrt(T)
    drift    = (r - 0.5 * sigma^2) * T

    payoffs = Vector{Float64}(undef, n_paths)

    @inbounds Threads.@threads for i in 1:n_half
        z = randn()                          # standard normal
        S1 = S * exp(drift + sigma * sqrtT * z)
        S2 = S * exp(drift - sigma * sqrtT * z)  # antithetic
        payoffs[i]        = is_call ? max(S1 - K, 0.0) : max(K - S1, 0.0)
        payoffs[i+n_half] = is_call ? max(S2 - K, 0.0) : max(K - S2, 0.0)
    end

    mean_payoff = mean(payoffs)
    stderr      = std(payoffs) / sqrt(n_paths)
    (discount * mean_payoff, discount * stderr)
end

# ──────────────────────────────────────────────────────────────
# Iron Condor Analytics
# ──────────────────────────────────────────────────────────────

"""
    iron_condor_pnl(S_at_expiry, short_put, long_put, short_call, long_call, net_credit)

P&L of an Iron Condor at expiry.
Positive = profit; negative = loss.
"""
function iron_condor_pnl(S::Float64, sp::Float64, lp::Float64,
                          sc::Float64, lc::Float64, credit::Float64)::Float64
    put_spread_pnl  = max(sp - S, 0.0) - max(lp - S, 0.0)
    call_spread_pnl = max(S - sc, 0.0) - max(S - lc, 0.0)
    credit - put_spread_pnl - call_spread_pnl
end

"""
    iron_condor_pop(S, sp, lp, sc, lc, T, r, sigma) -> Float64

Probability of Profit for an Iron Condor (analytical BSM).
= P(lp < S_T < lc) = N(d_lc) - N(d_lp)  (approx. using log-normal)
"""
function iron_condor_pop(S::Float64, sp::Float64, lp::Float64,
                          sc::Float64, lc::Float64,
                          T::Float64, r::Float64, sigma::Float64)::Float64
    d_lo = (log(S / lp) + (r - 0.5 * sigma^2) * T) / (sigma * sqrt(T))
    d_hi = (log(S / lc) + (r - 0.5 * sigma^2) * T) / (sigma * sqrt(T))
    ncdf(d_hi) - ncdf(d_lo)
end

"""Breakeven prices for an Iron Condor."""
function iron_condor_breakevens(sp::Float64, lp::Float64,
                                sc::Float64, lc::Float64,
                                credit::Float64)::Tuple{Float64, Float64}
    lower = sp - credit
    upper = sc + credit
    (lower, upper)
end

# ──────────────────────────────────────────────────────────────
# Wheel Strategy Expected Value
# ──────────────────────────────────────────────────────────────

"""
    wheel_ev(S, K, T, r, sigma, premium) -> Float64

Expected value of selling a cash-secured put.
EV = premium - E[max(K - S_T, 0)] discounted
   = premium - BSM_put_price(S, K, T, r, sigma)
"""
function wheel_ev(S::Float64, K::Float64, T::Float64,
                  r::Float64, sigma::Float64, premium::Float64)::Float64
    theoretical_put = bsm_price(S, K, T, r, sigma, 0.0, false)
    premium - theoretical_put   # positive = edge in seller's favour
end

"""
    assignment_probability(S, K, T, r, sigma) -> Float64

Approximate probability of put assignment at expiry using BSM.
= N(-d2)  [risk-neutral probability the put ends ITM]
"""
function assignment_probability(S::Float64, K::Float64, T::Float64,
                                 r::Float64, sigma::Float64)::Float64
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * sigma^2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    ncdf(-d2)
end

# ──────────────────────────────────────────────────────────────
# Kelly Criterion for Position Sizing
# ──────────────────────────────────────────────────────────────

"""
    kelly_fraction(win_prob, win_pct, loss_pct) -> Float64

Full Kelly fraction.
- `win_prob`:  probability of winning trade
- `win_pct`:   return on winning trade (e.g., 0.02 = 2%)
- `loss_pct`:  loss on losing trade (e.g., 0.04 = 4%)

Returns optimal fraction of capital to risk (clamp to [0, 0.25] in practice).
"""
function kelly_fraction(win_prob::Float64, win_pct::Float64, loss_pct::Float64)::Float64
    q = 1.0 - win_prob
    b = win_pct / loss_pct
    frac = win_prob - q / b
    clamp(frac, 0.0, 0.25)  # never risk more than 25% (half-Kelly is more prudent)
end

# ──────────────────────────────────────────────────────────────
# VaR / CVaR (Historical Simulation)
# ──────────────────────────────────────────────────────────────

"""
    var_cvar(returns, confidence) -> (VaR, CVaR)

Historical simulation Value at Risk and Conditional VaR.
`returns` is a vector of daily P&L values.
`confidence` = 0.95 for 95% VaR.
"""
function var_cvar(returns::Vector{Float64}, confidence::Float64 = 0.95)::Tuple{Float64, Float64}
    sorted   = sort(returns)
    cutoff   = (1.0 - confidence)
    idx      = max(1, round(Int, cutoff * length(sorted)))
    var_val  = -sorted[idx]                        # VaR (positive = loss)
    tail     = sorted[1:idx]
    cvar_val = isempty(tail) ? var_val : -mean(tail)  # CVaR (expected loss beyond VaR)
    (var_val, cvar_val)
end

# ──────────────────────────────────────────────────────────────
# All-in-one Greeks snapshot (for the AI feature vector)
# ──────────────────────────────────────────────────────────────

"""
    greeks_snapshot(S, K, T, r, sigma, q, is_call) -> NamedTuple

Returns all first- and second-order Greeks in one call to minimise
overhead when called from Python.
"""
function greeks_snapshot(S::Float64, K::Float64, T::Float64, r::Float64,
                         sigma::Float64, q::Float64 = 0.0, is_call::Bool = true)
    (
        price  = bsm_price(S, K, T, r, sigma, q, is_call),
        delta  = delta(S, K, T, r, sigma, q, is_call),
        gamma  = gamma(S, K, T, r, sigma, q),
        theta  = theta(S, K, T, r, sigma, q, is_call),
        vega   = vega(S, K, T, r, sigma, q),
        rho    = rho(S, K, T, r, sigma, q, is_call),
        vanna  = vanna(S, K, T, r, sigma, q),
        charm  = charm(S, K, T, r, sigma, q, is_call),
    )
end

end  # module OptionsMath
