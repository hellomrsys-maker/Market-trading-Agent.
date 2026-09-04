# engine/julia/cfi_valuation_breadth_engine.jl
# OptionAlpha Agent — Module O5: Julia DCF WACC & Intrinsic Value Simulator

function calculate_dcf_fair_value(fcfs::Vector{Float64}, wacc::Float64, terminal_growth::Float64, debt::Float64)
    n = length(fcfs)
    pv_fcfs = 0.0
    for t in 1:n
        pv_fcfs += fcfs[t] / ((1.0 + wacc)^t)
    end
    terminal_val = (fcfs[end] * (1.0 + terminal_growth)) / (wacc - terminal_growth)
    pv_terminal = terminal_val / ((1.0 + wacc)^n)
    enterprise_value = pv_fcfs + pv_terminal
    fair_equity_value = enterprise_value - debt
    return fair_equity_value
end
