package com.optionalpha.engine;

public class ExoticMultiLegLadderEngine {
    public static class LadderState {
        public double strikeRung1;
        public double strikeRung2;
        public double strikeRung3;
        public double lambdaElasticity;
        public double netPremium;
        public int strategyArchetype;
    }

    public static LadderState constructStrip(double spot, double atm, double callPrem, double putPrem) {
        LadderState state = new LadderState();
        state.strikeRung1 = atm;
        state.strikeRung2 = atm;
        state.strikeRung3 = atm;
        state.netPremium = (2.0 * putPrem) + callPrem;
        double netDelta = (1.0 * 0.50) + (2.0 * (-0.50));
        state.lambdaElasticity = (state.netPremium > 0.001) ? (netDelta * spot) / state.netPremium : 0.0;
        state.strategyArchetype = 1;
        return state;
    }
}
