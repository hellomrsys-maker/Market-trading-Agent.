package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AI2 (Java): Institutional Volatility Edge & Expiration Microstructure Engine.
 * Implements strike pinning models, Vega/Theta risk budgeting, and probability of touch.
 */
public class VolatilityEdgeExpirationEngine {
    private final double vegaThetaMaxRatio;

    public VolatilityEdgeExpirationEngine(double vegaThetaMaxRatio) {
        this.vegaThetaMaxRatio = vegaThetaMaxRatio;
    }

    public VolatilityEdgeExpirationEngine() {
        this(3.5);
    }

    public Map<String, Object> calculatePinningForce(double spotPrice, double strikePrice, double dteDays, int openInterest) {
        Map<String, Object> res = new HashMap<>();
        double distance = Math.abs(spotPrice - strikePrice);
        double timeFactor = Math.exp(-Math.max(0.01, dteDays) * 2.0);
        double pullScore = (openInterest / ((distance * distance) + 1.0)) * timeFactor;
        boolean isCandidate = (distance < 2.0) && (dteDays <= 1.0) && (openInterest > 5000);

        res.put("pullScore", pullScore);
        res.put("isCandidate", isCandidate);
        return res;
    }

    public Map<String, Object> evaluateVegaThetaBudget(double vega, double theta) {
        Map<String, Object> res = new HashMap<>();
        double ratio = Math.abs(vega) / Math.max(1e-4, Math.abs(theta));
        boolean isBalanced = ratio <= this.vegaThetaMaxRatio;

        res.put("ratio", ratio);
        res.put("isBalanced", isBalanced);
        return res;
    }
}
