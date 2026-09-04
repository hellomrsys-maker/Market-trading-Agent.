package com.optionalpha.research;

import java.util.List;

/**
 * OptionAlpha Agent — Module W2: Java Cliquet, Napoleon & Mountain Range Pricing Engine
 */
public class CliquetMountainRangeEngine {

    public static double calculateLflcCliquet(double[] returns, double localFloor, double localCap) {
        double sum = 0.0;
        for (double r : returns) {
            sum += Math.max(localFloor, Math.min(r, localCap));
        }
        return sum;
    }

    public static double calculateGflcCliquet(double[] returns, double localFloor, double localCap, double globalFloor, double globalCap) {
        double rawSum = calculateLflcCliquet(returns, localFloor, localCap);
        return Math.max(globalFloor, Math.min(globalCap, rawSum));
    }

    public static double calculateNapoleon(double[] returns, double maxCoupon) {
        double worst = Double.MAX_VALUE;
        for (double r : returns) {
            if (r < worst) worst = r;
        }
        return Math.max(0.0, maxCoupon + worst);
    }

    public static double calculateEverest(double[] returns, double coupon) {
        double worst = Double.MAX_VALUE;
        for (double r : returns) {
            if (r < worst) worst = r;
        }
        return coupon + worst;
    }
}
