package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BC2 (Java): Volume Spread Analysis & False Breakout / Trap Filter Engine.
 * Evaluates volume surge multipliers and Wyckoff Spring/Upthrust traps in Java.
 */
public class VolumeBreakoutTrapFilter {
    private final double minSurge;

    public VolumeBreakoutTrapFilter(double minSurge) {
        this.minSurge = minSurge;
    }

    public VolumeBreakoutTrapFilter() {
        this(1.50);
    }

    public Map<String, Object> evaluateVolume(double breakVol, double smaVol, boolean candleClosed) {
        Map<String, Object> res = new HashMap<>();
        double surgeRatio = breakVol / Math.max(1.0, smaVol);
        boolean confirmed = surgeRatio >= this.minSurge && candleClosed;

        res.put("surgeRatio", surgeRatio);
        res.put("confirmed", confirmed);
        return res;
    }

    public Map<String, Object> detectTrap(double keyLevel, double extremePrice, double closePrice, boolean isSupport) {
        Map<String, Object> res = new HashMap<>();
        boolean isTrap;
        if (isSupport) {
            isTrap = (extremePrice < keyLevel) && (closePrice >= keyLevel);
        } else {
            isTrap = (extremePrice > keyLevel) && (closePrice <= keyLevel);
        }

        res.put("isTrap", isTrap);
        res.put("action", isTrap ? "FADE_FALSE_BREAK" : "FOLLOW_TREND");
        return res;
    }
}
