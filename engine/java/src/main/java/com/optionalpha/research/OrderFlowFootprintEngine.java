package com.optionalpha.research;

import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;

/**
 * OptionAlpha Agent — Module I2: Java Order Flow Footprint & VPOC Delta Engine
 * Enterprise Level 2 / Level 3 NSE Market Depth & Footprint State Tracking
 */
public class OrderFlowFootprintEngine {
    private static final Logger logger = Logger.getLogger(OrderFlowFootprintEngine.class.getName());
    private double runningCumulativeDelta = 0.0;
    private double runningCumulativeVolume = 0.0;

    public OrderFlowFootprintEngine() {
        logger.info("Initializing Java Enterprise Order Flow Footprint & VPOC Engine...");
    }

    public Map<String, Object> processLevel3OrderBook(
            double[] bidPrices, double[] bidVolumes,
            double[] askPrices, double[] askVolumes) {
        
        double totalBidVol = 0.0;
        double totalAskVol = 0.0;
        for (double v : bidVolumes) totalBidVol += v;
        for (double v : askVolumes) totalAskVol += v;

        double delta = totalAskVol - totalBidVol;
        this.runningCumulativeDelta += delta;
        this.runningCumulativeVolume += (totalBidVol + totalAskVol);

        Map<String, Object> result = new HashMap<>();
        result.put("depth_levels", Math.min(bidPrices.length, 20));
        result.put("instant_delta", delta);
        result.put("cumulative_delta", this.runningCumulativeDelta);
        result.put("cum_delta_pct", (this.runningCumulativeDelta / Math.max(1.0, this.runningCumulativeVolume)) * 100.0);
        result.put("orderbook_state", delta > 0 ? "BUY_SIDE_AGGRESSION" : "SELL_SIDE_AGGRESSION");

        return result;
    }

    public String evaluateValueAreaInteraction(double currentPrice, double vah, double val, double vpoc) {
        if (currentPrice > vah) {
            return "ACCEPTANCE_ABOVE_VAH_BULLISH_EXPANSION";
        } else if (currentPrice < val) {
            return "ACCEPTANCE_BELOW_VAL_BEARISH_EXPANSION";
        } else if (Math.abs(currentPrice - vpoc) <= (vah - val) * 0.05) {
            return "CONGESTION_AT_VPOC_HIGH_LIQUIDITY_EQUILIBRIUM";
        }
        return "INSIDE_VALUE_AREA_ROTATIONAL";
    }
}
