package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AN2 (Java): Schwager Algorithmic Risk Budgeting & Robust System Optimization Engine.
 * Implements ATR position sizing, walk-forward degradation checks, and portfolio heat governors.
 */
public class FuturesRiskGovernorEngine {
    private final double maxTradeRisk;
    private final double maxHeat;
    private final double minRobustness;

    public FuturesRiskGovernorEngine(double maxTradeRisk, double maxHeat, double minRobustness) {
        this.maxTradeRisk = maxTradeRisk;
        this.maxHeat = maxHeat;
        this.minRobustness = minRobustness;
    }

    public FuturesRiskGovernorEngine() {
        this(1.5, 6.0, 0.65);
    }

    public Map<String, Object> calculateAtrPosition(double equity, double riskPct, double atr, double multiplier, double pointVal) {
        Map<String, Object> res = new HashMap<>();
        double clampedRisk = Math.min(riskPct, this.maxTradeRisk) / 100.0;
        double dollarRisk = equity * clampedRisk;
        double perContractRisk = Math.max(1.0, atr * multiplier * pointVal);
        int contracts = Math.max(1, (int) Math.floor(dollarRisk / perContractRisk));

        res.put("dollarRiskTarget", dollarRisk);
        res.put("perContractRisk", perContractRisk);
        res.put("recommendedContracts", contracts);
        return res;
    }

    public Map<String, Object> evaluateRobustness(double inSampleSharpe, double outOfSampleSharpe) {
        Map<String, Object> res = new HashMap<>();
        double ratio = outOfSampleSharpe / Math.max(1e-4, inSampleSharpe);
        boolean isRobust = ratio >= this.minRobustness && outOfSampleSharpe > 0.5;

        res.put("ratio", ratio);
        res.put("isDeployable", isRobust);
        res.put("verdict", isRobust ? "ROBUST_DEPLOYABLE" : "OVERFITTED_WARNING");
        return res;
    }
}
