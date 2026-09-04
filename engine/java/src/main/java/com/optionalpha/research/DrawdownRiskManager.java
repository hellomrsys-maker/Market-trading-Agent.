package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module T_sys2: Java System Drawdown, Risk Management & Compounding Engine
 */
public class DrawdownRiskManager {

    private double currentCapital;
    private double peakEquity;
    private double maxDdCutoffPct;
    private int consecutiveLosses;

    public DrawdownRiskManager(double initialCapital, double maxDdCutoffPct) {
        this.currentCapital = initialCapital;
        this.peakEquity = initialCapital;
        this.maxDdCutoffPct = maxDdCutoffPct;
        this.consecutiveLosses = 0;
    }

    public int calculatePositionSize(double riskPct, double maxLossPerContract) {
        double maxDollarRisk = this.currentCapital * (riskPct / 100.0);
        if (maxLossPerContract <= 0) return 1;
        return (int) Math.max(1, Math.floor(maxDollarRisk / maxLossPerContract));
    }

    public Map<String, Object> updateTrade(double pnl) {
        this.currentCapital += pnl;
        if (this.currentCapital > this.peakEquity) {
            this.peakEquity = this.currentCapital;
        }

        if (pnl < 0) {
            this.consecutiveLosses++;
        } else {
            this.consecutiveLosses = 0;
        }

        double dollarDd = this.peakEquity - this.currentCapital;
        double pctDd = (this.peakEquity > 0) ? (dollarDd / this.peakEquity) * 100.0 : 0.0;

        boolean isHalted = (pctDd >= this.maxDdCutoffPct) || (this.consecutiveLosses >= 6);

        Map<String, Object> state = new HashMap<>();
        state.put("currentCapital", this.currentCapital);
        state.put("peakEquity", this.peakEquity);
        state.put("pctDrawdown", pctDd);
        state.put("consecutiveLosses", this.consecutiveLosses);
        state.put("isHalted", isHalted);
        return state;
    }
}
