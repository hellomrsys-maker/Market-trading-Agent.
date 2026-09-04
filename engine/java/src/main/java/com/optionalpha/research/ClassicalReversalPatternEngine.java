package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BA2 (Java): Classical Reversal Pattern Recognition Engine.
 * Implements Head & Shoulders and Double Top/Bottom detection and measured moves in Java.
 */
public class ClassicalReversalPatternEngine {
    private final double tolerancePct;

    public ClassicalReversalPatternEngine(double tolerancePct) {
        this.tolerancePct = tolerancePct;
    }

    public ClassicalReversalPatternEngine() {
        this(1.5);
    }

    public Map<String, Object> evaluateHeadAndShoulders(
        double ls, double head, double rs, double neckline, double spot, boolean isInverse
    ) {
        Map<String, Object> res = new HashMap<>();
        boolean valid = !isInverse ? (head > ls && head > rs) : (head < ls && head < rs);
        double height = Math.abs(head - neckline);
        double target = !isInverse ? (neckline - height) : (neckline + height);
        boolean breakout = !isInverse ? (spot < neckline) : (spot > neckline);

        res.put("valid", valid);
        res.put("target", target);
        res.put("breakout", breakout);
        return res;
    }

    public Map<String, Object> evaluateDoubleTopBottom(double p1, double p2, double neckline, double spot, boolean isBottom) {
        Map<String, Object> res = new HashMap<>();
        double avgPeak = (p1 + p2) / 2.0;
        double height = Math.abs(avgPeak - neckline);
        double target = !isBottom ? (neckline - height) : (neckline + height);
        boolean breakout = !isBottom ? (spot < neckline) : (spot > neckline);

        res.put("target", target);
        res.put("breakout", breakout);
        return res;
    }
}
