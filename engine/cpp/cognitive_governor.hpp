// engine/cpp/cognitive_governor.hpp
// OptionAlpha Agent — C++20 Cognitive Governor and Meta-Decision Arbiter
// Polyglot Pillar 4: C++20 Engine Core
// MASTER MANDATE & POLYGLOT COMPUTING RULE APPLIED

#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>
#include <iostream>

namespace optionalpha {

// Deep representation of the cognitive state sent back to Python API via zero-bridge
struct alignas(64) CognitiveArbitrationState {
    double thinking_score;           // Base AI model confidence
    double concentration_weight;     // Softmax salience
    double recall_boost;             // KNN episodic memory boost
    double final_confidence;         // Fully arbitrated confidence
    bool is_approved;                // Final Go/No-Go
    bool crisis_override;            // Did the recall engine flag a crisis?
    char pad[14];                    // 64-byte alignment padding for zero-bridge synchronization
};

class CognitiveGovernorEngine {
public:
    static inline CognitiveArbitrationState arbitrate(
        double base_confidence,
        double attention_salience,
        double historical_recall_boost,
        bool crisis_detected,
        double confidence_threshold = 0.65
    ) {
        // Faculty 5: Meta-cognitive Arbitration
        // If crisis is detected, we penalize lack of historical recall edge massively.
        double crisis_penalty = (crisis_detected && historical_recall_boost < 0.0) ? -0.30 : 0.0;
        
        // Massive leverage applied to concentration to filter out noise
        double combined = base_confidence + (attention_salience * 5.0) + historical_recall_boost + crisis_penalty;
        
        // Clamp confidence between 10% and 98%
        double final_conf = std::clamp(combined, 0.10, 0.98);
        bool approved = final_conf >= confidence_threshold;

        return {
            base_confidence,
            attention_salience,
            historical_recall_boost,
            final_conf,
            approved,
            crisis_detected,
            {0} // padding
        };
    }

    // Faculty 4: Lateral Defensive Morphing calculations (Hot Path)
    static inline double calculate_roll_out_down_strike(double current_strike, double spot_price) {
        // Target is minimum of 90% of spot or 95% of current strike, rounded to nearest 2.5
        double target_base = std::min(spot_price * 0.90, current_strike * 0.95);
        return std::round(target_base / 2.5) * 2.5;
    }
    
    // Asymmetric Wing calculations (Hot Path)
    static inline std::pair<double, double> calculate_asymmetric_wings(double put_skew_steepness, double base_width) {
        if (put_skew_steepness > 0.06) {
            return {std::max(2.5, base_width - 2.5), base_width + 5.0}; // tight put, wide call
        } else if (put_skew_steepness < -0.02) {
            return {base_width + 5.0, std::max(2.5, base_width - 2.5)}; // wide put, tight call
        }
        return {base_width, base_width};
    }
};

} // namespace optionalpha
