package com.optionalpha.engine;

public class CryptoSpotEngine {
    public static class CryptoSpotState {
        public double spotPrice;
        public double bidDepthUsd;
        public double askDepthUsd;
        public double orderBookImbalance;
        public double triangularArbSpread;
        public double nonMarginableBuyingPower;
        public int assetPairId;
        public int maxNotionalK;
        public boolean isTradable;
        public boolean isFractionable;
        public int feeBps;
        public int statusFlags;
    }

    public static CryptoSpotState initialize(double spot, double cashPower, int pairId) {
        CryptoSpotState state = new CryptoSpotState();
        state.spotPrice = spot;
        state.bidDepthUsd = spot * 5.0;
        state.askDepthUsd = spot * 5.0;
        state.orderBookImbalance = 0.0;
        state.triangularArbSpread = 0.0;
        state.nonMarginableBuyingPower = cashPower;
        state.assetPairId = pairId;
        state.maxNotionalK = 200;
        state.isTradable = true;
        state.isFractionable = true;
        state.feeBps = 25;
        state.statusFlags = 1;
        return state;
    }

    public static double computeOrderBookImbalance(CryptoSpotState state, double bidVol, double askVol) {
        double total = bidVol + askVol;
        if (total <= 0.0001) {
            state.orderBookImbalance = 0.0;
            return 0.0;
        }
        state.orderBookImbalance = (bidVol - askVol) / total;
        return state.orderBookImbalance;
    }

    public static double evaluateTriangularArbitrage(CryptoSpotState state, double btcUsd, double ethBtc, double ethUsd) {
        double syntheticEthUsd = ethBtc * btcUsd;
        if (ethUsd <= 0.0001) return 0.0;
        double discrepancy = (ethUsd - syntheticEthUsd) / ethUsd;
        state.triangularArbSpread = discrepancy;
        if (Math.abs(discrepancy) > 0.0050) {
            state.statusFlags |= 2;
        }
        return discrepancy;
    }
}
