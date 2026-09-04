package com.optionalpha.engine;

public class InstitutionalIronCondorEngine {
    public static class IronCondorState {
        public double expectedPriceGbm;
        public double netPremiumCredit;
        public double maxRiskCapital;
        public double portfolioDelta;
        public double portfolioGamma;
        public double portfolioTheta;
        public int archetypeId;
        public short dte;
        public boolean isIvCrushTarget;
        public boolean isMartingaleValid;
    }

    public static IronCondorState buildCondor(int archetypeId, double spot, double drift, double sigma, double timeYears) {
        IronCondorState state = new IronCondorState();
        state.archetypeId = archetypeId;
        state.expectedPriceGbm = spot * Math.exp(drift * timeYears);
        state.isMartingaleValid = Math.abs(state.expectedPriceGbm - spot) < 1.0;
        state.isIvCrushTarget = (archetypeId == 2);
        return state;
    }
}
