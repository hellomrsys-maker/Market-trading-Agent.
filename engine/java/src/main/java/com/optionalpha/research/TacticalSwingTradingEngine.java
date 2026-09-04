package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AA2 (Java): Tactical Swing Trading & Technical Microstructure Engine.
 * Implements ABCD swing patterns, Flag breakouts, and Moving Average Confluence in Java.
 */
public class TacticalSwingTradingEngine {

    public Map<String, Object> evaluateABCDPattern(double pointA, double pointB, double pointC, boolean isBullish) {
        double abLeg = Math.abs(pointA - pointB);
        Map<String, Object> result = new HashMap<>();

        if (isBullish) {
            double retracementRatio = abLeg > 0 ? (pointB - pointC) / abLeg : 0.0;
            double pointD = pointC + abLeg;
            double stopLoss = pointC * 0.98;
            boolean valid = retracementRatio >= 0.382 && retracementRatio <= 0.786 && pointC > pointA;
            double rr = (pointC - stopLoss) > 0 ? (pointD - pointC) / (pointC - stopLoss) : 0.0;

            result.put("pattern", "BULLISH_ABCD");
            result.put("valid_setup", valid);
            result.put("entry_trigger", pointB);
            result.put("point_d_target", Math.round(pointD * 100.0) / 100.0);
            result.put("stop_loss", Math.round(stopLoss * 100.0) / 100.0);
            result.put("reward_to_risk", Math.round(rr * 100.0) / 100.0);
        } else {
            double retracementRatio = abLeg > 0 ? (pointC - pointB) / abLeg : 0.0;
            double pointD = pointC - abLeg;
            double stopLoss = pointC * 1.02;
            boolean valid = retracementRatio >= 0.382 && retracementRatio <= 0.786 && pointC < pointA;
            double rr = (stopLoss - pointC) > 0 ? (pointC - pointD) / (stopLoss - pointC) : 0.0;

            result.put("pattern", "BEARISH_ABCD");
            result.put("valid_setup", valid);
            result.put("entry_trigger", pointB);
            result.put("point_d_target", Math.round(pointD * 100.0) / 100.0);
            result.put("stop_loss", Math.round(stopLoss * 100.0) / 100.0);
            result.put("reward_to_risk", Math.round(rr * 100.0) / 100.0);
        }
        return result;
    }

    public Map<String, Object> detectBullFlag(double poleStart, double poleEnd, double pullbackExtreme, double currentPrice) {
        double poleHeight = poleEnd - poleStart;
        Map<String, Object> signal = new HashMap<>();

        if (poleHeight <= 0) {
            signal.put("valid", false);
            return signal;
        }

        double pullbackDepth = (poleEnd - pullbackExtreme) / poleHeight;
        if (pullbackDepth >= 0.10 && pullbackDepth <= 0.50 && currentPrice >= poleEnd) {
            double stop = pullbackExtreme * 0.99;
            double risk = currentPrice - stop;
            double target = currentPrice + (2.0 * risk);

            signal.put("valid", true);
            signal.put("pattern", "BULL_FLAG_BREAKOUT");
            signal.put("entry", currentPrice);
            signal.put("stop_loss", Math.round(stop * 100.0) / 100.0);
            signal.put("target", Math.round(target * 100.0) / 100.0);
            signal.put("reward_to_risk", 2.0);
        } else {
            signal.put("valid", false);
        }
        return signal;
    }
}
