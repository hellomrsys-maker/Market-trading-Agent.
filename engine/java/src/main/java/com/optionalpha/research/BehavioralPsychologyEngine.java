package com.optionalpha.research;

import java.util.HashMap;
import java.util.Map;

/**
 * Module Y2 (Java): Behavioral Psychology & Cognitive Scripting Engine.
 * Synthesizes Emma Edwards' financial psychology models in enterprise Java.
 */
public class BehavioralPsychologyEngine {

    public enum InnerVillain {
        NONE,
        CHANGE_YOUR_LIFE_CHARLIE,
        MAKEOVER_MARGARET,
        WHATS_THE_POINT_WANDA,
        KEEP_UP_KARA_CONNIE,
        HAMSTER_WHEEL_HARRIET,
        FIX_IT_LATER_FRAN,
        FUCK_IT_FATIMA,
        SABOTAGE_SAM,
        TIGHT_HOLD_TINA
    }

    public enum DecisionZone {
        ACTIVATION,
        DECISION,
        REFLECTION,
        EMPOWERMENT
    }

    private InnerVillain activeVillain = InnerVillain.NONE;
    private DecisionZone currentZone = DecisionZone.ACTIVATION;

    public InnerVillain classifySabotageArchetype(
            String triggerContext,
            String emotionalState,
            boolean isImpulsive,
            boolean isPostBlowout,
            boolean isNearGoal,
            boolean isSocialPrompted) {
        
        if (isPostBlowout) {
            activeVillain = InnerVillain.FUCK_IT_FATIMA;
        } else if (isNearGoal && isImpulsive) {
            activeVillain = InnerVillain.SABOTAGE_SAM;
        } else if (isSocialPrompted) {
            activeVillain = InnerVillain.KEEP_UP_KARA_CONNIE;
        } else if (triggerContext.toLowerCase().contains("fatal")) {
            activeVillain = InnerVillain.WHATS_THE_POINT_WANDA;
        } else if (triggerContext.toLowerCase().contains("later") || emotionalState.toLowerCase().contains("procrastinate")) {
            activeVillain = InnerVillain.FIX_IT_LATER_FRAN;
        } else if (emotionalState.toLowerCase().contains("identity")) {
            activeVillain = InnerVillain.MAKEOVER_MARGARET;
        } else if (triggerContext.toLowerCase().contains("transform")) {
            activeVillain = InnerVillain.CHANGE_YOUR_LIFE_CHARLIE;
        } else if (emotionalState.toLowerCase().contains("fear_spending")) {
            activeVillain = InnerVillain.TIGHT_HOLD_TINA;
        } else {
            activeVillain = InnerVillain.NONE;
        }
        return activeVillain;
    }

    public Map<String, Object> evaluate3PResilience(double permanence, double pervasiveness, double personalisation) {
        double p1 = Math.max(0.0, Math.min(1.0, permanence));
        double p2 = Math.max(0.0, Math.min(1.0, pervasiveness));
        double p3 = Math.max(0.0, Math.min(1.0, personalisation));
        double avgDistortion = (p1 + p2 + p3) / 3.0;
        double toughness = 1.0 - avgDistortion;

        Map<String, Object> result = new HashMap<>();
        result.put("permanence", p1);
        result.put("pervasiveness", p2);
        result.put("personalisation", p3);
        result.put("composite_mental_toughness", Math.round(toughness * 10000.0) / 10000.0);
        return result;
    }
}
