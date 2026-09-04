package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module X2: Java Volatility Derivatives, Variance Swaps & Hybrid Copula Engine
 */
public class VarianceSwapCopulaEngine {

    public static double calculateRealizedVariance(double[] logReturns, double annualizationFactor) {
        if (logReturns.length == 0) return 0.0;
        double sumSq = 0.0;
        for (double r : logReturns) {
            sumSq += r * r;
        }
        return (annualizationFactor / logReturns.length) * sumSq;
    }

    public static Map<String, Double> calculateVarianceSwapGreeks(double tYears, double timeElapsed, double currentSigma) {
        double tRem = Math.max(1e-4, tYears - timeElapsed);
        double tSafe = Math.max(1e-4, tYears);

        double cashGamma = 2.0 / tSafe;
        double vega = (2.0 / tSafe) * currentSigma * tRem;
        double theta = - (1.0 / tSafe) * currentSigma * currentSigma;

        Map<String, Double> greeks = new HashMap<>();
        greeks.put("cashGamma", cashGamma);
        greeks.put("vega", vega);
        greeks.put("theta", theta);
        return greeks;
    }
}
