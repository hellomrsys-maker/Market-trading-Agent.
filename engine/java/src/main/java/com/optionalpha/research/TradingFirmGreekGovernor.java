package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AX2 (Java): Trading Firm Greek Inventory Governance & Vega/Gamma Risk Budgeting Engine.
 * Evaluates Greek inventory limits, gamma rent ratios, and vega risk budgets in Java.
 */
public class TradingFirmGreekGovernor {
    private final double maxDelta;
    private final double minRentRatio;
    private final double maxVegaPct;

    public TradingFirmGreekGovernor(double maxDelta, double minRentRatio, double maxVegaPct) {
        this.maxDelta = maxDelta;
        this.minRentRatio = minRentRatio;
        this.maxVegaPct = maxVegaPct;
    }

    public TradingFirmGreekGovernor() {
        this(50.0, 1.0, 8.0);
    }

    public Map<String, Object> auditInventory(
        double delta, double gamma, double theta, double vega,
        double spot, double ivAnnual, double equity
    ) {
        Map<String, Object> res = new HashMap<>();
        double dailySigma = ivAnnual / Math.sqrt(252.0);
        double dailyGammaCost = 0.5 * Math.abs(gamma) * (spot * spot) * (dailySigma * dailySigma);
        double rentRatio = Math.abs(theta) / Math.max(1e-4, dailyGammaCost);

        double vegaExposure = Math.abs(vega) * 100.0;
        double vegaPct = (vegaExposure / Math.max(1.0, equity)) * 100.0;

        boolean deltaOk = Math.abs(delta) <= this.maxDelta;
        boolean rentOk = rentRatio >= this.minRentRatio;
        boolean vegaOk = vegaPct <= this.maxVegaPct;
        boolean approved = deltaOk && rentOk && vegaOk;

        res.put("rentRatio", rentRatio);
        res.put("vegaPct", vegaPct);
        res.put("isApproved", approved);
        res.put("action", approved ? "GREEKS_BALANCED" : "REBALANCE_INVENTORY");
        return res;
    }
}
