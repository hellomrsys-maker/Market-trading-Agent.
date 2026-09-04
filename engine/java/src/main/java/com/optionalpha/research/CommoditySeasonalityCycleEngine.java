package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AU2 (Java): Agricultural & Energy Seasonality Cycles & Weather Premium Engine.
 * Evaluates seasonal tendency cycles, weather shock multipliers, and old-crop/new-crop spreads in Java.
 */
public class CommoditySeasonalityCycleEngine {
    public CommoditySeasonalityCycleEngine() {}

    public Map<String, Object> evaluateSeasonality(double baseSeasonalScore, double weatherSeverity) {
        Map<String, Object> res = new HashMap<>();
        double adjusted = Math.max(-1.0, Math.min(1.0, baseSeasonalScore + (weatherSeverity * 0.5)));
        String regime = adjusted >= 0.5 ? "STRONG_BULL_SEASON" : (adjusted <= -0.5 ? "STRONG_BEAR_HARVEST" : "NEUTRAL");

        res.put("baseScore", baseSeasonalScore);
        res.put("adjustedScore", adjusted);
        res.put("regime", regime);
        return res;
    }

    public Map<String, Object> evaluateCropSpread(double oldCrop, double newCrop, double historicalMean) {
        Map<String, Object> res = new HashMap<>();
        double spread = oldCrop - newCrop;
        boolean inverted = spread > 0;
        String signal = (spread - historicalMean > 25.0) ? "ENTER_BULL_INVERSION" : "FAIR_VALUE";

        res.put("spread", spread);
        res.put("inverted", inverted);
        res.put("signal", signal);
        return res;
    }
}
