package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AP2 (Java): Dynamic Covered Call Yield & Dividend Capture Optimizer Engine.
 * Implements static/max yield attribution, downside protection, and early ex-dividend assignment checks.
 */
public class CoveredCallYieldEngine {
    public CoveredCallYieldEngine() {}

    public Map<String, Object> evaluateCoveredCall(
        double stockBasis, double currentSpot, double strike,
        double premium, double dte, double dividendPerShare
    ) {
        Map<String, Object> res = new HashMap<>();
        double bePrice = stockBasis - premium;
        double downsideProtection = (premium / currentSpot) * 100.0;

        double staticYield = ((premium + dividendPerShare) / stockBasis) * 100.0;
        double annualizedStatic = staticYield * (365.0 / Math.max(1.0, dte));

        double capGain = Math.max(0.0, strike - stockBasis);
        double maxYield = ((capGain + premium + dividendPerShare) / stockBasis) * 100.0;
        double annualizedMax = maxYield * (365.0 / Math.max(1.0, dte));

        double intrinsic = Math.max(0.0, currentSpot - strike);
        double extrinsic = Math.max(0.0, premium - intrinsic);
        boolean earlyAssignment = (currentSpot > strike) && (extrinsic < dividendPerShare);

        res.put("breakevenPrice", bePrice);
        res.put("downsideProtectionPct", downsideProtection);
        res.put("annualizedStaticYield", annualizedStatic);
        res.put("annualizedMaxYield", annualizedMax);
        res.put("earlyAssignmentWarning", earlyAssignment);
        return res;
    }
}
