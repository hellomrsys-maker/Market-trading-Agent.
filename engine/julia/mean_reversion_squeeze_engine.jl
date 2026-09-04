module MeanReversionSqueezeEngineModule

export MeanReversionSqueezeState, compute_pnr

struct MeanReversionSqueezeState
    pnr_threshold::Float64
    bollinger_upper::Float64
    bollinger_lower::Float64
    keltner_upper::Float64
    keltner_lower::Float64
    current_adx::Float64
    current_rsi::Float32
    current_atr::Float32
    dte::UInt16
    is_squeeze_active::UInt8
    is_pnr_breached::UInt8
    dmi_bullish_cross::UInt8
    dmi_bearish_cross::UInt8
    cut_50pct_loss::UInt8
    padding::UInt8
end

function compute_pnr(long_strike::Float64, short_strike::Float64, dte::Integer, atr::Real, current_price::Float64)
    pnr_offset = (long_strike * dte * atr) / 2000.0
    pnr_threshold = long_strike - pnr_offset
    is_breached = current_price < pnr_threshold ? UInt8(1) : UInt8(0)
    cut_loss = (is_breached == 1 && dte < 15) ? UInt8(1) : UInt8(0)

    return MeanReversionSqueezeState(
        pnr_threshold, 0.0, 0.0, 0.0, 0.0, 0.0,
        Float32(50.0), Float32(atr), UInt16(dte),
        UInt8(0), is_breached, UInt8(0), UInt8(0), cut_loss, UInt8(0)
    )
end

end
