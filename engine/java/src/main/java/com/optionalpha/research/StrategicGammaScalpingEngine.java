package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module AF2 (Java): Strategic Gamma Scalping & Position Adjustment Engine.
 * Calculates Gamma Decay breakevens ("Paying the Rent") and daily sigma moves in Java.
 */
public class StrategicGammaScalpingEngine {

    public double calculateGammaDecayBreakeven(double dailyTheta, double positionGamma) {
        double g = Math.max(1e-6, positionGamma);
        double th = Math.abs(dailyTheta);
        double decayMove = Math.sqrt((2.0 * th) / g);
        return Math.round(decayMove * 10000.0) / 10000.0;
    }

    public Map<String, Double> calculateDailySigmaMove(double spotPrice, double annualVol) {
        double dailyVol = annualVol / Math.sqrt(252.0);
        double sigma1 = spotPrice * dailyVol;

        Map<String, Double> res = new HashMap<>();
        res.put("daily_vol_pct", Math.round(dailyVol * 10000.0) / 100.0);
        res.put("one_sigma_move", Math.round(sigma1 * 100.0) / 100.0);
        res.put("upper_1sigma", Math.round((spotPrice + sigma1) * 100.0) / 100.0);
        res.put("lower_1sigma", Math.round((spotPrice - sigma1) * 100.0) / 100.0);
        return res;
    }
}
