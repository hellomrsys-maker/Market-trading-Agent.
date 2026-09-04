package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AE2 (Java): Multi-Dimensional Spread, Ratio & Wing Engine.
 * Models Ratio spreads, Backspreads, and Butterfly pricing in Java.
 */
public class MultidimensionalSpreadWingEngine {

    public Map<String, Object> structure1x2CallRatioSpread(
            double k1Long, double k2Short, double longCallPrem, double shortCallPrem) {

        double netCash = (2.0 * shortCallPrem) - longCallPrem;
        double strikeDiff = k2Short - k1Long;
        double maxProfit = strikeDiff + netCash;
        double upsideBE = k2Short + maxProfit;
        double escapeStrike = k2Short + strikeDiff;

        Map<String, Object> res = new HashMap<>();
        res.put("spread_type", "CALL_RATIO_1X2");
        res.put("net_cash", Math.round(netCash * 100.0) / 100.0);
        res.put("max_profit", Math.round(maxProfit * 100.0) / 100.0);
        res.put("upside_breakeven", Math.round(upsideBE * 100.0) / 100.0);
        res.put("butterfly_escape_strike", escapeStrike);
        return res;
    }

    public Map<String, Object> structure2x1CallBackspread(
            double k1Short, double k2Long, double shortCallPrem, double longCallPrem) {

        double netCredit = shortCallPrem - (2.0 * longCallPrem);
        double strikeDiff = k2Long - k1Short;
        double maxLoss = Math.max(0.0, strikeDiff - netCredit);
        double upsideBE = k2Long + strikeDiff - netCredit;

        Map<String, Object> res = new HashMap<>();
        res.put("spread_type", "CALL_BACKSPREAD_2X1");
        res.put("net_credit", Math.round(netCredit * 100.0) / 100.0);
        res.put("max_loss", Math.round(maxLoss * 100.0) / 100.0);
        res.put("upside_breakeven", Math.round(upsideBE * 100.0) / 100.0);
        return res;
    }
}
