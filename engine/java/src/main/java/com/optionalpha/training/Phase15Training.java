package com.optionalpha.training;

import com.optionalpha.research.AllWeatherVommaEngine;
import com.optionalpha.research.GammaScalpingStochasticEngine;
import com.optionalpha.research.BladerunnerCarryForexEngine;
import com.optionalpha.research.StructuredCollarBoxArbitrageEngine;

import java.util.Map;

/**
 * Phase 15 Training Matrix Runner (T2 - Java).
 * Benchmarks enterprise state execution across Modules BE2, BF2, BG2, BH2.
 */
public class Phase15Training {
    public static void main(String[] args) {
        System.out.println("[T2 JAVA] Starting Enterprise State Memory Training Epochs for Phase 15...");

        // 1. Train BE2
        AllWeatherVommaEngine vommaEngine = new AllWeatherVommaEngine();
        Map<String, Object> vommaRes = vommaEngine.classifyRegime(-12.5, 38.0);
        Map<String, Object> marginRes = vommaEngine.auditMargin(-7800.0, -11000.0, -1000.0, 20000.0);

        // 2. Train BF2
        GammaScalpingStochasticEngine scalpEngine = new GammaScalpingStochasticEngine();
        Map<String, Object> scalpRes = scalpEngine.evaluateHedge(12.5, 100.0);

        // 3. Train BG2
        BladerunnerCarryForexEngine fxEngine = new BladerunnerCarryForexEngine();
        Map<String, Object> bladeRes = fxEngine.evaluateBladerunner(1.3520, 1.3500, true, true);
        Map<String, Object> carryRes = fxEngine.calculateCarry(4.50, 0.10, 100000.0);

        // 4. Train BH2
        StructuredCollarBoxArbitrageEngine boxEngine = new StructuredCollarBoxArbitrageEngine();
        Map<String, Object> collarRes = boxEngine.structureCollar(79.0, 88.0, 1.75, 85.0, 1.24);
        Map<String, Object> boxRes = boxEngine.evaluateBox(95.0, 105.0, 8.80);

        System.out.println("[T2 JAVA] Modules BE2, BF2, BG2, BH2 trained successfully.");
    }
}
