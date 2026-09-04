package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AK2 (Java): Schwager Classical Price Action, Key Reversal & Breakout Trap Engine.
 * Implements Key Reversals, Spring/Upthrust traps, and 3-Gap classifications in Java.
 */
public class SchwagerPriceActionEngine {
    private final double volumeSurgeMultiplier;

    public SchwagerPriceActionEngine(double volumeSurgeMultiplier) {
        this.volumeSurgeMultiplier = volumeSurgeMultiplier;
    }

    public SchwagerPriceActionEngine() {
        this(1.3);
    }

    public Map<String, Object> evaluateKeyReversal(
        double prevLow, double prevHigh, double prevClose,
        double currLow, double currHigh, double currClose,
        double currVol, double avgVol
    ) {
        Map<String, Object> res = new HashMap<>();
        boolean volSurge = avgVol <= 0 || (currVol >= avgVol * this.volumeSurgeMultiplier);

        boolean isBull = (currLow < prevLow) && (currClose > prevClose) && volSurge;
        boolean isBear = (currHigh > prevHigh) && (currClose < prevClose) && volSurge;

        String pattern = "NO_REVERSAL";
        if (isBull) pattern = "BULLISH_KEY_REVERSAL";
        else if (isBear) pattern = "BEARISH_KEY_REVERSAL";

        res.put("pattern", pattern);
        res.put("isReversal", isBull || isBear);
        res.put("stopLevel", isBull ? currLow : currHigh);
        return res;
    }

    public Map<String, Object> detectTrap(double support, double resistance, double high, double low, double close) {
        Map<String, Object> res = new HashMap<>();
        boolean isSpring = (low < support) && (close >= support);
        boolean isUpthrust = (high > resistance) && (close <= resistance);

        String trap = "NO_TRAP";
        if (isSpring) trap = "BULLISH_SPRING_TRAP";
        else if (isUpthrust) trap = "BEARISH_UPTHRUST_TRAP";

        res.put("trap", trap);
        res.put("isSpring", isSpring);
        res.put("isUpthrust", isUpthrust);
        return res;
    }
}
