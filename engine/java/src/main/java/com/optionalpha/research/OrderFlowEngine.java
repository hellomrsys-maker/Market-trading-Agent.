package com.optionalpha.research;

public class OrderFlowEngine {
    public String analyzeOiAndVolume(String priceTrend, String oiTrend, String volTrend) {
        if (priceTrend.equals("RISING") && oiTrend.equals("RISING")) return "LONG_BUILDUP";
        return "NEUTRAL";
    }
}
