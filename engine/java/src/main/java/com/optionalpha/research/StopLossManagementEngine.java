package com.optionalpha.research;

import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;

/**
 * OptionAlpha Agent — Module K2: Java Systematic 6-Type Stop Loss Management Engine
 */
public class StopLossManagementEngine {
    private static final Logger logger = Logger.getLogger(StopLossManagementEngine.class.getName());

    public Map<String, Double> computeAllStopLossLevels(
            double entryPrice, double targetPrice, double supportLevel, double atr, double riskPct, boolean isLong) {
        
        Map<String, Double> stops = new HashMap<>();
        
        // 1. Percentage
        stops.put("percentage_sl", isLong ? entryPrice * (1.0 - riskPct) : entryPrice * (1.0 + riskPct));
        // 2. Support / Resistance
        stops.put("sr_structural_sl", isLong ? supportLevel - 0.5 : supportLevel + 0.5);
        // 3. Volatility (ATR)
        stops.put("volatility_sl", isLong ? entryPrice - (atr * 1.5) : entryPrice + (atr * 1.5));
        // 4. 2:1 Risk-Reward
        double reward = Math.abs(targetPrice - entryPrice);
        stops.put("rr_2to1_sl", isLong ? entryPrice - (reward / 2.0) : entryPrice + (reward / 2.0));

        return stops;
    }
}
