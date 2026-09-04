package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AV2 (Java): Physical Cash-to-Futures Basis & Storage Arbitrage Engine.
 * Evaluates local basis regimes, basis Z-scores, and cash-and-carry storage arbitrage in Java.
 */
public class CashFuturesBasisArbitrageEngine {
    public CashFuturesBasisArbitrageEngine() {}

    public Map<String, Object> evaluateBasis(double cashPrice, double futuresPrice, double histMean, double histStd) {
        Map<String, Object> res = new HashMap<>();
        double basis = cashPrice - futuresPrice;
        double std = Math.max(1e-4, histStd);
        double zscore = (basis - histMean) / std;

        String regime;
        if (zscore >= 1.5) regime = "STRONG_BASIS_PHYSICAL_SCARCITY";
        else if (zscore <= -1.5) regime = "WEAK_BASIS_STORAGE_OPPORTUNITY";
        else regime = "NORMAL_EQUILIBRIUM";

        res.put("basis", basis);
        res.put("zscore", zscore);
        res.put("regime", regime);
        return res;
    }

    public Map<String, Object> evaluateCashCarry(double cashPrice, double futuresPrice, double carryCost) {
        Map<String, Object> res = new HashMap<>();
        double netProfit = (futuresPrice - cashPrice) - carryCost;
        boolean isProfitable = netProfit > 0;

        res.put("netProfit", netProfit);
        res.put("isProfitable", isProfitable);
        return res;
    }
}
