package com.optionalpha.research;

import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;

/**
 * OptionAlpha Agent — Module J2: Java Option Buyer's Volatility & Milestone Trailing Engine
 */
public class OptionBuyingRulesEngine {
    private static final Logger logger = Logger.getLogger(OptionBuyingRulesEngine.class.getName());

    public Map<String, Object> evaluateOptionBuyOrder(
            boolean isTrend, boolean isConsolidation, double vix, double cashPrice, double triggerPrice) {
        
        Map<String, Object> decision = new HashMap<>();
        boolean approved = isTrend && !isConsolidation && (vix < 25.0) && (cashPrice >= triggerPrice);
        decision.put("approved", approved);
        decision.put("strike_recommendation", "IN_THE_MONEY_DEEP_GAMMA");
        decision.put("max_holding_days", 3);
        decision.put("risk_allocation_pct", 2.0); // max 2-3% capital risk

        return decision;
    }

    public double calculateDynamicTrailingSL(
            double entryPrice, double currentPrice, double t1, double t2, double initialSL) {
        if (currentPrice >= t2) {
            return t1; // SL at Target 1
        } else if (currentPrice >= t1) {
            return entryPrice; // SL at Cost
        }
        return initialSL;
    }
}
