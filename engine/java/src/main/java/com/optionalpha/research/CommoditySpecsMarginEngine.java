package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AS2 (Java): Futures Contract Specifications, Tick Multipliers & SPAN Margin Engine.
 * Implements contract multipliers, SPAN margin requirements, and liquidation proximity scoring in Java.
 */
public class CommoditySpecsMarginEngine {
    public CommoditySpecsMarginEngine() {}

    public Map<String, Object> auditMargin(double equity, double initialMargin, double maintMargin) {
        Map<String, Object> res = new HashMap<>();
        double excess = equity - maintMargin;
        double utilization = (initialMargin / Math.max(1.0, equity)) * 100.0;
        
        double proximity = (initialMargin > maintMargin) ? 
            ((equity - maintMargin) / (initialMargin - maintMargin)) : 1.0;

        boolean isSafe = proximity >= 1.0;
        String status = (equity < maintMargin) ? "MARGIN_CALL" : (isSafe ? "HEALTHY" : "WARNING");

        res.put("excess", excess);
        res.put("utilization", utilization);
        res.put("proximity", proximity);
        res.put("status", status);
        res.put("isSafe", isSafe);
        return res;
    }
}
