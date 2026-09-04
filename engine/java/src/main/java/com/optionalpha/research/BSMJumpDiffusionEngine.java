package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module R2: Java Advanced Black-Scholes, Greeks & Jump-Diffusion Engine
 */
public class BSMJumpDiffusionEngine {

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

    public static Map<String, Double> priceMertonBSM(double s, double x, double t, double r, double sigma, double q) {
        double sqrtT = Math.sqrt(Math.max(1e-6, t));
        double d1 = (Math.log(s / x) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrtT);
        double d2 = d1 - sigma * sqrtT;

        double nd1 = normalCdf(d1);
        double nd2 = normalCdf(d2);
        double expQt = Math.exp(-q * t);
        double expRt = Math.exp(-r * t);

        double call = s * expQt * nd1 - x * expRt * nd2;
        double put = x * expRt * normalCdf(-d2) - s * expQt * normalCdf(-d1);

        double deltaCall = expQt * nd1;
        double elasticity = (s * deltaCall) / Math.max(1e-4, call);

        Map<String, Double> out = new HashMap<>();
        out.put("callPrice", call);
        out.put("putPrice", put);
        out.put("d1", d1);
        out.put("d2", d2);
        out.put("deltaCall", deltaCall);
        out.put("elasticityCall", elasticity);
        return out;
    }

    public static double probabilityEverItm(double s, double x, double t, double r, double sigma, double q) {
        if (s >= x) return 1.0;
        double sqrtT = Math.sqrt(Math.max(1e-6, t));
        double d2 = (Math.log(s / x) + (r - q - 0.5 * sigma * sigma) * t) / (sigma * sqrtT);
        double b = (1.0 / sigma) * Math.log(x / s);
        double a = (1.0 / sigma) * (r - q - 0.5 * sigma * sigma);

        double pEver = normalCdf(d2) + Math.exp(2.0 * a * b) * normalCdf(d2 - 2.0 * a * sqrtT);
        return Math.min(1.0, Math.max(0.0, pEver));
    }
}
