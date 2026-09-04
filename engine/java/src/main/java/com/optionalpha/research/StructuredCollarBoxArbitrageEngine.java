package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BH2 (Java): Structured Options, Collars & Binary Box Arbitrage Engine.
 * Evaluates costless collars, Long Box risk-free arbitrage, and binary options in Java.
 */
public class StructuredCollarBoxArbitrageEngine {
    public StructuredCollarBoxArbitrageEngine() {}

    public Map<String, Object> structureCollar(double basis, double callK, double callPrem, double putK, double putPrem) {
        Map<String, Object> res = new HashMap<>();
        double netPrem = callPrem - putPrem;
        boolean isCostless = netPrem >= 0.0;

        res.put("netPrem", netPrem);
        res.put("isCostless", isCostless);
        return res;
    }

    public Map<String, Object> evaluateBox(double k1, double k2, double netDebit) {
        Map<String, Object> res = new HashMap<>();
        double payoff = k2 - k1;
        double profit = payoff - netDebit;
        boolean profitable = profit > 0.0;

        res.put("payoff", payoff);
        res.put("profit", profit);
        res.put("profitable", profitable);
        return res;
    }

    public Map<String, Object> evaluateBinary(double bet, double payoutPct, double rebatePct, boolean itm) {
        Map<String, Object> res = new HashMap<>();
        double totalReturn = itm ? bet * (1.0 + payoutPct / 100.0) : bet * (rebatePct / 100.0);
        double netProfit = totalReturn - bet;

        res.put("totalReturn", totalReturn);
        res.put("netProfit", netProfit);
        return res;
    }
}
