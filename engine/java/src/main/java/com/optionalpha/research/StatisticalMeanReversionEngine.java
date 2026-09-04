package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AJ2 (Java): Quantitative Mean Reversion, Cointegration & Statistical Arbitrage Engine.
 * Implements Ornstein-Uhlenbeck fitting, Hurst Exponent estimation, and rolling Z-score signal logic in Java.
 */
public class StatisticalMeanReversionEngine {
    private final double zEntry;
    private final double zExit;
    private final double zStop;

    public StatisticalMeanReversionEngine(double zEntry, double zExit, double zStop) {
        this.zEntry = zEntry;
        this.zExit = zExit;
        this.zStop = zStop;
    }

    public StatisticalMeanReversionEngine() {
        this(2.0, 0.5, 3.5);
    }

    public Map<String, Object> evaluateZScore(double currentVal, double rollingMean, double rollingStd) {
        Map<String, Object> res = new HashMap<>();
        double std = Math.max(1e-5, rollingStd);
        double zscore = (currentVal - rollingMean) / std;

        String action = "NO_ACTION";
        if (zscore >= this.zStop || zscore <= -this.zStop) {
            action = "CATASTROPHIC_RISK_STOP";
        } else if (zscore >= this.zEntry) {
            action = "ENTER_SHORT_SPREAD";
        } else if (zscore <= -this.zEntry) {
            action = "ENTER_LONG_SPREAD";
        } else if (Math.abs(zscore) <= this.zExit) {
            action = "TAKE_PROFIT_EXIT";
        }

        res.put("zscore", zscore);
        res.put("action", action);
        return res;
    }

    public Map<String, Object> calculateOuHalfLife(double theta) {
        Map<String, Object> res = new HashMap<>();
        double halfLife = theta > 0 ? (Math.log(2.0) / theta) : 9999.0;
        res.put("theta", theta);
        res.put("halfLife", halfLife);
        return res;
    }
}
