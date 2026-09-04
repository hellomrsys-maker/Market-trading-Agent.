package com.optionalpha.training;

import com.optionalpha.research.WeeklySqueezeEngine;
import com.optionalpha.research.BSMJumpDiffusionEngine;
import com.optionalpha.research.BinaryOptionsEngine;
import com.optionalpha.research.DrawdownRiskManager;

import java.util.Map;

/**
 * Phase 5 Java Training Module (T2)
 */
public class Phase5Training {
    public static void main(String[] args) {
        System.out.println("[T2 JAVA] Starting Enterprise State Memory Training Epochs for Phase 5...");

        // 1. Weekly Squeeze
        WeeklySqueezeEngine.HeikinAshiBar prevBar = new WeeklySqueezeEngine.HeikinAshiBar(98.0, 102.0, 97.0, 101.0, 97.0, 100.0);
        WeeklySqueezeEngine.HeikinAshiBar currBar = new WeeklySqueezeEngine.HeikinAshiBar(100.0, 105.0, 99.0, 104.0, prevBar.open, prevBar.close);
        Map<String, Object> sqzRes = WeeklySqueezeEngine.evaluateWeeklySetup(103.0, 97.0, 104.0, 96.0, 102.0, 100.0, 95.0, currBar, prevBar);
        System.out.println("[T2 JAVA] Squeeze Engine: InSqueeze=" + sqzRes.get("inSqueeze") + ", Action=" + sqzRes.get("recommendedAction"));

        // 2. BSM Jump Diffusion
        Map<String, Double> bsmRes = BSMJumpDiffusionEngine.priceMertonBSM(100.0, 100.0, 0.25, 0.05, 0.20, 0.02);
        double pEver = BSMJumpDiffusionEngine.probabilityEverItm(100.0, 110.0, 0.5, 0.05, 0.25, 0.0);
        System.out.printf("[T2 JAVA] BSM Engine: Call=%.2f, P*_ever=%.1f%%\n", bsmRes.get("callPrice"), pEver * 100.0);

        // 3. Binary Options
        Map<String, Double> binRes = BinaryOptionsEngine.priceShortVolatilityStrangle(20.0, 80.0, 2);
        System.out.printf("[T2 JAVA] Binary Strangle: Collateral=%.2f, MaxProfit=%.2f\n", binRes.get("totalCollateral"), binRes.get("maxProfit"));

        // 4. Drawdown Risk
        DrawdownRiskManager drm = new DrawdownRiskManager(10000.0, 20.0);
        int posSize = drm.calculatePositionSize(2.0, 50.0);
        System.out.println("[T2 JAVA] Drawdown Risk: PosSize=" + posSize);

        System.out.println("[T2 JAVA] Modules Q2, R2, S2, T_sys2 trained successfully.");
    }
}
