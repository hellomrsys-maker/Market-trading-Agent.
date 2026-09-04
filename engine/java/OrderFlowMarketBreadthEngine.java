package com.optionalpha.engine;

public class OrderFlowMarketBreadthEngine {
    public static class BreadthState {
        public double mcclellanOscillator;
        public double mcclellanSummation;
        public double armsTrinRatio;
        public double chaikinMoneyFlow;
        public double optionOrderFlowVol;
        public double flowNormalRatio;
        public int isUnusualFlowDetected;
        public int isTkoBreakout;
        public int isTrinExtremeFear;
    }

    public static BreadthState auditBreadth(double dailyVol, double avgVol, double advIssues, double decIssues, double advVol, double decVol) {
        BreadthState state = new BreadthState();
        state.optionOrderFlowVol = dailyVol;
        state.flowNormalRatio = dailyVol / Math.max(1.0, avgVol);
        state.isUnusualFlowDetected = (state.flowNormalRatio >= 5.0) ? 1 : 0;
        double adRatio = advIssues / Math.max(1.0, decIssues);
        double volRatio = advVol / Math.max(1.0, decVol);
        state.armsTrinRatio = adRatio / Math.max(0.001, volRatio);
        state.isTrinExtremeFear = (state.armsTrinRatio >= 1.5) ? 1 : 0;
        return state;
    }
}
