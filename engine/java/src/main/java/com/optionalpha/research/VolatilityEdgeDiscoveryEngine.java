package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AW2 (Java): Volatility Edge Discovery & Realized vs. Implied Mispricing Engine.
 * Evaluates IV vs HV spreads, IV percentiles, and mispricing regimes in Java.
 */
public class VolatilityEdgeDiscoveryEngine {
    private final double expensiveVol;
    private final double cheapVol;

    public VolatilityEdgeDiscoveryEngine(double expensiveVol, double cheapVol) {
        this.expensiveVol = expensiveVol;
        this.cheapVol = cheapVol;
    }

    public VolatilityEdgeDiscoveryEngine() {
        this(4.0, -2.0);
    }

    public Map<String, Object> evaluateEdge(double iv30d, double hv30d, double ivMin, double ivMax) {
        Map<String, Object> res = new HashMap<>();
        double spread = iv30d - hv30d;
        double range = Math.max(1.0, ivMax - ivMin);
        double rank = Math.max(0.0, Math.min(100.0, ((iv30d - ivMin) / range) * 100.0));

        boolean isExpensive = (spread >= this.expensiveVol) || (rank >= 75.0);
        boolean isCheap = (spread <= this.cheapVol) || (rank <= 25.0);

        String regime = isExpensive ? "EXPENSIVE_SHORT_VOL" : (isCheap ? "CHEAP_LONG_VOL" : "NEUTRAL");

        res.put("spread", spread);
        res.put("ivRank", rank);
        res.put("regime", regime);
        res.put("isExpensive", isExpensive);
        res.put("isCheap", isCheap);
        return res;
    }
}
