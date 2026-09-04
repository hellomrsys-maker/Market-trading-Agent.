package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BD2 (Java): Multi-Timeframe Harmonic & Geometric Pattern Alignment Governor.
 * Enforces R:R >= 2.0 and multi-timeframe directional trend confluence in Java.
 */
public class PatternAlignmentRiskGovernor {
    private final double minRr;

    public PatternAlignmentRiskGovernor(double minRr) {
        this.minRr = minRr;
    }

    public PatternAlignmentRiskGovernor() {
        this(2.0);
    }

    public Map<String, Object> auditSetup(double entry, double target, double stopLoss, int htfDir, int patternDir) {
        Map<String, Object> res = new HashMap<>();
        double reward = Math.abs(target - entry);
        double risk = Math.abs(entry - stopLoss);
        double rr = reward / Math.max(1e-4, risk);

        boolean rrOk = rr >= this.minRr;
        boolean htfOk = (htfDir == patternDir) || (htfDir == 0);
        boolean approved = rrOk && htfOk;

        res.put("rrRatio", rr);
        res.put("isApproved", approved);
        res.put("verdict", approved ? "APPROVED_EXECUTE" : "BLOCKED");
        return res;
    }
}
