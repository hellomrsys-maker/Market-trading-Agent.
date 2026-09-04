package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AZ2 (Java): Professional Trade Adjustment, Repair & Dynamic Hedging Protocol Engine.
 * Evaluates trade defense decision trees, delta breaches, and repair directives in Java.
 */
public class TradeAdjustmentRepairEngine {
    private final double deltaBreach;
    private final double maxLossMultiple;

    public TradeAdjustmentRepairEngine(double deltaBreach, double maxLossMultiple) {
        this.deltaBreach = deltaBreach;
        this.maxLossMultiple = maxLossMultiple;
    }

    public TradeAdjustmentRepairEngine() {
        this(0.35, 2.0);
    }

    public Map<String, Object> auditDefense(double pnl, double initialCredit, double shortDelta, double dte, double extrinsic) {
        Map<String, Object> res = new HashMap<>();
        boolean isDeltaBreached = Math.abs(shortDelta) >= this.deltaBreach;
        double maxLoss = initialCredit * this.maxLossMultiple;
        boolean isMaxLossHit = pnl <= -maxLoss;

        String action = "HOLD";
        if (isMaxLossHit) {
            action = "CUT_LOSS_DISCIPLINED_EXIT";
        } else if (isDeltaBreached) {
            if (dte >= 14.0 && extrinsic > 0.30) {
                action = "ROLL_UNTESTED_WING_CONVERT_IRON_CONDOR";
            } else if (dte < 7.0) {
                action = "ROLL_SPREAD_OUT_IN_TIME";
            } else {
                action = "DELTA_HEDGE_WITH_SHARES";
            }
        }

        res.put("isDeltaBreached", isDeltaBreached);
        res.put("isMaxLossHit", isMaxLossHit);
        res.put("action", action);
        return res;
    }
}
