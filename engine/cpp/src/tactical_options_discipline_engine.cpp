#include "state_vector.h"
#include <vector>
#include <algorithm>

namespace optionalpha {

class TacticalOptionsDisciplineEngine {
public:
    explicit TacticalOptionsDisciplineEngine(AtomicStateVector& state) : state_(state) {}

    // Simple OCO (One-Cancels-Other) demonstration: given two profit targets, pick the higher one and set as active
    double selectOCO(double target1, double target2) {
        double selected = std::max(target1, target2);
        // Store selected target in shared state (using volatility field for demo)
        state_.volatility = selected;
        return selected;
    }

    // Simple vertical spread payoff calculation placeholder
    double verticalSpreadPayoff(double strikeLong, double strikeShort, double price, bool isCredit) {
        double payoff = 0.0;
        if (isCredit) {
            // Credit spread: max profit is premium received, loss is difference between strikes minus premium
            payoff = (strikeShort - strikeLong) - (price - strikeLong);
        } else {
            // Debit spread: payoff = max(0, price - strikeLong) - max(0, price - strikeShort)
            payoff = std::max(0.0, price - strikeLong) - std::max(0.0, price - strikeShort);
        }
        // Store payoff in shared state (using price field for demo)
        state_.price = payoff;
        return payoff;
    }

private:
    AtomicStateVector& state_;
};

} // namespace optionalpha
