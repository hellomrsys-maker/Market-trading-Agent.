package com.optionalpha.engine;

public class MeanReversionSqueezeEngine {
    public static class SqueezeState {
        public double pnrThreshold;
        public double bollingerUpper;
        public double bollingerLower;
        public double keltnerUpper;
        public double keltnerLower;
        public double currentAdx;
        public float currentRsi;
        public float currentAtr;
        public short dte;
        public boolean isSqueezeActive;
        public boolean isPnrBreached;
        public boolean dmiBullishCross;
        public boolean dmiBearishCross;
        public boolean cut50pctLoss;
    }

    public static SqueezeState evaluateState(double longStrike, double shortStrike, short dte, float atr, double currentPrice) {
        SqueezeState state = new SqueezeState();
        state.dte = dte;
        state.currentAtr = atr;
        double pnrOffset = (longStrike * dte * atr) / 2000.0;
        state.pnrThreshold = longStrike - pnrOffset;
        state.isPnrBreached = currentPrice < state.pnrThreshold;
        state.cut50pctLoss = state.isPnrBreached && (dte < 15);
        return state;
    }
}
