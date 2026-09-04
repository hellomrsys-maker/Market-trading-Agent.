package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AT2 (Java): Commodity Physical Delivery Risk, First Notice Day (FND) & Roll Governor Engine.
 * Evaluates FND countdowns, physical delivery flags, and volume crossover roll triggers in Java.
 */
public class DeliveryRollGovernorEngine {
    private final int fndWarningDays;

    public DeliveryRollGovernorEngine(int fndWarningDays) {
        this.fndWarningDays = fndWarningDays;
    }

    public DeliveryRollGovernorEngine() {
        this(5);
    }

    public Map<String, Object> evaluateRoll(boolean isPhysical, int daysToFnd, double volM1, double volM2) {
        Map<String, Object> res = new HashMap<>();
        boolean isVolRolled = volM2 > volM1;
        boolean isFndDanger = isPhysical && (daysToFnd <= this.fndWarningDays);

        String action = "HOLD";
        if (isPhysical && daysToFnd <= 1) {
            action = "MANDATORY_LIQUIDATE";
        } else if (isFndDanger || isVolRolled) {
            action = "EXECUTE_CALENDAR_ROLL";
        }

        res.put("isPhysical", isPhysical);
        res.put("isVolRolled", isVolRolled);
        res.put("isFndDanger", isFndDanger);
        res.put("action", action);
        return res;
    }
}
