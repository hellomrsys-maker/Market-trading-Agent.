#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <cstring>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Behavioral Psychology & Cognitive Scripting.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) BehavioralPsychologyState {
    uint32_t active_villain_id;     // 4 bytes (0-9)
    uint32_t current_zone_id;       // 4 bytes (0: Activation, 1: Decision, 2: Reflection, 3: Empowerment)
    float permanence_score;         // 4 bytes (0.0 to 1.0)
    float pervasiveness_score;      // 4 bytes (0.0 to 1.0)
    float personalisation_score;    // 4 bytes (0.0 to 1.0)
    float composite_mental_toughness;// 4 bytes
    uint32_t circuit_breaker_active;// 4 bytes (0 or 1)
    uint32_t intentional_status;    // 4 bytes
    uint8_t padding[32];            // 32 bytes padding -> Total 64 bytes
};

static_assert(sizeof(BehavioralPsychologyState) == 64, "BehavioralPsychologyState must be exactly 64 bytes for Zero-Bridge synchronization");

class BehavioralPsychologyEngine {
public:
    static void update_psychology_state(
        BehavioralPsychologyState& state,
        uint32_t villain_id,
        uint32_t zone_id,
        float permanence,
        float pervasiveness,
        float personalisation
    ) {
        state.active_villain_id = villain_id;
        state.current_zone_id = zone_id;
        state.permanence_score = std::max(0.0f, std::min(1.0f, permanence));
        state.pervasiveness_score = std::max(0.0f, std::min(1.0f, pervasiveness));
        state.personalisation_score = std::max(0.0f, std::min(1.0f, personalisation));
        
        float avg_distortion = (state.permanence_score + state.pervasiveness_score + state.personalisation_score) / 3.0f;
        state.composite_mental_toughness = 1.0f - avg_distortion;
        state.circuit_breaker_active = (state.composite_mental_toughness < 0.35f || villain_id == 6 || villain_id == 7) ? 1 : 0;
        state.intentional_status = (state.current_zone_id == 3) ? 1 : 0;
    }
};

} // namespace optionalpha
