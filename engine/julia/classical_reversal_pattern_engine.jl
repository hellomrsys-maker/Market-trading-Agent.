# Module BA5 (Julia): Classical Reversal Pattern Recognition Engine
# Quantitative evaluation of Head & Shoulders and Double Top/Bottom geometric formations.

module ClassicalReversalPatternEngine

export evaluate_head_and_shoulders, evaluate_double_top_bottom

function evaluate_head_and_shoulders(ls::Float64, head::Float64, rs::Float64, neckline::Float64, spot::Float64, is_inverse::Bool)
    valid = !is_inverse ? (head > ls && head > rs) : (head < ls && head < rs)
    height = abs(head - neckline)
    target = !is_inverse ? (neckline - height) : (neckline + height)
    breakout = !is_inverse ? (spot < neckline) : (spot > neckline)

    return (is_valid = valid, height = height, target = target, is_breakout = breakout)
end

function evaluate_double_top_bottom(p1::Float64, p2::Float64, neckline::Float64, spot::Float64, is_bottom::Bool)
    avg_peak = (p1 + p2) / 2.0
    height = abs(avg_peak - neckline)
    target = !is_bottom ? (neckline - height) : (neckline + height)
    breakout = !is_bottom ? (spot < neckline) : (spot > neckline)

    return (height = height, target = target, is_breakout = breakout)
end

end
