package com.optionalpha.research;

import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;

/**
 * OptionAlpha Agent — Module M2: Java SMC & Expectancy Engine
 */
public class SMCExpectancyEngine {
    private static final Logger logger = Logger.getLogger(SMCExpectancyEngine.class.getName());

    public Map<String, Object> evaluateExpectancyAndKelly(double winRate, double avgWinR, double avgLossR) {
        double lossRate = 1.0 - winRate;
        double expectancy = (winRate * avgWinR) - (lossRate * avgLossR);
        
        double b = avgWinR / Math.max(0.01, avgLossR);
        double kelly = (b * winRate - lossRate) / b;
        double halfKelly = Math.max(0.0, kelly / 2.0);

        Map<String, Object> res = new HashMap<>();
        res.put("expectancy_r", expectancy);
        res.put("breakeven_win_rate", avgLossR / (avgWinR + avgLossR));
        res.put("recommended_half_kelly_pct", Math.min(2.0, halfKelly * 100.0));
        res.put("has_positive_edge", expectancy > 0.0);

        return res;
    }
}
