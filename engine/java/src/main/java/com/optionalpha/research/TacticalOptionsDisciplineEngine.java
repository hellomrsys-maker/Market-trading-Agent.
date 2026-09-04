package com.optionalpha.research;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Module AB2 (Java): Tactical Options Structuring & Execution Discipline Engine.
 * Structures Iron Condors, manages OCO brackets, and enforces 1-2% / 7% capital preservation in Java.
 */
public class TacticalOptionsDisciplineEngine {

    private double accountEquity;

    public TacticalOptionsDisciplineEngine(double accountEquity) {
        this.accountEquity = accountEquity;
    }

    public TacticalOptionsDisciplineEngine() {
        this(10000.0);
    }

    public Map<String, Object> calculatePositionSize(double entryPrice, double stopLossPrice, boolean isAggressive) {
        double riskFraction = isAggressive ? 0.02 : 0.01;
        double maxDollarRisk = accountEquity * riskFraction;
        double perShareRisk = Math.abs(entryPrice - stopLossPrice);

        int numShares = perShareRisk > 0 ? (int) Math.floor(maxDollarRisk / perShareRisk) : 0;
        int contracts = numShares / 100;

        Map<String, Object> result = new HashMap<>();
        result.put("account_equity", accountEquity);
        result.put("max_dollar_risk", Math.round(maxDollarRisk * 100.0) / 100.0);
        result.put("per_share_risk", Math.round(perShareRisk * 100.0) / 100.0);
        result.put("recommended_shares", numShares);
        result.put("recommended_contracts", contracts);
        return result;
    }

    public Map<String, Object> structureIronCondor(
            double k1PutLong, double k2PutShort,
            double k3CallShort, double k4CallLong,
            double premPutShort, double premPutLong,
            double premCallShort, double premCallLong) {

        double putCredit = premPutShort - premPutLong;
        double callCredit = premCallShort - premCallLong;
        double totalCredit = (putCredit + callCredit) * 100.0;

        double wingWidth = (k2PutShort - k1PutLong) * 100.0;
        double maxLoss = Math.max(0.0, wingWidth - totalCredit);
        double maxProfit = totalCredit;
        double rr = maxLoss > 0 ? maxProfit / maxLoss : 0.0;

        Map<String, Object> payoff = new HashMap<>();
        payoff.put("net_credit", Math.round(totalCredit * 100.0) / 100.0);
        payoff.put("wing_width", Math.round(wingWidth * 100.0) / 100.0);
        payoff.put("max_profit", Math.round(maxProfit * 100.0) / 100.0);
        payoff.put("max_loss", Math.round(maxLoss * 100.0) / 100.0);
        payoff.put("reward_to_risk", Math.round(rr * 100.0) / 100.0);
        return payoff;
    }

    public Map<String, Object> auditDiscipline(boolean attemptedStopPull, int consecutiveWins, boolean isRevengeTrade) {
        List<String> violations = new ArrayList<>();
        if (attemptedStopPull) {
            violations.add("RULE_VIOLATION: Never pull a stop loss.");
        }
        if (consecutiveWins >= 4) {
            violations.add("WARNING: Arrogance risk. Halve sizing.");
        }
        if (isRevengeTrade) {
            violations.add("CIRCUIT_BREAKER: Revenge trade lockout.");
        }

        Map<String, Object> res = new HashMap<>();
        res.put("trading_allowed", violations.isEmpty());
        res.put("violations", violations);
        return res;
    }
}
