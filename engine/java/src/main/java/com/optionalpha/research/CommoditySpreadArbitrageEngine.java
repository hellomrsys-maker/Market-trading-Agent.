package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AL2 (Java): Intermarket Commodity Processing & Calendar Spread Arbitrage Engine.
 * Implements 3:2:1 Energy Crack Spreads and Soybean Crush Spreads in Java.
 */
public class CommoditySpreadArbitrageEngine {
    private final double riskFreeRate;

    public CommoditySpreadArbitrageEngine(double riskFreeRate) {
        this.riskFreeRate = riskFreeRate;
    }

    public CommoditySpreadArbitrageEngine() {
        this(0.045);
    }

    public Map<String, Object> computeEnergy321Crack(double crudeOilPrice, double gasolinePrice, double heatingOilPrice) {
        Map<String, Object> res = new HashMap<>();
        double gasBarrel = gasolinePrice * 42.0;
        double hoBarrel = heatingOilPrice * 42.0;
        double revenue = (2.0 * gasBarrel) + (1.0 * hoBarrel);
        double cost = 3.0 * crudeOilPrice;

        double margin = (revenue - cost) / 3.0;
        String signal = margin >= 25.0 ? "SELL_CRACK_SPREAD" : (margin <= 10.0 ? "BUY_CRACK_SPREAD" : "HOLD");

        res.put("marginPerBarrel", margin);
        res.put("signal", signal);
        return res;
    }

    public Map<String, Object> computeSoybeanCrush(double soybeansBu, double mealTon, double oilLb) {
        Map<String, Object> res = new HashMap<>();
        double mealRev = mealTon * 2.2;
        double oilRev = oilLb * 11.0;
        double gpmCents = (mealRev + oilRev) - soybeansBu;
        String signal = gpmCents > 180.0 ? "REVERSE_CRUSH" : (gpmCents < 60.0 ? "ENTER_CRUSH" : "HOLD");

        res.put("gpmCents", gpmCents);
        res.put("gpmDollars", gpmCents / 100.0);
        res.put("signal", signal);
        return res;
    }
}
