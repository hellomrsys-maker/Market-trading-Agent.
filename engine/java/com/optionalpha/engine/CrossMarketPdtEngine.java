package com.optionalpha.engine;

public class CrossMarketPdtEngine {
    public static class PdtState {
        public double accountEquity;
        public double marginBorrowed;
        public double forexLeverage;
        public double futuresTickValue;
        public double maxRiskPerTrade;
        public double currentDrawdownPct;
        public int roundTrips5d;
        public boolean pdtRestricted;
    }

    public static boolean auditCompliance(PdtState state, boolean isDayTrade, double proposedRisk) {
        if (state.currentDrawdownPct >= 0.10) return false;
        if (proposedRisk > (state.accountEquity * 0.05)) return false;
        if (state.accountEquity < 25000.0 && isDayTrade) {
            if (state.roundTrips5d >= 3) {
                state.pdtRestricted = true;
                return false;
            }
            state.roundTrips5d++;
        }
        return true;
    }
}
