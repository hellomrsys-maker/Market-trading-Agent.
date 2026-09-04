package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module V2: Java Barrier, Digital & Autocallable Structuring Engine
 */
public class BarrierAutocallableEngine {

    public static double calculateDiscreteBarrierShift(double barrier, double sigma, double tYears, int numObs, boolean isShortBarrier) {
        if (numObs <= 0) return barrier;
        double dt = tYears / (double) numObs;
        double factor = 0.5826 * sigma * Math.sqrt(dt);
        return barrier * Math.exp(isShortBarrier ? factor : -factor);
    }

    public static double normalCdf(double z) {
        return 0.5 * (1.0 + erf(z / Math.sqrt(2.0)));
    }

    public static double normalPdf(double z) {
        return (1.0 / Math.sqrt(2.0 * Math.PI)) * Math.exp(-0.5 * z * z);
    }

    private static double erf(double z) {
        double t = 1.0 / (1.0 + 0.5 * Math.abs(z));
        double ans = 1.0 - t * Math.exp(-z * z - 1.26551223 +
                t * (1.00002368 +
                t * (0.37409196 +
                t * (0.09678418 +
                t * (-0.18628806 +
                t * (0.27886807 +
                t * (-1.13520398 +
                t * (1.48851587 +
                t * (-0.82215223 +
                t * 0.17087277)))))))));
        return (z >= 0) ? ans : -ans;
    }

    public static Map<String, Double> digitalWithSkewCorrection(double s, double x, double t, double r, double sigma, double skew) {
        double sqrtT = Math.sqrt(Math.max(1e-6, t));
        double d1 = (Math.log(s / x) + (r + 0.5 * sigma * sigma) * t) / (sigma * sqrtT);
        double d2 = d1 - sigma * sqrtT;

        double vega = s * normalPdf(d1) * sqrtT;
        double bsDigital = Math.exp(-r * t) * normalCdf(d2);
        double skewAdj = vega * Math.abs(skew);

        Map<String, Double> out = new HashMap<>();
        out.put("bsDigital", bsDigital);
        out.put("skewAdj", skewAdj);
        out.put("totalPrice", bsDigital + skewAdj);
        return out;
    }
}
