# Module Z5 (Julia): Top-Down Cash Flow & Capital Ecosystem Engine
# Precision mathematical modeling of cashflow allocation, sinking fund amortizations, and leak litmus tests.

module CashflowCapitalEcosystemEngine

export calculate_ecosystem, sinking_fund_installment, leak_litmus_test

function sinking_fund_installment(target::Float64, periods::Int, buffer::Float64=0.10)
    if periods <= 0
        return target * (1.0 + buffer)
    end
    return (target * (1.0 + buffer)) / Float64(periods)
end

function calculate_ecosystem(income::Float64, fixed::Float64, variable::Float64, sinking::Float64, savings_ratio::Float64=0.20)
    total_essentials = fixed + variable + sinking
    workable = max(0.0, income - total_essentials)
    keep_alloc = workable * savings_ratio
    spend_alloc = max(0.0, workable - keep_alloc)
    
    return (
        total_income = income,
        workable_total = round(workable, digits=2),
        keep_savings = round(keep_alloc, digits=2),
        spend_discretionary = round(spend_alloc, digits=2)
    )
end

function leak_litmus_test(category::String, est_freq::Int, est_spend::Float64, act_freq::Int, act_spend::Float64)
    freq_diff = act_freq - est_freq
    spend_leak = act_spend - est_spend
    return (
        category = category,
        freq_diff = freq_diff,
        monetary_leak = round(spend_leak, digits=2),
        is_leaking = spend_leak > 0.0 || freq_diff > 0
    )
end

end # module
