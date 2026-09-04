package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module Z2 (Java): Top-Down Cash Flow & Capital Ecosystem Engine.
 * Implements payday neutrality, sinking fund amortizations, and leak detection in enterprise Java.
 */
public class CashflowCapitalEcosystemEngine {

    private double newZeroBuffer;

    public CashflowCapitalEcosystemEngine(double newZeroBuffer) {
        this.newZeroBuffer = newZeroBuffer;
    }

    public CashflowCapitalEcosystemEngine() {
        this(100.0);
    }

    public double calculateSinkingFundInstallment(double targetAmount, int periodsRemaining, double bufferPercent) {
        if (periodsRemaining <= 0) {
            return targetAmount * (1.0 + bufferPercent);
        }
        return (targetAmount * (1.0 + bufferPercent)) / (double) periodsRemaining;
    }

    public Map<String, Double> calculateStreamlinedEcosystem(
            double income,
            double fixedCosts,
            double variableCosts,
            double sinkingFundsTotal,
            double savingsRatio) {
        
        double totalEssentials = fixedCosts + variableCosts + sinkingFundsTotal;
        double workable = Math.max(0.0, income - totalEssentials);
        double keepAlloc = workable * savingsRatio;
        double spendAlloc = Math.max(0.0, workable - keepAlloc);

        Map<String, Double> state = new HashMap<>();
        state.put("total_income", income);
        state.put("fixed_essentials", fixedCosts);
        state.put("variable_essentials", variableCosts);
        state.put("sinking_funds_total", sinkingFundsTotal);
        state.put("workable_total", Math.round(workable * 100.0) / 100.0);
        state.put("keep_savings_allocated", Math.round(keepAlloc * 100.0) / 100.0);
        state.put("spend_discretionary_allocated", Math.round(spendAlloc * 100.0) / 100.0);
        state.put("new_zero_buffer", newZeroBuffer);
        return state;
    }

    public Map<String, Object> executeMoneyLeakLitmusTest(
            String category,
            int estFreq,
            double estSpend,
            int actFreq,
            double actSpend) {
        
        int freqDiff = actFreq - estFreq;
        double spendLeak = actSpend - estSpend;

        Map<String, Object> res = new HashMap<>();
        res.put("category", category);
        res.put("frequency_discrepancy", freqDiff);
        res.put("monetary_leak_amount", Math.round(spendLeak * 100.0) / 100.0);
        res.put("is_leaking", spendLeak > 0 || freqDiff > 0);
        res.put("hilss_potential", Math.max(0.0, spendLeak));
        return res;
    }
}
