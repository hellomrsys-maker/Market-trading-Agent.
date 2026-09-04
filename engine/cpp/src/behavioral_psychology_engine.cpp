#include "state_vector.h"
#include <string>
#include <vector>

namespace optionalpha {

class BehavioralPsychologyEngine {
public:
    explicit BehavioralPsychologyEngine(AtomicStateVector& state) : state_(state) {}
    std::string classifyArchetype(const std::vector<double>& features) {
        double sum = 0.0;
        for (double f : features) sum += f;
        if (sum < 10) return "Procrastinator";
        if (sum < 20) return "Overspender";
        if (sum < 30) return "RiskAverse";
        return "Optimist";
    }
    void updateScore(double score) {
        state_.price = score; // demo usage of shared state
    }
private:
    AtomicStateVector& state_;
};

} // namespace optionalpha
