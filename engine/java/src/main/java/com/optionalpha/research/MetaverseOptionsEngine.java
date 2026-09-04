package com.optionalpha.research;

public class MetaverseOptionsEngine {
    public String analyzeOrderFlowDelta(double callDelta, double putDelta) {
        if (callDelta > putDelta * 1.5) return "BULLISH_INSTITUTIONAL_SENTIMENT";
        return "NEUTRAL_DELTA";
    }
}
