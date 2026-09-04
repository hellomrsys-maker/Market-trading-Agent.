# engine/julia/pattern_recognition.jl
# OptionAlpha Agent — Julia Quantitative Candlestick & Price Action Statistical Classifier
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions

struct OHLCBar
    open::Float64
    high::Float64
    low::Float64
    close::Float64
end

function classify_reversal_patterns(b1::OHLCBar, b2::OHLCBar, b3::OHLCBar)
    b1_body = abs(b1.close - b1.open)
    b2_body = abs(b2.close - b2.open)
    b3_bull = b3.close > b3.open
    
    # Morning Star
    if b1.close < b1.open && b2_body < b1_body * 0.35 && b3_bull && b3.close >= b1.open - (b1_body * 0.40)
        return (pattern = :MORNING_STAR, direction = :BULLISH, confidence = 0.90)
    end
    
    # Evening Star
    if b1.close > b1.open && b2_body < b1_body * 0.35 && !b3_bull && b3.close <= b1.open + (b1_body * 0.40)
        return (pattern = :EVENING_STAR, direction = :BEARISH, confidence = 0.90)
    end
    
    # Engulfing
    if b2.close < b2.open && b3_bull && b3.open <= b2.close && b3.close >= b2.open
        return (pattern = :BULLISH_ENGULFING, direction = :BULLISH, confidence = 0.88)
    end
    
    if b2.close > b2.open && !b3_bull && b3.open >= b2.close && b3.close <= b2.open
        return (pattern = :BEARISH_ENGULFING, direction = :BEARISH, confidence = 0.88)
    end
    
    return (pattern = :NO_PATTERN, direction = :NEUTRAL, confidence = 0.50)
end
