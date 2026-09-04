package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BB2 (Java): Bilateral & Continuation Geometric Pattern Engine.
 * Evaluates triangle geometries, flagpoles, and measured move continuation targets in Java.
 */
public class ContinuationGeometryPatternEngine {
    public ContinuationGeometryPatternEngine() {}

    public Map<String, Object> evaluateTriangle(double upperSlope, double lowerSlope, double baseHeight, double breakoutPrice, double spot) {
        Map<String, Object> res = new HashMap<>();
        String type;
        double target;
        boolean breakout;

        if (Math.abs(upperSlope) < 0.05 && lowerSlope > 0.05) {
            type = "ASCENDING_TRIANGLE";
            target = breakoutPrice + baseHeight;
            breakout = spot > breakoutPrice;
        } else if (Math.abs(lowerSlope) < 0.05 && upperSlope < -0.05) {
            type = "DESCENDING_TRIANGLE";
            target = breakoutPrice - baseHeight;
            breakout = spot < breakoutPrice;
        } else {
            type = "SYMMETRICAL_TRIANGLE";
            target = spot > breakoutPrice ? (breakoutPrice + baseHeight) : (breakoutPrice - baseHeight);
            breakout = Math.abs(spot - breakoutPrice) > 0.5;
        }

        res.put("type", type);
        res.put("target", target);
        res.put("breakout", breakout);
        return res;
    }

    public Map<String, Object> evaluateFlag(double flagStart, double flagPeak, double breakoutPrice, double spot, boolean isBull) {
        Map<String, Object> res = new HashMap<>();
        double height = Math.abs(flagPeak - flagStart);
        double target = isBull ? (breakoutPrice + height) : (breakoutPrice - height);
        boolean breakout = isBull ? (spot > breakoutPrice) : (spot < breakoutPrice);

        res.put("target", target);
        res.put("breakout", breakout);
        return res;
    }
}
