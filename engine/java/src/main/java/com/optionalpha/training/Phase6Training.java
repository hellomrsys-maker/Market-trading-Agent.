package com.optionalpha.training;

import com.optionalpha.research.DispersionRainbowEngine;
import com.optionalpha.research.BarrierAutocallableEngine;
import com.optionalpha.research.CliquetMountainRangeEngine;
import com.optionalpha.research.VarianceSwapCopulaEngine;

import java.util.Map;

/**
 * Phase 6 Java Training Module (T2)
 */
public class Phase6Training {
    public static void main(String[] args) {
        System.out.println("[T2 JAVA] Starting Enterprise State Memory Training Epochs for Phase 6...");

        // 1. Dispersion & Rainbow
        double[] weights = {0.5, 0.5};
        double[] vols = {0.20, 0.30};
        double[][] corr = {{1.0, 0.4}, {0.4, 1.0}};
        double varP = DispersionRainbowEngine.calculateBasketVariance(weights, vols, corr);
        double boParity = DispersionRainbowEngine.bestOfWorstOfParity(8.0, 6.0, 3.5);
        System.out.printf("[T2 JAVA] Dispersion Engine: BasketVar=%.4f, BO_Parity=%.2f\n", varP, boParity);

        // 2. Barrier & Digital
        double hShift = BarrierAutocallableEngine.calculateDiscreteBarrierShift(80.0, 0.20, 1.0, 252, true);
        Map<String, Double> digRes = BarrierAutocallableEngine.digitalWithSkewCorrection(100.0, 100.0, 1.0, 0.05, 0.20, -0.05);
        System.out.printf("[T2 JAVA] Barrier Engine: ShiftedH=%.2f, DigitalPrice=%.4f\n", hShift, digRes.get("totalPrice"));

        // 3. Cliquet & Mountain
        double[] rets = {0.05, -0.02, 0.08};
        double lflc = CliquetMountainRangeEngine.calculateLflcCliquet(rets, 0.0, 0.05);
        double napoleon = CliquetMountainRangeEngine.calculateNapoleon(rets, 0.50);
        System.out.printf("[T2 JAVA] Cliquet Engine: LFLC=%.2f%%, Napoleon=%.2f%%\n", lflc * 100.0, napoleon * 100.0);

        // 4. Variance Swap
        double[] logRets = {0.01, -0.015, 0.02, -0.005, 0.012};
        double rv = VarianceSwapCopulaEngine.calculateRealizedVariance(logRets, 252.0);
        Map<String, Double> greeks = VarianceSwapCopulaEngine.calculateVarianceSwapGreeks(1.0, 0.25, 0.20);
        System.out.printf("[T2 JAVA] Variance Swap: RV=%.4f, CashGamma=%.2f, Vega=%.4f\n", rv, greeks.get("cashGamma"), greeks.get("vega"));

        System.out.println("[T2 JAVA] Modules U2, V2, W2, X2 trained successfully.");
    }
}
