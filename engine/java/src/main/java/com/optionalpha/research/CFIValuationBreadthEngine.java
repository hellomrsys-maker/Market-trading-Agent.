package com.optionalpha.research;

import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;

/**
 * OptionAlpha Agent — Module O2: Java Institutional Valuation & Market Breadth Engine
 */
public class CFIValuationBreadthEngine {
    private static final Logger logger = Logger.getLogger(CFIValuationBreadthEngine.class.getName());

    public Map<String, Object> evaluateMarketBreadth(
            int advStocks, int decStocks, double advVol, double decVol, double adx14) {
        
        double advDecRatio = (double) advStocks / Math.max(1, decStocks);
        double volRatio = advVol / Math.max(1.0, decVol);
        double trin = advDecRatio / Math.max(0.001, volRatio);

        Map<String, Object> state = new HashMap<>();
        state.put("trin", trin);
        state.put("adx_14", adx14);
        state.put("is_trending", adx14 >= 25.0);
        state.put("regime", trin < 0.50 ? "OVERBOUGHT" : (trin > 3.00 ? "OVERSOLD" : "EQUILIBRIUM"));

        return state;
    }
}
