package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AY2 (Java): Volatility Skew, Smile Geometry & Ratio Arbitrage Engine.
 * Evaluates strike skew slopes, term slopes, and Broken Wing Butterfly (BWB) structures in Java.
 */
public class VolatilitySkewArbitrageEngine {
    private final double steepSkewThreshold;

    public VolatilitySkewArbitrageEngine(double steepSkewThreshold) {
        this.steepSkewThreshold = steepSkewThreshold;
    }

    public VolatilitySkewArbitrageEngine() {
        this(0.25);
    }

    public Map<String, Object> evaluateSkew(double ivAtm, double ivPut25, double ivCall25, double iv30, double iv90) {
        Map<String, Object> res = new HashMap<>();
        double strikeSkew = (ivPut25 - ivCall25) / Math.max(1e-4, ivAtm);
        double termSlope = (iv90 - iv30) / Math.max(1e-4, iv30);
        boolean isSteep = strikeSkew >= this.steepSkewThreshold;

        res.put("strikeSkew", strikeSkew);
        res.put("termSlope", termSlope);
        res.put("isSteep", isSteep);
        return res;
    }

    public Map<String, Object> structureBwb(double k1, double k2, double k3, double c1, double c2, double c3) {
        Map<String, Object> res = new HashMap<>();
        double netCredit = (2.0 * c2) - c1 - c3;
        boolean zeroDownside = netCredit >= 0.0;

        res.put("netCredit", netCredit);
        res.put("zeroDownside", zeroDownside);
        return res;
    }
}
