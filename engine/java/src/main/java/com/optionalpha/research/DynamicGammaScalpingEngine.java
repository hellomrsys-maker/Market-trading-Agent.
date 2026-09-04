package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AH2 (Java): Dynamic Algorithmic Gamma Scalping & Discrete Rebalancing Engine.
 * Implements Leland-Whalley-Wilmott rebalancing bands and discrete gamma scalping PnL.
 */
public class DynamicGammaScalpingEngine {
    private final double riskAversion;
    private final double transactionCost;

    public DynamicGammaScalpingEngine(double riskAversion, double transactionCost) {
        this.riskAversion = riskAversion;
        this.transactionCost = transactionCost;
    }

    public DynamicGammaScalpingEngine() {
        this(1.0, 0.005);
    }

    public Map<String, Object> computeOptimalBand(double portfolioGamma) {
        Map<String, Object> res = new HashMap<>();
        double absGamma = Math.max(1e-7, Math.abs(portfolioGamma));
        double term = (1.5 * this.transactionCost * absGamma) / Math.max(1e-5, this.riskAversion);
        double threshold = Math.pow(term, 1.0 / 3.0);
        double clamped = Math.max(0.02, Math.min(0.25, threshold));

        res.put("portfolioGamma", portfolioGamma);
        res.put("optimalDeltaThreshold", clamped);
        return res;
    }

    public Map<String, Object> calculateScalpPnl(double gamma, double spot, double realVol, double impVol, double dtYears, double costs) {
        Map<String, Object> res = new HashMap<>();
        double gammaDollar = 0.5 * gamma * (spot * spot);
        double varDiff = (realVol * realVol) - (impVol * impVol);
        double grossPnl = gammaDollar * varDiff * dtYears;
        double netPnl = grossPnl - costs;

        res.put("grossPnl", grossPnl);
        res.put("netPnl", netPnl);
        res.put("isProfitable", netPnl > 0);
        return res;
    }
}
