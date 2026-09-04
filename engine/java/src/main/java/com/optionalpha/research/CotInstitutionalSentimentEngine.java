package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AM2 (Java): COT Institutional Positioning & Sentiment Engine.
 * Implements 3-year rolling COT percentile indices and Open Interest momentum interpretation.
 */
public class CotInstitutionalSentimentEngine {
    private final double extremeBull;
    private final double extremeBear;

    public CotInstitutionalSentimentEngine(double extremeBull, double extremeBear) {
        this.extremeBull = extremeBull;
        this.extremeBear = extremeBear;
    }

    public CotInstitutionalSentimentEngine() {
        this(90.0, 10.0);
    }

    public Map<String, Object> calculateCotIndex(double currentNet, double minNet, double maxNet) {
        Map<String, Object> res = new HashMap<>();
        double rng = Math.max(1.0, maxNet - minNet);
        double index = ((currentNet - minNet) / rng) * 100.0;
        double clamped = Math.max(0.0, Math.min(100.0, index));

        boolean isBull = clamped >= this.extremeBull;
        boolean isBear = clamped <= this.extremeBear;

        String status = "NEUTRAL";
        if (isBull) status = "EXTREME_COMMERCIAL_ACCUMULATION_BULLISH";
        else if (isBear) status = "EXTREME_COMMERCIAL_DISTRIBUTION_BEARISH";

        res.put("cotIndex", clamped);
        res.put("status", status);
        res.put("isExtreme", isBull || isBear);
        return res;
    }

    public Map<String, Object> evaluatePriceOi(double priceChange, double oiChange) {
        Map<String, Object> res = new HashMap<>();
        String regime;
        String bias;

        if (priceChange > 0 && oiChange > 0) {
            regime = "STRONG_BULLISH_NEW_LONGS";
            bias = "BUY_MOMENTUM";
        } else if (priceChange > 0 && oiChange <= 0) {
            regime = "WEAK_BULLISH_SHORT_COVERING";
            bias = "FADE_OR_TIGHTEN_STOPS";
        } else if (priceChange < 0 && oiChange > 0) {
            regime = "STRONG_BEARISH_NEW_SHORTS";
            bias = "SELL_MOMENTUM";
        } else {
            regime = "WEAK_BEARISH_LONG_LIQUIDATION";
            bias = "PREPARE_FOR_REVERSAL_BOUNCE";
        }

        res.put("regime", regime);
        res.put("bias", bias);
        return res;
    }
}
