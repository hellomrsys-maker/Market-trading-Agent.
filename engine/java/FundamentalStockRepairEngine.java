package com.optionalpha.engine;

public class FundamentalStockRepairEngine {
    public static class RepairState {
        public double peRatio;
        public double pegRatio;
        public double debtToAssetsRatio;
        public double repairLongStrike;
        public double repairShortStrike;
        public double cashReservePct;
        public int secMaterialFlag;
        public int useNakedOverSpread;
        public int isRepairRecommended;
    }

    public static RepairState evaluateRepair(double price, double costBasis, double vix, double cashPct) {
        RepairState state = new RepairState();
        state.cashReservePct = cashPct;
        state.useNakedOverSpread = (vix >= 20.0) ? 1 : 0;
        double dropPct = ((costBasis - price) / costBasis) * 100.0;
        if (dropPct >= 15.0 && dropPct <= 25.0) {
            state.isRepairRecommended = 1;
            state.repairLongStrike = price;
            state.repairShortStrike = price + ((costBasis - price) / 2.0);
        } else {
            state.isRepairRecommended = 0;
        }
        return state;
    }
}
