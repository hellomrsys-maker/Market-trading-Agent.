package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BG2 (Java): Forex Microstructure, Bladerunner 20-EMA & Carry Trade Engine.
 * Evaluates Bladerunner 20-EMA price action, rollover carry trade yields, and Kelly Criterion sizing in Java.
 */
public class BladerunnerCarryForexEngine {
    private final double maxKelly;

    public BladerunnerCarryForexEngine(double maxKelly) {
        this.maxKelly = maxKelly;
    }

    public BladerunnerCarryForexEngine() {
        this(0.25);
    }

    public Map<String, Object> evaluateBladerunner(double spot, double ema20, boolean rejected, boolean confirmed) {
        Map<String, Object> res = new HashMap<>();
        boolean above = spot > ema20;
        String polarity = above ? "BULLISH_ABOVE" : "BEARISH_BELOW";
        String signal = "WAIT";

        if (above && rejected && confirmed) signal = "ENTER_LONG";
        else if (!above && rejected && confirmed) signal = "ENTER_SHORT";

        res.put("polarity", polarity);
        res.put("signal", signal);
        return res;
    }

    public Map<String, Object> calculateCarry(double longRate, double shortRate, double units) {
        Map<String, Object> res = new HashMap<>();
        double diff = (longRate - shortRate) / 100.0;
        double dailyInterest = (diff * units) / 365.0;

        res.put("diff", diff);
        res.put("dailyInterest", dailyInterest);
        return res;
    }

    public Map<String, Object> calculateKelly(double winProb, double winLossRatio) {
        Map<String, Object> res = new HashMap<>();
        double w = Math.max(0.01, Math.min(0.99, winProb));
        double r = Math.max(0.01, winLossRatio);

        double kelly = w - ((1.0 - w) / r);
        double alloc = Math.max(0.0, Math.min(this.maxKelly, kelly));

        res.put("kelly", kelly);
        res.put("allocationPct", alloc * 100.0);
        return res;
    }
}
