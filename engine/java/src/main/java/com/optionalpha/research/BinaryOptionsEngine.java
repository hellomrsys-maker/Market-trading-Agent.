package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * OptionAlpha Agent — Module S2: Java Binary Digital & Volatility Strangle Engine
 */
public class BinaryOptionsEngine {

    public static Map<String, Double> calculateBinaryCollateral(String type, double premium, int contracts) {
        double collateralPerUnit = "LONG".equalsIgnoreCase(type) ? premium : (100.0 - premium);
        double maxProfitPerUnit = "LONG".equalsIgnoreCase(type) ? (100.0 - premium) : premium;
        double totalCollateral = collateralPerUnit * contracts;
        double totalProfit = maxProfitPerUnit * contracts;

        Map<String, Double> res = new HashMap<>();
        res.put("collateralPerContract", collateralPerUnit);
        res.put("maxProfitPerContract", maxProfitPerUnit);
        res.put("totalCollateral", totalCollateral);
        res.put("totalMaxProfit", totalProfit);
        res.put("rewardRiskRatio", totalProfit / Math.max(1e-4, totalCollateral));
        return res;
    }

    public static Map<String, Double> priceShortVolatilityStrangle(double highAsk, double lowBid, int contracts) {
        double longCost = lowBid;
        double shortCollateral = 100.0 - highAsk;
        double totalCollateral = (longCost + shortCollateral) * contracts;
        double maxProfit = (200.0 * contracts) - totalCollateral;

        double upperLoss = shortCollateral - (100.0 - longCost);
        double lowerLoss = longCost - (100.0 - shortCollateral);
        double maxLoss = Math.max(Math.abs(upperLoss), Math.abs(lowerLoss)) * contracts;

        Map<String, Double> res = new HashMap<>();
        res.put("totalCollateral", totalCollateral);
        res.put("maxProfit", maxProfit);
        res.put("maxLoss", maxLoss);
        res.put("rewardRiskRatio", maxProfit / Math.max(1e-4, maxLoss));
        return res;
    }
}
