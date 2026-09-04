package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AO2 (Java): Cash-Secured Put (CSP) Ladder & Acquisition Basis Optimizer Engine.
 * Implements CSP strike selection, discounted basis formulas, and annualized ROC calculations in Java.
 */
public class CashSecuredPutEngine {
    private final double deltaMin;
    private final double deltaMax;

    public CashSecuredPutEngine(double deltaMin, double deltaMax) {
        this.deltaMin = deltaMin;
        this.deltaMax = deltaMax;
    }

    public CashSecuredPutEngine() {
        this(0.20, 0.30);
    }

    public Map<String, Object> evaluateCsp(double spot, double strike, double premium, double dte, double putDelta) {
        Map<String, Object> res = new HashMap<>();
        double costBasis = strike - premium;
        double discountPct = ((spot - costBasis) / spot) * 100.0;
        double collateral = strike * 100.0;
        double tradeRoc = ((premium * 100.0) / collateral) * 100.0;
        double annualizedRoc = tradeRoc * (365.0 / Math.max(1.0, dte));
        double popEst = (1.0 - Math.abs(putDelta)) * 100.0;

        boolean isOptimal = (Math.abs(putDelta) >= this.deltaMin && Math.abs(putDelta) <= this.deltaMax) && (dte >= 30.0 && dte <= 45.0);

        res.put("effectiveCostBasis", costBasis);
        res.put("discountPct", discountPct);
        res.put("annualizedRocPct", annualizedRoc);
        res.put("popEst", popEst);
        res.put("isOptimal", isOptimal);
        return res;
    }
}
