package com.optionalpha.engine;

public class KaChingConvexityEngine {
    public static class KaChingState {
        public double longPutStrike;
        public double shortPutStrike;
        public double longPutDelta;
        public double shortPutDelta;
        public double netWeeklyPremium;
        public double cumulativeCash;
        public int daysToEarnings;
        public int rollCount;
        public boolean doubleDipActive;
    }

    public static KaChingState initialize(double spot, double iv, int dte) {
        KaChingState state = new KaChingState();
        state.longPutDelta = (iv > 0.35) ? 0.38 : 0.25;
        state.longPutStrike = spot * (1.0 - (state.longPutDelta == 0.25 ? 0.08 : 0.05));
        state.shortPutDelta = (spot >= state.longPutStrike) ? 0.50 : 0.40;
        state.shortPutStrike = spot;
        state.netWeeklyPremium = spot * 0.018 * (1.0 + iv);
        state.cumulativeCash = state.netWeeklyPremium;
        state.daysToEarnings = dte;
        state.rollCount = 0;
        state.doubleDipActive = false;
        return state;
    }
}
