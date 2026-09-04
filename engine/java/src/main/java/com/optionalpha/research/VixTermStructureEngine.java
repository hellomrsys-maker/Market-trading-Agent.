package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AG2 (Java): VIX Term Structure, Futures Roll Yield & Volatility ETP Arbitrage Engine.
 * Implements M1-M8 term structure modeling, roll yield extraction, and VVIX surge detection in Java.
 */
public class VixTermStructureEngine {
    private final double highVvixThreshold;

    public VixTermStructureEngine(double highVvixThreshold) {
        this.highVvixThreshold = highVvixThreshold;
    }

    public VixTermStructureEngine() {
        this(115.0);
    }

    public Map<String, Object> analyzeTermStructure(double spotVix, double m1Price, double m2Price, int deltaDays) {
        Map<String, Object> res = new HashMap<>();
        double slope = m2Price - m1Price;
        double basis = m1Price - spotVix;
        double rollYieldAnnual = ((m2Price - m1Price) / m1Price) * (365.0 / Math.max(1, deltaDays)) * 100.0;

        String regime;
        if (slope > 0.15) {
            regime = "CONTANGO";
        } else if (slope < -0.15) {
            regime = "BACKWARDATION";
        } else {
            regime = "FLAT";
        }

        res.put("spotVix", spotVix);
        res.put("m1Price", m1Price);
        res.put("slope", slope);
        res.put("basis", basis);
        res.put("rollYieldPct", rollYieldAnnual);
        res.put("regime", regime);
        return res;
    }

    public Map<String, Object> evaluateVvixTailRisk(double spotVix, double spotVvix) {
        Map<String, Object> res = new HashMap<>();
        boolean isElevated = spotVvix >= this.highVvixThreshold;
        String action = isElevated ? "BUY_VIX_CALL_SPREADS" : "STANDARD_HARVEST";

        res.put("spotVvix", spotVvix);
        res.put("isElevated", isElevated);
        res.put("action", action);
        return res;
    }
}
