package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module Q2: Java Dynamic Weekly Squeeze & Heikin Ashi Engine
 * Strict Enterprise State and Verification Governance.
 */
public class WeeklySqueezeEngine {

    public static class HeikinAshiBar {
        public double open;
        public double high;
        public double low;
        public double close;
        public boolean isStrongBull;
        public boolean isStrongBear;
        public String color;

        public HeikinAshiBar(double o, double h, double l, double c, double prevO, double prevC) {
            this.open = (prevO + prevC) / 2.0;
            this.close = (o + h + l + c) / 4.0;
            this.high = Math.max(h, Math.max(this.open, this.close));
            this.low = Math.min(l, Math.min(this.open, this.close));
            this.isStrongBull = (this.close > this.open) && (Math.abs(this.low - this.open) < 1e-4);
            this.isStrongBear = (this.close < this.open) && (Math.abs(this.high - this.open) < 1e-4);
            this.color = (this.close >= this.open) ? "WHITE" : "RED";
        }
    }

    public static boolean checkSqueeze(double bbUpper, double bbLower, double keltnerUpper, double keltnerLower) {
        return (bbUpper < keltnerUpper) && (bbLower > keltnerLower);
    }

    public static double get50PctMidpoint(double openP, double closeP) {
        return (openP + closeP) / 2.0;
    }

    public static Map<String, Object> evaluateWeeklySetup(
        double bbUpper, double bbLower, double keltnerUpper, double keltnerLower,
        double ema13, double ema21, double ema55,
        HeikinAshiBar currentBar, HeikinAshiBar prevBar
    ) {
        boolean inSqueeze = checkSqueeze(bbUpper, bbLower, keltnerUpper, keltnerLower);
        boolean bullTrend = (ema13 > ema21) && (ema21 > ema55);
        boolean bearTrend = (ema13 < ema21) && (ema21 < ema55);

        boolean longSignal = currentBar.isStrongBull && prevBar.isStrongBull && bullTrend;
        boolean shortSignal = currentBar.isStrongBear && prevBar.isStrongBear && bearTrend;

        Map<String, Object> res = new HashMap<>();
        res.put("inSqueeze", inSqueeze);
        res.put("longSignal", longSignal);
        res.put("shortSignal", shortSignal);
        res.put("recommendedAction", longSignal ? "ENTER_PUT_CREDIT_SPREAD_AT_MIDPOINT" : (shortSignal ? "ENTER_CALL_CREDIT_SPREAD_AT_MIDPOINT" : "WAIT_FOR_SETUP"));
        return res;
    }
}
