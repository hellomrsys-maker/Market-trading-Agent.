package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AR2 (Java): Disciplined Capital Allocation, Sizing & Anti-Gambling Risk Governor Engine.
 * Enforces 5% allocation limits, 25% cash reserve buffers, and 14-day earnings filters.
 */
public class RetailIncomeRiskGovernor {
    private final double maxSymbolAlloc;
    private final double minCashBuffer;
    private final int minEarningsBuffer;

    public RetailIncomeRiskGovernor(double maxSymbolAlloc, double minCashBuffer, int minEarningsBuffer) {
        this.maxSymbolAlloc = maxSymbolAlloc;
        this.minCashBuffer = minCashBuffer;
        this.minEarningsBuffer = minEarningsBuffer;
    }

    public RetailIncomeRiskGovernor() {
        this(5.0, 25.0, 14);
    }

    public Map<String, Object> auditTrade(double equity, double freeCash, double proposedCollateral, double existingCollateral, int daysToEarnings) {
        Map<String, Object> res = new HashMap<>();
        double maxAllowed = equity * (this.maxSymbolAlloc / 100.0);
        double totalExposure = existingCollateral + proposedCollateral;
        boolean symbolOk = totalExposure <= maxAllowed;

        double remainingCash = freeCash - proposedCollateral;
        double cashBufferPct = (remainingCash / Math.max(1.0, equity)) * 100.0;
        boolean cashOk = cashBufferPct >= this.minCashBuffer;

        boolean earningsOk = daysToEarnings >= this.minEarningsBuffer;
        boolean approved = symbolOk && cashOk && earningsOk;

        res.put("isApproved", approved);
        res.put("cashBufferPct", cashBufferPct);
        res.put("maxAllowedSymbol", maxAllowed);
        res.put("verdict", approved ? "APPROVED_EXECUTE" : "BLOCKED_RISK_VIOLATION");
        return res;
    }
}
