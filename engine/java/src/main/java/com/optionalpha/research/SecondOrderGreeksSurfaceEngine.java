package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AD2 (Java): Higher-Order Greeks, Moments & Volatility Surface Engine.
 * Calculates analytical Vanna, Vomma, Charm and Forward Implied Volatility in Java.
 */
public class SecondOrderGreeksSurfaceEngine {

    public double calculateForwardImpliedVolatility(double volNear, int daysNear, double volDeferred, int daysDeferred) {
        if (daysDeferred <= daysNear) {
            return volDeferred;
        }
        double v1SqT = Math.pow(volNear, 2) * (double) daysNear;
        double v2SqT = Math.pow(volDeferred, 2) * (double) daysDeferred;
        double deltaT = (double) (daysDeferred - daysNear);

        double num = v2SqT - v1SqT;
        if (num <= 0) {
            return 0.0;
        }
        return Math.round(Math.sqrt(num / deltaT) * 10000.0) / 10000.0;
    }

    public Map<String, Object> evaluateTermStructureRegime(int daysNear, double volNear, int daysFar, double volFar) {
        double slope = (volFar - volNear) / (double) (daysFar - daysNear);
        String regime = "FLAT";
        if (slope > 0.0005) {
            regime = "NORMAL_CONTANGO";
        } else if (slope < -0.0005) {
            regime = "INVERTED_BACKWARDATION";
        }

        Map<String, Object> result = new HashMap<>();
        result.put("regime", regime);
        result.put("slope", Math.round(slope * 1000000.0) / 1000000.0);
        return result;
    }
}
