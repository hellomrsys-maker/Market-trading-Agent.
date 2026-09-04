package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AQ2 (Java): The Wheel Strategy Lifecycle & Dynamic State Machine Engine.
 * Manages 4-state lifecycle transitions and amortized net cost basis calculation in Java.
 */
public class WheelStrategyEngine {
    public WheelStrategyEngine() {}

    public Map<String, Object> trackLifecycle(
        String state, double spot, double costBasisShares,
        double putPremiums, double callPremiums, double dividends,
        double optionStrike, double originalPremium, double currentOptionPrice
    ) {
        Map<String, Object> res = new HashMap<>();
        double trueBasis = costBasisShares - putPremiums - callPremiums - dividends;

        double profitCaptured = originalPremium - currentOptionPrice;
        double profitPct = originalPremium > 0 ? (profitCaptured / originalPremium) * 100.0 : 0.0;
        boolean target50Hit = profitPct >= 50.0;

        String nextState = state;
        String action = "MAINTAIN_POSITION";

        if ("STATE_1_LIQUID_CASH".equals(state)) {
            action = "SCAN_AND_SELL_CSP_30DTE";
            nextState = "STATE_2_PUT_ACTIVE";
        } else if ("STATE_2_PUT_ACTIVE".equals(state)) {
            if (target50Hit) {
                action = "CLOSE_PUT_50PCT_PROFIT";
                nextState = "STATE_1_LIQUID_CASH";
            } else if (spot < optionStrike) {
                action = "PREPARE_FOR_ASSIGNMENT";
                nextState = "STATE_3_STOCK_ASSIGNED";
            }
        } else if ("STATE_3_STOCK_ASSIGNED".equals(state)) {
            action = "SELL_COVERED_CALL";
            nextState = "STATE_4_CALL_ACTIVE";
        } else if ("STATE_4_CALL_ACTIVE".equals(state)) {
            if (target50Hit) {
                action = "CLOSE_CALL_50PCT_PROFIT";
                nextState = "STATE_3_STOCK_ASSIGNED";
            } else if (spot > optionStrike) {
                action = "SHARES_CALLED_AWAY";
                nextState = "STATE_1_LIQUID_CASH";
            }
        }

        res.put("trueNetCostBasis", trueBasis);
        res.put("profitPct", profitPct);
        res.put("is50PctHit", target50Hit);
        res.put("nextState", nextState);
        res.put("action", action);
        return res;
    }
}
