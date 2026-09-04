package com.optionalpha.engine;

public class RatioBackspreadEngine {
    public static class BackspreadState {
        public double shortStrike;
        public double longStrike;
        public double netDebitCredit;
        public double maxLoss;
        public double upperBep;
        public double lowerBep;
        public boolean isCall;
    }

    public static BackspreadState construct(double atm, double otm, double shortPrem, double longPrem, boolean isCall) {
        BackspreadState state = new BackspreadState();
        state.shortStrike = atm;
        state.longStrike = otm;
        state.netDebitCredit = (2.0 * longPrem) - shortPrem;
        state.maxLoss = Math.abs(otm - atm) + state.netDebitCredit;
        state.upperBep = otm + state.maxLoss;
        state.lowerBep = atm + (state.netDebitCredit < 0.0 ? state.netDebitCredit : 0.0);
        state.isCall = isCall;
        return state;
    }
}
