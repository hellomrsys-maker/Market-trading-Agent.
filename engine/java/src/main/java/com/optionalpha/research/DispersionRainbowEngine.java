package com.optionalpha.research;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module U2: Java Multi-Asset Dispersion, Rainbow & Basket Engine
 */
public class DispersionRainbowEngine {

    public static double calculateBasketVariance(double[] weights, double[] vols, double[][] corr) {
        int n = weights.length;
        double var = 0.0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                var += weights[i] * weights[j] * vols[i] * vols[j] * corr[i][j];
            }
        }
        return Math.max(1e-6, var);
    }

    public static double bestOfWorstOfParity(double call1, double call2, double worstOfCall) {
        return call1 + call2 - worstOfCall;
    }

    public static double calculateRainbowPayoff(double[] returns, double[] weightsDescending) {
        double[] sorted = returns.clone();
        Arrays.sort(sorted);
        // reverse to descending
        double payoff = 0.0;
        int n = Math.min(sorted.length, weightsDescending.length);
        for (int i = 0; i < n; i++) {
            payoff += weightsDescending[i] * sorted[sorted.length - 1 - i];
        }
        return Math.max(0.0, payoff);
    }

    public static Map<String, Double> evaluateIcbcVsCbc(double[] rets, double cap) {
        double sumCapped = 0.0;
        double sumRaw = 0.0;
        for (double r : rets) {
            sumCapped += Math.min(r, cap);
            sumRaw += r;
        }
        double icbc = Math.max(0.0, sumCapped / rets.length);
        double cbc = Math.max(0.0, Math.min(sumRaw / rets.length, cap));

        Map<String, Double> out = new HashMap<>();
        out.put("icbcPayoff", icbc);
        out.put("cbcPayoff", cbc);
        out.put("dispersionBenefit", cbc - icbc);
        return out;
    }
}
