package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module BE2 (Java): Karl Domm All-Weather Options Portfolio & Tail Risk Vomma Engine.
 * Evaluates SPAN margin slicing, 4 market regimes, and 5-delta teenie put positive vomma in Java.
 */
public class AllWeatherVommaEngine {
    private final double maxMarginUtil;

    public AllWeatherVommaEngine(double maxMarginUtil) {
        this.maxMarginUtil = maxMarginUtil;
    }

    public AllWeatherVommaEngine() {
        this(65.0);
    }

    public Map<String, Object> classifyRegime(double spxReturn, double vixSpike) {
        Map<String, Object> res = new HashMap<>();
        String regime;
        if (vixSpike >= 35.0) regime = "CRASH_MARKET";
        else if (spxReturn < -8.0 && vixSpike < 30.0) regime = "GRIND_DOWN_MARKET";
        else if (Math.abs(spxReturn) <= 4.0) regime = "SIDEWAYS_MARKET";
        else regime = "RISING_BULL_MARKET";

        res.put("regime", regime);
        return res;
    }

    public Map<String, Object> auditMargin(double pnl12Down, double pnl20Down, double pnl10Up, double plannedCapital) {
        Map<String, Object> res = new HashMap<>();
        double s12 = Math.abs(Math.min(0.0, pnl12Down));
        double s20 = Math.abs(Math.min(0.0, pnl20Down)) / 2.0;
        double s10 = Math.abs(Math.min(0.0, pnl10Up));

        double req = Math.max(s12, Math.max(s20, s10));
        double util = (req / Math.max(1.0, plannedCapital)) * 100.0;
        boolean isSafe = util <= this.maxMarginUtil;

        res.put("req", req);
        res.put("util", util);
        res.put("isSafe", isSafe);
        return res;
    }

    public Map<String, Object> evaluateTeenieVomma(double coreVomma, int numTeenies, double teenieVommaEach) {
        Map<String, Object> res = new HashMap<>();
        double hedgeVomma = numTeenies * teenieVommaEach;
        double netVomma = coreVomma + hedgeVomma;
        boolean hasPosVomma = netVomma > 0.0;

        res.put("netVomma", netVomma);
        res.put("hasPosVomma", hasPosVomma);
        return res;
    }
}
