package com.optionalpha.research;

public class MinerHighProbabilityEngine {
    public int calculatePositionSize(double capital, double entry, double stop) {
        double maxRisk = capital * 0.03;
        double riskPerUnit = Math.abs(entry - stop);
        return (int) (maxRisk / riskPerUnit);
    }
}
