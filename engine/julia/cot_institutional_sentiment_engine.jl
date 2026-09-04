# Module AM5 (Julia): COT Institutional Positioning & Sentiment Engine
# Quantitative evaluation of COT percentile rankings and volume/OI dynamics.

module CotInstitutionalSentimentEngine

export calculate_cot_index, evaluate_price_oi

function calculate_cot_index(current_net::Float64, min_net::Float64, max_net::Float64)
    rng = max(1.0, max_net - min_net)
    idx = clamp(((current_net - min_net) / rng) * 100.0, 0.0, 100.0)
    is_extreme = idx >= 90.0 || idx <= 10.0
    status = idx >= 90.0 ? "EXTREME_BULLISH" : (idx <= 10.0 ? "EXTREME_BEARISH" : "NEUTRAL")
    return (cot_index = idx, is_extreme = is_extreme, status = status)
end

function evaluate_price_oi(price_change::Float64, oi_change::Float64)
    if price_change > 0 && oi_change > 0
        regime = "STRONG_BULLISH"
    elseif price_change > 0 && oi_change <= 0
        regime = "WEAK_BULLISH"
    elseif price_change < 0 && oi_change > 0
        regime = "STRONG_BEARISH"
    else
        regime = "WEAK_BEARISH"
    end
    return regime
end

end
