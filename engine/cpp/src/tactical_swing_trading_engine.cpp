#include "state_vector.h"
#include <vector>
#include <algorithm>

namespace optionalpha {

class TacticalSwingTradingEngine {
public:
    explicit TacticalSwingTradingEngine(AtomicStateVector& state) : state_(state) {}

    // Detect simple ABCD pattern based on price series (placeholder logic)
    bool detectABCD(const std::vector<double>& prices) {
        if (prices.size() < 4) return false;
        double a = prices[0];
        double b = prices[1];
        double c = prices[2];
        double d = prices[3];
        return (b > a && c < b && d > c && d > a);
    }

    // Update state with a signal strength value
    void updateSignal(double signal) {
        state_.price = signal; // demo usage
    }

private:
    AtomicStateVector& state_;
};

} // namespace optionalpha
