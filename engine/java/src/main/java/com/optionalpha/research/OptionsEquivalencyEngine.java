package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AC2 (Java): Options Equivalency, Synthetics & Arbitrage Engine.
 * Implements Put-Call parity, basis arithmetic, and conversion/reversal arbitrage in Java.
 */
public class OptionsEquivalencyEngine {

    public Map<String, Double> computeBasis(double stockPrice, double interestRate, int daysToExp, double dividend) {
        double t = (double) daysToExp / 360.0;
        double carry = stockPrice * interestRate * t;
        double basis = carry - dividend;
        double fwd = stockPrice + basis;

        Map<String, Double> res = new HashMap<>();
        res.put("carry", Math.round(carry * 10000.0) / 10000.0);
        res.put("basis", Math.round(basis * 10000.0) / 10000.0);
        res.put("forward_price", Math.round(fwd * 10000.0) / 10000.0);
        return res;
    }

    public Map<String, Object> evaluatePutCallParity(
            double stockPrice, double strikePrice,
            double callPrice, double putPrice,
            double interestRate, int daysToExp, double dividend) {

        double t = (double) daysToExp / 360.0;
        double carry = stockPrice * interestRate * t;
        double basis = carry - dividend;

        double theoreticalStock = callPrice - putPrice + strikePrice - basis;
        double synthCall = stockPrice - strikePrice + putPrice + basis;
        double synthPut = callPrice + strikePrice - stockPrice - basis;

        Map<String, Object> out = new HashMap<>();
        out.put("actual_stock", stockPrice);
        out.put("theoretical_stock", Math.round(theoreticalStock * 100.0) / 100.0);
        out.put("synthetic_call", Math.round(synthCall * 100.0) / 100.0);
        out.put("synthetic_put", Math.round(synthPut * 100.0) / 100.0);
        return out;
    }

    public Map<String, Object> evaluateBoxSpread(double callSpreadCost, double putSpreadCost, double k1, double k2) {
        double boxCost = callSpreadCost + putSpreadCost;
        double parValue = Math.abs(k2 - k1);
        double profit = parValue - boxCost;

        Map<String, Object> res = new HashMap<>();
        res.put("box_cost", Math.round(boxCost * 100.0) / 100.0);
        res.put("par_value", Math.round(parValue * 100.0) / 100.0);
        res.put("guaranteed_profit", Math.round(profit * 100.0) / 100.0);
        res.put("is_arbitrage", profit > 0.05);
        return res;
    }
}
